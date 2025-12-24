#!/usr/bin/env python3
"""
Backtest Multi-Source Sentiment Trading Strategy
Test how the sentiment model would have performed with 10 trades
over the last 6 months (June 23, 2025 - Dec 23, 2025)

Strategy:
- BUY when combined sentiment < -0.1 (Fear)
- SELL when combined sentiment > +0.1 (Greed) OR after holding for 7 days
- Use historical Fear & Greed data + simulated Reddit sentiment
"""
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json


def fetch_historical_fear_greed(days=180):
    """Fetch historical Fear & Greed Index data"""
    print(f"\nFetching {days} days of Fear & Greed Index...")

    try:
        url = f"https://api.alternative.me/fng/?limit={days}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            fear_greed_data = []
            for entry in data['data']:
                fear_greed_data.append({
                    'date': datetime.fromtimestamp(int(entry['timestamp'])),
                    'value': int(entry['value']),
                    'classification': entry['value_classification'],
                    'normalized': (int(entry['value']) - 50) / 50
                })

            print(f"✓ Fetched {len(fear_greed_data)} days of data")
            return fear_greed_data

    except Exception as e:
        print(f"ERROR: {e}")

    return None


def fetch_historical_bitcoin_price(days=180):
    """Fetch historical Bitcoin price data"""
    print(f"\nFetching {days} days of Bitcoin price data...")

    try:
        btc = yf.Ticker("BTC-USD")
        df = btc.history(period=f"{days}d", interval="1d")

        print(f"✓ Fetched {len(df)} days of price data")
        print(f"  Price range: ${df['Close'].min():,.0f} - ${df['Close'].max():,.0f}")

        return df

    except Exception as e:
        print(f"ERROR: {e}")
        return None


def simulate_reddit_sentiment(date, price_change_7d):
    """
    Simulate Reddit sentiment based on recent price action

    In reality, Reddit sentiment tends to:
    - Be bullish after price increases (lagging indicator)
    - Be bearish after price decreases (lagging indicator)

    We'll simulate this with some noise
    """
    # Base sentiment follows price trend (lagging)
    base_sentiment = price_change_7d / 100 * 0.5  # Reduce magnitude

    # Add random noise (-0.2 to +0.2)
    noise = np.random.uniform(-0.2, 0.2)

    simulated_sentiment = np.clip(base_sentiment + noise, -1, 1)

    return simulated_sentiment


def calculate_combined_sentiment(fear_greed_value, reddit_sentiment):
    """
    Combine Fear & Greed (60%) and Reddit (40%)
    Same weighting as in the live model
    """
    fg_normalized = (fear_greed_value - 50) / 50
    combined = fg_normalized * 0.6 + reddit_sentiment * 0.4

    return combined


def backtest_trading_strategy(fear_greed_data, price_df):
    """
    Backtest the sentiment trading strategy

    Rules:
    - BUY when combined sentiment < -0.1 (Fear in market)
    - SELL when:
      1. Combined sentiment > +0.1 (Greed in market), OR
      2. Held for 7 days (take profit/cut loss)
    """
    print("\n" + "=" * 80)
    print("BACKTESTING SENTIMENT TRADING STRATEGY")
    print("=" * 80)
    print("\nStrategy:")
    print("  BUY: When combined sentiment < -0.1 (Fear)")
    print("  SELL: When sentiment > +0.1 (Greed) OR after 7 days")
    print("  Weighting: Fear & Greed 60%, Reddit 40%")
    print("=" * 80)

    # Create merged dataset
    merged_data = []

    for fg in fear_greed_data:
        date = fg['date'].date()

        # Find matching price
        matching_prices = price_df[price_df.index.date == date]

        if len(matching_prices) > 0:
            price = matching_prices['Close'].iloc[0]

            # Calculate 7-day price change for Reddit sentiment simulation
            try:
                week_ago = price_df[price_df.index.date == (date - timedelta(days=7))]
                if len(week_ago) > 0:
                    week_ago_price = week_ago['Close'].iloc[0]
                    price_change_7d = (price - week_ago_price) / week_ago_price * 100
                else:
                    price_change_7d = 0
            except:
                price_change_7d = 0

            # Simulate Reddit sentiment
            reddit_sentiment = simulate_reddit_sentiment(date, price_change_7d)

            # Calculate combined sentiment
            combined_sentiment = calculate_combined_sentiment(fg['value'], reddit_sentiment)

            merged_data.append({
                'date': date,
                'price': price,
                'fear_greed': fg['value'],
                'reddit_sentiment': reddit_sentiment,
                'combined_sentiment': combined_sentiment,
                'fg_classification': fg['classification']
            })

    print(f"\n✓ Prepared {len(merged_data)} days of data for backtesting")

    # Set random seed for reproducible Reddit sentiment simulation
    np.random.seed(42)

    # Regenerate with seed
    for item in merged_data:
        date = item['date']

        # Get price change
        try:
            idx = next(i for i, d in enumerate(merged_data) if d['date'] == date)
            if idx >= 7:
                week_ago_price = merged_data[idx - 7]['price']
                price_change_7d = (item['price'] - week_ago_price) / week_ago_price * 100
            else:
                price_change_7d = 0
        except:
            price_change_7d = 0

        item['reddit_sentiment'] = simulate_reddit_sentiment(date, price_change_7d)
        item['combined_sentiment'] = calculate_combined_sentiment(item['fear_greed'], item['reddit_sentiment'])

    # Execute trades
    trades = []
    position = None
    max_trades = 10

    for i, day in enumerate(merged_data):
        date = day['date']
        price = day['price']
        sentiment = day['combined_sentiment']

        # Check for BUY signal
        if position is None and len(trades) < max_trades:
            if sentiment < -0.1:  # Fear in market
                position = {
                    'buy_date': date,
                    'buy_price': price,
                    'buy_sentiment': sentiment,
                    'buy_fg': day['fear_greed'],
                    'days_held': 0
                }

                print(f"\n📉 Trade {len(trades) + 1}: BUY")
                print(f"  Date: {date}")
                print(f"  Price: ${price:,.2f}")
                print(f"  Sentiment: {sentiment:.3f} (Fear & Greed: {day['fear_greed']})")

        # Check for SELL signal
        elif position is not None:
            position['days_held'] += 1

            # Sell conditions
            should_sell = False
            sell_reason = ""

            if sentiment > 0.1:  # Greed in market
                should_sell = True
                sell_reason = "Greed signal"
            elif position['days_held'] >= 7:  # Held for 7 days
                should_sell = True
                sell_reason = "7-day exit"

            if should_sell:
                profit_pct = (price - position['buy_price']) / position['buy_price'] * 100
                profit_usd = (price - position['buy_price']) / position['buy_price'] * 10000  # $10k position

                trades.append({
                    'trade_num': len(trades) + 1,
                    'buy_date': position['buy_date'],
                    'sell_date': date,
                    'buy_price': position['buy_price'],
                    'sell_price': price,
                    'days_held': position['days_held'],
                    'buy_sentiment': position['buy_sentiment'],
                    'sell_sentiment': sentiment,
                    'buy_fg': position['buy_fg'],
                    'sell_fg': day['fear_greed'],
                    'profit_pct': profit_pct,
                    'profit_usd': profit_usd,
                    'sell_reason': sell_reason
                })

                print(f"  📈 SELL")
                print(f"  Date: {date}")
                print(f"  Price: ${price:,.2f}")
                print(f"  Days held: {position['days_held']}")
                print(f"  Return: {profit_pct:+.2f}% (${profit_usd:+,.0f})")
                print(f"  Reason: {sell_reason}")

                position = None

    return trades


def print_results(trades):
    """Print backtest results"""
    print("\n" + "=" * 80)
    print("BACKTEST RESULTS")
    print("=" * 80)

    if len(trades) == 0:
        print("\n❌ No trades executed!")
        return

    df = pd.DataFrame(trades)

    print(f"\n📊 Total Trades: {len(trades)}")
    print(f"Winning Trades: {len(df[df['profit_pct'] > 0])} ({len(df[df['profit_pct'] > 0])/len(trades)*100:.1f}%)")
    print(f"Losing Trades: {len(df[df['profit_pct'] < 0])} ({len(df[df['profit_pct'] < 0])/len(trades)*100:.1f}%)")

    print(f"\n💰 Performance Metrics:")
    print(f"Average Return: {df['profit_pct'].mean():+.2f}%")
    print(f"Median Return: {df['profit_pct'].median():+.2f}%")
    print(f"Best Trade: {df['profit_pct'].max():+.2f}%")
    print(f"Worst Trade: {df['profit_pct'].min():+.2f}%")
    print(f"Average Days Held: {df['days_held'].mean():.1f} days")

    print(f"\n💵 P&L (starting with $10,000 per trade):")
    print(f"Total Profit: ${df['profit_usd'].sum():+,.2f}")
    print(f"Average Profit/Trade: ${df['profit_usd'].mean():+,.2f}")

    # Calculate cumulative return (compounding)
    cumulative_return = 1.0
    for ret in df['profit_pct']:
        cumulative_return *= (1 + ret / 100)

    total_return_pct = (cumulative_return - 1) * 100
    print(f"\n📈 Cumulative Return: {total_return_pct:+.2f}%")
    print(f"Final Portfolio Value: ${10000 * cumulative_return:,.2f} (from $10,000)")

    print("\n" + "=" * 80)
    print("TRADE DETAILS")
    print("=" * 80)

    for trade in trades:
        print(f"\nTrade {trade['trade_num']}:")
        print(f"  Buy:  {trade['buy_date']} @ ${trade['buy_price']:,.2f} (Sentiment: {trade['buy_sentiment']:.3f}, F&G: {trade['buy_fg']})")
        print(f"  Sell: {trade['sell_date']} @ ${trade['sell_price']:,.2f} (Sentiment: {trade['sell_sentiment']:.3f}, F&G: {trade['sell_fg']})")
        print(f"  Return: {trade['profit_pct']:+.2f}% over {trade['days_held']} days ({trade['sell_reason']})")

    print("\n" + "=" * 80)


def save_results(trades):
    """Save backtest results"""
    results = {
        'backtest_period': '2025-06-23 to 2025-12-23',
        'total_trades': len(trades),
        'trades': trades
    }

    if len(trades) > 0:
        df = pd.DataFrame(trades)

        results['summary'] = {
            'win_rate': len(df[df['profit_pct'] > 0]) / len(trades) * 100,
            'avg_return_pct': df['profit_pct'].mean(),
            'total_return_pct': ((1 + df['profit_pct']/100).prod() - 1) * 100,
            'avg_days_held': df['days_held'].mean()
        }

    filename = "sentiment_backtest_results.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"✓ Results saved to: {filename}")


def main():
    """Main entry point"""
    print("=" * 80)
    print("MULTI-SOURCE SENTIMENT BACKTEST")
    print("=" * 80)
    print("\nPeriod: June 23, 2025 - December 23, 2025 (6 months)")
    print("Target: 10 trades")
    print("Strategy: Buy on Fear, Sell on Greed or after 7 days")
    print("=" * 80)

    # Fetch historical data
    fear_greed_data = fetch_historical_fear_greed(days=180)
    price_df = fetch_historical_bitcoin_price(days=180)

    if fear_greed_data is None or price_df is None:
        print("\n❌ Failed to fetch data")
        return

    # Run backtest
    trades = backtest_trading_strategy(fear_greed_data, price_df)

    # Print results
    print_results(trades)

    # Save results
    save_results(trades)


if __name__ == "__main__":
    main()

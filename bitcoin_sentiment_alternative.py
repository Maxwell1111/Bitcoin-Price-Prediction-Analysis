#!/usr/bin/env python3
"""
Bitcoin Sentiment Analysis - Alternative Approach
Uses publicly available sentiment data and news sources to predict Bitcoin price

Since Reddit API requires authentication, we'll use:
1. Alternative.me Crypto Fear & Greed Index API (public, no auth needed)
2. Historical correlation analysis
3. Price action sentiment indicators
"""
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time


def fetch_fear_greed_index():
    """
    Fetch Crypto Fear & Greed Index from Alternative.me API
    Free API, no authentication required
    Returns sentiment score from 0-100:
      0-24: Extreme Fear
      25-49: Fear
      50-74: Greed
      75-100: Extreme Greed
    """
    print("\nFetching Crypto Fear & Greed Index...")

    try:
        url = "https://api.alternative.me/fng/?limit=30"  # Last 30 days
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if 'data' in data:
                fear_greed_data = []

                for entry in data['data']:
                    fear_greed_data.append({
                        'timestamp': datetime.fromtimestamp(int(entry['timestamp'])),
                        'value': int(entry['value']),
                        'classification': entry['value_classification']
                    })

                print(f"✓ Fetched {len(fear_greed_data)} days of Fear & Greed Index")

                # Get latest
                latest = fear_greed_data[0]
                print(f"  Latest: {latest['value']} ({latest['classification']}) on {latest['timestamp'].date()}")

                return fear_greed_data

        print("ERROR: Could not fetch Fear & Greed Index")
        return None

    except Exception as e:
        print(f"ERROR fetching Fear & Greed Index: {e}")
        return None


def fetch_bitcoin_price(days=30):
    """Fetch Bitcoin price data"""
    print(f"\nFetching Bitcoin price data (last {days} days)...")

    try:
        btc = yf.Ticker("BTC-USD")
        df = btc.history(period=f"{days}d", interval="1d")

        print(f"✓ Fetched {len(df)} days of price data")
        print(f"  Current price: ${df['Close'].iloc[-1]:,.2f}")

        return df

    except Exception as e:
        print(f"ERROR fetching price data: {e}")
        return None


def normalize_sentiment_to_score(value):
    """
    Normalize Fear & Greed Index (0-100) to sentiment score (-1 to 1)
    0 (Extreme Fear) → -1
    50 (Neutral) → 0
    100 (Extreme Greed) → +1
    """
    return (value - 50) / 50


def correlate_sentiment_with_price(fear_greed_data, price_df):
    """
    Correlate sentiment with price movements

    Args:
        fear_greed_data: List of Fear & Greed Index data
        price_df: DataFrame with Bitcoin prices
    """
    print("\n" + "=" * 80)
    print("ANALYZING SENTIMENT vs PRICE CORRELATION")
    print("=" * 80)

    # Merge sentiment and price data
    combined_data = []

    for fg in fear_greed_data:
        # Find closest price
        date = fg['timestamp'].date()

        # Try to find matching price
        matching_prices = price_df[price_df.index.date == date]

        if len(matching_prices) > 0:
            price = matching_prices['Close'].iloc[0]

            combined_data.append({
                'date': date,
                'sentiment_value': fg['value'],
                'sentiment_score': normalize_sentiment_to_score(fg['value']),
                'classification': fg['classification'],
                'price': price
            })

    if len(combined_data) == 0:
        print("ERROR: No matching data")
        return None

    # Convert to DataFrame
    df = pd.DataFrame(combined_data)

    print(f"\n✓ Matched {len(df)} days of sentiment and price data")

    # Calculate price changes at different horizons
    for days in [1, 3, 7]:
        if len(df) > days:
            df[f'price_change_{days}d'] = df['price'].pct_change(periods=days) * 100

    # Calculate correlation
    print("\n" + "-" * 80)
    print("CORRELATION ANALYSIS")
    print("-" * 80)

    for days in [1, 3, 7]:
        col = f'price_change_{days}d'
        if col in df.columns:
            correlation = df['sentiment_score'].corr(df[col])
            print(f"\n{days}-day price change vs sentiment:")
            print(f"  Correlation: {correlation:+.3f}")

            if abs(correlation) > 0.3:
                print(f"  ✅ MODERATE correlation detected!")
            elif abs(correlation) > 0.5:
                print(f"  ✅✅ STRONG correlation detected!")
            else:
                print(f"  ➖ Weak correlation")

    return df


def test_sentiment_trading_strategy(df):
    """
    Test a simple sentiment-based trading strategy

    Strategy:
    - Buy when sentiment is Extreme Fear (value < 25)
    - Sell when sentiment is Extreme Greed (value > 75)
    - Hold otherwise
    """
    print("\n" + "=" * 80)
    print("BACKTESTING SENTIMENT TRADING STRATEGY")
    print("=" * 80)

    print("\nStrategy:")
    print("  BUY: When Fear & Greed < 25 (Extreme Fear)")
    print("  SELL: When Fear & Greed > 75 (Extreme Greed)")
    print("  HOLD: Otherwise")

    trades = []
    position = None

    for i, row in df.iterrows():
        sentiment = row['sentiment_value']
        price = row['price']
        date = row['date']

        # Buy signal: Extreme Fear
        if sentiment < 25 and position is None:
            position = {
                'buy_price': price,
                'buy_date': date,
                'buy_sentiment': sentiment
            }
            print(f"\n📉 BUY at ${price:,.2f} on {date} (Sentiment: {sentiment} - Extreme Fear)")

        # Sell signal: Extreme Greed
        elif sentiment > 75 and position is not None:
            profit_pct = (price - position['buy_price']) / position['buy_price'] * 100
            days_held = (date - position['buy_date']).days

            trades.append({
                'buy_price': position['buy_price'],
                'sell_price': price,
                'buy_date': position['buy_date'],
                'sell_date': date,
                'profit_pct': profit_pct,
                'days_held': days_held
            })

            print(f"📈 SELL at ${price:,.2f} on {date} (Sentiment: {sentiment} - Extreme Greed)")
            print(f"   Return: {profit_pct:+.1f}% over {days_held} days")

            position = None

    print("\n" + "-" * 80)
    print("TRADING RESULTS")
    print("-" * 80)

    if len(trades) == 0:
        print("\nNo trades executed during this period")
        return None

    df_trades = pd.DataFrame(trades)

    print(f"\nTotal trades: {len(trades)}")
    print(f"Winning trades: {len(df_trades[df_trades['profit_pct'] > 0])}")
    print(f"Losing trades: {len(df_trades[df_trades['profit_pct'] < 0])}")
    print(f"Win rate: {len(df_trades[df_trades['profit_pct'] > 0]) / len(trades) * 100:.1f}%")

    print(f"\nAverage return: {df_trades['profit_pct'].mean():+.1f}%")
    print(f"Best trade: {df_trades['profit_pct'].max():+.1f}%")
    print(f"Worst trade: {df_trades['profit_pct'].min():+.1f}%")
    print(f"Total return: {df_trades['profit_pct'].sum():+.1f}%")

    return df_trades


def make_prediction(latest_sentiment):
    """Make prediction based on current sentiment"""
    print("\n" + "=" * 80)
    print("CURRENT PREDICTION")
    print("=" * 80)

    value = latest_sentiment['value']
    classification = latest_sentiment['classification']
    score = normalize_sentiment_to_score(value)

    print(f"\nCurrent Sentiment:")
    print(f"  Value: {value}/100")
    print(f"  Classification: {classification}")
    print(f"  Normalized Score: {score:+.3f}")

    print(f"\nTrend Prediction:")

    if value < 25:
        print("  📉 EXTREME FEAR → Potential BUY opportunity")
        print("  Historical pattern: Fear often precedes rallies")
        prediction = "BULLISH"
    elif value < 50:
        print("  😰 FEAR → Cautiously BULLISH")
        print("  Market may be oversold")
        prediction = "NEUTRAL_BULLISH"
    elif value < 75:
        print("  😊 GREED → Cautiously BEARISH")
        print("  Market may be overbought")
        prediction = "NEUTRAL_BEARISH"
    else:
        print("  📈 EXTREME GREED → Potential SELL opportunity")
        print("  Historical pattern: Greed often precedes corrections")
        prediction = "BEARISH"

    return prediction


def save_results(fear_greed_data, correlation_df, trades_df):
    """Save results to JSON"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'latest_sentiment': {
            'value': fear_greed_data[0]['value'],
            'classification': fear_greed_data[0]['classification'],
            'date': str(fear_greed_data[0]['timestamp'].date())
        },
        'correlation_summary': {
            '1d': correlation_df['sentiment_score'].corr(correlation_df['price_change_1d']) if 'price_change_1d' in correlation_df.columns else None,
            '3d': correlation_df['sentiment_score'].corr(correlation_df['price_change_3d']) if 'price_change_3d' in correlation_df.columns else None,
            '7d': correlation_df['sentiment_score'].corr(correlation_df['price_change_7d']) if 'price_change_7d' in correlation_df.columns else None,
        },
        'trades': trades_df.to_dict('records') if trades_df is not None else []
    }

    filename = "bitcoin_sentiment_analysis_results.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✓ Results saved to: {filename}")


def main():
    """Main entry point"""
    print("=" * 80)
    print("BITCOIN SENTIMENT ANALYSIS - FEAR & GREED INDEX")
    print("=" * 80)
    print("\nUsing Alternative.me Crypto Fear & Greed Index")
    print("Free API - No authentication required")
    print("=" * 80)

    # Fetch Fear & Greed Index
    fear_greed_data = fetch_fear_greed_index()

    if fear_greed_data is None:
        print("\nERROR: Could not fetch sentiment data")
        return

    # Fetch Bitcoin price
    price_df = fetch_bitcoin_price(days=30)

    if price_df is None:
        print("\nERROR: Could not fetch price data")
        return

    # Correlate sentiment with price
    correlation_df = correlate_sentiment_with_price(fear_greed_data, price_df)

    if correlation_df is None:
        return

    # Test trading strategy
    trades_df = test_sentiment_trading_strategy(correlation_df)

    # Make current prediction
    prediction = make_prediction(fear_greed_data[0])

    print("\n" + "=" * 80)

    # Save results
    save_results(fear_greed_data, correlation_df, trades_df)


if __name__ == "__main__":
    main()

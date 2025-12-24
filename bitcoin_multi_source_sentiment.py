#!/usr/bin/env python3
"""
Bitcoin Multi-Source Sentiment Analysis
Enhanced version combining:
1. Fear & Greed Index (Alternative.me)
2. Reddit sentiment (no auth required)
3. News sentiment (optional)

Based on code from bitcoin-trading-advisor repository
"""
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class MultiSourceSentimentAnalyzer:
    """Analyze sentiment from multiple sources"""

    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()

    def fetch_fear_greed_index(self):
        """Fetch Crypto Fear & Greed Index"""
        print("\n📊 Fetching Fear & Greed Index...")

        try:
            url = "https://api.alternative.me/fng/?limit=30"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    latest = data['data'][0]
                    print(f"✓ Fear & Greed: {latest['value']} ({latest['value_classification']})")

                    return {
                        'value': int(latest['value']),
                        'classification': latest['value_classification'],
                        'normalized_score': (int(latest['value']) - 50) / 50
                    }
        except Exception as e:
            print(f"✗ Failed to fetch Fear & Greed: {e}")

        return None

    def fetch_reddit_posts(self, subreddit='Bitcoin', limit=25):
        """
        Fetch Reddit posts using public JSON API (no authentication required)
        Based on bitcoin-trading-advisor implementation
        """
        print(f"\n🔴 Fetching Reddit r/{subreddit} posts...")

        try:
            # Use Reddit's public JSON API
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; BitcoinSentimentBot/1.0)'}

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                posts = []
                for post in data['data']['children']:
                    post_data = post['data']

                    # Filter for Bitcoin-related content
                    if any(keyword in post_data['title'].lower() for keyword in ['btc', 'bitcoin', 'crypto']):
                        posts.append({
                            'title': post_data['title'],
                            'text': post_data.get('selftext', ''),
                            'score': post_data['score'],
                            'num_comments': post_data['num_comments'],
                            'created': datetime.fromtimestamp(post_data['created_utc'])
                        })

                print(f"✓ Found {len(posts)} relevant posts")
                return posts

        except Exception as e:
            print(f"✗ Failed to fetch Reddit: {e}")

        return []

    def analyze_reddit_sentiment(self, posts):
        """Analyze sentiment of Reddit posts using VADER"""
        if not posts:
            return None

        print(f"\n🔍 Analyzing {len(posts)} Reddit posts...")

        sentiments = []

        for post in posts:
            # Combine title and text
            full_text = f"{post['title']} {post['text']}"

            # Get VADER sentiment
            scores = self.vader.polarity_scores(full_text)
            compound = scores['compound']

            # Weight by engagement (score + comments)
            weight = np.log1p(post['score']) * np.log1p(post['num_comments'])

            sentiments.append({
                'compound': compound,
                'weight': weight,
                'title': post['title'][:60]
            })

        # Calculate weighted average
        total_weight = sum(s['weight'] for s in sentiments)
        if total_weight == 0:
            weighted_sentiment = 0
        else:
            weighted_sentiment = sum(s['compound'] * s['weight'] for s in sentiments) / total_weight

        # Count sentiment distribution
        positive = sum(1 for s in sentiments if s['compound'] > 0.05)
        negative = sum(1 for s in sentiments if s['compound'] < -0.05)
        neutral = len(sentiments) - positive - negative

        print(f"✓ Sentiment analyzed:")
        print(f"  Positive: {positive} ({positive/len(sentiments)*100:.1f}%)")
        print(f"  Negative: {negative} ({negative/len(sentiments)*100:.1f}%)")
        print(f"  Neutral: {neutral} ({neutral/len(sentiments)*100:.1f}%)")
        print(f"  Weighted score: {weighted_sentiment:+.3f}")

        return {
            'weighted_sentiment': weighted_sentiment,
            'positive_pct': positive / len(sentiments) * 100,
            'negative_pct': negative / len(sentiments) * 100,
            'total_posts': len(sentiments),
            'top_posts': sentiments[:5]
        }

    def fetch_bitcoin_price(self, days=30):
        """Fetch Bitcoin price data"""
        print(f"\n💰 Fetching Bitcoin price ({days} days)...")

        try:
            btc = yf.Ticker("BTC-USD")
            df = btc.history(period=f"{days}d", interval="1d")

            print(f"✓ Current price: ${df['Close'].iloc[-1]:,.2f}")
            return df

        except Exception as e:
            print(f"✗ Failed to fetch price: {e}")
            return None

    def calculate_combined_sentiment(self, fear_greed, reddit_sentiment):
        """
        Combine Fear & Greed and Reddit sentiment into unified score

        Weight distribution:
        - Fear & Greed: 60% (professional index)
        - Reddit: 40% (community sentiment)
        """
        if fear_greed is None and reddit_sentiment is None:
            return None

        scores = []
        weights = []

        # Fear & Greed (if available)
        if fear_greed:
            scores.append(fear_greed['normalized_score'])
            weights.append(0.6)

        # Reddit (if available)
        if reddit_sentiment:
            scores.append(reddit_sentiment['weighted_sentiment'])
            weights.append(0.4)

        # Calculate weighted average
        combined_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)

        return combined_score

    def generate_trading_signal(self, combined_score, fear_greed, reddit_sentiment):
        """Generate trading signal based on combined sentiment"""
        print("\n" + "=" * 80)
        print("TRADING SIGNAL")
        print("=" * 80)

        # Show individual components
        print("\nSentiment Components:")

        if fear_greed:
            print(f"  Fear & Greed: {fear_greed['value']}/100 ({fear_greed['classification']})")
            print(f"    Normalized: {fear_greed['normalized_score']:+.3f}")

        if reddit_sentiment:
            print(f"  Reddit Sentiment: {reddit_sentiment['weighted_sentiment']:+.3f}")
            print(f"    Positive posts: {reddit_sentiment['positive_pct']:.1f}%")

        print(f"\n📊 Combined Score: {combined_score:+.3f}")

        # Generate signal
        if combined_score < -0.3:
            signal = "STRONG BUY"
            emoji = "📉📉"
            explanation = "Extreme fear - contrarian buy opportunity"
        elif combined_score < -0.1:
            signal = "BUY"
            emoji = "📉"
            explanation = "Fear in market - potential entry point"
        elif combined_score > 0.3:
            signal = "STRONG SELL"
            emoji = "📈📈"
            explanation = "Extreme greed - contrarian sell opportunity"
        elif combined_score > 0.1:
            signal = "SELL"
            emoji = "📈"
            explanation = "Greed in market - consider taking profits"
        else:
            signal = "HOLD"
            emoji = "➖"
            explanation = "Neutral sentiment - wait for clearer signal"

        print(f"\n{emoji} Signal: {signal}")
        print(f"Reason: {explanation}")

        print("=" * 80)

        return {
            'signal': signal,
            'score': combined_score,
            'explanation': explanation
        }

    def run_analysis(self):
        """Run complete multi-source sentiment analysis"""
        print("=" * 80)
        print("BITCOIN MULTI-SOURCE SENTIMENT ANALYSIS")
        print("=" * 80)
        print("\nSources:")
        print("  1. Fear & Greed Index (Alternative.me)")
        print("  2. Reddit r/Bitcoin + r/CryptoCurrency")
        print("=" * 80)

        results = {
            'timestamp': datetime.now().isoformat(),
            'sources': {}
        }

        # Fetch Fear & Greed
        fear_greed = self.fetch_fear_greed_index()
        if fear_greed:
            results['sources']['fear_greed'] = fear_greed

        # Fetch Reddit sentiment from multiple subreddits
        all_reddit_posts = []

        for subreddit in ['Bitcoin', 'CryptoCurrency']:
            posts = self.fetch_reddit_posts(subreddit, limit=25)
            all_reddit_posts.extend(posts)
            time.sleep(2)  # Rate limiting

        reddit_sentiment = None
        if all_reddit_posts:
            reddit_sentiment = self.analyze_reddit_sentiment(all_reddit_posts)
            results['sources']['reddit'] = reddit_sentiment

        # Fetch Bitcoin price
        price_df = self.fetch_bitcoin_price(days=30)

        if price_df is not None:
            current_price = price_df['Close'].iloc[-1]
            results['current_price'] = current_price

            # Calculate 7-day change
            if len(price_df) >= 7:
                week_ago_price = price_df['Close'].iloc[-7]
                week_change = (current_price - week_ago_price) / week_ago_price * 100
                results['7d_price_change'] = week_change

                print(f"\n📈 7-day change: {week_change:+.2f}%")

        # Calculate combined sentiment
        combined_score = self.calculate_combined_sentiment(fear_greed, reddit_sentiment)

        if combined_score is not None:
            results['combined_sentiment'] = combined_score

            # Generate trading signal
            signal = self.generate_trading_signal(combined_score, fear_greed, reddit_sentiment)
            results['signal'] = signal

            # Save results
            self.save_results(results)

        else:
            print("\n❌ Could not calculate sentiment (no data sources available)")

        return results

    def save_results(self, results):
        """Save results to JSON"""
        filename = "bitcoin_multi_source_sentiment_results.json"

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n✓ Results saved to: {filename}")


def main():
    """Main entry point"""
    analyzer = MultiSourceSentimentAnalyzer()
    results = analyzer.run_analysis()


if __name__ == "__main__":
    main()

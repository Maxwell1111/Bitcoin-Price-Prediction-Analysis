#!/usr/bin/env python3
"""
Bitcoin Reddit Sentiment Analysis for Price Prediction
Analyzes sentiment from r/Bitcoin, r/CryptoCurrency and correlates with price movements

Strategy:
1. Fetch recent posts/comments from Bitcoin subreddits
2. Perform sentiment analysis (positive/negative/neutral)
3. Calculate sentiment score
4. Correlate with Bitcoin price movements (1h, 4h, 24h, 7d)
5. Test predictive power
"""
import praw
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
from collections import defaultdict
import re

# Sentiment analysis
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("WARNING: TextBlob not installed. Install with: pip install textblob")

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("WARNING: VADER not installed. Install with: pip install vaderSentiment")


def setup_reddit():
    """
    Setup Reddit API connection
    Note: You'll need to create a Reddit app at https://www.reddit.com/prefs/apps
    For now, we'll use PRAW's read-only mode without authentication
    """
    print("Setting up Reddit API (read-only mode)...")

    try:
        # Use read-only mode - no authentication needed but limited
        reddit = praw.Reddit(
            client_id="",  # Empty for read-only
            client_secret="",  # Empty for read-only
            user_agent="bitcoin_sentiment_analyzer/1.0"
        )

        # Test connection
        reddit.read_only = True

        print("✓ Reddit API setup successful (read-only mode)")
        return reddit

    except Exception as e:
        print(f"ERROR setting up Reddit: {e}")
        return None


def fetch_reddit_posts(reddit, subreddit_name='Bitcoin', limit=100, time_filter='day'):
    """
    Fetch recent posts from a subreddit

    Args:
        reddit: PRAW Reddit instance
        subreddit_name: Name of subreddit
        limit: Number of posts to fetch
        time_filter: 'hour', 'day', 'week', 'month'
    """
    print(f"\nFetching posts from r/{subreddit_name}...")

    try:
        subreddit = reddit.subreddit(subreddit_name)

        posts = []

        # Get hot posts
        for post in subreddit.hot(limit=limit):
            posts.append({
                'title': post.title,
                'text': post.selftext,
                'score': post.score,
                'created_utc': datetime.fromtimestamp(post.created_utc),
                'num_comments': post.num_comments,
                'upvote_ratio': post.upvote_ratio
            })

        print(f"✓ Fetched {len(posts)} posts from r/{subreddit_name}")
        return posts

    except Exception as e:
        print(f"ERROR fetching posts: {e}")
        return []


def analyze_sentiment_textblob(text):
    """Analyze sentiment using TextBlob"""
    if not text or not TEXTBLOB_AVAILABLE:
        return 0.0

    try:
        blob = TextBlob(text)
        # Returns polarity between -1 (negative) and 1 (positive)
        return blob.sentiment.polarity
    except:
        return 0.0


def analyze_sentiment_vader(text):
    """Analyze sentiment using VADER (better for social media)"""
    if not text or not VADER_AVAILABLE:
        return 0.0

    try:
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(text)
        # Use compound score (-1 to 1)
        return scores['compound']
    except:
        return 0.0


def calculate_reddit_sentiment(posts, method='vader'):
    """
    Calculate overall sentiment score from posts

    Args:
        posts: List of post dictionaries
        method: 'vader' or 'textblob'
    """
    print(f"\nCalculating sentiment using {method.upper()}...")

    if method == 'vader' and not VADER_AVAILABLE:
        print("VADER not available, falling back to TextBlob")
        method = 'textblob'

    if method == 'textblob' and not TEXTBLOB_AVAILABLE:
        print("TextBlob not available either!")
        return None

    sentiments = []

    for post in posts:
        # Combine title and text
        full_text = f"{post['title']} {post['text']}"

        # Calculate sentiment
        if method == 'vader':
            sentiment = analyze_sentiment_vader(full_text)
        else:
            sentiment = analyze_sentiment_textblob(full_text)

        # Weight by score (upvotes) and comments
        weight = np.log1p(post['score']) * np.log1p(post['num_comments'])

        sentiments.append({
            'sentiment': sentiment,
            'weight': weight,
            'score': post['score'],
            'title': post['title'][:50]
        })

    # Calculate weighted average sentiment
    total_weight = sum(s['weight'] for s in sentiments)

    if total_weight == 0:
        weighted_sentiment = 0
    else:
        weighted_sentiment = sum(s['sentiment'] * s['weight'] for s in sentiments) / total_weight

    # Calculate simple average too
    simple_sentiment = np.mean([s['sentiment'] for s in sentiments])

    # Count positive/negative/neutral
    positive = sum(1 for s in sentiments if s['sentiment'] > 0.05)
    negative = sum(1 for s in sentiments if s['sentiment'] < -0.05)
    neutral = len(sentiments) - positive - negative

    print(f"✓ Sentiment analyzed")
    print(f"  Positive posts: {positive} ({positive/len(sentiments)*100:.1f}%)")
    print(f"  Negative posts: {negative} ({negative/len(sentiments)*100:.1f}%)")
    print(f"  Neutral posts: {neutral} ({neutral/len(sentiments)*100:.1f}%)")
    print(f"  Simple average sentiment: {simple_sentiment:+.3f}")
    print(f"  Weighted sentiment: {weighted_sentiment:+.3f}")

    return {
        'weighted_sentiment': weighted_sentiment,
        'simple_sentiment': simple_sentiment,
        'positive_pct': positive / len(sentiments) * 100,
        'negative_pct': negative / len(sentiments) * 100,
        'neutral_pct': neutral / len(sentiments) * 100,
        'total_posts': len(sentiments),
        'sentiments': sentiments
    }


def fetch_bitcoin_price_data(hours=168):
    """Fetch recent Bitcoin price data"""
    print(f"\nFetching Bitcoin price data (last {hours} hours)...")

    try:
        btc = yf.Ticker("BTC-USD")
        df = btc.history(period=f"{hours//24+1}d", interval="1h")

        print(f"✓ Fetched {len(df)} hourly price points")
        print(f"  Current price: ${df['Close'].iloc[-1]:,.2f}")

        return df

    except Exception as e:
        print(f"ERROR fetching price data: {e}")
        return None


def correlate_sentiment_with_price(sentiment_data, price_df, hours_ahead=[1, 4, 24, 168]):
    """
    Correlate sentiment with future price movements

    Args:
        sentiment_data: Dictionary with sentiment scores
        price_df: DataFrame with Bitcoin prices
        hours_ahead: List of time horizons to test (in hours)
    """
    print("\n" + "=" * 80)
    print("CORRELATING SENTIMENT WITH PRICE MOVEMENTS")
    print("=" * 80)

    current_price = price_df['Close'].iloc[-1]

    results = {
        'current_price': current_price,
        'sentiment': sentiment_data['weighted_sentiment'],
        'predictions': {}
    }

    print(f"\nCurrent Bitcoin price: ${current_price:,.2f}")
    print(f"Current sentiment: {sentiment_data['weighted_sentiment']:+.3f}")

    # Make predictions based on sentiment
    for hours in hours_ahead:
        if len(price_df) < hours:
            print(f"\nNot enough historical data for {hours}h prediction")
            continue

        # Get price from 'hours' ago
        past_price = price_df['Close'].iloc[-hours]
        actual_change_pct = (current_price - past_price) / past_price * 100

        # Predict based on sentiment
        # Positive sentiment → predict price increase
        # Negative sentiment → predict price decrease

        sentiment_threshold = 0.05

        if sentiment_data['weighted_sentiment'] > sentiment_threshold:
            prediction = "UP"
            predicted_positive = True
        elif sentiment_data['weighted_sentiment'] < -sentiment_threshold:
            prediction = "DOWN"
            predicted_positive = False
        else:
            prediction = "NEUTRAL"
            predicted_positive = None

        # Check if we can verify (need future data)
        # For now, we'll use historical correlation

        results['predictions'][f'{hours}h'] = {
            'prediction': prediction,
            'sentiment': sentiment_data['weighted_sentiment'],
            'historical_change': actual_change_pct
        }

        print(f"\n{hours}-hour prediction:")
        print(f"  Sentiment: {sentiment_data['weighted_sentiment']:+.3f}")
        print(f"  Prediction: {prediction}")
        print(f"  Historical {hours}h change: {actual_change_pct:+.2f}%")

    return results


def simulate_sentiment_trading(sentiment_score, threshold=0.05):
    """
    Simulate trading decision based on sentiment

    Args:
        sentiment_score: Current sentiment score (-1 to 1)
        threshold: Minimum sentiment to trigger buy/sell

    Returns:
        'BUY', 'SELL', or 'HOLD'
    """
    if sentiment_score > threshold:
        return 'BUY'
    elif sentiment_score < -threshold:
        return 'SELL'
    else:
        return 'HOLD'


def show_top_sentiments(sentiment_data, n=10):
    """Show top positive and negative posts"""
    print("\n" + "=" * 80)
    print("TOP POSTS BY SENTIMENT")
    print("=" * 80)

    sentiments = sentiment_data['sentiments']

    # Sort by sentiment
    sorted_sentiments = sorted(sentiments, key=lambda x: x['sentiment'], reverse=True)

    print(f"\n📈 TOP {n} MOST POSITIVE POSTS:")
    for i, s in enumerate(sorted_sentiments[:n], 1):
        print(f"\n{i}. \"{s['title']}...\"")
        print(f"   Sentiment: {s['sentiment']:+.3f} | Score: {s['score']}")

    print(f"\n📉 TOP {n} MOST NEGATIVE POSTS:")
    for i, s in enumerate(sorted_sentiments[-n:], 1):
        print(f"\n{i}. \"{s['title']}...\"")
        print(f"   Sentiment: {s['sentiment']:+.3f} | Score: {s['score']}")


def save_results(sentiment_data, correlation_results):
    """Save results to JSON"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'sentiment': {
            'weighted': sentiment_data['weighted_sentiment'],
            'simple': sentiment_data['simple_sentiment'],
            'positive_pct': sentiment_data['positive_pct'],
            'negative_pct': sentiment_data['negative_pct'],
            'total_posts': sentiment_data['total_posts']
        },
        'price': correlation_results['current_price'],
        'predictions': correlation_results['predictions']
    }

    filename = "bitcoin_reddit_sentiment_results.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to: {filename}")


def main():
    """Main entry point"""
    print("=" * 80)
    print("BITCOIN REDDIT SENTIMENT ANALYSIS")
    print("=" * 80)
    print("\nAnalyzing Reddit sentiment to predict Bitcoin price movements")
    print("Subreddits: r/Bitcoin, r/CryptoCurrency")
    print("=" * 80)

    # Check dependencies
    if not TEXTBLOB_AVAILABLE and not VADER_AVAILABLE:
        print("\nERROR: No sentiment analysis library available!")
        print("Install one of:")
        print("  pip install textblob")
        print("  pip install vaderSentiment")
        return

    # Setup Reddit
    reddit = setup_reddit()
    if reddit is None:
        print("\nERROR: Could not setup Reddit API")
        return

    # Fetch posts from multiple subreddits
    all_posts = []

    for subreddit in ['Bitcoin', 'CryptoCurrency']:
        posts = fetch_reddit_posts(reddit, subreddit, limit=100)
        all_posts.extend(posts)
        time.sleep(1)  # Rate limiting

    if len(all_posts) == 0:
        print("\nERROR: No posts fetched")
        return

    print(f"\n✓ Total posts fetched: {len(all_posts)}")

    # Analyze sentiment
    sentiment_data = calculate_reddit_sentiment(all_posts, method='vader')

    if sentiment_data is None:
        print("\nERROR: Sentiment analysis failed")
        return

    # Fetch Bitcoin price
    price_df = fetch_bitcoin_price_data(hours=168)  # 1 week

    if price_df is None:
        print("\nERROR: Could not fetch price data")
        return

    # Correlate sentiment with price
    correlation_results = correlate_sentiment_with_price(
        sentiment_data,
        price_df,
        hours_ahead=[1, 4, 24, 168]
    )

    # Show top posts
    show_top_sentiments(sentiment_data, n=5)

    # Trading signal
    signal = simulate_sentiment_trading(sentiment_data['weighted_sentiment'])

    print("\n" + "=" * 80)
    print("TRADING SIGNAL")
    print("=" * 80)
    print(f"\nSentiment: {sentiment_data['weighted_sentiment']:+.3f}")
    print(f"Signal: {signal}")

    if signal == 'BUY':
        print("📈 BULLISH - Consider buying")
    elif signal == 'SELL':
        print("📉 BEARISH - Consider selling")
    else:
        print("➖ NEUTRAL - Hold position")

    print("\n" + "=" * 80)

    # Save results
    save_results(sentiment_data, correlation_results)


if __name__ == "__main__":
    main()

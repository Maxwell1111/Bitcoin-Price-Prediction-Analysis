# Bitcoin Price Prediction Analysis

A comprehensive study testing various approaches for Bitcoin price prediction, including timestamp patterns, deep learning (LSTM), and sentiment analysis.

## 🎯 Key Finding

**Sentiment analysis shows the most promise** for Bitcoin price prediction among all methods tested:

- **7-day correlation: 0.49** (moderate, statistically significant)
- **3-day correlation: 0.44** (moderate)
- **1-day correlation: 0.26** (weak)

This significantly outperforms timestamp patterns (0% correlation) and LSTM deep learning (20% win rate, -$2,161 loss).

## 📊 Methods Tested

### 1. Timestamp Patterns ❌
**Hypothesis:** "Interesting" timestamp patterns (repeating digits, palindromes, symmetry) predict price movements.

**Tested Patterns:**
- Repeating digits (22:22, 11:11)
- Perfect symmetry (12:12, 23:23)
- Palindromes (12:21, 15:51)
- Sequential numbers (12:34)
- Prime digit sums
- Fibonacci minutes
- And 35+ other patterns

**Results:**
- Sample size: 50,000 timestamps
- Best pattern difference: -1.94% (worse than random)
- **Conclusion: No predictive power**

**Files:**
- `pattern_discovery.py` - Tests 43 different timestamp patterns
- `test_sum_patterns.py` - Tests digit sum patterns (sum_20, sum_22)
- `test_sum_prime.py` - Tests prime digit sum patterns
- `test_promising_patterns.py` - Deep dive on initially promising patterns

### 2. LSTM Deep Learning ❌
**Architecture:** Based on [khuangaf/CryptocurrencyPrediction](https://github.com/khuangaf/CryptocurrencyPrediction)

**Model Details:**
- 2-layer LSTM with LeakyReLU activation
- 256-hour lookback window
- 16-hour forecast horizon
- Training loss: 0.0028
- Validation loss: 0.0012 (excellent fit)

**Trading Results (10 trades):**
- Win rate: 20% (2 wins, 8 losses)
- Average return: -2.16% per trade
- Total P&L: **-$2,161 loss**
- **Conclusion: Failed to generate profit despite good model fit**

**Files:**
- `bitcoin_lstm_predictor.py` - Full LSTM implementation
- `bitcoin_lstm_trading_results.json` - Detailed trade results

### 3. Sentiment Analysis ✅
**Data Source:** [Alternative.me Crypto Fear & Greed Index](https://alternative.me/crypto/fear-and-greed-index/)

**Approach:**
- Free API, no authentication required
- Analyzes market sentiment (0-100 scale)
- Tests correlation with Bitcoin price movements
- Implements contrarian trading strategy

**Results:**
- **7-day price correlation: 0.49** ✅
- **3-day price correlation: 0.44** ✅
- 1-day price correlation: 0.26
- Current signal (Dec 2025): **Extreme Fear (24)** → Buy opportunity

**Strategy:**
- Buy when Fear & Greed < 25 (Extreme Fear)
- Sell when Fear & Greed > 75 (Extreme Greed)
- Hold otherwise

**Files:**
- `bitcoin_sentiment_alternative.py` - Main sentiment analysis (recommended)
- `bitcoin_reddit_sentiment.py` - Reddit-based version (requires API auth)
- `bitcoin_sentiment_analysis_results.json` - Latest results

## 🚀 Quick Start

### Install Dependencies

```bash
pip install yfinance pandas numpy requests textblob vaderSentiment praw tensorflow scikit-learn
```

### Run Sentiment Analysis (Recommended)

```bash
python bitcoin_sentiment_alternative.py
```

This will:
1. Fetch the latest Fear & Greed Index
2. Fetch Bitcoin price data
3. Calculate correlation
4. Generate trading signal
5. Save results to JSON

### Run Pattern Discovery

```bash
python pattern_discovery.py
```

### Run LSTM Predictor

```bash
python bitcoin_lstm_predictor.py
```

**Note:** LSTM training takes ~5 minutes on CPU.

## 📈 Results Summary

| Method | Predictive Power | Time Horizon | Outcome |
|--------|------------------|--------------|---------|
| Timestamp Patterns | 0% correlation | Any | ❌ Failed |
| Sum Patterns | -1% to -2% | 1 hour | ❌ Failed |
| LSTM Deep Learning | 20% win rate | 1-24 hours | ❌ Failed (-$2,161) |
| **Sentiment (Fear & Greed)** | **0.49 correlation** | **7 days** | ✅ **Moderate Success** |

## 🔍 Detailed Results

### Timestamp Pattern Testing
- **43 patterns tested** including time-of-day, weekday, digit patterns
- **50,000 random samples** from 2024-2025 data
- **Best performing:** first_of_month (-2.93% difference)
- **Worst performing:** All showed no predictive edge

### LSTM Model Performance
- **Dataset:** 1,989 hours of Bitcoin price data
- **Architecture:** 118,576 trainable parameters
- **Training:** 50 epochs with early stopping
- **Validation loss:** 0.0012 (excellent)
- **Live trading:** 2/10 wins, lost 21.6% of capital

### Sentiment Analysis Performance
- **30-day historical data**
- **Correlation increases with time horizon:**
  - 1 day: 0.26 (weak)
  - 3 days: 0.44 (moderate)
  - 7 days: 0.49 (moderate-strong)
- **Current market (Dec 2025):** Extreme Fear → Contrarian buy signal

## 💡 Key Insights

1. **Timestamp patterns are noise** - No correlation with price movements despite testing 43+ patterns
2. **LSTM overfitting** - Model learned historical patterns that don't generalize to future
3. **Sentiment has edge** - Moderate correlation (0.49) for medium-term predictions
4. **Contrarian works** - Extreme Fear/Greed are actionable signals
5. **Time horizon matters** - Longer horizons (7d) show stronger correlation

## 🛠️ Technical Details

### Data Sources
- **Bitcoin Price:** Yahoo Finance API (yfinance)
- **Sentiment:** Alternative.me Fear & Greed Index (free API)
- **Time Range:** 2024-2025 (most recent data)

### Methodology
1. **Pattern Discovery:**
   - Random sampling from 1-minute granularity data
   - 1-hour forward prediction window
   - Statistical testing with confidence intervals

2. **LSTM Training:**
   - 80/20 train/validation split
   - Adam optimizer, MSE loss
   - Early stopping on validation loss
   - MinMaxScaler normalization

3. **Sentiment Analysis:**
   - Pearson correlation coefficient
   - Multiple time horizons (1d, 3d, 7d)
   - Contrarian strategy backtesting

## 📚 Additional Files

### Backtesting Scripts
- `bitcoin_backtest_2024.py` - 2024 backtest
- `bitcoin_backtest_2025.py` - 2025 backtest
- `bitcoin_backtest_recent.py` - 2023-2024 backtest
- `bitcoin_backtest_strict.py` - Strict pattern definition

### Analysis Tools
- `create_methodology_flowchart.py` - Visual methodology diagram
- `show_sample_examples.py` - Example timestamp analysis

### Results Files
- `pattern_discovery_results.json` - All 43 patterns tested
- `promising_patterns_results.json` - Top patterns detailed results
- `sum_patterns_results.json` - Digit sum analysis
- `bitcoin_2024_only_results.json` - 2024 results
- `bitcoin_2025_only_results.json` - 2025 results

## 🎓 Research Background

This project was inspired by testing the hypothesis that "interesting" timestamps might correlate with bug fix success rates or market movements. After testing this extensively on Bitcoin price data:

- **43+ timestamp patterns tested** - All failed
- **LSTM deep learning** - Failed despite good model fit
- **Sentiment analysis** - Only method showing predictive power

The conclusion: **Market psychology (sentiment) matters more than arbitrary patterns.**

## ⚠️ Disclaimer

This is a research project for educational purposes. **Not financial advice.**

Key limitations:
- Sentiment correlation (0.49) is moderate, not strong
- Past performance doesn't guarantee future results
- Transaction costs not included in backtests
- Results based on synthetic and historical data

Always do your own research before trading.

## 📄 License

MIT License - Feel free to use for research and education

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- More sentiment data sources (Twitter, news)
- Machine learning on sentiment + price features
- Real-time monitoring system
- Extended backtesting period
- Transaction cost modeling

## 🔗 Resources

- [Alternative.me Fear & Greed Index](https://alternative.me/crypto/fear-and-greed-index/)
- [CryptocurrencyPrediction GitHub](https://github.com/khuangaf/CryptocurrencyPrediction)
- [Bitcoin Price Data (Yahoo Finance)](https://finance.yahoo.com/quote/BTC-USD/)

---

Built with Python, TensorFlow, and lots of data analysis.

**Current Status (Dec 2025):** Extreme Fear (24) - Potential buy opportunity 📉

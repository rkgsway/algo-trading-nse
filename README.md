# NSE Algorithmic Trading Framework

A complete Python framework for algorithmic trading on NSE (National Stock Exchange of India) using Angel One broker API.

## Features

- 📊 **Real-time Data**: Live market data via Angel One SmartAPI WebSocket
- 🔄 **Multiple Strategies**: Moving Average, RSI, MACD, Bollinger Bands
- 📈 **Backtesting**: Historical data backtesting engine
- 🎯 **Order Management**: Automated order placement and tracking
- 💰 **Portfolio Management**: Real-time P&L tracking
- 🛡️ **Risk Management**: Stop loss, take profit, position sizing
- 📊 **Analytics & Logging**: Detailed trade logs and performance metrics

## Architecture

```
algo-trading-nse/
├── config/                 # Configuration files
│   └── settings.py
├── data/                   # Data fetching & processing
│   ├── angel_api.py
│   ├── data_fetcher.py
│   └── cache.py
├── strategies/             # Trading strategies
│   ├── base_strategy.py
│   ├── moving_average.py
│   ├── rsi_strategy.py
│   └── macd_strategy.py
├── backtesting/            # Backtesting engine
│   ├── backtest.py
│   └── performance.py
├── execution/              # Order execution
│   ├── order_manager.py
│   └── risk_manager.py
├── utils/                  # Utilities
│   ├── logger.py
│   ├── helpers.py
│   └── telegram_notifier.py
├── main.py                 # Main trading bot
├── requirements.txt
└── .env.example
```

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/rkgsway/algo-trading-nse.git
cd algo-trading-nse
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Angel One credentials**
```bash
cp .env.example .env
# Edit .env with your Angel One API credentials
```

4. **Run the trading bot**
```bash
python main.py
```

## Angel One Setup

### Get API Credentials

1. Open Angel One app → Settings
2. Go to "API" or "Developer Settings"
3. Generate API key and get auth token
4. Note your Client Code, API Key, and Auth Token

### Environment Variables

```env
ANGEL_API_KEY=your_api_key
ANGEL_CLIENT_CODE=your_client_code
ANGEL_PASSWORD=your_password
ANGEL_TOTP=your_2fa_totp  # If enabled

# Trading Configuration
LIVE_TRADING=false  # Set to true for live trading
MAX_POSITION_SIZE=10000
RISK_PERCENTAGE=2
```

## Quick Start Example

```python
from trading_bot import TradingBot
from strategies.moving_average import MovingAverageStrategy

# Initialize bot
bot = TradingBot()

# Create strategy
strategy = MovingAverageStrategy(
    symbol="SBIN",
    timeframe="5min",
    fast_period=20,
    slow_period=50
)

# Run strategy
bot.run_strategy(strategy, live=False)  # backtesting
```

## Supported Instruments

- **Equities**: All NSE listed stocks (SBIN, INFY, TCS, etc.)
- **Indices**: NIFTY 50, NIFTY BANK, SENSEX, etc.
- **Futures & Options**: NFO contracts (optional)

## Dependencies

- `smartapi-python` - Angel One API
- `pandas` - Data processing
- `numpy` - Numerical computations
- `ta` - Technical analysis
- `pytz` - Timezone handling
- `python-dotenv` - Environment configuration
- `requests` - HTTP requests
- `schedule` - Task scheduling
- `websocket-client` - WebSocket connections

## Best Practices

1. **Always backtest** before live trading
2. **Start small** - use minimal position sizes
3. **Use stop losses** - never risk more than 2% per trade
4. **Monitor logs** - check trading logs regularly
5. **Weekend testing** - test on historical data first
6. **Paper trading** - use Angel One paper trading mode

## Risk Disclaimer

This is an educational project. Algorithmic trading involves significant risk.

⚠️ **Important:**
- Past performance ≠ future results
- Market conditions can change rapidly
- Test thoroughly before live trading
- Start with small positions
- Always maintain risk management rules

## Support & Resources

- [Angel One SmartAPI Docs](https://smartapi.angelbroking.com/)
- [NSE Website](https://www.nseindia.com)
- [Python TA-Lib](https://github.com/mrjbq7/ta-lib)

## License

MIT License - See LICENSE file

## Contributing

Contributions welcome! Please submit pull requests with improvements.

---

**Disclaimer**: This framework is for educational and research purposes only. The author is not responsible for trading losses or financial damage.
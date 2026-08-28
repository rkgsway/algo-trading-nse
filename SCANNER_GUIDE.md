# Multi-Symbol Scanner Guide

## Overview

The Multi-Symbol Scanner allows you to scan **210+ FnO stocks** and **major indices** (NIFTY, BANKNIFTY, SENSEX, etc.) simultaneously to identify trading signals in real-time.

---

## 📊 What You Can Scan

### **210+ FnO Stocks** including:
- **NIFTY 50 Holdings** - RELIANCE, TCS, INFY, SBIN, ICICIBANK, BAJAJFINSV, LT, MARUTI, HDFC, WIPRO, etc.
- **Banking Sector** - SBIN, ICICIBANK, KOTAKBANK, AXISBANK, INDUSIND, AUBANK, BANKBARODA
- **IT Sector** - TCS, INFY, WIPRO, HCLTECH, TECHM, LTIM, MINDTREE
- **Pharma** - SUNPHARMA, DRREDDY, LUPIN, CIPLA, ALKEM, ABBOTINDIA, BIOCON
- **Auto** - MARUTI, BAJAJ-AUTO, EICHERMOT, HEROMOTOCO, TATAMOTORS, MAHINDRA
- **FMCG** - HINDUNILVR, BRITANNIA, ITC, TATACONSUM, NESTLEIND, COLPAL
- **Energy** - RELIANCE, BPCL, ONGC, POWERGRID, NTPC, COAL, ADANIGREEN
- **Metals & Mining** - HINDALCO, JSWSTEEL, TATASTEELQ, NMDC, SAIL
- And 180+ more stocks...

### **Major Indices:**
- NIFTY 50 (NSE Broad Market)
- BANKNIFTY (Banking Index)
- NIFTY IT (IT Companies)
- NIFTY PHARMA (Pharmaceutical)
- NIFTY AUTO (Automotive)
- FINNIFTY (Financial)
- MIDCAP (Midcap Companies)
- SENSEX (BSE Benchmark)

---

## 🚀 Quick Start

### **1. Simple One-Time Scan**

```python
from scanner.multi_symbol_scanner import MultiSymbolScanner

# Create scanner
scanner = MultiSymbolScanner(
    max_workers=20,      # 20 parallel threads (for 210+ stocks)
    timeframe='5'        # 5-minute candles
)

# Scan all 210+ stocks + indices
signals = scanner.scan_all_symbols()

# Print results
scanner.print_signals_summary()
```

**Output:**
```
================================================================================
SCAN RESULTS - 2026-08-28 14:30:45
Total Symbols Scanned: 218 | Signals Found: 12
================================================================================

🟢 BUY SIGNALS (7)
================================================================================
Symbol          LTP         Volume          OI              Strategy
----------------================================================================
SBIN            540.50      1,500,000       50,000,000      Supertrend + RSI
INFY            1,850.25    800,000         35,000,000      Supertrend + RSI
TCS             3,250.75    600,000         25,000,000      Supertrend + RSI
...

🔴 SELL SIGNALS (5)
================================================================================
Symbol          LTP         Volume          OI              Strategy
================================================================================
RELIANCE        2,850.00    2,000,000       80,000,000      Supertrend + RSI
HDFC            2,450.50    900,000         40,000,000      Supertrend + RSI
...

================================================================================
SUMMARY: 7 Buy + 5 Sell = 12 Total Signals
================================================================================
```

---

### **2. Continuous Watching (Real-time Monitor)**

```python
from scanner.multi_symbol_scanner import MultiSymbolScanner

scanner = MultiSymbolScanner(max_workers=20, timeframe='5')

# Watch continuously for 1 hour, scanning every 60 seconds
scanner.watch_symbols(
    interval=60,        # Scan every 60 seconds
    duration=3600       # Run for 1 hour (3600 seconds)
)
```

**Output:**
```
--- Scan #1 at 14:30:00 ---
🎯 SIGNAL FOUND: SBIN            BUY 🟢       LTP: 540.50
🎯 SIGNAL FOUND: INFY            BUY 🟢       LTP: 1850.25
... [scan results]

--- Scan #2 at 14:31:00 ---
[Next scan results]
```

---

### **3. Scan Specific Symbols Only**

```python
# Scan only NIFTY 50 stocks
nifty50 = ['RELIANCE', 'TCS', 'INFY', 'SBIN', 'ICICIBANK', 'HDFC', 'WIPRO']
signals = scanner.scan_all_symbols(symbols=nifty50)

# Or scan only banking stocks
banking = ['SBIN', 'ICICIBANK', 'KOTAKBANK', 'AXISBANK', 'INDUSIND']
signals = scanner.scan_all_symbols(symbols=banking)

# Or scan only indices
indices = ['NIFTY', 'BANKNIFTY', 'NIFTY IT', 'SENSEX']
signals = scanner.scan_all_symbols(symbols=indices)
```

---

### **4. Export Results to CSV**

```python
# After scanning
scanner.scan_all_symbols()

# Export to CSV
scanner.export_signals_to_csv('trading_signals.csv')

# Creates 3 files:
# 1. trading_signals.csv - All signals
# 2. buy_signals_YYYYMMDD_HHMMSS.csv - Only buy signals
# 3. sell_signals_YYYYMMDD_HHMMSS.csv - Only sell signals
```

---

### **5. Get Sector-wise Signals**

```python
scanner.scan_all_symbols()

# Print signals grouped by sector
scanner.print_sector_summary()
```

**Output:**
```
================================================================================
SIGNALS BY SECTOR
================================================================================

Banking:
  BUY: 2, SELL: 1
    - SBIN            BUY 🟢       @ 540.50
    - ICICIBANK       BUY 🟢       @ 625.25
    - KOTAKBANK       SELL 🔴      @ 1850.75

IT:
  BUY: 1, SELL: 0
    - INFY            BUY 🟢       @ 1850.25

Pharma:
  BUY: 2, SELL: 2
    - SUNPHARMA       BUY 🟢       @ 750.50
    - DRREDDY         SELL 🔴      @ 1450.25
    ...

Energy:
  BUY: 1, SELL: 1
    - RELIANCE        SELL 🔴      @ 2850.00
    ...

================================================================================
SECTOR SUMMARY: 7 Buy + 5 Sell = 12 Total Signals
================================================================================
```

---

### **6. Get Statistics**

```python
scanner.scan_all_symbols()

# Get scan statistics
stats = scanner.get_scan_stats()

print(f"Total Symbols Scanned: {stats['total_scanned']}")
print(f"Total Signals Found: {stats['total_signals']}")
print(f"Buy Signals: {stats['buy_signals']}")
print(f"Sell Signals: {stats['sell_signals']}")
print(f"Buy/Sell Ratio: {stats['buy_sell_ratio']:.2f}")
```

---

### **7. Get Top Volume Signals**

```python
# Get signals with highest trading volume
top_signals = scanner.get_highest_volume_signals(limit=10)

for sig in top_signals:
    print(f"{sig['symbol']}: {sig['signal_name']} - Volume: {sig['volume']:,.0f}")
```

---

### **8. Convert Signals to DataFrame**

```python
# Get signals as pandas DataFrame
df = scanner.get_signals_dataframe()

print(df)
print(df.to_string())  # Pretty print

# Analyze
print(f"Average volume: {df['volume'].mean():,.0f}")
print(f"Symbols: {', '.join(df['symbol'].unique())}")
```

---

## 🔧 Advanced Usage

### **Custom Strategy with Scanner**

```python
from scanner.multi_symbol_scanner import MultiSymbolScanner
from strategies.institutional_strategies import VolumeProfileStrategy

scanner = MultiSymbolScanner(max_workers=20, timeframe='5')

# Use different strategy
strategy = VolumeProfileStrategy(
    symbol='DUMMY',  # Scanner will change this
    period=20,
    volume_threshold=1.5
)

signals = scanner.scan_all_symbols(strategy=strategy)
```

---

### **Scan During Market Hours Only**

```python
from datetime import datetime

scanner = MultiSymbolScanner(max_workers=20, timeframe='5')

# Check if market is open
now = datetime.now()
market_open = now.hour >= 9 and now.hour <= 15  # 9:15 AM to 3:30 PM IST

if market_open:
    signals = scanner.scan_all_symbols()
    scanner.print_signals_summary()
else:
    print("Market is closed!")
```

---

### **Alert System (Email/Telegram on Signal)**

```python
from scanner.multi_symbol_scanner import MultiSymbolScanner
import smtplib
from email.mime.text import MIMEText

scanner = MultiSymbolScanner(max_workers=20, timeframe='5')

signals = scanner.scan_all_symbols()

if signals:
    # Send email alert
    msg = MIMEText(f"Found {len(signals)} trading signals!\n\n")
    msg['Subject'] = f"Trading Alerts - {len(signals)} Signals"
    
    # Send to your email
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login('your_email@gmail.com', 'your_password')
    server.send_message(msg)
    server.quit()
    
    print(f"✓ Alert sent for {len(signals)} signals")
```

---

## 📈 Performance Optimization

### **Workers Parameter**

```python
# For 210+ stocks, use 20 workers
scanner = MultiSymbolScanner(max_workers=20)

# Scan time: ~30-60 seconds (depending on network)
# Each symbol: ~1-2 seconds

# If you want faster scanning, increase workers:
scanner = MultiSymbolScanner(max_workers=30)  # ~20-30 seconds

# But not too many (API rate limiting):
# Max recommended: 50 workers
```

### **Timeframe Selection**

```python
# 5-minute candles (most active signals)
scanner = MultiSymbolScanner(timeframe='5')

# 15-minute candles (more stable signals)
scanner = MultiSymbolScanner(timeframe='15')

# Hourly candles (longer-term signals)
scanner = MultiSymbolScanner(timeframe='60')
```

---

## 🎯 Real-world Example: Morning Scan

```python
from scanner.multi_symbol_scanner import MultiSymbolScanner
from datetime import datetime
import time

def morning_market_scan():
    """Scan market every 5 minutes during market hours"""
    
    scanner = MultiSymbolScanner(max_workers=20, timeframe='5')
    
    print(f"Starting morning market scan at {datetime.now().strftime('%H:%M:%S')}")
    
    # Market opens at 9:15 AM, scan every 5 minutes till 10:00 AM
    for minute in range(0, 60, 5):
        time.sleep(5 * 60)  # Wait 5 minutes
        
        signals = scanner.scan_all_symbols()
        
        print(f"\n{datetime.now().strftime('%H:%M:%S')} - Scan Results:")
        print(f"  Total Signals: {len(signals)}")
        
        if signals:
            buy = len([s for s in signals if s['signal'] == 1])
            sell = len([s for s in signals if s['signal'] == -1])
            print(f"  Buy: {buy}, Sell: {sell}")
            
            # Print top signals
            top = scanner.get_highest_volume_signals(limit=3)
            for sig in top:
                print(f"    - {sig['symbol']}: {sig['signal_name']} @ {sig['ltp']}")
            
            # Export to file
            scanner.export_signals_to_csv(f"signals_{datetime.now().strftime('%H%M%S')}.csv")

# Run scan
morning_market_scan()
```

---

## 🚨 Common Issues & Solutions

### **Issue 1: API Rate Limiting**

**Problem:** Getting "Too many requests" error

**Solution:**
```python
# Reduce workers or add delay
scanner = MultiSymbolScanner(max_workers=10)  # Instead of 20

# Or scan in batches
import time
all_symbols = scanner.get_all_scan_symbols()
batch_size = 50

for i in range(0, len(all_symbols), batch_size):
    batch = all_symbols[i:i+batch_size]
    signals = scanner.scan_all_symbols(symbols=batch)
    time.sleep(2)  # Wait between batches
```

---

### **Issue 2: Slow Scanning**

**Problem:** Taking too long to scan all symbols

**Solution:**
```python
# Increase workers
scanner = MultiSymbolScanner(max_workers=30)

# Or scan specific sectors instead of all
banking = ['SBIN', 'ICICIBANK', 'KOTAKBANK', 'AXISBANK', 'INDUSIND']
signals = scanner.scan_all_symbols(symbols=banking)
```

---

### **Issue 3: No Signals Found**

**Problem:** Scanner returns empty results

**Solutions:**
1. Check market is open (9:15 AM - 3:30 PM IST)
2. Verify symbols are correct
3. Check historical data availability
4. Try different timeframe (5 min vs 15 min)

```python
# Debug: Check individual symbol
quote = scanner.angel.get_quote('SBIN')
print(quote)  # Should show price data

# Check data fetching
data = scanner.data_fetcher.get_candles('SBIN', '5')
print(f"Data shape: {data.shape}")  # Should not be empty
```

---

## 📊 Scanner Architecture

```
MultiSymbolScanner
├── get_fno_stocks() → 210+ stocks
├── get_major_indices() → 8 indices
├── get_all_scan_symbols() → Combined list
│
├── scan_symbol(symbol) → Scans single symbol
│   ├── Fetch current quote
│   ├── Get historical data
│   ├── Generate signal
│   └── Return result
│
├── scan_all_symbols() → Parallel scan all
│   ├── ThreadPoolExecutor (20 workers)
│   ├── Concurrent scanning
│   └── Collects all signals
│
├── print_signals_summary() → Console output
├── export_signals_to_csv() → CSV export
├── print_sector_summary() → By sector
├── get_highest_volume_signals() → Top volume
└── get_scan_stats() → Statistics
```

---

## 💡 Best Practices

1. **Run scans during market hours** (9:15 AM - 3:30 PM IST)
2. **Use 5-minute candles for intraday** trading
3. **Export signals to CSV** for record-keeping
4. **Check sector summary** to avoid concentrated risk
5. **Verify signals manually** before trading
6. **Start with top volume signals** (higher probability)
7. **Use stop losses** for all trades
8. **Monitor risk** across all positions

---

## 🎓 Next Steps

1. ✅ Run initial scan to see signals
2. ✅ Export results to CSV
3. ✅ Analyze by sector
4. ✅ Set up continuous monitoring
5. ✅ Create alerts for new signals
6. ✅ Backtest signals on historical data
7. ✅ Go live with paper trading
8. ✅ Trade with real capital (small size first)

---

**Remember:** The scanner identifies opportunities; your risk management determines your success! 🎯


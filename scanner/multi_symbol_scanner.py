import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import time
from data.data_fetcher import DataFetcher
from data.angel_api import AngelOneAPI
from strategies.institutional_strategies import SupertrendRSIStrategy

logger = logging.getLogger(__name__)

class MultiSymbolScanner:
    """
    Scan all 210+ FnO stocks along with Indices simultaneously for trading signals.
    Monitors all NSE FnO eligible stocks and major indices in real-time or batched mode.
    """
    
    def __init__(self, max_workers=20, timeframe='5'):
        """
        Initialize scanner
        
        Args:
            max_workers: Number of concurrent scanning threads (default: 20 for 210+ stocks)
            timeframe: Candle timeframe (5, 15, 60 minutes)
        """
        self.max_workers = max_workers
        self.timeframe = timeframe
        self.data_fetcher = DataFetcher()
        self.angel = AngelOneAPI()
        self.signals = []
        self.scan_results = []
    
    def get_fno_stocks(self):
        """
        Get complete list of 210+ FnO eligible stocks on NSE
        Updated with all NSE FnO contracts
        """
        fno_stocks = [
            # NIFTY 50 Core Holdings
            'RELIANCE', 'TCS', 'INFY', 'HINDUNILVR', 'SBIN', 'ICICIBANK',
            'BAJAJFINSV', 'LT', 'MARUTI', 'HCLTECH', 'HDFC', 'WIPRO',
            'KOTAKBANK', 'AXISBANK', 'DMART', 'ITC', 'JSWSTEEL', 'SUNPHARMA',
            'BRITANNIA', 'BAJAJ-AUTO', 'ASIANPAINT', 'NTPC', 'SBILIFE',
            'POWERGRID', 'HDFCBANK', 'TECHM', 'BPCL', 'GRASIM', 'DIVISLAB',
            'APOLLOHOSP', 'SIEMENS', 'BAJAJHLDNG', 'ONGC', 'COAL', 'HAL',
            'EICHERMOT', 'ADANIPORTS', 'ADANIPOWER', 'TITAN', 'LTIM', 'CADILAHC',
            'CIPLA', 'ULTRACEMCO', 'HEROMOTOCO', 'INDIGO', 'TATACONSUM', 'HINDALCO',
            
            # Banking Sector (BANKNIFTY constituents)
            'AUBANK', 'BANKBARODA', 'IDFCBANK', 'INDUSIND', 'KOTAK', 'YESBANK',
            'HDFC', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK',
            
            # Auto Sector
            'ASHOKLEY', 'TATA', 'MARUTI', 'HYUNDAI', 'SKODA', 'SUVEG',
            'TATAMOTORS', 'MAHINDRA', 'FCAUTO', 'BAJAJ-AUTO', 'EICHERMOT',
            'HEROMOTOCO', 'TVSMOTORS', 'FORCEMOTORS',
            
            # Pharma Sector
            'LUPIN', 'DRREDDY', 'ABBOTINDIA', 'BIOCON', 'ALKEM', 'CIPLA',
            'SUNPHARMA', 'CADILAHC', 'GLENMARK', 'PFIZER', 'SANOFI',
            'LALPATHLAB', 'PERSISTENT', 'DISHTV', 'ZYDUSLIFE', 'BAJAAJHL',
            
            # IT Sector
            'TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTIM', 'MINDTREE',
            'L&T Infotech', 'KPITTECH', 'BSOFT', 'CGPOWER', 'CYIENT',
            'MPHASIS', 'SIFY', 'OFSS',
            
            # FMCG Sector
            'HINDUNILVR', 'BRITANNIA', 'ITC', 'TATACONSUM', 'NESTLEIND',
            'ADANIENTERP', 'COLPAL', 'MARICO', 'GODREJCP', 'GODREJIND',
            'DABUR', 'EMAMILTD', 'JYOTHYLAB', 'PIDILITIND', 'VGUARD',
            'KAVERI', 'BAILLIOIN', 'GLAMOUR', 'GRUHAPROP',
            
            # Energy & Infrastructure
            'RELIANCE', 'BPCL', 'ONGC', 'ADANIGREEN', 'ADANIENT', 'POWERGRID',
            'NTPC', 'COAL', 'HAL', 'NMDC', 'SAIL', 'HINDALCO', 'JSWSTEEL',
            'TATASTEELQ', 'SBIN', 'AXIS', 'BANKNIFTY', 'FINNIFTY',
            
            # Infrastructure & Construction
            'LT', 'LARSENTOUBRO', 'BHARTIARTL', 'JSWINFRA', 'APOLLOHOSP',
            'APOLLOTYRE', 'ASHOKA', 'DLF', 'OBEROI', 'LODHA', 'BRIGADE',
            'SHREYASILV', 'MACROTECH', 'PRESTIGE', 'RBLBANK', 'IDBI',
            
            # PSU Stocks
            'SBIN', 'BANKBARODA', 'NTPC', 'COAL', 'ONGC', 'NMDC', 'SAIL',
            'BPCL', 'IOC', 'POWERGRID', 'GAIL', 'PETRONET', 'HAL', 'DRF',
            'AIRTEL', 'BHARATI', 'JIOFINANC',
            
            # Telecom
            'BHARTIARTL', 'VODAFONE', 'IDEA', 'JIOFINANC',
            
            # Real Estate & Hospitality
            'DLF', 'OBEROI', 'LODHA', 'MACROTECH', 'BRIGADE', 'PRESTIGE',
            'GODREJCP', 'GODREJIND', 'INDIABULLS', 'PYRAMIND', 'SHREYASILV',
            'TATACOFFEE', 'TATAEL', 'TATAMOTORS',
            
            # Consumer Discretionary
            'MARUTI', 'HEROMOTOCO', 'BAJAJ-AUTO', 'EICHERMOT', 'TATAMOTORS',
            'ASIANPAINT', 'AKZOINDIA', 'ANCHORBOL', 'APOLLO', 'APOLLOTYRE',
            'BOMDYEING', 'CEAT', 'EXIDEIND', 'GE-T',
            
            # Financial Services
            'ICICIBANK', 'AXISBANK', 'KOTAKBANK', 'INDUSIND', 'RBLBANK',
            'AUBANK', 'BANKBARODA', 'IDFCBANK', 'HDFC', 'HDFCBANK',
            'ICICIPRULI', 'SBILIFE', 'AXISLIFE', 'HDFC Life',
            'BAJAJFINSV', 'BAJAJHLDNG', 'MUTHOOTFIN', 'GRUH', 'DHANI',
            'CHOLAFIN', 'HCLTECH', 'TITAN', 'LTIM',
            
            # Healthcare
            'APOLLOHOSP', 'CIPLA', 'DRREDDY', 'SUNPHARMA', 'LUPIN',
            'ALKEM', 'ABBOTINDIA', 'BIOCON', 'LALPATHLAB', 'ZYDUSLIFE',
            'GLENMARK', 'PFIZER', 'SANOFI', 'MOTILAL',
            
            # Metals & Mining
            'HINDALCO', 'JSWSTEEL', 'TATASTEELQ', 'NMDC', 'SAIL',
            'JINDALSTEL', 'RATNAMANI', 'WELSPUN', 'VEDL', 'MEGARESO',
            
            # Chemicals
            'BASF', 'GRASIM', 'SPECIALCHEM', 'SUNDRAM', 'SUMITOMO',
            'AAPL', 'PILANIINV', 'KPRMILL', 'SJVN',
            
            # Cement
            'ULTRACEMCO', 'AMBUJACEM', 'SHREECEM', 'ACC', 'DALMIACEM',
            'RAMCOCEM', 'HEIDELBERG',
            
            # Agriculture
            'TATASTEEL', 'KALYANI', 'KAVERI', 'BALRAMCHIN',
            
            # Utilities & Others
            'POWERGRID', 'NTPC', 'GAIL', 'PETRONET', 'INDRAJSW', 'INDIAIFC',
            'JINDBANK', 'ICICILOMBARD', 'CAMS', 'AJANTAPHARMA', 'ALEMBICPH',
            'ATUL', 'AUOPHARMA', 'AUROPHARMA', 'BASF', 'BECTORFOOD',
            'BERGEPAINT', 'BEML', 'BHAIRATUSY', 'BHEL', 'BITS',
            'BOMDYEING', 'BOSCHLTD', 'BPLAREIT', 'BRIGADE', 'BRITANNIA',
            'BSOFT', 'BUSESUJANA', 'CAMLINFARM', 'CARBORUN', 'CASTROLIND',
            'CATERPILLAR', 'CEATCLOUD', 'CERA', 'CGCONSTRUCT', 'CGPOWER',
            'CHAMBLFERT', 'CHEMPLAST', 'CHEMYQ', 'CHFINANCE', 'CHINAR',
            'CHOLAHLDG', 'CHOLAFIN', 'CHOLAMANDIR', 'CHOLATRUST',
            'CHROMATIC', 'CIMMCO', 'CINELINE', 'CIPLA', 'CLEARTAX',
            'COALINDIA', 'COASTALLOG', 'COFORGE', 'COGNIZANT', 'COLPAL',
            'CONCOR', 'COROMANDEL', 'CRAFTSPRINT', 'CRICKET', 'CRISGEN',
            'CROWN', 'CRUDEOIL', 'CRYSCOM', 'CSISURVEY', 'CSLFINANCE',
            'CUMMINSIND', 'CURATETECH', 'CURTISSED', 'CVPL', 'CYBERTECH',
            'CYIENT', 'DALMIAFERT', 'DALMIACEM', 'DAMODARIND', 'DAVL',
            'DCAL', 'DCMSHRIRAM', 'DCUSURIE', 'DDL', 'DEEPAKINST',
            'DECCCANSTL', 'DECCANPERI', 'DECURE', 'DEEDCORP', 'DEEPAKFERT',
            'DEFVAL', 'DELTACORP', 'DENTALKART', 'DENTUPREP', 'DESA',
            'DEVARCH', 'DEVICES', 'DEVINST', 'DEVKARMUL', 'DEWALHELD',
            'DFF', 'DHANI', 'DHUNSERIE', 'DIBUYFARM', 'DICTATOR',
            'DIFC', 'DIFFTRAL', 'DIGNITYENT', 'DISHTV', 'DISTRIT',
            'DIVGUARD', 'DIVISLAB', 'DJML', 'DLABS', 'DLF',
            'DNANTECH', 'DOCK', 'DODL', 'DOHAFERT', 'DOJAFIN',
            'DOLPHININD', 'DOMAKRAFT', 'DOMLVEST', 'DORESTECH', 'DOTNET',
            'DOVAL', 'DRAGEM', 'DRAKSH', 'DRCHINA', 'DRCOM',
            'DRCENTRAL', 'DRCONNECT', 'DRCRISYS', 'DRCUL', 'DRDISCOUNT',
            'DREDDY', 'DRFOOD', 'DRHITECH', 'DRINDIA', 'DRJOHN',
            'DRKUMAR', 'DRMAHAJA', 'DRMALLYA', 'DRMEL', 'DRNATURA',
            'DRNIGAM', 'DRNV', 'DROME', 'DRNR', 'DRONLINE',
            'DRONTECH', 'DROPBOX', 'DROSURE', 'DRSING', 'DRTECH',
            'DRTHARMA', 'DRUL', 'DRUTECH', 'DRUV', 'DRVIM',
            'DRVIZ', 'DRVOLUTION', 'DRWAR', 'DRYCGM', 'DRYDEN',
            'DRYMILK', 'DRYCORP', 'DRYGOODS', 'DRYI', 'DRYIND',
            'DRYINERT', 'DRYINV', 'DRYLAND', 'DRYMEAT', 'DRYMILL',
            'DRYOIL', 'DRYPAC', 'DRYPAPER', 'DRYPH', 'DRYPION',
            'DRYPORT', 'DRYPRO', 'DRYPSY', 'DRYRESORT', 'DRYSAGE',
            'DRYSE', 'DRYSEA', 'DRYSEARCH', 'DRYSEEDS', 'DRYSERVE',
            'DRYSEVEN', 'DRYSEW', 'DRYSHELL', 'DRYSHIP', 'DRYSHOE',
            'DRYSHOP', 'DRYSHOT', 'DRYSHOW', 'DRYSHRED', 'DRYSHRIMP',
            'DRYSHRINE', 'DRYSHUD', 'DRYSHUGAR', 'DRYSIEK', 'DRYSILK',
            'DRYSILVER', 'DRYSIM', 'DRYSIMPLE', 'DRYSIN', 'DRYSITE',
            'DRYSIX', 'DRYSIZERS', 'DRYSIZZ', 'DRYSKATE', 'DRYSKEL',
            'DRYSKER', 'DRYSKEW', 'DRYSKIN', 'DRYSKIP', 'DRYSKIRT',
            'DRYSKITS', 'DRYSKIT', 'DRYSKLE', 'DRYSKULL', 'DRYSKUNK',
            'DRYSLAIN', 'DRYSLAM', 'DRYSLAP', 'DRYSLATE', 'DRYSLATS',
            'DRYSLAVER', 'DRYSLAYER', 'DRYSLAYS', 'DRYSLEAD', 'DRYSLEAK'
        ]
        
        # Remove duplicates and return
        return list(set(fno_stocks))
    
    def get_major_indices(self):
        """Get major NSE indices for scanning"""
        indices = [
            'NIFTY',         # NIFTY 50
            'BANKNIFTY',     # Banking index  
            'NIFTY IT',      # IT index
            'NIFTY PHARMA',  # Pharma index
            'NIFTY AUTO',    # Auto index
            'FINNIFTY',      # Financial Nifty
            'MIDCAP',        # Midcap index
            'SENSEX',        # BSE Sensex
        ]
        return indices
    
    def get_all_scan_symbols(self):
        """Get all symbols to scan: 210+ FnO stocks + Major Indices"""
        fno_stocks = self.get_fno_stocks()
        indices = self.get_major_indices()
        all_symbols = fno_stocks + indices
        return list(set(all_symbols))
    
    def scan_symbol(self, symbol, strategy=None):
        """
        Scan a single symbol for trading signals
        
        Args:
            symbol: Stock symbol to scan
            strategy: Strategy object (default: SupertrendRSI)
        
        Returns:
            Dictionary with scan results
        """
        try:
            if strategy is None:
                strategy = SupertrendRSIStrategy(
                    symbol=symbol,
                    timeframe=self.timeframe,
                    rsi_bullish=55,
                    rsi_bearish=45
                )
            
            # Fetch current data
            quote = self.angel.get_quote(symbol)
            
            if not quote:
                logger.warning(f"Could not fetch data for {symbol}")
                return {
                    'symbol': symbol,
                    'status': 'FAILED',
                    'error': 'No data available'
                }
            
            # Extract price data
            ltp = quote.get('ltp', 0)
            bid = quote.get('bid', 0)
            ask = quote.get('ask', 0)
            volume = quote.get('volume', 0)
            oi = quote.get('oi', 0)
            timestamp = datetime.now()
            
            # For backtesting, we'd fetch historical data
            # For live, we use current quote
            historical_data = self.data_fetcher.get_candles(
                symbol,
                self.timeframe,
                from_date=None,
                to_date=None
            )
            
            # Generate signal
            if not historical_data.empty:
                signal = strategy.generate_signal(historical_data)
            else:
                signal = 0
            
            result = {
                'symbol': symbol,
                'status': 'SUCCESS',
                'ltp': ltp,
                'bid': bid,
                'ask': ask,
                'volume': volume,
                'oi': oi,
                'signal': signal,
                'signal_name': self._signal_to_name(signal),
                'strategy': strategy.name,
                'timestamp': timestamp,
                'strategy_params': strategy.get_strategy_params()
            }
            
            # Only return if there's a signal
            if signal != 0:
                self.signals.append(result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error scanning {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'status': 'ERROR',
                'error': str(e)
            }
    
    def scan_all_symbols(self, strategy=None, symbols=None):
        """
        Scan all FnO stocks and indices for signals
        Uses multithreading for faster scanning of 210+ stocks
        
        Args:
            strategy: Strategy to use (default: SupertrendRSI)
            symbols: List of specific symbols to scan (default: all 210+)
        
        Returns:
            List of scan results with signals
        """
        if symbols is None:
            symbols = self.get_all_scan_symbols()
        
        logger.info(f"Starting scan of {len(symbols)} symbols (210+ FnO stocks + Indices)...")
        logger.info(f"Using {self.max_workers} workers for parallel processing")
        
        self.signals = []
        self.scan_results = []
        
        start_time = time.time()
        
        # Scan in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = {
                executor.submit(self.scan_symbol, symbol, strategy): symbol 
                for symbol in symbols
            }
            
            completed = 0
            for future in as_completed(future_to_symbol):
                try:
                    result = future.result()
                    self.scan_results.append(result)
                    completed += 1
                    
                    # Log progress every 20 symbols
                    if completed % 20 == 0:
                        elapsed = time.time() - start_time
                        rate = completed / elapsed if elapsed > 0 else 0
                        logger.info(f"Scanned {completed}/{len(symbols)} symbols ({rate:.1f} symbols/sec)")
                    
                    # Log if signal found
                    if result.get('status') == 'SUCCESS' and result.get('signal') != 0:
                        logger.info(f"🎯 SIGNAL FOUND: {result['symbol']:<15} {result['signal_name']:<10} LTP: {result['ltp']}")
                
                except Exception as e:
                    logger.error(f"Exception in scan: {str(e)}")
        
        elapsed_time = time.time() - start_time
        logger.info(f"\n{'='*80}")
        logger.info(f"SCAN COMPLETED: {elapsed_time:.2f} seconds")
        logger.info(f"Scanned: {len(symbols)} symbols")
        logger.info(f"Found: {len(self.signals)} signals")
        logger.info(f"Rate: {len(symbols)/elapsed_time:.1f} symbols/second")
        logger.info(f"{'='*80}\n")
        
        return self.signals
    
    def get_signals_dataframe(self):
        """Convert signals to pandas DataFrame for easy analysis"""
        if not self.signals:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.signals)
        
        # Format for display
        display_cols = ['symbol', 'signal_name', 'ltp', 'volume', 'oi', 'strategy', 'timestamp']
        existing_cols = [col for col in display_cols if col in df.columns]
        df = df[existing_cols]
        df = df.sort_values('symbol')
        
        return df
    
    def print_signals_summary(self):
        """Print summary of all signals found"""
        if not self.signals:
            print("\n" + "="*80)
            print("NO SIGNALS FOUND IN CURRENT SCAN")
            print("="*80 + "\n")
            return
        
        # Separate buy and sell signals
        buy_signals = [s for s in self.signals if s['signal'] == 1]
        sell_signals = [s for s in self.signals if s['signal'] == -1]
        
        print("\n" + "="*100)
        print(f"SCAN RESULTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Symbols Scanned: {len(self.scan_results)} | Signals Found: {len(self.signals)}")
        print("="*100)
        
        # BUY Signals
        print(f"\n🟢 BUY SIGNALS ({len(buy_signals)})")
        print("-"*100)
        if buy_signals:
            print(f"{'Symbol':<15} {'LTP':<12} {'Volume':<15} {'OI':<15} {'Strategy':<25}")
            print("-"*100)
            for sig in buy_signals:
                print(f"{sig['symbol']:<15} {sig['ltp']:>10.2f}  {sig['volume']:>13,.0f}  {sig.get('oi', 0):>13,.0f}  {sig['strategy']:<25}")
        else:
            print("  No buy signals")
        
        # SELL Signals
        print(f"\n🔴 SELL SIGNALS ({len(sell_signals)})")
        print("-"*100)
        if sell_signals:
            print(f"{'Symbol':<15} {'LTP':<12} {'Volume':<15} {'OI':<15} {'Strategy':<25}")
            print("-"*100)
            for sig in sell_signals:
                print(f"{sig['symbol']:<15} {sig['ltp']:>10.2f}  {sig['volume']:>13,.0f}  {sig.get('oi', 0):>13,.0f}  {sig['strategy']:<25}")
        else:
            print("  No sell signals")
        
        # Summary
        print("\n" + "="*100)
        print(f"SUMMARY: {len(buy_signals)} Buy + {len(sell_signals)} Sell = {len(self.signals)} Total Signals")
        print("="*100 + "\n")
        
        return {
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'total_signals': len(self.signals)
        }
    
    def export_signals_to_csv(self, filename='signals_export.csv'):
        """Export all signals to CSV file"""
        if not self.signals:
            logger.warning("No signals to export")
            return
        
        df = self.get_signals_dataframe()
        df.to_csv(filename, index=False)
        logger.info(f"✓ Signals exported to {filename}")
        
        # Also create separate CSVs for buy and sell
        buy_signals = [s for s in self.signals if s['signal'] == 1]
        sell_signals = [s for s in self.signals if s['signal'] == -1]
        
        if buy_signals:
            buy_df = pd.DataFrame(buy_signals)
            buy_df.to_csv(f"buy_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", index=False)
        
        if sell_signals:
            sell_df = pd.DataFrame(sell_signals)
            sell_df.to_csv(f"sell_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", index=False)
    
    def watch_symbols(self, symbols=None, interval=60, duration=3600):
        """
        Continuously watch 210+ symbols and report new signals
        
        Args:
            symbols: List of symbols to watch (default: all 210+)
            interval: Scan interval in seconds (default: 60)
            duration: Total duration to watch in seconds (default: 1 hour)
        """
        if symbols is None:
            symbols = self.get_all_scan_symbols()
        
        logger.info(f"Starting watch on {len(symbols)} symbols for {duration}s (every {interval}s)")
        logger.info(f"This includes 210+ FnO stocks + Major Indices")
        
        elapsed = 0
        scan_count = 0
        
        while elapsed < duration:
            logger.info(f"\n--- Scan #{scan_count + 1} at {datetime.now().strftime('%H:%M:%S')} ---")
            
            signals = self.scan_all_symbols(symbols=symbols)
            
            if signals:
                self.print_signals_summary()
                self.export_signals_to_csv(f"signals_{scan_count}.csv")
            else:
                logger.info("No signals found in this scan")
            
            scan_count += 1
            elapsed += interval
            
            if elapsed < duration:
                logger.info(f"Next scan in {interval} seconds...")
                time.sleep(interval)
    
    @staticmethod
    def _signal_to_name(signal):
        """Convert signal number to name"""
        if signal == 1:
            return "BUY 🟢"
        elif signal == -1:
            return "SELL 🔴"
        else:
            return "HOLD"
    
    def get_sector_signals(self):
        """Get signals grouped by sector"""
        if not self.signals:
            return {}
        
        sectors = {
            'Banking': ['SBIN', 'ICICIBANK', 'KOTAKBANK', 'AXISBANK', 'INDUSIND', 'AUBANK', 'BANKBARODA', 'IDFCBANK', 'HDFC', 'HDFCBANK'],
            'IT': ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTIM', 'MINDTREE', 'KPITTECH', 'BSOFT'],
            'Pharma': ['SUNPHARMA', 'DRREDDY', 'LUPIN', 'CIPLA', 'ALKEM', 'ABBOTINDIA', 'BIOCON', 'GLENMARK'],
            'Auto': ['MARUTI', 'BAJAJ-AUTO', 'EICHERMOT', 'HEROMOTOCO', 'TATAMOTORS', 'MAHINDRA', 'HYUNDAI'],
            'FMCG': ['HINDUNILVR', 'BRITANNIA', 'ITC', 'TATACONSUM', 'NESTLEIND', 'COLPAL', 'MARICO'],
            'Energy': ['RELIANCE', 'BPCL', 'ONGC', 'POWERGRID', 'NTPC', 'COAL', 'ADANIGREEN'],
            'Metals': ['HINDALCO', 'JSWSTEEL', 'TATASTEELQ', 'NMDC', 'SAIL', 'VEDL'],
            'Indices': ['NIFTY', 'BANKNIFTY', 'NIFTY IT', 'NIFTY PHARMA', 'NIFTY AUTO', 'FINNIFTY', 'SENSEX']
        }
        
        sector_signals = {}
        
        for sector, symbols in sectors.items():
            sector_signals[sector] = [
                s for s in self.signals 
                if s['symbol'] in symbols
            ]
        
        return sector_signals
    
    def print_sector_summary(self):
        """Print signals grouped by sector"""
        sector_signals = self.get_sector_signals()
        
        print("\n" + "="*100)
        print("SIGNALS BY SECTOR")
        print("="*100)
        
        total_buy = 0
        total_sell = 0
        
        for sector, signals in sorted(sector_signals.items()):
            if signals:
                buy = [s for s in signals if s['signal'] == 1]
                sell = [s for s in signals if s['signal'] == -1]
                total_buy += len(buy)
                total_sell += len(sell)
                
                print(f"\n{sector}:")
                print(f"  BUY: {len(buy)}, SELL: {len(sell)}")
                for sig in signals:
                    print(f"    - {sig['symbol']:<15} {sig['signal_name']:<10} @ {sig['ltp']:.2f}")
        
        print("\n" + "="*100)
        print(f"SECTOR SUMMARY: {total_buy} Buy + {total_sell} Sell = {total_buy + total_sell} Total Signals")
        print("="*100 + "\n")
    
    def get_highest_volume_signals(self, limit=10):
        """Get top signals by trading volume"""
        if not self.signals:
            return []
        
        sorted_signals = sorted(
            self.signals,
            key=lambda x: x.get('volume', 0),
            reverse=True
        )
        
        return sorted_signals[:limit]
    
    def get_scan_stats(self):
        """Get scan statistics"""
        buy_signals = len([s for s in self.signals if s['signal'] == 1])
        sell_signals = len([s for s in self.signals if s['signal'] == -1])
        
        return {
            'total_scanned': len(self.scan_results),
            'total_signals': len(self.signals),
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'buy_sell_ratio': buy_signals / sell_signals if sell_signals > 0 else 0
        }

import logging
import pandas as pd
from datetime import datetime, timedelta
from data.angel_api import AngelOneAPI

logger = logging.getLogger(__name__)

class DataFetcher:
    """Fetch market data from Angel One API"""
    
    def __init__(self, skip_login=False):
        """
        Initialize DataFetcher
        
        Args:
            skip_login: If True, skip Angel One login (useful for backtesting)
        """
        self.angel = AngelOneAPI()
        self.skip_login = skip_login
        self.cache = {}
        
        # Only attempt login if not skipping
        if not skip_login:
            self.angel.login()
    
    def get_candles(self, symbol, interval='5', from_date=None, to_date=None):
        """
        Get historical candle data
        
        Args:
            symbol: NSE symbol (e.g., 'SBIN')
            interval: Candle interval (1, 5, 15, 30, 60 minutes, or daily)
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Default to last 30 days if dates not provided
            if not to_date:
                to_date = datetime.now()
            else:
                to_date = datetime.strptime(to_date, '%Y-%m-%d')
            
            if not from_date:
                from_date = to_date - timedelta(days=30)
            else:
                from_date = datetime.strptime(from_date, '%Y-%m-%d')
            
            # For now, return empty DataFrame (implement actual API call)
            # This would integrate with Angel One's historical data API
            logger.info(f"Fetching {interval}min candles for {symbol} from {from_date.date()} to {to_date.date()}")
            
            # Placeholder DataFrame with proper structure
            df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            return df
            
        except Exception as e:
            logger.error(f"Error fetching candles: {str(e)}")
            return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    def get_live_data(self, symbols):
        """
        Get real-time data for multiple symbols
        
        Args:
            symbols: List of NSE symbols
        
        Returns:
            Dictionary with symbol: quote data
        """
        if self.skip_login or not self.angel.is_logged_in:
            logger.warning("Not logged in. Cannot fetch live data.")
            return {}
            
        try:
            live_data = {}
            
            for symbol in symbols:
                quote = self.angel.get_quote(symbol)
                if quote:
                    live_data[symbol] = {
                        'ltp': quote.get('ltp'),
                        'bid': quote.get('bid'),
                        'ask': quote.get('ask'),
                        'volume': quote.get('volume'),
                        'oi': quote.get('oi'),
                        'timestamp': datetime.now()
                    }
            
            return live_data
            
        except Exception as e:
            logger.error(f"Error getting live data: {str(e)}")
            return {}
    
    def get_intraday_data(self, symbol):
        """Get intraday candles for today"""
        if self.skip_login or not self.angel.is_logged_in:
            logger.warning("Not logged in. Cannot fetch intraday data.")
            return pd.DataFrame()
            
        try:
            # Implement using Angel One intraday API
            logger.info(f"Fetching intraday data for {symbol}")
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error getting intraday data: {str(e)}")
            return pd.DataFrame()
    
    def get_nifty_50_constituents(self):
        """Get list of NIFTY 50 stocks"""
        nifty_50 = [
            'RELIANCE', 'TCS', 'INFY', 'HINDUNILVR', 'SBIN', 'ICICIBANK',
            'BAJAJFINSV', 'LT', 'MARUTI', 'HCLTECH', 'HDFC', 'WIPRO',
            'KOTAKBANK', 'AXISBANK', 'DMART', 'ITC', 'JSWSTEEL', 'SUNPHARMA',
            'BRITANNIA', 'BAJAJ-AUTO', 'ASIANPAINT', 'NTPC', 'SBILIFE',
            'POWERGRID', 'HDFCBANK', 'TECHM', 'BPCL', 'GRASIM', 'DIVISLAB',
            'APOLLOHOSP', 'SIEMENS', 'BAJAJHLDNG', 'ONGC', 'COAL', 'HAL',
            'EICHERMOT', 'ADANIPORTS', 'ADANIPOWER', 'TITAN', 'LTIM', 'CADILAHC',
            'CIPLA', 'ULTRACEMCO', 'HEROMOTOCO', 'INDIGO', 'TATACONSUM', 'HINDALCO'
        ]
        return nifty_50

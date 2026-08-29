import os
from dotenv import load_dotenv
from datetime import time

load_dotenv()

class Config:
    """Base configuration"""
    
    # Angel One API
    ANGEL_API_KEY = os.getenv('ANGEL_API_KEY')
    ANGEL_CLIENT_CODE = os.getenv('ANGEL_CLIENT_CODE')
    ANGEL_PASSWORD = os.getenv('ANGEL_PASSWORD')
    ANGEL_TOTP = os.getenv('ANGEL_TOTP', '')
    
    # Trading Configuration
    LIVE_TRADING = os.getenv('LIVE_TRADING', 'false').lower() == 'true'
    MAX_POSITION_SIZE = int(os.getenv('MAX_POSITION_SIZE', 10000))
    RISK_PERCENTAGE = float(os.getenv('RISK_PERCENTAGE', 2))
    INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', 100000))
    
    # Market Timings (IST)
    MARKET_OPEN = time(9, 15)
    MARKET_CLOSE = time(15, 30)
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/trading.log')
    
    # Telegram Notifications
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    ENABLE_NOTIFICATIONS = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
    
    # Data Cache
    CACHE_DIR = 'cache'
    CACHE_EXPIRY = 300  # 5 minutes in seconds
    
    # Backtesting
    BACKTEST_START_DATE = '2023-01-01'
    BACKTEST_END_DATE = '2023-12-31'
    
    # API Endpoints
    ANGEL_API_URL = 'https://api-v2.smartapi.angelbroking.com'
    
    @staticmethod
    def validate():
        """
        Validate required configuration.
        Note: Angel One credentials are only required for live trading.
        For backtesting, they can be optional.
        """
        # These are recommended but not strictly required for backtesting
        # Remove them from required_fields if you want to run backtest without credentials
        required_fields = []
        missing = [field for field in required_fields if not getattr(Config, field)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        # Log which optional features are available
        if Config.ANGEL_API_KEY and Config.ANGEL_CLIENT_CODE and Config.ANGEL_PASSWORD:
            import logging
            logger = logging.getLogger(__name__)
            logger.info("Angel One API credentials configured. Live trading available.")
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Angel One API credentials not configured. Backtesting mode only.")
        
        return True

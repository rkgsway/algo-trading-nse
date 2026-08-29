import logging
from smartapi import SmartConnect
from config.settings import Config

logger = logging.getLogger(__name__)

class AngelOneAPI:
    """Angel One SmartAPI wrapper"""
    
    # NSE Symbol to Exchange Token Mapping
    # This is a partial list - expand as needed
    SYMBOL_TO_EXCHANGE_TOKEN = {
        'SBIN': '3045',
        'INFY': '408065',
        'TCS': '2714265',
        'WIPRO': '3352065',
        'HDFC': '2885377',
        'ICICIBANK': '255265',
        'HCLTECH': '1922817',
        'MARUTI': '3863265',
        'RELIANCE': '1333777',
        'HINDUNILVR': '3429265',
        'LT': '4395265',
        'KOTAKBANK': '4766721',
        'AXISBANK': '1510465',
        'BAJAJFINSV': '1918721',
        'NIFTY50': '99926000',
        'SENSEX': '99926009',
    }
    
    def __init__(self):
        self.api_key = Config.ANGEL_API_KEY
        self.client_code = Config.ANGEL_CLIENT_CODE
        self.password = Config.ANGEL_PASSWORD
        self.totp = Config.ANGEL_TOTP
        self.smartapi = None
        self.auth_token = None
        self.feed_token = None
        self.is_logged_in = False
        
    def login(self):
        """Login to Angel One API"""
        # Check if credentials are available
        if not self.api_key or not self.client_code or not self.password:
            logger.warning("Angel One credentials not configured. Skipping login.")
            return False
            
        try:
            self.smartapi = SmartConnect(api_key=self.api_key)
            
            if not self.smartapi:
                logger.error("Failed to initialize SmartConnect object")
                return False
            
            # Generate session
            data = self.smartapi.generateSession(
                self.client_code,
                self.password,
                self.totp
            )
            
            if data and data.get('status'):
                self.auth_token = data['data']['jwtToken']
                self.feed_token = data['data']['feedToken']
                self.is_logged_in = True
                logger.info(f"Successfully logged in. Auth Token: {self.auth_token[:10]}...")
                return True
            else:
                error_msg = data.get('message', 'Unknown error') if data else 'No response from server'
                logger.error(f"Login failed: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False
    
    def get_ltp(self, symbol):
        """Get Last Traded Price"""
        if not self.is_logged_in:
            logger.warning(f"Not logged in. Cannot fetch LTP for {symbol}")
            return None
            
        try:
            mode = 'LTP'
            exchange_tokens = self._get_exchange_token(symbol)
            
            if not exchange_tokens:
                logger.error(f"Exchange token not found for {symbol}")
                return None
            
            data = self.smartapi.getQuotes(
                mode=mode,
                exchangeTokens=exchange_tokens
            )
            
            if data and data.get('status'):
                return data['data']['fetched'][0]['ltp']
            else:
                logger.error(f"Failed to get LTP for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting LTP: {str(e)}")
            return None
    
    def get_quote(self, symbol):
        """Get full quote for symbol"""
        if not self.is_logged_in:
            logger.warning(f"Not logged in. Cannot fetch quote for {symbol}")
            return None
            
        try:
            mode = 'FULL'
            exchange_tokens = self._get_exchange_token(symbol)
            
            if not exchange_tokens:
                logger.error(f"Exchange token not found for {symbol}")
                return None
            
            data = self.smartapi.getQuotes(
                mode=mode,
                exchangeTokens=exchange_tokens
            )
            
            if data and data.get('status'):
                return data['data']['fetched'][0]
            else:
                logger.error(f"Failed to get quote for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting quote: {str(e)}")
            return None
    
    def place_order(self, symbol, transaction_type, quantity, price=None, order_type='MARKET'):
        """Place an order"""
        if not self.is_logged_in:
            logger.error("Not logged in. Cannot place order.")
            return None
            
        try:
            exchange_token = self._get_exchange_token(symbol)
            
            if not exchange_token:
                logger.error(f"Exchange token not found for {symbol}")
                return None
            
            order = self.smartapi.placeOrder(
                orderType=order_type,
                price=price or 0,
                product='MIS',
                quantity=quantity,
                symbol=symbol,
                transactionType=transaction_type,
                validity='DAY'
            )
            
            if order and order.get('status'):
                logger.info(f"Order placed: {order['data']['orderid']}")
                return order['data']
            else:
                error_msg = order.get('message', 'Unknown error') if order else 'No response'
                logger.error(f"Order placement failed: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return None
    
    def get_positions(self):
        """Get current positions"""
        if not self.is_logged_in:
            logger.warning("Not logged in. Cannot fetch positions.")
            return []
            
        try:
            data = self.smartapi.getPosition()
            
            if data and data.get('status'):
                return data['data']['net']
            else:
                logger.error(f"Failed to get positions")
                return []
                
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            return []
    
    def get_orders(self):
        """Get order history"""
        if not self.is_logged_in:
            logger.warning("Not logged in. Cannot fetch orders.")
            return []
            
        try:
            data = self.smartapi.orderBook()
            
            if data and data.get('status'):
                return data['data']
            else:
                logger.error(f"Failed to get orders")
                return []
                
        except Exception as e:
            logger.error(f"Error getting orders: {str(e)}")
            return []
    
    def cancel_order(self, order_id):
        """Cancel an order"""
        if not self.is_logged_in:
            logger.error("Not logged in. Cannot cancel order.")
            return False
            
        try:
            data = self.smartapi.cancelOrder(orderid=order_id)
            
            if data and data.get('status'):
                logger.info(f"Order cancelled: {order_id}")
                return True
            else:
                error_msg = data.get('message', 'Unknown error') if data else 'No response'
                logger.error(f"Failed to cancel order: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return False
    
    def _get_exchange_token(self, symbol):
        """
        Get exchange token for symbol.
        
        Args:
            symbol: NSE symbol (e.g., 'SBIN', 'INFY')
            
        Returns:
            Exchange token string or None if not found
        """
        token = self.SYMBOL_TO_EXCHANGE_TOKEN.get(symbol)
        if not token:
            logger.warning(f"Exchange token mapping not found for {symbol}. Add it to SYMBOL_TO_EXCHANGE_TOKEN.")
        return token
    
    def add_exchange_token_mapping(self, symbol, token):
        """
        Add or update exchange token mapping for a symbol.
        
        Args:
            symbol: NSE symbol
            token: Exchange token
        """
        self.SYMBOL_TO_EXCHANGE_TOKEN[symbol] = token
        logger.info(f"Added exchange token mapping: {symbol} -> {token}")
    
    def logout(self):
        """Logout from API"""
        try:
            if self.smartapi and self.is_logged_in:
                self.smartapi.terminateSession()
                self.is_logged_in = False
                logger.info("Logged out successfully")
                return True
        except Exception as e:
            logger.error(f"Error logging out: {str(e)}")
            return False

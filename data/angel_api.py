import logging
from smartapi import SmartConnect
from config.settings import Config

logger = logging.getLogger(__name__)

class AngelOneAPI:
    """Angel One SmartAPI wrapper"""
    
    def __init__(self):
        self.api_key = Config.ANGEL_API_KEY
        self.client_code = Config.ANGEL_CLIENT_CODE
        self.password = Config.ANGEL_PASSWORD
        self.totp = Config.ANGEL_TOTP
        self.smartapi = None
        self.auth_token = None
        self.feed_token = None
        
    def login(self):
        """Login to Angel One API"""
        try:
            self.smartapi = SmartConnect(api_key=self.api_key)
            
            # Generate session
            data = self.smartapi.generateSession(
                self.client_code,
                self.password,
                self.totp
            )
            
            if data['status']:
                self.auth_token = data['data']['jwtToken']
                self.feed_token = data['data']['feedToken']
                logger.info(f"Successfully logged in. Auth Token: {self.auth_token[:10]}...")
                return True
            else:
                logger.error(f"Login failed: {data['message']}")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False
    
    def get_ltp(self, symbol):
        """Get Last Traded Price"""
        try:
            mode = 'LTP'
            exchange_tokens = self._get_exchange_token(symbol)
            
            if not exchange_tokens:
                return None
            
            data = self.smartapi.getQuotes(
                mode=mode,
                exchangeTokens=exchange_tokens
            )
            
            if data['status']:
                return data['data']['fetched'][0]['ltp']
            else:
                logger.error(f"Failed to get LTP for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting LTP: {str(e)}")
            return None
    
    def get_quote(self, symbol):
        """Get full quote for symbol"""
        try:
            mode = 'FULL'
            exchange_tokens = self._get_exchange_token(symbol)
            
            if not exchange_tokens:
                return None
            
            data = self.smartapi.getQuotes(
                mode=mode,
                exchangeTokens=exchange_tokens
            )
            
            if data['status']:
                return data['data']['fetched'][0]
            else:
                logger.error(f"Failed to get quote for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting quote: {str(e)}")
            return None
    
    def place_order(self, symbol, transaction_type, quantity, price=None, order_type='MARKET'):
        """Place an order"""
        try:
            exchange_token = self._get_exchange_token(symbol)
            
            order_data = {
                'mode': 'FULL',
                'exchangeTokens': exchange_token
            }
            
            order = self.smartapi.placeOrder(
                orderType=order_type,
                price=price or 0,
                product='MIS',
                quantity=quantity,
                symbol=symbol,
                transactionType=transaction_type,
                validity='DAY'
            )
            
            if order['status']:
                logger.info(f"Order placed: {order['data']['orderid']}")
                return order['data']
            else:
                logger.error(f"Order placement failed: {order['message']}")
                return None
                
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return None
    
    def get_positions(self):
        """Get current positions"""
        try:
            data = self.smartapi.getPosition()
            
            if data['status']:
                return data['data']['net']
            else:
                logger.error(f"Failed to get positions")
                return []
                
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            return []
    
    def get_orders(self):
        """Get order history"""
        try:
            data = self.smartapi.orderBook()
            
            if data['status']:
                return data['data']
            else:
                logger.error(f"Failed to get orders")
                return []
                
        except Exception as e:
            logger.error(f"Error getting orders: {str(e)}")
            return []
    
    def cancel_order(self, order_id):
        """Cancel an order"""
        try:
            data = self.smartapi.cancelOrder(orderid=order_id)
            
            if data['status']:
                logger.info(f"Order cancelled: {order_id}")
                return True
            else:
                logger.error(f"Failed to cancel order: {data['message']}")
                return False
                
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return False
    
    def _get_exchange_token(self, symbol):
        """Get exchange token for symbol (implement based on NSE symbol mapping)"""
        # This would need a mapping of NSE symbols to exchange tokens
        # For now, returning a placeholder
        pass
    
    def logout(self):
        """Logout from API"""
        try:
            if self.smartapi:
                self.smartapi.terminateSession()
                logger.info("Logged out successfully")
                return True
        except Exception as e:
            logger.error(f"Error logging out: {str(e)}")
            return False

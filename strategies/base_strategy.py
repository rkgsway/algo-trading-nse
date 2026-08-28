import logging
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, symbol, timeframe='5', max_position_size=1):
        self.symbol = symbol
        self.timeframe = timeframe
        self.max_position_size = max_position_size
        self.position = 0  # 0: no position, 1: long, -1: short
        self.entry_price = None
        self.entry_time = None
        self.trades = []
    
    @abstractmethod
    def generate_signal(self, data):
        """
        Generate trading signal based on strategy logic
        
        Args:
            data: Market data (DataFrame or dict)
        
        Returns:
            Signal: 1 (BUY), -1 (SELL), 0 (HOLD)
        """
        pass
    
    def on_bar_close(self, data):
        """Called when a candle closes"""
        signal = self.generate_signal(data)
        return signal
    
    def on_trade_entry(self, symbol, price, quantity, direction):
        """Called when entering a trade"""
        self.position = direction
        self.entry_price = price
        self.entry_time = datetime.now()
        logger.info(f"Entry: {symbol} @ {price} ({quantity} units) - {direction}")
    
    def on_trade_exit(self, symbol, price, quantity, pnl):
        """Called when exiting a trade"""
        self.position = 0
        trade = {
            'symbol': symbol,
            'entry_price': self.entry_price,
            'exit_price': price,
            'quantity': quantity,
            'direction': 'BUY' if self.entry_price < price else 'SELL',
            'pnl': pnl,
            'pnl_percent': (pnl / (self.entry_price * quantity)) * 100,
            'entry_time': self.entry_time,
            'exit_time': datetime.now()
        }
        self.trades.append(trade)
        logger.info(f"Exit: {symbol} @ {price} - P&L: ₹{pnl:.2f}")
    
    def get_statistics(self):
        """Get strategy performance statistics"""
        if not self.trades:
            return {}
        
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t['pnl'] > 0)
        losing_trades = sum(1 for t in self.trades if t['pnl'] < 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(t['pnl'] for t in self.trades)
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
        
        winning_avg = sum(t['pnl'] for t in self.trades if t['pnl'] > 0) / winning_trades if winning_trades > 0 else 0
        losing_avg = sum(t['pnl'] for t in self.trades if t['pnl'] < 0) / losing_trades if losing_trades > 0 else 0
        
        profit_factor = abs(winning_avg * winning_trades / (losing_avg * losing_trades)) if losing_avg != 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'profit_factor': profit_factor,
            'trades': self.trades
        }

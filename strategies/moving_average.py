import pandas as pd
from strategies.base_strategy import BaseStrategy

class MovingAverageStrategy(BaseStrategy):
    """Simple Moving Average Crossover Strategy"""
    
    def __init__(self, symbol, timeframe='5', fast_period=20, slow_period=50, max_position_size=1):
        super().__init__(symbol, timeframe, max_position_size)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.name = 'Moving Average Crossover'
    
    def generate_signal(self, data):
        """
        Generate signal based on MA crossover
        
        BUY when fast MA > slow MA
        SELL when fast MA < slow MA
        """
        if len(data) < self.slow_period:
            return 0  # Not enough data
        
        # Calculate moving averages
        data['fast_ma'] = data['close'].rolling(window=self.fast_period).mean()
        data['slow_ma'] = data['close'].rolling(window=self.slow_period).mean()
        
        # Get latest values
        fast_ma = data['fast_ma'].iloc[-1]
        slow_ma = data['slow_ma'].iloc[-1]
        current_price = data['close'].iloc[-1]
        
        # Check crossover
        if len(data) > 1:
            prev_fast = data['fast_ma'].iloc[-2]
            prev_slow = data['slow_ma'].iloc[-2]
            
            # Bullish crossover
            if prev_fast <= prev_slow and fast_ma > slow_ma:
                return 1  # BUY
            
            # Bearish crossover
            elif prev_fast >= prev_slow and fast_ma < slow_ma:
                return -1  # SELL
        
        return 0  # HOLD
    
    def get_strategy_params(self):
        """Return strategy parameters"""
        return {
            'name': self.name,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
            'max_position_size': self.max_position_size
        }

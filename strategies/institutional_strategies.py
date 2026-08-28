import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class VolumeProfileStrategy(BaseStrategy):
    """
    Volume Profile Strategy - Identifies institutional accumulation/distribution zones
    
    Institutional traders create distinctive volume profiles at key price levels.
    This strategy identifies:
    - Point of Control (POC) - price level with highest volume
    - Value Area - price range containing 70% of volume
    - Volume Nodes - accumulation zones
    """
    
    def __init__(self, symbol, timeframe='5', period=20, volume_threshold=1.5, max_position_size=1):
        super().__init__(symbol, timeframe, max_position_size)
        self.period = period
        self.volume_threshold = volume_threshold
        self.name = 'Volume Profile'
        self.poc = None
        self.value_area_high = None
        self.value_area_low = None
    
    def generate_signal(self, data):
        """
        Generate signals based on volume profile analysis
        
        BUY: Price approaches POC from above with institutional volume
        SELL: Price approaches POC from below with institutional volume
        """
        if len(data) < self.period:
            return 0
        
        recent_data = data.iloc[-self.period:]
        
        # Calculate Volume Profile
        self._calculate_volume_profile(recent_data)
        
        # Get current price and volume
        current_price = data['close'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].tail(20).mean()
        
        # Check for institutional volume
        volume_strength = current_volume / avg_volume if avg_volume > 0 else 0
        
        if len(data) < 2:
            return 0
        
        prev_price = data['close'].iloc[-2]
        
        # Signal Logic
        if self.poc and self.value_area_low and self.value_area_high:
            # Institutional buying at value area (support)
            if (current_price > self.value_area_low and 
                prev_price <= self.value_area_low and 
                volume_strength > self.volume_threshold):
                return 1  # BUY
            
            # Institutional selling at value area (resistance)
            elif (current_price < self.value_area_high and 
                  prev_price >= self.value_area_high and 
                  volume_strength > self.volume_threshold):
                return -1  # SELL
        
        return 0
    
    def _calculate_volume_profile(self, data):
        """Calculate volume profile metrics"""
        try:
            # Sort by price
            price_volume = data[['close', 'volume']].copy()
            price_volume['price_bucket'] = pd.cut(price_volume['close'], bins=20)
            
            # Group and sum volume by price bucket
            profile = price_volume.groupby('price_bucket')['volume'].sum().sort_values(ascending=False)
            
            if len(profile) > 0:
                # Point of Control (highest volume price)
                poc_interval = profile.index[0]
                self.poc = (poc_interval.left + poc_interval.right) / 2
                
                # Value Area (70% of total volume)
                cumsum = profile.cumsum()
                total_volume = cumsum.iloc[-1]
                value_area_volume = total_volume * 0.7
                
                value_area_indices = cumsum[cumsum <= value_area_volume].index
                if len(value_area_indices) > 0:
                    self.value_area_high = value_area_indices[0].right
                    self.value_area_low = value_area_indices[-1].left
        
        except Exception as e:
            logger.error(f"Error calculating volume profile: {str(e)}")
    
    def get_strategy_params(self):
        return {
            'name': self.name,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'period': self.period,
            'volume_threshold': self.volume_threshold,
            'poc': self.poc,
            'value_area_high': self.value_area_high,
            'value_area_low': self.value_area_low
        }


class OrderBlockStrategy(BaseStrategy):
    """
    Order Block Strategy - Identifies institutional order placement zones
    
    When institutional traders place large orders, they create:
    - Sharp reversals
    - Price rejections at specific levels
    - Volume surges followed by price movement
    
    This identifies these institutional "order blocks"
    """
    
    def __init__(self, symbol, timeframe='5', lookback=10, min_reversal_points=3, max_position_size=1):
        super().__init__(symbol, timeframe, max_position_size)
        self.lookback = lookback
        self.min_reversal_points = min_reversal_points
        self.name = 'Order Block'
        self.bullish_blocks = []
        self.bearish_blocks = []
    
    def generate_signal(self, data):
        """
        Generate signals based on order blocks
        
        BUY: Price retests bullish order block (support created by selling)
        SELL: Price retests bearish order block (resistance created by buying)
        """
        if len(data) < self.lookback + 5:
            return 0
        
        # Identify order blocks
        self._identify_order_blocks(data)
        
        current_price = data['close'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].tail(20).mean()
        
        # Check if price is at an order block
        for block in self.bullish_blocks[-3:]:  # Check last 3 blocks
            if (block['low'] <= current_price <= block['high'] and 
                current_volume > avg_volume * 1.3):
                return 1  # BUY at bullish block support
        
        for block in self.bearish_blocks[-3:]:
            if (block['low'] <= current_price <= block['high'] and 
                current_volume > avg_volume * 1.3):
                return -1  # SELL at bearish block resistance
        
        return 0
    
    def _identify_order_blocks(self, data):
        """Identify bullish and bearish order blocks"""
        try:
            prices = data['close'].values
            self.bullish_blocks = []
            self.bearish_blocks = []
            
            # Look for reversals (order blocks)
            for i in range(self.lookback, len(prices) - 1):
                # Bullish reversal (low followed by higher close)
                if (prices[i] < prices[i-1] and prices[i] < prices[i+1] and 
                    data['volume'].iloc[i] > data['volume'].tail(20).mean()):
                    
                    self.bullish_blocks.append({
                        'low': prices[i],
                        'high': prices[i] * 1.01,  # Small range
                        'timestamp': data.index[i] if isinstance(data.index, pd.DatetimeIndex) else i,
                        'strength': data['volume'].iloc[i]
                    })
                
                # Bearish reversal (high followed by lower close)
                if (prices[i] > prices[i-1] and prices[i] > prices[i+1] and 
                    data['volume'].iloc[i] > data['volume'].tail(20).mean()):
                    
                    self.bearish_blocks.append({
                        'low': prices[i] * 0.99,
                        'high': prices[i],
                        'timestamp': data.index[i] if isinstance(data.index, pd.DatetimeIndex) else i,
                        'strength': data['volume'].iloc[i]
                    })
        
        except Exception as e:
            logger.error(f"Error identifying order blocks: {str(e)}")
    
    def get_strategy_params(self):
        return {
            'name': self.name,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'bullish_blocks': len(self.bullish_blocks),
            'bearish_blocks': len(self.bearish_blocks)
        }


class ICTStrategy(BaseStrategy):
    """
    ICT (Inner Circle Trading) Strategy - Advanced institutional method
    
    Concepts:
    - Smart Money Concentration (SMC) zones
    - Liquidity pools (where Stop Losses cluster)
    - Fair Value Gaps (FVG) - unmitigated price zones
    - Breaker blocks - institutional entry zones
    """
    
    def __init__(self, symbol, timeframe='5', fvg_threshold=0.005, max_position_size=1):
        super().__init__(symbol, timeframe, max_position_size)
        self.fvg_threshold = fvg_threshold
        self.name = 'ICT (Inner Circle Trading)'
        self.fair_value_gaps = []
        self.liquidity_pools = []
    
    def generate_signal(self, data):
        """
        Generate signals based on ICT concepts
        
        BUY: Price enters Fair Value Gap + Liquidity Pool with proper structure
        SELL: Same but in opposite direction
        """
        if len(data) < 10:
            return 0
        
        # Identify Fair Value Gaps
        self._identify_fvg(data)
        
        # Identify Liquidity Pools
        self._identify_liquidity_pools(data)
        
        current_price = data['close'].iloc[-1]
        
        # Check if price is in FVG
        for gap in self.fair_value_gaps[-3:]:
            if gap['low'] <= current_price <= gap['high']:
                # Check if market structure is bullish
                if self._is_bullish_structure(data):
                    return 1  # BUY in bullish FVG
                elif self._is_bearish_structure(data):
                    return -1  # SELL in bearish FVG
        
        return 0
    
    def _identify_fvg(self, data):
        """Identify Fair Value Gaps - unmitigated price zones"""
        try:
            prices = data['close'].values
            highs = data['high'].values
            lows = data['low'].values
            
            self.fair_value_gaps = []
            
            for i in range(2, len(prices) - 1):
                # Bullish FVG (gap up)
                if lows[i] > highs[i-2]:
                    gap_size = lows[i] - highs[i-2]
                    if gap_size / highs[i-2] > self.fvg_threshold:
                        self.fair_value_gaps.append({
                            'type': 'bullish',
                            'low': highs[i-2],
                            'high': lows[i],
                            'timestamp': i
                        })
                
                # Bearish FVG (gap down)
                elif highs[i] < lows[i-2]:
                    gap_size = lows[i-2] - highs[i]
                    if gap_size / lows[i-2] > self.fvg_threshold:
                        self.fair_value_gaps.append({
                            'type': 'bearish',
                            'low': highs[i],
                            'high': lows[i-2],
                            'timestamp': i
                        })
        
        except Exception as e:
            logger.error(f"Error identifying FVG: {str(e)}")
    
    def _identify_liquidity_pools(self, data):
        """Identify liquidity pools - where stop losses cluster"""
        try:
            prices = data['close'].values
            volumes = data['volume'].values
            
            self.liquidity_pools = []
            
            # Find price levels with high volume clusters
            for i in range(10, len(prices) - 5):
                window = prices[i-5:i+5]
                if len(window) > 0:
                    # Check for price cluster (low volatility + high volume)
                    std_dev = np.std(window)
                    avg_vol = np.mean(volumes[i-5:i+5])
                    
                    if std_dev < (np.mean(window) * 0.01) and avg_vol > np.mean(volumes) * 1.5:
                        self.liquidity_pools.append({
                            'price': np.mean(window),
                            'strength': avg_vol,
                            'timestamp': i
                        })
        
        except Exception as e:
            logger.error(f"Error identifying liquidity pools: {str(e)}")
    
    def _is_bullish_structure(self, data):
        """Check if market structure is bullish"""
        if len(data) < 5:
            return False
        recent = data['close'].tail(5).values
        return recent[-1] > recent[-2] and recent[-2] > recent[-3]
    
    def _is_bearish_structure(self, data):
        """Check if market structure is bearish"""
        if len(data) < 5:
            return False
        recent = data['close'].tail(5).values
        return recent[-1] < recent[-2] and recent[-2] < recent[-3]
    
    def get_strategy_params(self):
        return {
            'name': self.name,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'fair_value_gaps': len(self.fair_value_gaps),
            'liquidity_pools': len(self.liquidity_pools),
            'fvg_threshold': self.fvg_threshold
        }


class SmartMoneyFlowStrategy(BaseStrategy):
    """
    Smart Money Flow Strategy - Tracks institutional money movement
    
    Identifies:
    - Large volume accumulation (before breakouts)
    - Distribution patterns (before breakdowns)
    - VWAP divergences (institutional trades vs retail)
    - Money flow ratio (buy pressure vs sell pressure)
    """
    
    def __init__(self, symbol, timeframe='5', accumulation_period=20, max_position_size=1):
        super().__init__(symbol, timeframe, max_position_size)
        self.accumulation_period = accumulation_period
        self.name = 'Smart Money Flow'
    
    def generate_signal(self, data):
        """
        Generate signals based on smart money flow analysis
        
        BUY: Accumulation phase + VWAP breakout
        SELL: Distribution phase + VWAP breakdown
        """
        if len(data) < self.accumulation_period:
            return 0
        
        # Calculate VWAP
        vwap = self._calculate_vwap(data)
        
        # Calculate Money Flow Ratio
        mfr = self._calculate_money_flow_ratio(data)
        
        # Calculate Accumulation/Distribution
        ad = self._calculate_accumulation_distribution(data)
        
        current_price = data['close'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].tail(20).mean()
        
        if len(data) < 2:
            return 0
        
        prev_price = data['close'].iloc[-2]
        prev_vwap = vwap.iloc[-2] if len(vwap) > 1 else vwap.iloc[-1]
        
        # Bullish Signal: Price above VWAP + Strong Money Flow + High Volume
        if (current_price > vwap.iloc[-1] and prev_price <= prev_vwap and
            mfr > 0.6 and ad.iloc[-1] > ad.iloc[-self.accumulation_period] and
            current_volume > avg_volume * 1.2):
            return 1  # BUY
        
        # Bearish Signal: Price below VWAP + Weak Money Flow + High Volume
        elif (current_price < vwap.iloc[-1] and prev_price >= prev_vwap and
              mfr < 0.4 and ad.iloc[-1] < ad.iloc[-self.accumulation_period] and
              current_volume > avg_volume * 1.2):
            return -1  # SELL
        
        return 0
    
    def _calculate_vwap(self, data):
        """Calculate Volume Weighted Average Price"""
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        vwap = (typical_price * data['volume']).rolling(window=self.accumulation_period).sum() / \
               data['volume'].rolling(window=self.accumulation_period).sum()
        return vwap
    
    def _calculate_money_flow_ratio(self, data):
        """Calculate Money Flow Ratio (Buy Pressure / Total Volume)"""
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        money_flow = typical_price * data['volume']
        
        # Positive flow when price > previous close
        positive_flow = money_flow[data['close'] > data['close'].shift(1)].sum()
        total_flow = money_flow.sum()
        
        if total_flow > 0:
            return positive_flow / total_flow
        return 0.5
    
    def _calculate_accumulation_distribution(self, data):
        """Calculate Accumulation/Distribution Line"""
        clv = ((data['close'] - data['low']) - (data['high'] - data['close'])) / \
              (data['high'] - data['low'])
        clv = clv.fillna(0)
        ad = (clv * data['volume']).cumsum()
        return ad
    
    def get_strategy_params(self):
        return {
            'name': self.name,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'accumulation_period': self.accumulation_period
        }


class LiquiditySweeperStrategy(BaseStrategy):
    """
    Liquidity Sweeper Strategy - Institutional trap identification
    
    Institutions often:
    1. Move price to hit stop losses (sweep liquidity)
    2. Then reverse and move in the intended direction
    
    This catches the reversal after liquidity sweeps
    """
    
    def __init__(self, symbol, timeframe='5', swing_length=5, max_position_size=1):
        super().__init__(symbol, timeframe, max_position_size)
        self.swing_length = swing_length
        self.name = 'Liquidity Sweeper'
        self.recent_high = None
        self.recent_low = None
    
    def generate_signal(self, data):
        """
        Generate signals based on liquidity sweeps
        
        BUY: Price breaks below recent low + volume spike, then reverses
        SELL: Price breaks above recent high + volume spike, then reverses
        """
        if len(data) < self.swing_length + 5:
            return 0
        
        # Find recent swing high and low
        self._identify_swings(data)
        
        current_price = data['close'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].tail(20).mean()
        
        if len(data) < 2:
            return 0
        
        prev_price = data['close'].iloc[-2]
        prev_prev_price = data['close'].iloc[-3] if len(data) >= 3 else prev_price
        
        # Check for liquidity sweep followed by reversal
        if self.recent_low and self.recent_high:
            # Bearish sweep (break below + high volume + reversal)
            if (prev_price < self.recent_low and 
                current_price > prev_price and
                current_volume > avg_volume * 1.5):
                return 1  # BUY after bearish sweep
            
            # Bullish sweep (break above + high volume + reversal)
            elif (prev_price > self.recent_high and 
                  current_price < prev_price and
                  current_volume > avg_volume * 1.5):
                return -1  # SELL after bullish sweep
        
        return 0
    
    def _identify_swings(self, data):
        """Identify recent swing high and low"""
        try:
            recent = data['close'].tail(self.swing_length)
            self.recent_high = recent.max()
            self.recent_low = recent.min()
        except Exception as e:
            logger.error(f"Error identifying swings: {str(e)}")
    
    def get_strategy_params(self):
        return {
            'name': self.name,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'recent_high': self.recent_high,
            'recent_low': self.recent_low,
            'swing_length': self.swing_length
        }


class SupertrendRSIStrategy(BaseStrategy):
    """
    Supertrend + RSI Strategy - Institutional Breakout with Momentum Confirmation
    
    Combines:
    - Supertrend for trend identification and stop loss placement
    - RSI for momentum confirmation (>55 bullish, <45 bearish)
    
    This catches strong institutional moves with proper risk management
    
    Supertrend is ideal for institutions because:
    - Clear entry/exit points
    - Built-in stop losses
    - Works well with high volume moves
    
    RSI Confirmation:
    - RSI > 55: Strong bullish momentum (not overbought)
    - RSI < 45: Strong bearish momentum (not oversold)
    - 45-55: Neutral zone, avoid trading
    """
    
    def __init__(self, symbol, timeframe='5', atr_period=10, atr_multiplier=3.0, 
                 rsi_period=14, rsi_bullish=55, rsi_bearish=45, max_position_size=1):
        super().__init__(symbol, timeframe, max_position_size)
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.rsi_period = rsi_period
        self.rsi_bullish = rsi_bullish  # RSI > 55 = Strong bullish
        self.rsi_bearish = rsi_bearish  # RSI < 45 = Strong bearish
        self.name = 'Supertrend + RSI'
        self.supertrend = None
        self.supertrend_direction = None
    
    def generate_signal(self, data):
        """
        Generate signals combining Supertrend + RSI momentum
        
        BUY: 
        - Supertrend is bullish (price above lower band)
        - RSI > 55 (strong momentum)
        - Volume confirmation
        
        SELL:
        - Supertrend is bearish (price below upper band)
        - RSI < 45 (strong bearish momentum)
        - Volume confirmation
        """
        if len(data) < max(self.atr_period, self.rsi_period) + 5:
            return 0
        
        # Calculate Supertrend
        supertrend, supertrend_direction = self._calculate_supertrend(data)
        
        # Calculate RSI
        rsi = self._calculate_rsi(data)
        
        if supertrend is None or rsi is None:
            return 0
        
        current_price = data['close'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].tail(20).mean()
        
        # Get current values
        current_supertrend = supertrend.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_direction = supertrend_direction.iloc[-1]
        
        # Bullish Signal
        if (current_direction > 0 and  # Supertrend is bullish
            current_rsi > self.rsi_bullish and  # RSI > 55 (strong momentum)
            current_price > current_supertrend and  # Price above Supertrend line
            current_volume > avg_volume * 1.2):  # Volume confirmation
            return 1  # BUY
        
        # Bearish Signal
        elif (current_direction < 0 and  # Supertrend is bearish
              current_rsi < self.rsi_bearish and  # RSI < 45 (weak momentum)
              current_price < current_supertrend and  # Price below Supertrend line
              current_volume > avg_volume * 1.2):  # Volume confirmation
            return -1  # SELL
        
        return 0  # HOLD
    
    def _calculate_supertrend(self, data):
        """
        Calculate Supertrend indicator
        
        Formula:
        1. Calculate ATR (Average True Range)
        2. Basic Upperband = (HIGH + LOW) / 2 + Multiplier * ATR
        3. Basic Lowerband = (HIGH + LOW) / 2 - Multiplier * ATR
        4. Final Band = Adjust based on previous values
        5. Supertrend = Upper band if price below, Lower band if above
        """
        try:
            high = data['high']
            low = data['low']
            close = data['close']
            
            # Calculate ATR
            atr = self._calculate_atr(data)
            
            # Calculate basic bands
            hl2 = (high + low) / 2
            matr = self.atr_multiplier * atr
            
            basic_ub = hl2 + matr
            basic_lb = hl2 - matr
            
            # Calculate final bands
            final_ub = basic_ub.copy()
            final_lb = basic_lb.copy()
            
            for i in range(1, len(final_ub)):
                final_ub.iloc[i] = basic_ub.iloc[i] if basic_ub.iloc[i] < final_ub.iloc[i-1] or close.iloc[i-1] > final_ub.iloc[i-1] else final_ub.iloc[i-1]
                final_lb.iloc[i] = basic_lb.iloc[i] if basic_lb.iloc[i] > final_lb.iloc[i-1] or close.iloc[i-1] < final_lb.iloc[i-1] else final_lb.iloc[i-1]
            
            # Determine Supertrend
            supertrend = pd.Series(index=data.index, dtype='float64')
            direction = pd.Series(index=data.index, dtype='float64')
            
            for i in range(len(data)):
                if i == 0:
                    supertrend.iloc[i] = close.iloc[i]
                    direction.iloc[i] = 1
                else:
                    if close.iloc[i] <= final_ub.iloc[i]:
                        supertrend.iloc[i] = final_ub.iloc[i]
                        direction.iloc[i] = -1
                    else:
                        supertrend.iloc[i] = final_lb.iloc[i]
                        direction.iloc[i] = 1
            
            return supertrend, direction
        
        except Exception as e:
            logger.error(f"Error calculating Supertrend: {str(e)}")
            return None, None
    
    def _calculate_atr(self, data):
        """Calculate Average True Range"""
        try:
            high = data['high']
            low = data['low']
            close = data['close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=self.atr_period).mean()
            
            return atr
        
        except Exception as e:
            logger.error(f"Error calculating ATR: {str(e)}")
            return None
    
    def _calculate_rsi(self, data):
        """
        Calculate Relative Strength Index (RSI)
        
        Formula:
        1. Calculate price changes
        2. Separate gains and losses
        3. Calculate average gain and loss over period
        4. RS = Average Gain / Average Loss
        5. RSI = 100 - (100 / (1 + RS))
        """
        try:
            close = data['close']
            delta = close.diff()
            
            gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
        
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return None
    
    def get_strategy_params(self):
        return {
            'name': self.name,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'atr_period': self.atr_period,
            'atr_multiplier': self.atr_multiplier,
            'rsi_period': self.rsi_period,
            'rsi_bullish_threshold': self.rsi_bullish,
            'rsi_bearish_threshold': self.rsi_bearish,
            'max_position_size': self.max_position_size
        }

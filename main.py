#!/usr/bin/env python3
"""
NSE Algorithmic Trading Bot
Integrated with Angel One broker
"""

import logging
import sys
from datetime import datetime
from config.settings import Config
from data.angel_api import AngelOneAPI
from data.data_fetcher import DataFetcher
from strategies.moving_average import MovingAverageStrategy
from utils.logger import setup_logger

logger = setup_logger(__name__)

class TradingBot:
    """Main trading bot class"""
    
    def __init__(self, skip_angel_login=False):
        logger.info("Initializing Trading Bot...")
        
        # Validate configuration FIRST before initializing API
        try:
            Config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            sys.exit(1)
        
        self.skip_angel_login = skip_angel_login
        self.data_fetcher = DataFetcher(skip_login=skip_angel_login)
        self.angel = AngelOneAPI()
        self.strategies = []
        self.positions = {}
        self.orders = {}
    
    def add_strategy(self, strategy):
        """Add a strategy to the bot"""
        self.strategies.append(strategy)
        logger.info(f"Added strategy: {strategy.name} for {strategy.symbol}")
    
    def run_backtest(self, strategy, start_date, end_date):
        """
        Run backtesting for a strategy
        
        Args:
            strategy: Strategy object
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        """
        logger.info(f"Starting backtest for {strategy.symbol} ({start_date} to {end_date})")
        
        try:
            # Fetch historical data
            data = self.data_fetcher.get_candles(
                strategy.symbol,
                strategy.timeframe,
                start_date,
                end_date
            )
            
            if data.empty:
                logger.warning(f"No data available for backtest")
                return
            
            # Process each candle
            for idx in range(strategy.slow_period, len(data)):
                candle_data = data.iloc[:idx+1]
                signal = strategy.on_bar_close(candle_data)
                
                # Execute trades based on signals
                if signal == 1 and strategy.position == 0:
                    logger.info(f"Backtest BUY signal at {data.iloc[idx]['timestamp']}")
                    strategy.on_trade_entry(
                        strategy.symbol,
                        data.iloc[idx]['close'],
                        100,
                        1
                    )
                
                elif signal == -1 and strategy.position == 1:
                    logger.info(f"Backtest SELL signal at {data.iloc[idx]['timestamp']}")
                    pnl = (data.iloc[idx]['close'] - strategy.entry_price) * 100
                    strategy.on_trade_exit(
                        strategy.symbol,
                        data.iloc[idx]['close'],
                        100,
                        pnl
                    )
            
            # Print statistics
            stats = strategy.get_statistics()
            logger.info("\n" + "="*50)
            logger.info("BACKTEST RESULTS")
            logger.info("="*50)
            logger.info(f"Total Trades: {stats.get('total_trades', 0)}")
            logger.info(f"Winning Trades: {stats.get('winning_trades', 0)}")
            logger.info(f"Losing Trades: {stats.get('losing_trades', 0)}")
            logger.info(f"Win Rate: {stats.get('win_rate', 0):.2f}%")
            logger.info(f"Total P&L: ₹{stats.get('total_pnl', 0):.2f}")
            logger.info(f"Average P&L: ₹{stats.get('avg_pnl', 0):.2f}")
            logger.info(f"Profit Factor: {stats.get('profit_factor', 0):.2f}")
            logger.info("="*50 + "\n")
            
        except Exception as e:
            logger.error(f"Backtest error: {str(e)}")
    
    def run_live(self):
        """Run live trading"""
        if not Config.LIVE_TRADING:
            logger.warning("Live trading is disabled. Set LIVE_TRADING=true in .env")
            return
        
        logger.info("Starting live trading...")
        
        if not self.angel.login():
            logger.error("Failed to login to Angel One")
            return
        
        try:
            # Trading loop would go here
            pass
        
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        
        finally:
            self.angel.logout()
    
    def shutdown(self):
        """Cleanup and shutdown"""
        logger.info("Shutting down Trading Bot")
        self.angel.logout()

def main():
    """Main entry point"""
    
    # Create bot instance with skip_angel_login=True for backtesting
    # Set to False if you want to login to Angel One before backtesting
    bot = TradingBot(skip_angel_login=True)
    
    # Create and add strategy
    strategy = MovingAverageStrategy(
        symbol='SBIN',
        timeframe='5',
        fast_period=20,
        slow_period=50
    )
    bot.add_strategy(strategy)
    
    # Run backtest
    logger.info("Starting application...")
    bot.run_backtest(strategy, '2023-01-01', '2023-12-31')
    
    # Uncomment for live trading
    # bot.run_live()
    
    # Cleanup
    bot.shutdown()

if __name__ == '__main__':
    main()

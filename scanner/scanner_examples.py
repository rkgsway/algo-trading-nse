#!/usr/bin/env python3
"""
Multi-Symbol Scanner - Example Usage Scripts
Demonstrates how to use the scanner for 210+ FnO stocks and indices
"""

import sys
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from scanner.multi_symbol_scanner import MultiSymbolScanner

# ============================================================================
# EXAMPLE 1: Simple One-Time Scan
# ============================================================================

def example_1_simple_scan():
    """
    Scan all 210+ FnO stocks + indices once and print results
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Simple One-Time Scan")
    print("="*80)
    
    # Create scanner
    scanner = MultiSymbolScanner(
        max_workers=20,      # 20 parallel threads
        timeframe='5'        # 5-minute candles
    )
    
    # Get list of symbols to scan
    all_symbols = scanner.get_all_scan_symbols()
    print(f"\nTotal symbols to scan: {len(all_symbols)}")
    print(f"  - FnO Stocks: {len(scanner.get_fno_stocks())}")
    print(f"  - Indices: {len(scanner.get_major_indices())}")
    
    # Scan all symbols
    print(f"\nScanning {len(all_symbols)} symbols...")
    signals = scanner.scan_all_symbols()
    
    # Print results
    scanner.print_signals_summary()
    
    # Print statistics
    stats = scanner.get_scan_stats()
    print(f"\nStatistics:")
    print(f"  Total Scanned: {stats['total_scanned']}")
    print(f"  Buy Signals: {stats['buy_signals']}")
    print(f"  Sell Signals: {stats['sell_signals']}")
    print(f"  Buy/Sell Ratio: {stats['buy_sell_ratio']:.2f}")

# ============================================================================
# EXAMPLE 2: Scan Specific Sector
# ============================================================================

def example_2_sector_scan(sector='Banking'):
    """
    Scan only a specific sector
    
    Args:
        sector: 'Banking', 'IT', 'Pharma', 'Auto', 'FMCG', 'Energy', 'Metals'
    """
    print("\n" + "="*80)
    print(f"EXAMPLE 2: {sector} Sector Scan")
    print("="*80)
    
    scanner = MultiSymbolScanner(max_workers=10, timeframe='5')
    
    # Define sectors
    sectors_map = {
        'Banking': ['SBIN', 'ICICIBANK', 'KOTAKBANK', 'AXISBANK', 'INDUSIND', 
                    'AUBANK', 'BANKBARODA', 'IDFCBANK', 'HDFC', 'HDFCBANK'],
        
        'IT': ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTIM', 
               'MINDTREE', 'KPITTECH', 'BSOFT'],
        
        'Pharma': ['SUNPHARMA', 'DRREDDY', 'LUPIN', 'CIPLA', 'ALKEM', 
                   'ABBOTINDIA', 'BIOCON', 'GLENMARK'],
        
        'Auto': ['MARUTI', 'BAJAJ-AUTO', 'EICHERMOT', 'HEROMOTOCO', 
                 'TATAMOTORS', 'MAHINDRA', 'HYUNDAI'],
        
        'FMCG': ['HINDUNILVR', 'BRITANNIA', 'ITC', 'TATACONSUM', 
                 'NESTLEIND', 'COLPAL', 'MARICO'],
        
        'Energy': ['RELIANCE', 'BPCL', 'ONGC', 'POWERGRID', 'NTPC', 'COAL'],
        
        'Metals': ['HINDALCO', 'JSWSTEEL', 'TATASTEELQ', 'NMDC', 'SAIL', 'VEDL']
    }
    
    symbols = sectors_map.get(sector, [])
    
    if not symbols:
        print(f"Sector '{sector}' not found!")
        return
    
    print(f"\nScanning {len(symbols)} stocks in {sector} sector...")
    signals = scanner.scan_all_symbols(symbols=symbols)
    
    # Print results
    scanner.print_signals_summary()
    
    # Group by signal
    buy_signals = [s for s in signals if s['signal'] == 1]
    sell_signals = [s for s in signals if s['signal'] == -1]
    
    print(f"\n{sector} Sector Summary:")
    print(f"  Buy Signals: {len(buy_signals)}")
    print(f"  Sell Signals: {len(sell_signals)}")
    
    if buy_signals:
        print("\n  Top Buy Opportunities:")
        for sig in sorted(buy_signals, key=lambda x: x['volume'], reverse=True)[:3]:
            print(f"    - {sig['symbol']}: {sig['ltp']:.2f} (Volume: {sig['volume']:,.0f})")

# ============================================================================
# EXAMPLE 3: Continuous Market Monitoring
# ============================================================================

def example_3_continuous_watch(duration_minutes=30, scan_interval_seconds=60):
    """
    Continuously scan market and report new signals
    
    Args:
        duration_minutes: How long to run the monitor
        scan_interval_seconds: Time between scans
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Continuous Market Monitoring")
    print("="*80)
    
    scanner = MultiSymbolScanner(max_workers=20, timeframe='5')
    
    duration_seconds = duration_minutes * 60
    scan_count = 0
    total_signals = []
    
    print(f"\nMonitoring market for {duration_minutes} minutes (scanning every {scan_interval_seconds}s)")
    print(f"Press Ctrl+C to stop\n")
    
    try:
        elapsed = 0
        while elapsed < duration_seconds:
            scan_count += 1
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            print(f"\n{'='*80}")
            print(f"Scan #{scan_count} at {timestamp}")
            print(f"{'='*80}")
            
            # Scan all symbols
            signals = scanner.scan_all_symbols()
            total_signals.extend(signals)
            
            if signals:
                scanner.print_signals_summary()
                
                # Export this scan's results
                csv_filename = f"scan_{scan_count:03d}_{datetime.now().strftime('%H%M%S')}.csv"
                scanner.export_signals_to_csv(csv_filename)
                logger.info(f"Results exported to {csv_filename}")
            else:
                logger.info("No signals found in this scan")
            
            elapsed += scan_interval_seconds
            
            if elapsed < duration_seconds:
                remaining = duration_seconds - elapsed
                logger.info(f"\nNext scan in {scan_interval_seconds}s (remaining: {remaining}s)")
                time.sleep(scan_interval_seconds)
        
        # Print summary
        print(f"\n{'='*80}")
        print("MONITORING COMPLETED")
        print(f"{'='*80}")
        print(f"Total scans: {scan_count}")
        print(f"Total signals found: {len(total_signals)}")
        
        if total_signals:
            buy = len([s for s in total_signals if s['signal'] == 1])
            sell = len([s for s in total_signals if s['signal'] == -1])
            print(f"Buy signals: {buy}, Sell signals: {sell}")
    
    except KeyboardInterrupt:
        print(f"\n\nMonitoring stopped by user")
        print(f"Total scans completed: {scan_count}")

# ============================================================================
# EXAMPLE 4: Export All Signals to CSV
# ============================================================================

def example_4_export_signals():
    """
    Scan and export results to CSV files
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Scan and Export to CSV")
    print("="*80)
    
    scanner = MultiSymbolScanner(max_workers=20, timeframe='5')
    
    print("\nScanning all 210+ stocks + indices...")
    signals = scanner.scan_all_symbols()
    
    if signals:
        print(f"\nFound {len(signals)} signals!")
        
        # Export to CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"trading_signals_{timestamp}.csv"
        scanner.export_signals_to_csv(csv_filename)
        
        print(f"\n✓ Exported to files:")
        print(f"  - {csv_filename}")
        print(f"  - buy_signals_{timestamp}.csv")
        print(f"  - sell_signals_{timestamp}.csv")
        
        # Also print to console
        df = scanner.get_signals_dataframe()
        print(f"\nSignal Summary:")
        print(df.to_string(index=False))
    else:
        print("No signals found in this scan")

# ============================================================================
# EXAMPLE 5: Sector-wise Analysis
# ============================================================================

def example_5_sector_analysis():
    """
    Scan all symbols and analyze results by sector
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Sector-wise Analysis")
    print("="*80)
    
    scanner = MultiSymbolScanner(max_workers=20, timeframe='5')
    
    print("\nScanning all symbols...")
    signals = scanner.scan_all_symbols()
    
    # Print sector summary
    scanner.print_sector_summary()
    
    # Get high volume signals
    print("\nTop 5 Signals by Volume:")
    print("-" * 80)
    top_volume = scanner.get_highest_volume_signals(limit=5)
    
    if top_volume:
        for i, sig in enumerate(top_volume, 1):
            print(f"{i}. {sig['symbol']:<15} {sig['signal_name']:<10} LTP: {sig['ltp']:>8.2f}  Vol: {sig['volume']:>12,.0f}")
    else:
        print("No signals found")

# ============================================================================
# EXAMPLE 6: Scan Only Indices
# ============================================================================

def example_6_index_scan():
    """
    Scan only major indices (not individual stocks)
    Useful for understanding overall market direction
    """
    print("\n" + "="*80)
    print("EXAMPLE 6: Major Indices Scan")
    print("="*80)
    
    scanner = MultiSymbolScanner(max_workers=10, timeframe='5')
    
    indices = scanner.get_major_indices()
    print(f"\nScanning {len(indices)} major indices:")
    for idx in indices:
        print(f"  - {idx}")
    
    print("\nScanning indices...")
    signals = scanner.scan_all_symbols(symbols=indices)
    
    # Print results
    scanner.print_signals_summary()
    
    if signals:
        print("\nIndex Analysis:")
        for sig in signals:
            direction = "UP ↑" if sig['signal'] == 1 else "DOWN ↓"
            print(f"  {sig['symbol']:<15} {direction:<10} {sig['ltp']:>8.2f}")

# ============================================================================
# EXAMPLE 7: High-Volume Signals Focus
# ============================================================================

def example_7_high_volume_focus():
    """
    Focus on signals with highest trading volume
    Generally more reliable for scalping/intraday
    """
    print("\n" + "="*80)
    print("EXAMPLE 7: High-Volume Signals (Best for Intraday)")
    print("="*80)
    
    scanner = MultiSymbolScanner(max_workers=20, timeframe='5')
    
    print("\nScanning all symbols...")
    signals = scanner.scan_all_symbols()
    
    if signals:
        # Get top 20 by volume
        top_signals = scanner.get_highest_volume_signals(limit=20)
        
        print(f"\nTop 20 Signals by Volume:")
        print("-" * 100)
        print(f"{'#':<3} {'Symbol':<15} {'Signal':<10} {'LTP':<12} {'Volume':<18} {'OI':<15}")
        print("-" * 100)
        
        for i, sig in enumerate(top_signals, 1):
            print(f"{i:<3} {sig['symbol']:<15} {sig['signal_name']:<10} {sig['ltp']:>10.2f}  {sig['volume']:>16,.0f}  {sig.get('oi', 0):>13,.0f}")
        
        print("-" * 100)
        print("\n💡 These high-volume signals are typically best for:")
        print("   - Scalping (2-5 min trades)")
        print("   - Intraday trading")
        print("   - Better liquidity for entries/exits")
    else:
        print("No signals found")

# ============================================================================
# EXAMPLE 8: NIFTY 50 Only Scan
# ============================================================================

def example_8_nifty50_scan():
    """
    Scan only NIFTY 50 stocks (bluechip companies)
    """
    print("\n" + "="*80)
    print("EXAMPLE 8: NIFTY 50 Stocks Scan (Bluechip)")
    print("="*80)
    
    scanner = MultiSymbolScanner(max_workers=15, timeframe='5')
    
    nifty50 = [
        'RELIANCE', 'TCS', 'INFY', 'HINDUNILVR', 'SBIN', 'ICICIBANK',
        'BAJAJFINSV', 'LT', 'MARUTI', 'HCLTECH', 'HDFC', 'WIPRO',
        'KOTAKBANK', 'AXISBANK', 'DMART', 'ITC', 'JSWSTEEL', 'SUNPHARMA',
        'BRITANNIA', 'BAJAJ-AUTO', 'ASIANPAINT', 'NTPC', 'SBILIFE',
        'POWERGRID', 'HDFCBANK', 'TECHM', 'BPCL', 'GRASIM', 'DIVISLAB',
        'APOLLOHOSP', 'SIEMENS', 'BAJAJHLDNG', 'ONGC', 'COAL', 'HAL',
        'EICHERMOT', 'ADANIPORTS', 'ADANIPOWER', 'TITAN', 'LTIM', 'CADILAHC',
        'CIPLA', 'ULTRACEMCO', 'HEROMOTOCO', 'INDIGO', 'TATACONSUM', 'HINDALCO',
        'JSWSTEEL', 'ASHOKLEY'
    ]
    
    print(f"\nScanning {len(nifty50)} NIFTY 50 stocks...")
    signals = scanner.scan_all_symbols(symbols=nifty50)
    
    # Print results
    scanner.print_signals_summary()

# ============================================================================
# Main Menu
# ============================================================================

def main():
    """
    Interactive menu for running examples
    """
    examples = {
        '1': ('Simple One-Time Scan', example_1_simple_scan),
        '2': ('Sector Scan (Banking)', lambda: example_2_sector_scan('Banking')),
        '3': ('Continuous Market Monitoring (30 min)', lambda: example_3_continuous_watch(30, 60)),
        '4': ('Scan and Export to CSV', example_4_export_signals),
        '5': ('Sector-wise Analysis', example_5_sector_analysis),
        '6': ('Major Indices Scan', example_6_index_scan),
        '7': ('High-Volume Signals Focus', example_7_high_volume_focus),
        '8': ('NIFTY 50 Scan', example_8_nifty50_scan),
    }
    
    print("\n" + "="*80)
    print("MULTI-SYMBOL SCANNER - EXAMPLE SCRIPTS")
    print("Scan 210+ FnO Stocks + Indices for Trading Signals")
    print("="*80)
    print("\nAvailable Examples:")
    
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    print("\n  0. Exit")
    print("\n" + "="*80)
    
    while True:
        choice = input("\nSelect example to run (0-8): ").strip()
        
        if choice == '0':
            print("Exiting...")
            break
        
        if choice in examples:
            name, func = examples[choice]
            print(f"\n\nRunning: {name}")
            
            try:
                func()
            except Exception as e:
                logger.error(f"Error running example: {e}")
                import traceback
                traceback.print_exc()
            
            input("\n\nPress Enter to continue...")
        else:
            print("Invalid choice! Please select 0-8")

if __name__ == "__main__":
    # If run with argument, run that example directly
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        
        if example_num == '1':
            example_1_simple_scan()
        elif example_num == '2':
            example_2_sector_scan()
        elif example_num == '3':
            example_3_continuous_watch()
        elif example_num == '4':
            example_4_export_signals()
        elif example_num == '5':
            example_5_sector_analysis()
        elif example_num == '6':
            example_6_index_scan()
        elif example_num == '7':
            example_7_high_volume_focus()
        elif example_num == '8':
            example_8_nifty50_scan()
        else:
            print("Invalid example number")
    else:
        # Run interactive menu
        main()

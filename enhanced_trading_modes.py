"""
Enhanced Multi-Asset Trading System with 3 Modes
=================================================

This advanced system provides three distinct trading modes:
1. 15-Min Scalping Mode - Fixed 15m timeframe for quick scalp trades
2. Instant Entry Mode - Immediate BUY/SELL signals with selected timeframe
3. Entry Setup Mode - High-probability trigger levels for pending orders

Supported Assets: EUR/USD, GBP/USD, Gold, Bitcoin
"""

from twelve_data_fetcher import download_gold_data, save_data_to_csv, initialize_twelve_data
from ict_ai_enhanced_analyzer import EnhancedICTAnalyzer
from pine_ict_analyzer import PineICTAnalyzer
from google_gemini_integration import GoogleGeminiAPI
from realtime_price_fetcher import RealTimePriceFetcher
import pandas as pd
import numpy as np
from datetime import datetime
import os
import atexit
import signal
import sys
from dotenv import load_dotenv
from enhanced_trading_system import EnhancedTradingSystem

def main():
    """Main execution function with Twelve Data API integration"""
    # Load environment variables
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    twelve_data_key = os.getenv("TWELVE_DATA_API_KEY")
    if not GEMINI_API_KEY or not twelve_data_key:
        print("❌ Missing API keys. Please set GEMINI_API_KEY and TWELVE_DATA_API_KEY in your .env file.")
        return
    
    print("🚀 ENHANCED ICT TRADING SYSTEM")
    print("=" * 30)
    print("Professional trading with Twelve Data API")
    print("Real-time forex • crypto • commodities")
    print()
    
    print("🔑 Using configured Twelve Data API key")
    
    print("📡 Initializing Twelve Data API...")
    
    try:
        # Initialize Twelve Data API
        if not initialize_twelve_data(twelve_data_key):
            print("❌ Failed to initialize Twelve Data API")
            print("💡 Please check your API key and try again")
            return
        
        # Create enhanced trading system
        trading_system = EnhancedTradingSystem(GEMINI_API_KEY)
        
        # Set up real-time price fetcher with Twelve Data
        print("🔧 Configuring real-time price fetching...")
        
        # Run the trading system
        signal = trading_system.run_trading_system()
        
        # Print the signal
        trading_system.print_signal(signal)
        
        # Save signal to file for logging
        if signal:
            log_file = f"trading_signals_{datetime.now().strftime('%Y%m%d')}.csv"
            signal_df = pd.DataFrame([signal])
            
            if os.path.exists(log_file):
                signal_df.to_csv(log_file, mode='a', header=False, index=False)
            else:
                signal_df.to_csv(log_file, index=False)
            
            print(f"📝 Signal logged to: {log_file}")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Trading system stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Try running the system again with a valid Twelve Data API key")

if __name__ == "__main__":
    main()

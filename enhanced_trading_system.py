import pandas as pd
import numpy as np
from datetime import datetime
import os
import atexit
import signal
import sys
from twelve_data_fetcher import download_gold_data, save_data_to_csv, initialize_twelve_data
from ict_ai_enhanced_analyzer import EnhancedICTAnalyzer
from pine_ict_analyzer import PineICTAnalyzer
from google_gemini_integration import GoogleGeminiAPI
from realtime_price_fetcher import RealTimePriceFetcher

# Paste the entire EnhancedTradingSystem class definition here, as it was in enhanced_trading_modes.py
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

class EnhancedTradingSystem:
    """
    Enhanced trading system with three distinct modes
    """
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.analyzer = EnhancedICTAnalyzer(api_key)
        self.pine_analyzer = PineICTAnalyzer()
        self.current_price = None
        self.atr_value = None
        self.selected_asset = None
        self.selected_timeframe = None
        self.selected_mode = None
        self.asset_config = self._get_asset_config()
        self.timeframe_config = self._get_timeframe_config()
        self.mode_config = self._get_mode_config()
        
        # Track created files for cleanup
        self.created_files = []
        
        # Register cleanup functions
        atexit.register(self._cleanup_files)
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _get_asset_config(self):
        """Asset configuration for different instruments"""
        return {
            '1': {
                'name': 'EUR/USD',
                'symbol': 'EUR/USD',
                'display_name': 'EURUSD',
                'price_decimals': 5,
                'pip_value': 0.0001,
                'pip_buffer': 5
            },
            '2': {
                'name': 'GBP/USD',
                'symbol': 'GBP/USD', 
                'display_name': 'GBPUSD',
                'price_decimals': 5,
                'pip_value': 0.0001,
                'pip_buffer': 5
            },
            '3': {
                'name': 'Gold (XAUUSD)',
                'symbol': 'XAU/USD',
                'display_name': 'XAUUSD',
                'price_decimals': 2,
                'pip_value': 0.10,
                'pip_buffer': 5
            },
            '4': {
                'name': 'Bitcoin',
                'symbol': 'BTC/USD',
                'display_name': 'BITCOIN',
                'price_decimals': 2,
                'pip_value': 1.00,
                'pip_buffer': 5
            }
        }
    
    def _get_timeframe_config(self):
        """Timeframe configuration for different intervals"""
        return {
            '1': {
                'name': '1 Minute',
                'interval': '1m',
                'display_name': '1MIN',
                'data_period_days': 7
            },
            '2': {
                'name': '5 Minutes',
                'interval': '5m',
                'display_name': '5MIN',
                'data_period_days': 14
            },
            '3': {
                'name': '15 Minutes',
                'interval': '15m',
                'display_name': '15MIN',
                'data_period_days': 30
            },
            '4': {
                'name': 'Multiple Timeframes',
                'type': 'multi',
                'display_name': 'MULTI-TF',
                'timeframes': [
                    {
                        'interval': '1d',
                        'name': 'Daily',
                        'purpose': 'Liquidity & Key Levels',
                        'data_period_days': 90  # 3 months for daily
                    },
                    {
                        'interval': '4h',
                        'name': '4 Hour',
                        'purpose': 'Main Analysis',
                        'data_period_days': 60
                    },
                    {
                        'interval': '1h',
                        'name': '1 Hour',
                        'purpose': 'Trend Confirmation',
                        'data_period_days': 30
                    },
                    {
                        'interval': '15m',
                        'name': '15 Minutes',
                        'purpose': 'Entry Zone',
                        'data_period_days': 14
                    },
                    {
                        'interval': '5m',
                        'name': '5 Minutes',
                        'purpose': 'Fine-tuning Entry',
                        'data_period_days': 7
                    }
                ]
            }
        }
    
    def _get_mode_config(self):
        """Trading mode configuration"""
        return {
            '1': {
                'name': '15-Min Scalping Mode',
                'type': 'scalping',
                'timeframe_fixed': '15m',
                'tp_atr_multiple': 1.5,  # Tighter TP for scalping
                'sl_atr_multiple': 1.0,  # Tighter SL for scalping
                'description': 'Quick scalp trades on 15-minute charts'
            },
            '2': {
                'name': 'Instant Entry Mode',
                'type': 'instant',
                'timeframe_fixed': None,  # User selects
                'tp_atr_multiple': 2.5,
                'sl_atr_multiple': 1.2,
                'description': 'Immediate BUY/SELL signals'
            },
            '3': {
                'name': 'Entry Setup Mode',
                'type': 'setup',
                'timeframe_fixed': None,  # User selects
                'tp_atr_multiple': 2.5,
                'sl_atr_multiple': 1.2,
                'confluence_threshold': 2.0,  # High probability threshold
                'description': 'High-probability trigger levels for pending orders'
            }
        }
    
    def select_mode(self):
        """Interactive mode selection"""
        print("🎯 ENHANCED TRADING SYSTEM")
        print("=" * 35)
        print("Select your trading mode:")
        print()
        
        for key, config in self.mode_config.items():
            print(f"{key}. {config['name']}")
            print(f"   {config['description']}")
            print()
        
        while True:
            try:
                choice = input("Enter your choice (1-3): ").strip()
                if choice in self.mode_config:
                    self.selected_mode = self.mode_config[choice]
                    print(f"✓ Selected: {self.selected_mode['name']}")
                    print()
                    return True
                else:
                    print("❌ Invalid choice. Please enter 1, 2, or 3.")
            except KeyboardInterrupt:
                print("\n\n⏹️ Selection cancelled by user")
                return False
    
    def select_asset(self):
        """Interactive asset selection"""
        print("📊 SELECT ASSET")
        print("=" * 20)
        print("Choose the asset to analyze:")
        print()
        
        for key, config in self.asset_config.items():
            print(f"{key}. {config['name']} ({config['symbol']})")
        
        print()
        while True:
            try:
                choice = input("Enter your choice (1-4): ").strip()
                if choice in self.asset_config:
                    self.selected_asset = self.asset_config[choice]
                    print(f"✓ Selected: {self.selected_asset['name']}")
                    print()
                    return True
                else:
                    print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
            except KeyboardInterrupt:
                print("\n\n⏹️ Selection cancelled by user")
                return False
    
    def select_timeframe(self):
        """Interactive timeframe selection (if not fixed by mode)"""
        if self.selected_mode['timeframe_fixed']:
            # Mode has fixed timeframe (e.g., scalping mode uses 15m)
            fixed_tf = self.selected_mode['timeframe_fixed']
            for key, config in self.timeframe_config.items():
                if config['interval'] == fixed_tf:
                    self.selected_timeframe = config
                    print(f"⏰ Timeframe: {config['name']} (Fixed for {self.selected_mode['name']})")
                    print()
                    return True
        else:
            # User selects timeframe
            print("⏰ SELECT TIMEFRAME")
            print("=" * 25)
            print("Choose the timeframe for analysis:")
            print()
            
            for key, config in self.timeframe_config.items():
                if key == '4':
                    print(f"{key}. {config['name']} (Top-down Analysis)")
                    print("   Daily → 4H → 1H → 15M → 5M")
                else:
                    print(f"{key}. {config['name']} ({config['interval']})")
            
            print()
            while True:
                try:
                    choice = input("Enter your choice (1-4): ").strip()
                    if choice in self.timeframe_config:
                        self.selected_timeframe = self.timeframe_config[choice]
                        if choice == '4':
                            print("\n📊 Multi-Timeframe Analysis Selected")
                            print("  • Daily: Liquidity & Key Levels")
                            print("  • 4H: Market Structure Analysis")
                            print("  • 1H: Trend Confirmation")
                            print("  • 15M: Entry Zone Identification")
                            print("  • 5M: Fine-tuning Entry Points")
                        else:
                            print(f"✓ Selected: {self.selected_timeframe['name']}")
                        print()
                        return True
                    else:
                        print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                except KeyboardInterrupt:
                    print("\n\n⏹️ Selection cancelled by user")
                    return False
    
    def download_fresh_data(self):
        """Download latest data for selected asset and timeframe"""
        asset_name = self.selected_asset['name']
        timeframe_name = self.selected_timeframe['name']
        
        if self.selected_timeframe.get('type') == 'multi':
            # Multi-timeframe mode
            print(f"📥 Downloading {asset_name} data for multiple timeframes...")
            success = True
            
            for tf in self.selected_timeframe['timeframes']:
                interval = tf['interval']
                days = tf['data_period_days']
                months = max(1, days // 30)
                
                print(f"\n⏳ {tf['name']} ({tf['purpose']})...")
                filename = f"{self.selected_asset['display_name'].lower()}_{interval}_data.csv"
                
                data = download_gold_data(
                    symbol=self.selected_asset['symbol'],
                    months=months,
                    interval=interval
                )
                
                if data is not None:
                    save_data_to_csv(data, filename=filename)
                    print(f"✓ {len(data)} candles downloaded")
                    
                    # Track created file for cleanup
                    self.created_files.append(filename)
                    
                    # Store file path in timeframe config for later use
                    tf['data_file'] = filename
                else:
                    print(f"❌ Failed to download {tf['name']} data")
                    success = False
                    break
            
            if success:
                print("\n✅ Multi-timeframe data download complete")
                # Use the lowest timeframe (5m) as the primary data file
                self.selected_asset['data_file'] = self.selected_timeframe['timeframes'][-1]['data_file']
                return True
            else:
                return False
        else:
            # Single timeframe mode
            interval = self.selected_timeframe['interval']
            days = self.selected_timeframe['data_period_days']
            
            print(f"📥 Downloading fresh {asset_name} data ({timeframe_name})...")
            
            # Calculate months based on days (minimum 1 month)
            months = max(1, days // 30)
            
            # Dynamic filename based on asset and timeframe
            filename = f"{self.selected_asset['display_name'].lower()}_{interval}_data.csv"
            
            data = download_gold_data(
                symbol=self.selected_asset['symbol'],
                months=months,
                interval=interval
            )
            
            if data is not None:
                save_data_to_csv(data, filename=filename)
                print(f"✓ Fresh {timeframe_name} data saved: {len(data)} candles")
                
                # Track created file for cleanup
                self.created_files.append(filename)
                
                # Update the data file path for loading
                self.selected_asset['data_file'] = filename
                return True
            else:
                print("❌ Failed to download data")
                return False
    
    def analyze_market(self):
        """Analyze market and calculate current conditions using Pine Script ICT"""
        if self.selected_timeframe.get('type') == 'multi':
            return self._analyze_multi_timeframe()
            
        print("🔍 Analyzing market conditions with Pine Script ICT...")
        
        try:
            # Load data and remove any duplicate columns
            data = pd.read_csv(self.selected_asset['data_file'])
            data.columns = data.columns.str.lower()  # Ensure lowercase columns
            data = data.loc[:,~data.columns.duplicated()]  # Remove duplicate columns
            
            print(f"✓ Loaded data shape: {data.shape}")
            print(f"✓ Columns: {list(data.columns)}")
            
            # Load the fresh data into both analyzers
            self.analyzer.load_data(file_path=self.selected_asset['data_file'])
            self.analyzer.calculate_indicators()
            
            # Parse datetime if needed
            if 'datetime' in data.columns:
                data['datetime'] = pd.to_datetime(data['datetime'])
                data.set_index('datetime', inplace=True)
            
            # Load cleaned data into Pine Script analyzer
            self.pine_analyzer.load_data(data)
            self.pine_analyzer.calculate_all_indicators()
            
            # Get historical price and ATR from Pine analyzer
            historical_price = self.pine_analyzer.data['close'].iloc[-1]
            self.atr_value = self.pine_analyzer.data['atr'].iloc[-1]
            
            # Get real-time current price
            asset_name = self.selected_asset['name']
            print(f"💰 Fetching real-time {asset_name} price...")
            
            price_fetcher = RealTimePriceFetcher(symbol=self.selected_asset['symbol'])
            price_data = price_fetcher.get_price_with_validation(historical_price)
            
            if price_data['success']:
                self.current_price = price_data['price']
                decimals = self.selected_asset['price_decimals']
                print(f"✓ Real-time price: ${self.current_price:.{decimals}f} ({price_data['source']})")
            else:
                self.current_price = historical_price
                decimals = self.selected_asset['price_decimals']
                print(f"⚠️ Using historical price: ${self.current_price:.{decimals}f}")
            
            # Get Pine Script analysis summary
            pine_summary = self.pine_analyzer.get_analysis_summary()
            pine_signals = self.pine_analyzer.get_latest_signals()
            
            print(f"✓ Pine Script analysis complete:")
            print(f"  • Order Blocks: {pine_summary['bullish_obs']} Bull, {pine_summary['bearish_obs']} Bear")
            print(f"  • Active FVGs: {pine_summary['active_fvg_up']} Up, {pine_summary['active_fvg_down']} Down")
            print(f"  • Market Structure: {pine_summary['current_structure']}")
            print(f"  • ATR: ${self.atr_value:.{decimals}f}")
            
            return True
        except Exception as e:
            print(f"❌ Error during market analysis: {str(e)}")
            return False
    
    def generate_signal(self):
        """Generate signal based on selected mode"""
        # Handle multi-timeframe analysis if selected
        if self.selected_timeframe.get('type') == 'multi':
            return self._generate_multi_timeframe_signal()
            
        if self.selected_mode['type'] == 'scalping':
            return self._generate_scalping_signal()
        elif self.selected_mode['type'] == 'instant':
            return self._generate_instant_signal()
        elif self.selected_mode['type'] == 'setup':
            return self._generate_setup_signal()
    
    def _generate_multi_timeframe_signal(self):
        """Generate comprehensive signal using multi-timeframe analysis"""
        analysis = self.selected_timeframe['analysis']
        asset_name = self.selected_asset['name']
        decimals = self.selected_asset['price_decimals']
        
        print("\n🔄 GENERATING MULTI-TIMEFRAME SIGNAL")
        print("=" * 40)
        
        # Get analysis from each timeframe
        daily = analysis['1d']
        h4 = analysis['4h']
        h1 = analysis['1h']
        m15 = analysis['15m']
        m5 = analysis['5m']
        
        # Compile multi-timeframe signal prompt
        signal_prompt = f"""
{asset_name.upper()} MULTI-TIMEFRAME ICT ANALYSIS

Current Price: ${self.current_price:.{decimals}f}
ATR (15M): ${self.atr_value:.{decimals}f}

DAILY TIMEFRAME (Liquidity Analysis):
- Market Bias: {daily['signals'].get('market_bias', 'Neutral')}
- Day High/Low: H={daily['summary'].get('day_high', 'N/A')} / L={daily['summary'].get('day_low', 'N/A')}
- Liquidity Levels Above: {daily['signals'].get('liquidity_levels_above', [])}
- Liquidity Levels Below: {daily['signals'].get('liquidity_levels_below', [])}
- Recent Liquidity Sweeps: High={daily['signals'].get('recent_high_sweep', False)}, Low={daily['signals'].get('recent_low_sweep', False)}

4 HOUR TIMEFRAME (Structure Analysis):
- Market Structure: {h4['summary'].get('current_structure', 'N/A')} (1=Bull, -1=Bear, 0=Neutral)
- Order Blocks: {h4['summary'].get('bullish_obs', 0)} Bull, {h4['summary'].get('bearish_obs', 0)} Bear
- Key Support Levels: {h4['signals'].get('support_levels', [])}
- Key Resistance Levels: {h4['signals'].get('resistance_levels', [])}
- Most Recent FVG: {h4['signals'].get('recent_fvg', 'None')}

1 HOUR TIMEFRAME (Trend Analysis):
- Trend Direction: {h1['signals'].get('trend_direction', 'N/A')}
- Momentum State: {h1['signals'].get('momentum', 'N/A')}
- Active FVGs Up: {h1['summary'].get('active_fvg_up', 0)}
  Levels: {h1['signals'].get('fvg_up_levels', [])}
- Active FVGs Down: {h1['summary'].get('active_fvg_down', 0)}
  Levels: {h1['signals'].get('fvg_down_levels', [])}

15 MINUTE TIMEFRAME (Entry Zone):
- Entry Zones: {m15['signals'].get('entry_zones', [])}
- Stop Levels: {m15['signals'].get('stop_levels', [])}
- Price Action: {m15['signals'].get('price_action', 'N/A')}
- Recent FVG Fills: {m15['signals'].get('recent_fvg_fills', [])}

5 MINUTE TIMEFRAME (Fine Entry):
- Entry Points: {m5['signals'].get('entry_points', [])}
- Recent Wicks: High={m5['signals'].get('recent_high_wick', 'N/A')}, Low={m5['signals'].get('recent_low_wick', 'N/A')}
- Short-term Bias: {m5['signals'].get('short_term_bias', 'N/A')}
- Volume Profile: {m5['signals'].get('volume_profile', 'N/A')}

ADVANCED ICT ENTRY CONDITIONS:
1. Liquidity Sweep Entries:
   - Enter after confirmed sweep of key liquidity level
   - Use nearest untapped FVG as target
   - Place stops beyond swept level

2. FVG-based Entries:
   - Enter when price reaches untapped FVG
   - Stop loss behind FVG formation candle
   - Target: Next significant FVG or OB

3. Order Block Entries:
   - Enter at first retest of fresh OB
   - Stop behind OB formation
   - Target nearest opposing FVG

4. Market Structure Entries:
   - Enter after structure break and retest
   - Stop behind last structure point
   - Target: Next key structure level

RESPOND WITH ONE OF THESE DETAILED FORMATS:

FOR LIQUIDITY SWEEP ENTRY:
BUY AFTER SWEEP OF [LIQ_LEVEL] ≥ [ENTRY] TP:[TAKE_PROFIT] SL:[STOP_LOSS]
• Sweep Confirmation: [Describe required sweep pattern]
• Entry Timing: [Specify exact entry conditions]
• Stop Loss Logic: [Explain stop placement]
• Target Selection: [Explain TP level choice]
• Risk Management: [Position sizing based on ATR]

OR

SELL AFTER SWEEP OF [LIQ_LEVEL] ≤ [ENTRY] TP:[TAKE_PROFIT] SL:[STOP_LOSS]
[Same bullet points as above]

FOR FVG ENTRY:
BUY AT FVG [FVG_LEVEL] ≥ [ENTRY] TP:[TAKE_PROFIT] SL:[STOP_LOSS]
• FVG Validation: [Describe FVG quality]
• Entry Timing: [Specify exact entry conditions]
• Stop Loss Logic: [Explain stop placement]
• Target Selection: [Explain TP level choice]
• Risk Management: [Position sizing based on ATR]

OR

SELL AT FVG [FVG_LEVEL] ≤ [ENTRY] TP:[TAKE_PROFIT] SL:[STOP_LOSS]
[Same bullet points as above]

OR

WAIT - [SPECIFIC REASON AND NEXT SETUP TO WATCH FOR]

MULTI-TF CONFLUENCE:
• Daily Bias: [Explain how setup aligns with daily liquidity]
• 4H Structure: [Explain structure support for setup]
• 1H Trend: [Explain trend alignment]
• 15M Setup: [Detail entry zone formation]
• 5M Trigger: [Specify exact entry trigger]

Generate precise ICT setup with specific entry conditions and management rules.
"""
        
        try:
            ai_signal = self.analyzer.gemini_api.send_prompt(signal_prompt)
            signal = self._parse_signal(ai_signal, mode_type='multi')
            signal['multi_tf_data'] = {
                'daily': daily['summary'],
                '4h': h4['summary'],
                '1h': h1['summary'],
                '15m': m15['summary'],
                '5m': m5['summary']
            }
            return signal
        except Exception as e:
            print(f"❌ Error generating multi-timeframe signal: {str(e)}")
            return self._fallback_multi_timeframe_signal(analysis)
    
    def _fallback_multi_timeframe_signal(self, analysis):
        """Generate fallback signal using multi-timeframe analysis"""
        signal = {
            'timestamp': datetime.now(),
            'current_price': self.current_price,
            'action': None,  # Will be set based on analysis
            'entry': self.current_price,
            'tp': None,
            'sl': None,
            'confidence': 'Multi-TF ICT',
            'raw_signal': 'Multi-timeframe fallback analysis',
            'asset': self.selected_asset['name'],
            'mode': 'multi'
        }
        
        # Check daily bias
        daily_bias = analysis['1d']['signals'].get('market_bias', 'neutral')
        
        # Check 4H structure
        h4_structure = analysis['4h']['summary'].get('current_structure', 0)
        
        # Check 4H levels
        h4_support = analysis['4h']['signals'].get('support_levels', [])
        h4_resistance = analysis['4h']['signals'].get('resistance_levels', [])
        
        # Check 1H trend and momentum
        h1_trend = analysis['1h']['signals'].get('trend_direction', 'neutral')
        h1_momentum = analysis['1h']['signals'].get('momentum', 'neutral')
        
        # Check 15M entry zones
        m15_entry_zones = analysis['15m']['signals'].get('entry_zones', [])
        
        # Calculate confluence
        long_confluence = 0
        short_confluence = 0
        
        # Daily bias confluence
        if daily_bias.lower() == 'bullish':
            long_confluence += 1
        elif daily_bias.lower() == 'bearish':
            short_confluence += 1
        
        # 4H structure confluence
        if h4_structure == 1:
            long_confluence += 1
        elif h4_structure == -1:
            short_confluence += 1
        
        # 1H trend confluence
        if h1_trend.lower() == 'bullish':
            long_confluence += 1
        elif h1_trend.lower() == 'bearish':
            short_confluence += 1
            
        # 1H momentum confluence
        if h1_momentum.lower() == 'bullish':
            long_confluence += 0.5
        elif h1_momentum.lower() == 'bearish':
            short_confluence += 0.5
        
        # Determine nearest support and resistance
        support_levels = sorted([level for level in h4_support if level < self.current_price])
        resistance_levels = sorted([level for level in h4_resistance if level > self.current_price])
        
        nearest_support = support_levels[-1] if support_levels else self.current_price - self.atr_value * 2
        nearest_resistance = resistance_levels[0] if resistance_levels else self.current_price + self.atr_value * 2
        
        # Always generate a setup based on strongest bias
        if long_confluence >= short_confluence:
            # Bullish setup
            signal['action'] = 'BUY_SETUP'
            
            # Entry near support with confirmation
            entry_price = nearest_support + (self.atr_value * 0.2)  # Small buffer above support
            signal['entry'] = round(entry_price, self.selected_asset['price_decimals'])
            
            # Stop below support
            sl_price = nearest_support - (self.atr_value * 1.0)
            signal['sl'] = round(sl_price, self.selected_asset['price_decimals'])
            
            # Target at resistance or ATR-based
            if resistance_levels:
                tp_price = nearest_resistance
            else:
                tp_price = entry_price + (self.atr_value * 2.5)
            signal['tp'] = round(tp_price, self.selected_asset['price_decimals'])
            
            signal['raw_signal'] = (
                f"BUY SETUP - Bullish bias (Confluence: {long_confluence:.1f}) "
                f"• Entry above support @ {signal['entry']} "
                f"• Daily={daily_bias}, 4H={h4_structure}, 1H={h1_trend}"
            )
        else:
            # Bearish setup
            signal['action'] = 'SELL_SETUP'
            
            # Entry near resistance with confirmation
            entry_price = nearest_resistance - (self.atr_value * 0.2)  # Small buffer below resistance
            signal['entry'] = round(entry_price, self.selected_asset['price_decimals'])
            
            # Stop above resistance
            sl_price = nearest_resistance + (self.atr_value * 1.0)
            signal['sl'] = round(sl_price, self.selected_asset['price_decimals'])
            
            # Target at support or ATR-based
            if support_levels:
                tp_price = nearest_support
            else:
                tp_price = entry_price - (self.atr_value * 2.5)
            signal['tp'] = round(tp_price, self.selected_asset['price_decimals'])
            
            signal['raw_signal'] = (
                f"SELL SETUP - Bearish bias (Confluence: {short_confluence:.1f}) "
                f"• Entry below resistance @ {signal['entry']} "
                f"• Daily={daily_bias}, 4H={h4_structure}, 1H={h1_trend}"
            )
        
        # Add entry zone validation from 15M timeframe
        if m15_entry_zones:
            signal['raw_signal'] += f"\n• Validate with 15M entry zones: {m15_entry_zones}"
        
        return signal
    
    def _generate_scalping_signal(self):
        """Generate scalping signal with tighter parameters using Pine Script data"""
        # Get Pine Script analysis
        pine_summary = self.pine_analyzer.get_analysis_summary()
        pine_signals = self.pine_analyzer.get_latest_signals(lookback=5)
        recent_candles = self.pine_analyzer.data.tail(5)
        
        # Calculate simple confluence based on Pine Script indicators
        long_signals = 0
        short_signals = 0
        
        if pine_signals['recent_ob_bull']:
            long_signals += 1
        if pine_signals['recent_ob_bear']:
            short_signals += 1
        if pine_signals['recent_fvg_up']:
            long_signals += 1
        if pine_signals['recent_fvg_down']:
            short_signals += 1
        if pine_summary['current_structure'] == 1:
            long_signals += 1
        elif pine_summary['current_structure'] == -1:
            short_signals += 1
        if pine_signals['displacement_bias'] == 'bullish':
            long_signals += 1
        elif pine_signals['displacement_bias'] == 'bearish':
            short_signals += 1
        
        # Scalping-specific AI prompt with Pine Script data
        asset_name = self.selected_asset['name']
        decimals = self.selected_asset['price_decimals']
        
        signal_prompt = f"""
{asset_name.upper()} 15-MINUTE SCALPING SIGNAL (Pine Script ICT)

Current Price: ${self.current_price:.{decimals}f}
ATR: ${self.atr_value:.{decimals}f}
Mode: SCALPING (Quick In/Out)

Pine Script ICT Data (Last 5 candles):
- Bullish Signals: {long_signals} (OB: {pine_signals['recent_ob_bull']}, FVG: {pine_signals['recent_fvg_up']})
- Bearish Signals: {short_signals} (OB: {pine_signals['recent_ob_bear']}, FVG: {pine_signals['recent_fvg_down']})
- Market Structure: {pine_summary['current_structure']} (1=Bull, -1=Bear, 0=Neutral)
- Displacement Bias: {pine_signals['displacement_bias']}
- Recent Liq Sweeps: Up={pine_signals['recent_liq_sweep_up']}, Down={pine_signals['recent_liq_sweep_down']}

SCALPING CRITERIA:
- Look for immediate momentum
- Prefer quick 1.5x ATR targets
- Tight 1.0x ATR stops

RESPOND WITH THIS FORMAT:
BUY [ENTRY] TP:[TAKE_PROFIT] SL:[STOP_LOSS] - [BRIEF_REASON]
OR
SELL [ENTRY] TP:[TAKE_PROFIT] SL:[STOP_LOSS] - [BRIEF_REASON]
OR
WAIT - [BRIEF_REASON]

Focus on immediate scalping opportunities with Pine Script ICT confirmation.
"""
        
        try:
            ai_signal = self.analyzer.gemini_api.send_prompt(signal_prompt)
            return self._parse_signal(ai_signal, mode_type='scalping')
        except Exception as e:
            return self._fallback_pine_signal(long_signals, short_signals, mode_type='scalping')
    
    def _generate_instant_signal(self):
        """Generate instant entry signal"""
        # Get ICT analysis summary
        summary = self.analyzer.get_analysis_summary()
        latest_candle = self.analyzer.data.iloc[-1]
        recent_candles = self.analyzer.data.tail(10)
        
        # Check recent confluence scores
        avg_long_confluence = recent_candles['confluence_long'].mean()
        avg_short_confluence = recent_candles['confluence_short'].mean()
        
        # Check for recent ICT patterns
        recent_bullish_ob = recent_candles['bullish_ob'].sum()
        recent_bearish_ob = recent_candles['bearish_ob'].sum()
        recent_long_liq = recent_candles['liquidity_grab_long'].sum()
        recent_short_liq = recent_candles['liquidity_grab_short'].sum()
        
        # Market structure bias
        market_structure = latest_candle['market_structure']
        
        # Instant entry AI prompt
        asset_name = self.selected_asset['name']
        decimals = self.selected_asset['price_decimals']
        
        signal_prompt = f"""
{asset_name.upper()} INSTANT ENTRY SIGNAL

Current Price: ${self.current_price:.{decimals}f}
ATR: ${self.atr_value:.{decimals}f}
Mode: INSTANT ENTRY

Recent ICT Data:
- Long Confluence Avg: {avg_long_confluence:.1f}
- Short Confluence Avg: {avg_short_confluence:.1f}
- Recent Bullish OB: {recent_bullish_ob}
- Recent Bearish OB: {recent_bearish_ob}
- Long Liquidity Grabs: {recent_long_liq}
- Short Liquidity Grabs: {recent_short_liq}
- Market Structure: {market_structure}

RESPOND WITH THIS FORMAT:
BUY [ENTRY] TP:[TAKE_PROFIT] SL:[STOP_LOSS] - [BRIEF_REASON]
OR
SELL [ENTRY] TP:[TAKE_PROFIT] SL:[STOP_LOSS] - [BRIEF_REASON]
OR
WAIT - [BRIEF_REASON]

Provide immediate entry recommendation.
"""
        
        try:
            ai_signal = self.analyzer.gemini_api.send_prompt(signal_prompt)
            return self._parse_signal(ai_signal, mode_type='instant')
        except Exception as e:
            return self._fallback_signal(avg_long_confluence, avg_short_confluence, mode_type='instant')
    
    def _generate_setup_signal(self):
        """Generate swing-based setup with comprehensive ICT analysis"""
        # Get Pine Script analysis data
        pine_summary = self.pine_analyzer.get_analysis_summary()
        pine_signals = self.pine_analyzer.get_latest_signals(lookback=20)
        recent_data = self.pine_analyzer.data.tail(50)  # More data for swing analysis
        
        # Find recent swing levels
        swing_highs = self._find_recent_swings(recent_data, 'high')
        swing_lows = self._find_recent_swings(recent_data, 'low')
        
        # Get active Order Blocks and FVGs
        active_obs = self._get_active_ict_levels()
        
        # Calculate setup levels and confluence
        setup_data = self._calculate_setup_levels(swing_highs, swing_lows, active_obs)
        
        # Generate comprehensive ICT-based setup
        asset_name = self.selected_asset['name']
        decimals = self.selected_asset['price_decimals']
        pip_buffer = self.selected_asset['pip_buffer']
        
        signal_prompt = f"""
{asset_name.upper()} SWING TRADING SETUP (Pine Script ICT Analysis)

Current Price: ${self.current_price:.{decimals}f}
ATR: ${self.atr_value:.{decimals}f}
Mode: ENTRY SETUP (Swing Trading Focus)

Pine Script ICT Analysis:
- Market Structure: {pine_summary['current_structure']} (1=Bull, -1=Bear, 0=Neutral)
- Total Order Blocks: {pine_summary['bullish_obs']} Bull, {pine_summary['bearish_obs']} Bear
- Active FVGs: {pine_summary['active_fvg_up']} Up, {pine_summary['active_fvg_down']} Down
- Displacement Bias: {pine_signals['displacement_bias']}
- Recent Liquidity Sweeps: Up={pine_signals['recent_liq_sweep_up']}, Down={pine_signals['recent_liq_sweep_down']}

Swing Analysis:
- Nearest Swing High: ${setup_data['swing_high']:.{decimals}f} (resistance)
- Nearest Swing Low: ${setup_data['swing_low']:.{decimals}f} (support)
- Price Position: {setup_data['price_position']}

ICT Confluence Factors:
{setup_data['confluence_text']}

SETUP CRITERIA:
- Generate swing-based entry setups using Pine Script ICT data
- Include {pip_buffer}-pip buffer from key levels
- Provide detailed ICT explanation for educational value
- Focus on practical swing trading opportunities

RESPOND WITH THIS FORMAT:
BUY WHEN ≥ [TRIGGER_PRICE] TP:[TAKE_PROFIT] SL:[STOP_LOSS] - [SHORT_REASON]

DETAILED_ICT_EXPLANATION:
• Market Structure: [Explain current bias and why it supports the trade]
• Entry Logic: [Why this specific level is significant]
• ICT Theory: [How this fits institutional trading models]
• Confluence: [List 2-3 supporting factors]
• Risk Management: [Stop and target justification]

OR

SELL WHEN ≤ [TRIGGER_PRICE] TP:[TAKE_PROFIT] SL:[STOP_LOSS] - [SHORT_REASON]

DETAILED_ICT_EXPLANATION:
• Market Structure: [Explain current bias and why it supports the trade]
• Entry Logic: [Why this specific level is significant]
• ICT Theory: [How this fits institutional trading models]
• Confluence: [List 2-3 supporting factors]
• Risk Management: [Stop and target justification]

Generate practical swing setups with comprehensive ICT education.
"""
        
        try:
            ai_signal = self.analyzer.gemini_api.send_prompt(signal_prompt)
            return self._parse_setup_signal_with_explanation(ai_signal)
        except Exception as e:
            return self._fallback_swing_setup(setup_data)
    
    def _parse_signal(self, ai_response, mode_type):
        """Parse AI response into structured signal"""
        signal = {
            'timestamp': datetime.now(),
            'current_price': self.current_price,
            'action': 'WAIT',
            'entry': None,
            'tp': None,
            'sl': None,
            'confidence': 'AI',
            'raw_signal': ai_response.strip(),
            'asset': self.selected_asset['name'],
            'mode': mode_type
        }
        
        response = ai_response.upper().strip()
        
        if mode_type == 'setup':
            # Parse setup triggers
            if 'BUY WHEN' in response:
                signal['action'] = 'BUY_SETUP'
                signal.update(self._extract_levels(response, 'BUY', mode_type))
            elif 'SELL WHEN' in response:
                signal['action'] = 'SELL_SETUP'
                signal.update(self._extract_levels(response, 'SELL', mode_type))
        else:
            # Parse instant/scalping signals
            if 'BUY' in response:
                signal['action'] = 'BUY'
                signal.update(self._extract_levels(response, 'BUY', mode_type))
            elif 'SELL' in response:
                signal['action'] = 'SELL'
                signal.update(self._extract_levels(response, 'SELL', mode_type))
        
        return signal
    
    def _extract_levels(self, response, action, mode_type):
        """Extract price levels from AI response"""
        levels = {}
        decimals = self.selected_asset['price_decimals']
        
        try:
            # Extract numbers from response
            import re
            numbers = re.findall(r'\d+\.?\d*', response)
            
            if len(numbers) >= 3:
                levels['entry'] = round(float(numbers[0]), decimals)
                levels['tp'] = round(float(numbers[1]), decimals)
                levels['sl'] = round(float(numbers[2]), decimals)
            else:
                # Fallback to ATR-based calculation
                levels.update(self._calculate_atr_levels(action, mode_type))
                
        except:
            levels.update(self._calculate_atr_levels(action, mode_type))
        
        return levels
    
    def _calculate_atr_levels(self, action, mode_type):
        """Calculate TP/SL based on ATR and mode"""
        levels = {}
        decimals = self.selected_asset['price_decimals']
        
        # Get ATR multiples based on mode
        tp_multiple = self.selected_mode['tp_atr_multiple']
        sl_multiple = self.selected_mode['sl_atr_multiple']
        
        if action in ['BUY', 'BUY_SETUP']:
            levels['entry'] = round(self.current_price, decimals)
            levels['tp'] = round(self.current_price + (self.atr_value * tp_multiple), decimals)
            levels['sl'] = round(self.current_price - (self.atr_value * sl_multiple), decimals)
        else:  # SELL, SELL_SETUP
            levels['entry'] = round(self.current_price, decimals)
            levels['tp'] = round(self.current_price - (self.atr_value * tp_multiple), decimals)
            levels['sl'] = round(self.current_price + (self.atr_value * sl_multiple), decimals)
        
        return levels
    
    def _fallback_signal(self, long_conf, short_conf, mode_type):
        """Fallback signal generation if AI fails"""
        signal = {
            'timestamp': datetime.now(),
            'current_price': self.current_price,
            'action': 'WAIT',
            'entry': self.current_price,
            'tp': None,
            'sl': None,
            'confidence': 'ICT',
            'raw_signal': 'Fallback analysis',
            'asset': self.selected_asset['name'],
            'mode': mode_type
        }
        
        # Apply confluence threshold for setup mode
        if mode_type == 'setup':
            threshold = self.selected_mode['confluence_threshold']
            if max(long_conf, short_conf) < threshold:
                signal['reason'] = f'Low confluence (max: {max(long_conf, short_conf):.1f})'
                return signal
        
        # Simple confluence-based decision
        if long_conf > short_conf and long_conf >= 1.5:
            action = 'BUY_SETUP' if mode_type == 'setup' else 'BUY'
            signal['action'] = action
            signal.update(self._calculate_atr_levels('BUY', mode_type))
        elif short_conf > long_conf and short_conf >= 1.5:
            action = 'SELL_SETUP' if mode_type == 'setup' else 'SELL'
            signal['action'] = action
            signal.update(self._calculate_atr_levels('SELL', mode_type))
        
        return signal
    
    def _fallback_pine_signal(self, long_signals, short_signals, mode_type):
        """Fallback signal generation using Pine Script signals if AI fails"""
        signal = {
            'timestamp': datetime.now(),
            'current_price': self.current_price,
            'action': 'WAIT',
            'entry': self.current_price,
            'tp': None,
            'sl': None,
            'confidence': 'Pine Script ICT',
            'raw_signal': f'Pine Script fallback: Long={long_signals}, Short={short_signals}',
            'asset': self.selected_asset['name'],
            'mode': mode_type
        }
        
        # Apply confluence threshold for setup mode
        if mode_type == 'setup':
            threshold = 2  # Require at least 2 signals for setup mode
            if max(long_signals, short_signals) < threshold:
                signal['reason'] = f'Low Pine Script signals (max: {max(long_signals, short_signals)})'
                return signal
        
        # Simple Pine Script signal-based decision
        if long_signals > short_signals and long_signals >= 2:
            action = 'BUY_SETUP' if mode_type == 'setup' else 'BUY'
            signal['action'] = action
            signal.update(self._calculate_atr_levels('BUY', mode_type))
        elif short_signals > long_signals and short_signals >= 2:
            action = 'SELL_SETUP' if mode_type == 'setup' else 'SELL'
            signal['action'] = action
            signal.update(self._calculate_atr_levels('SELL', mode_type))
        
        return signal
    
    def _find_recent_swings(self, data, swing_type):
        """Find recent swing highs or lows from Pine Script data"""
        swings = []
        column_name = f'pivot_{swing_type.lower()}'
        
        if column_name in data.columns:
            swing_points = data[data[column_name] == True].tail(3)  # Last 3 swings
            for idx, row in swing_points.iterrows():
                swings.append({
                    'price': row[swing_type.lower()],
                    'index': idx,
                    'distance': abs(self.current_price - row[swing_type.lower()])
                })
        
        # Sort by distance from current price
        swings.sort(key=lambda x: x['distance'])
        return swings[:2]  # Return 2 nearest swings
    
    def _get_active_ict_levels(self):
        """Get active Order Blocks and FVGs from Pine Script data"""
        levels = {
            'bullish_obs': [],
            'bearish_obs': [],
            'fvg_up': [],
            'fvg_down': []
        }
        
        # Get recent Order Blocks
        for ob in self.pine_analyzer.bullish_obs[-3:]:  # Last 3 bullish OBs
            if not ob.breaker:  # Only active (unbroken) OBs
                levels['bullish_obs'].append({
                    'top': ob.top,
                    'btm': ob.btm,
                    'distance': min(abs(self.current_price - ob.top), abs(self.current_price - ob.btm))
                })
        
        for ob in self.pine_analyzer.bearish_obs[-3:]:  # Last 3 bearish OBs
            if not ob.breaker:  # Only active (unbroken) OBs
                levels['bearish_obs'].append({
                    'top': ob.top,
                    'btm': ob.btm,
                    'distance': min(abs(self.current_price - ob.top), abs(self.current_price - ob.btm))
                })
        
        # Get active FVGs
        for fvg in self.pine_analyzer.fvg_up[-3:]:  # Last 3 bullish FVGs
            if fvg.active:
                levels['fvg_up'].append({
                    'top': fvg.top,
                    'btm': fvg.btm,
                    'distance': min(abs(self.current_price - fvg.top), abs(self.current_price - fvg.btm))
                })
        
        for fvg in self.pine_analyzer.fvg_down[-3:]:  # Last 3 bearish FVGs
            if fvg.active:
                levels['fvg_down'].append({
                    'top': fvg.top,
                    'btm': fvg.btm,
                    'distance': min(abs(self.current_price - fvg.top), abs(self.current_price - fvg.btm))
                })
        
        return levels
    
    def _calculate_setup_levels(self, swing_highs, swing_lows, active_obs):
        """Calculate setup levels and confluence factors"""
        decimals = self.selected_asset['price_decimals']
        pip_buffer = self.selected_asset['pip_buffer'] * self.selected_asset['pip_value']
        
        # Get nearest swing levels
        swing_high = swing_highs[0]['price'] if swing_highs else self.current_price + self.atr_value
        swing_low = swing_lows[0]['price'] if swing_lows else self.current_price - self.atr_value
        
        # Determine price position
        if self.current_price > (swing_high + swing_low) / 2:
            price_position = "Upper range (near resistance)"
        elif self.current_price < (swing_high + swing_low) / 2:
            price_position = "Lower range (near support)"
        else:
            price_position = "Mid-range"
        
        # Build confluence text
        confluence_factors = []
        
        # Check proximity to Order Blocks
        for ob in active_obs['bullish_obs']:
            if abs(self.current_price - ob['btm']) < self.atr_value * 0.5:
                confluence_factors.append(f"Near Bullish OB support at ${ob['btm']:.{decimals}f}")
        
        for ob in active_obs['bearish_obs']:
            if abs(self.current_price - ob['top']) < self.atr_value * 0.5:
                confluence_factors.append(f"Near Bearish OB resistance at ${ob['top']:.{decimals}f}")
        
        # Check proximity to FVGs
        for fvg in active_obs['fvg_up']:
            if abs(self.current_price - fvg['btm']) < self.atr_value * 0.3:
                confluence_factors.append(f"Near Bullish FVG at ${fvg['btm']:.{decimals}f}")
        
        for fvg in active_obs['fvg_down']:
            if abs(self.current_price - fvg['top']) < self.atr_value * 0.3:
                confluence_factors.append(f"Near Bearish FVG at ${fvg['top']:.{decimals}f}")
        
        if not confluence_factors:
            confluence_factors.append("Price between key levels - monitor for breakout")
        
        confluence_text = "\n".join([f"- {factor}" for factor in confluence_factors])
        
        return {
            'swing_high': swing_high,
            'swing_low': swing_low,
            'price_position': price_position,
            'confluence_text': confluence_text,
            'confluence_count': len(confluence_factors)
        }
    
    def _parse_setup_signal_with_explanation(self, ai_response):
        """Parse setup signal with detailed ICT explanation"""
        signal = {
            'timestamp': datetime.now(),
            'current_price': self.current_price,
            'action': 'WAIT',
            'entry': None,
            'tp': None,
            'sl': None,
            'confidence': 'AI',
            'raw_signal': ai_response.strip(),
            'asset': self.selected_asset['name'],
            'mode': 'setup',
            'ict_explanation': None
        }
        
        response = ai_response.strip()
        
        # Split response into signal and explanation
        if 'DETAILED_ICT_EXPLANATION:' in response:
            parts = response.split('DETAILED_ICT_EXPLANATION:')
            signal_part = parts[0].strip()
            explanation_part = parts[1].strip() if len(parts) > 1 else ""
            signal['ict_explanation'] = explanation_part
        else:
            signal_part = response
        
        response_upper = signal_part.upper().strip()
        
        # Parse setup triggers
        if 'BUY WHEN' in response_upper:
            signal['action'] = 'BUY_SETUP'
            signal.update(self._extract_levels(signal_part, 'BUY', 'setup'))
        elif 'SELL WHEN' in response_upper:
            signal['action'] = 'SELL_SETUP'
            signal.update(self._extract_levels(signal_part, 'SELL', 'setup'))
        
        return signal
    
    def _fallback_swing_setup(self, setup_data):
        """Fallback swing setup generation using Pine Script data"""
        decimals = self.selected_asset['price_decimals']
        pip_buffer = self.selected_asset['pip_buffer'] * self.selected_asset['pip_value']
        
        signal = {
            'timestamp': datetime.now(),
            'current_price': self.current_price,
            'action': 'WAIT',
            'entry': self.current_price,
            'tp': None,
            'sl': None,
            'confidence': 'Pine Script ICT',
            'asset': self.selected_asset['name'],
            'mode': 'setup',
            'ict_explanation': None
        }
        
        # Simple swing-based setup logic
        swing_high = setup_data['swing_high']
        swing_low = setup_data['swing_low']
        
        # Determine setup direction based on market structure and position
        pine_summary = self.pine_analyzer.get_analysis_summary()
        market_structure = pine_summary['current_structure']
        
        if market_structure == 1 and self.current_price < swing_low + pip_buffer:
            # Bullish setup near swing low
            signal['action'] = 'BUY_SETUP'
            signal['entry'] = round(swing_low + pip_buffer, decimals)
            signal.update(self._calculate_atr_levels('BUY', 'setup'))
            signal['raw_signal'] = f"BUY WHEN ≥ ${signal['entry']:.{decimals}f} - Swing low support in bullish structure"
            signal['ict_explanation'] = f"""
• Market Structure: Bullish ({market_structure}) - trend favors upward movement
• Entry Logic: Entry above swing low at ${swing_low:.{decimals}f} with {self.selected_asset['pip_buffer']}-pip buffer
• ICT Theory: Swing lows act as institutional support zones where smart money accumulates
• Confluence: Bullish market structure + swing support level
• Risk Management: Stop below swing low, target based on {self.selected_mode['tp_atr_multiple']}x ATR"""
            
        elif market_structure == -1 and self.current_price > swing_high - pip_buffer:
            # Bearish setup near swing high
            signal['action'] = 'SELL_SETUP'
            signal['entry'] = round(swing_high - pip_buffer, decimals)
            signal.update(self._calculate_atr_levels('SELL', 'setup'))
            signal['raw_signal'] = f"SELL WHEN ≤ ${signal['entry']:.{decimals}f} - Swing high resistance in bearish structure"
            signal['ict_explanation'] = f"""
• Market Structure: Bearish ({market_structure}) - trend favors downward movement
• Entry Logic: Entry below swing high at ${swing_high:.{decimals}f} with {self.selected_asset['pip_buffer']}-pip buffer
• ICT Theory: Swing highs act as institutional resistance zones where smart money distributes
• Confluence: Bearish market structure + swing resistance level
• Risk Management: Stop above swing high, target based on {self.selected_mode['tp_atr_multiple']}x ATR"""
        else:
            signal['raw_signal'] = f"No clear swing setup - Price: ${self.current_price:.{decimals}f}, Swing Range: ${swing_low:.{decimals}f} - ${swing_high:.{decimals}f}"
            signal['ict_explanation'] = f"""
• Market Structure: Neutral/Unclear ({market_structure})
• Entry Logic: Price between swing levels - wait for clearer setup
• ICT Theory: Avoid trading in consolidation between key levels
• Confluence: Insufficient confluence factors present
• Risk Management: Wait for price to approach key swing levels with clear structure"""
        
        return signal

    def run_trading_system(self):
        """Run the complete trading system"""
        # Step 1: Mode selection
        if not self.select_mode():
            return None
        
        # Step 2: Asset selection
        if not self.select_asset():
            return None
        
        # Step 3: Timeframe selection
        if not self.select_timeframe():
            return None
        
        mode_name = self.selected_mode['name']
        display_name = self.selected_asset['display_name']
        timeframe_name = self.selected_timeframe['display_name']
        
        print(f"🚀 {mode_name.upper()}")
        print(f"📊 {display_name} {timeframe_name}")
        print("=" * 50)
        
        # Step 4: Download fresh data
        if not self.download_fresh_data():
            return None
        
        # Step 5: Analyze market
        if not self.analyze_market():
            return None
        
        # Step 6: Generate signal
        signal = self.generate_signal()
        
        return signal
    
    def _analyze_multi_timeframe(self):
        """Analyze market using multiple timeframes"""
        print("\n🔍 MULTI-TIMEFRAME ANALYSIS")
        print("=" * 40)
        
        try:
            analysis_results = {
                'daily': None,
                '4h': None,
                '1h': None,
                '15m': None,
                '5m': None
            }
            
            # Analyze each timeframe
            for tf in self.selected_timeframe['timeframes']:
                interval = tf['interval']
                name = tf['name']
                purpose = tf['purpose']
                
                print(f"\n📊 {name} Analysis ({purpose})")
                print("-" * 30)
                
                # Load and prepare data
                data = pd.read_csv(tf['data_file'])
                data.columns = data.columns.str.lower()
                data = data.loc[:,~data.columns.duplicated()]
                
                if 'datetime' in data.columns:
                    data['datetime'] = pd.to_datetime(data['datetime'])
                    data.set_index('datetime', inplace=True)
                
                # Load data into analyzers
                self.analyzer.load_data(file_path=tf['data_file'])
                self.analyzer.calculate_indicators()
                
                self.pine_analyzer.load_data(data)
                self.pine_analyzer.calculate_all_indicators()
                
                # Get analysis summary
                pine_summary = self.pine_analyzer.get_analysis_summary()
                pine_signals = self.pine_analyzer.get_latest_signals()
                
                # Store analysis based on timeframe
                analysis_results[interval] = {
                    'summary': pine_summary,
                    'signals': pine_signals,
                    'data': data
                }
                
                # Print timeframe-specific analysis
                if interval == '1d':
                    self._print_daily_analysis(pine_summary, pine_signals)
                elif interval == '4h':
                    self._print_4h_analysis(pine_summary, pine_signals)
                elif interval == '1h':
                    self._print_1h_analysis(pine_summary, pine_signals)
                elif interval == '15m':
                    self._print_15m_analysis(pine_summary, pine_signals)
                    # Get ATR from 15m for position sizing
                    self.atr_value = self.pine_analyzer.data['atr'].iloc[-1]
                elif interval == '5m':
                    self._print_5m_analysis(pine_summary, pine_signals)
                    # Get current price from 5m
                    self.current_price = self.pine_analyzer.data['close'].iloc[-1]
                
            # Store multi-timeframe analysis results
            self.selected_timeframe['analysis'] = analysis_results
            
            return True
            
        except Exception as e:
            print(f"❌ Error during multi-timeframe analysis: {str(e)}")
            return False
    
    def _print_daily_analysis(self, summary, signals):
        """Print daily timeframe analysis"""
        print("Day High:", summary.get('day_high', 'N/A'))
        print("Day Low:", summary.get('day_low', 'N/A'))
        print("Liquidity Levels Above:", len(signals.get('liquidity_levels_above', [])))
        print("Liquidity Levels Below:", len(signals.get('liquidity_levels_below', [])))
        print("Market Bias:", signals.get('market_bias', 'Neutral'))
    
    def _print_4h_analysis(self, summary, signals):
        """Print 4-hour timeframe analysis"""
        print("\n4H TIMEFRAME ICT ANALYSIS:")
        print("-" * 30)
        print("Market Structure:", summary.get('current_structure', 'N/A'))
        
        # Order Blocks Analysis
        bull_obs = summary.get('bullish_obs', 0)
        bear_obs = summary.get('bearish_obs', 0)
        print(f"Active Order Blocks: {bull_obs} Bull, {bear_obs} Bear")
        
        # Get detailed OB information if available
        ob_details = signals.get('ob_details', {})
        if ob_details.get('bullish', []):
            print("\nBullish OBs:")
            for ob in ob_details['bullish'][-3:]:  # Show last 3
                print(f"  • ${ob.get('price', 0):.4f} ({ob.get('age', 'N/A')} candles)")
        
        if ob_details.get('bearish', []):
            print("\nBearish OBs:")
            for ob in ob_details['bearish'][-3:]:
                print(f"  • ${ob.get('price', 0):.4f} ({ob.get('age', 'N/A')} candles)")
        
        # Support/Resistance Levels
        support_levels = signals.get('support_levels', [])
        resistance_levels = signals.get('resistance_levels', [])
        
        if support_levels:
            print("\nKey Support Levels:")
            for level in support_levels[-3:]:  # Show last 3
                print(f"  • ${float(level):.4f}")
        
        if resistance_levels:
            print("\nKey Resistance Levels:")
            for level in resistance_levels[-3:]:
                print(f"  • ${float(level):.4f}")
        
        # Recent Structure Breaks
        breaks = signals.get('structure_breaks', [])
        if breaks:
            print("\nRecent Structure Breaks:")
            for brk in breaks[-2:]:
                if isinstance(brk, dict):
                    print(f"  • {brk.get('type', 'Unknown')} break at ${float(brk.get('price', 0)):.4f}")
                else:
                    print(f"  • Break at ${float(brk):.4f}")
        
        # FVG Information
        fvgs = signals.get('active_fvgs', {'up': [], 'down': []})
        if fvgs.get('up'):
            print("\nBullish FVGs:")
            for fvg in fvgs['up'][-2:]:
                print(f"  • ${float(fvg.get('top', 0)):.4f} - ${float(fvg.get('bottom', 0)):.4f}")
        
        if fvgs.get('down'):
            print("\nBearish FVGs:")
            for fvg in fvgs['down'][-2:]:
                print(f"  • ${float(fvg.get('top', 0)):.4f} - ${float(fvg.get('bottom', 0)):.4f}")
    
    def _print_1h_analysis(self, summary, signals):
        """Print 1-hour timeframe analysis"""
        print("\n1H TIMEFRAME ICT ANALYSIS:")
        print("-" * 30)
        print("Trend Direction:", signals.get('trend_direction', 'N/A'))
        print("Momentum:", signals.get('momentum', 'N/A'))
        
        # FVG Analysis
        fvg_count_up = summary.get('active_fvg_up', 0)
        fvg_count_down = summary.get('active_fvg_down', 0)
        print(f"\nActive FVGs: {fvg_count_up} Up, {fvg_count_down} Down")
        
        # Get detailed FVG information if available
        fvg_details = signals.get('fvg_details', {})
        
        if fvg_details.get('up', []):
            print("\nBullish FVGs:")
            for fvg in fvg_details['up'][-3:]:  # Show last 3
                if isinstance(fvg, dict):
                    top = float(fvg.get('top', 0))
                    bottom = float(fvg.get('bottom', 0))
                    size = top - bottom
                    print(f"  • ${top:.4f} - ${bottom:.4f} (Size: {size:.4f})")
        
        if fvg_details.get('down', []):
            print("\nBearish FVGs:")
            for fvg in fvg_details['down'][-3:]:  # Show last 3
                if isinstance(fvg, dict):
                    top = float(fvg.get('top', 0))
                    bottom = float(fvg.get('bottom', 0))
                    size = top - bottom
                    print(f"  • ${top:.4f} - ${bottom:.4f} (Size: {size:.4f})")
        
        # Order Flow Analysis
        print("\nOrder Flow:")
        print(f"• Recent OB Breaks: {signals.get('recent_ob_breaks', 0)}")
        print(f"• Fresh FVGs: {signals.get('fresh_fvgs', 0)}")
        print(f"• Swept Levels: {signals.get('swept_levels', 0)}")
        
        # Additional Price Action Details
        if signals.get('recent_moves', []):
            print("\nRecent Price Action:")
            for move in signals.get('recent_moves', [])[-2:]:  # Show last 2
                print(f"• {move.get('type', 'Move')}: {move.get('description', 'N/A')}")
    
    def _print_15m_analysis(self, summary, signals):
        """Print 15-minute timeframe analysis"""
        print("\n15M TIMEFRAME ICT ANALYSIS:")
        print("-" * 30)
        
        # Entry Zones
        entry_zones = signals.get('entry_zones', [])
        entry_count = len(entry_zones) if isinstance(entry_zones, list) else 0
        print(f"Entry Zones Found: {entry_count}")
        
        if isinstance(entry_zones, list) and entry_zones:
            print("Potential Entry Areas:")
            for zone in entry_zones[-3:]:
                if isinstance(zone, dict):
                    print(f"  • ${zone.get('price', 0):.4f} ({zone.get('type', 'Unknown')})")
        
        # Order Blocks & FVGs
        ob_count = summary.get('fresh_obs', 0)
        fvg_count = summary.get('active_fvgs', 0)
        sweep_count = signals.get('recent_sweeps', 0)
        
        print("\nRecent Formations:")
        print(f"• Fresh Order Blocks: {ob_count}")
        print(f"• Active FVGs: {fvg_count}")
        print(f"• Recent Sweeps: {sweep_count}")
        
        # Recent Order Block Details
        ob_details = signals.get('ob_details', {})
        if ob_details.get('fresh', []):
            print("\nFresh Order Blocks:")
            for ob in ob_details['fresh'][-2:]:  # Show last 2
                print(f"  • {ob.get('type', 'OB')} at ${float(ob.get('price', 0)):.4f}")
        
        # Recent FVG Details
        fvg_details = signals.get('fvg_details', {})
        if fvg_details.get('active', []):
            print("\nActive FVGs:")
            for fvg in fvg_details['active'][-2:]:  # Show last 2
                print(f"  • {fvg.get('type', 'FVG')} (${float(fvg.get('size', 0)):.4f} range)")
        
        # Price Action
        print("\nPrice Action Analysis:")
        print(f"• Structure: {signals.get('structure_state', 'N/A')}")
        print(f"• Recent Test: {signals.get('recent_test', 'None')}")
        print(f"• Momentum: {signals.get('momentum_state', 'N/A')}")
        
        # Additional Market Context
        ctx = signals.get('market_context', {})
        if ctx:
            print("\nMarket Context:")
            print(f"• Volatility: {ctx.get('volatility', 'N/A')}")
            print(f"• Volume Profile: {ctx.get('volume_profile', 'N/A')}")
    
    def _print_5m_analysis(self, summary, signals):
        """Print 5-minute timeframe analysis"""
        print("\n5M TIMEFRAME ICT ANALYSIS:")
        print("-" * 30)
        
        # Entry Points
        entry_points = signals.get('entry_points', [])
        entry_count = len(entry_points) if isinstance(entry_points, list) else 0
        print(f"Entry Points Found: {entry_count}")
        
        if isinstance(entry_points, list) and entry_points:
            print("\nPrecise Entry Points:")
            for point in entry_points[-3:]:  # Show last 3
                if isinstance(point, dict):
                    price = float(point.get('price', 0))
                    entry_type = point.get('type', 'Unknown')
                    confidence = point.get('confidence', 'N/A')
                    print(f"  • ${price:.4f} ({entry_type}) - Confidence: {confidence}")
        
        # Recent Market Activity
        recent_high = float(signals.get('recent_high_wick', 0))
        recent_low = float(signals.get('recent_low_wick', 0))
        
        print("\nRecent Activity:")
        print(f"• High Wick: ${recent_high:.4f}")
        print(f"• Low Wick: ${recent_low:.4f}")
        print(f"• Wick Range: ${(recent_high - recent_low):.4f}")
        print(f"• Volume Profile: {signals.get('volume_profile', 'N/A')}")
        
        # Micro Price Action
        micro_moves = signals.get('micro_moves', [])
        if isinstance(micro_moves, list) and micro_moves:
            print("\nRecent Price Moves:")
            for move in micro_moves[-2:]:  # Show last 2
                if isinstance(move, dict):
                    print(f"  • {move.get('type', 'Move')}: {move.get('description', 'N/A')}")
        
        # Short-term Analysis
        print("\nShort-term Analysis:")
        print(f"• Bias: {signals.get('short_term_bias', 'N/A')}")
        print(f"• Structure State: {signals.get('micro_structure', 'N/A')}")
        print(f"• Recent Break: {signals.get('recent_break', 'None')}")
        
        # Entry Conditions
        conditions = signals.get('entry_conditions', {})
        if conditions:
            print("\nEntry Conditions:")
            for condition, status in conditions.items():
                print(f"• {condition}: {status}")
    
    def print_signal(self, signal):
        """Print formatted signal based on mode"""
        if signal is None:
            print("❌ Unable to generate signal")
            return
        
        # Extract reasoning from raw signal
        reasoning = "ICT Analysis"
        if signal.get('raw_signal'):
            raw = signal['raw_signal']
            if '-' in raw:
                reasoning = raw.split('-')[-1].strip()
        
        decimals = self.selected_asset['price_decimals']
        asset_name = self.selected_asset['name']
        mode_type = signal.get('mode', 'unknown')
        
        print(f"\n📊 {asset_name.upper()} SIGNAL")
        print("=" * 40)
        print(f"⏰ Time: {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💰 Current Price: ${signal['current_price']:.{decimals}f}")
        print(f"🎯 Action: {signal['action']}")
        print(f"💡 Reason: {reasoning}")
        
        if signal['action'] not in ['WAIT']:
            print(f"📍 Entry: ${signal['entry']:.{decimals}f}")
            print(f"🟢 Take Profit: ${signal['tp']:.{decimals}f}")
            print(f"🔴 Stop Loss: ${signal['sl']:.{decimals}f}")
            
            # Calculate risk/reward
            if signal['action'] in ['BUY', 'BUY_SETUP']:
                profit_pips = signal['tp'] - signal['entry']
                loss_pips = signal['entry'] - signal['sl']
            else:
                profit_pips = signal['entry'] - signal['tp']
                loss_pips = signal['sl'] - signal['entry']
            
            rr_ratio = profit_pips / loss_pips if loss_pips > 0 else 0
            print(f"⚖️ Risk/Reward: 1:{rr_ratio:.1f}")
            
            # Mode-specific quick copy format
            if mode_type == 'setup':
                action_text = signal['action'].replace('_SETUP', ' WHEN')
                operator = '≥' if 'BUY' in signal['action'] else '≤'
                print(f"\n📋 QUICK COPY:")
                print(f"{action_text} {operator} ${signal['entry']:.{decimals}f}")
                print(f"TP: ${signal['tp']:.{decimals}f} | SL: ${signal['sl']:.{decimals}f}")
            else:
                action_text = signal['action']
                print(f"\n📋 QUICK COPY:")
                print(f"{action_text} {asset_name} @ ${signal['entry']:.{decimals}f}")
                print(f"TP: ${signal['tp']:.{decimals}f} | SL: ${signal['sl']:.{decimals}f}")
        
        # Show ICT explanation for setup mode
        if mode_type == 'setup' and signal.get('ict_explanation'):
            print(f"\n📚 ICT EXPLANATION:")
            print(signal['ict_explanation'])
        
        # Print immediate action guide for multi-timeframe mode
        if mode_type == 'multi':
            print("\n📝 WHAT TO DO NOW:")
            print("-" * 40)
            
            if signal['action'] == 'WAIT':
                print("1. Monitor the identified levels:")
                print("   • Daily liquidity levels for potential sweeps")
                print("   • 4H order blocks for reversals")
                print("   • Active FVGs for potential fills")
                print("2. Wait for one of these triggers:")
                print("   • Clean sweep of liquidity level")
                print("   • Price reaching untapped FVG")
                print("   • Fresh order block formation")
                print("3. Look for entry when price action confirms the setup")
            else:
                entry_type = "BUY" if "BUY" in signal['action'] else "SELL"
                print(f"1. {entry_type} Setup Identified:")
                print(f"   • Entry: ${signal['entry']:.{decimals}f}")
                print(f"   • Stop Loss: ${signal['sl']:.{decimals}f}")
                print(f"   • Target: ${signal['tp']:.{decimals}f}")
                print("2. Monitor Entry Conditions:")
                if "SWEEP" in signal.get('raw_signal', ''):
                    print("   • Wait for liquidity sweep confirmation")
                    print("   • Enter only after sweep is complete")
                elif "FVG" in signal.get('raw_signal', ''):
                    print("   • Wait for price to reach FVG level")
                    print("   • Confirm FVG remains valid (not filled)")
                print("3. Risk Management:")
                print("   • Use stated stop loss level")
                print("   • Consider scaling out at key levels")
            
            print("\n4. Important Reminders:")
            print("   • Confirm entry with lower timeframe price action")
            print("   • Always respect your stop loss")
            print("   • Monitor higher timeframes for changes")
        
        print(f"\n🤖 Source: {signal.get('confidence', 'ICT')}")
        print(f"📋 Mode: {mode_type.upper()}")
        print("=" * 40)
    
    def _cleanup_files(self):
        """Clean up created CSV files"""
        if self.created_files:
            print("\n🧹 Cleaning up temporary files...")
            for filename in self.created_files:
                try:
                    if os.path.exists(filename):
                        os.remove(filename)
                        print(f"✓ Deleted: {filename}")
                except Exception as e:
                    print(f"⚠️ Could not delete {filename}: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C interrupt"""
        print("\n\n⏹️ Program interrupted by user")
        self._cleanup_files()
        sys.exit(0)

def main():
    """Main execution function with Twelve Data API integration"""
    # Your Gemini API key
    GEMINI_API_KEY = "AIzaSyDLhXxQ6yyLRFFKHZWpH1FQiVl8AZW-3sg"
    
    print("🚀 ENHANCED ICT TRADING SYSTEM")
    print("=" * 30)
    print("Professional trading with Twelve Data API")
    print("Real-time forex • crypto • commodities")
    print()
    
    # Use predefined Twelve Data API key
    twelve_data_key = "fcbc1b91fbb34e3cb94b21c33b4598f8"
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

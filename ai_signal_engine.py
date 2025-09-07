#!/usr/bin/env python3
"""
AI Trading Signal Generation Engine
Uses real MT5 market data to generate trading signals
"""

import os
import httpx
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Signal, User
import statistics

# MT5 Bridge Configuration
MT5_BRIDGE_URL = os.getenv("MT5_BRIDGE_URL", "http://ai.cash-revolution.com:8000")
MT5_BRIDGE_API_KEY = os.getenv("MT5_BRIDGE_API_KEY", "1d2376ae63aedb38f4d13e1041fb5f0b56cc48c44a8f106194d2da23e4039736")

class TechnicalAnalyzer:
    """Technical analysis functions for signal generation"""
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0.0
        return sum(prices[-period:]) / period
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0  # Neutral
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def detect_trend(prices: List[float], period: int = 20) -> str:
        """Detect price trend direction"""
        if len(prices) < period:
            return "SIDEWAYS"
        
        sma_short = TechnicalAnalyzer.calculate_sma(prices, 5)
        sma_long = TechnicalAnalyzer.calculate_sma(prices, period)
        
        if sma_short > sma_long * 1.001:  # 0.1% threshold
            return "BULLISH"
        elif sma_short < sma_long * 0.999:
            return "BEARISH"
        else:
            return "SIDEWAYS"
    
    @staticmethod
    def calculate_volatility(prices: List[float]) -> float:
        """Calculate price volatility (standard deviation)"""
        if len(prices) < 2:
            return 0.0
        return statistics.stdev(prices) / statistics.mean(prices) * 100

class SignalEngine:
    """Main signal generation engine"""
    
    def __init__(self):
        # Major Forex Pairs
        major_pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCHF", "USDCAD", "NZDUSD"]
        
        # Minor Forex Pairs (Cross currencies)
        minor_pairs = [
            "EURGBP", "EURJPY", "EURCHF", "EURAUD", "EURCAD", "EURNZD",
            "GBPJPY", "GBPCHF", "GBPAUD", "GBPCAD", "GBPNZD",
            "AUDJPY", "AUDCHF", "AUDCAD", "AUDNZD",
            "CADJPY", "CADCHF", "NZDJPY", "NZDCHF", "NZDCAD",
            "CHFJPY"
        ]
        
        # Precious Metals
        metals = ["XAUUSD", "XAGUSD"]  # Gold, Silver
        
        # Stock Indices  
        indices = ["US500", "NAS100", "US30"]  # S&P 500, NASDAQ, Dow Jones
        
        # Combine all symbols
        self.symbols = major_pairs + minor_pairs + metals + indices
        self.analyzer = TechnicalAnalyzer()
        
        print(f"Initialized SignalEngine with {len(self.symbols)} symbols:")
        print(f"- Major Pairs: {len(major_pairs)}")
        print(f"- Minor Pairs: {len(minor_pairs)}")  
        print(f"- Metals: {len(metals)}")
        print(f"- Indices: {len(indices)}")
        print(f"- Total: {len(self.symbols)}")
    
    async def get_market_data(self, symbol: str, count: int = 100) -> Optional[List[Dict]]:
        """Fetch historical price data from MT5 Bridge"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                headers = {"X-API-Key": MT5_BRIDGE_API_KEY}
                
                rates_request = {
                    "symbol": symbol,
                    "timeframe": "M15",  # 15-minute timeframe
                    "count": count
                }
                
                response = await client.post(
                    f"{MT5_BRIDGE_URL}/bridge/rates",
                    json=rates_request,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("rates", [])
                else:
                    print(f"Failed to get data for {symbol}: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"Error fetching market data for {symbol}: {e}")
            return None
    
    def analyze_symbol(self, symbol: str, rates_data: List[Dict]) -> Optional[Dict]:
        """Analyze symbol and generate signal if conditions are met"""
        if not rates_data or len(rates_data) < 50:
            return None
        
        # Extract close prices
        closes = [float(rate["close"]) for rate in rates_data]
        highs = [float(rate["high"]) for rate in rates_data]
        lows = [float(rate["low"]) for rate in rates_data]
        
        # Current price and analysis
        current_price = closes[-1]
        
        # Technical indicators
        rsi = self.analyzer.calculate_rsi(closes)
        trend = self.analyzer.detect_trend(closes)
        volatility = self.analyzer.calculate_volatility(closes[-20:])  # Last 20 periods
        sma_20 = self.analyzer.calculate_sma(closes, 20)
        sma_50 = self.analyzer.calculate_sma(closes, 50)
        
        # Signal generation logic - More flexible approach
        signal_type = None
        confidence = 0
        explanation = ""
        
        print(f"  {symbol}: Price={current_price:.5f}, RSI={rsi:.1f}, Trend={trend}, Vol={volatility:.2f}%, SMA20={sma_20:.5f}")
        
        # Trend-following signals (relaxed conditions)
        if trend == "BULLISH" and current_price > sma_20:
            if rsi < 75:  # More flexible overbought threshold
                signal_type = "BUY"
                base_confidence = 70 if rsi < 60 else 65
                confidence = min(95, base_confidence + (70 - rsi) * 0.3 + min(volatility, 2) * 2)
                explanation = f"Bullish trend confirmed with price above MA20. RSI at {rsi:.1f} supports upward momentum. Volatility: {volatility:.2f}%."
            
        elif trend == "BEARISH" and current_price < sma_20:
            if rsi > 25:  # More flexible oversold threshold
                signal_type = "SELL"
                base_confidence = 70 if rsi > 40 else 65
                confidence = min(95, base_confidence + (rsi - 30) * 0.3 + min(volatility, 2) * 2)
                explanation = f"Bearish trend with price below MA20. RSI at {rsi:.1f} indicates continued downward pressure. Volatility: {volatility:.2f}%."
        
        # Sideways market - look for breakouts or reversals (more flexible)
        elif trend == "SIDEWAYS":
            if rsi > 60:  # Look for potential reversal signals
                signal_type = "SELL"
                confidence = min(85, 55 + (rsi - 60) * 1.2 + volatility * 10)
                explanation = f"Sideways market with RSI at {rsi:.1f} suggesting short-term weakness. Low volatility ({volatility:.2f}%) scalping opportunity."
                
            elif rsi < 40:  # Look for potential bounce signals
                signal_type = "BUY"
                confidence = min(85, 55 + (40 - rsi) * 1.2 + volatility * 10)
                explanation = f"RSI at {rsi:.1f} in ranging market suggests potential upward move. Low volatility scalping setup."
        
        # Strong momentum signals (regardless of trend)
        if not signal_type:
            if rsi > 75 and sma_20 > sma_50 * 1.002:  # Strong uptrend but overbought
                signal_type = "SELL"
                confidence = min(80, 55 + (rsi - 75) * 2)
                explanation = f"Strong uptrend but RSI overbought at {rsi:.1f}. Short-term pullback expected."
                
            elif rsi < 25 and sma_20 < sma_50 * 0.998:  # Strong downtrend but oversold
                signal_type = "BUY"
                confidence = min(80, 55 + (25 - rsi) * 2)
                explanation = f"Oversold RSI ({rsi:.1f}) in downtrend suggests temporary bounce opportunity."
        
        # Ensure minimum confidence threshold
        if signal_type and confidence >= 60:  # Lower threshold for more signals
            # Calculate stop loss and take profit
            atr_approx = (max(highs[-20:]) - min(lows[-20:])) / 20  # Approximate ATR
            
            if signal_type == "BUY":
                stop_loss = current_price - (atr_approx * 1.5)
                take_profit = current_price + (atr_approx * 2.5)
            else:  # SELL
                stop_loss = current_price + (atr_approx * 1.5)
                take_profit = current_price - (atr_approx * 2.5)
            
            return {
                "symbol": symbol,
                "signal_type": signal_type,
                "entry_price": round(current_price, 5),
                "stop_loss": round(stop_loss, 5),
                "take_profit": round(take_profit, 5),
                "confidence": round(confidence, 1),
                "explanation": explanation,
                "trend": trend,
                "rsi": round(rsi, 1),
                "volatility": round(volatility, 2)
            }
        
        return None
    
    async def generate_signals(self, max_signals: int = 3) -> List[Dict]:
        """Generate trading signals for multiple symbols"""
        print(f"Generating signals for {len(self.symbols)} symbols...")
        
        signals = []
        
        for symbol in self.symbols:
            if len(signals) >= max_signals:
                break
                
            print(f"Analyzing {symbol}...")
            
            # Get market data
            rates_data = await self.get_market_data(symbol)
            
            if rates_data:
                # Analyze and generate signal
                signal_data = self.analyze_symbol(symbol, rates_data)
                
                if signal_data:
                    signals.append(signal_data)
                    print(f"Generated {signal_data['signal_type']} signal for {symbol} with {signal_data['confidence']}% confidence")
                else:
                    print(f"No signal conditions met for {symbol}")
            else:
                print(f"Failed to get data for {symbol}")
            
            # Small delay to avoid overwhelming the bridge
            await asyncio.sleep(0.5)
        
        print(f"Generated {len(signals)} signals total")
        return signals
    
    def save_signals_to_db(self, signals: List[Dict], user_id: Optional[int] = None):
        """Save generated signals to database"""
        db = SessionLocal()
        
        try:
            for signal_data in signals:
                # Create new signal
                new_signal = Signal(
                    user_id=user_id,  # None for public signals
                    asset=signal_data["symbol"],
                    signal_type=signal_data["signal_type"],
                    entry_price=signal_data["entry_price"],
                    stop_loss=signal_data["stop_loss"],
                    take_profit=signal_data["take_profit"],
                    reliability=signal_data["confidence"],
                    is_public=True,  # Make signals public
                    current_price=signal_data["entry_price"],
                    gemini_explanation=signal_data["explanation"],
                    expires_at=datetime.utcnow() + timedelta(hours=4),  # 4-hour expiry
                    is_active=True,
                    outcome="PENDING"
                )
                
                db.add(new_signal)
                print(f"Saved {signal_data['signal_type']} signal for {signal_data['symbol']}")
            
            db.commit()
            print(f"Successfully saved {len(signals)} signals to database")
            
        except Exception as e:
            db.rollback()
            print(f"Error saving signals to database: {e}")
        finally:
            db.close()

async def main():
    """Main function to generate and save signals"""
    print("=" * 60)
    print("AI TRADING SIGNAL GENERATION ENGINE")
    print("=" * 60)
    
    engine = SignalEngine()
    
    # Generate signals
    signals = await engine.generate_signals(max_signals=5)
    
    if signals:
        # Save to database
        engine.save_signals_to_db(signals)
        
        print("\nGENERATED SIGNALS SUMMARY:")
        print("-" * 40)
        
        for signal in signals:
            print(f"• {signal['symbol']}: {signal['signal_type']} @ {signal['entry_price']}")
            print(f"  Confidence: {signal['confidence']}%")
            print(f"  SL: {signal['stop_loss']} | TP: {signal['take_profit']}")
            print(f"  Reason: {signal['explanation'][:80]}...")
            print()
    else:
        print("No signals generated this time")
    
    print("=" * 60)
    print("SIGNAL GENERATION COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
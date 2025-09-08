import os
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from sqlalchemy.orm import Session
from schemas import SignalTypeEnum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
    else:
        model = None
except ImportError:
    GEMINI_AVAILABLE = False
    model = None

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False

class ProfessionalSignalEngine:
    """
    MOTORE PROFESSIONALE DI GENERAZIONE SEGNALI DI TRADING

    Combina:
    - Analisi tecnica avanzata (RSI, MACD, Bollinger Bands, ATR)
    - Price action analysis (pattern candele, trend, supporti/resistenze)
    - Dati reali da MetaTrader 5 (tick data, volumi, spread)
    - Spiegazioni AI tramite Google Gemini
    - Sistema di scoring affidabilità 0-100%
    """

    def __init__(self):
        self.mt5_bridge_url = os.getenv("MT5_BRIDGE_URL", "http://ai.cash-revolution.com:8000")
        self.bridge_connected = False

        # Asset supportati con varianti per diversi broker
        self.symbol_variants = {
            # FOREX MAJOR PAIRS - varianti comuni broker
            "EURUSD": ["EURUSD", "EURUSDm", "EURUSD.", "EURUSD.raw", "EURUSD#"],
            "GBPUSD": ["GBPUSD", "GBPUSDm", "GBPUSD.", "GBPUSD.raw", "GBPUSD#"],
            "USDJPY": ["USDJPY", "USDJPYm", "USDJPY.", "USDJPY.raw", "USDJPY#"],
            "USDCHF": ["USDCHF", "USDCHFm", "USDCHF.", "USDCHF.raw", "USDCHF#"],
            "AUDUSD": ["AUDUSD", "AUDUSDm", "AUDUSD.", "AUDUSD.raw", "AUDUSD#"],
            "USDCAD": ["USDCAD", "USDCADm", "USDCAD.", "USDCAD.raw", "USDCAD#"],
            "NZDUSD": ["NZDUSD", "NZDUSDm", "NZDUSD.", "NZDUSD.raw", "NZDUSD#"],
            
            # FOREX MINOR PAIRS 
            "EURGBP": ["EURGBP", "EURGBPm", "EURGBP.", "EURGBP.raw", "EURGBP#"],
            "EURJPY": ["EURJPY", "EURJPYm", "EURJPY.", "EURJPY.raw", "EURJPY#"],
            "EURCHF": ["EURCHF", "EURCHFm", "EURCHF.", "EURCHF.raw", "EURCHF#"],
            "EURAUD": ["EURAUD", "EURAUDm", "EURAUD.", "EURAUD.raw", "EURAUD#"],
            "GBPJPY": ["GBPJPY", "GBPJPYm", "GBPJPY.", "GBPJPY.raw", "GBPJPY#"],
            "GBPCHF": ["GBPCHF", "GBPCHFm", "GBPCHF.", "GBPCHF.raw", "GBPCHF#"],
            "AUDCAD": ["AUDCAD", "AUDCADm", "AUDCAD.", "AUDCAD.raw", "AUDCAD#"],
            "AUDJPY": ["AUDJPY", "AUDJPYm", "AUDJPY.", "AUDJPY.raw", "AUDJPY#"],
            "CADJPY": ["CADJPY", "CADJPYm", "CADJPY.", "CADJPY.raw", "CADJPY#"],
            "CHFJPY": ["CHFJPY", "CHFJPYm", "CHFJPY.", "CHFJPY.raw", "CHFJPY#"],
            
            # METALS - varianti comuni
            "XAUUSD": ["XAUUSD", "XAUUSDm", "XAUUSD.", "GOLD", "GOLDm", "GOLD.", "Au"],
            "XAGUSD": ["XAGUSD", "XAGUSDm", "XAGUSD.", "SILVER", "SILVERm", "SILVER.", "Ag"],
            
            # INDICES - varianti broker diversi
            "US500": ["US500", "US500m", "US500.", "SPX500", "SP500", "S&P500"],
            "US30": ["US30", "US30m", "US30.", "DJI30", "DJ30", "DJIA", "YM"],
            "NAS100": ["NAS100", "NAS100m", "NAS100.", "NASDAQ", "NDX", "NQ"],
            "GER30": ["GER30", "GER30m", "GER30.", "DAX30", "DAX", "DE30"],
            "UK100": ["UK100", "UK100m", "UK100.", "FTSE", "UKX"],
            "JPN225": ["JPN225", "JPN225m", "JPN225.", "NIKKEI", "N225", "NI225"],
        }
        
        # Lista completa simboli base
        self.supported_symbols = list(self.symbol_variants.keys())

        # Timeframes per analisi multi-frame
        self.timeframes = {
            'M1': 1,
            'M5': 5,
            'M15': 15,
            'M30': 30,
            'H1': 60,
            'H4': 240,
            'D1': 1440
        }

    def check_mt5_bridge(self) -> bool:
        """Controlla connessione al MT5 Bridge sulla VPS"""
        try:
            response = requests.get(
                f"{self.mt5_bridge_url}/api/mt5/quotes",
                params={"symbols": "EURUSD"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.bridge_connected = data.get("bridge_connected", False)
                logger.info(f"MT5 Bridge {'connesso' if self.bridge_connected else 'disconnesso'}")
                return self.bridge_connected
            else:
                logger.error(f"MT5 Bridge non raggiungibile: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Errore connessione MT5 Bridge: {e}")
            return False

    def get_market_data(self, symbol: str, timeframe: str = 'H1', count: int = 500) -> Optional[pd.DataFrame]:
        """
        Estrae dati di mercato reali da MT5
        Prova tutte le varianti del simbolo per diversi broker
        """
        if not self.mt5_initialized:
            if not self.initialize_mt5():
                return None

        # Prova tutte le varianti del simbolo
        variants = self.symbol_variants.get(symbol, [symbol])
        
        for variant in variants:
            try:
                # Scarica dati OHLCV da MT5
                rates = mt5.copy_rates_from_pos(
                    variant, 
                    self.timeframes.get(timeframe, mt5.TIMEFRAME_H1), 
                    0, 
                    count
                )

                if rates is not None and len(rates) > 50:  # Dati sufficienti
                    # Converte in DataFrame pandas per analisi
                    df = pd.DataFrame(rates)
                    df['time'] = pd.to_datetime(df['time'], unit='s')
                    df.set_index('time', inplace=True)
                    
                    logger.info(f"Dati trovati per {symbol} usando variante {variant}")
                    return df

            except Exception as e:
                logger.debug(f"Variante {variant} non funziona: {e}")
                continue

        logger.error(f"Nessuna variante funzionante per {symbol}")
        return None

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcola tutti gli indicatori tecnici utilizzati per i segnali:
        - Moving Averages (SMA, EMA)
        - RSI (Relative Strength Index)
        - MACD (Moving Average Convergence Divergence)
        - Bollinger Bands
        - ATR (Average True Range)
        - Stochastic Oscillator
        """
        try:
            # Moving Averages per identificare trend
            df['sma_20'] = talib.SMA(df['close'], 20)
            df['sma_50'] = talib.SMA(df['close'], 50)
            df['ema_12'] = talib.EMA(df['close'], 12)
            df['ema_26'] = talib.EMA(df['close'], 26)

            # RSI per momentum e ipercomprato/ipervenduto
            df['rsi'] = talib.RSI(df['close'], 14)

            # MACD per segnali di incrocio
            df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'])

            # Bollinger Bands per volatilità
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(df['close'])

            # ATR per calcolo stop loss/take profit
            df['atr'] = talib.ATR(df['high'], df['low'], df['close'], 14)

            # Stochastic per conferme
            df['stoch_k'], df['stoch_d'] = talib.STOCH(df['high'], df['low'], df['close'])

            return df

        except Exception as e:
            logger.error(f"Errore calcolo indicatori: {e}")
            return df

    def analyze_price_action(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        ANALISI PRICE ACTION PROFESSIONALE

        Analizza:
        - Trend direction (up/down/sideways)
        - Momentum strength
        - Support/resistance levels
        - Candlestick patterns
        - Volume confirmation

        Restituisce un dizionario con punteggi per ogni componente
        """
        try:
            latest = df.iloc[-1]  # Ultima candela
            prev = df.iloc[-2]    # Candela precedente

            score_components = {}

            # ANALISI TREND - peso maggiore
            if latest['close'] > latest['sma_20'] > latest['sma_50']:
                score_components['uptrend'] = 30
            elif latest['close'] < latest['sma_20'] < latest['sma_50']:
                score_components['downtrend'] = -30
            else:
                score_components['sideways'] = 5

            # MOMENTUM ANALYSIS
            if latest['rsi'] > 70:
                score_components['overbought'] = -15  # Possibile inversione
            elif latest['rsi'] < 30:
                score_components['oversold'] = 15   # Possibile rimbalzo
            else:
                score_components['neutral_rsi'] = 5

            # MACD CROSSOVER SIGNALS - segnali forti
            if latest['macd'] > latest['macd_signal'] and prev['macd'] <= prev['macd_signal']:
                score_components['macd_bullish_cross'] = 20
            elif latest['macd'] < latest['macd_signal'] and prev['macd'] >= prev['macd_signal']:
                score_components['macd_bearish_cross'] = -20

            # BOLLINGER BANDS - estremi
            if latest['close'] < latest['bb_lower']:
                score_components['bb_oversold'] = 15
            elif latest['close'] > latest['bb_upper']:
                score_components['bb_overbought'] = -15

            # CANDLESTICK PATTERN ANALYSIS
            body_size = abs(latest['close'] - latest['open'])
            candle_range = latest['high'] - latest['low']

            if body_size > candle_range * 0.7:  # Candela con corpo forte
                if latest['close'] > latest['open']:
                    score_components['strong_bullish_candle'] = 10
                else:
                    score_components['strong_bearish_candle'] = -10

            return score_components

        except Exception as e:
            logger.error(f"Errore analisi price action: {e}")
            return {}

    def calculate_support_resistance(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calcola livelli di supporto e resistenza tramite pivot points"""
        try:
            recent_data = df.tail(50)  # Ultimi 50 periodi

            high = recent_data['high'].max()
            low = recent_data['low'].min()
            close = df.iloc[-1]['close']

            # Pivot Points calculation
            pivot = (high + low + close) / 3
            r1 = (2 * pivot) - low
            s1 = (2 * pivot) - high
            r2 = pivot + (high - low)
            s2 = pivot - (high - low)

            return {
                'pivot': pivot,
                'resistance_1': r1,
                'resistance_2': r2,
                'support_1': s1,
                'support_2': s2,
                'recent_high': high,
                'recent_low': low
            }

        except Exception as e:
            logger.error(f"Errore calcolo supporti/resistenze: {e}")
            return {}

    def generate_signal(self, symbol: str, db: Session) -> Optional[Dict]:
        """
        GENERAZIONE SEGNALE COMPLETA

        Process completo:
        1. Scarica dati reali da MT5
        2. Calcola indicatori tecnici
        3. Analizza price action
        4. Determina tipo segnale e affidabilità
        5. Calcola stop loss e take profit
        6. Genera spiegazione AI con Gemini
        7. Restituisce segnale completo
        """
        try:
            logger.info(f"Generando segnale per {symbol}")

            # 1. Ottieni dati di mercato
            df = self.get_market_data(symbol, 'H1', 500)
            if df is None:
                return None

            # 2. Calcola indicatori
            df = self.calculate_technical_indicators(df)

            # 3. Analizza price action
            pa_scores = self.analyze_price_action(df)
            price_action_score = sum(pa_scores.values())

            # 4. Calcola supporti/resistenze
            levels = self.calculate_support_resistance(df)

            # 5. Determina tipo segnale e affidabilità
            current_price = df.iloc[-1]['close']
            atr = df.iloc[-1]['atr']

            signal_type = SignalTypeEnum.HOLD
            reliability = 50.0

            if price_action_score > 35:
                signal_type = SignalTypeEnum.BUY
                reliability = min(90.0, 50 + price_action_score)
            elif price_action_score < -35:
                signal_type = SignalTypeEnum.SELL
                reliability = min(90.0, 50 + abs(price_action_score))

            # 6. Calcola stop loss e take profit basati su ATR
            if signal_type == SignalTypeEnum.BUY:
                stop_loss = current_price - (2 * atr)
                take_profit = current_price + (3 * atr)
            elif signal_type == SignalTypeEnum.SELL:
                stop_loss = current_price + (2 * atr)
                take_profit = current_price - (3 * atr)
            else:
                stop_loss = None
                take_profit = None

            # 7. Genera spiegazione AI (fallback se Gemini non disponibile)
            explanation = self.generate_gemini_explanation(
                symbol, signal_type, pa_scores, levels
            ) or f"Segnale {signal_type.value} per {symbol} basato su analisi tecnica multi-indicatore."

            # 8. Crea oggetto segnale completo
            signal_data = {
                'asset': symbol,
                'signal_type': signal_type,
                'reliability': reliability,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'current_price': current_price,
                'gemini_explanation': explanation,
                'price_action_score': price_action_score,
                'market_conditions': {
                    'atr': atr,
                    'rsi': df.iloc[-1]['rsi'],
                    'macd': df.iloc[-1]['macd'],
                    'trend': 'bullish' if price_action_score > 0 else 'bearish',
                    'support_resistance': levels,
                    'score_breakdown': pa_scores
                },
                'expires_at': datetime.utcnow() + timedelta(hours=8)
            }

            logger.info(f"Generato {signal_type.value} per {symbol} - Affidabilità: {reliability}%")
            return signal_data

        except Exception as e:
            logger.error(f"Errore generazione segnale {symbol}: {e}")
            return None

    def generate_gemini_explanation(
        self, 
        symbol: str, 
        signal_type: SignalTypeEnum, 
        scores: Dict[str, float],
        levels: Dict[str, float]
    ) -> str:
        """
        Genera spiegazione professionale usando Google Gemini AI
        Include motivi del segnale, fattori tecnici, rischi e suggerimenti
        """
        if not model:
            return self.generate_fallback_explanation(symbol, signal_type, scores)

        try:
            prompt = f"""Analizza questo segnale di trading per {symbol}:

            Tipo di segnale: {signal_type.value}
            Punteggi analisi tecnica: {scores}
            Livelli supporto/resistenza: {levels}

            Fornisci una spiegazione professionale (max 120 parole) che includa:
            1. Il motivo principale del segnale
            2. I fattori tecnici chiave
            3. I rischi da considerare
            4. Suggerimenti per la gestione

            Scrivi in italiano, linguaggio professionale ma chiaro."""

            response = model.generate_content(prompt)
            return response.text

        except Exception as e:
            logger.warning(f"Gemini non disponibile per {symbol}: {e}")
            return self.generate_fallback_explanation(symbol, signal_type, scores)

    def generate_fallback_explanation(
        self,
        symbol: str,
        signal_type: SignalTypeEnum,
        scores: Dict[str, float]
    ) -> str:
        """Genera spiegazione tecnica senza AI quando Gemini non è disponibile"""
        
        main_factors = []
        
        # Analizza i principali fattori tecnici
        for factor, score in scores.items():
            if abs(score) > 15:
                if "trend" in factor.lower():
                    main_factors.append("trend favorevole")
                elif "rsi" in factor.lower():
                    main_factors.append("RSI in zona favorevole")
                elif "macd" in factor.lower():
                    main_factors.append("segnale MACD positivo")
                elif "bb" in factor.lower():
                    main_factors.append("prezzo vicino a Bollinger Band")

        factors_text = ", ".join(main_factors[:3]) if main_factors else "indicatori tecnici"
        
        explanations = {
            SignalTypeEnum.BUY: f"Segnale rialzista su {symbol} supportato da {factors_text}. Momentum positivo e condizioni tecniche favorevoli per acquisti.",
            SignalTypeEnum.SELL: f"Segnale ribassista su {symbol} basato su {factors_text}. Pressione vendita e setup tecnico negativo.",
            SignalTypeEnum.HOLD: f"Mercato laterale su {symbol}. Segnali misti dagli indicatori tecnici. Attendere conferme per nuove posizioni."
        }
        
        return explanations.get(signal_type, f"Analisi tecnica {signal_type.value} per {symbol}.")

    def shutdown(self):
        """Chiude connessione MT5"""
        if self.mt5_initialized:
            mt5.shutdown()
            self.mt5_initialized = False
            logger.info("Connessione MT5 chiusa")

# Istanza globale del motore segnali
signal_engine = ProfessionalSignalEngine()

def get_signal_engine() -> ProfessionalSignalEngine:
    """Ottieni l'istanza globale del motore segnali"""
    return signal_engine
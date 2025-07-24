from utils.indicators import calculate_ema, calculate_rsi
from ai.trend_detector import TrendDetector
from ai.pattern_recognizer import detect_pattern
from ai.ta_engine import analyze_technicals
import ccxt

class StrategyManager:
    def __init__(self, ema_fast=7, ema_slow=21, rsi_period=14):
        self.ema_fast_period = ema_fast
        self.ema_slow_period = ema_slow
        self.rsi_period = rsi_period
        self.trend_detector = TrendDetector()
        self.prev_rsi = None

        # === Exchange 1h və 4h üçün qurulur
        self.exchange = ccxt.gate()
        self.symbol = 'TON/USDT:USDT'

    def get_higher_tf_context(self, symbol):
        try:
            ohlcv_1h = self.exchange.fetch_ohlcv(symbol, timeframe='1h', limit=30)
            ohlcv_4h = self.exchange.fetch_ohlcv(symbol, timeframe='4h', limit=30)

            decision_1h = analyze_technicals(ohlcv_1h)  # "buy", "sell", "hold"
            decision_4h = analyze_technicals(ohlcv_4h)

            return decision_1h, decision_4h
        except Exception as e:
            return "hold", "hold"

    def decide(self, close_prices: list[float], full_candles: list[list]) -> str:
        if len(close_prices) < max(self.ema_slow_period, self.rsi_period) + 1:
            return "NO_ACTION"

        ema_fast = calculate_ema(close_prices, self.ema_fast_period)
        ema_slow = calculate_ema(close_prices, self.ema_slow_period)
        rsi = calculate_rsi(close_prices, self.rsi_period)
        trend = self.trend_detector.detect_trend(close_prices)
        pattern = detect_pattern(full_candles)
        tf_1h, tf_4h = self.get_higher_tf_context(self.symbol)

        decision = "NO_ACTION"

        # === Güclü uyğunluq varsa:
        if trend == "uptrend" and ema_fast > ema_slow and rsi > 50:
            if tf_1h == "buy" and tf_4h != "sell":
                decision = "LONG"
        elif trend == "downtrend" and ema_fast < ema_slow and rsi < 50:
            if tf_1h == "sell" and tf_4h != "buy":
                decision = "SHORT"

        # === Pattern təsdiqi (əlavə gücləndirici siqnal)
        if decision == "LONG" and pattern == "bullish":
            decision = "LONG"
        elif decision == "SHORT" and pattern == "bearish":
            decision = "SHORT"
        elif pattern in ["bullish", "bearish"] and decision == "NO_ACTION":
            decision = "LONG" if pattern == "bullish" else "SHORT"

        # === Ekstremal RSI-lər: STOP et
        if rsi >= 90 or rsi <= 10:
            decision = "NO_ACTION"

        # === RSI dəyişimi yoxdursa, impuls zəifdir → dayan
        if self.prev_rsi is not None:
            delta_rsi = abs(rsi - self.prev_rsi)
            if delta_rsi < 2.5:
                decision = "NO_ACTION"

        self.prev_rsi = rsi
        return decision

    def get_indicators(self, close_prices: list[float]) -> dict:
        return {
            "ema_fast": calculate_ema(close_prices, self.ema_fast_period),
            "ema_slow": calculate_ema(close_prices, self.ema_slow_period),
            "rsi": calculate_rsi(close_prices, self.rsi_period),
        }
# ai/strategy_manager.py

from utils.indicators import calculate_ema, calculate_rsi, is_overbought, is_oversold
from ai.trend_detector import TrendDetector

class StrategyManager:
    def __init__(self, ema_fast=7, ema_slow=21, rsi_period=14):
        self.ema_fast_period = ema_fast
        self.ema_slow_period = ema_slow
        self.rsi_period = rsi_period
        self.trend_detector = TrendDetector()

    def decide(self, close_prices: list[float]) -> str:
        if len(close_prices) < max(self.ema_slow_period, self.rsi_period) + 1:
            return "NO_ACTION"

        ema_fast = calculate_ema(close_prices, self.ema_fast_period)
        ema_slow = calculate_ema(close_prices, self.ema_slow_period)
        rsi = calculate_rsi(close_prices, self.rsi_period)
        trend = self.trend_detector.detect_trend(close_prices)

        if ema_fast > ema_slow and not is_overbought(rsi) and trend == "uptrend":
            return "LONG"
        elif ema_fast < ema_slow and not is_oversold(rsi) and trend == "downtrend":
            return "SHORT"
        else:
            return "NO_ACTION"

    def get_indicators(self, close_prices: list[float]) -> dict:
        return {
            "ema_fast": calculate_ema(close_prices, self.ema_fast_period),
            "ema_slow": calculate_ema(close_prices, self.ema_slow_period),
            "rsi": calculate_rsi(close_prices, self.rsi_period),
        }
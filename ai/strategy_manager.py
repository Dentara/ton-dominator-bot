# ai/strategy_manager.py

from utils.indicators import calculate_ema, calculate_rsi
from ai.trend_detector import TrendDetector

class StrategyManager:
    def __init__(self, ema_fast=7, ema_slow=21, rsi_period=14):
        self.ema_fast_period = ema_fast
        self.ema_slow_period = ema_slow
        self.rsi_period = rsi_period
        self.trend_detector = TrendDetector()
        self.prev_rsi = None

    def decide(self, close_prices: list[float]) -> str:
        if len(close_prices) < max(self.ema_slow_period, self.rsi_period) + 1:
            return "NO_ACTION"

        ema_fast = calculate_ema(close_prices, self.ema_fast_period)
        ema_slow = calculate_ema(close_prices, self.ema_slow_period)
        rsi = calculate_rsi(close_prices, self.rsi_period)
        trend = self.trend_detector.detect_trend(close_prices)

        debug_msg = (
            f"[STRATEGY DEBUG]\n"
            f"EMA7: {ema_fast}, EMA21: {ema_slow}\n"
            f"RSI: {rsi}, Prev RSI: {self.prev_rsi}\n"
            f"Trend: {trend}"
        )
        print(debug_msg)

        # Əlavə Telegram debug mesajı üçün istəyirsənsə buraya göndərə bilərsən
        # send_telegram_message(debug_msg)

        # === RSI Breakout ===
        if self.prev_rsi:
            if self.prev_rsi < 40 and rsi > 45:
                return "LONG"
            if self.prev_rsi > 60 and rsi < 55:
                return "SHORT"

        # === Sadə RSI əsasında siqnallar ===
        if rsi <= 30:
            return "LONG"
        elif rsi >= 70:
            return "SHORT"

        # === EMA + Trend kombinasiya (yumşaldılmış) ===
        if ema_fast > ema_slow and rsi > 50 and trend in ["uptrend", "neutral"]:
            return "LONG"
        elif ema_fast < ema_slow and rsi < 50 and trend in ["downtrend", "neutral"]:
            return "SHORT"

        self.prev_rsi = rsi
        return "NO_ACTION"

    def get_indicators(self, close_prices: list[float]) -> dict:
        return {
            "ema_fast": calculate_ema(close_prices, self.ema_fast_period),
            "ema_slow": calculate_ema(close_prices, self.ema_slow_period),
            "rsi": calculate_rsi(close_prices, self.rsi_period),
        }
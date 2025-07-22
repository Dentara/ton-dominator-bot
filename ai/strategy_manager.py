# ai/strategy_manager.py (test üçün override)

from utils.indicators import calculate_ema, calculate_rsi, is_overbought, is_oversold

class StrategyManager:
    def __init__(self, ema_fast=7, ema_slow=21, rsi_period=14):
        self.ema_fast_period = ema_fast
        self.ema_slow_period = ema_slow
        self.rsi_period = rsi_period

    def decide(self, prices: list[float]) -> str:
        return "LONG"  # 👈 test üçün sabit siqnal verəcək

    def get_indicators(self, prices: list[float]) -> dict:
        return {
            "ema_fast": 0,
            "ema_slow": 0,
            "rsi": 0,
        }

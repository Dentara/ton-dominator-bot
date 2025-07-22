from utils.indicators import calculate_ema, calculate_rsi, is_overbought, is_oversold

class StrategyManager:
    def __init__(self, ema_fast=7, ema_slow=21, rsi_period=14):
        self.ema_fast_period = ema_fast
        self.ema_slow_period = ema_slow
        self.rsi_period = rsi_period

    def decide(self, prices: list[float]) -> str:
        if len(prices) < max(self.ema_slow_period, self.rsi_period) + 1:
            return "NO_ACTION"

        ema_fast = calculate_ema(prices, self.ema_fast_period)
        ema_slow = calculate_ema(prices, self.ema_slow_period)
        rsi = calculate_rsi(prices, self.rsi_period)

        if ema_fast > ema_slow and not is_overbought(rsi):
            return "LONG"
        elif ema_fast < ema_slow and not is_oversold(rsi):
            return "SHORT"
        else:
            return "NO_ACTION"

    def get_indicators(self, prices: list[float]) -> dict:
        return {
            "ema_fast": calculate_ema(prices, self.ema_fast_period),
            "ema_slow": calculate_ema(prices, self.ema_slow_period),
            "rsi": calculate_rsi(prices, self.rsi_period),
        }

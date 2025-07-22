ema_fast = calculate_ema(prices, self.ema_fast_period)
ema_slow = calculate_ema(prices, self.ema_slow_period)
rsi = calculate_rsi(prices, self.rsi_period)

if ema_fast > ema_slow and not is_overbought(rsi):
    return "LONG"
elif ema_fast < ema_slow and not is_oversold(rsi):
    return "SHORT"
else:
    return "NO_ACTION"

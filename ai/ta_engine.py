import talib
import numpy as np

def analyze_technicals(candles):
    closes = [x[4] for x in candles]
    closes_np = np.array(closes)

    rsi = talib.RSI(closes_np, timeperiod=14)[-1]
    ema_short = talib.EMA(closes_np, timeperiod=9)[-1]
    ema_long = talib.EMA(closes_np, timeperiod=21)[-1]

    if rsi < 35 and ema_short > ema_long:
        return "buy"
    elif rsi > 65 and ema_short < ema_long:
        return "sell"
    return "hold"

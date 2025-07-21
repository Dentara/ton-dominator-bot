import talib
import numpy as np

def detect_pattern(candles):
    opens = np.array([x[1] for x in candles])
    highs = np.array([x[2] for x in candles])
    lows = np.array([x[3] for x in candles])
    closes = np.array([x[4] for x in candles])

    hammer = talib.CDLHAMMER(opens, highs, lows, closes)[-1]
    engulfing = talib.CDLENGULFING(opens, highs, lows, closes)[-1]

    if hammer > 0 or engulfing > 0:
        return "bullish"
    elif hammer < 0 or engulfing < 0:
        return "bearish"
    return "neutral"

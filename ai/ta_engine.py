import pandas as pd
import numpy as np

def compute_ema_rsi(candles: list, ema_periods=(20, 50), rsi_period=14):
    """
    CCXT formatinda OHLCV candle siyahısı daxilində:
    [timestamp, open, high, low, close, volume]
    """
    if not candles or len(candles) < max(*ema_periods, rsi_period + 2):
        return None

    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # EMA-lar
    for period in ema_periods:
        df[f'EMA{period}'] = df['close'].ewm(span=period, adjust=False).mean()

    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=rsi_period).mean()
    avg_loss = loss.rolling(window=rsi_period).mean()

    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # EMA slope (EMA20)
    if len(df) >= ema_periods[0] + 2:
        ema_now = df[f'EMA{ema_periods[0]}'].iloc[-1]
        ema_prev = df[f'EMA{ema_periods[0]}'].iloc[-3]
        ema_slope = round((ema_now - ema_prev) / ema_prev * 100, 4) if ema_prev != 0 else 0
    else:
        ema_slope = 0

    # Price spike (son 2 candle)
    close_now = df['close'].iloc[-1]
    close_prev = df['close'].iloc[-2]
    price_spike = abs((close_now - close_prev) / close_prev * 100) >= 0.3

    # Candle pattern (Engulfing)
    prev_open, prev_close = df.iloc[-2][['open', 'close']]
    curr_open, curr_close = df.iloc[-1][['open', 'close']]
    bullish_engulfing = (prev_close < prev_open) and (curr_close > curr_open) and (curr_close > prev_open) and (curr_open < prev_close)
    bearish_engulfing = (prev_close > prev_open) and (curr_close < curr_open) and (curr_close < prev_open) and (curr_open > prev_close)

    latest = df.iloc[-1]

    return {
        "EMA20": round(latest[f'EMA{ema_periods[0]}'], 2),
        "EMA50": round(latest[f'EMA{ema_periods[1]}'], 2),
        "RSI": round(latest['RSI'], 2),
        "EMA_SLOPE": ema_slope,
        "SPIKE": price_spike,
        "BULLISH_ENGULFING": bullish_engulfing,
        "BEARISH_ENGULFING": bearish_engulfing
    }
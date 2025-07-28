import pandas as pd

def compute_ema_rsi(candles: list, ema_periods=(20, 50), rsi_period=14):
    """
    CCXT formatinda OHLCV candle siyahısı daxilində:
    [timestamp, open, high, low, close, volume]
    """
    if not candles or len(candles) < max(*ema_periods, rsi_period):
        return None

    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    for period in ema_periods:
        df[f'EMA{period}'] = df['close'].ewm(span=period, adjust=False).mean()

    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=rsi_period).mean()
    avg_loss = loss.rolling(window=rsi_period).mean()

    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    latest = df.iloc[-1]
    return {
        "EMA20": round(latest[f'EMA20'], 2),
        "EMA50": round(latest[f'EMA50'], 2),
        "RSI": round(latest['RSI'], 2)
    }

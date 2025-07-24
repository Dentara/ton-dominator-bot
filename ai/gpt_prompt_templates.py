def simple_prompt(ema7, ema21, rsi, trend, price):
    return (
        f"EMA7: {ema7}, EMA21: {ema21}, RSI: {rsi}, Trend: {trend}, Qiymət: {price}.\n"
        f"Bu dataya əsasən LONG, SHORT və ya NO_ACTION tövsiyə et. Səbəbi qısa izah et."
    )

def advanced_prompt(ema7, ema21, rsi, trend, price):
    return (
        f"EMA7: {ema7}, EMA21: {ema21}, RSI: {rsi}, Trend: {trend}, Qiymət: {price}.\n"
        f"Yalnız bir cavab ver: LONG, SHORT və ya NO_ACTION. Əlavə heç nə yazma."
    )

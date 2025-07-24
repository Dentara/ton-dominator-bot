def simple_prompt(ema7, ema21, rsi, trend, price):
    return (
        f"EMA7: {ema7}, EMA21: {ema21}, RSI: {rsi}, Trend: {trend}, Qiymət: {price}.\n"
        f"Bu dataya əsasən LONG, SHORT və ya NO_ACTION tövsiyə et. Səbəbi qısa izah et."
    )

def advanced_prompt(ema7, ema21, rsi, trend, price):
    return (
        f"Sən texniki analitik botusan. TON/USDT üçün strategiya tövsiyə et:\n"
        f"- EMA7: {ema7}\n"
        f"- EMA21: {ema21}\n"
        f"- RSI: {rsi}\n"
        f"- Trend: {trend}\n"
        f"- Qiymət: {price}\n\n"
        f"Cavab:\n"
        f"1. Siqnal (LONG/SHORT/NO_ACTION)\n"
        f"2. Qısa izah və tövsiyə"
    )

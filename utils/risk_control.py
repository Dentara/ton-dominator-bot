def adjust_position_size(price, sentiment, strategy, usdt_balance):
    risk_percent = 0.02  # hər əməliyyatda 2% risk
    risk_usdt = usdt_balance * risk_percent

    if sentiment == "bearish" and strategy == "sell":
        risk_usdt *= 1
    elif sentiment == "bullish" and strategy == "buy":
        risk_usdt *= 2.4

    ton_amount = round(risk_usdt / price, 2)
    return max(0.1, ton_amount)

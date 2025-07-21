def adjust_position_size(base_amount, sentiment, strategy):
    if sentiment == "bearish" and strategy == "sell":
        return base_amount * 0.5  # risk azalt
    elif sentiment == "bullish" and strategy == "buy":
        return base_amount * 1.5  # fürsəti dəyərləndir
    else:
        return base_amount

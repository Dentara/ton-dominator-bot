from datetime import datetime
import time

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def execute_trade(exchange, symbol: str, side: str, amount: float) -> dict:
    try:
        log(f"📤 Əməliyyat: {side.upper()} göndərilir → {amount} {symbol}")
        if side == "buy":
            order = exchange.create_market_buy_order(symbol, amount)
        elif side == "sell":
            order = exchange.create_market_sell_order(symbol, amount)
        else:
            log(f"❌ Naməlum əməliyyat növü: {side}")
            return {}
        log(f"✅ Əməliyyat tamamlandı: {side.upper()} {amount} {symbol}")
        return order
    except Exception as e:
        log(f"❗ Əməliyyat xətası: {e}")
        time.sleep(5)
        return {}

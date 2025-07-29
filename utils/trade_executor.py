from datetime import datetime
import time

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def execute_trade(exchange, symbol: str, side: str, notional_usdt: float) -> dict:
    try:
        contract = symbol.replace("/USDT:USDT", "_USDT")
        side_code = 1 if side.lower() == "buy" else 2

        log(f"📤 Əməliyyat göndərilir: {side.upper()} → {notional_usdt} USDT notional on {contract}")

        order = exchange.private_linear_post_orders({
            "contract": contract,
            "size": round(notional_usdt, 2),
            "price": 0,
            "tif": "ioc",
            "side": side_code
        })

        log(f"✅ Əməliyyat tamamlandı: {side.upper()} {notional_usdt} USDT → {contract}")
        return order

    except Exception as e:
        log(f"❗ Əməliyyat xətası: {e}")
        time.sleep(3)
        return {}
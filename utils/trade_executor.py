from datetime import datetime
import time

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def execute_trade(exchange, symbol: str, side: str, amount: float) -> dict:
    try:
        # Dəyəri 0-dan kiçik və ya simvol boşdursa, icra etmə
        if amount <= 0 or not symbol:
            log(f"⚠️ Etibarsız miqdar və ya simvol: {symbol} → {amount}")
            return {}

        # Simvol uyğunlaşdır (Gate.io formatı: TON/USDT:USDT)
        market = exchange.market(symbol)
        market_symbol = market['symbol']

        # Əməliyyat logu
        log(f"📤 Əməliyyat: {side.upper()} → {amount} kontrakt → {market_symbol}")

        # Əmri icra et
        if side.lower() == "buy":
            order = exchange.create_market_buy_order(market_symbol, amount)
        elif side.lower() == "sell":
            order = exchange.create_market_sell_order(market_symbol, amount)
        else:
            log(f"❌ Naməlum əməliyyat növü: {side}")
            return {}

        log(f"✅ Əməliyyat tamamlandı: {side.upper()} {amount} {market_symbol}")
        return order

    except Exception as e:
        log(f"❗ Əməliyyat xətası: {e}")
        time.sleep(3)
        return {}
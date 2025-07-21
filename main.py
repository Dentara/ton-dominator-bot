import os
import ccxt
from datetime import datetime

# === Logger ===
def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

# === API Keys ===
api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")

if not api_key or not api_secret:
    log("❌ API açarları tapılmayıb!")
    exit(1)

# === Exchange Setup ===
try:
    exchange = ccxt.gate({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'perpetual'
        }
    })
    log("✅ Exchange uğurla yaradıldı")
except Exception as e:
    log(f"❌ Exchange yaradılarkən xəta: {e}")
    exit(1)

# === Parametrlər ===
symbol = 'TON/USDT:USDT'
leverage = 3
amount = 1  # test üçün 1 TON

# === Botun əsas funksiyası ===
def run_bot():
    log("🚀 TEST: TON DOMINATOR başladı")

    try:
        exchange.set_leverage(leverage, symbol)
        log(f"✅ Leverage təyin edildi: {leverage}x")
    except Exception as e:
        log(f"❌ Leverage xətası: {e}")

    try:
        price = exchange.fetch_ticker(symbol)['last']
        log(f"📈 TON qiyməti: {price}")

        # Sadə filtrləmə: 3.5-dən yuxarı almayacaq
        if price > 3.5:
            log("🟡 TON qiyməti 3.5-dən yuxarıdır, ALIŞ etmədi.")
            return

        order = exchange.create_market_buy_order(symbol, amount)
        log(f"✅ TEST BUY: {amount} TON at {price}")
    except Exception as e:
        log(f"❗️ ERROR: {e}")

# === Başlat ===
if __name__ == "__main__":
    run_bot()

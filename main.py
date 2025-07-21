import os
import ccxt
import time
from datetime import datetime

# === Logger ===
def log(msg):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {msg}")

# === API Keys ===
api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")

if not api_key or not api_secret:
    log("❌ API açarları tapılmadı!")
    exit(1)

# === Exchange Config ===
try:
    exchange = ccxt.gate({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'perpetual'}
    })
    log("✅ Exchange uğurla yaradıldı")
except Exception as e:
    log(f"❌ Exchange xətası: {e}")
    exit(1)

# === Parametrlər ===
symbol = 'TON/USDT:USDT'
leverage = 3
amount = 1  # TON miqdarı
buy_threshold = 3.5
sell_threshold = 3.8

active_position = None

# === Bot funksiyası ===
def run_bot():
    global active_position

    try:
        exchange.set_leverage(leverage, symbol)
        log(f"✅ Leverage təyin edildi: {leverage}x")
    except Exception as e:
        log(f"⚠️ Leverage xətası: {e}")

    while True:
        try:
            ticker = exchange.fetch_ticker(symbol)
            price = ticker['last']
            log(f"📊 TON Qiyməti: {price} USDT")

            if not active_position and price < buy_threshold:
                order = exchange.create_market_buy_order(symbol, amount)
                log(f"✅ ALIŞ edildi: {amount} TON at {price} USDT")
                active_position = {
                    "side": "long",
                    "entry_price": price
                }

            elif active_position and active_position["side"] == "long" and price > sell_threshold:
                order = exchange.create_market_sell_order(symbol, amount)
                pnl = round((price - active_position["entry_price"]) * amount, 2)
                log(f"✅ SATIŞ edildi: {amount} TON at {price} USDT | 💰 PNL: {pnl} USDT")
                active_position = None

            else:
                log("⏳ Şərtlər uyğun deyil. Gözləyirəm...")

            time.sleep(60)

        except Exception as e:
            log(f"❗️ Dövr daxilində xəta: {e}")
            time.sleep(30)

# === Başlat ===
if __name__ == "__main__":
    run_bot()

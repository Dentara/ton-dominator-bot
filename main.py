import os
import time
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
    log("❌ API açarları tapılmadı!")
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
    log(f"❌ Exchange xətası: {e}")
    exit(1)

# === Parameters ===
symbol = 'TON/USDT:USDT'
leverage = 3
base_amount = 1

# === Bot Core Loop ===
def run_bot():
    log("🚀 TON DOMINATOR başladı (Live mode)")

    try:
        exchange.set_leverage(leverage, symbol)
        log(f"✅ Leverage təyin edildi: {leverage}x")
    except Exception as e:
        log(f"❌ Leverage xətası: {e}")

    while True:
        try:
            ticker = exchange.fetch_ticker(symbol)
            price = ticker['last']
            log(f"💰 Cari TON qiyməti: {price}")

            if price < 3.2:
                order = exchange.create_market_buy_order(symbol, base_amount)
                log(f"✅ BUY {base_amount} TON at {price}")
            elif price > 3.8:
                order = exchange.create_market_sell_order(symbol, base_amount)
                log(f"✅ SELL {base_amount} TON at {price}")
            else:
                log("🟡 Şərt yoxdur, gözləyir...")

            time.sleep(60)  # 1 dəqiqə fasilə

        except Exception as e:
            log(f"❗️ Dövr xətası: {e}")
            time.sleep(30)

# === Entry Point ===
if __name__ == "__main__":
    run_bot()

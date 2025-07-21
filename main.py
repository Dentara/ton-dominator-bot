import os
import ccxt
from utils.logger import log

# === API Açarları ===
api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")

if not api_key or not api_secret:
    log("❌ API açarları tapılmadı!")
    exit(1)

# === Exchange Obyekti ===
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

# === Parametrlər ===
symbol = 'TON/USDT:USDT'
leverage = 3
amount = 1  # test üçün 1 TON al

# === Bot Test Funksiyası ===
def run_bot():
    log("🚀 TEST: TON DOMINATOR başladı")

    try:
        exchange.set_leverage(leverage, symbol)
        log(f"✅ Leverage təyin edildi: {leverage}x")
    except Exception as e:
        log(f"❌ Leverage xətası: {e}")

    try:
        price = exchange.fetch_ticker(symbol)['last']
        log(f"✅ TON qiyməti: {price}")

        # TEST BUY ORDER
        order = exchange.create_market_buy_order(symbol, amount)
        log(f"✅ TEST BUY: {amount} TON at {price}")
    except Exception as e:
        log(f"❗️ ERROR: {e}")

# === Başlat ===
if __name__ == "__main__":
    run_bot()

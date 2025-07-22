import os
import time
import ccxt
from datetime import datetime
from ai.strategy_manager import StrategyManager
from utils.trade_executor import execute_trade

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
price_history = []

strategy = StrategyManager()

# === Bot Core Loop ===
def run_bot():
    log("🚀 GATE PERP BOT başladı (Intelligent mode)")

    try:
        exchange.set_leverage(leverage, symbol)
        log(f"✅ Leverage təyin edildi: {leverage}x")
    except Exception as e:
        log(f"❌ Leverage xətası: {e}")

    while True:
        try:
            ticker = exchange.fetch_ticker(symbol)
            price = ticker['last']
            price_history.append(price)
            if len(price_history) > 100:
                price_history.pop(0)

            log(f"💰 Cari TON qiyməti: {price}")

            decision = strategy.decide(price_history)
            indicators = strategy.get_indicators(price_history)
            log(f"📊 EMA7: {indicators['ema_fast']}, EMA21: {indicators['ema_slow']}, RSI: {indicators['rsi']}, Siqnal: {decision}")

            if decision == "LONG":
                execute_trade(exchange, symbol, "buy", base_amount)
            elif decision == "SHORT":
                execute_trade(exchange, symbol, "sell", base_amount)
            else:
                log("🟡 NO_ACTION: Mövqe açılmadı")

            time.sleep(60)  # 1 dəqiqə fasilə

        except Exception as e:
            log(f"❗️ Dövr xətası: {e}")
            time.sleep(30)

# === Entry Point ===
if __name__ == "__main__":
    run_bot()

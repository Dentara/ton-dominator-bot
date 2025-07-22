import os
import time
import ccxt
from datetime import datetime
from ai.strategy_manager import StrategyManager
from ai.state_tracker import StateTracker
from utils.trade_executor import execute_trade
from utils.risk_control import RiskManager

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

if not api_key or not api_secret:
    log(f"❌ API açarları tapılmadı! API_KEY: {api_key}, API_SECRET: {api_secret}")
    exit(1)

# === Parameters ===
symbol = 'TON/USDT:USDT'
leverage = 3
base_amount = 1
price_history = []

strategy = StrategyManager()
risk_manager = RiskManager()
state_tracker = StateTracker()

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

            balance_info = exchange.fetch_balance({'type': 'contract'})
            usdt_balance = balance_info['total']['USDT']

            if risk_manager.is_risk_limit_exceeded(usdt_balance):
                log("⛔ Risk limiti aşılıb, ticarət dayandırılır")
                break

            decision = strategy.decide(price_history)
            indicators = strategy.get_indicators(price_history)
            log(f"📊 EMA7: {indicators['ema_fast']}, EMA21: {indicators['ema_slow']}, RSI: {indicators['rsi']}, Siqnal: {decision}")

            order = {}
            if decision in ["LONG", "SHORT"] and state_tracker.should_trade(decision):
                side = "buy" if decision == "LONG" else "sell"
                order = execute_trade(exchange, symbol, side, base_amount)
                state_tracker.update_position(decision)
            elif decision == "NO_ACTION":
                log("🟡 NO_ACTION: Mövqe açılmadı")
            else:
                log("🟡 Eyni mövqe mövcuddur, ticarət atlanır")

            if 'info' in order and 'profit' in order['info']:
                pnl = float(order['info']['profit'])
                risk_manager.update_pnl(pnl)

            time.sleep(60)  # 1 dəqiqə fasilə

        except Exception as e:
            log(f"❗️ Dövr xətası: {e}")
            time.sleep(30)

# === Entry Point ===
if __name__ == "__main__":
    run_bot()

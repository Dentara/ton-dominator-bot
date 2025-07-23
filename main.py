import os
import time
import ccxt
from datetime import datetime
from ai.strategy_manager import StrategyManager
from ai.state_tracker import StateTracker
from utils.trade_executor import execute_trade
from utils.risk_control import RiskManager
from utils.telegram_notifier import send_telegram_message

# === Logger ===
def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {msg}"
    print(line)
    send_telegram_message(line)

log("🔄 BOT FAYLI BAŞLADI")

# === API Keys ===
api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")

if not api_key or not api_secret:
    log(f"❌ API açarları tapılmadı! API_KEY: {api_key}, API_SECRET: {api_secret}")
    exit(1)

# === Exchange Setup ===
try:
    exchange = ccxt.gate({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'swap'  # Futures (perpetual) balans üçün
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

            try:
                balance_info = exchange.fetch_balance({"type": "swap"})
                usdt_balance = balance_info['total'].get('USDT', 0)
                log(f"💳 Futures Balans: {usdt_balance} USDT")
            except Exception as e:
                log(f"❗ Balance oxuma xətası: {e}")
                usdt_balance = 0

            if risk_manager.is_risk_limit_exceeded(usdt_balance):
                log("⛔ Risk limiti aşılıb, ticarət dayandırılır")
                break

            decision = strategy.decide(price_history)
            indicators = strategy.get_indicators(price_history)

            message = (
                f"📊 <b>TON ANALİZ</b>\n"
                f"EMA7: {indicators['ema_fast']}\n"
                f"EMA21: {indicators['ema_slow']}\n"
                f"RSI: {indicators['rsi']}\n"
                f"📌 Siqnal: <b>{decision}</b>"
            )
            send_telegram_message(message)

            order = {}
            if decision in ["LONG", "SHORT"] and state_tracker.should_trade(decision):
                side = "buy" if decision == "LONG" else "sell"
                order = execute_trade(exchange, symbol, side, base_amount)
                state_tracker.update_position(decision)
                log(f"📌 Mövqe yeniləndi: {decision}")
            elif decision == "NO_ACTION":
                log("🟡 NO_ACTION: Mövqe açılmadı")
            else:
                log("🟡 Eyni mövqe mövcuddur, ticarət atlanır")

            if 'info' in order and 'profit' in order['info']:
                pnl = float(order['info']['profit'])
                risk_manager.update_pnl(pnl)

            time.sleep(60)

        except Exception as e:
            log(f"❗️ Dövr xətası: {e}")
            time.sleep(30)

# === Entry Point ===
run_bot()
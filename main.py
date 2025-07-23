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
            'defaultType': 'swap'
        }
    })
    log("✅ Exchange uğurla yaradıldı")
except Exception as e:
    log(f"❌ Exchange xətası: {e}")
    exit(1)

# === Parameters ===
symbol = 'TON/USDT:USDT'
leverage = 3
strategy = StrategyManager()
risk_manager = RiskManager()
state_tracker = StateTracker()

# === Bot Core Loop ===
def run_bot():
    log("🚀 GATE PERP BOT başladı (Trend + Candle + Cooldown)")

    try:
        exchange.set_leverage(leverage, symbol)
        log(f"✅ Leverage təyin edildi: {leverage}x")
    except Exception as e:
        log(f"❌ Leverage xətası: {e}")

    last_candle_time = None

    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=30)
            last_candle = ohlcv[-1]
            candle_time = last_candle[0]
            close_prices = [c[4] for c in ohlcv]
            current_price = close_prices[-1]

            if candle_time == last_candle_time:
                time.sleep(5)
                continue

            last_candle_time = candle_time
            log(f"🕐 Yeni 1 dəqiqəlik candle gəldi | Qiymət: {current_price}")

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

            decision = strategy.decide(close_prices)
            indicators = strategy.get_indicators(close_prices)

            message = (
                f"📊 <b>TON ANALİZ</b>\n"
                f"EMA7: {indicators['ema_fast']}\n"
                f"EMA21: {indicators['ema_slow']}\n"
                f"RSI: {indicators['rsi']}\n"
                f"📌 Siqnal: <b>{decision}</b>\n"
                f"Mövcud Mövqe: {state_tracker.get_position()}"
            )
            send_telegram_message(message)

            amount = max(round((usdt_balance * 0.1) / current_price, 2), 2)
            if amount < 0.1:
                log("⚠️ Balans çox aşağıdır, əməliyyat atlandı")
                continue

            active_position = state_tracker.get_position()

            if decision == "NO_ACTION":
                log("🟡 NO_ACTION: Mövqe açılmadı")
                continue

            if decision != active_position:
                if state_tracker.can_close_position():
                    side = "buy" if decision == "LONG" else "sell"
                    order = execute_trade(exchange, symbol, side, amount)
                    state_tracker.update_position(decision)
                    log(f"📌 Mövqe dəyişdi və yeniləndi: {decision} | Miqdar: {amount} TON")
                else:
                    log("⏳ Mövqe hələ qorunur, əks siqnal üçün vaxt lazım")
            else:
                # Mövqe eyni istiqamətdədirsə, artır
                side = "buy" if decision == "LONG" else "sell"
                order = execute_trade(exchange, symbol, side, amount)
                state_tracker.update_position(decision)
                log(f"🔁 Mövqe artırıldı: {decision} | Miqdar: {amount} TON")

            if 'info' in order and 'profit' in order['info']:
                pnl = float(order['info']['profit'])
                risk_manager.update_pnl(pnl)

            time.sleep(5)

        except Exception as e:
            log(f"❗️ Dövr xətası: {e}")
            time.sleep(10)

# === Entry Point ===
run_bot()
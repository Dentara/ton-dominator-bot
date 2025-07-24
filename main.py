import os
import time
import ccxt
from datetime import datetime
from ai.strategy_manager import StrategyManager
from ai.state_tracker import StateTracker
from utils.trade_executor import execute_trade
from utils.risk_control import RiskManager
from utils.telegram_notifier import send_telegram_message
from ai.gpt_assistant import ask_gpt

DEBUG_MODE = False  # Debug mesajları göstərmək istəsən True et

# === Logger və Telegram bildirişləri ===
def notify(msg: str, level: str = "info"):
    if level == "debug" and not DEBUG_MODE:
        return
    send_telegram_message(msg)

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {msg}"
    print(line)
    notify(line, level="info")

log("🔄 BOT FAYLI BAŞLADI")

# === API açarları
api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")
if not api_key or not api_secret:
    log("❌ API açarları tapılmadı!")
    exit(1)

# === Exchange konfiqurasiya
try:
    exchange = ccxt.gate({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'swap'}
    })
    log("✅ Exchange uğurla yaradıldı")
except Exception as e:
    log(f"❌ Exchange xətası: {e}")
    exit(1)

# === Parametrlər
symbol = 'TON/USDT:USDT'
leverage = 3
strategy = StrategyManager()
risk_manager = RiskManager()
state_tracker = StateTracker()

# === Bot Dövrü
def run_bot():
    log("🚀 GATE PERP BOT başladı (GPT + Strategy + Cooldown)")

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

            # === Strategiya qərarı
            local_decision = strategy.decide(close_prices)
            indicators = strategy.get_indicators(close_prices)

            # === Xəbər sentimenti (placeholder, növbəti mərhələdə doldurulacaq)
            sentiment = "neutral"  # Bura get_sentiment_score() inteqrasiya ediləcək

            # === GPT qərarı
            gpt_msg = (
                f"1 dəqiqəlik TON/USDT texniki analiz:\n"
                f"Qiymət: {current_price}, EMA7: {indicators['ema_fast']}, EMA21: {indicators['ema_slow']}, RSI: {indicators['rsi']}\n"
                f"Xəbər sentimenti: {sentiment}\n"
                f"Sənin ticarət qərarın nə olar? Qısa şəkildə LONG / SHORT / NO_ACTION cavabı ver."
            )
            gpt_reply = ask_gpt(gpt_msg)

            def parse_gpt_decision(text: str) -> str:
                lowered = text.lower()
                if "long" in lowered:
                    return "LONG"
                elif "short" in lowered:
                    return "SHORT"
                return "NO_ACTION"

            gpt_decision = parse_gpt_decision(gpt_reply)

            # === Final qərar – yalnız hər ikisi eyni olarsa
            if local_decision == gpt_decision and local_decision != "NO_ACTION":
                decision = local_decision
            else:
                decision = "NO_ACTION"

            debug_message = (
                f"🔍 <b>STRATEGIYA DEBUG</b>\n"
                f"EMA7: {indicators['ema_fast']}\n"
                f"EMA21: {indicators['ema_slow']}\n"
                f"RSI: {indicators['rsi']}\n"
                f"📌 Qərar (local): {local_decision}\n"
                f"🧠 GPT Analiz:\n{gpt_reply}\n"
                f"🧩 Qərar (final): <b>{decision}</b>\n"
                f"📎 Cari Mövqe: {state_tracker.get_position()}"
            )
            notify(debug_message, level="debug")

            # === Əməliyyat qərarı
            amount = max(round((usdt_balance * 0.1) / current_price, 2), 1)
            if amount < 0.1:
                notify("⚠️ Balans çox aşağıdır, əməliyyat atlandı", level="info")
                continue

            active_position = state_tracker.get_position()
            order = {}

            if decision == "NO_ACTION":
                notify("🟡 NO_ACTION: Mövqe açılmadı", level="status")
                continue

            if decision != active_position:
                if active_position == "NONE" or state_tracker.can_close_position():
                    side = "buy" if decision == "LONG" else "sell"
                    order = execute_trade(exchange, symbol, side, amount)
                    state_tracker.update_position(decision)
                    notify(f"📌 Mövqe dəyişdi: {decision} | Miqdar: {amount} TON")
                else:
                    notify("⏳ Mövqe qorunur, əks siqnal üçün vaxt lazımdır")
            else:
                side = "buy" if decision == "LONG" else "sell"
                order = execute_trade(exchange, symbol, side, amount)
                state_tracker.update_position(decision)
                notify(f"🔁 Mövqe artırıldı: {decision} | Miqdar: {amount} TON")

            if 'info' in order and 'profit' in order['info']:
                pnl = float(order['info']['profit'])
                risk_manager.update_pnl(pnl)

            time.sleep(5)

        except Exception as e:
            notify(f"❗ Dövr xətası: {e}")
            time.sleep(10)

# === Başlat
run_bot()

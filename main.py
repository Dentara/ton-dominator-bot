import os
import time
import ccxt
from datetime import datetime
from ai.strategy_manager import StrategyManager
from ai.state_tracker import StateTracker
from ai.sentiment_analyzer import get_sentiment_score
from ai.gpt_assistant import ask_gpt
from ai.ta_engine import analyze_technicals
from utils.trade_executor import execute_trade
from utils.risk_control import RiskManager
from utils.telegram_notifier import send_telegram_message

DEBUG_MODE = False

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

# === API
api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")

if not api_key or not api_secret:
    log("❌ API açarları tapılmadı!")
    exit(1)

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

symbol = 'TON/USDT:USDT'
leverage = 3
strategy = StrategyManager()
risk_manager = RiskManager()
state_tracker = StateTracker()

def get_higher_tf_context(symbol):
    try:
        ohlcv_1h = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=30)
        ohlcv_4h = exchange.fetch_ohlcv(symbol, timeframe='4h', limit=30)
        decision_1h = analyze_technicals(ohlcv_1h)
        decision_4h = analyze_technicals(ohlcv_4h)
        return decision_1h, decision_4h
    except:
        return "hold", "hold"

def run_bot():
    log("🚀 GATE PERP BOT başladı (GPT + Strategiya + Sentiment + 1h/4h Trend + Margin)")

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
                        # === Balans hesabla
            try:
                balance_info = exchange.fetch_balance({"type": "swap"})
                total_balance = balance_info['total'].get('USDT', 0) or 0
                free_balance = balance_info['free'].get('USDT', 0) or 0

                positions = exchange.fetch_positions()
                total_other_margin = 0.0
                other_positions_info = ""

                for pos in positions:
                    symbol_ = pos.get('symbol', '')
                    contracts = float(pos.get('contracts') or 0)
                    margin = float(pos.get('initialMargin') or 0)
                    side = pos.get('side') or ''

                    if contracts > 0 and symbol_ != symbol:
                        total_other_margin += margin
                        other_positions_info += f"🔒 {symbol_} | {side} | Miqdar: {contracts} | Margin: {margin}\n"

                usable_balance = free_balance - total_other_margin
                if usable_balance < 0:
                    usable_balance = 0

                log(f"💳 Ümumi Balans: {total_balance} USDT")
                log(f"🧮 Marginə uyğun istifadə oluna bilən balans: {usable_balance} USDT")

                if other_positions_info:
                    log("📌 Bot xarici açıq mövqelər:\n" + other_positions_info)

            except Exception as e:
                log(f"❗ Balance oxuma xətası: {e}")
                usable_balance = 0

            if risk_manager.is_risk_limit_exceeded(usable_balance):
                log("⛔ Risk limiti aşılıb, bot dayandırılır")
                break

            # === Strategiya qərarı
            local_decision = strategy.decide(close_prices, ohlcv)
            indicators = strategy.get_indicators(close_prices)
            sentiment = get_sentiment_score()
            decision_1h, decision_4h = get_higher_tf_context(symbol)
            log(f"🧭 1h qərarı: {decision_1h}, 4h qərarı: {decision_4h}")

            # === GPT
            gpt_msg = (
                f"TON/USDT texniki analiz:\n"
                f"Qiymət: {current_price}, EMA7: {indicators['ema_fast']}, "
                f"EMA21: {indicators['ema_slow']}, RSI: {indicators['rsi']}\n"
                f"Sentiment: {sentiment}\n"
                f"Bu kontekstdə ticarət qərarın nə olar? (LONG / SHORT / NO_ACTION)"
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

            # === Final Qərar Məntiqi
            if gpt_decision == "LONG" and decision_1h != "sell" and decision_4h != "sell":
                decision = "LONG"
            elif gpt_decision == "SHORT" and decision_1h != "buy" and decision_4h != "buy":
                decision = "SHORT"
            elif local_decision == gpt_decision and local_decision != "NO_ACTION":
                decision = local_decision
            else:
                decision = "NO_ACTION"

            notify(
                f"🔍 <b>STRATEGIYA DEBUG</b>\n"
                f"EMA7: {indicators['ema_fast']}, EMA21: {indicators['ema_slow']}\n"
                f"RSI: {indicators['rsi']}, Sentiment: {sentiment}\n"
                f"📌 Local: {local_decision}, GPT: {gpt_decision}\n"
                f"🧭 1h: {decision_1h}, 4h: {decision_4h}\n"
                f"✅ Final: <b>{decision}</b>",
                level="info"
            )

            amount = max(round((usable_balance * 0.1) / current_price, 2), 5)
            if amount < 0.1:
                notify("⚠️ Balans azdır, əməliyyat atlanır")
                continue

            active_position = state_tracker.get_position()
            order = {}

            if decision == "NO_ACTION":
                notify("🟡 NO_ACTION: Heç bir əməliyyat aparılmadı")
                continue

            if decision != active_position:
                if active_position == "NONE" or state_tracker.can_close_position():
                    side = "buy" if decision == "LONG" else "sell"
                    order = execute_trade(exchange, symbol, side, amount)
                    state_tracker.update_position(decision)
                    notify(f"📌 Yeni mövqe açıldı: {decision} | {amount} TON")
                else:
                    notify("⏳ Mövqe qorunur, cooldown aktivdir")
            else:
                side = "buy" if decision == "LONG" else "sell"
                order = execute_trade(exchange, symbol, side, amount)
                state_tracker.update_position(decision)
                notify(f"🔁 Mövqe artırıldı: {decision} | {amount} TON")

            if 'info' in order and 'profit' in order['info']:
                pnl = float(order['info']['profit'])
                risk_manager.update_pnl(pnl)

            time.sleep(5)

        except Exception as e:
            notify(f"❗️ Dövr xətası: {e}")
            time.sleep(10)

# === Başlat
run_bot()
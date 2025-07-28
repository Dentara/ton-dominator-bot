import os
import time
import ccxt
from datetime import datetime
from ai.strategy_manager import StrategyManager
from ai.state_tracker import StateTracker
from ai.sentiment_analyzer import get_sentiment_score
from ai.gpt_assistant import ask_gpt
from ai.ta_engine import analyze_technicals
from ai.pattern_recognizer import detect_pattern
from utils.trade_executor import execute_trade
from utils.risk_control import RiskManager
from utils.telegram_notifier import send_telegram_message

DEBUG_MODE = False

def notify(msg: str, level: str = "info"):
    if level == "debug" and not DEBUG_MODE:
        return
    if level == "silent":
        return
    send_telegram_message(msg)

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

log("🔄 BOT FAYLI BAŞLADI")

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

symbols = ['TON/USDT:USDT', 'CAKE/USDT:USDT', 'GT/USDT:USDT', 'XRP/USDT:USDT']

leverage = 3
strategy = StrategyManager()
risk_manager = RiskManager()
state_tracker = StateTracker()
last_candle_times = {symbol: None for symbol in symbols}

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
    log("🚀 GATE PERP BOT başladı")

    for symbol in symbols:
        try:
            exchange.set_leverage(leverage, symbol)
            log(f"✅ Leverage {symbol} üçün təyin olundu: {leverage}x")
        except Exception as e:
            log(f"❌ Leverage xətası ({symbol}): {e}")

    while True:
        for symbol in symbols:
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=30)
                last_candle = ohlcv[-1]
                candle_time = last_candle[0]
                close_prices = [c[4] for c in ohlcv]
                current_price = close_prices[-1]

                if candle_time == last_candle_times[symbol]:
                    continue
                last_candle_times[symbol] = candle_time

                balance_info = exchange.fetch_balance({"type": "swap"})
                free_balance = balance_info['free'].get('USDT', 0) or 0

                positions = exchange.fetch_positions()
                total_other_margin = 0.0
                active_position = None
                current_contracts = 0
                unrealized_pnl = 0

                for pos in positions:
                    if pos.get("symbol") == symbol:
                        active_position = pos.get("side", "").upper()
                        current_contracts = float(pos.get("contracts") or 0)
                        unrealized_pnl = float(pos.get("unrealizedPnl") or 0)
                    else:
                        margin = float(pos.get("initialMargin") or 0)
                        if margin > 0:
                            total_other_margin += margin

                usable_balance = max(free_balance - total_other_margin, 0)

                if risk_manager.is_risk_limit_exceeded(usable_balance):
                    notify(f"⛔ {symbol} üçün risk limiti aşılıb")
                    continue

                local_decision = strategy.decide(close_prices, ohlcv)
                indicators = strategy.get_indicators(close_prices)
                sentiment = get_sentiment_score()
                pattern = detect_pattern(ohlcv)
                decision_1h, decision_4h = get_higher_tf_context(symbol)

                gpt_msg = (
                    f"{symbol} üçün texniki analiz:\n"
                    f"EMA7: {indicators['ema_fast']}, EMA21: {indicators['ema_slow']}, "
                    f"RSI: {indicators['rsi']}, Pattern: {pattern}\n"
                    f"Sentiment: {sentiment}, 1h: {decision_1h}, 4h: {decision_4h}\n"
                    f"Açıq mövqe: {active_position}, Kontraktlar: {current_contracts}, Balans: {usable_balance:.2f} USDT\n"
                    f"Yalnız bir sözlə cavab ver: LONG, SHORT və ya NO_ACTION."
                )

                gpt_decision = ask_gpt(gpt_msg).strip().upper()
                if gpt_decision not in ["LONG", "SHORT"]:
                    gpt_decision = "NO_ACTION"
                if gpt_decision == "LONG" and decision_1h != "sell" and decision_4h != "sell":
                    decision = "LONG"
                elif gpt_decision == "SHORT" and decision_1h != "buy" and decision_4h != "buy":
                    decision = "SHORT"
                elif local_decision == gpt_decision and local_decision != "NO_ACTION":
                    decision = local_decision
                else:
                    decision = "NO_ACTION"

                notify(f"📍 {symbol} üçün qərar: {decision}", level="info")

                # Əks mövqe varsa → əməliyyatı blokla
                if active_position == "LONG" and decision == "SHORT":
                    notify(f"🚫 {symbol}: Aktiv LONG mövqe var, yeni SHORT bloklandı", level="info")
                    continue
                if active_position == "SHORT" and decision == "LONG":
                    notify(f"🚫 {symbol}: Aktiv SHORT mövqe var, yeni LONG bloklandı", level="info")
                    continue

                # Mövqe çoxdursa, balansın 90%-dən çoxdursa → keç
                if current_contracts * current_price > usable_balance * 0.9:
                    notify(f"⛔ {symbol}: Mövqe artıq balansın 90%-nə bərabərdir. Əməliyyat keçildi.", level="info")
                    continue

                amount = max(round((usable_balance * 0.1) / current_price, 2), 5)
                if amount < 0.1:
                    notify(f"⚠️ {symbol} üçün balans azdır", level="silent")
                    continue

                order = {}
                current_state = state_tracker.get_position(symbol)

                if decision == "NO_ACTION":
                    continue

                if decision != current_state:
                    if current_state == "NONE" or state_tracker.can_close_position(symbol):
                        side = "buy" if decision == "LONG" else "sell"
                        order = execute_trade(exchange, symbol, side, amount)
                        state_tracker.update_position(symbol, decision)
                        notify(f"✅ Yeni mövqe ({symbol}): {decision} | {amount}")
                    else:
                        continue
                else:
                    side = "buy" if decision == "LONG" else "sell"
                    order = execute_trade(exchange, symbol, side, amount)
                    state_tracker.update_position(symbol, decision)
                    notify(f"➕ Mövqe artırıldı ({symbol}): {decision} | {amount}")

                if 'info' in order and 'profit' in order['info']:
                    pnl = float(order['info']['profit'])
                    risk_manager.update_pnl(pnl)

            except Exception as e:
                notify(f"❗ Xəta ({symbol}): {e}")
                time.sleep(10)

        time.sleep(5)

run_bot()
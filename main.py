import os
import time
import ccxt
from datetime import datetime
from ai.gpt_assistant import ask_gpt
from ai.ta_engine import compute_ema_rsi
from utils.trade_executor import execute_trade
from utils.telegram_notifier import send_telegram_message

DEBUG_MODE = False
TOKENS = ["TON/USDT:USDT", "GT/USDT:USDT"]
LEVERAGE = 3
POSITION_STATE = {}
DECISION_MEMORY = {}


def notify(msg: str, level: str = "info"):
    if level == "debug" and not DEBUG_MODE:
        return
    if level == "silent":
        return
    send_telegram_message(msg)


def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")


log("🟢 TON DOMINATOR GPT BOT BAŞLADI")

api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")

if not api_key or not api_secret:
    log("❌ API açarları tapılmadı!")
    send_telegram_message("❌ API açarları tapılmadı!")
    exit(1)

try:
    exchange = ccxt.gate({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'swap'}
    })
    log("✅ Exchange bağlantısı quruldu")
except Exception as e:
    msg = f"❌ Exchange bağlantı xətası: {e}"
    log(msg)
    send_telegram_message(msg)
    exit(1)

for symbol in TOKENS:
    try:
        exchange.set_leverage(LEVERAGE, symbol)
        POSITION_STATE[symbol] = {"last_candle_time": None, "last_position": "NONE"}
        DECISION_MEMORY[symbol] = {"last_decision": "NONE", "timestamp": 0}
        log(f"⚙️ Leverage təyin olundu: {LEVERAGE}x → {symbol}")
    except Exception as e:
        notify(f"❌ Leverage təyini uğursuz: {symbol} | {e}")


def get_trend(symbol, timeframe='1h'):
    try:
        candles = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=30)
        closes = [x[4] for x in candles]
        if closes[-1] > closes[-2] > closes[-3]:
            return "up"
        elif closes[-1] < closes[-2] < closes[-3]:
            return "down"
        else:
            return "sideways"
    except:
        return "unknown"


def run_bot():
    log("🚀 GPT əsaslı çox tokenli futures bot başladı")

    while True:
        for symbol in TOKENS:
            try:
                last_time = POSITION_STATE[symbol]["last_candle_time"]
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=50)
                last_candle = ohlcv[-1]
                candle_time = last_candle[0]
                current_price = last_candle[4]

                if candle_time == last_time:
                    continue
                POSITION_STATE[symbol]["last_candle_time"] = candle_time

                balance_info = exchange.fetch_balance({"type": "swap"})
                free_balance = balance_info['free'].get('USDT', 0) or 0
                positions = exchange.fetch_positions()
                active_position = "NONE"
                contracts = 0
                pnl = 0

                for pos in positions:
                    if pos.get("symbol") == symbol:
                        contracts = float(pos.get("contracts") or 0)
                        pnl = float(pos.get("unrealizedPnl") or 0)
                        side = pos.get("side")
                        if side:
                            active_position = side.upper()

                trend_1h = get_trend(symbol, '1h')
                trend_4h = get_trend(symbol, '4h')

                # EMA/RSI hesabla
                indicators = compute_ema_rsi(ohlcv)
                ema20 = indicators.get("EMA20") if indicators else "?"
                ema50 = indicators.get("EMA50") if indicators else "?"
                rsi = indicators.get("RSI") if indicators else "?"

                # BTC sentiment al
                btc_trend_1h = get_trend("BTC/USDT:USDT", '1h')
                btc_trend_4h = get_trend("BTC/USDT:USDT", '4h')

                # Qısa tarixçə
                last_decision = DECISION_MEMORY[symbol]["last_decision"]
                last_time_diff = int((time.time() - DECISION_MEMORY[symbol]["timestamp"]) / 60)

                gpt_msg = (
                    f"Token: {symbol}\n"
                    f"Balans: {free_balance:.2f} USDT\n"
                    f"Mövqe: {active_position}, Kontraktlar: {contracts}, PnL: {pnl:.2f} USDT\n"
                    f"Trend: 1h={trend_1h}, 4h={trend_4h}\n"
                    f"EMA20={ema20}, EMA50={ema50}, RSI={rsi}\n"
                    f"BTC Trend: 1h={btc_trend_1h}, 4h={btc_trend_4h}\n"
                    f"Son qərar: {last_decision} ({last_time_diff} dəq əvvəl)\n"
                    f"Yalnız bir cavab ver: LONG, SHORT və ya NO_ACTION"
                )

                raw_response = ask_gpt(gpt_msg)
                decision = raw_response.strip().upper()
                if decision not in ["LONG", "SHORT"]:
                    decision = "NO_ACTION"

                send_telegram_message(f"📍 {symbol} GPT qərarı: {decision}")

                DECISION_MEMORY[symbol] = {
                    "last_decision": decision,
                    "timestamp": time.time()
                }

                if decision == "NO_ACTION" or decision == active_position:
                    continue

                amount = max(round((free_balance * 0.2) / current_price, 2), 5)
                if amount < 1:
                    continue

                side = "buy" if decision == "LONG" else "sell"
                order = execute_trade(exchange, symbol, side, amount)
                POSITION_STATE[symbol]["last_position"] = decision

                send_telegram_message(f"✅ Yeni mövqe açıldı: {symbol} → {decision} | {amount} miqdar")

            except Exception as e:
                error_msg = f"❌ {symbol} üçün BOT XƏTASI: {str(e)}"
                log(error_msg)
                send_telegram_message(error_msg)

        time.sleep(5)


run_bot()

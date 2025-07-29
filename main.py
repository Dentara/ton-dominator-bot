import os
import time
import ccxt
from datetime import datetime
from ai.gpt_assistant import ask_gpt
from ai.ta_engine import compute_ema_rsi
from utils.telegram_notifier import send_telegram_message

DEBUG_MODE = False
TOKENS = [
    "TON/USDT:USDT",
    "GT/USDT:USDT",
    "XRP/USDT:USDT",
    "CAKE/USDT:USDT",
    "DOGE/USDT:USDT",
    "KAS/USDT:USDT"
]
LEVERAGE = 3
POSITION_STATE = {}
DECISION_MEMORY = {}

CONTRACT_MULTIPLIERS = {
    "TON/USDT:USDT": 0.1,
    "GT/USDT:USDT": 1,
    "XRP/USDT:USDT": 10,
    "CAKE/USDT:USDT": 0.1,
    "DOGE/USDT:USDT": 10,
    "KAS/USDT:USDT": 10
}

def notify(msg: str, level: str = "info"):
    if level == "debug" and not DEBUG_MODE:
        return
    if level == "silent":
        return
    send_telegram_message(msg)

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

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

def run_bot():
    log("🚀 GPT əsaslı CCXT düzəlişli versiya başladı")
    summary = []

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

                indicators = compute_ema_rsi(ohlcv)
                ema20 = indicators.get("EMA20") if indicators else "?"
                ema50 = indicators.get("EMA50") if indicators else "?"
                rsi = indicators.get("RSI") if indicators else "?"

                btc_trend_1h = get_trend("BTC/USDT:USDT", '1h')
                btc_trend_4h = get_trend("BTC/USDT:USDT", '4h')

                gpt_msg = (
                    f"Token: {symbol}\n"
                    f"Balans: {free_balance:.2f} USDT\n"
                    f"Mövqe: {active_position}, Kontraktlar: {contracts}, PnL: {pnl:.2f} USDT\n"
                    f"Trend: 1h={trend_1h}, 4h={trend_4h}\n"
                    f"EMA20={ema20}, EMA50={ema50}, RSI={rsi}\n"
                    f"BTC Trend: 1h={btc_trend_1h}, 4h={btc_trend_4h}\n"
                    f"Yalnız bir cavab ver."
                )

                raw_response = ask_gpt(gpt_msg).strip().upper()

                if "CLOSE" in raw_response:
                    if active_position != "NONE" and contracts > 0:
                        side = "sell" if active_position == "LONG" else "buy"
                        exchange.create_market_order(symbol, side, contracts)
                        POSITION_STATE[symbol]["last_position"] = "NONE"
                        summary.append(f"{symbol} → CLOSE (contracts={contracts})")
                    else:
                        summary.append(f"{symbol} → SKIPPED (mövqe yoxdur)")
                    continue

                if any(d in raw_response for d in ["LONG", "SHORT"]):
                    direction = "LONG" if "LONG" in raw_response else "SHORT"
                    try:
                        usdt_str = ''.join(filter(lambda x: x.isdigit() or x=='.', raw_response))
                        notional = float(usdt_str)
                        multiplier = CONTRACT_MULTIPLIERS.get(symbol, 1)
                        contracts = round((notional / current_price / LEVERAGE) / multiplier)
                    except:
                        summary.append(f"{symbol} → NO_ACTION (amount error)")
                        continue

                    if contracts * current_price * LEVERAGE * multiplier > free_balance:
                        summary.append(f"{symbol} → SKIPPED (low balance)")
                        continue

                    side = "buy" if direction == "LONG" else "sell"
                    exchange.create_market_order(symbol, side, contracts)
                    POSITION_STATE[symbol]["last_position"] = direction
                    summary.append(f"{symbol} → {direction} ({contracts} kontrakt) ≈ {notional} USDT")
                elif active_position != "NONE" and contracts > 0:
                    summary.append(f"{symbol} → NO_ACTION (mövqe açıq: {contracts})")
                else:
                    summary.append(f"{symbol} → NO_ACTION")

            except Exception as e:
                summary.append(f"{symbol} → XƏTA: {str(e)}")

        if summary:
            notify("📊 GPT QƏRARLARI:\n" + "\n".join(summary))
            summary.clear()

        time.sleep(5)

run_bot()
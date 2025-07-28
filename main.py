import os
import time
import ccxt
from datetime import datetime
from ai.gpt_assistant import ask_gpt
from utils.trade_executor import execute_trade
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

log("🟢 TON DOMINATOR GPT BOT BAŞLADI")

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
    log("✅ Exchange bağlantısı quruldu")
except Exception as e:
    log(f"❌ Exchange bağlantı xətası: {e}")
    exit(1)

symbol = "TON/USDT:USDT"
leverage = 3

try:
    exchange.set_leverage(leverage, symbol)
    log(f"⚙️ Leverage təyin olundu: {leverage}x")
except Exception as e:
    log(f"❌ Leverage təyini uğursuz: {e}")

last_candle_time = None
last_position = "NONE"

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
    global last_candle_time, last_position
    log("🚀 GPT əsaslı TON futures bot başladı")

    while True:
        try:
            # Candle məlumatı
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=30)
            last_candle = ohlcv[-1]
            candle_time = last_candle[0]
            current_price = last_candle[4]

            if candle_time == last_candle_time:
                time.sleep(5)
                continue
            last_candle_time = candle_time

            # Balans və mövqe məlumatları
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

            # Trendləri al
            trend_1h = get_trend(symbol, '1h')
            trend_4h = get_trend(symbol, '4h')

            # GPT üçün sorğu qur
            gpt_msg = (
                f"Token: {symbol}\n"
                f"Balans: {free_balance:.2f} USDT\n"
                f"Açıq mövqe: {active_position}, kontraktlar: {contracts}, PnL: {pnl:.2f} USDT\n"
                f"1h trend: {trend_1h}, 4h trend: {trend_4h}\n"
                f"Yalnız bir cavab ver: LONG, SHORT və ya NO_ACTION"
            )

            decision = ask_gpt(gpt_msg).strip().upper()
            if decision not in ["LONG", "SHORT"]:
                decision = "NO_ACTION"

            notify(f"📍 GPT qərarı: {decision}", level="info")

            if decision == "NO_ACTION":
                continue

            if decision == active_position:
                notify(f"⏸️ {symbol}: Mövqe artıq açıqdır – yeni əməliyyat edilmədi", level="debug")
                continue

            amount = max(round((free_balance * 0.2) / current_price, 2), 5)
            if amount < 1:
                notify(f"⚠️ Balans çox azdır ({free_balance:.2f} USDT), əməliyyat dayandırıldı", level="info")
                continue

            side = "buy" if decision == "LONG" else "sell"
            order = execute_trade(exchange, symbol, side, amount)
            last_position = decision
            notify(f"✅ Yeni mövqe açıldı: {decision} | {amount} TON", level="info")

        except Exception as e:
            notify(f"❌ BOT XƏTASI: {e}", level="info")
            time.sleep(10)

        time.sleep(5)

run_bot()

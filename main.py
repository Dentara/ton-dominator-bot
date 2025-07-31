# TON Dominator GPT Bot (Breakout-lar üçün ağıllı MACD override ilə)
import os
import time
import numpy as np
import ccxt
from datetime import datetime
from ai.gpt_assistant import ask_gpt
from ai.ta_engine import compute_ema_rsi
from utils.trade_executor import execute_trade
from utils.telegram_notifier import send_telegram_message

DEBUG_MODE = False
TOKENS = [
    "TON/USDT:USDT", "XRP/USDT:USDT", "CAKE/USDT:USDT", "DOGE/USDT:USDT", "KAS/USDT:USDT"
]
LEVERAGE = 3
POSITION_STATE = {}
TOKEN_SIZES = {
    "TON/USDT:USDT": 1000, "KAS/USDT:USDT": 40,
    "XRP/USDT:USDT": 10, "CAKE/USDT:USDT": 500, "DOGE/USDT:USDT": 80
}

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def notify(msg: str, level: str = "info"):
    if level == "debug" and not DEBUG_MODE:
        return
    if level == "silent":
        return
    send_telegram_message(msg)

def get_trend(symbol, timeframe='1h'):
    try:
        candles = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=30)
        closes = [x[4] for x in candles]
        if closes[-1] > closes[-2] > closes[-3]: return "up"
        elif closes[-1] < closes[-2] < closes[-3]: return "down"
        else: return "sideways"
    except: return "unknown"

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
        log(f"⚙️ Leverage təyin olundu: {LEVERAGE}x → {symbol}")
    except Exception as e:
        notify(f"❌ Leverage təyini uğursuz: {symbol} | {e}")

def run_bot():
    summary = []
    while True:
        for symbol in TOKENS:
            try:
                last_time = POSITION_STATE[symbol]["last_candle_time"]
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=50)
                last_candle = ohlcv[-1]
                candle_time = last_candle[0]
                if candle_time == last_time:
                    continue
                POSITION_STATE[symbol]["last_candle_time"] = candle_time

                indicators = compute_ema_rsi(ohlcv)
                if not indicators:
                    summary.append(f"{symbol} → NO_ACTION (yetersiz data)")
                    continue

                ema20 = indicators.get("EMA20")
                ema50 = indicators.get("EMA50")
                rsi = indicators.get("RSI")
                rsi_prev = indicators.get("RSI_PREV")
                slope = indicators.get("EMA_SLOPE")
                spike = indicators.get("SPIKE")
                pattern_long = indicators.get("BULLISH_ENGULFING")
                pattern_short = indicators.get("BEARISH_ENGULFING")
                macd = indicators.get("MACD")
                signal = indicators.get("MACD_SIGNAL")
                hist = indicators.get("MACD_HIST")
                ema_spread = abs(ema20 - ema50) / ema50 * 100 if ema50 else 0

                trend_1h = get_trend(symbol, '1h')
                trend_4h = get_trend(symbol, '4h')
                trend_5m = get_trend(symbol, '5m')
                btc_trend_1h = get_trend("BTC/USDT:USDT", '1h')
                btc_trend_4h = get_trend("BTC/USDT:USDT", '4h')

                balance_info = exchange.fetch_balance({"type": "swap"})
                free_balance = balance_info['free'].get('USDT', 0) or 0
                positions = exchange.fetch_positions()
                active_position, contracts, pnl = "NONE", 0, 0
                for pos in positions:
                    if pos.get("symbol") == symbol:
                        contracts = float(pos.get("contracts") or 0)
                        pnl = float(pos.get("unrealizedPnl") or 0)
                        side = pos.get("side")
                        if side:
                            active_position = side.upper()

                gpt_msg = (
                    f"Token: {symbol}\n"
                    f"Balans: {free_balance:.2f} USDT\n"
                    f"Mövqe: {active_position}, Kontraktlar: {contracts}, PnL: {pnl:.2f} USDT\n"
                    f"Trend: 1h={trend_1h}, 4h={trend_4h}, 5m={trend_5m}\n"
                    f"EMA20={ema20}, EMA50={ema50}, RSI={rsi}\n"
                    f"MACD={macd}, SIGNAL={signal}, HIST={hist}\n"
                    f"BTC Trend: 1h={btc_trend_1h}, 4h={btc_trend_4h}\n"
                    f"Slope={slope}, Spike={spike}, Pattern: Bullish={pattern_long}, Bearish={pattern_short}\n"
                    f"Yalnız bir cavab ver: LONG, SHORT və ya NO_ACTION"
                )

                decision_text = ask_gpt(gpt_msg).strip().upper()
                if decision_text not in {"LONG", "SHORT", "NO_ACTION"}:
                    summary.append(f"{symbol} → GPT XƏTASI: qərar tanınmadı → {decision_text}")
                    continue

                # Yeni ağıllı MACD filtri: sadəcə zəif histogram varsa, amma impuls yoxdursa blokla
                if hist is not None and abs(hist) < 0.05:
                    if not spike and not pattern_long and slope < 0.03:
                        summary.append(f"{symbol} → NO_ACTION (MACD zəif + impuls da zəifdir)")
                        continue

                if decision_text == "LONG" and rsi_prev and rsi < rsi_prev and ema_spread < 0.05 and hist < 0.03:
                    summary.append(f"{symbol} → NO_ACTION (trend bitir, zəif siqnallar)")
                    continue

                if decision_text == "SHORT" and rsi_prev and rsi > rsi_prev and ema_spread < 0.05 and hist < 0.03:
                    summary.append(f"{symbol} → NO_ACTION (trend bitir, zəif düşüş)")
                    continue

                if ema_spread < 0.03 and (48 <= rsi <= 52):
                    summary.append(f"{symbol} → NO_ACTION (weak trend)")
                    continue

                if (decision_text == "LONG" and trend_5m != "up") or (decision_text == "SHORT" and trend_5m != "down"):
                    summary.append(f"{symbol} → NO_ACTION (5m uyğunsuz)")
                    continue

                amount = TOKEN_SIZES.get(symbol, 0)
                if amount < 1:
                    summary.append(f"{symbol} → SKIPPED (no amount)")
                    continue

                side = "buy" if decision_text == "LONG" else "sell"
                contract_symbol = symbol.replace("/USDT:USDT", "_USDT")
                order = execute_trade(exchange, contract_symbol, side, amount)
                POSITION_STATE[symbol]["last_position"] = decision_text
                summary.append(f"{symbol} → {decision_text} ({amount})")

            except Exception as e:
                summary.append(f"{symbol} → XƏTA: {str(e)}")

        if summary:
            notify("📊 GPT QƏRARLARI:\n" + "\n".join(summary))
            summary.clear()

        time.sleep(5)

run_bot()
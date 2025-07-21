import os
import time
import ccxt
import numpy as np
from datetime import datetime

def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")

if not api_key or not api_secret:
    log("❌ API tapılmadı!")
    exit(1)

symbol = 'TON/USDT:USDT'
leverage = 3
initial_balance = 1000
min_amount = 0.1
active_position = None

try:
    exchange = ccxt.gate({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'perpetual'}
    })
    log("✅ Exchange yaradıldı")
except Exception as e:
    log(f"❌ Exchange xətası: {e}")
    exit(1)

def calculate_rsi(closes, period=14):
    deltas = np.diff(closes)
    seed = deltas[:period]
    up = seed[seed > 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    return round(100 - (100 / (1 + rs)), 2)

def calculate_ema(closes, period):
    k = 2 / (period + 1)
    ema = [closes[0]]
    for price in closes[1:]:
        ema.append(price * k + ema[-1] * (1 - k))
    return round(ema[-1], 4)

def analyze_technicals(candles):
    closes = np.array([x[4] for x in candles])
    if len(closes) < 21:
        return "hold"
    rsi = calculate_rsi(closes)
    ema9 = calculate_ema(closes, 9)
    ema21 = calculate_ema(closes, 21)
    log(f"📈 RSI: {rsi}, EMA9: {ema9}, EMA21: {ema21}")
    if rsi < 50 and ema9 > ema21:
        return "buy"
    elif rsi > 50 and ema9 < ema21:
        return "sell"
    return "hold"

def place_order(side, amount, price):
    try:
        amount = max(amount, 0.1)
        if side == "buy":
            exchange.create_market_buy_order(symbol, amount)
        else:
            exchange.create_market_sell_order(symbol, amount)
        log(f"✅ ORDER: {side.upper()} {amount} TON at {price}")
        return True
    except Exception as e:
        log(f"❌ ORDER error: {e}")
        return False

def run_bot():
    global active_position
    log("🚀 TON DOMINATOR AI PRO başladı")
    try:
        exchange.set_leverage(leverage, symbol)
        log(f"✅ Leverage təyin olundu: {leverage}x")
    except Exception as e:
        log(f"❌ Leverage xətası: {e}")

    while True:
        try:
            ticker = exchange.fetch_ticker(symbol)
            price = ticker.get("last")
            if not price:
                log("❌ TON qiyməti tapılmadı!")
                continue

            candles = exchange.fetch_ohlcv(symbol, '1m', limit=100)
            strategy = analyze_technicals(candles)
            balance = exchange.fetch_balance()
            usdt = balance['total'].get('USDT', initial_balance)
            amount = round(max(usdt * 0.02 / price, 0.1), 2)

            log(f"📊 STRATEGY: {strategy} | PRICE: {price} | AMOUNT: {amount} | BAL: {usdt}")

            if strategy == "buy" and not active_position:
                if place_order("buy", amount, price):
                    active_position = {"side": "long", "entry": price, "amount": amount}
            elif strategy == "sell" and not active_position:
                if place_order("sell", amount, price):
                    active_position = {"side": "short", "entry": price, "amount": amount}
            elif active_position:
                entry = active_position['entry']
                side = active_position['side']
                amt = active_position['amount']

                # TP və SL
                tp = entry * 1.005 if side == "long" else entry * 0.995
                sl = entry * 0.993 if side == "long" else entry * 1.007

                if (side == "long" and (price >= tp or price <= sl)) or \
                   (side == "short" and (price <= tp or price >= sl)):
                    act = "sell" if side == "long" else "buy"
                    if place_order(act, amt, price):
                        pnl = round((price - entry) * amt, 2) if side == "long" else round((entry - price) * amt, 2)
                        log(f"💰 Mövqe bağlandı. PNL: {pnl} USDT")
                        active_position = None

            time.sleep(60)

        except Exception as e:
            log(f"❗️ Dövr xətası: {e}")
            time.sleep(30)

if __name__ == "__main__":
    run_bot()

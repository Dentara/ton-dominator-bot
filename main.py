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
    log("❌ API açarları tapılmayıb.")
    exit(1)

try:
    exchange = ccxt.gate({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'perpetual'
        }
    })
    log("✅ Exchange quruldu.")
except Exception as e:
    log(f"❌ Exchange xətası: {e}")
    exit(1)

symbol = 'TON/USDT:USDT'
leverage = 3
initial_balance = 1000
min_amount = 0.1
active_position = None

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
    ema_short = calculate_ema(closes, 9)
    ema_long = calculate_ema(closes, 21)
    log(f"📈 RSI: {rsi}, EMA9: {ema_short}, EMA21: {ema_long}")
    if rsi < 50 and ema_short > ema_long:
        return "buy"
    elif rsi > 50 and ema_short < ema_long:
        return "sell"
    return "hold"

def place_order(type, amount, price):
    try:
        if amount < 0.1:
            amount = 0.1
        if type == "buy":
            exchange.create_market_buy_order(symbol, amount)
        else:
            exchange.create_market_sell_order(symbol, amount)
        log(f"✅ ORDER: {type.upper()} {amount} TON at {price}")
        return True
    except Exception as e:
        log(f"❌ ORDER ERROR: {e}")
        return False

def calculate_pnl(entry_price, exit_price, amount, side):
    if side == "long":
        return round((exit_price - entry_price) * amount, 2)
    else:
        return round((entry_price - exit_price) * amount, 2)

def run_bot():
    global active_position

    log("🚀 TON DOMINATOR AI PRO başladı.")

    try:
        exchange.set_leverage(leverage, symbol)
        log(f"✅ Leverage: {leverage}x")
    except Exception as e:
        log(f"⚠️ Leverage təyini xətası: {e}")

    while True:
        try:
            ticker = exchange.fetch_ticker(symbol)
            price = ticker['last']
            candles = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=100)

            strategy = analyze_technicals(candles)

            balance = exchange.fetch_balance()
            usdt_balance = balance['total'].get('USDT', initial_balance)
            risk_usdt = usdt_balance * 0.02
            amount = round(max(risk_usdt / price, min_amount), 2)

            log(f"📊 Strategy: {strategy} | Price: {price} | Amount: {amount} | Balance: {usdt_balance}")

            if strategy == "buy" and not active_position:
                if place_order("buy", amount, price):
                    active_position = {"side": "long", "entry": price, "amount": amount}

            elif strategy == "sell" and not active_position:
                if place_order("sell", amount, price):
                    active_position = {"side": "short", "entry": price, "amount": amount}

            elif active_position:
                side = active_position['side']
                entry = active_position['entry']
                amt = active_position['amount']

                tp_hit = price >= entry * 1.005 if side == "long" else price <= entry * 0.995
                sl_hit = price <= entry * 0.993 if side == "long" else price >= entry * 1.007

                if tp_hit or sl_hit:
                    action = "sell" if side == "long" else "buy"
                    if place_order(action, amt, price):
                        pnl = calculate_pnl(entry, price, amt, side)
                        log(f"💰 Mövqe bağlandı. PNL: {pnl} USDT")
                        active_position = None

            time.sleep(60)

        except Exception as e:
            log(f"❗️ Dövr xətası: {e}")
            time.sleep(30)

if __name__ == "__main__":
    run_bot()

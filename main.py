import os
import time
import ccxt
import numpy as np
import requests
from datetime import datetime

# ===== Logger sistemi =====
def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

# ===== API açarlarını oxu =====
api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")

if not api_key or not api_secret:
    log("❌ API açarları tapılmadı! Render Environment Variables daxil edilməyib.")
    exit(1)

# ===== Exchange yarat =====
try:
    exchange = ccxt.gate({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'perpetual'
        }
    })
    log("✅ Exchange obyekti uğurla yaradıldı")
except Exception as e:
    log(f"❌ Exchange yaradılarkən xəta: {e}")
    exit(1)

# ===== Parametrlər =====
symbol = 'TON/USDT:USDT'
leverage = 3
initial_balance = 1000  # kapital
min_amount = 0.1
max_risk_percent = 0.02  # 2% risk per trade

# ===== Texniki analiz: RSI və EMA =====
def calculate_rsi(closes, period=14):
    deltas = np.diff(closes)
    seed = deltas[:period]
    up = seed[seed > 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

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

    if rsi < 35 and ema_short > ema_long:
        return "buy"
    elif rsi > 65 and ema_short < ema_long:
        return "sell"
    return "hold"

# ===== Candle pattern tanıma =====
def detect_pattern(candles):
    opens = np.array([x[1] for x in candles])
    highs = np.array([x[2] for x in candles])
    lows = np.array([x[3] for x in candles])
    closes = np.array([x[4] for x in candles])

    o = opens[-1]
    c = closes[-1]
    h = highs[-1]
    l = lows[-1]

    body = abs(c - o)
    candle_range = h - l
    if candle_range == 0:
        return "neutral"

    lower_shadow = min(c, o) - l
    upper_shadow = h - max(c, o)

    if body / candle_range < 0.3 and lower_shadow / candle_range > 0.5:
        return "bullish"
    elif body / candle_range < 0.3 and upper_shadow / candle_range > 0.5:
        return "bearish"
    else:
        return "neutral"

# ===== Strategiya birləşdirici =====
def determine_strategy(ta, pattern):
    if ta == "buy" and pattern == "bullish":
        return "buy"
    elif ta == "sell" and pattern == "bearish":
        return "sell"
    return "hold"

# ===== Sentiment analiz (simulyasiya) =====
def get_sentiment_score():
    try:
        # Burada real API inteqrasiya edilə bilər (məsələn: LunarCrush, GNews və s.)
        url = "https://cryptopanic.com/api/v1/posts/?auth_token=demo&currencies=TON"
        response = requests.get(url)
        data = response.json()
        positive = sum(1 for post in data['results'] if post['vote']['positive'] > 0)
        negative = sum(1 for post in data['results'] if post['vote']['negative'] > 0)
        score = positive - negative
        if score >= 2:
            return "bullish"
        elif score <= -2:
            return "bearish"
        else:
            return "neutral"
    except Exception as e:
        return "neutral"
# ===== Mövqe ölçüsünü balans əsasında təyin et =====
def adjust_position_size(price, sentiment, strategy, usdt_balance):
    risk_percent = 0.02  # hər əməliyyatda 2% risk
    risk_usdt = usdt_balance * risk_percent

    # Reaksiya sentimentə görə dəyişir
    if sentiment == "bearish" and strategy == "sell":
        risk_usdt *= 0.6
    elif sentiment == "bullish" and strategy == "buy":
        risk_usdt *= 1.4

    # TON olaraq miqdarı qaytar
    ton_amount = round(risk_usdt / price, 2)
    return max(min_amount, ton_amount)

# ===== Trade logu yadda saxla =====
trade_log = []
active_position = None  # Mövcud açıq mövqe
pnl_history = []

def record_trade(action, amount, price, pnl=None):
    trade = {
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'action': action,
        'amount': amount,
        'price': price,
        'pnl': pnl
    }
    trade_log.append(trade)
    if pnl is not None:
        pnl_history.append(pnl)
    log(f"📘 Trade Log: {trade}")

# ===== PNL hesabla =====
def calculate_pnl(entry_price, exit_price, amount):
    return round((exit_price - entry_price) * amount, 2)

# ===== Order yerinə yetir =====
def place_order(type, amount, price):
    try:
        if type == "buy":
            result = exchange.create_market_buy_order(symbol, amount)
        else:
            result = exchange.create_market_sell_order(symbol, amount)
        log(f"✅ Order uğurludur: {type.upper()} {amount} TON at {price}")
        return result
    except Exception as e:
        log(f"❌ Order error: {e}")
        return None

# ===== Bot əsas dövrü =====
def run_bot():
    global active_position

    log("🚀 TON DOMINATOR AI PRO işə başladı")

    try:
        exchange.set_leverage(leverage, symbol)
        log(f"✅ Leverage təyin edildi: {leverage}x")
    except Exception as e:
        log(f"⚠️ Leverage error: {e}")

    while True:
        try:
            # Bazar məlumatları
            ticker = exchange.fetch_ticker(symbol)
            price = ticker['last']
            candles = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=100)

            ta_signal = analyze_technicals(candles)
            pattern_signal = detect_pattern(candles)
            strategy = determine_strategy(ta_signal, pattern_signal)
            sentiment = get_sentiment_score()

            # Balansı oxu
            balance = exchange.fetch_balance()
            usdt_balance = balance['total'].get('USDT', initial_balance)

            # Mövqe ölçüsünü hesabla
            amount = adjust_position_size(price, sentiment, strategy, usdt_balance)

            log(f"📊 [S]: {strategy} | [Sent]: {sentiment} | [P]: {price} | [A]: {amount} | [Bal]: {usdt_balance}")

            if strategy == "buy" and not active_position:
                result = place_order("buy", amount, price)
                if result:
                    active_position = {
                        "side": "long",
                        "entry": price,
                        "amount": amount
                    }
                    record_trade("BUY", amount, price)

            elif strategy == "sell" and not active_position:
                result = place_order("sell", amount, price)
                if result:
                    active_position = {
                        "side": "short",
                        "entry": price,
                        "amount": amount
                    }
                    record_trade("SELL", amount, price)

            # Mövqe varsa, çıxış şərtlərini qiymətləndir
            elif active_position:
                entry = active_position['entry']
                amt = active_position['amount']
                side = active_position['side']

                # Çıxış şərtləri
                if (side == "long" and price >= entry * 1.01) or (side == "short" and price <= entry * 0.99):
                    result = place_order("sell" if side == "long" else "buy", amt, price)
                    if result:
                        pnl = calculate_pnl(entry, price, amt) if side == "long" else calculate_pnl(price, entry, amt)
                        record_trade("CLOSE", amt, price, pnl)
                        active_position = None
                        log(f"💰 Mövqe bağlandı. PNL: {pnl}")

            time.sleep(60)

        except Exception as e:
            log(f"❗️ Dövr xətası: {e}")
            time.sleep(30)

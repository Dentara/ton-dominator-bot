import os
import time
import ccxt
from ai.ta_engine import analyze_technicals
from ai.pattern_recognizer import detect_pattern
from ai.strategy_shift import determine_strategy
from ai.sentiment_analyzer import get_sentiment_score
from utils.logger import log
from utils.risk_control import adjust_position_size

# === Environment Variables ===
api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")

if not api_key or not api_secret:
    log("❌ API açarları tapılmadı! Render Environment Variables daxil edilməyib.")
    exit(1)

# === Exchange Object ===
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

# === Symbol & Parameters ===
symbol = 'TON/USDT:USDT'
leverage = 3
base_amount = 1

# === Market Check ===
def check_market():
    try:
        log("📦 Marketləri yükləyirəm...")
        markets = exchange.load_markets()
        log(f"✅ Ümumi market sayı: {len(markets)}")

        found = False
        for s in markets:
            if 'TON' in s:
                log(f"🔍 Mövcud TON bazarı: {s}")
            if s == symbol:
                found = True

        if not found:
            log(f"❌ '{symbol}' mövcud deyil! Düzgün symbol təyin edilməlidir.")
            exit(1)
        else:
            log(f"✅ '{symbol}' mövcuddur və istifadə ediləcək.")
    except Exception as e:
        log(f"❌ Market yoxlanışı zamanı xəta: {e}")
        exit(1)

# === Bot Core ===
def run_bot():
    log("🚀 TON DOMINATOR AI v2.0 başladı")

    try:
        exchange.set_leverage(leverage, symbol)
        log(f"✅ Leverage təyin edildi: {leverage}x")
    except Exception as e:
        log(f"⚠️ Leverage təyini uğursuz: {e}")

    while True:
        try:
            log("📥 Ticker çəkilir...")
            ticker = exchange.fetch_ticker(symbol)
            price = ticker['last']
            log(f"✅ TON qiyməti: {price}")

            log("📥 Candle çəkilir...")
            candles = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=100)
            log(f"✅ Candle sayı: {len(candles)}")

            ta_signal = analyze_technicals(candles)
            pattern_signal = detect_pattern(candles)
            strategy = determine_strategy(ta_signal, pattern_signal)
            sentiment = get_sentiment_score()
            amount = adjust_position_size(base_amount, sentiment, strategy)

            log(f"📊 STRATEGIYA → Price: {price} | Signal: {strategy} | Sentiment: {sentiment} | Amount: {amount}")

            if strategy == "buy":
                exchange.create_market_buy_order(symbol, amount)
                log(f"✅ BUY əmri icra olundu: {amount} TON at {price}")
            elif strategy == "sell":
                exchange.create_market_sell_order(symbol, amount)
                log(f"✅ SELL əmri icra olundu: {amount} TON at {price}")
            else:
                log("🟡 HOLD – Şərtlər əməliyyat üçün uyğun deyil")

            time.sleep(60)

        except Exception as e:
            log(f"❗️ Dövr daxilində xəta: {e}")
            time.sleep(30)

# === Başlat ===
if __name__ == "__main__":
    check_market()
    run_bot()

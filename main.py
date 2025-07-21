import os
import time
import ccxt
from ai.ta_engine import analyze_technicals
from ai.pattern_recognizer import detect_pattern
from ai.strategy_shift import determine_strategy
from ai.sentiment_analyzer import get_sentiment_score
from utils.logger import log
from utils.risk_control import adjust_position_size

# API açarlarını oxu
api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")

if not api_key or not api_secret:
    log("❌ API açarları tapılmadı! Environment Variables düzgün daxil olunmayıb.")
    exit(1)

# Exchange qur
try:
    exchange = ccxt.gate({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'perpetual'}
    })
except Exception as e:
    log(f"❌ exchange init xətası: {e}")
    exit(1)

symbol = 'TON/USDT:USDT'
leverage = 3
base_amount = 1

def run_bot():
    log("✅ TON DOMINATOR AI v2.0 başladı...")

    try:
        exchange.set_leverage(leverage, symbol)
        log(f"✅ Leverage təyin olundu: {leverage}x")
    except Exception as e:
        log(f"❌ Leverage qoyulmadı: {e}")

    while True:
        try:
            ticker = exchange.fetch_ticker(symbol)
            candles = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=100)
            price = ticker['last']

            ta_signal = analyze_technicals(candles)
            pattern_signal = detect_pattern(candles)
            strategy = determine_strategy(ta_signal, pattern_signal)
            sentiment = get_sentiment_score()
            amount = adjust_position_size(base_amount, sentiment, strategy)

            log(f"📊 TON Price: {price} | Strategy: {strategy} | Sentiment: {sentiment} | Amount: {amount}")

            if strategy == "buy":
                exchange.create_market_buy_order(symbol, amount)
                log(f"✅ BUY {amount:.2f} TON at {price}")
            elif strategy == "sell":
                exchange.create_market_sell_order(symbol, amount)
                log(f"✅ SELL {amount:.2f} TON at {price}")
            else:
                log("🟡 HOLD – Şərtlər uyğun deyil")

            time.sleep(60)

        except Exception as e:
            log(f"❌ İşləmə zamanı xəta: {e}")
            time.sleep(30)

if __name__ == "__main__":
    run_bot()

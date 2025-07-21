import os
import time
import ccxt
from ai.ta_engine import analyze_technicals
from ai.pattern_recognizer import detect_pattern
from ai.strategy_shift import determine_strategy
from utils.logger import log

api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")

exchange = ccxt.gate({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {'defaultType': 'delivery'}
})

symbol = 'TON/USDT:USDT'
leverage = 3
amount = 1

def run_bot():
    log("TON DOMINATOR AI v2.0 started...")
    exchange.set_leverage(leverage, symbol)
    
    while True:
        try:
            ticker = exchange.fetch_ticker(symbol)
            candles = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=100)
            price = ticker['last']
            
            ta_signal = analyze_technicals(candles)
            pattern_signal = detect_pattern(candles)
            strategy = determine_strategy(ta_signal, pattern_signal)

            log(f"Price: {price} | Strategy: {strategy}")

            if strategy == "buy":
                exchange.create_market_buy_order(symbol, amount)
                log(f"BUY order executed at {price}")
            elif strategy == "sell":
                exchange.create_market_sell_order(symbol, amount)
                log(f"SELL order executed at {price}")
            else:
                log("No action taken.")

            time.sleep(60)

        except Exception as e:
            log(f"Error: {e}")
            time.sleep(15)

if __name__ == "__main__":
    run_bot()

import ccxt
import time
import os

# API açarlarını oxu
api_key = os.getenv("3215690da725d2f6600d68c0b3f94acd")
api_secret = os.getenv("49992db3f25ad79ad37c71588a07f1896868b7fc0ba46e1c79b53ec9317fab49")

# Gate.io futures bazarında işə sal
exchange = ccxt.gate({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

symbol = 'TON/USDT:USDT'
leverage = 3
amount = 1  # 1 TON per trade

# Leverage təyin et
markets = exchange.load_markets()
market = markets[symbol]
exchange.set_leverage(leverage, symbol)

def run_bot():
    print("TON Dominator Bot started...")
    while True:
        ticker = exchange.fetch_ticker(symbol)
        price = ticker['last']
        print(f"CURRENT TON PRICE: {price} USDT")

        balance = exchange.fetch_balance()
        ton_position = balance['total'].get('TON', 0)

        if price < 3.2:
            order = exchange.create_market_buy_order(symbol, amount)
            print(f"Bought {amount} TON at {price}")
        elif price > 3.8 and ton_position > 0:
            order = exchange.create_market_sell_order(symbol, amount)
            print(f"Sold {amount} TON at {price}")
        
        time.sleep(60)  # 1 dəqiqədən bir yoxla

if __name__ == "__main__":
    run_bot()

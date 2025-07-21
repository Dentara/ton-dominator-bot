import ccxt
import time
import os

api_key = os.getenv("GATE_API_KEY")
api_secret = os.getenv("GATE_API_SECRET")

exchange = ccxt.gate({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'delivery',
    }
})

symbol = 'TON/USDT:USDT'
leverage = 3
base_amount = 1  # LOT ölçüsü
lower_price = 3.00
upper_price = 3.80
grid_count = 20

def generate_grid(lower, upper, count):
    step = (upper - lower) / count
    return [round(lower + step * i, 4) for i in range(count + 1)]

def cancel_open_orders():
    try:
        orders = exchange.fetch_open_orders(symbol)
        for order in orders:
            exchange.cancel_order(order['id'], symbol)
    except Exception as e:
        print(f"Cancel error: {e}")

def run_bot():
    print("TON DOMINATOR AI GRID BOT started...")
    exchange.set_leverage(leverage, symbol)
    grids = generate_grid(lower_price, upper_price, grid_count)

    while True:
        try:
            price = exchange.fetch_ticker(symbol)['last']
            print(f"TON price: {price}")

            balance = exchange.fetch_balance()
            ton_bal = balance['total'].get('TON', 0)
            usdt_bal = balance['total'].get('USDT', 0)

            cancel_open_orders()

            for grid_price in grids:
                if price <= grid_price:
                    print(f"Placing LONG buy order at {grid_price}")
                    exchange.create_limit_buy_order(symbol, base_amount, grid_price)
                elif price >= grid_price:
                    print(f"Placing SHORT sell order at {grid_price}")
                    exchange.create_limit_sell_order(symbol, base_amount, grid_price)

            time.sleep(30)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_bot()

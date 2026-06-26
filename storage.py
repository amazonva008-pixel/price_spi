import json
import os

PRICES_FILE = "price.json"

def load_prices():
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                return {}
            except json.JSONDecodeError:
                return {}
    return {}

def save_price(product_name, price):
    prices = load_prices()
    prices[product_name] = price
    with open(PRICES_FILE, 'w') as f:
        json.dump(prices, f, indent=4)

def get_last_price(product_name):
    prices = load_prices()
    return prices.get(product_name, None)



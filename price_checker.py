from requests.packages import target
import re
from storage import get_last_price, save_price, load_prices
import logging

logger = logging.getLogger("price_spi")


def clean_price(raw_price):
    cleaned = re.sub(r"[^\d.]", "", raw_price)
    return float(cleaned)

def check_price(product, current_price_raw):
    name = product['name']


    target = product['target_price']


    current_price = clean_price(current_price_raw)
    last_price = get_last_price(name)

    save_price(name, current_price)

    logger.debug(f"Product: {name} | Current: £{current_price} | Target: £{target} | Last: £{last_price}")

    if current_price < target:
        return "Price Below Target"

    if last_price and current_price < target:
        return "Price Dropped"
    return 'No Alert'





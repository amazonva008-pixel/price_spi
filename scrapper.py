from http.client import responses
from itertools import product

import requests
from bs4 import BeautifulSoup


def fetch_page(url):
    headers = {
        "User_Agent": "Mozilla/5.0 (Windows NT 10.0; Win 64; x64)"
    }
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    return response.text

def parse_price(html):
    soup = BeautifulSoup(html, 'html.parser')
    price_tag = soup.find("p", class_="price_color")

    if price_tag:
        return price_tag.text.strip()
    else:
        return None
if __name__ == '__main__':
    from config_loader import load_config
    from price_checker import check_price

    config = load_config()
    product = config['products'][0]

    url = product['url']
    html = fetch_page(url)
    raw_price = parse_price(html)

    result = check_price(product, raw_price)
    print(f"Alert Status {result}")




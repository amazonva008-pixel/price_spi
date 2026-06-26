import asyncio
import sys
from itertools import product

import aiohttp
from bs4 import BeautifulSoup
from config_loader import load_config
from price_checker import check_price
from logger import setup_logger

# Windows async DNS fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Get our logger - one line gives us logging everywhere
logger = setup_logger()

async def fetch_page_async(session, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientConnectorError:
        logger.error(f"Cannot connect to {url} - check your internet")
        return None
    except aiohttp.ClientResponseError as e:
        logger.error(f"Website returned error {e.status} for {url}")
        return None
    except asyncio.TimeoutError:
        logger.error(f"Timed out waiting for {url}")
        return None

async def parse_price_async(html, product):
    try:
        soup = BeautifulSoup(html, "html.parser")
        price_tag =  soup.find(
            product["price_tag"],
            attrs={"itemprop": product["price_class"]}
        ) or soup.find(

            product["price_tag"],
            class_=product["price_class"]
        )

        if price_tag:
            return price_tag.text.strip()
        logger.warning(f"Price tag not found for {product['name']}")
        return None
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
        return None

async def monitor_product(session, product):
    name = product["name"]
    url = product["url"]

    logger.info(f"Checking: {name}")

    html = await fetch_page_async(session, url)
    if html is None:
        logger.warning(f"Skipping {name} - could not fetch page")
        return

    raw_price = await parse_price_async(html, product)
    if raw_price is None:
        logger.warning(f"Skipping {name} - could not parse price")
        return

    result = check_price(product, raw_price)

    if result == "PRICE_BELOW_TARGET":
        logger.warning(f"ALERT! {name} is below target price!")
    elif result == "PRICE_DROPPED":
        logger.warning(f"ALERT! {name} price has dropped!")
    else:
        logger.info(f"{name} - No alert")

async def main_loop():
    config = load_config()
    interval = config["check_interval"]
    products = config["products"]

    logger.info(f"Price Spy started! Watching {len(products)} products")
    logger.info(f"Checking every {interval} seconds")
    logger.info("=" * 40)

    while True:
        try:
            async with aiohttp.ClientSession() as session:
                tasks = [monitor_product(session, p) for p in products]
                await asyncio.gather(*tasks)

            logger.info(f"Next check in {interval} seconds...")
            await asyncio.sleep(interval)

        except Exception as e:
            logger.critical(f"Main loop crashed: {e}")
            logger.info("Restarting in 60 seconds...")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main_loop())
import json
import os
import re
import time
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from notifier import send_discord_alert
from logger import setup_logger
from storage import get_last_price, save_price

logger: logging.Logger = setup_logger()

def load_config():
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f)
    return {"products": []}

def trim_url(url):
    return url.split("?")[0]

def create_driver():
    options = Options()
    options.add_argument("--headless=new") # The modern headless flag
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox") # CRITICAL for GitHub Actions
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_daraz_price(url):
    driver = create_driver()
    try:
        logger.info(f"Opening chrome for: {url}")
        driver.get(url)

        wait = WebDriverWait(driver, 15)
        price_element = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".pdp-price_size_xl")
            )
        )
        raw_price = price_element.text.strip()
        return raw_price
    except Exception as e:
        logger.error(f"Error Scraping {url}: {e}")
        return None
    finally:
        driver.quit()

def clean_daraz_price(raw_price):
    cleaned = raw_price.replace("Rs.", "").strip()
    cleaned = re.sub(r"[^\d.]", "", cleaned)
    return float(cleaned)

def check_and_notify(product_name, url):
    url = trim_url(url)
    raw_price = scrape_daraz_price(url)
    
    if raw_price is None:
        logger.warning(f"Skipping {product_name} - could not scrape price")
        return

    current_price = clean_daraz_price(raw_price)
    last_price = get_last_price(product_name)
    save_price(product_name, current_price)

    logger.debug(
        f"Product: {product_name} | "
        f"Current: Rs.{current_price} | "
        f"Last: Rs.{last_price}"
    )
    
    if last_price is None:
        logger.info(f"First check for {product_name} - price saved: Rs.{current_price}")
        return

    if current_price < last_price:
        diff = last_price - current_price
        logger.warning(f"Price DROPPED! {product_name} | Rs.{last_price} -> Rs. {current_price}")
        send_discord_alert(product_name, last_price, current_price, "dropped")
    elif current_price > last_price:
        diff = current_price - last_price
        logger.warning(f"Price Increased! {product_name} | Rs.{last_price} -> Rs. {current_price}")
        send_discord_alert(product_name, last_price, current_price, "increased")
    else:
        logger.info(f"No change for {product_name} - RS. {current_price}")


if __name__ == "__main__":
    logger.info("Price Spy Engine Triggered by Automation...")

    # 1. Load the config file once
    config = load_config()
    products = config.get("products", [])

    # 2. Loop through all products once
    for product in products:
        if "daraz.pk" in product["url"]:
            logger.info(f"Checking: {product['name']}")
            check_and_notify(product["name"], product["url"])

    # 3. No loop, no sleep. Just finish and exit!
    logger.info("All checks completed. Worker shutting down.")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; x64)'
        "Chrome/120.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    return driver

if __name__ == "__main__":
    print("Stating Chrome.....")
    driver = create_driver()

    print("Visiting Daraz ....")
    driver.get("http://www.daraz.pk")

    time.sleep(3)
    print(f"Page title: {driver.title}")
    print("Chrome is working")

    driver.quit()



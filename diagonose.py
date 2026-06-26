import requests
from bs4 import BeautifulSoup

url = "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(url, headers=headers)
response.encoding = "utf-8"
soup = BeautifulSoup(response.text, "html.parser")

# Find anything with "price" in its class
all_tags = soup.find_all(class_=lambda c: c and "price" in c.lower())

for tag in all_tags[:5]:
    print(tag)
    print("---")
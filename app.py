from flask import Flask, render_template, request, redirect, url_for
import json
import os
from daraz_scraper import clean_daraz_price, scrape_daraz_price
from price_checker import clean_price

app = Flask(__name__)

CONFIG_FILE = "config.json"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"check_interval": 30, "products": []}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


def trim_url(url):
    return url.split("?")[0]


@app.route("/")
def index():
    config = load_config()
    return render_template("index.html", products=config.get("products", []))


@app.route("/add", methods=["POST"])
def add_product():
    name = request.form.get("name")
    raw_url = request.form.get("url")

    if name and raw_url:
        clean_url = trim_url(raw_url)
        config = load_config()

        raw_price = scrape_daraz_price(clean_url)
        clean_price_web = clean_daraz_price(raw_price)
        target_price = clean_price_web * 0.8
        # Structure matching your config requirements
        new_product = {
            "name": name,
            "url": clean_url,
            "price_tag": ".pdp-price_size_xl",
            "price_class": "",
            "target_price": target_price
        }

        config["products"].append(new_product)
        save_config(config)

    return redirect(url_for("index"))


@app.route("/delete/<int:product_index>")
def delete_product(product_index):
    config = load_config()
    if 0 <= product_index < len(config["products"]):
        config["products"].pop(product_index)
        save_config(config)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
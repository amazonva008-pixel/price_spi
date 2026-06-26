import json

def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    return config

if __name__ == "__main__":
    config = load_config()
    print(f"Check Interval: {config['check_interval']} seconds")
    print(f"Watching{len(config['products'])} products:")

    for product in config["products"]:
        print(f" -{product['name']} | Target: £{product['target_price']}")
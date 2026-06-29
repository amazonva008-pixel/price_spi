import os
import requests
import json
from dotenv import load_dotenv
from logger import setup_logger

logger = setup_logger()

# Load local .env if it exists, otherwise do nothing
load_dotenv()

def send_discord_alert(product_name, old_price, new_price, status):
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    
    if not webhook_url:
        logger.error("CRITICAL: DISCORD_WEBHOOK is missing! Cannot send alert.")
        return

    # Create the message payload
    if status == "dropped":
        color = 65280 # Green
        title = "📉 PRICE DROP ALERT!"
    else:
        color = 16711680 # Red
        title = "📈 Price Increased Alert"

    data = {
        "embeds": [{
            "title": title,
            "description": f"**{product_name}**",
            "color": color,
            "fields": [
                {"name": "Old Price", "value": f"Rs. {old_price}", "inline": True},
                {"name": "New Price", "value": f"Rs. {new_price}", "inline": True}
            ]
        }]
    }

    try:
        response = requests.post(
            webhook_url, 
            data=json.dumps(data), 
            headers={"Content-Type": "application/json"}
        )
        
        # Check if Discord accepted the message
        if response.status_code == 204:
            logger.info("✅ Discord notification sent successfully!")
        else:
            logger.error(f"❌ Discord rejected the message. Status: {response.status_code}, Error: {response.text}")
            
    except Exception as e:
        logger.error(f"❌ Failed to connect to Discord: {e}")

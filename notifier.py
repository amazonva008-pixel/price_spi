import os
import requests
from dotenv import load_dotenv



load_dotenv()

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_alert(product_name, last_price, current_price, direction):
    if direction == "dropped":
        diff =last_price - current_price
        emoji = "🟢"
        title = "PRICE DROPPED!"
        color = 3066993
        description = (
            f"**{product_name}**\n\n"
            f"~~Rs. {last_price:,.0f}~~ → **Rs. {current_price:,.0f}**\n"
            f"You save: **Rs. {diff:,.0f}**"
        )
    else:
        diff = current_price - last_price
        emoji = "🔴"
        title = "PRICE INCREASED!"
        color = 15158332
        description = (
            f"**{product_name}**\n\n"
            f"Rs. {last_price:,.0f} → **Rs. {current_price:,.0f}**\n"
            f"Increased by: **Rs. {diff:,.0f}**"
        )

    payload = {
    "embeds": [
        {
            "title": f"{emoji}  {title}",
            "description": description,
            "color": color,
            "footer": {
                "text": "Price Spy 🕷️ | Daraz.pk"
            }
        }
    ]
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("Discord notification sent! ✅")
            return True
        else:
            print(f"Discord error: {response.status_code}")
            return False

    except Exception as e:
        print(f"Failed to send Discord alert: {e}")
        return False




if __name__ == "__main__":
    send_discord_alert(
        product_name="Tecno Spark GO 3",
        last_price=35000,
        current_price=29999,
        direction="dropped"
    )
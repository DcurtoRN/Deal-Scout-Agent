import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

def send_telegram(msg):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Missing Telegram config")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": chat_id, "text": msg},
        timeout=30
    )

    print("Telegram status:", response.status_code)
    print("Telegram response:", response.text)

watch_categories = [
    "LEGO",
    "Power tools",
    "Pokemon cards",
    "Small appliances",
    "Electronics accessories"
]

message = (
    "Deal Scout Phase 1 check-in\n\n"
    f"Run time: {datetime.now(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %I:%M %p EST')}\n\n"
    "Current watch categories:\n"
    + "\n".join(f"- {item}" for item in watch_categories)
    + "\n\nSystem status: GitHub runner + Telegram alerts working."
)

send_telegram(message)

print("Phase 1 stable check finished")

import os
import requests

print("SCRIPT STARTED")

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

print("TOKEN EXISTS:", bool(token))
print("CHAT ID EXISTS:", bool(chat_id))
print("CHAT ID VALUE:", chat_id)

if not token or not chat_id:
    print("MISSING TOKEN OR CHAT ID")
    raise SystemExit(1)

url = f"https://api.telegram.org/bot{token}/sendMessage"

response = requests.post(
    url,
    json={
        "chat_id": chat_id,
        "text": "GitHub Telegram test successful"
    },
    timeout=30
)

print("STATUS CODE:", response.status_code)
print("RESPONSE TEXT:", response.text)
print("SCRIPT FINISHED")

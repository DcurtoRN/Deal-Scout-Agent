import os
import requests
from bs4 import BeautifulSoup


def send_telegram(msg):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    print("Telegram token exists:", bool(token))
    print("Telegram chat id exists:", bool(chat_id))
    print("Telegram chat id value:", chat_id)

    if not token or not chat_id:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": msg
        }
    )

    print("Telegram status code:", response.status_code)
    print("Telegram response:", response.text)


print("Deal Scout Agent Running")

url = "https://www.target.com/c/lego-construction-toys/-/N-5xt9h"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "lxml")

items = soup.find_all("a")
results = []

for item in items:
    text = item.get_text(strip=True)
    if "LEGO" in text and "$" in text:
        results.append(text)

print("Possible deals found:")
for r in results[:10]:
    print(r)

print("ABOUT TO SEND TELEGRAM")

send_telegram("Deal Scout agent ran successfully.")

print("TELEGRAM FUNCTION FINISHED")

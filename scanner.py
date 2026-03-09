import os
import re
import requests
from bs4 import BeautifulSoup

def send_telegram(msg):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Missing Telegram config")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": msg
        },
        timeout=30
    )

    print("Telegram status:", response.status_code)
    print("Telegram response:", response.text)

print("Starting Target LEGO scan...")

url = "https://www.target.com/c/lego-construction-toys/-/N-5xt9h"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(response.text, "lxml")

items = soup.find_all("a")
results = []

for item in items:
    text = item.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()

    if "LEGO" in text and "$" in text and len(text) > 15:
        results.append(text)

# remove duplicates while keeping order
results = list(dict.fromkeys(results))

# keep only the first 10
results = results[:10]

if results:
    message = "Target LEGO scan results:\n\n" + "\n\n".join(f"- {r}" for r in results)
else:
    message = "Target LEGO scan ran, but no matching items were found."

send_telegram(message)

print("Scan finished")

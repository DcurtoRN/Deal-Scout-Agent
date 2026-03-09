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

print("Starting Best Buy LEGO scan...")

url = "https://www.bestbuy.com/site/searchpage.jsp?st=lego"
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=30)
print("Page status:", response.status_code)

soup = BeautifulSoup(response.text, "lxml")

matches = []

# Pull visible text lines from the whole page
page_text = soup.get_text("\n", strip=True)
lines = [re.sub(r"\s+", " ", line).strip() for line in page_text.split("\n")]

for line in lines:
    if "LEGO" in line and "$" in line and len(line) > 10:
        matches.append(line)

# Remove duplicates, keep first 10
matches = list(dict.fromkeys(matches))[:10]

if matches:
    message = "Best Buy LEGO scan results:\n\n" + "\n\n".join(f"- {m}" for m in matches)
else:
    message = "Best Buy LEGO scan ran, but found no clean LEGO price matches."

send_telegram(message)

print("Matches found:", len(matches))
for m in matches:
    print(m)

print("Scan finished")

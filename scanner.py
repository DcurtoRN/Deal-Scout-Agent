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

url = "https://www.target.com/s/lego%20construction%20site"
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=30)
print("Page status:", response.status_code)

html = response.text
soup = BeautifulSoup(html, "lxml")

# First pass: collect visible text from page
page_text = soup.get_text("\n", strip=True)

# Look for lines that mention LEGO and a price
lines = [re.sub(r"\s+", " ", line).strip() for line in page_text.split("\n")]
matches = []

for i, line in enumerate(lines):
    if "LEGO" in line and "$" in line:
        matches.append(line)

# Backup pass: search all text chunks if first pass is sparse
if not matches:
    text_chunks = soup.find_all(string=True)
    for chunk in text_chunks:
        text = re.sub(r"\s+", " ", str(chunk)).strip()
        if "LEGO" in text and "$" in text and len(text) > 10:
            matches.append(text)

# Remove duplicates and keep first 10
matches = list(dict.fromkeys(matches))[:10]

if matches:
    message = "Target LEGO scan results:\n\n" + "\n\n".join(f"- {m}" for m in matches)
else:
    message = "Target LEGO scan ran, but still found no clean LEGO price matches on the page."

send_telegram(message)

print("Matches found:", len(matches))
for m in matches:
    print(m)

print("Scan finished")

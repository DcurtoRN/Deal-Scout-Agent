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
        json={"chat_id": chat_id, "text": msg},
        timeout=30
    )

    print("Telegram status:", response.status_code)
    print("Telegram response:", response.text)

print("Starting eBay LEGO scan...")

url = "https://www.ebay.com/sch/i.html?_nkw=lego"
headers = {
    "User-Agent": "Mozilla/5.0"
}

try:
    response = requests.get(url, headers=headers, timeout=20)
    print("Page status:", response.status_code)

    soup = BeautifulSoup(response.text, "lxml")
    matches = []

    # eBay search result cards commonly use these classes/selectors
    items = soup.select(".s-item")

    for item in items:
        title_el = item.select_one(".s-item__title")
        price_el = item.select_one(".s-item__price")
        link_el = item.select_one(".s-item__link")

        if not title_el or not price_el or not link_el:
            continue

        title = re.sub(r"\s+", " ", title_el.get_text(" ", strip=True)).strip()
        price = re.sub(r"\s+", " ", price_el.get_text(" ", strip=True)).strip()
        link = link_el.get("href", "").strip()

        if not title or not price or not link:
            continue

        # Skip generic or sponsored junk
        bad_phrases = [
            "shop on ebay",
            "results matching fewer words",
            "sponsored"
        ]
        if any(bp in title.lower() for bp in bad_phrases):
            continue

        matches.append(f"{title}\nPrice: {price}\n{link}")

    # dedupe and keep first 8
    seen = set()
    cleaned = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            cleaned.append(m)

    cleaned = cleaned[:8]

    if cleaned:
        message = "Phase 1 eBay LEGO results:\n\n" + "\n\n".join(f"- {m}" for m in cleaned)
    else:
        message = "Phase 1 eBay scan completed, but no clean product matches were found."

    send_telegram(message)

except requests.exceptions.Timeout:
    msg = "Phase 1 eBay scan failed: request timed out."
    print(msg)
    send_telegram(msg)

except requests.exceptions.RequestException as e:
    msg = f"Phase 1 eBay scan failed: request error: {str(e)}"
    print(msg)
    send_telegram(msg)

except Exception as e:
    msg = f"Phase 1 eBay scan failed: unexpected error: {str(e)}"
    print(msg)
    send_telegram(msg)

print("Scan finished")

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

print("Starting Phase 1 product-link scan...")

url = "https://www.amazon.com/gp/goldbox"
headers = {
    "User-Agent": "Mozilla/5.0"
}

try:
    response = requests.get(url, headers=headers, timeout=20)
    print("Page status:", response.status_code)

    soup = BeautifulSoup(response.text, "lxml")

    matches = []

    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        text = re.sub(r"\s+", " ", text).strip()
        href = a["href"]

        if len(text) < 20:
            continue

        # Ignore obvious generic promo junk
        bad_phrases = [
            "shop now", "see more", "learn more", "limited time",
            "deals", "under $", "top deals", "coupon", "discover"
        ]
        if any(bp in text.lower() for bp in bad_phrases):
            continue

        # Keep things that look more like product pages/links
        if "/dp/" in href or "/gp/" in href or len(text.split()) >= 4:
            full_url = href if href.startswith("http") else f"https://www.amazon.com{href}"
            matches.append(f"{text}\n{full_url}")

    # remove duplicates while preserving order
    seen = set()
    cleaned = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            cleaned.append(m)

    cleaned = cleaned[:8]

    if cleaned:
        message = "Phase 1 product-like results:\n\n" + "\n\n".join(f"- {m}" for m in cleaned)
    else:
        message = "Phase 1 scan completed, but no clean product-like links were found."

    send_telegram(message)

except requests.exceptions.Timeout:
    error_msg = "Phase 1 scan failed: request timed out while fetching the source page."
    print(error_msg)
    send_telegram(error_msg)

except requests.exceptions.RequestException as e:
    error_msg = f"Phase 1 scan failed: request error: {str(e)}"
    print(error_msg)
    send_telegram(error_msg)

except Exception as e:
    error_msg = f"Phase 1 scan failed: unexpected error: {str(e)}"
    print(error_msg)
    send_telegram(error_msg)

print("Scan finished")

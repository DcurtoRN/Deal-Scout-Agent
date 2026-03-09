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

print("Starting Phase 1 scan...")

url = "https://www.amazon.com/gp/goldbox"
headers = {
    "User-Agent": "Mozilla/5.0"
}

try:
    response = requests.get(url, headers=headers, timeout=20)
    print("Page status:", response.status_code)

    soup = BeautifulSoup(response.text, "lxml")
    page_text = soup.get_text("\n", strip=True)

    lines = [re.sub(r"\s+", " ", line).strip() for line in page_text.split("\n")]
    matches = []

    for line in lines:
        if "$" in line and len(line) > 10:
            matches.append(line)

    matches = list(dict.fromkeys(matches))[:10]

    if matches:
        message = "Phase 1 scan results:\n\n" + "\n\n".join(f"- {m}" for m in matches)
    else:
        message = "Phase 1 scan completed, but no clean priced items were found."

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

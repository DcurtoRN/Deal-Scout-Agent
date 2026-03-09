import os
import json
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


def load_watchlist(path="watchlist.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_message(watchlist_data):
    current_time = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %I:%M %p EST")

    categories = watchlist_data.get("categories", [])

    if not categories:
        return (
            "Deal Scout Phase 2 check-in\n\n"
            f"Run time: {current_time}\n\n"
            "No categories found in watchlist.json"
        )

    lines = []
    for category in categories:
        name = category.get("name", "Unnamed Category")
        min_roi = category.get("min_roi", 0)
        min_profit = category.get("min_profit", 0)

        lines.append(
            f"- {name} | Min ROI: {int(min_roi * 100)}% | Min Profit: ${min_profit}"
        )

    message = (
        "Deal Scout Phase 2 check-in\n\n"
        f"Run time: {current_time}\n\n"
        "Tracked categories from watchlist.json:\n"
        + "\n".join(lines)
        + "\n\nSystem status: GitHub runner + Telegram alerts + watchlist file working."
    )

    return message


def main():
    print("Loading watchlist.json...")
    watchlist_data = load_watchlist()

    print("Building Telegram message...")
    message = build_message(watchlist_data)

    print("Sending Telegram message...")
    send_telegram(message)

    print("Phase 2 check finished")


if __name__ == "__main__":
    main()

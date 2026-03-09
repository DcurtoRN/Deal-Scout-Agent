import os
import json
import csv
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


def load_price_reference(path="price_reference.csv"):
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def build_message(watchlist_data, price_rows):
    current_time = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %I:%M %p EST")

    categories = watchlist_data.get("categories", [])

    category_lines = []
    for category in categories:
        name = category.get("name", "Unnamed Category")
        min_roi = category.get("min_roi", 0)
        min_profit = category.get("min_profit", 0)
        category_lines.append(
            f"- {name} | Min ROI: {int(min_roi * 100)}% | Min Profit: ${min_profit}"
        )

    total_rows = len(price_rows)
    placeholder_rows = 0
    reference_lines = []

    for row in price_rows[:5]:
        category = row.get("category", "Unknown")
        brand = row.get("brand", "Unknown")
        model_key = row.get("model_key", "Unknown")
        avg_resale = row.get("avg_resale_price", "0")
        confidence = row.get("confidence", "unknown")

        if avg_resale in ("0", "0.0", "0.00", ""):
            placeholder_rows += 1

        reference_lines.append(
            f"- {category} | {brand} | {model_key} | Avg Resale: ${avg_resale} | Confidence: {confidence}"
        )

    # count all placeholders, not just first 5
    placeholder_rows = sum(
        1 for row in price_rows
        if row.get("avg_resale_price", "0") in ("0", "0.0", "0.00", "")
    )

    message = (
        "Deal Scout Phase 2 check-in\n\n"
        f"Run time: {current_time}\n\n"
        "Tracked categories from watchlist.json:\n"
        + ("\n".join(category_lines) if category_lines else "- None found")
        + "\n\n"
        f"Reference pricing rows loaded: {total_rows}\n"
        f"Placeholder rows still needing real pricing: {placeholder_rows}\n\n"
        "Sample reference entries:\n"
        + ("\n".join(reference_lines) if reference_lines else "- None found")
        + "\n\nSystem status: GitHub runner + Telegram alerts + watchlist + price reference working."
    )

    return message


def main():
    print("Loading watchlist.json...")
    watchlist_data = load_watchlist()

    print("Loading price_reference.csv...")
    price_rows = load_price_reference()

    print("Building Telegram message...")
    message = build_message(watchlist_data, price_rows)

    print("Sending Telegram message...")
    send_telegram(message)

    print("Phase 2 reference check finished")


if __name__ == "__main__":
    main()

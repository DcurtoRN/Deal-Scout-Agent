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


def get_category_rules(watchlist_data, category_name):
    for category in watchlist_data.get("categories", []):
        if category.get("name", "").strip().lower() == category_name.strip().lower():
            return category
    return None


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def score_item(row, rules):
    category = row.get("category", "Unknown")
    brand = row.get("brand", "Unknown")
    model_key = row.get("model_key", "Unknown")
    confidence = row.get("confidence", "unknown")

    buy_price = to_float(row.get("buy_price"))
    avg_resale_price = to_float(row.get("avg_resale_price"))
    fee_pct = to_float(row.get("estimated_fee_pct"))
    shipping = to_float(row.get("estimated_shipping"))

    fees = avg_resale_price * fee_pct
    profit = avg_resale_price - buy_price - fees - shipping
    roi = (profit / buy_price) if buy_price > 0 else 0

    min_roi = to_float(rules.get("min_roi", 0.30)) if rules else 0.30
    min_profit = to_float(rules.get("min_profit", 15)) if rules else 15

    if profit >= min_profit and roi >= min_roi:
        action = "BUY"
    elif profit > 0 and roi >= (min_roi * 0.5):
        action = "WATCH"
    else:
        action = "SKIP"

    return {
        "category": category,
        "brand": brand,
        "model_key": model_key,
        "buy_price": round(buy_price, 2),
        "avg_resale_price": round(avg_resale_price, 2),
        "fees": round(fees, 2),
        "shipping": round(shipping, 2),
        "profit": round(profit, 2),
        "roi_pct": round(roi * 100, 1),
        "action": action,
        "confidence": confidence,
        "min_roi_pct": round(min_roi * 100, 1),
        "min_profit": round(min_profit, 2)
    }


def build_message(watchlist_data, scored_items):
    current_time = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %I:%M %p EST")

    lines = []
    for item in scored_items:
        lines.append(
            f"{item['action']} | {item['category']} | {item['brand']} {item['model_key']}\n"
            f"Buy: ${item['buy_price']} | Resale: ${item['avg_resale_price']}\n"
            f"Fees: ${item['fees']} | Shipping: ${item['shipping']}\n"
            f"Profit: ${item['profit']} | ROI: {item['roi_pct']}%\n"
            f"Confidence: {item['confidence']} | Thresholds: {item['min_roi_pct']}% / ${item['min_profit']}"
        )

    message = (
        "Deal Scout Phase 2 scoring check\n\n"
        f"Run time: {current_time}\n\n"
        "Scored reference items:\n\n"
        + "\n\n".join(lines)
        + "\n\nSystem status: scoring engine working."
    )

    return message


def main():
    print("Loading watchlist.json...")
    watchlist_data = load_watchlist()

    print("Loading price_reference.csv...")
    price_rows = load_price_reference()

    print("Scoring items...")
    scored_items = []
    for row in price_rows:
        rules = get_category_rules(watchlist_data, row.get("category", ""))
        scored_items.append(score_item(row, rules))

    print("Building Telegram message...")
    message = build_message(watchlist_data, scored_items)

    print("Sending Telegram message...")
    send_telegram(message)

    print("Phase 2 scoring check finished")


if __name__ == "__main__":
    main()

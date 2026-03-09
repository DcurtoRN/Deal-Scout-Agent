import os
import json
import csv
import requests
from datetime import datetime
from zoneinfo import ZoneInfo


def now_est():
    return datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %I:%M %p EST")


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


def load_csv_rows(path):
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def get_category_rules(watchlist_data, category_name):
    for category in watchlist_data.get("categories", []):
        if category.get("name", "").strip().lower() == category_name.strip().lower():
            return category
    return None


def build_reference_lookup(price_rows):
    lookup = {}

    for row in price_rows:
        category = row.get("category", "").strip().lower()
        brand = row.get("brand", "").strip().lower()
        model_key = row.get("model_key", "").strip().lower()
        condition = row.get("condition", "").strip().lower()

        key = (category, brand, model_key, condition)
        lookup[key] = row

    return lookup


def score_candidate(candidate, reference_row, rules):
    category = candidate.get("category", "Unknown")
    brand = candidate.get("brand", "Unknown")
    model_key = candidate.get("model_key", "Unknown")
    title = candidate.get("title", "Unknown")
    source = candidate.get("source", "Unknown")
    url = candidate.get("url", "")
    condition = candidate.get("condition", "unknown")

    buy_price = to_float(candidate.get("price"))
    avg_resale_price = to_float(reference_row.get("avg_resale_price"))
    fee_pct = to_float(reference_row.get("estimated_fee_pct"))
    shipping = to_float(reference_row.get("estimated_shipping"))

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
        "title": title,
        "source": source,
        "url": url,
        "category": category,
        "brand": brand,
        "model_key": model_key,
        "condition": condition,
        "buy_price": round(buy_price, 2),
        "avg_resale_price": round(avg_resale_price, 2),
        "fees": round(fees, 2),
        "shipping": round(shipping, 2),
        "profit": round(profit, 2),
        "roi_pct": round(roi * 100, 1),
        "action": action,
        "confidence": reference_row.get("confidence", "unknown"),
        "min_roi_pct": round(min_roi * 100, 1),
        "min_profit": round(min_profit, 2)
    }


def score_candidates(candidates, reference_lookup, watchlist_data):
    scored = []
    unmatched = []

    for candidate in candidates:
        category = candidate.get("category", "").strip().lower()
        brand = candidate.get("brand", "").strip().lower()
        model_key = candidate.get("model_key", "").strip().lower()
        condition = candidate.get("condition", "").strip().lower()

        key = (category, brand, model_key, condition)
        reference_row = reference_lookup.get(key)

        if not reference_row:
            unmatched.append(candidate)
            continue

        rules = get_category_rules(watchlist_data, candidate.get("category", ""))
        scored.append(score_candidate(candidate, reference_row, rules))

    return scored, unmatched


def append_scored_results(scored_items, path="scored_results.csv"):
    run_time = now_est()

    fieldnames = [
        "run_time", "title", "source", "category", "brand", "model_key", "condition",
        "buy_price", "avg_resale_price", "fees", "shipping", "profit", "roi_pct",
        "action", "confidence", "url"
    ]

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        for item in scored_items:
            writer.writerow({
                "run_time": run_time,
                "title": item["title"],
                "source": item["source"],
                "category": item["category"],
                "brand": item["brand"],
                "model_key": item["model_key"],
                "condition": item["condition"],
                "buy_price": item["buy_price"],
                "avg_resale_price": item["avg_resale_price"],
                "fees": item["fees"],
                "shipping": item["shipping"],
                "profit": item["profit"],
                "roi_pct": item["roi_pct"],
                "action": item["action"],
                "confidence": item["confidence"],
                "url": item["url"]
            })


def build_alert_key(item):
    return (
        item.get("source", "").strip().lower(),
        item.get("category", "").strip().lower(),
        item.get("brand", "").strip().lower(),
        item.get("model_key", "").strip().lower(),
        item.get("condition", "").strip().lower(),
        str(item.get("buy_price", "")).strip()
    )


def load_alerted_keys(path="alerted_items.csv"):
    keys = set()
    rows = load_csv_rows(path)

    for row in rows:
        key = (
            row.get("source", "").strip().lower(),
            row.get("category", "").strip().lower(),
            row.get("brand", "").strip().lower(),
            row.get("model_key", "").strip().lower(),
            row.get("condition", "").strip().lower(),
            str(row.get("buy_price", "")).strip()
        )
        keys.add(key)

    return keys


def append_alerted_items(items, path="alerted_items.csv"):
    fieldnames = [
        "alert_time", "title", "source", "category", "brand",
        "model_key", "condition", "buy_price", "action", "url"
    ]

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        for item in items:
            writer.writerow({
                "alert_time": now_est(),
                "title": item["title"],
                "source": item["source"],
                "category": item["category"],
                "brand": item["brand"],
                "model_key": item["model_key"],
                "condition": item["condition"],
                "buy_price": item["buy_price"],
                "action": item["action"],
                "url": item["url"]
            })


def filter_new_buy_items(scored_items, alerted_keys):
    buy_items = [item for item in scored_items if item["action"] == "BUY"]
    new_buy_items = []

    for item in buy_items:
        key = build_alert_key(item)
        if key not in alerted_keys:
            new_buy_items.append(item)

    return buy_items, new_buy_items


def build_buy_alert_message(all_buy_items, new_buy_items, unmatched_items):
    current_time = now_est()

    if not all_buy_items:
        return (
            "Deal Scout BUY alert check\n\n"
            f"Run time: {current_time}\n\n"
            "No BUY candidates found this run.\n\n"
            f"Unmatched candidates: {len(unmatched_items)}\n"
            "All scored items were still saved to scored_results.csv."
        )

    if not new_buy_items:
        return (
            "Deal Scout BUY alert check\n\n"
            f"Run time: {current_time}\n\n"
            f"BUY candidates found: {len(all_buy_items)}\n"
            "New BUY alerts: 0\n\n"
            "All BUY items this run were already alerted previously.\n\n"
            f"Unmatched candidates: {len(unmatched_items)}\n"
            "All scored items were still saved to scored_results.csv."
        )

    blocks = [
        "Deal Scout NEW BUY alert\n",
        f"Run time: {current_time}\n",
        f"BUY candidates found this run: {len(all_buy_items)}",
        f"New BUY alerts sent: {len(new_buy_items)}\n"
    ]

    for item in new_buy_items:
        blocks.append(
            f"- {item['brand']} {item['model_key']} ({item['category']})\n"
            f"  Source: {item['source']}\n"
            f"  Buy: ${item['buy_price']} | Resale: ${item['avg_resale_price']}\n"
            f"  Fees: ${item['fees']} | Shipping: ${item['shipping']}\n"
            f"  Profit: ${item['profit']} | ROI: {item['roi_pct']}%\n"
            f"  Confidence: {item['confidence']}\n"
            f"  Link: {item['url']}\n"
        )

    blocks.append(f"Unmatched candidates: {len(unmatched_items)}")
    blocks.append("Scored results saved to scored_results.csv.")
    blocks.append("New BUY alerts saved to alerted_items.csv.")

    return "\n".join(blocks)


def main():
    print("Loading watchlist.json...")
    watchlist_data = load_watchlist()

    print("Loading price_reference.csv...")
    price_rows = load_csv_rows("price_reference.csv")

    print("Loading candidate_items.csv...")
    candidate_rows = load_csv_rows("candidate_items.csv")

    print("Building reference lookup...")
    reference_lookup = build_reference_lookup(price_rows)

    print("Scoring candidates...")
    scored_items, unmatched_items = score_candidates(
        candidate_rows,
        reference_lookup,
        watchlist_data
    )

    print("Appending scored results to scored_results.csv...")
    append_scored_results(scored_items)

    print("Loading previously alerted BUY items...")
    alerted_keys = load_alerted_keys()

    print("Filtering BUY items against alert history...")
    all_buy_items, new_buy_items = filter_new_buy_items(scored_items, alerted_keys)

    if new_buy_items:
        print("Appending new BUY alerts to alerted_items.csv...")
        append_alerted_items(new_buy_items)
    else:
        print("No new BUY alerts to save.")

    print("Building Telegram message...")
    message = build_buy_alert_message(all_buy_items, new_buy_items, unmatched_items)

    print("Sending Telegram message...")
    send_telegram(message)

    print("Alert suppression run finished")


if __name__ == "__main__":
    main()

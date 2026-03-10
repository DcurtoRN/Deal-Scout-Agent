import os
import json
import csv
import requests
from datetime import datetime
from zoneinfo import ZoneInfo


WATCHLIST_PATH = "data/watchlist.json"
PRICE_REFERENCE_PATH = "data/price_reference.csv"
CANDIDATES_PATH = "data/candidate_items.csv"
SCORED_RESULTS_PATH = "data/scored_results.csv"
ALERTED_ITEMS_PATH = "data/alerted_items.csv"


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


def load_watchlist(path=WATCHLIST_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_csv_rows(path):
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def write_csv_rows(path, fieldnames, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


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
        key = (
            row.get("category", "").strip().lower(),
            row.get("brand", "").strip().lower(),
            row.get("model_key", "").strip().lower(),
            row.get("condition", "").strip().lower(),
        )
        lookup[key] = row
    return lookup


def build_alert_key(item):
    return (
        item.get("source", "").strip().lower(),
        item.get("category", "").strip().lower(),
        item.get("brand", "").strip().lower(),
        item.get("model_key", "").strip().lower(),
        item.get("condition", "").strip().lower(),
        str(item.get("buy_price", "")).strip(),
    )


def load_alerted_keys(path=ALERTED_ITEMS_PATH):
    keys = set()
    rows = load_csv_rows(path)
    for row in rows:
        keys.add((
            row.get("source", "").strip().lower(),
            row.get("category", "").strip().lower(),
            row.get("brand", "").strip().lower(),
            row.get("model_key", "").strip().lower(),
            row.get("condition", "").strip().lower(),
            str(row.get("buy_price", "")).strip(),
        ))
    return keys


def append_alerted_items(items, path=ALERTED_ITEMS_PATH):
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


def append_scored_results(scored_items, path=SCORED_RESULTS_PATH):
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
    }


def process_candidates(candidate_rows, reference_lookup, watchlist_data):
    scored_items = []
    unmatched_items = []

    for row in candidate_rows:
        status = row.get("status", "").strip().lower()
        if status != "new":
            continue

        key = (
            row.get("category", "").strip().lower(),
            row.get("brand", "").strip().lower(),
            row.get("model_key", "").strip().lower(),
            row.get("condition", "").strip().lower(),
        )

        reference_row = reference_lookup.get(key)

        if not reference_row:
            row["status"] = "unmatched"
            row["notes"] = "No matching reference row found"
            unmatched_items.append(row)
            continue

        rules = get_category_rules(watchlist_data, row.get("category", ""))
        scored = score_candidate(row, reference_row, rules)
        scored_items.append(scored)

        if scored["action"] == "BUY":
            # status updated later after dedupe check
            pass
        else:
            row["status"] = "scored"
            row["notes"] = f"Scored as {scored['action']}"

    return scored_items, unmatched_items, candidate_rows


def update_candidate_statuses_for_new_buys(candidate_rows, new_buy_items):
    new_buy_keys = {
        (
            item["source"].strip().lower(),
            item["category"].strip().lower(),
            item["brand"].strip().lower(),
            item["model_key"].strip().lower(),
            item["condition"].strip().lower(),
            str(item["buy_price"]).strip(),
        )
        for item in new_buy_items
    }

    for row in candidate_rows:
        if row.get("status", "").strip().lower() != "new":
            continue

        key = (
            row.get("source", "").strip().lower(),
            row.get("category", "").strip().lower(),
            row.get("brand", "").strip().lower(),
            row.get("model_key", "").strip().lower(),
            row.get("condition", "").strip().lower(),
            str(to_float(row.get("price"))).rstrip("0").rstrip(".") if "." in str(to_float(row.get("price"))) else str(to_float(row.get("price"))),
        )

        # buy_price in scored items is rounded numeric, normalize both sides:
        alt_key = (
            row.get("source", "").strip().lower(),
            row.get("category", "").strip().lower(),
            row.get("brand", "").strip().lower(),
            row.get("model_key", "").strip().lower(),
            row.get("condition", "").strip().lower(),
            str(round(to_float(row.get("price")), 2)),
        )

        if key in new_buy_keys or alt_key in new_buy_keys:
            row["status"] = "alerted"
            row["notes"] = "BUY alert sent"


def mark_existing_buys_as_scored(candidate_rows, scored_items, new_buy_items):
    new_buy_lookup = {
        (
            item["source"].strip().lower(),
            item["category"].strip().lower(),
            item["brand"].strip().lower(),
            item["model_key"].strip().lower(),
            item["condition"].strip().lower(),
            str(item["buy_price"]).strip(),
        )
        for item in new_buy_items
    }

    for row in candidate_rows:
        if row.get("status", "").strip().lower() != "new":
            continue

        candidate_buy_key = (
            row.get("source", "").strip().lower(),
            row.get("category", "").strip().lower(),
            row.get("brand", "").strip().lower(),
            row.get("model_key", "").strip().lower(),
            row.get("condition", "").strip().lower(),
            str(round(to_float(row.get("price")), 2)),
        )

        if candidate_buy_key in new_buy_lookup:
            continue

        # if it was a BUY but already alerted before, mark as alerted
        for item in scored_items:
            item_key = (
                item["source"].strip().lower(),
                item["category"].strip().lower(),
                item["brand"].strip().lower(),
                item["model_key"].strip().lower(),
                item["condition"].strip().lower(),
                str(item["buy_price"]).strip(),
            )
            row_key = candidate_buy_key

            if item_key == row_key and item["action"] == "BUY":
                row["status"] = "alerted"
                row["notes"] = "BUY item already alerted previously"
                break


def build_buy_alert_message(all_buy_items, new_buy_items, unmatched_items, processed_new_count):
    current_time = now_est()

    if processed_new_count == 0:
        return (
            "Deal Scout status check\n\n"
            f"Run time: {current_time}\n\n"
            "No NEW candidate items to process this run."
        )

    if not all_buy_items:
        return (
            "Deal Scout BUY alert check\n\n"
            f"Run time: {current_time}\n\n"
            f"New candidates processed: {processed_new_count}\n"
            "No BUY candidates found among new items.\n\n"
            f"Unmatched new candidates: {len(unmatched_items)}\n"
            "Scored results were saved."
        )

    if not new_buy_items:
        return (
            "Deal Scout BUY alert check\n\n"
            f"Run time: {current_time}\n\n"
            f"New candidates processed: {processed_new_count}\n"
            f"BUY candidates found among them: {len(all_buy_items)}\n"
            "New BUY alerts: 0\n\n"
            "All BUY items in this batch were already alerted previously."
        )

    blocks = [
        "Deal Scout NEW BUY alert\n",
        f"Run time: {current_time}",
        f"New candidates processed: {processed_new_count}",
        f"BUY candidates found in batch: {len(all_buy_items)}",
        f"New BUY alerts sent: {len(new_buy_items)}\n",
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

    blocks.append(f"Unmatched new candidates: {len(unmatched_items)}")
    return "\n".join(blocks)


def main():
    print("Loading watchlist...")
    watchlist_data = load_watchlist()

    print("Loading reference pricing...")
    price_rows = load_csv_rows(PRICE_REFERENCE_PATH)

    print("Loading candidates...")
    candidate_rows = load_csv_rows(CANDIDATES_PATH)
    candidate_fieldnames = list(candidate_rows[0].keys()) if candidate_rows else [
        "timestamp", "source", "title", "price", "url", "category", "brand",
        "model_key", "condition", "status", "notes"
    ]

    new_count = sum(1 for row in candidate_rows if row.get("status", "").strip().lower() == "new")
    print(f"New candidates found in file: {new_count}")

    print("Building reference lookup...")
    reference_lookup = build_reference_lookup(price_rows)

    print("Processing new candidates...")
    scored_items, unmatched_items, candidate_rows = process_candidates(
        candidate_rows,
        reference_lookup,
        watchlist_data
    )

    if scored_items:
        print("Appending scored results...")
        append_scored_results(scored_items, SCORED_RESULTS_PATH)
    else:
        print("No scored items to append.")

    print("Loading alert history...")
    alerted_keys = load_alerted_keys(ALERTED_ITEMS_PATH)

    all_buy_items = [item for item in scored_items if item["action"] == "BUY"]
    new_buy_items = [item for item in all_buy_items if build_alert_key(item) not in alerted_keys]

    if new_buy_items:
        print("Saving new BUY alerts...")
        append_alerted_items(new_buy_items, ALERTED_ITEMS_PATH)
    else:
        print("No new BUY alerts to save.")

    print("Updating candidate statuses...")
    update_candidate_statuses_for_new_buys(candidate_rows, new_buy_items)
    mark_existing_buys_as_scored(candidate_rows, scored_items, new_buy_items)

    print("Writing updated candidate_items.csv...")
    write_csv_rows(CANDIDATES_PATH, candidate_fieldnames, candidate_rows)

    print("Building Telegram message...")
    message = build_buy_alert_message(all_buy_items, new_buy_items, unmatched_items, new_count)

    print("Sending Telegram message...")
    send_telegram(message)

    print("Status management run finished")


if __name__ == "__main__":
    main()

def send_telegram(msg):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    print("Telegram token exists:", bool(token))
    print("Telegram chat id exists:", bool(chat_id))
    print("Telegram chat id value:", chat_id)

    if not token or not chat_id:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": msg
        }
    )

    print("Telegram status code:", response.status_code)
    print("Telegram response:", response.text)

print("Possible deals found:")

for r in results[:10]:
    print(r)

send_telegram("Deal Scout agent ran successfully.")

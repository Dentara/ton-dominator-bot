import requests
import time

TELEGRAM_TOKEN = "8044814129:AAGuUT5ORrNjEm26PzeSshLMsMxW2aymIf8"
CHAT_ID = "91607116"
last_msg_time = 0

def send_telegram_message(text: str):
    global last_msg_time
    now = time.time()
    if now - last_msg_time < 1.2:  # Telegram 1 msg/sec limiti
        time.sleep(1.2)
    last_msg_time = now

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload)
        print(f"✅ Status kodu: {response.status_code}")
        print(f"🔁 Cavab: {response.text}")

        if response.status_code != 200:
            print(f"⚠️ Telegram mesajı göndərilə bilmədi!")
    except Exception as e:
        print(f"❌ Telegram göndəriş xətası: {e}")
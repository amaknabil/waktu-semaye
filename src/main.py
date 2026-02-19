import httpx
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv
import telebot

# 1. Load the .env file
load_dotenv(find_dotenv(), override=True)

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
BASE_URL = os.getenv("URL") # Ensure this ends with a / in .env

# Zone Mapping (Zone Name, Topic ID)
ZONES_TO_PROCESS = [
    (os.getenv("ZONE_PJ"), os.getenv("TOPIC_PJ")),
    (os.getenv("ZONE_MCH"), os.getenv("TOPIC_MCH"))
]

class PrayerClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch_today_times(self, zone,year,month,nextday):
        try:
            print(f"Fetching prayer times for {zone}...")
            # Using join logic to avoid double slashes
            url = f"{self.base_url.rstrip('/')}/{zone}?year={year}&month={month}"
            response = httpx.get(url)
            response.raise_for_status()
            data = response.json()
            
            for prayer in data.get('prayers', []):
                if prayer['day'] == nextday:
                    return prayer
            return None
        except Exception as e:
            print(f"Error for {zone}: {e}")
            return None

def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%I:%M %p')

def create_message(zone_code, p):
    return (
        f"🕋 *Waktu Solat {zone_code}*\n"
        f"📅 {(datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')}\n\n"
        f"Subuh: `{format_time(p['fajr'])}`\n"
        f"Zohor: `{format_time(p['dhuhr'])}`\n"
        f"Asar: `{format_time(p['asr'])}`\n"
        f"Maghrib: `{format_time(p['maghrib'])}`\n"
        f"Isyak: `{format_time(p['isha'])}`"
    )

def main():
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment.")
        return

    # Initialize Bot and Client
    bot = telebot.TeleBot(BOT_TOKEN.strip())
    client = PrayerClient(BASE_URL)
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    year = tomorrow.year
    month = tomorrow.month
    nextday = tomorrow.day


    for zone_code, topic_id in ZONES_TO_PROCESS:
        if not zone_code or not topic_id:
            continue
            
        nextday_data = client.fetch_today_times(zone_code,year,month,nextday)
        
        if nextday_data:
            message_text = create_message(zone_code, nextday_data)
            try:
                bot.send_message(
                    chat_id=GROUP_ID,
                    text=message_text,
                    message_thread_id=topic_id,
                    parse_mode="Markdown"
                )
                print(f"Success: Message sent to Topic {topic_id} ({zone_code})")
            except Exception as e:
                print(f"Telegram Error for {zone_code}: {e}")
        else:
            print(f"No data found for {zone_code} today.")

if __name__ == "__main__":
    main()
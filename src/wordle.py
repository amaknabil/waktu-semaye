import os
import httpx
import telebot
import logging
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

# 1. Setup Logging (Better than print statements)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_wordle_data():
    load_dotenv(find_dotenv(), override=True)
    
    # Configuration
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    GROUP_ID = os.getenv("GROUP_ID")
    TOPIC_ID = os.getenv("TOPIC_WORDLE")
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    url = f"https://www.nytimes.com/svc/wordle/v2/{date_str}.json"

    # 2. Using a context manager for httpx
    with httpx.Client(timeout=10.0) as client:
        try:
            response = client.get(url)
            response.raise_for_status() # Raises error for 4xx or 5xx codes
            
            data = response.json()
            solution = data["solution"].upper() # .upper() makes it look more like the game
            n_words = data["days_since_launch"]
            
            # Formatting the message nicely
            msg = (
                    f"*Wordle #{data['days_since_launch']}*\n\n"
                    f"📅 *Date:* `{data['print_date']}`\n"
                    f"🧠 *Word:* * {solution} *"
                )


            # 3. Initializing Bot
            bot = telebot.TeleBot(BOT_TOKEN)
            bot.send_message(
                chat_id=GROUP_ID,
                text=msg,
                message_thread_id=TOPIC_ID,
                parse_mode="Markdown"
            )
            logger.info("Successfully sent Wordle update to Telegram.")

        except httpx.HTTPStatusError as e:
            logger.error(f"NYT API Error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    get_wordle_data()
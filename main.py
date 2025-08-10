import time
from datetime import datetime
from sys import exit

from telegram_utils import send_telegram_message
from utils import get_trades, initialize_price

highest_price_reference = initialize_price()

if highest_price_reference is None:
    exit()
last_sent_minute_block = -1
while True:
    current_minute_block = datetime.now().minute // 15
    if current_minute_block != last_sent_minute_block:
        send_telegram_message("Bot up and running")
        last_sent_minute_block = current_minute_block
    try:
        highest_price_reference = get_trades(highest_price_reference)
        time.sleep(10)
    except Exception as e:
        print(f"Error encountered: {e}")
        print("Retrying in 30 seconds...")
        time.sleep(30)
        # Re-initialize price reference in case of connection issues
        highest_price_reference = initialize_price()
        if highest_price_reference is None:
            print("Failed to re-initialize price reference. Exiting.")
            exit()

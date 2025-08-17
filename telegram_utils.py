import os

import telebot
from dotenv import load_dotenv

load_dotenv()


def send_telegram_message(message):
    if os.getenv("ENABLE_TELEGRAM_NOTIFICATIONS"):
        bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        bot.send_message(chat_id=chat_id, text=message)

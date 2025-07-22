import time

from dotenv import load_dotenv

from utils import get_trades

load_dotenv()

while True:
    print("Checking current status...")
    get_trades()
    time.sleep(5)

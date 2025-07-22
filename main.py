from dotenv import load_dotenv
import time
from utils import get_liquidation_status

load_dotenv()

while True:
    print("Checking current status...")
    get_liquidation_status()
    time.sleep(5)
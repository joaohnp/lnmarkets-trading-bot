import time
from sys import exit

from utils import get_trades, initialize_price

highest_price_reference = initialize_price()

if highest_price_reference is None:
    exit()

while True:
    try:
        highest_price_reference = get_trades(highest_price_reference)
        time.sleep(10)
    except Exception as e:
        print(e)
        exit()

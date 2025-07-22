import json
import logging  # Import the logging module
import os

from dotenv import load_dotenv
from lnmarkets import rest

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


options = {
    "key": os.getenv("LN_MARKETS_KEY"),
    "secret": os.getenv("LN_MARKETS_SECRET"),
    "passphrase": os.getenv("LN_MARKETS_PASSPHRASE"),
    "network": "mainnet",
}

lnm = rest.LNMarketsRest(**options)


def add_margin(id, amount=1000):
    lnm.futures_add_margin({"amount": amount, "id": id})
    logging.info("Margin added to the trade")  # Use logging.info instead of print


def current_profit(trade):
    logging.info(trade["pl"])  # Use logging.info


def get_liquidation_status(trade, current_price):
    closure_threshold = (trade["liquidation"] / current_price) * 100
    if closure_threshold >= 95:
        logging.warning(  # Use logging.warning for a potential issue
            f"Trade {trade['id']} is at {round(closure_threshold, 2)}% of liquidation threshold"
        )
        add_margin(trade["id"])


def get_trades():
    current_price = json.loads(lnm.futures_get_ticker())["index"]
    running_trades = lnm.futures_get_trades({"type": "running"})
    trades_json = json.loads(running_trades)
    for trade in trades_json:
        get_liquidation_status(trade, current_price)

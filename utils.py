import json
import logging  # Import the logging module
import os
import time

from dotenv import load_dotenv
from lnmarkets import rest

from telegram_utils import send_telegram_message

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
user_configs = {
    "diff_to_buy": 85,
    "percentage_to_buy": 1.005,
    "real_profit": 1.0045,
    "max_trades": 65,
    "margin": 1000,
    "quantity": 150,
    "leverage": 13,
    "threshold_to_add": 95,
    "safe_guard": True,
    "min_order_diff": 250,
}
lnm = rest.LNMarketsRest(**options)


def message_handler(message):
    logging.info(message)
    send_telegram_message(message)


def initialize_price():
    """Fetches the initial price from the API and sets it as reference."""
    try:
        initial_price = json.loads(lnm.futures_get_ticker())["index"]
        msg = f"Initial reference price: {initial_price}"
        message_handler(msg)
        return initial_price
    except Exception as e:
        logging.error(f"Could not get initial price. Exiting. Error: {e}")
        return None  # Returns None in case of failure


def add_margin(id, amount=user_configs["margin"]):
    lnm.futures_add_margin({"amount": amount, "id": id})
    margin_message = f"Margin added to order {id} for amount {amount}"
    time.sleep(3)
    # message_handler(margin_message)


def adjust_order(trade, new_takeprofit):
    old_takeprofit = trade["takeprofit"]
    lnm.futures_update_trade({
        "id": trade["id"],
        "type": "takeprofit",
        "value": new_takeprofit,
    })
    adjusted_profit_msg = (
        f"Goal of {trade['id']} from {old_takeprofit} to {new_takeprofit}"
    )
    time.sleep(3)
    # message_handler(adjusted_profit_msg)


def get_liquidation_status(trade, current_price):
    closure_threshold = (trade["liquidation"] / current_price) * 100
    if closure_threshold >= user_configs["threshold_to_add"]:
        # warning_message = f"""Trade {trade["id"]} is at
        # {round(closure_threshold, 2)}% of liquidation threshold"""
        # message_handler(warning_message)
        try:
            add_margin(trade["id"])
        except Exception as e:
            exception_message = (
                f"Error adding margin to trade {trade['id']}: {e}"
            )
            message_handler(exception_message)


def buy_order(takeprofit):
    lnm.futures_new_trade({
        "type": "m",
        "side": "b",
        "quantity": user_configs["quantity"],
        "leverage": user_configs["leverage"],
        "takeprofit": round(takeprofit),
    })
    new_order_text = f"New order aiming at {takeprofit}"
    message_handler(new_order_text)


def adjust_take_profit(trade):
    sum_carry_fees = trade["sum_carry_fees"]
    opening_fee = trade["opening_fee"]
    expected_profit = trade["quantity"] * (
        (1 / trade["price"] - 1 / trade["takeprofit"]) * 100000000
    )
    real_profit = expected_profit - sum_carry_fees - opening_fee
    ideal_profit = trade["quantity"] * (
        (
            1 / trade["price"]
            - 1 / (trade["price"] * user_configs["real_profit"])
        )
        * 100000000
    )
    if round(real_profit) < round(ideal_profit):
        # breakpoint()
        required_expected_profit = ideal_profit + sum_carry_fees + opening_fee
        new_takeprofit = 1 / (
            1 / trade["price"]
            - required_expected_profit / (trade["quantity"] * 100000000)
        )
        if round(new_takeprofit) > trade["takeprofit"]:
            adjust_order(trade, new_takeprofit=round(new_takeprofit))


reference_price = None


def is_sufficient_distance_from_orders(current_price, min_distance=None):
    """
    Check if the current price is at least min_distance away from all existing orders.

    Args:
        current_price (float): Current market price
        min_distance (float): Minimum required distance from existing orders (defaults to user_configs["min_order_diff"])

    Returns:
        bool: True if current price is sufficiently distant from all existing orders, False otherwise
    """
    if min_distance is None:
        min_distance = user_configs["min_order_diff"]

    try:
        running_trades = lnm.futures_get_trades({"type": "running"})
        trades_json = json.loads(running_trades)

        for trade in trades_json:
            if abs(trade["price"] - current_price) < min_distance:
                msg_attempt_buy = f"""Order {trade["id"]} at price {trade["price"]} is
                    too close to current price {current_price}. Distance:
                    {abs(trade["price"] - current_price)}"""
                # message_handler(msg_attempt_buy)
                return False
        return True
    except Exception as e:
        error_msg = f"Error checking distance from existing orders: {e}"
        message_handler(error_msg)
        return False


def get_trades(highest_price_reference):
    buying_diff = user_configs["diff_to_buy"]
    current_price = json.loads(lnm.futures_get_ticker())["index"]
    new_highest_price = max(highest_price_reference, current_price)
    if new_highest_price > highest_price_reference:
        highest_price_reference = new_highest_price
        price_peak_text = (
            f"New price peak reached. New reference: {highest_price_reference}"
        )
        message_handler(price_peak_text)

    running_trades = lnm.futures_get_trades({"type": "running"})
    trades_json = json.loads(running_trades)
    next_buy = highest_price_reference - current_price
    if (next_buy >= buying_diff) and (
        len(trades_json) <= user_configs["max_trades"]
    ):
        if user_configs["safe_guard"]:
            if is_sufficient_distance_from_orders(current_price):
                takeprofit = current_price * user_configs["percentage_to_buy"]
                try:
                    buy_order(takeprofit)
                    buying_message = f"Buy order executed at {current_price}. Resetting peak reference to this value."
                    message_handler(buying_message)
                    highest_price_reference = current_price
                except Exception as e:
                    error_msg = f"Error executing buy order: {e}"
                    message_handler(error_msg)
        else:
            takeprofit = current_price * user_configs["percentage_to_buy"]
            try:
                buy_order(takeprofit)
                buying_message = f"Buy order executed at {current_price}"
                message_handler(buying_message)
                highest_price_reference = current_price
            except Exception as e:
                error_msg = f"Error executing buy order: {e}"
                message_handler(error_msg)

    for trade in trades_json:
        get_liquidation_status(trade, current_price)
        adjust_take_profit(trade)
    return highest_price_reference

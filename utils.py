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
user_configs = {
    "diff_to_buy": 225,
    "percentage_to_buy": 1.005,
    "real_profit": 1.0035,
    "max_trades": 50,
    "margin": 800,
    "quantity": 300,
    "leverage": 18,
    "threshold_to_add": 97.5,
}
lnm = rest.LNMarketsRest(**options)


def initialize_price():
    """Busca o preço inicial na API e o define como referência."""
    try:
        initial_price = json.loads(lnm.futures_get_ticker())["index"]
        logging.info(f"Preço de referência inicial definido: {initial_price}")
        return initial_price
    except Exception as e:
        logging.error(f"Não foi possível obter o preço inicial. Encerrando. Erro: {e}")
        return None  # Retorna None em caso de falha


def add_margin(id, amount=user_configs["margin"]):
    lnm.futures_add_margin({"amount": amount, "id": id})
    logging.info("Margin added to the trade")  # Use logging.info instead of print


def adjust_order(trade, new_takeprofit):
    old_takeprofit = trade["takeprofit"]
    lnm.futures_update_trade(
        {"id": trade["id"], "type": "takeprofit", "value": new_takeprofit}
    )
    logging.info(
        f"Takeprofit of order {trade['id']} from {old_takeprofit} adjusted to {new_takeprofit}"
    )


def current_profit(trade):
    logging.info(trade["pl"])  # Use logging.info


def get_liquidation_status(trade, current_price):
    closure_threshold = (trade["liquidation"] / current_price) * 100
    if closure_threshold >= user_configs["threshold_to_add"]:
        logging.warning(  # Use logging.warning for a potential issue
            f"Trade {trade['id']} is at {round(closure_threshold, 2)}% of liquidation threshold"
        )
        add_margin(trade["id"])


def buy_order(takeprofit):
    lnm.futures_new_trade(
        {
            "type": "m",
            "side": "b",
            "quantity": user_configs["quantity"],
            "leverage": user_configs["leverage"],
            "takeprofit": round(takeprofit),
        }
    )
    logging.info(
        f"Order bought aiming at {takeprofit}"
    )  # Use logging.info instead of print


def adjust_take_profit(trade):
    sum_carry_fees = trade["sum_carry_fees"]
    opening_fee = trade["opening_fee"]
    expected_profit = trade["quantity"] * (
        (1 / trade["price"] - 1 / trade["takeprofit"]) * 100000000
    )
    real_profit = expected_profit - sum_carry_fees - opening_fee
    ideal_profit = trade["quantity"] * (
        (1 / trade["price"] - 1 / (trade["price"] * user_configs["real_profit"]))
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


def get_trades(highest_price_reference):
    buying_diff = user_configs["diff_to_buy"]
    current_price = json.loads(lnm.futures_get_ticker())["index"]

    # Atualiza a referência de preço para o valor mais alto visto até agora
    new_highest_price = max(highest_price_reference, current_price)
    if new_highest_price > highest_price_reference:
        highest_price_reference = new_highest_price
        logging.info(
            f"Novo pico de preço atingido. Nova referência para compra: {highest_price_reference}"
        )

    # logging.info(
    #     f"""Pico: {highest_price_reference}, Atual: {current_price}, Compra: {highest_price_reference - buying_diff}"""
    # )

    running_trades = lnm.futures_get_trades({"type": "running"})
    trades_json = json.loads(running_trades)
    next_buy = highest_price_reference - current_price
    logging.info(f"""Próxima compra: {next_buy}""")
    if (next_buy >= buying_diff) and (len(trades_json) <= user_configs["max_trades"]):
        takeprofit = current_price * user_configs["percentage_to_buy"]
        buy_order(takeprofit)

        # Após comprar, a nova referência de pico se torna o preço atual
        logging.info(
            f"Ordem de compra executada a {current_price}. Resetando referência de pico para este valor."
        )
        highest_price_reference = current_price

    for trade in trades_json:
        get_liquidation_status(trade, current_price)
        adjust_take_profit(trade)

    # Retorna a referência atualizada para o main loop
    return highest_price_reference

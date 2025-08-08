# LNMarkets Trading Bot

This is a simple trading bot for LNMarkets that operates based on a dollar-cost averaging (DCA) strategy. The bot monitors the Bitcoin price and executes buy orders when the price drops by a specified amount from its most recent peak.

## How It Works

The bot follows a simple but effective strategy:

1.  **Initialize Price Reference**: On startup, the bot fetches the current Bitcoin price and sets it as the initial `highest_price_reference`.
2.  **Monitor Price**: The bot continuously checks the Bitcoin price.
3.  **Update Price Peak**: If the current price is higher than `highest_price_reference`, the bot updates the reference to the new peak.
4.  **Buy on Dips**: If the price drops by a configurable amount (`diff_to_buy`) from the `highest_price_reference`, the bot places a buy order.
5.  **Take Profit**: Each buy order has a take-profit level calculated based on a configurable percentage (`percentage_to_buy`).
6.  **Safeguards**:
    *   **Maximum Trades**: The bot will not open new trades if the maximum number of concurrent trades (`max_trades`) is reached.
    *   **Minimum Distance**: The bot will not open a new trade if the current price is too close to an existing open order, preventing clustered trades.
    *   **Add Margin**: The bot will automatically add margin to a position if it gets close to the liquidation price.

## Getting Started

### Prerequisites

*   Python 3.7+
*   An LNMarkets account

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/lnmarkets-trading-bot.git
    cd lnmarkets-trading-bot
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

3.  **Set up your environment variables**:

    Create a `.env` file in the root of the project and add your LNMarkets API credentials:

    ```
    LN_MARKETS_KEY=your_api_key
    LN_MARKETS_SECRET=your_api_secret
    LN_MARKETS_PASSPHRASE=your_api_passphrase
    ```

### Running the Bot

To start the bot, run the `main.py` script:

```bash
uv run main.py
```

The bot will start running and logging its activities to the console.

## Configuration

You can customize the bot's behavior by modifying the `user_configs` dictionary in the `utils.py` file.

| Parameter           | Description                                                                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `diff_to_buy`       | The price difference from the highest reference price that triggers a buy order.                                                                      |
| `percentage_to_buy` | The percentage above the current price to set the take-profit for a new order.                                                                         |
| `real_profit`       | The target profit percentage for a trade after accounting for fees. The bot will adjust the take-profit to achieve this.                                 |
| `max_trades`        | The maximum number of open trades allowed at any given time.                                                                                           |
| `margin`            | The amount of margin to add to a position when it is close to liquidation.                                                                             |
| `quantity`          | The quantity for each trade in USD.                                                                                                                    |
| `leverage`          | The leverage to use for each trade.                                                                                                                    |
| `threshold_to_add`  | The percentage of the liquidation price that triggers adding more margin. For example, `97.5` means margin will be added when the price is at 97.5% of the liquidation price. |
| `safe_guard`        | If `True`, the bot will check for a minimum distance between orders before placing a new one.                                                            |
| `min_order_diff`    | The minimum price difference required between the current price and existing orders to place a new buy order.                                            |

## Dependencies

This project relies on the following Python libraries:

*   `python-dotenv`: For loading environment variables from a `.env` file.
*   `lnmarkets`: The official Python client for the LNMarkets API.


## Disclaimer

This trading bot is provided for educational purposes only. Trading cryptocurrencies involves significant risk, and you should never trade with money you cannot afford to lose. The author is not responsible for any financial losses you may incur. Use this bot at your own risk.

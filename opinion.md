# Opinion.md

Hey! Thanks for asking for my input. Here are some thoughts on the points you raised.

## Price Checking Logic (`utils.py`)

You mentioned you had the impression that if the price goes down and then up again, it's not being registered as a new high. You are 100% correct, and this is a direct consequence of the current trading strategy's logic.

### How it Works Now

1.  The bot keeps track of a `highest_price_reference`, which is the highest price seen since the last purchase.
2.  It only considers making a purchase if the price drops a specific amount (`diff_to_buy`) below this reference price.
3.  A new `highest_price_reference` is only set if the current price exceeds the old reference price.
4.  When a purchase is made, the `highest_price_reference` is reset to the purchase price.

### The "Problem"

Let's walk through your scenario:
- The `highest_price_reference` is, say, **$50,000**.
- The price **goes down** to **$49,500**.
- Then, the price **goes up again** to **$49,800**.

In this case, the bot does **not** register $49,800 as a new high. Why? Because it's still lower than the $50,000 reference price it's holding onto. The bot is essentially waiting for one of two things to happen:
a) The price drops far enough from $50,000 to trigger a buy.
b) The price climbs above $50,000, setting a new reference peak.

This is a "buy-the-dip" strategy. It's designed to buy only when the price has fallen significantly from a recent high.

### Is this a bug?

Not necessarily a bug, but perhaps not the behavior you want. The current logic is sound for the strategy it's implementing. However, if the market is trading sideways or in a channel (bouncing between a floor and a ceiling without making new highs), this logic will result in very few trades.

### How could we change it?

If you want the bot to be more active and capture smaller price swings, we could change the logic to identify "local" peaks instead of just the absolute highest peak.

Here's one idea: instead of just keeping one `highest_price_reference`, we could track the recent price history (e.g., the last `N` prices). From this history, we could identify turning points (when the price stops falling and starts rising). A rise after a fall could establish a new, "local" reference high, from which we could then look for another dip.

This would make the bot more responsive in a ranging market, but it would also be more complex. We'd have to be careful to define what constitutes a "turning point" to avoid trading on insignificant noise.

Let me know what you think of this. We can dive deeper into a potential implementation if this sounds like the right direction.

## Adding Alerts for Price Bounces

You're looking for a way to get notified when the price dips and then bounces, without necessarily changing the buying logic. I think that's a great idea for staying informed about the market's behavior. We can achieve this by adding a bit of state to our price-checking function.

### The Plan

We can introduce a couple of new variables to track the price's recent movement. Let's say we add `previous_price` and `price_trend` to our main loop.

1.  **`previous_price`**: This will store the price from the last time we checked.
2.  **`price_trend`**: This could be `'down'` or `'up'`, indicating the direction of the last price change.

With these two variables, we can detect a "bounce" whenever the `price_trend` changes from `'down'` to `'up'`. When that happens, we can fire off a Telegram message to you.

### What the Code Might Look Like

We would need to modify the `get_trades` function in `utils.py` to accept and return these new state variables. Here’s a rough sketch of how the logic inside the function could look:

```python
def get_trades(highest_price_reference, previous_price, price_trend):
    # ... (existing code to get current_price)

    # Determine the new price trend
    new_trend = price_trend
    if current_price > previous_price:
        new_trend = 'up'
    elif current_price < previous_price:
        new_trend = 'down'

    # Check for a bounce
    if new_trend == 'up' and price_trend == 'down':
        bounce_message = f"Price bounced! From {previous_price} to {current_price}"
        message_handler(bounce_message)

    # ... (the rest of the existing logic for buying and managing trades)

    # Return the updated state
    return highest_price_reference, current_price, new_trend
```

### Important Considerations

-   **State Management**: We'd have to initialize `previous_price` and `price_trend` at the start of the bot, similar to how `highest_price_reference` is initialized.
-   **No Change to Trading**: This addition is purely for notifications. It doesn't interfere with the `highest_price_reference` or the "buy-the-dip" logic. The bot will still only buy when its main conditions are met.
-   **Noise**: We might want to set a minimum threshold for a price change to be considered a trend, to avoid getting spammed with notifications for very small fluctuations. For example, a change of less than $10 might not be considered a trend change.

This approach would give you the visibility you want without altering the core trading strategy. Let me know if this sounds like what you had in mind!
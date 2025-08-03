# utils/price_feed.py

# TEMP MOCK — replace with source_manager later

FAKE_PRICES = {
    "eth": 3000,
    "wbtc": 65000,
    "usdc": 1.0,
    "arb": 1.2,
    "link": 15,
    "sol": 140,
    "matic": 0.9
}

def get_price(symbol):
    return FAKE_PRICES.get(symbol.lower())
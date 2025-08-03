# utils/sources/coingecko.py

import random

def get_price_from_coingecko(symbol):
    # Fake mock price from CoinGecko
    return round(random.uniform(1, 5000), 2)

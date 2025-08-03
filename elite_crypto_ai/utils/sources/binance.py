# utils/sources/binance.py

import random

def get_price_from_binance(symbol):
    # Fake mock price from Binance
    return round(random.uniform(1, 5000), 2)
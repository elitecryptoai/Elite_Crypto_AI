# utils/sources/chainlink.py

import random

def get_price_from_chainlink(symbol):
    # Fake mock price from Chainlink
    return round(random.uniform(1, 5000), 2)
# utils/price_utils.py

import random
from datetime import datetime

# Temporary mock — replace with real historical lookup logic later

def get_historical_price(symbol, timestamp):
    random.seed(hash(symbol + timestamp.isoformat()) % 100000)
    base = 300 if symbol.lower() == "eth" else 60000 if symbol.lower() == "wbtc" else 1
    return round(base * random.uniform(0.9, 1.1), 2)

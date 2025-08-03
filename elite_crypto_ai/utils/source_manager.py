# utils/source_manager.py — Live Multi-Source Pricing

import time
import random
from utils.sources.coingecko import get_price_from_coingecko
from utils.sources.binance import get_price_from_binance
from utils.sources.uniswap import get_price_from_uniswap
from utils.sources.chainlink import get_price_from_chainlink

ETH_TOKENS = ["eth", "wbtc", "usdc", "link", "arb", "op", "matic"]

TOKEN_METADATA = {
    "eth": {"name": "Ethereum", "network": "ethereum"},
    "wbtc": {"name": "Wrapped BTC", "network": "ethereum"},
    "usdc": {"name": "USD Coin", "network": "ethereum"},
    "link": {"name": "Chainlink", "network": "ethereum"},
    "arb": {"name": "Arbitrum", "network": "ethereum"},
    "op": {"name": "Optimism", "network": "ethereum"},
    "matic": {"name": "Polygon", "network": "ethereum"},
}


def get_token_metadata(symbol):
    return TOKEN_METADATA.get(symbol.lower(), {"name": symbol.upper(), "network": "unknown"})


def get_top_tokens(limit=100):
    return [{"symbol": t} for t in ETH_TOKENS[:limit]]


def get_price_change_signal(token):
    return round(random.uniform(-0.05, 0.05), 4)  # mock % change 24h


def get_price(symbol):
    sources = [
        ("binance", get_price_from_binance),
        ("uniswap", get_price_from_uniswap),
        ("chainlink", get_price_from_chainlink),
        ("coingecko", get_price_from_coingecko),
    ]

    for name, fn in sources:
        try:
            price = fn(symbol)
            if price and price > 0:
                print(f"[source_manager] ✅ {name} returned price for {symbol.upper()}: {price}")
                return price
        except Exception as e:
            print(f"[source_manager] ❌ {name} failed for {symbol}: {e}")
            continue

    print(f"[source_manager] ❗ All sources failed for {symbol}")
    return None

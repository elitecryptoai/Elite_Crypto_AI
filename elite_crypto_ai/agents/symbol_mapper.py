# symbol_mapper.py — FINALIZED VERSION WITH FALLBACKS

import json
import os

MAP_FILE = "data/symbol_map.json"

# Default fallback mapping
STATIC_MAP = {
    "wbtc": "WBTC",
    "eth": "ETH",
    "usdc": "USDC",
    "usdt": "USDT",
    "btc": "WBTC",
    "matic": "MATIC",
    "link": "LINK",
    "arb": "ARB",
    "op": "OP"
}


def load_symbol_map():
    if not os.path.exists(MAP_FILE):
        return STATIC_MAP
    with open(MAP_FILE, "r") as f:
        dynamic = json.load(f)
    return {**STATIC_MAP, **dynamic}


def resolve_symbol(symbol):
    symbol = symbol.lower()
    symbol_map = load_symbol_map()
    return symbol_map.get(symbol, symbol.upper())


if __name__ == "__main__":
    print(resolve_symbol("wbtc"))  # WBTC
    print(resolve_symbol("btc"))   # WBTC (fallback to wrapped)
    print(resolve_symbol("sol"))   # SOL (fallback to upper)

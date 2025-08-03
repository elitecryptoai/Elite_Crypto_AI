# utils/cryptoquant.py — Live Whale, Exchange, Miner, Stablecoin Metrics

import os
import json
import requests
from datetime import datetime

CRYPTOQUANT_API_URL = "https://api.cryptoquant.com/v1"
SECRETS_PATH = "secrets/cryptoquant.json"

# Load API key
with open(SECRETS_PATH, "r") as f:
    CRYPTOQUANT_API_KEY = json.load(f).get("cryptoquant_api_key")

HEADERS = {
    "Authorization": f"Bearer {CRYPTOQUANT_API_KEY}"
}

def fetch(endpoint, params=None):
    url = f"{CRYPTOQUANT_API_URL}/{endpoint}"
    try:
        res = requests.get(url, headers=HEADERS, params=params, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"❌ CryptoQuant fetch error ({endpoint}): {e}")
        return None

# --------- METRIC WRAPPERS ---------

def get_exchange_flow(asset="btc"):
    return fetch(f"onchain/exchange-flows/netflow", {"symbol": asset})

def get_whale_tx(asset="btc"):
    return fetch(f"onchain/whales/transactions", {"symbol": asset})

def get_miner_reserve(asset="btc"):
    return fetch(f"onchain/miners/reserve", {"symbol": asset})

def get_stablecoin_ratio():
    return fetch("onchain/stablecoins/exchange-reserve-ratio", {})

# --------- BATCH WRAPPER ---------

def get_all_metrics(asset="btc"):
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "asset": asset,
        "exchange_flows": get_exchange_flow(asset),
        "whale_tx": get_whale_tx(asset),
        "miner_reserve": get_miner_reserve(asset),
        "stablecoin_ratio": get_stablecoin_ratio()
    }

# --------- Save Daily Cache ---------

def save_metrics(asset="btc", output_folder="intel/metrics"):
    os.makedirs(output_folder, exist_ok=True)
    metrics = get_all_metrics(asset)
    filename = f"{output_folder}/{asset}_metrics.json"
    with open(filename, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"✅ Saved metrics for {asset} → {filename}")

# ✅ Test
if __name__ == "__main__":
    for coin in ["btc", "eth", "sol", "matic", "link"]:
        save_metrics(coin)

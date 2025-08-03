# intel_engine.py — Upgraded with Real CryptoQuant Pro Data

import os
import json
from datetime import datetime
from utils.cryptoquant import get_all_metrics

MARKET_STATUS_FILE = "intel/market_status.json"

TOP_COINS = ["btc", "eth", "sol", "matic", "link"]

def analyze_macro():
    macro = {
        "timestamp": datetime.utcnow().isoformat(),
        "macro_trend": "neutral",
        "intel_score": 0.5,
        "assets": {}
    }

    score_total = 0
    count = 0

    for coin in TOP_COINS:
        data = get_all_metrics(coin)
        macro["assets"][coin] = data

        # Scoring logic
        score = 0

        # Exchange inflow → bearish
        flows = data.get("exchange_flows", {}).get("result", [])
        if flows:
            latest = flows[-1]
            netflow = latest.get("value", 0)
            if netflow > 0:
                score -= 1
            else:
                score += 1

        # Whale activity → large tx = bullish
        whales = data.get("whale_tx", {}).get("result", [])
        if whales:
            score += min(len(whales), 5) * 0.2

        # Miner reserves → decreasing = bearish
        miners = data.get("miner_reserve", {}).get("result", [])
        if len(miners) >= 2:
            delta = miners[-1]["value"] - miners[-2]["value"]
            if delta < 0:
                score -= 0.5
            else:
                score += 0.5

        # Stablecoin ratio
        stable = data.get("stablecoin_ratio", {}).get("result", [])
        if stable:
            ratio = stable[-1].get("value", 0)
            if ratio > 1:
                score += 0.25
            else:
                score -= 0.25

        score_total += score
        count += 1

    macro["intel_score"] = round(max(0.0, min(1.0, 0.5 + score_total / (count * 4.0))), 3)

    # Trend label
    if macro["intel_score"] >= 0.7:
        macro["macro_trend"] = "bullish"
    elif macro["intel_score"] <= 0.3:
        macro["macro_trend"] = "bearish"

    os.makedirs(os.path.dirname(MARKET_STATUS_FILE), exist_ok=True)
    with open(MARKET_STATUS_FILE, "w") as f:
        json.dump(macro, f, indent=2)

    print(f"✅ Market intel written to {MARKET_STATUS_FILE}")

# ✅ Test
if __name__ == "__main__":
    analyze_macro()

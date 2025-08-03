# coin_generator.py

import json
from utils.source_manager import get_token_metadata, get_top_tokens
from utils.data_loader import load_price_data
from utils.signal_utils import detect_volume_spike, detect_volatility_spike

OUTPUT_PATH = "data/generated_coins.json"


def generate_candidate_coins(limit=100):
    top = get_top_tokens(limit)
    selected = []

    for token in top:
        symbol = token["symbol"]
        data = load_price_data(symbol)
        if data is None or data.empty:
            continue

        volume_signal = detect_volume_spike(data)
        vol_spike = detect_volatility_spike(data)

        if volume_signal or vol_spike:
            meta = get_token_metadata(symbol)
            selected.append({
                "symbol": symbol,
                "volume_spike": volume_signal,
                "volatility_spike": vol_spike,
                "name": meta.get("name"),
                "network": meta.get("network"),
            })

    with open(OUTPUT_PATH, "w") as f:
        json.dump(selected, f, indent=2)

    return selected


if __name__ == "__main__":
    coins = generate_candidate_coins()
    print(json.dumps(coins, indent=2))
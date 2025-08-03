"""
price_feed_agent.py

✅ Fetches real-time prices for coins using SourceManager
✅ Outputs to data/price_feed.json
"""

import json
import os
from agents.source_manager import SourceManager
from datetime import datetime

class PriceFeedAgent:
    def __init__(self,
                 coin_list_path="data/coins_for_strategy.json",
                 output_path="data/price_feed.json"):
        self.coin_list_path = coin_list_path
        self.output_path = output_path
        self.source = SourceManager()

    def load_coins(self):
        if not os.path.exists(self.coin_list_path):
            raise Exception("Missing coins_for_strategy.json")
        with open(self.coin_list_path) as f:
            data = json.load(f)
        return data.get("coins", [])

    def build_price_feed(self):
        coins = self.load_coins()
        prices = {}
        for coin in coins:
            try:
                price = self.source.get_price(coin)
                prices[coin.lower()] = round(price, 6)
            except Exception as e:
                print(f"[PriceFeedAgent] ❌ Failed to fetch {coin}: {e}")
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "prices": prices
        }
        with open(self.output_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"[PriceFeedAgent] ✅ Price feed built for {len(prices)} tokens")

# ✅ Test
if __name__ == "__main__":
    agent = PriceFeedAgent()
    agent.build_price_feed()

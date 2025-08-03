# search_agent.py — ULTRA HYBRID VERSION (Elite + CoinGecko + Social Powered)

import requests
import time
import json
import os
from datetime import datetime
from utils.signal_utils import get_social_buzz, get_trend_strength, get_volume_signal
from utils.intel_loader import load_latest_intel
from utils.social_scanner import scan_reddit, scan_twitter, scan_google_trends
from utils.thematic_classifier import classify_token_theme
from utils.token_ranker import rank_tokens_by_signal_strength

ETH_OUTPUT = "data/coin_scan_results.json"
FULL_OUTPUT = "data/coin_scan_global.json"
NON_ETH_ALERTS = "data/top_non_eth_alerts.json"
SEARCH_LOG = "logs/search_log.json"

class SearchAgent:
    def __init__(self, max_coins=1000):
        self.api = "https://api.coingecko.com/api/v3"
        self.max_coins = max_coins
        self.sleep_between_pages = 1.2
        self.eth_tokens = []
        self.non_eth_tokens = []
        self.global_ranked = []
        self.reddit_data = {}
        self.twitter_data = {}
        self.trends_data = {}
        self.intel = load_latest_intel()
        self.results = []

    def fetch_market_data(self, page):
        url = f"{self.api}/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 250,
            "page": page,
            "sparkline": False,
            "price_change_percentage": "24h,7d"
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    def is_eth_token(self, coin):
        return coin.get("platforms", {}).get("ethereum") is not None

    def load_social_signals(self):
        print("[SearchAgent] 🧠 Loading social alpha...")
        self.reddit_data = scan_reddit()
        self.twitter_data = scan_twitter()
        self.trends_data = scan_google_trends()

    def score_coin(self, coin):
        change_7d = coin.get("price_change_percentage_7d_in_currency", 0) or 0
        vol_24h = coin.get("total_volume", 0) or 0
        base_score = (change_7d / 100) + (vol_24h / 1e9)

        symbol = coin["symbol"].lower()
        intel_score = self.intel.get(symbol, {}).get("intel_score", 0)
        volume_signal = get_volume_signal(symbol)
        trend_strength = get_trend_strength(symbol)
        buzz = get_social_buzz(symbol)

        reddit_score = self.reddit_data.get(symbol, 0)
        twitter_score = self.twitter_data.get(symbol, 0)
        trend_score = self.trends_data.get(symbol, 0)
        social_composite = reddit_score * 0.4 + twitter_score * 0.4 + trend_score * 0.2

        multiplier = 1
        if intel_score >= 3:
            multiplier += 0.3
        if volume_signal > 1.5:
            multiplier += 0.3
        if trend_strength > 0.7:
            multiplier += 0.2
        if buzz > 0.3:
            multiplier += 0.2
        if social_composite > 0.4:
            multiplier += 0.3

        score = base_score * multiplier + social_composite
        return round(score, 6)

    def scan(self):
        self.load_social_signals()
        all_entries = []
        page = 1

        while len(all_entries) < self.max_coins:
            data = self.fetch_market_data(page)
            if not data:
                break
            for coin in data:
                symbol = coin["symbol"].lower()
                score = self.score_coin(coin)
                entry = {
                    "symbol": symbol,
                    "score": score,
                    "price": coin.get("current_price", 0),
                    "theme": classify_token_theme(symbol),
                    "intel": self.intel.get(symbol, {}),
                    "reddit": self.reddit_data.get(symbol, 0),
                    "twitter": self.twitter_data.get(symbol, 0),
                    "trend": self.trends_data.get(symbol, 0)
                }
                all_entries.append(entry)
                if self.is_eth_token(coin):
                    self.eth_tokens.append(entry)
                else:
                    self.non_eth_tokens.append(entry)
            page += 1
            time.sleep(self.sleep_between_pages)

        self.eth_tokens.sort(key=lambda x: -x["score"])
        self.non_eth_tokens.sort(key=lambda x: -x["score"])
        self.global_ranked = sorted(all_entries, key=lambda x: -x["score"])

        timestamp = datetime.utcnow().isoformat()
        json.dump({"timestamp": timestamp, "coins": self.eth_tokens}, open(ETH_OUTPUT, "w"), indent=2)
        json.dump({"timestamp": timestamp, "coins": self.global_ranked}, open(FULL_OUTPUT, "w"), indent=2)
        json.dump({"timestamp": timestamp, "top_non_eth": self.non_eth_tokens[:6]}, open(NON_ETH_ALERTS, "w"), indent=2)
        json.dump({"timestamp": timestamp, "top_candidates": self.global_ranked[:25]}, open("data/coins_to_test.json", "w"), indent=2)

        with open(SEARCH_LOG, "a") as log:
            log.write(json.dumps({
                "timestamp": timestamp,
                "top_candidates": self.global_ranked[:25]
            }) + "\n")

        print(f"🔍 SearchAgent Complete → ETH: {len(self.eth_tokens)} | Non-ETH: {len(self.non_eth_tokens)}")


if __name__ == "__main__":
    SearchAgent().scan()

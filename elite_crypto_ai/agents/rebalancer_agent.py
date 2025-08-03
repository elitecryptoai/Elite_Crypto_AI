# rebalancer_agent.py — ULTRA ELITE FUSION VERSION

import json
import os
from datetime import datetime
from utils.wallet import get_wallet_holdings
from utils.price_feed import get_price
from utils.memory import load_allocation_memory, save_allocation_memory

PORTFOLIO_PATH = "wallets/portfolio.json"
MARKET_STATUS = "data/market_status.json"
REBALANCE_LOG = "logs/rebalance_log.json"
OUTPUT_PATH = "data/rebalance_plan.json"
DRIFT_THRESHOLD = 0.03  # 3% drift tolerance
PORTFOLIO_SIZE = 10000  # assume $10K default portfolio size


class RebalancerAgent:
    def __init__(self):
        self.target_alloc = {}
        self.market = {}
        self.holdings = {}
        self.prices = {}
        self.plan = {
            "timestamp": datetime.utcnow().isoformat(),
            "market_alert": "neutral",
            "drift_corrections": {}
        }

    def load_all(self):
        if os.path.exists(PORTFOLIO_PATH):
            with open(PORTFOLIO_PATH) as f:
                self.target_alloc = json.load(f)
        if os.path.exists(MARKET_STATUS):
            with open(MARKET_STATUS) as f:
                self.market = json.load(f)
        self.holdings = get_wallet_holdings()
        self.prices = {sym: get_price(sym) for sym in self.holdings}

    def normalize_alloc(self):
        all_tokens = {}
        for token, info in self.target_alloc.items():
            token = token.lower()
            all_tokens[token] = all_tokens.get(token, 0) + info["amount_usd"]
        total = sum(all_tokens.values())
        return {k: v / total for k, v in all_tokens.items()}

    def compute_drift(self, normalized):
        for token, target_pct in normalized.items():
            price = self.prices.get(token)
            if price is None:
                continue
            target_val = target_pct * PORTFOLIO_SIZE
            actual_qty = self.holdings.get(token, 0)
            actual_val = actual_qty * price
            drift = (actual_val - target_val) / target_val
            if abs(drift) > DRIFT_THRESHOLD:
                self.plan["drift_corrections"][token] = {
                    "target_val": round(target_val, 2),
                    "actual_val": round(actual_val, 2),
                    "drift_pct": round(drift, 4)
                }

    def write_output(self):
        os.makedirs("data", exist_ok=True)
        with open(OUTPUT_PATH, "w") as f:
            json.dump(self.plan, f, indent=2)

        log_entry = {"timestamp": self.plan["timestamp"], "plan": self.plan["drift_corrections"]}
        if os.path.exists(REBALANCE_LOG):
            with open(REBALANCE_LOG, "r") as f:
                log = json.load(f)
        else:
            log = []
        log.append(log_entry)
        with open(REBALANCE_LOG, "w") as f:
            json.dump(log[-200:], f, indent=2)
        save_allocation_memory(self.plan["drift_corrections"])

    def run(self):
        print("🔄 RebalancerAgent running...")
        self.load_all()
        if self.market.get("status") == "bearish":
            print("🛑 Market is bearish — skipping rebalancing.")
            self.plan["market_alert"] = "bearish"
        else:
            norm = self.normalize_alloc()
            self.compute_drift(norm)
        self.write_output()
        print(f"✅ Rebalance plan complete with {len(self.plan['drift_corrections'])} corrections.")


if __name__ == "__main__":
    RebalancerAgent().run()
    
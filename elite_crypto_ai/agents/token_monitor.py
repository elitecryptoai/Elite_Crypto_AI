import os
import json
from datetime import datetime
from utils.token_utils import get_price_history, get_live_price, get_token_score

MONITOR_FILE = "wallets/portfolio.json"
EXIT_LOG = "logs/token_exit_log.json"
SWAP_SIGNAL_FILE = "data/swap_signals.json"

THRESHOLD_DROP = -0.15  # -15% drop triggers review
SCORE_DECAY_THRESHOLD = -0.25

class TokenMonitor:
    def __init__(self):
        self.portfolio = {}
        self.exits = []
        self.swaps = []

    def load_portfolio(self):
        if not os.path.exists(MONITOR_FILE):
            print("[Monitor] ❌ Portfolio file not found.")
            return False
        with open(MONITOR_FILE, "r") as f:
            self.portfolio = json.load(f)
        return True

    def analyze_token(self, token, data):
        symbol = token.lower()
        history = get_price_history(symbol)
        current = get_live_price(symbol)
        intel_score = get_token_score(symbol)

        if not history or not current:
            return

        initial = history[0]
        drop = (current - initial) / initial

        if drop < THRESHOLD_DROP or intel_score < SCORE_DECAY_THRESHOLD:
            self.exits.append({
                "symbol": symbol,
                "drop_pct": round(drop, 4),
                "intel_score": intel_score,
                "timestamp": datetime.utcnow().isoformat()
            })
            self.swaps.append(symbol)

    def process_portfolio(self):
        for tier in ["safe", "medium", "risky"]:
            tokens = self.portfolio.get(tier, {})
            for symbol in tokens:
                self.analyze_token(symbol, tokens[symbol])

    def save_outputs(self):
        if self.exits:
            with open(EXIT_LOG, "a") as log:
                log.write(json.dumps({
                    "timestamp": datetime.utcnow().isoformat(),
                    "exits": self.exits
                }) + "\n")

        if self.swaps:
            with open(SWAP_SIGNAL_FILE, "w") as f:
                json.dump({
                    "timestamp": datetime.utcnow().isoformat(),
                    "candidates": self.swaps
                }, f, indent=2)

        print(f"[Monitor] 🧠 Evaluated {len(self.exits)} token exits.")

    def run(self):
        if self.load_portfolio():
            self.process_portfolio()
            self.save_outputs()

if __name__ == "__main__":
    TokenMonitor().run()

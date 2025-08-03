# signal_miner.py — ANALYZES BEST PERFORMING STRATEGY SIGNALS

import os
import json
from collections import defaultdict

STRATEGY_META_PATH = "intel/strategy_metadata.json"
PERFORMANCE_PATH = "intel/performance_metrics.json"
OUTPUT_PATH = "intel/best_signals.json"

class SignalMiner:
    def __init__(self):
        self.metadata = {}
        self.performance = {}
        self.signal_scores = defaultdict(list)

    def load_data(self):
        if os.path.exists(STRATEGY_META_PATH):
            with open(STRATEGY_META_PATH, "r") as f:
                self.metadata = json.load(f)
        if os.path.exists(PERFORMANCE_PATH):
            with open(PERFORMANCE_PATH, "r") as f:
                self.performance = json.load(f)

    def analyze_signals(self):
        for token, meta in self.metadata.items():
            signals = meta.get("signal_triggers", [])
            perf = self.performance.get(token, {})
            sharpe = perf.get("sharpe", 0)
            drawdown = perf.get("drawdown", 1)
            hit_rate = perf.get("hit_rate", 0)
            score = sharpe * 0.6 + hit_rate * 0.3 - drawdown * 0.1

            for signal in signals:
                self.signal_scores[signal].append(score)

    def save_best_signals(self):
        avg_scores = {
            signal: round(sum(scores)/len(scores), 4)
            for signal, scores in self.signal_scores.items() if scores
        }
        sorted_signals = sorted(avg_scores.items(), key=lambda x: -x[1])
        best = [s for s, _ in sorted_signals]

        with open(OUTPUT_PATH, "w") as f:
            json.dump({"best_signals": best, "scores": avg_scores}, f, indent=2)
        print(f"✅ Saved best signals to {OUTPUT_PATH}")

    def run(self):
        print("🧠 Running Signal Miner...")
        self.load_data()
        self.analyze_signals()
        self.save_best_signals()

if __name__ == "__main__":
    SignalMiner().run()

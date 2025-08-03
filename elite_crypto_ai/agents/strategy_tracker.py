# strategy_tracker.py — ULTRA ELITE STRATEGY PERFORMANCE TRACKER

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from utils.data_loader import load_strategy_results

TRACKER_FILE = "logs/strategy_feedback.json"

class StrategyTracker:
    def __init__(self):
        self.results_dir = "results/strategy_runs"
        self.feedback = {}

    def safe_load(self, path):
        try:
            return pd.read_csv(path)
        except:
            return None

    def calculate_metrics(self, df):
        if df is None or len(df) < 5:
            return None

        df = df.copy()
        df['returns'] = df['close'].pct_change().fillna(0) * df['signal'].shift(1).fillna(0)
        df['equity'] = (1 + df['returns']).cumprod()
        equity_curve = df['equity']

        # Sharpe Ratio
        sharpe = np.mean(df['returns']) / (np.std(df['returns']) + 1e-8) * np.sqrt(252)

        # Max Drawdown
        peak = equity_curve.cummax()
        drawdown = (equity_curve - peak) / peak
        max_dd = drawdown.min()

        # Hit Rate & Win/Loss
        wins = df[df['returns'] > 0].shape[0]
        losses = df[df['returns'] < 0].shape[0]
        total = wins + losses
        hit_rate = wins / total if total > 0 else 0

        return {
            "sharpe": round(sharpe, 3),
            "max_drawdown": round(max_dd, 3),
            "hit_rate": round(hit_rate, 3),
            "trades": int(total),
            "gain": round(equity_curve.iloc[-1] - 1.0, 3)
        }

    def scan_results(self):
        if not os.path.exists(self.results_dir):
            print("❌ No strategy results found.")
            return

        for file in os.listdir(self.results_dir):
            if not file.endswith(".csv"):
                continue
            token = file.replace(".csv", "")
            df = self.safe_load(os.path.join(self.results_dir, file))
            metrics = self.calculate_metrics(df)
            if metrics:
                self.feedback[token] = metrics

    def save(self):
        os.makedirs("logs", exist_ok=True)
        with open(TRACKER_FILE, "w") as f:
            json.dump(self.feedback, f, indent=2)

    def run(self):
        print("🔎 Running Strategy Tracker...")
        self.scan_results()
        self.save()
        print(f"✅ Strategy feedback saved → {TRACKER_FILE}")

if __name__ == "__main__":
    StrategyTracker().run()

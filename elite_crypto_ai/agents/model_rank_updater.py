# model_rank_updater.py — FINAL ULTRA ELITE VERSION 🚀
# Combines lifetime ROI, rolling accuracy, recent scores, and self-healing model ranking

import os
import json
from collections import defaultdict
from datetime import datetime, timedelta
import pandas as pd

FORECAST_LOG = "logs/forecast_history.json"
MODEL_RANK_FILE = "logs/forecast_model_rank.json"

WINDOW = 200  # How many recent forecasts to evaluate
ROLLOUT_DAYS = 14  # Fresh rolling score weight

class ModelRankUpdater:
    def __init__(self):
        self.history = []
        self.now = datetime.utcnow()
        self.df = pd.DataFrame()
        self.model_scores = defaultdict(lambda: {"wins": 0, "total": 0, "roi": []})

    def load_forecast_history(self):
        if os.path.exists(FORECAST_LOG):
            with open(FORECAST_LOG, "r") as f:
                self.history = json.load(f)
            self.df = pd.DataFrame(self.history)
            self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])
        else:
            print("⚠️ No forecast history found.")

    def score_forecasts(self):
        recent = self.df.sort_values("timestamp").tail(WINDOW)

        for i, row in recent.iterrows():
            try:
                model = row["forecast"].get("model_used", "unknown").lower()
                label = row["forecast"].get("forecast_label", "neutral").lower()
                entry_price = row.get("entry_price", 0)

                # Find next future price for same token
                future = self.df[
                    (self.df.token == row.token) & (self.df.timestamp > row.timestamp)
                ].sort_values("timestamp")
                if future.empty:
                    continue
                resolved_price = future.iloc[0].price
                pct = (resolved_price - entry_price) / entry_price if entry_price else 0

                hit = (
                    label == "bullish" and pct > 0.01 or
                    label == "bearish" and pct < -0.01 or
                    label == "neutral" and abs(pct) <= 0.01
                )

                if hit:
                    self.model_scores[model]["wins"] += 1
                self.model_scores[model]["total"] += 1
                self.model_scores[model]["roi"].append(pct)
            except Exception as e:
                print(f"❌ Scoring error: {e}")

    def compute_rank(self):
        weighted = []
        for model, data in self.model_scores.items():
            if data["total"] == 0:
                continue
            acc = data["wins"] / data["total"]
            avg_roi = sum(data["roi"]) / len(data["roi"]) if data["roi"] else 0
            recency_boost = self.df[self.df.forecast.apply(lambda f: f.get("model_used", "").lower() == model and self.now - pd.to_datetime(f["timestamp"]) < timedelta(days=ROLLOUT_DAYS))].shape[0]
            weight = round((acc + avg_roi + recency_boost * 0.001), 4)
            weighted.append((model, weight))

        weighted.sort(key=lambda x: -x[1])
        return [m for m, _ in weighted] or ["gpt-4"]

    def write_rank(self, rank):
        os.makedirs("logs", exist_ok=True)
        with open(MODEL_RANK_FILE, "w") as f:
            json.dump(rank, f, indent=2)

    def run(self):
        print("🧠 Running Model Rank Updater...")
        self.load_forecast_history()
        self.score_forecasts()
        rank = self.compute_rank()
        self.write_rank(rank)
        print(f"✅ Model rank updated: {rank}")

if __name__ == "__main__":
    ModelRankUpdater().run()

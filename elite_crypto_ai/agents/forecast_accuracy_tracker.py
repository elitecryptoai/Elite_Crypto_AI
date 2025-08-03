# forecast_accuracy_tracker.py — ULTRA ELITE (FULL INTEGRATION + SCORING + LEARNING)

import os
import json
from datetime import datetime
from utils.price_utils import get_historical_price
from utils.memory import read_recent_forecasts, record_accuracy_score

FORECAST_HISTORY_LOG = "logs/forecast_history.json"
ACCURACY_LOG = "logs/forecast_accuracy.json"

class ForecastAccuracyTracker:
    def __init__(self):
        self.history = []
        self.scores = {}

    def load_forecast_history(self):
        if os.path.exists(FORECAST_HISTORY_LOG):
            with open(FORECAST_HISTORY_LOG, "r") as f:
                self.history = json.load(f)
        else:
            print("⚠️ No forecast history found.")
            self.history = []

    def evaluate_forecast(self, entry):
        token = entry["token"]
        forecast_label = entry["forecast"]["forecast_label"].lower()
        entry_price = entry.get("entry_price", 0)
        timestamp = entry.get("timestamp")

        try:
            price_now = get_historical_price(token, timestamp)
            price_change = (price_now - entry_price) / entry_price

            correct = (
                (forecast_label == "bullish" and price_change > 0.01) or
                (forecast_label == "bearish" and price_change < -0.01) or
                (forecast_label == "neutral" and -0.01 <= price_change <= 0.01)
            )

            score = {
                "token": token,
                "forecast": forecast_label,
                "price_change": round(price_change, 4),
                "correct": correct,
                "timestamp": timestamp
            }
            return score
        except Exception as e:
            print(f"❌ Error evaluating {token}: {e}")
            return None

    def update_scores(self):
        self.scores = {}
        for entry in self.history[-200:]:  # Limit to last 200
            result = self.evaluate_forecast(entry)
            if result:
                token = result["token"]
                if token not in self.scores:
                    self.scores[token] = []
                self.scores[token].append(result)

    def save_accuracy_log(self):
        os.makedirs("logs", exist_ok=True)
        with open(ACCURACY_LOG, "w") as f:
            json.dump(self.scores, f, indent=2)

    def summarize_accuracy(self):
        summary = {}
        for token, results in self.scores.items():
            total = len(results)
            correct = sum(1 for r in results if r["correct"])
            avg_change = sum(r["price_change"] for r in results) / total
            summary[token] = {
                "total_forecasts": total,
                "correct_count": correct,
                "accuracy_pct": round(correct / total, 3),
                "avg_price_change": round(avg_change, 4)
            }
        return summary

    def record_scores(self):
        summary = self.summarize_accuracy()
        for token, stats in summary.items():
            record_accuracy_score(token, stats)

    def run(self):
        print("📊 Running Forecast Accuracy Tracker...")
        self.load_forecast_history()
        self.update_scores()
        self.save_accuracy_log()
        self.record_scores()
        print("✅ Accuracy tracking complete.")

if __name__ == "__main__":
    ForecastAccuracyTracker().run()

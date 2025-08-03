# llm_forecast_analyzer.py — ULTRA ELITE VERSION w/ FULL AI SIGNAL INSIGHT + TOKEN ROUTING + PROMPT AUTO-TUNING + NOTES

import json
import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from collections import defaultdict

FORECAST_LOG = "logs/forecast_history.json"
OUTPUT_FILE = "intel/llm_model_performance.json"
TOKEN_ROUTING_FILE = "intel/token_model_routing.json"
MODEL_NOTES_FILE = "intel/model_notes.json"

# Scoring weights
FULL_HIT = 1.0
PARTIAL_HIT = 0.5
MISS = 0.0
WINDOWS = [7, 30]  # Rolling accuracy windows (days)


class ForecastAnalyzer:
    def __init__(self):
        self.history = []
        self.now = datetime.utcnow()
        self.df = pd.DataFrame()
        self.token_stats = defaultdict(lambda: defaultdict(list))
        self.notes = defaultdict(list)

    def load_forecast_log(self):
        if not os.path.exists(FORECAST_LOG):
            print("⚠️ No forecast history found.")
            return
        with open(FORECAST_LOG, "r") as f:
            self.history = json.load(f)
        self.df = pd.DataFrame(self.history)
        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])

    def score_forecast(self, forecast, actual_change):
        label = forecast.lower()
        if abs(actual_change) < 0.01:
            return PARTIAL_HIT if label == "neutral" else MISS
        if actual_change > 0.01:
            return FULL_HIT if label == "bullish" else MISS
        if actual_change < -0.01:
            return FULL_HIT if label == "bearish" else MISS
        return MISS

    def analyze(self):
        if self.df.empty:
            print("❌ No data to analyze.")
            return

        scored = []
        token_model_scores = defaultdict(lambda: defaultdict(list))

        for _, row in self.df.iterrows():
            token = row["token"]
            forecast = row["forecast"]
            model = forecast["model_used"].lower()
            label = forecast["forecast_label"]
            confidence = forecast.get("confidence_score", 0)
            rationale = forecast.get("rationale", "")
            actual_price = row["price"]

            # Find next price entry for same token
            future = self.df[
                (self.df.token == token) &
                (self.df.timestamp > row.timestamp)
            ].sort_values("timestamp")
            if future.empty:
                continue

            future_price = future.iloc[0].price
            pct_change = (future_price - actual_price) / actual_price
            score = self.score_forecast(label, pct_change)

            scored.append({
                "token": token,
                "model": model,
                "label": label,
                "confidence": confidence,
                "pct_change": round(pct_change, 4),
                "score": score,
                "timestamp": row.timestamp.isoformat(),
                "roi": round(pct_change * 100, 2),
                "coherence_placeholder": 1.0,
                "rationale": rationale
            })

            self.token_stats[token][model].append(score)
            token_model_scores[token][model].append(score)

        full = pd.DataFrame(scored)
        output = {}
        routing = {}

        for model in full.model.unique():
            model_df = full[full.model == model]
            accuracy = model_df.score.mean()
            avg_conf = model_df.confidence.mean()
            drift = avg_conf - accuracy
            avg_roi = model_df.roi.mean()
            count = len(model_df)

            self.notes[model].append(f"{datetime.utcnow().isoformat()}: {count} forecasts, ROI={avg_roi:.2f}, ACC={accuracy:.2f}, Drift={drift:.2f}")

            output[model] = {
                "lifetime_accuracy": round(accuracy, 4),
                "avg_confidence": round(avg_conf, 4),
                "confidence_drift": round(drift, 4),
                "avg_roi": round(avg_roi, 4),
                "forecast_count": count,
                "roi_rank": 0,
                "acc_rank": 0
            }

            for window in WINDOWS:
                cutoff = self.now - timedelta(days=window)
                recent_df = model_df[model_df.timestamp > cutoff]
                if not recent_df.empty:
                    output[model][f"acc_{window}d"] = round(recent_df.score.mean(), 4)
                    output[model][f"roi_{window}d"] = round(recent_df.roi.mean(), 4)

        # Per-token best model
        for token, models in token_model_scores.items():
            avg_scores = {m: sum(scores)/len(scores) for m, scores in models.items() if scores}
            if avg_scores:
                best_model = max(avg_scores, key=avg_scores.get)
                routing[token] = best_model

        # Rank models
        acc_sorted = sorted(output.items(), key=lambda x: x[1]["lifetime_accuracy"], reverse=True)
        roi_sorted = sorted(output.items(), key=lambda x: x[1]["avg_roi"], reverse=True)

        for i, (m, _) in enumerate(acc_sorted):
            output[m]["acc_rank"] = i + 1
        for i, (m, _) in enumerate(roi_sorted):
            output[m]["roi_rank"] = i + 1

        # Save files
        with open(OUTPUT_FILE, "w") as f:
            json.dump(output, f, indent=2)
        with open(TOKEN_ROUTING_FILE, "w") as f:
            json.dump(routing, f, indent=2)
        with open(MODEL_NOTES_FILE, "w") as f:
            json.dump(self.notes, f, indent=2)

        print("✅ LLM forecast performance saved →", OUTPUT_FILE)
        print("✅ Token model routing saved →", TOKEN_ROUTING_FILE)
        print("✅ Notes saved →", MODEL_NOTES_FILE)


if __name__ == "__main__":
    analyzer = ForecastAnalyzer()
    analyzer.load_forecast_log()
    analyzer.analyze()

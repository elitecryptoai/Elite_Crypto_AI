# forecast_memory_logger.py — ULTRA ELITE (Memory Logger + Reason Archive + Forecast Debug)

import os
import json
from datetime import datetime

FORECAST_HISTORY_LOG = "logs/forecast_history.json"
REASON_ARCHIVE_FILE = "logs/forecast_reasons.json"
MODEL_ROTATION_LOG = "logs/forecast_model_rotation.json"

class ForecastMemoryLogger:
    def __init__(self):
        self.history = []
        self.reasons = {}
        self.rotation = []

    def load_forecasts(self):
        if os.path.exists(FORECAST_HISTORY_LOG):
            with open(FORECAST_HISTORY_LOG, "r") as f:
                self.history = json.load(f)
        else:
            print("⚠️ No forecast history found.")
            self.history = []

    def extract_reasons(self):
        for entry in self.history:
            token = entry["token"]
            rationale = entry["forecast"].get("rationale", "N/A")
            model = entry["forecast"].get("model_used", "UNKNOWN")
            ts = entry["timestamp"]
            if token not in self.reasons:
                self.reasons[token] = []
            self.reasons[token].append({
                "timestamp": ts,
                "rationale": rationale,
                "model": model
            })

    def track_rotation(self):
        rotation = {}
        for entry in self.history:
            model = entry["forecast"].get("model_used", "UNKNOWN")
            if model not in rotation:
                rotation[model] = 0
            rotation[model] += 1
        self.rotation = rotation

    def save(self):
        os.makedirs("logs", exist_ok=True)
        with open(REASON_ARCHIVE_FILE, "w") as f:
            json.dump(self.reasons, f, indent=2)
        with open(MODEL_ROTATION_LOG, "w") as f:
            json.dump(self.rotation, f, indent=2)

    def run(self):
        print("🧠 Running Forecast Memory Logger...")
        self.load_forecasts()
        self.extract_reasons()
        self.track_rotation()
        self.save()
        print("✅ Memory log + rotation saved.")

if __name__ == "__main__":
    ForecastMemoryLogger().run()

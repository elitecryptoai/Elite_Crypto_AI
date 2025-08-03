# report_builder.py

import json
import os
from datetime import datetime

FORECAST_LOG = "data/forecast_log.json"
ACCURACY_LOG = "data/forecast_accuracy.json"


def load_latest_forecasts():
    if not os.path.exists(FORECAST_LOG):
        return []
    with open(FORECAST_LOG, "r") as f:
        forecasts = json.load(f)
    latest = {}
    for f in forecasts:
        sym = f["symbol"]
        if sym not in latest or f["timestamp"] > latest[sym]["timestamp"]:
            latest[sym] = f
    return latest


def load_accuracy():
    if not os.path.exists(ACCURACY_LOG):
        return {}
    with open(ACCURACY_LOG, "r") as f:
        return json.load(f)


def build_forecast_report():
    latest = load_latest_forecasts()
    accuracy = load_accuracy()
    lines = ["📊 FORECAST SUMMARY"]
    for symbol, f in latest.items():
        lines.append(f"\n🔹 {symbol} ({f['model']}):")
        for k, v in f["forecast"].items():
            lines.append(f"  • {k.title()}: {v}")

    lines.append("\n🎯 MODEL ACCURACY")
    for model_key, score in accuracy.items():
        pct = (score["correct"] / score["total"]) * 100 if score["total"] > 0 else 0
        lines.append(f"  • {model_key}: {score['correct']}/{score['total']} ({pct:.1f}%)")

    lines.append("\n🧠 ADAPTIVE STRATEGY USE:")
    lines.append("  • Strategy selection is now influenced by short-term trend forecasts.")
    lines.append("  • RSPS/Momentum for bullish, MCA/Hedge for bearish, DCA/Vol for sideways.")

    return "\n".join(lines)


if __name__ == "__main__":
    print(build_forecast_report())

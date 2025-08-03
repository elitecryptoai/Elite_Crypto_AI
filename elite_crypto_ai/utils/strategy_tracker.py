# utils/strategy_tracker.py

import os
import json

PERF_FILE = "intel/performance_metrics.json"

def get_strategy_performance():
    if not os.path.exists(PERF_FILE):
        return {}
    with open(PERF_FILE, "r") as f:
        return json.load(f)

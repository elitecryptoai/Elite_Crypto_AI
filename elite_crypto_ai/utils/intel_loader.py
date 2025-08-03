# utils/intel_loder.py
import json
import os

INTEL_FILE = "data/intel_report.json"


def load_latest_intel():
    if not os.path.exists(INTEL_FILE):
        return {}
    with open(INTEL_FILE, "r") as f:
        return json.load(f)

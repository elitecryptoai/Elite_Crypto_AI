# utils/portfolio_loader
import os
import json

BACKTEST_FILE = "data/backtest_results.json"


def load_all_backtest_results():
    if not os.path.exists(BACKTEST_FILE):
        return []
    with open(BACKTEST_FILE, "r") as f:
        return json.load(f)

# strategy_heatmap_generator.py — 🔥 Strategy Evolution Heatmap Generator

import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

PERFORMANCE_LOG = "logs/strategy_feedback.json"
OUTPUT_DIR = "logs/heatmaps"

class HeatmapGenerator:
    def __init__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def load_performance_data(self):
        if not os.path.exists(PERFORMANCE_LOG):
            print("⚠️ No strategy feedback found.")
            return {}
        with open(PERFORMANCE_LOG, "r") as f:
            return json.load(f)

    def build_matrix(self, performance_data):
        rows = []
        for token, strategies in performance_data.items():
            row = {"token": token}
            for strat in strategies:
                name = strat.get("strategy")
                score = strat.get("sharpe", 0)  # fallback if not included
                row[name] = score
            rows.append(row)
        return pd.DataFrame(rows).set_index("token")

    def generate_heatmap(self, df):
        plt.figure(figsize=(12, max(6, len(df) * 0.4)))
        sns.heatmap(df, cmap="RdYlGn", annot=True, fmt=".2f", linewidths=0.5)
        plt.title("Strategy Evolution Heatmap")
        plt.tight_layout()

        filename = f"heatmap_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
        full_path = os.path.join(OUTPUT_DIR, filename)
        plt.savefig(full_path)
        plt.close()
        print(f"✅ Heatmap saved to {full_path}")

    def run(self):
        print("🔥 Generating Strategy Evolution Heatmap...")
        data = self.load_performance_data()
        if not data:
            return
        df = self.build_matrix(data)
        if df.empty:
            print("⚠️ No performance matrix to visualize.")
            return
        self.generate_heatmap(df)

if __name__ == "__main__":
    HeatmapGenerator().run()

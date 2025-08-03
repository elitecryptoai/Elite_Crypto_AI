# email_reporter.py — ULTRA ELITE REPORTER (DAILY VISUAL INTEL TO PROTONMAIL)

import os
import json
from datetime import datetime
from agents.utils.llm import query_llm_with_fallback
from agents.utils.email_utils import send_email
from PIL import Image
import matplotlib.pyplot as plt

# File paths
FORECAST_FILE = "intel/forecast_signals.json"
PERFORMANCE_FILE = "intel/performance_metrics.json"
PORTFOLIO_FILE = "wallets/portfolio.json"
MARKET_FILE = "intel/market_status.json"
STRATEGY_FEEDBACK_FILE = "logs/strategy_feedback.json"
FORECAST_TRACKER = "logs/prices/forecast_price_tracker.json"
MODEL_PERF_FILE = "intel/llm_model_performance.json"
PROMPT_SCORES = "data/prompt_scores.json"
FORECAST_ACCURACY = "data/forecast_accuracy.json"
HEATMAP_DIR = "logs/heatmaps"
VISUAL_EXPORT = "logs/email_exports"

class EmailReporter:
    def __init__(self):
        self.forecast = {}
        self.performance = {}
        self.portfolio = {}
        self.market = {}
        self.feedback = {}
        self.tracker = {}
        self.model_perf = {}
        self.prompt_scores = {}
        self.forecast_accuracy = {}
        self.attachments = []

    def safe_load(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def load_all_data(self):
        self.forecast = self.safe_load(FORECAST_FILE)
        self.performance = self.safe_load(PERFORMANCE_FILE)
        self.portfolio = self.safe_load(PORTFOLIO_FILE)
        self.market = self.safe_load(MARKET_FILE)
        self.feedback = self.safe_load(STRATEGY_FEEDBACK_FILE)
        self.tracker = self.safe_load(FORECAST_TRACKER)
        self.model_perf = self.safe_load(MODEL_PERF_FILE)
        self.prompt_scores = self.safe_load(PROMPT_SCORES)
        self.forecast_accuracy = self.safe_load(FORECAST_ACCURACY)

    def load_heatmaps(self):
        if os.path.exists(HEATMAP_DIR):
            for f in os.listdir(HEATMAP_DIR):
                if f.endswith(".png"):
                    self.attachments.append(os.path.join(HEATMAP_DIR, f))

    def export_model_table_image(self):
        from pandas import DataFrame

        rows = []
        for model in self.model_perf:
            perf = self.model_perf[model]
            acc = self.forecast_accuracy.get(model, {}).get("accuracy", None)
            score = self.prompt_scores.get(model, None)
            rows.append({
                "Model": model.upper(),
                "Accuracy": round(acc, 3) if acc is not None else "N/A",
                "ROI": round(perf.get("avg_roi", 0) * 100, 2),
                "Drift": round(perf.get("confidence_drift", 0), 3),
                "Weight": round(score, 3) if score is not None else "N/A"
            })
        df = DataFrame(rows).sort_values("Accuracy", ascending=False)
        os.makedirs(VISUAL_EXPORT, exist_ok=True)
        path = os.path.join(VISUAL_EXPORT, "model_performance_table.png")
        fig, ax = plt.subplots(figsize=(8, len(df) * 0.5))
        ax.axis('tight')
        ax.axis('off')
        ax.table(cellText=df.values, colLabels=df.columns, loc='center')
        plt.title("Model Performance Table")
        plt.savefig(path, bbox_inches='tight')
        self.attachments.append(path)

    def build_prompt(self):
        return f"""
You are a financial intelligence analyst.
Write a concise, professional crypto report.

Market:
{json.dumps(self.market, indent=2)}

Portfolio:
{json.dumps(self.portfolio, indent=2)[:1000]}

Forecasts:
{json.dumps(self.forecast, indent=2)[:1000]}

Strategies:
{json.dumps(self.feedback, indent=2)[:1000]}

Performance:
{json.dumps(self.performance, indent=2)[:1000]}

Forecast Tracker:
{json.dumps(self.tracker, indent=2)[:500]}

Respond with a professional, formatted report suitable for email.
Include key market insights, allocations, strongest coins, strategy summaries, and system evolution if present.
Keep it concise but informative.
"""

    def run(self):
        print("📢 Running Email Reporter...")
        self.load_all_data()
        self.load_heatmaps()
        self.export_model_table_image()
        prompt = self.build_prompt()
        try:
            report = query_llm_with_fallback(prompt)
            send_email(subject="📊 Daily AI Crypto Report",
                       body=report,
                       attachments=self.attachments)
            print("✅ Email sent successfully.")
        except Exception as e:
            print(f"❌ Email failed: {e}")

if __name__ == "__main__":
    EmailReporter().run()

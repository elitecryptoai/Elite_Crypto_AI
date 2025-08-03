# self_trainer.py — ULTRA ELITE SELF-EVOLVING STRATEGY TRAINER 🚀

import os
import json
from datetime import datetime
from collections import defaultdict
from agents.utils.llm import query_llm_with_fallback
from utils.strategy_tracker import get_strategy_performance
from utils.intel_loader import get_forecast_accuracy_stats

ACCURACY_LOG = "data/forecast_accuracy.json"
PROMPT_SCORES = "data/prompt_scores.json"
STRATEGY_FEEDBACK = "logs/strategy_feedback.json"
PERFORMANCE_FILE = "intel/performance_metrics.json"
STRATEGY_FOLDER = "strategies"
MODEL_PERF_FILE = "intel/llm_model_performance.json"  # consider centralizing in global config for reuse

BOOST = 1.07
DECAY = 0.93
MIN_WEIGHT = 0.05
MAX_WEIGHT = 5.0

class SelfTrainer:
    def __init__(self):
        self.model_scores = defaultdict(lambda: 1.0)
        self.forecast_accuracy = {}
        self.model_performance = {}
        self.strategy_performance = {}

    def load_data(self):
        self.forecast_accuracy = get_forecast_accuracy_stats()
        self.model_performance = self.load_llm_performance_metrics()  # pulled from llm_forecast_analyzer for dashboard integration
        self.strategy_performance = get_strategy_performance()
        self.model_scores = self.load_prompt_scores()

    def load_prompt_scores(self):
        if not os.path.exists(PROMPT_SCORES):
            return defaultdict(lambda: 1.0)
        with open(PROMPT_SCORES, "r") as f:
            return defaultdict(lambda: 1.0, json.load(f))

    def load_model_performance(self):
        if not os.path.exists(MODEL_PERF_FILE):
            return {}
        with open(MODEL_PERF_FILE, "r") as f:
            return json.load(f)

    def save_prompt_scores(self):
        with open(PROMPT_SCORES, "w") as f:
            json.dump(dict(self.model_scores), f, indent=2)

    def update_model_weights(self):
        for model_key in set(list(self.forecast_accuracy.keys()) + list(self.model_performance.keys())):
            model = model_key.split("_")[0].lower()
            accuracy = self.forecast_accuracy.get(model_key, {}).get("accuracy", 0.5)
            roi = self.model_performance.get(model, {}).get("avg_roi", 0)
            drift = self.model_performance.get(model, {}).get("confidence_drift", 0)

            if accuracy >= 0.7 or roi > 0.03:
                self.model_scores[model] = min(MAX_WEIGHT, self.model_scores[model] * BOOST)
            elif accuracy < 0.4 or drift > 0.2:
                self.model_scores[model] = max(MIN_WEIGHT, self.model_scores[model] * DECAY)  # log drift-based downgrade for dashboard heatmap

    def regenerate_strategies(self):
        os.makedirs(STRATEGY_FOLDER, exist_ok=True)
        for token, metrics in self.strategy_performance.items():
            sharpe = metrics.get("sharpe", 0)
            drawdown = metrics.get("drawdown", 0)
            hit_rate = metrics.get("hit_rate", 0)
            if sharpe < 0.5 or drawdown > 0.25 or hit_rate < 0.3:
                prompt = f"""
You are a crypto strategy engineer. The current strategy for {token} is underperforming.
Sharpe: {sharpe}, Drawdown: {drawdown}, Hit Rate: {hit_rate}

Please create a new strategy in Python with:
- Clear buy/sell logic
- Lower drawdown
- Better hit rate
- Return a Strategy class using lowercase OHLCV column names
Only return raw code.
"""
                try:
                    raw_code = query_llm_with_fallback(prompt)
                    code = "import pandas as pd\n" + raw_code.split("import pandas")[-1].strip()
                    filename = os.path.join(STRATEGY_FOLDER, f"{token}_auto.py")
                    with open(filename, "w") as f:
                        f.write(code)
                    print(f"✅ Regenerated strategy for {token}")
                except Exception as e:
                    print(f"❌ Failed to regenerate {token}: {e}")

    def run(self):
        print("🤖 Running Self Trainer (Ultra Elite Mode)...")
        self.load_data()
        self.update_model_weights()
        self.save_prompt_scores()
        self.regenerate_strategies()
        print("✅ Self-training complete.")

if __name__ == "__main__":
    SelfTrainer().run()

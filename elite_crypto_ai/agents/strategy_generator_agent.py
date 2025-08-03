# strategy_generator_agent.py — ULTRA ELITE STRATEGY BUILDER (AUTONOMOUS + SIGNAL-AWARE)

import os
import json
from datetime import datetime
from agents.utils.llm import query_llm_with_fallback
from utils.strategy_tracker import get_strategy_performance

PERFORMANCE_FILE = "intel/performance_metrics.json"
SIGNAL_INTEL_FILE = "intel/best_signals.json"
STRATEGY_FOLDER = "strategies"
STRATEGY_METADATA_FILE = "intel/strategy_metadata.json"

DEFAULT_SIGNALS = ["RSI", "EMA", "MACD", "SMA", "Bollinger", "Stochastic", "ADX"]

class StrategyGenerator:
    def __init__(self):
        self.performance = {}
        self.signal_intel = {}
        self.metadata = {}

    def load_data(self):
        if os.path.exists(PERFORMANCE_FILE):
            with open(PERFORMANCE_FILE, "r") as f:
                self.performance = json.load(f)
        if os.path.exists(SIGNAL_INTEL_FILE):
            with open(SIGNAL_INTEL_FILE, "r") as f:
                self.signal_intel = json.load(f)

    def generate_prompt(self, token, signals, stats):
        signal_summary = ", ".join(signals)
        return f"""
You are a crypto strategy architect.
Create a new Python trading strategy for: {token}

Stats:
Sharpe: {stats.get('sharpe', 'N/A')}
Drawdown: {stats.get('drawdown', 'N/A')}
Hit Rate: {stats.get('hit_rate', 'N/A')}

Requirements:
- Use top-performing signals from: {signal_summary}
- Design for high Sharpe, low drawdown, high hit rate
- Use lowercase OHLCV columns (open, high, low, close, volume)
- Return ONLY raw Python code (Strategy class)
"""

    def save_strategy(self, token, code):
        filename = os.path.join(STRATEGY_FOLDER, f"{token}_auto.py")
        with open(filename, "w") as f:
            f.write(code)

    def update_metadata(self, token, signals, stats):
        self.metadata[token] = {
            "updated": datetime.utcnow().isoformat(),
            "signals_used": signals,
            "sharpe": stats.get("sharpe", 0),
            "drawdown": stats.get("drawdown", 0),
            "hit_rate": stats.get("hit_rate", 0),
            "source": "strategy_generator"
        }

    def save_metadata(self):
        with open(STRATEGY_METADATA_FILE, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def run(self):
        print("🧠 Running Strategy Generator (Signal-Aware)...")
        self.load_data()
        os.makedirs(STRATEGY_FOLDER, exist_ok=True)

        for token, signals in self.signal_intel.items():
            try:
                stats = self.performance.get(token, {})
                print(f"✨ Generating strategy for {token} using: {signals}...")
                prompt = self.generate_prompt(token, signals, stats)
                raw = query_llm_with_fallback(prompt)
                code = "import pandas as pd\n" + raw.split("import pandas")[-1].strip()
                self.save_strategy(token, code)
                self.update_metadata(token, signals, stats)
            except Exception as e:
                print(f"❌ Generation failed for {token}: {e}")

        self.save_metadata()
        print("✅ Strategy Generation Complete.")

if __name__ == "__main__":
    StrategyGenerator().run()

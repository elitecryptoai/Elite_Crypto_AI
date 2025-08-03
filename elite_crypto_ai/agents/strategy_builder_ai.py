# strategy_builder_ai.py — ULTRA ELITE VERSION
# Autonomous Strategy Evolution Engine (Forecast-Aware, Performance-Driven)

import os
import json
from datetime import datetime
from agents.utils.llm import query_llm_with_fallback
from utils.strategy_tracker import get_strategy_performance
from utils.intel_loader import load_forecast_data, load_market_conditions

STRATEGY_FOLDER = "strategies"
PERFORMANCE_FILE = "intel/performance_metrics.json"
FORECAST_FILE = "intel/forecast_signals.json"


class StrategyBuilder:
    def __init__(self):
        self.forecasts = load_forecast_data()
        self.performance = get_strategy_performance()
        self.market = load_market_conditions()

    def should_upgrade(self, token):
        stats = self.performance.get(token, {})
        if not stats:
            return True
        sharpe = stats.get("sharpe", 0)
        drawdown = stats.get("drawdown", 1)
        hit = stats.get("hit_rate", 0)
        return sharpe < 0.5 or drawdown > 0.25 or hit < 0.3

    def build_prompt(self, token, forecast, performance, market):
        return f'''
You are a crypto trading strategy generator.

Your goal: Create a new, more intelligent trading strategy for the token: {token}.

Latest Forecast:
Label: {forecast.get("forecast_label")}
Confidence: {forecast.get("confidence_score")}
Model: {forecast.get("model_used")}

Recent Strategy Stats:
Sharpe: {performance.get("sharpe")}, Drawdown: {performance.get("drawdown")}, Hit Rate: {performance.get("hit_rate")}

Market Conditions:
Volatility: {market.get("volatility_score")}
Liquidity: {market.get("liquidity_trend")}
Dominant Trend: {market.get("trend_direction")}

Instructions:
- Strategy must be intelligent and resilient
- Use indicators if useful (RSI, MACD, EMA, VWAP, etc.)
- Ensure the output begins with:
```python
import pandas as pd
class Strategy:

- Must use lowercase OHLCV (open, high, low, close, volume)
- Return only code. No explanations.
'''

    def clean_code(self, raw):
        if "class Strategy" not in raw:
            raise ValueError("No Strategy class found")
        code = "import pandas as pd\n" + raw.split("import pandas")[-1].strip()
        return code

    def save_strategy(self, token, code):
        os.makedirs(STRATEGY_FOLDER, exist_ok=True)
        path = os.path.join(STRATEGY_FOLDER, f"{token}_auto.py")
        with open(path, "w") as f:
            f.write(code)
        print(f"✅ Strategy updated: {token} → {path}")

    def generate_all(self):
        for token, forecast in self.forecasts.items():
            try:
                if not self.should_upgrade(token):
                    continue
                stats = self.performance.get(token, {})
                prompt = self.build_prompt(token, forecast, stats, self.market)
                raw_code = query_llm_with_fallback(prompt)
                code = self.clean_code(raw_code)
                self.save_strategy(token, code)
            except Exception as e:
                print(f"❌ Failed to update {token}: {e}")

    def run(self):
        print("🧠 Running Strategy Builder AI...")
        self.generate_all()
        print("✅ Strategy building complete.")


if __name__ == "__main__":
    StrategyBuilder().run()

# strategy_agent.py — ULTRA ELITE STRATEGY TESTER (Phase 5 Upgrade)

import os
import json
import pandas as pd
from utils.data_loader import load_ohlcv
from utils.strategy_tracker import save_strategy_feedback, get_strategy_performance
from utils.intel_loader import get_forecast_labels

STRATEGIES_FOLDER = "strategies"
STRATEGY_FEEDBACK_FILE = "logs/strategy_feedback.json"
PERFORMANCE_FILE = "intel/performance_metrics.json"

class StrategyAgent:
    def __init__(self):
        self.tokens = []
        self.feedback = {}
        self.performance = {}
        self.forecast_labels = {}

    def load_tokens(self):
        try:
            with open("data/coin_scan_results.json") as f:
                self.tokens = [t['symbol'].lower() for t in json.load(f)["coins"]]
        except:
            self.tokens = []

    def load_forecasts(self):
        self.forecast_labels = get_forecast_labels()

    def test_strategy(self, token, strategy_module):
        try:
            df = load_ohlcv(token)
            strat = strategy_module.Strategy()
            signals = strat.generate_signals(df)

            if len(signals) != len(df):
                raise ValueError("Signal length mismatch")

            df["signal"] = signals
            df["return"] = df["close"].pct_change().fillna(0)
            df["strategy_return"] = df["signal"] * df["return"]

            cumulative = (1 + df["strategy_return"]).cumprod()
            pnl = cumulative.iloc[-1] - 1
            sharpe = (df["strategy_return"].mean() / df["strategy_return"].std()) * (252**0.5)
            drawdown = (cumulative.cummax() - cumulative).max()
            hit_rate = (df["strategy_return"] > 0).sum() / len(df)

            forecast_alignment = 0
            forecast_label = self.forecast_labels.get(token)
            if forecast_label == "BULLISH" and pnl > 0:
                forecast_alignment = 1
            elif forecast_label == "BEARISH" and pnl < 0:
                forecast_alignment = 1

            return {
                "pnl": round(pnl, 4),
                "sharpe": round(sharpe, 3),
                "drawdown": round(drawdown, 4),
                "hit_rate": round(hit_rate, 3),
                "alignment": forecast_alignment
            }
        except Exception as e:
            print(f"❌ Strategy test failed for {token}: {e}")
            return None

    def run(self):
        print("📊 Running Strategy Agent (Ultra Elite)...")
        self.load_tokens()
        self.load_forecasts()
        os.makedirs("logs", exist_ok=True)
        os.makedirs("intel", exist_ok=True)

        performance = {}
        feedback = {}

        for token in self.tokens:
            token_strats = {}
            try:
                for file in os.listdir(STRATEGIES_FOLDER):
                    if file.endswith(".py") and file.startswith(token):
                        path = os.path.join(STRATEGIES_FOLDER, file)
                        namespace = {}
                        with open(path) as f:
                            exec(f.read(), namespace)
                        result = self.test_strategy(token, namespace)
                        if result:
                            token_strats[file] = result
            except Exception as e:
                print(f"❌ Failed loading strategies for {token}: {e}")
                continue

            if token_strats:
                ranked = sorted(token_strats.items(), key=lambda x: -x[1]['sharpe'])
                feedback[token] = {
                    "top_strategy": ranked[0][0],
                    "all": token_strats
                }
                performance[token] = ranked[0][1]

        self.feedback = feedback
        self.performance = performance

        save_strategy_feedback(self.feedback)
        with open(PERFORMANCE_FILE, "w") as f:
            json.dump(self.performance, f, indent=2)

        print(f"✅ Strategy feedback + performance saved for {len(self.feedback)} tokens.")

if __name__ == "__main__":
    StrategyAgent().run()

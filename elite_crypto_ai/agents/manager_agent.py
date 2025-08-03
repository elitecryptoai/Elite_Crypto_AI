# manager_agent.py — ULTRA ELITE MANAGER (INTELLIGENT ALLOCATION + FORECAST/STRATEGY FUSION + LIFECYCLE MANAGEMENT)

import os
import json
from datetime import datetime
from agents.utils.llm import query_llm_with_fallback
from utils.strategy_tracker import get_strategy_performance
from utils.intel_loader import get_forecast_accuracy_stats
from utils.token_utils import get_live_price

STRATEGY_FEEDBACK_FILE = "logs/strategy_feedback.json"
FORECAST_FILE = "intel/forecast_signals.json"
MARKET_FILE = "intel/market_status.json"
PORTFOLIO_FILE = "wallets/portfolio.json"
EXECUTION_LOG = "logs/execution_log.json"
PERFORMANCE_FILE = "intel/performance_metrics.json"
SWAP_SIGNAL_FILE = "data/swap_signals.json"

class ManagerAgent:
    def __init__(self):
        self.forecast = {}
        self.feedback = {}
        self.market = {}
        self.performance = {}
        self.forecast_accuracy = {}
        self.portfolio = {"safe": {}, "medium": {}, "risky": {}}
        self.swap_candidates = []

    def load_inputs(self):
        def safe_load(path):
            if os.path.exists(path):
                with open(path, "r") as f:
                    return json.load(f)
            return {}

        self.forecast = safe_load(FORECAST_FILE)
        self.feedback = safe_load(STRATEGY_FEEDBACK_FILE)
        self.market = safe_load(MARKET_FILE)
        self.performance = safe_load(PERFORMANCE_FILE)
        self.forecast_accuracy = get_forecast_accuracy_stats()

        if os.path.exists(SWAP_SIGNAL_FILE):
            with open(SWAP_SIGNAL_FILE, "r") as f:
                data = json.load(f)
                self.swap_candidates = data.get("candidates", [])

    def score_token(self, token):
        f = self.forecast.get(token, {})
        p = self.performance.get(token, {})
        score = 0
        if f.get("confidence_score", 0) > 0.7:
            score += 1
        if p.get("sharpe", 0) > 1:
            score += 1
        if p.get("hit_rate", 0) > 0.5:
            score += 1
        if p.get("drawdown", 1) < 0.3:
            score += 1
        return score

    def select_tokens_fallback(self):
        sorted_fc = sorted(self.forecast.items(), key=lambda x: -x[1].get("confidence_score", 0))
        for token, data in sorted_fc[:20]:
            score = self.score_token(token)
            strat = self.feedback.get(token, {}).get("top_strategy", "UNKNOWN")
            if score >= 3:
                self.portfolio["safe"][token] = {"amount_usd": 2500, "strategy": strat}
            elif score == 2:
                self.portfolio["medium"][token] = {"amount_usd": 1500, "strategy": strat}
            elif score == 1:
                self.portfolio["risky"][token] = {"amount_usd": 1000, "strategy": strat}

    def build_prompt(self):
        top_forecasts = dict(list(self.forecast.items())[:10])
        return f"""
You are an elite crypto portfolio allocator.
Given the following inputs, return the ideal token split between Safe, Medium, Risky wallets.

Macro Trend: {self.market.get("macro_trend")}
Intel Score: {self.market.get("intel_score")}

Top Forecasts:
{json.dumps(top_forecasts, indent=2)}

Forecast Accuracy Stats:
{json.dumps(self.forecast_accuracy, indent=2)[:1000]}

Strategy Performance:
{json.dumps(self.performance, indent=2)[:1000]}

Return JSON like:
{{
  "safe": {{"TOKEN": {{"amount_usd": ###, "strategy": "STRAT"}}}},
  "medium": {{...}},
  "risky": {{...}}
}}
"""

    def ask_llm_for_allocations(self):
        try:
            prompt = self.build_prompt()
            response = query_llm_with_fallback(prompt)
            self.portfolio = json.loads(response)
        except Exception as e:
            print(f"❌ LLM fallback failed, using scoring model: {e}")
            self.select_tokens_fallback()

    def reallocate_swaps(self):
        for tier in ["safe", "medium", "risky"]:
            new_alloc = {}
            for token in self.portfolio.get(tier, {}):
                if token not in self.swap_candidates:
                    new_alloc[token] = self.portfolio[tier][token]
            self.portfolio[tier] = new_alloc

        if self.swap_candidates:
            print(f"[Manager] 🔄 Swapping out: {self.swap_candidates}")
            for token in self.swap_candidates:
                self.portfolio["medium"][f"usdc_{token}"] = {
                    "amount_usd": 1000,
                    "strategy": "HOLD",
                    "source": "swap_exit",
                    "value": get_live_price("usdc")
                }

    def write_portfolio(self):
        flat = {}
        for tier in self.portfolio:
            for token, info in self.portfolio[tier].items():
                flat[token] = {
                    "action": "buy",
                    "amount_usd": info.get("amount_usd", 0),
                    "strategy": info.get("strategy", "")
                }
        os.makedirs(os.path.dirname(PORTFOLIO_FILE), exist_ok=True)
        with open(PORTFOLIO_FILE, "w") as f:
            json.dump(flat, f, indent=2)

    def log_decisions(self):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "portfolio": self.portfolio,
            "macro_trend": self.market.get("macro_trend", "unknown"),
            "intel_score": self.market.get("intel_score", 0)
        }
        os.makedirs("logs", exist_ok=True)
        if os.path.exists(EXECUTION_LOG):
            with open(EXECUTION_LOG, "r") as f:
                log = json.load(f)
        else:
            log = []
        log.append(log_entry)
        with open(EXECUTION_LOG, "w") as f:
            json.dump(log[-300:], f, indent=2)

    def run(self):
        print("🧠 Manager Agent Running (Ultra Elite Mode)...")
        self.load_inputs()
        self.ask_llm_for_allocations()
        self.reallocate_swaps()
        self.write_portfolio()
        self.log_decisions()
        print("✅ Portfolio written with strategy + accuracy + swap-awareness.")

if __name__ == "__main__":
    ManagerAgent().run()

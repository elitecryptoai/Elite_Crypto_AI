# strategy_batch_runner.py — ULTRA ELITE PARALLEL STRATEGY RUNNER

import os
import json
import concurrent.futures
from agents.strategy_agent import StrategyAgent

STRATEGY_INPUT_FILE = "intel/forecast_signals.json"
STRATEGY_RESULTS_FILE = "logs/strategy_feedback.json"
MAX_THREADS = 8

class StrategyBatchRunner:
    def __init__(self):
        self.tokens = []
        self.results = {}

    def load_tokens(self):
        if not os.path.exists(STRATEGY_INPUT_FILE):
            print("❌ No forecast input file found.")
            return
        with open(STRATEGY_INPUT_FILE, "r") as f:
            self.tokens = list(json.load(f).keys())

    def run_for_token(self, token):
        try:
            agent = StrategyAgent(token=token)
            agent.run()
            return token, agent.result
        except Exception as e:
            print(f"❌ Strategy run failed for {token}: {e}")
            return token, {"error": str(e)}

    def run_parallel(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = [executor.submit(self.run_for_token, token) for token in self.tokens]
            for future in concurrent.futures.as_completed(futures):
                token, result = future.result()
                self.results[token] = result

    def save_results(self):
        os.makedirs("logs", exist_ok=True)
        with open(STRATEGY_RESULTS_FILE, "w") as f:
            json.dump(self.results, f, indent=2)

    def run(self):
        print("🚀 Running Strategy Batch Runner (Parallel Mode)...")
        self.load_tokens()
        if not self.tokens:
            print("⚠️ No tokens to run strategies for.")
            return
        self.run_parallel()
        self.save_results()
        print(f"✅ Completed strategy runs for {len(self.tokens)} tokens.")

if __name__ == "__main__":
    StrategyBatchRunner().run()

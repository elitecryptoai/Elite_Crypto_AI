# ----------- FULL FILE: strategy_simulator.py (ULTRA ELITE STRATEGY TEST ENGINE + FEEDBACK + EVOLUTION FLAGS) -----------
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

STRATEGY_FOLDER = "strategies"
DATA_FOLDER = "data"
CHART_FOLDER = "results/charts"
SIM_RESULTS_FILE = "intel/simulation_results.json"
TRADE_LOG_FILE = "logs/simulation_trade_log.json"
EVOLUTION_QUEUE = "logs/evolution_queue.json"

class StrategySimulator:
    def __init__(self):
        self.results = {}
        self.trade_log = []
        self.evolution_queue = []

    def load_strategy(self, strategy_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("Strategy", strategy_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.Strategy()

    def run_backtest(self, strategy, df):
        signals = strategy.generate_signals(df.copy())
        df = df.copy()
        df["signals"] = signals
        df["returns"] = df["close"].pct_change().fillna(0)
        df["strategy_returns"] = df["returns"] * df["signals"]
        df["cumulative"] = (df["strategy_returns"] + 1).cumprod()

        trades = df[df["signals"] != 0].copy()
        trades = trades[["timestamp", "close", "signals", "returns", "strategy_returns"]].to_dict(orient="records")

        total_return = df["cumulative"].iloc[-1] - 1
        win_rate = (df["strategy_returns"] > 0).sum() / len(df)
        return df, total_return, win_rate, trades

    def simulate_all(self):
        os.makedirs(CHART_FOLDER, exist_ok=True)
        for file in os.listdir(STRATEGY_FOLDER):
            if not file.endswith(".py"):
                continue

            token = file.replace("_auto.py", "").replace(".py", "")
            strategy_path = os.path.join(STRATEGY_FOLDER, file)
            data_path = os.path.join(DATA_FOLDER, f"{token}.csv")

            if not os.path.exists(data_path):
                print(f"⚠️ Missing price data for {token}")
                continue

            try:
                df = pd.read_csv(data_path)
                df.columns = [c.lower() for c in df.columns]
                df = df.sort_values("timestamp")
                strategy = self.load_strategy(strategy_path)
                df_bt, ret, win, trades = self.run_backtest(strategy, df)
                self.results[token] = {"return_pct": round(ret * 100, 2), "win_rate": round(win, 2)}
                self.trade_log.extend([{**t, "token": token, "strategy": file} for t in trades])
                if ret < 0.01 or win < 0.5:
                    self.evolution_queue.append({"token": token, "strategy": file, "reason": "underperforming"})
                self.plot(df_bt, token)
                print(f"✅ Simulated {token} | Return: {ret * 100:.2f}%, Win Rate: {win * 100:.2f}%")
            except Exception as e:
                print(f"❌ Failed to simulate {token}: {e}")

        with open(SIM_RESULTS_FILE, "w") as f:
            json.dump(self.results, f, indent=2)
        with open(TRADE_LOG_FILE, "w") as f:
            json.dump(self.trade_log, f, indent=2)
        with open(EVOLUTION_QUEUE, "w") as f:
            json.dump(self.evolution_queue, f, indent=2)

    def plot(self, df, token):
        plt.figure(figsize=(10, 5))
        plt.plot(df["timestamp"], df["cumulative"], label="Equity Curve")
        plt.title(f"{token.upper()} Strategy Backtest")
        plt.xlabel("Time")
        plt.ylabel("Cumulative Return")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(CHART_FOLDER, f"{token}.png"))
        plt.close()

    def run(self):
        print("📈 Running Strategy Simulator (ULTRA ELITE FEEDBACK MODE)...")
        self.simulate_all()
        print("✅ Simulation complete. Saved to simulation_results.json, trade_log.json, and evolution_queue.json")

if __name__ == "__main__":
    StrategySimulator().run()

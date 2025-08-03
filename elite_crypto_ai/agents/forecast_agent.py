# forecast_agent.py — ULTRA ELITE VERSION w/ MODEL ROUTING + INTEL SIGNAL FUSION + STRATEGY-AWARE METADATA

import os
import json
from datetime import datetime
from utils.source_manager import get_price_change_signal
from utils.sentiment_sources import get_google_trends_score, get_twitter_sentiment_score
from utils.cryptoquant import get_cryptoquant_metrics
from utils.llm import query_llm
from utils.strategy_tracker import get_strategy_metadata_tags

FORECAST_OUTPUT_PATH = "intel/forecast_signals.json"
FORECAST_HISTORY_LOG = "logs/forecast_history.json"
PRICE_TRACKER_FILE = "logs/prices/forecast_price_tracker.json"
MODEL_RANK_FILE = "logs/forecast_model_rank.json"
TOKEN_ROUTING_FILE = "intel/token_model_routing.json"

class ForecastAgent:
    def __init__(self):
        self.tokens = []
        self.forecast_data = {}
        self.tracker = {}
        self.model_rank = []
        self.token_routes = {}
        self.strategy_tags = {}

    def load_tokens(self):
        try:
            with open("logs/prices/current_prices.json", "r") as f:
                self.tokens = list(json.load(f).keys())
        except Exception as e:
            print(f"❌ Failed to load token list: {e}")
            self.tokens = []

    def load_model_rank(self):
        try:
            with open(MODEL_RANK_FILE, "r") as f:
                self.model_rank = json.load(f)
        except:
            self.model_rank = ["gpt-4"]

    def load_token_routes(self):
        if os.path.exists(TOKEN_ROUTING_FILE):
            with open(TOKEN_ROUTING_FILE, "r") as f:
                self.token_routes = json.load(f)

    def load_strategy_tags(self):
        try:
            self.strategy_tags = get_strategy_metadata_tags()
        except:
            self.strategy_tags = {}

    def build_prompt(self, token, price_signal, trend_score, sentiment_score, cq, model_used, meta):
        return f"""
You are a crypto market forecaster.
Coin: {token}
Price Momentum: {price_signal}
Google Trends Score: {trend_score}
Twitter Sentiment: {sentiment_score}
Miner Outflows: {cq['miner_outflows']}
Exchange Flows: {cq['exchange_flows']}
Stablecoin Inflows: {cq['stablecoin_inflows']}
Whale Activity: {cq['whale_activity']}

Return JSON:
{{
  "forecast_label": "BULLISH | BEARISH | NEUTRAL",
  "confidence_score": float (0-1),
  "rationale": "reason",
  "model_used": "{model_used.upper()}",
  "metadata": {{
    "time_horizon": "{meta.get('time_horizon', 'medium')}",
    "volatility_profile": "{meta.get('volatility_profile', 'medium')}",
    "signal_triggers": {meta.get('signal_triggers', ['RSI', 'EMA'])}
  }}
}}
"""

    def record_forecast(self, token, forecast, current_price):
        self.forecast_data[token] = forecast
        history_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "token": token,
            "forecast": forecast,
            "entry_price": current_price
        }
        if os.path.exists(FORECAST_HISTORY_LOG):
            with open(FORECAST_HISTORY_LOG, "r") as f:
                history = json.load(f)
        else:
            history = []
        history.append(history_entry)
        with open(FORECAST_HISTORY_LOG, "w") as f:
            json.dump(history[-300:], f, indent=2)

        if token not in self.tracker:
            self.tracker[token] = []
        self.tracker[token].append({
            "timestamp": history_entry["timestamp"],
            "price": current_price,
            "forecast_label": forecast["forecast_label"],
            "model": forecast["model_used"]
        })

    def save_outputs(self):
        os.makedirs("intel", exist_ok=True)
        with open(FORECAST_OUTPUT_PATH, "w") as f:
            json.dump(self.forecast_data, f, indent=2)

        os.makedirs("logs/prices", exist_ok=True)
        with open(PRICE_TRACKER_FILE, "w") as f:
            json.dump(self.tracker, f, indent=2)

    def run(self):
        print("🔮 Running Forecast Agent (Model-Rank + Routing Mode)...")
        self.load_tokens()
        self.load_model_rank()
        self.load_token_routes()
        self.load_strategy_tags()
        if not self.tokens:
            print("⚠️ No tokens available.")
            return

        rotation = 0
        for token in self.tokens:
            try:
                model_used = self.token_routes.get(token)
                if not model_used:
                    model_used = self.model_rank[rotation % len(self.model_rank)]

                print(f"📈 Forecasting {token} with {model_used}...")
                price_signal = get_price_change_signal(token)
                trend_score = get_google_trends_score(token)
                sentiment_score = get_twitter_sentiment_score(token)
                cq = get_cryptoquant_metrics(token)
                meta = self.strategy_tags.get(token, {})

                prompt = self.build_prompt(token, price_signal, trend_score, sentiment_score, cq, model_used, meta)
                response = query_llm(prompt, model_name=model_used)
                forecast = json.loads(response)

                current_price = price_signal.get("price", 0)
                self.record_forecast(token, forecast, current_price)
                print(f"✅ {token}: {forecast['forecast_label']} ({forecast['confidence_score']}) — {forecast['model_used']}")

                rotation += 1
            except Exception as e:
                print(f"❌ Forecast error for {token}: {e}")
                continue

        self.save_outputs()
        print("✅ Forecasting complete.")

if __name__ == "__main__":
    ForecastAgent().run()

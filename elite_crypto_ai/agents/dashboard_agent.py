# dashboard_agent.py — ULTRA ELITE DASHBOARD VISUALIZER 📊

import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px

MODEL_PERF_FILE = "intel/llm_model_performance.json"
PROMPT_SCORES = "data/prompt_scores.json"
FORECAST_ACCURACY = "data/forecast_accuracy.json"
FORECAST_FILE = "intel/forecast_signals.json"
PERFORMANCE_FILE = "intel/performance_metrics.json"
PORTFOLIO_FILE = "wallets/portfolio.json"
MARKET_FILE = "intel/market_status.json"
STRATEGY_FEEDBACK_FILE = "logs/strategy_feedback.json"
FORECAST_TRACKER = "logs/prices/forecast_price_tracker.json"
HEATMAP_DIR = "logs/heatmaps"

st.set_page_config(page_title="AI Model Dashboard", layout="wide")
st.title("🧠 Elite Intelligence + LLM Performance Dashboard")

# Load files
def safe_load(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

model_perf = safe_load(MODEL_PERF_FILE)
prompt_scores = safe_load(PROMPT_SCORES)
forecast_accuracy = safe_load(FORECAST_ACCURACY)
forecast = safe_load(FORECAST_FILE)
performance = safe_load(PERFORMANCE_FILE)
portfolio = safe_load(PORTFOLIO_FILE)
market = safe_load(MARKET_FILE)
feedback = safe_load(STRATEGY_FEEDBACK_FILE)
tracker = safe_load(FORECAST_TRACKER)

# Section: LLM Forecast Accuracy Heatmap
st.subheader("📈 LLM Forecast Model Comparison")
data = []
for model in model_perf:
    perf = model_perf.get(model, {})
    acc = forecast_accuracy.get(model, {}).get("accuracy", None)
    score = prompt_scores.get(model, None)
    data.append({
        "Model": model.upper(),
        "Accuracy": round(acc, 3) if acc is not None else "N/A",
        "ROI": round(perf.get("avg_roi", 0) * 100, 2),
        "Drift": round(perf.get("confidence_drift", 0), 3),
        "Weight": round(score, 3) if score is not None else "N/A"
    })

if data:
    df = pd.DataFrame(data)
    st.dataframe(df.sort_values("Accuracy", ascending=False))  # Consider exporting this key LLM performance table as image for email reports
    fig = px.imshow(df.set_index("Model")[ ["Accuracy", "ROI", "Drift", "Weight"] ], 
                    text_auto=True, aspect="auto", 
                    color_continuous_scale="RdBu_r")
    fig.update_layout(title="🔍 Model Performance Heatmap")
    st.plotly_chart(fig, use_container_width=True)  # Save this figure to PNG for email_reporter.py embedding

# Section: Forecast Snapshot
st.subheader("🔮 Forecast Snapshot")
if forecast:
    rows = []
    for token, data in forecast.items():
        rows.append({
            "Token": token,
            "Forecast": data["forecast_label"],
            "Confidence": data["confidence_score"],
            "Model": data["model_used"]
        })
    st.dataframe(sorted(rows, key=lambda x: -x["Confidence"]), use_container_width=True)

# Section: Forecast Tracker Accuracy Table
st.subheader("📊 Forecast Tracker History")
model_data = []
for token, logs in tracker.items():
    if logs:
        last = logs[-1]
        model_data.append({
            "Token": token,
            "Last Forecast": last.get("forecast_label"),
            "Model": last.get("model"),
            "Last Price": last.get("price")
        })
if model_data:
    st.dataframe(model_data, use_container_width=True)

# Section: Portfolio Breakdown
st.subheader("💼 Portfolio Allocations")
if portfolio:
    for wallet, holdings in portfolio.items():
        labels = list(holdings.keys())
        values = [info["amount_usd"] if isinstance(info, dict) else info for info in holdings.values()]
        fig = px.pie(names=labels, values=values, title=f"{wallet.title()} Wallet")
        st.plotly_chart(fig, use_container_width=True)

# Section: Strategy Heatmap
st.subheader("🔥 Strategy Performance Heatmap")
if feedback:
    rows = []
    for token, perf in feedback.items():
        rows.append({
            "Token": token,
            "Sharpe": perf.get("sharpe", 0),
            "Drawdown": perf.get("max_drawdown", 0),
            "HitRate": perf.get("hit_rate", 0),
        })
    if rows:
        st.dataframe(rows, use_container_width=True)
        st.plotly_chart(
            px.imshow([
                [r["Sharpe"] for r in rows],
                [r["Drawdown"] for r in rows],
                [r["HitRate"] for r in rows]
            ], labels=dict(x=list(range(len(rows))), y=["Sharpe", "Drawdown", "HitRate"])),
            use_container_width=True
        )

# Section: Market Intel
st.subheader("🌐 Market Intelligence Snapshot")
st.json(market)

# Section: Strategy Evolution Heatmaps
st.subheader("🧊 Strategy Evolution Visuals")
if os.path.exists(HEATMAP_DIR):  # You could zip or attach top heatmaps for email insights
    imgs = [f for f in os.listdir(HEATMAP_DIR) if f.endswith(".png")]
    for img in imgs:
        st.image(os.path.join(HEATMAP_DIR, img), caption=img, use_column_width=True)

# Footer
st.success("✅ Dashboard Loaded and Synced with AI Memory")

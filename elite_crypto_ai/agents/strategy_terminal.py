# strategy_terminal.py — GOD-TIER STRATEGY TERMINAL (ELITE CRYPTO QUANT DASHBOARD)

import os
import json
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

# Paths
FORECAST_FILE = "intel/forecast_signals.json"
PERFORMANCE_FILE = "intel/performance_metrics.json"
PORTFOLIO_FILE = "wallets/portfolio.json"
MARKET_FILE = "intel/market_status.json"
TRACKER_FILE = "logs/prices/forecast_price_tracker.json"
LLM_PERFORMANCE = "intel/llm_model_performance.json"
HEALTH_FILE = "logs/agent_health_scores.json"
HISTORY_FILE = "logs/forecast_history.json"
STRATEGY_META = "intel/strategy_metadata.json"

# Config
st.set_page_config(layout="wide")
st.title("🧠 Elite Strategy Intelligence Terminal")

# Utility

def safe(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

# Load all data
data = {
    "forecast": safe(FORECAST_FILE),
    "performance": safe(PERFORMANCE_FILE),
    "portfolio": safe(PORTFOLIO_FILE),
    "market": safe(MARKET_FILE),
    "tracker": safe(TRACKER_FILE),
    "llm": safe(LLM_PERFORMANCE),
    "health": safe(HEALTH_FILE),
    "history": safe(HISTORY_FILE),
    "metadata": safe(STRATEGY_META)
}

# Dashboard Selector
tab = st.selectbox("Select Dashboard", [
    "Forecast Heatmap",
    "ROI Leaderboard",
    "LLM Evolution",
    "Portfolio Breakdown",
    "Trade Simulation",
    "Correlation Matrix",
    "Drawdown Warnings",
    "Strategy Sandbox",
    "Super Forecast Mode"
])

# Forecast Heatmap
if tab == "Forecast Heatmap":
    st.header("🔮 Forecast Signal Accuracy Heatmap")
    records = []
    for token, logs in data["tracker"].items():
        for row in logs:
            records.append({
                "Token": token,
                "Model": row["model"],
                "Forecast": row["forecast_label"],
                "Confidence": row.get("confidence_score", 0),
                "Timestamp": row["timestamp"]
            })
    df = pd.DataFrame(records)
    if not df.empty:
        heat = pd.crosstab(df["Token"], df["Model"])
        st.dataframe(heat)

# ROI Leaderboard
elif tab == "ROI Leaderboard":
    st.header("💰 Historical ROI Leaderboard")
    perf = data["performance"]
    rows = [
        {
            "Token": k,
            "Sharpe": v.get("sharpe", 0),
            "Drawdown": v.get("drawdown", 0),
            "Hit Rate": v.get("hit_rate", 0),
        } for k, v in perf.items()
    ]
    st.dataframe(pd.DataFrame(rows).sort_values("Sharpe", ascending=False))

# LLM Evolution Viewer
elif tab == "LLM Evolution":
    st.header("🔮 LLM Forecast Evolution")
    models = data["llm"]
    if models:
        df = pd.DataFrame(models).T.reset_index().rename(columns={"index": "Model"})
        st.bar_chart(df.set_index("Model")["lifetime_accuracy"])
        st.bar_chart(df.set_index("Model")["avg_roi"])
        st.json(models)

# Portfolio Breakdown
elif tab == "Portfolio Breakdown":
    st.header("💼 Portfolio Overview")
    for wallet, alloc in data["portfolio"].items():
        st.subheader(wallet)
        fig = px.pie(names=list(alloc.keys()), values=list(alloc.values()))
        st.plotly_chart(fig)

# Trade Simulation
elif tab == "Trade Simulation":
    st.header("📉 Visual Trade Simulation")
    token = st.selectbox("Token", list(data["tracker"].keys()))
    series = data["tracker"].get(token, [])
    if series:
        df = pd.DataFrame(series)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        st.line_chart(df.set_index("timestamp")["price"])

# Correlation Matrix
elif tab == "Correlation Matrix":
    st.header("🧠 Cross-Coin Correlation Matrix")
    df = pd.DataFrame.from_dict(data["performance"], orient="index")
    if not df.empty:
        corr = df.corr()
        fig = px.imshow(corr, title="Strategy Metric Correlation")
        st.plotly_chart(fig)

# Drawdown Warnings
elif tab == "Drawdown Warnings":
    st.header("⚠️ High-Risk Drawdown Tokens")
    alerts = [
        {"Token": t, "Drawdown": v.get("drawdown", 0)}
        for t, v in data["performance"].items() if v.get("drawdown", 0) > 0.3
    ]
    st.dataframe(pd.DataFrame(alerts))

# Strategy Sandbox
elif tab == "Strategy Sandbox":
    st.header("🛠️ Strategy Sandbox")
    token = st.selectbox("Choose Token", list(data["metadata"].keys()))
    meta = data["metadata"].get(token, {})
    st.json(meta)
    path = f"strategies/{token}_auto.py"
    if os.path.exists(path):
        with open(path, "r") as f:
            code = f.read()
        edited = st.text_area("Edit Strategy Code", code, height=400)
        if st.button("💾 Save Strategy"):
            with open(path, "w") as f:
                f.write(edited)
            st.success("✅ Saved!")

# Super Forecast Mode
elif tab == "Super Forecast Mode":
    st.header("🚨 Super Forecast Mode")
    signals = []
    for token, f in data["forecast"].items():
        if f["confidence_score"] > 0.85:
            signals.append({
                "Token": token,
                "Label": f["forecast_label"],
                "Confidence": f["confidence_score"],
                "Model": f["model_used"]
            })
    st.dataframe(pd.DataFrame(signals).sort_values("Confidence", ascending=False))

st.success("✅ Terminal Ready. Choose tab to explore insights.")

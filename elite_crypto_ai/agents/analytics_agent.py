# analytics_agent.py

import pandas as pd
import os
import json
from utils.portfolio_loader import load_all_backtest_results

OUTPUT_PATH = "data/analytics_report.json"


def compute_volatility(df):
    return df["close"].pct_change().std() * (252 ** 0.5)


def compute_correlation_matrix(price_data):
    close_prices = {sym: df["close"] for sym, df in price_data.items() if not df.empty}
    return pd.DataFrame(close_prices).pct_change().corr()


def cluster_strategies(results):
    df = pd.DataFrame(results)
    grouped = df.groupby("strategy")["return"].agg(["mean", "std"])
    grouped["risk_score"] = grouped["mean"] / (grouped["std"] + 1e-6)
    return grouped.sort_values("risk_score", ascending=False).to_dict("index")


def build_analytics(price_data):
    result_data = load_all_backtest_results()

    vol_data = {sym: compute_volatility(df) for sym, df in price_data.items()}
    corr_matrix = compute_correlation_matrix(price_data)
    strat_clusters = cluster_strategies(result_data)

    analytics = {
        "volatility": vol_data,
        "correlation": corr_matrix.to_dict(),
        "strategy_clusters": strat_clusters,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(analytics, f, indent=2)

    return analytics


if __name__ == "__main__":
    from utils.data_loader import load_all_price_data
    data = load_all_price_data()
    output = build_analytics(data)
    print(json.dumps(output, indent=2))

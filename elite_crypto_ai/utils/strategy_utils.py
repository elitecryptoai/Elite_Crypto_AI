# utils/strategy_utils.py

def simulate_strategy(strategy, df):
    try:
        signals = strategy().generate_signals(df)
        return {"return": sum(signals) / len(signals) if signals else 0}
    except Exception as e:
        return {"return": -999, "error": str(e)}

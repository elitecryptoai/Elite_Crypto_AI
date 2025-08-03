# utils/data_loader.py

import os
import pandas as pd

def load_price_data(symbol):
    path = f"data/ohlcv/{symbol.lower()}.csv"
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    df.columns = [c.lower() for c in df.columns]
    return df

def load_all_price_data():
    folder = "data/ohlcv"
    return {f[:-4]: load_price_data(f[:-4]) for f in os.listdir(folder) if f.endswith(".csv")}  

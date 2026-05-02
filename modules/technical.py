import pandas as pd

def compute_technical(df):
    d = df.copy()

    d["SMA20"] = d["Close"].rolling(20).mean()
    d["SMA50"] = d["Close"].rolling(50).mean()

    # RSI
    delta = d["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    d["RSI"] = 100 - (100 / (1 + rs))

    return d

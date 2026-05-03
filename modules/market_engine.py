# =========================================
# NILE V17 - MARKET ENGINE (ALL-IN-ONE)
# =========================================

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf


# -----------------------------------------
# 🔹 CACHED DATA FETCH
# -----------------------------------------
@st.cache_data(ttl=900)
def get_history(symbol, period="6mo"):
    try:
        df = yf.download(symbol, period=period, auto_adjust=True, progress=False)
        return df.dropna()
    except:
        return pd.DataFrame()


@st.cache_data(ttl=86400)
def get_sector(symbol):
    try:
        info = yf.Ticker(symbol).info
        return info.get("sector", "Others")
    except:
        return "Others"


# -----------------------------------------
# 🔹 INDICATORS
# -----------------------------------------
def compute_indicators(df):
    d = df.copy()

    d["SMA20"] = d["Close"].rolling(20).mean()
    d["SMA50"] = d["Close"].rolling(50).mean()

    delta = d["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss

    d["RSI"] = 100 - (100 / (1 + rs))

    return d.dropna()


# -----------------------------------------
# 🔹 SAFE FLOAT (CRITICAL FIX)
# -----------------------------------------
def safe_float(x):
    try:
        return float(x)
    except:
        return np.nan


# -----------------------------------------
# 🔹 SCORING ENGINE
# -----------------------------------------
def score_stock(m):

    # Prevent crash if NaN
    if any(pd.isna(v) for v in m.values()):
        return 0

    score = 0

    if m["close"] > m["sma20"]: score += 20
    if m["close"] > m["sma50"]: score += 20
    if 50 < m["rsi"] < 70: score += 20

    return score


# -----------------------------------------
# 🔹 MAIN MARKET ANALYSIS
# -----------------------------------------
def analyze_universe(stocks):

    results = []

    for s in stocks:

        df = get_history(s)

        if df.empty or len(df) < 50:
            continue

        df = compute_indicators(df)

        if df.empty:
            continue

        last = df.iloc[-1]

        # 🔥 SAFE METRICS (FIXES YOUR ERROR)
        m = {
            "close": safe_float(last["Close"]),
            "sma20": safe_float(last["SMA20"]),
            "sma50": safe_float(last["SMA50"]),
            "rsi": safe_float(last["RSI"])
        }

        # Skip bad data
        if any(pd.isna(v) for v in m.values()):
            continue

        score = score_stock(m)

        trend = "Bullish" if m["sma20"] > m["sma50"] else "Bearish"

        sector = get_sector(s)

        results.append({
            "Stock": s,
            "Score": score,
            "RSI": round(m["rsi"], 2),
            "Trend": trend,
            "Sector": sector
        })

    return results


# -----------------------------------------
# 🔹 MARKET BREADTH
# -----------------------------------------
def market_breadth(results):

    if not results:
        return {
            "Advancers": 0,
            "Decliners": 0,
            "Neutral": 0,
            "Strength %": 0
        }

    adv = sum(1 for r in results if r["Score"] >= 60)
    dec = sum(1 for r in results if r["Score"] < 40)
    neutral = len(results) - adv - dec

    strength = (adv / len(results)) * 100

    return {
        "Advancers": adv,
        "Decliners": dec,
        "Neutral": neutral,
        "Strength %": round(strength, 2)
    }


# -----------------------------------------
# 🔹 SECTOR DISTRIBUTION
# -----------------------------------------
def sector_distribution(results):

    sector_data = {}

    for r in results:
        sector = r["Sector"]
        sector_data.setdefault(sector, []).append(r["Score"])

    return {
        sec: round(np.mean(scores), 2)
        for sec, scores in sector_data.items()
    }


# -----------------------------------------
# 🔹 TOP / WEAK STOCKS
# -----------------------------------------
def top_stocks(results, n=10):
    return sorted(results, key=lambda x: x["Score"], reverse=True)[:n]


def weak_stocks(results, n=10):
    return sorted(results, key=lambda x: x["Score"])[:n]

# =========================================
# NILE V17 - SINGLE FILE (FULL SYSTEM)
# =========================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Nile V17", layout="wide")

# -----------------------------------------
# 🔹 CACHED DATA
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
        return yf.Ticker(symbol).info.get("sector", "Others")
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
# 🔹 SAFE FLOAT
# -----------------------------------------
def safe_float(x):
    try:
        return float(x)
    except:
        return np.nan

# -----------------------------------------
# 🔹 SCORING
# -----------------------------------------
def score_stock(m):
    if any(pd.isna(v) for v in m.values()):
        return 0

    score = 0
    if m["close"] > m["sma20"]: score += 20
    if m["close"] > m["sma50"]: score += 20
    if 50 < m["rsi"] < 70: score += 20

    return score

# -----------------------------------------
# 🔹 MARKET ENGINE
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

        m = {
            "close": safe_float(last["Close"]),
            "sma20": safe_float(last["SMA20"]),
            "sma50": safe_float(last["SMA50"]),
            "rsi": safe_float(last["RSI"])
        }

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
# 🔹 BREADTH
# -----------------------------------------
def market_breadth(results):

    if not results:
        return 0,0,0,0

    adv = sum(1 for r in results if r["Score"] >= 60)
    dec = sum(1 for r in results if r["Score"] < 40)
    neutral = len(results) - adv - dec

    strength = (adv / len(results)) * 100

    return adv, dec, neutral, round(strength, 2)

# -----------------------------------------
# 🔹 SECTOR
# -----------------------------------------
def sector_distribution(results):

    sector_data = {}

    for r in results:
        sector_data.setdefault(r["Sector"], []).append(r["Score"])

    return {k: round(np.mean(v), 2) for k, v in sector_data.items()}

# -----------------------------------------
# 🔹 TOP / WEAK
# -----------------------------------------
def top_stocks(results, n=10):
    return sorted(results, key=lambda x: x["Score"], reverse=True)[:n]

def weak_stocks(results, n=10):
    return sorted(results, key=lambda x: x["Score"])[:n]

# -----------------------------------------
# 🔹 NIFTY 100
# -----------------------------------------
NIFTY_50 = [
"RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","INFY.NS","ITC.NS","LT.NS",
"KOTAKBANK.NS","AXISBANK.NS","SBIN.NS","BHARTIARTL.NS","ASIANPAINT.NS",
"MARUTI.NS","HCLTECH.NS","BAJFINANCE.NS","SUNPHARMA.NS","TITAN.NS",
"ULTRACEMCO.NS","NESTLEIND.NS","WIPRO.NS","NTPC.NS","POWERGRID.NS",
"TATAMOTORS.NS","M&M.NS","ONGC.NS","COALINDIA.NS","JSWSTEEL.NS",
"TATASTEEL.NS","ADANIPORTS.NS","INDUSINDBK.NS","TECHM.NS","GRASIM.NS",
"CIPLA.NS","DRREDDY.NS","HINDALCO.NS","HEROMOTOCO.NS","EICHERMOT.NS",
"BPCL.NS","BRITANNIA.NS","APOLLOHOSP.NS","DIVISLAB.NS","ADANIENT.NS",
"TATACONSUM.NS","PIDILITIND.NS","SBILIFE.NS","BAJAJ-AUTO.NS",
"SHRIRAMFIN.NS","TRENT.NS"
]

NIFTY_NEXT_50 = [
"ABB.NS","ADANIGREEN.NS","ADANIPOWER.NS","AMBUJACEM.NS","BANKBARODA.NS",
"BOSCHLTD.NS","CANBK.NS","CGPOWER.NS","CHOLAFIN.NS","DABUR.NS",
"DLF.NS","GAIL.NS","GODREJCP.NS","HAL.NS","HAVELLS.NS","ICICIGI.NS",
"ICICIPRULI.NS","INDIGO.NS","IOC.NS","IRCTC.NS","JINDALSTEL.NS",
"JSWENERGY.NS","LICI.NS","LODHA.NS","LUPIN.NS","MCDOWELL-N.NS",
"MOTHERSON.NS","NAUKRI.NS","NMDC.NS","PFC.NS","PNB.NS","POLYCAB.NS",
"RECLTD.NS","SAIL.NS","SIEMENS.NS","TVSMOTOR.NS","VEDL.NS",
"VOLTAS.NS","ZYDUSLIFE.NS","INDUSTOWER.NS","TORNTPHARM.NS",
"HDFCLIFE.NS","COLPAL.NS","MARICO.NS","UBL.NS","BERGEPAINT.NS",
"CONCOR.NS","OFSS.NS"
]

NIFTY_100 = sorted(list(set(NIFTY_50 + NIFTY_NEXT_50)))

# -----------------------------------------
# UI
# -----------------------------------------
st.title("📊 Nile V17 - Full Market Intelligence")

tabs = st.tabs(["Stock Analysis", "Market Analysis"])

# ---------------- STOCK ----------------
with tabs[0]:

    symbol = st.text_input("Stock", "RELIANCE.NS")

    if st.button("Analyze"):

        df = get_history(symbol)

        if df.empty:
            st.error("No data")
            st.stop()

        df = compute_indicators(df)
        last = df.iloc[-1]

        m = {
            "close": safe_float(last["Close"]),
            "sma20": safe_float(last["SMA20"]),
            "sma50": safe_float(last["SMA50"]),
            "rsi": safe_float(last["RSI"])
        }

        score = score_stock(m)

        col1, col2, col3 = st.columns(3)
        col1.metric("Score", score)
        col2.metric("RSI", round(m["rsi"],2))
        col3.metric("Trend", "Bullish" if m["sma20"] > m["sma50"] else "Bearish")

# ---------------- MARKET ----------------
with tabs[1]:

    universe = st.selectbox(
        "Select Universe",
        ["NIFTY 50", "NIFTY NEXT 50", "FULL (NIFTY 100)"]
    )

    if universe == "NIFTY 50":
        stocks = NIFTY_50
    elif universe == "NIFTY NEXT 50":
        stocks = NIFTY_NEXT_50
    else:
        stocks = NIFTY_100

    if st.button("Run Market Analysis"):

        results = analyze_universe(stocks)

        adv, dec, neutral, strength = market_breadth(results)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Advancers", adv)
        col2.metric("Decliners", dec)
        col3.metric("Neutral", neutral)
        col4.metric("Strength %", strength)

        st.subheader("📊 Sector Strength")
        sector = sector_distribution(results)
        st.bar_chart(sector)

        st.subheader("🔥 Top Stocks")
        st.dataframe(top_stocks(results, 10))

        st.subheader("⚠️ Weak Stocks")
        st.dataframe(weak_stocks(results, 10))

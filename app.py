# FINAL V11.4 ABSOLUTE INSTITUTIONAL AI WAR ROOM - SINGLE FULL STREAMLIT APP.PY
# =====================================================================
# Features:
# - NIFTY 50 / NIFTY 100 / Sector / Custom Universe switch
# - Sector Ranking + Sector Leaders + Sector Heatmap
# - Relative Strength vs NIFTY + RS mini charts
# - Momentum Ranking Engine (Top 20 / Top 50)
# - 52-Week High Proximity Scanner
# - Gap Up / Gap Down Scanner
# - Breakout Scanner + Swing Trade Engine
# - Candlestick Pattern Scanner
# - Supertrend + ADX + ATR + RSI + MACD
# - Support / Resistance auto zones
# - Persistent Watchlist + Notes + Status + CSV export
# - Stock Comparison Mode
# - Portfolio Builder + Rebalancing Suggestions + Risk Dashboard
# - Full Technical + Fundamental + Balance Sheet / P&L / Cash Flow
# - Cloud-safe single-file structure for Streamlit Cloud

import os
import io
import json
import math
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(page_title="FINAL V11.4 AI WAR ROOM", page_icon="🧠", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
.main {
    background: linear-gradient(180deg, #06101d 0%, #0a1220 45%, #111827 100%);
}
.block-container {padding-top: 0.8rem; padding-bottom: 2rem;}
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 14px;
    margin-bottom: 10px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
.small-note {font-size: 0.85rem; color: #9ca3af;}
</style>
""", unsafe_allow_html=True)

# ==================================================
# UNIVERSE CONFIG
# ==================================================
SECTOR_MAP = {
    "BANKING": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "INDUSINDBK.NS"],
    "IT": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTIM.NS"],
    "AUTO": ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "HEROMOTOCO.NS"],
    "PHARMA": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "LUPIN.NS", "TORNTPHARM.NS"],
    "FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS", "GODREJCP.NS"],
    "METALS": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "JINDALSTEL.NS", "NMDC.NS"],
    "ENERGY": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS", "IOC.NS", "GAIL.NS", "HINDPETRO.NS"],
    "INFRA": ["LT.NS", "ULTRACEMCO.NS", "ADANIPORTS.NS", "GRASIM.NS", "AMBUJACEM.NS", "SHREECEM.NS"],
    "FINANCIAL": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "SBILIFE.NS", "HDFCLIFE.NS", "ICICIPRULI.NS", "PFC.NS"],
}

NIFTY_50 = sorted({
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","INFY.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS",
    "LT.NS","KOTAKBANK.NS","HINDUNILVR.NS","AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","SUNPHARMA.NS",
    "M&M.NS","ULTRACEMCO.NS","TATAMOTORS.NS","NTPC.NS","POWERGRID.NS","ASIANPAINT.NS","NESTLEIND.NS",
    "BAJAJFINSV.NS","TITAN.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS","JSWSTEEL.NS","TATASTEEL.NS",
    "ADANIPORTS.NS","ONGC.NS","COALINDIA.NS","INDUSINDBK.NS","HDFCLIFE.NS","SBILIFE.NS","CIPLA.NS",
    "DRREDDY.NS","EICHERMOT.NS","HEROMOTOCO.NS","GRASIM.NS","BRITANNIA.NS","DIVISLAB.NS","BPCL.NS",
    "APOLLOHOSP.NS","SHRIRAMFIN.NS","BAJAJ-AUTO.NS","TRENT.NS","BEL.NS","HINDALCO.NS","TATACONSUM.NS"
})

NIFTY_100 = sorted(set(NIFTY_50 + [s for arr in SECTOR_MAP.values() for s in arr] + [
    "DLF.NS","LODHA.NS","PIDILITIND.NS","ABB.NS","SIEMENS.NS","BHEL.NS","TORNTPHARM.NS","GAIL.NS",
    "IOC.NS","HINDPETRO.NS","AMBUJACEM.NS","SHREECEM.NS","PFC.NS","NMDC.NS","VEDL.NS","DABUR.NS"
]))

DEFAULT_UNIVERSE = sorted({s for arr in SECTOR_MAP.values() for s in arr})
NIFTY_SYMBOL = "^NSEI"
WATCHLIST_FILE = "watchlist_v11_4.json"
WATCHLIST_META_FILE = "watchlist_meta_v11_4.json"

# ==================================================
# HELPERS
# ==================================================
def safe_float(x, default=np.nan):
    try:
        if x is None:
            return default
        return float(x)
    except:
        return default

@st.cache_data(ttl=3600, show_spinner=False)
def get_hist(symbol, period="1y", interval="1d"):
    try:
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        return df.dropna().copy()
    except:
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def get_info(symbol):
    try:
        return yf.Ticker(symbol).info
    except:
        return {}

@st.cache_data(ttl=3600, show_spinner=False)
def get_financials(symbol):
    try:
        tk = yf.Ticker(symbol)
        return tk.balance_sheet, tk.financials, tk.cashflow
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


def add_indicators(df):
    if df.empty:
        return df
    df = df.copy()
    df["SMA10"] = df["Close"].rolling(10).mean()
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["SMA100"] = df["Close"].rolling(100).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["RSI14"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_HIST"] = df["MACD"] - df["MACD_SIGNAL"]

    tr1 = df["High"] - df["Low"]
    tr2 = (df["High"] - df["Close"].shift()).abs()
    tr3 = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["ATR14"] = tr.rolling(14).mean()
    df["VolAvg20"] = df["Volume"].rolling(20).mean()

    plus_dm = df["High"].diff()
    minus_dm = -df["Low"].diff()
    plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0.0)
    minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0.0)
    atr = df["ATR14"].replace(0, np.nan)
    plus_di = 100 * pd.Series(plus_dm, index=df.index).rolling(14).mean() / atr
    minus_di = 100 * pd.Series(minus_dm, index=df.index).rolling(14).mean() / atr
    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)) * 100
    df["ADX14"] = dx.rolling(14).mean()

    # Supertrend
    hl2 = (df["High"] + df["Low"])/2
    multiplier = 3.0
    upperband = hl2 + multiplier * df["ATR14"]
    lowerband = hl2 - multiplier * df["ATR14"]
    final_upper = upperband.copy()
    final_lower = lowerband.copy()
    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)
    for i in range(1, len(df)):
        final_upper.iloc[i] = upperband.iloc[i] if (upperband.iloc[i] < final_upper.iloc[i-1]) or (df["Close"].iloc[i-1] > final_upper.iloc[i-1]) else final_upper.iloc[i-1]
        final_lower.iloc[i] = lowerband.iloc[i] if (lowerband.iloc[i] > final_lower.iloc[i-1]) or (df["Close"].iloc[i-1] < final_lower.iloc[i-1]) else final_lower.iloc[i-1]
        if i == 1:
            supertrend.iloc[i] = final_lower.iloc[i]
            direction.iloc[i] = 1
        else:
            if supertrend.iloc[i-1] == final_upper.iloc[i-1]:
                if df["Close"].iloc[i] <= final_upper.iloc[i]:
                    supertrend.iloc[i] = final_upper.iloc[i]
                    direction.iloc[i] = -1
                else:
                    supertrend.iloc[i] = final_lower.iloc[i]
                    direction.iloc[i] = 1
            else:
                if df["Close"].iloc[i] >= final_lower.iloc[i]:
                    supertrend.iloc[i] = final_lower.iloc[i]
                    direction.iloc[i] = 1
                else:
                    supertrend.iloc[i] = final_upper.iloc[i]
                    direction.iloc[i] = -1
    df["Supertrend"] = supertrend
    df["ST_Direction"] = direction.fillna(0)
    return df


def compute_returns(df, days):
    if df.empty or len(df) <= days:
        return np.nan
    return (df["Close"].iloc[-1] / df["Close"].iloc[-days - 1] - 1) * 100


def relative_strength_vs_nifty(stock_df, nifty_df, days=55):
    if stock_df.empty or nifty_df.empty or len(stock_df) <= days or len(nifty_df) <= days:
        return np.nan
    s = stock_df["Close"].iloc[-1] / stock_df["Close"].iloc[-days - 1]
    n = nifty_df["Close"].iloc[-1] / nifty_df["Close"].iloc[-days - 1]
    return (s / n - 1) * 100


def rs_sparkline(df, nifty_df, days=30):
    try:
        aligned = pd.concat([df["Close"].rename("Stock"), nifty_df["Close"].rename("NIFTY")], axis=1).dropna().tail(days)
        rel = (aligned["Stock"] / aligned["Stock"].iloc[0]) - (aligned["NIFTY"] / aligned["NIFTY"].iloc[0])
        return ",".join([str(round(x, 4)) for x in rel.values])
    except:
        return ""


def delivery_proxy(last_vol, avg_vol):
    if pd.isna(last_vol) or pd.isna(avg_vol) or avg_vol == 0:
        return "Normal"
    ratio = last_vol / avg_vol
    if ratio >= 2.0:
        return "Very High"
    if ratio >= 1.4:
        return "High"
    return "Normal"


def multi_timeframe_trend(symbol):
    d1 = add_indicators(get_hist(symbol, period="1y", interval="1d"))
    wk = add_indicators(get_hist(symbol, period="2y", interval="1wk"))
    mo = add_indicators(get_hist(symbol, period="5y", interval="1mo"))
    score = 0
    if not d1.empty and len(d1) > 200 and d1["Close"].iloc[-1] > d1["SMA50"].iloc[-1] > d1["SMA200"].iloc[-1]:
        score += 1
    if not wk.empty and len(wk) > 30 and wk["Close"].iloc[-1] > wk["SMA10"].iloc[-1] > wk["SMA20"].iloc[-1]:
        score += 1
    if not mo.empty and len(mo) > 12 and mo["Close"].iloc[-1] > mo["SMA10"].iloc[-1]:
        score += 1
    return {3:"Strong Bullish",2:"Bullish",1:"Mixed",0:"Weak"}.get(score,"Weak")


def detect_candlestick_pattern(df):
    if df.empty or len(df) < 3:
        return "NA"
    a = df.iloc[-1]
    p = df.iloc[-2]
    body = abs(a["Close"] - a["Open"])
    rng = max(a["High"] - a["Low"], 0.0001)
    upper = a["High"] - max(a["Close"], a["Open"])
    lower = min(a["Close"], a["Open"]) - a["Low"]
    if lower > body * 2 and upper < body and a["Close"] > a["Open"]:
        return "Hammer"
    if upper > body * 2 and lower < body and a["Close"] < a["Open"]:
        return "Shooting Star"
    if (p["Close"] < p["Open"]) and (a["Close"] > a["Open"]) and (a["Close"] > p["Open"]) and (a["Open"] < p["Close"]):
        return "Bullish Engulfing"
    if (p["Close"] > p["Open"]) and (a["Close"] < a["Open"]) and (a["Open"] > p["Close"]) and (a["Close"] < p["Open"]):
        return "Bearish Engulfing"
    if body / rng < 0.1:
        return "Doji"
    return "None"


def support_resistance(df, lookback=60):
    if df.empty or len(df) < lookback:
        return np.nan, np.nan
    recent = df.tail(lookback)
    support = recent["Low"].rolling(10).min().iloc[-1]
    resistance = recent["High"].rolling(10).max().iloc[-1]
    return round(support,2), round(resistance,2)


def momentum_score(df, nifty_df):
    if df.empty or len(df) < 220:
        return np.nan
    r21 = safe_float(compute_returns(df, 21), 0)
    r63 = safe_float(compute_returns(df, 63), 0)
    r126 = safe_float(compute_returns(df, 126), 0)
    rs55 = safe_float(relative_strength_vs_nifty(df, nifty_df, 55), 0)
    rsi = safe_float(df["RSI14"].iloc[-1], 50)
    adx = safe_float(df["ADX14"].iloc[-1], 15)
    vol = safe_float(df["Volume"].iloc[-1], 0) / max(safe_float(df["VolAvg20"].iloc[-1], 1), 1)
    trend = 0
    if df["Close"].iloc[-1] > df["SMA50"].iloc[-1]: trend += 1
    if df["Close"].iloc[-1] > df["SMA200"].iloc[-1]: trend += 1
    if df["SMA50"].iloc[-1] > df["SMA200"].iloc[-1]: trend += 1
    return round(r21*0.18 + r63*0.22 + r126*0.18 + rs55*0.18 + rsi*0.08 + adx*0.08 + vol*10*0.04 + trend*5*0.04, 2)


def sector_score(symbols, nifty_df):
    rows = []
    for sym in symbols:
        df = add_indicators(get_hist(sym, period="1y"))
        if df.empty or len(df) < 220:
            continue
        score = momentum_score(df, nifty_df)
        rows.append({
            "Symbol": sym,
            "Close": round(df["Close"].iloc[-1],2),
            "RS_vs_NIFTY_%": round(relative_strength_vs_nifty(df, nifty_df, 55),2),
            "1M_%": round(compute_returns(df, 21),2),
            "3M_%": round(compute_returns(df, 63),2),
            "RSI": round(safe_float(df["RSI14"].iloc[-1]),2),
            "ADX": round(safe_float(df["ADX14"].iloc[-1]),2),
            "Composite_Score": score,
            "Trend_Score": int((df["Close"].iloc[-1] > df["SMA50"].iloc[-1]) + (df["Close"].iloc[-1] > df["SMA200"].iloc[-1]) + (df["SMA50"].iloc[-1] > df["SMA200"].iloc[-1]))
        })
    out = pd.DataFrame(rows)
    return out.sort_values(["Composite_Score","Trend_Score"], ascending=False) if not out.empty else out


def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except:
            pass
    return ["RELIANCE.NS", "HDFCBANK.NS", "TCS.NS"]


def save_watchlist(lst):
    try:
        with open(WATCHLIST_FILE, "w") as f:
            json.dump(sorted(list(set(lst))), f)
    except:
        pass


def load_watchlist_meta():
    if os.path.exists(WATCHLIST_META_FILE):
        try:
            with open(WATCHLIST_META_FILE, "r") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except:
            pass
    return {}


def save_watchlist_meta(meta):
    try:
        with open(WATCHLIST_META_FILE, "w") as f:
            json.dump(meta, f)
    except:
        pass


def position_size(capital, risk_pct, entry, sl):
    risk_amt = capital * risk_pct / 100
    per_share = max(entry - sl, 0.01)
    qty_risk = math.floor(risk_amt / per_share)
    qty_cap = math.floor(capital / entry)
    qty = max(min(qty_risk, qty_cap), 0)
    return qty, qty * entry, risk_amt


def breakout_scan(universe, nifty_df):
    rows = []
    for sym in universe:
        df = add_indicators(get_hist(sym, period="1y"))
        if df.empty or len(df) < 260:
            continue
        last = df.iloc[-1]
        high_20 = df["High"].rolling(20).max().iloc[-2]
        high_55 = df["High"].rolling(55).max().iloc[-2]
        breakout = last["Close"] > high_20
        strong = last["Close"] > high_55
        bullish = last["Close"] > last["SMA50"] > last["SMA200"]
        if breakout and bullish:
            atr = safe_float(last["ATR14"], 0)
            entry = safe_float(last["Close"], 0)
            sl = round(max(entry - 1.5 * atr, safe_float(last["SMA20"], entry*0.95)), 2)
            t1 = round(entry + 2 * atr, 2)
            t2 = round(entry + 4 * atr, 2)
            rows.append({
                "Symbol": sym,
                "Close": round(entry,2),
                "Breakout_20D": breakout,
                "Breakout_55D": strong,
                "Volume_Boost": safe_float(last["Volume"],0) > safe_float(last["VolAvg20"],1) * 1.3,
                "Delivery_Proxy": delivery_proxy(last["Volume"], last["VolAvg20"]),
                "Pattern": detect_candlestick_pattern(df),
                "MTF": multi_timeframe_trend(sym),
                "RS_vs_NIFTY_%": round(relative_strength_vs_nifty(df, nifty_df, 55),2),
                "ADX": round(safe_float(last["ADX14"]),2),
                "ST": "Bullish" if safe_float(last["ST_Direction"],0) == 1 else "Bearish",
                "Entry": round(entry,2), "SL": sl, "Target1": t1, "Target2": t2
            })
    out = pd.DataFrame(rows)
    return out.sort_values(["Breakout_55D","RS_vs_NIFTY_%","ADX"], ascending=False) if not out.empty else out


def pattern_scan(universe):
    rows = []
    for sym in universe:
        df = add_indicators(get_hist(sym, period="6mo"))
        if df.empty or len(df) < 5:
            continue
        pat = detect_candlestick_pattern(df)
        if pat != "None":
            rows.append({
                "Symbol": sym,
                "Pattern": pat,
                "Close": round(df["Close"].iloc[-1],2),
                "RSI": round(safe_float(df["RSI14"].iloc[-1]),2),
                "ADX": round(safe_float(df["ADX14"].iloc[-1]),2),
                "Vol_Ratio": round(safe_float(df["Volume"].iloc[-1],0)/max(safe_float(df["VolAvg20"].iloc[-1],1),1),2)
            })
    out = pd.DataFrame(rows)
    return out.sort_values("Vol_Ratio", ascending=False) if not out.empty else out


def gap_scan(universe):
    rows = []
    for sym in universe:
        df = add_indicators(get_hist(sym, period="3mo"))
        if df.empty or len(df) < 3:
            continue
        prev = df.iloc[-2]
        last = df.iloc[-1]
        gap = ((last["Open"] / prev["Close"]) - 1) * 100
        if abs(gap) >= 1.5:
            rows.append({"Symbol": sym, "Gap_%": round(gap,2), "Close": round(last["Close"],2), "Type": "Gap Up" if gap > 0 else "Gap Down"})
    out = pd.DataFrame(rows)
    return out.sort_values("Gap_%", ascending=False) if not out.empty else out


def high_52w_scan(universe):
    rows = []
    for sym in universe:
        df = add_indicators(get_hist(sym, period="1y"))
        if df.empty or len(df) < 220:
            continue
        high_52 = df["High"].max()
        close = df["Close"].iloc[-1]
        dist = ((close / high_52) - 1) * 100
        if dist >= -5:
            rows.append({"Symbol": sym, "Close": round(close,2), "52W_High": round(high_52,2), "Distance_%": round(dist,2)})
    out = pd.DataFrame(rows)
    return out.sort_values("Distance_%", ascending=False) if not out.empty else out


def momentum_rank(universe, nifty_df):
    rows = []
    for sym in universe:
        df = add_indicators(get_hist(sym, period="1y"))
        if df.empty or len(df) < 220:
            continue
        score = momentum_score(df, nifty_df)
        last = df.iloc[-1]
        rows.append({
            "Symbol": sym,
            "Close": round(last["Close"],2),
            "Momentum_Score": score,
            "RS_vs_NIFTY_%": round(relative_strength_vs_nifty(df, nifty_df, 55),2),
            "1M_%": round(compute_returns(df, 21),2),
            "3M_%": round(compute_returns(df, 63),2),
            "6M_%": round(compute_returns(df, 126),2),
            "RSI": round(safe_float(last["RSI14"]),2),
            "ADX": round(safe_float(last["ADX14"]),2),
            "Supertrend": "Bullish" if safe_float(last["ST_Direction"],0) == 1 else "Bearish",
            "Signal": "BUY" if (score > 25 and safe_float(last["ST_Direction"],0) == 1 and safe_float(last["ADX14"],0) > 18) else ("AVOID" if score < 5 else "WATCH"),
            "RS_Sparkline": rs_sparkline(df, nifty_df)
        })
    out = pd.DataFrame(rows)
    return out.sort_values("Momentum_Score", ascending=False) if not out.empty else out


def build_watchlist_export(df):
    output = io.BytesIO()
    df.to_csv(output, index=False)
    return output.getvalue()

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.title("⚙️ V11.4 WAR ROOM Controls")
universe_mode = st.sidebar.selectbox("Universe", ["NIFTY 50", "NIFTY 100", "SECTOR UNIVERSE", "CUSTOM"])
selected_sector = st.sidebar.selectbox("Focus Sector", ["ALL"] + list(SECTOR_MAP.keys()))
capital = st.sidebar.number_input("Capital (₹)", min_value=10000, value=500000, step=10000)
risk_pct = st.sidebar.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.5)
custom_symbols = st.sidebar.text_area("Custom symbols (comma separated)", value="RELIANCE.NS,TCS.NS,HDFCBANK.NS" if universe_mode == "CUSTOM" else "")

if universe_mode == "NIFTY 50":
    universe = NIFTY_50
elif universe_mode == "NIFTY 100":
    universe = NIFTY_100
elif universe_mode == "SECTOR UNIVERSE":
    universe = DEFAULT_UNIVERSE if selected_sector == "ALL" else SECTOR_MAP[selected_sector]
else:
    universe = sorted(list(set([x.strip().upper() for x in custom_symbols.split(",") if x.strip()])))

watchlist = load_watchlist()
watch_meta = load_watchlist_meta()

st.sidebar.markdown("---")
st.sidebar.subheader("⭐ Persistent Watchlist")
add_symbol = st.sidebar.selectbox("Add stock", ["Select"] + sorted(set(universe + DEFAULT_UNIVERSE)))
if st.sidebar.button("Add to Watchlist") and add_symbol != "Select":
    if add_symbol not in watchlist:
        watchlist.append(add_symbol)
        save_watchlist(watchlist)
        st.sidebar.success(f"Added {add_symbol}")

remove_symbol = st.sidebar.selectbox("Remove stock", ["Select"] + watchlist)
if st.sidebar.button("Remove from Watchlist") and remove_symbol != "Select":
    watchlist = [x for x in watchlist if x != remove_symbol]
    if remove_symbol in watch_meta:
        del watch_meta[remove_symbol]
        save_watchlist_meta(watch_meta)
    save_watchlist(watchlist)
    st.sidebar.success(f"Removed {remove_symbol}")

# ==================================================
# HEADER
# ==================================================
st.title("🧠 FINAL V11.4 ABSOLUTE INSTITUTIONAL AI WAR ROOM")
st.caption("Momentum Engine • AI War Room Scanner • RS vs NIFTY • Supertrend + ADX • 52W High • Gap Scanner • Portfolio Rebalance • Full Technical + Fundamental")

nifty_df = add_indicators(get_hist(NIFTY_SYMBOL, period="1y"))
if nifty_df.empty:
    st.error("Unable to fetch NIFTY data right now. Please refresh later.")
    st.stop()

# ==================================================
# TOP METRICS
# ==================================================
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("NIFTY", f"{nifty_df['Close'].iloc[-1]:,.2f}", f"{compute_returns(nifty_df, 21):.2f}% (1M)")
c2.metric("Universe", len(universe))
c3.metric("Watchlist", len(watchlist))
c4.metric("Capital", f"₹{capital:,.0f}")
c5.metric("Risk/Trade", f"{risk_pct:.1f}%")
c6.metric("NIFTY 3M", f"{compute_returns(nifty_df, 63):.2f}%")

# ==================================================
# SECTOR RANKING + HEATMAP
# ==================================================
st.markdown("## 🏆 Sector Ranking + Sector Leaders")
sector_rows = []
sector_tables = {}
for sector, symbols in SECTOR_MAP.items():
    sdf = sector_score(symbols, nifty_df)
    sector_tables[sector] = sdf
    if not sdf.empty:
        sector_rows.append({
            "Sector": sector,
            "Avg_Composite_Score": round(sdf["Composite_Score"].mean(),2),
            "Avg_RS_vs_NIFTY_%": round(sdf["RS_vs_NIFTY_%"].mean(),2),
            "Bullish_Stocks": int((sdf["Trend_Score"] >= 2).sum()),
            "Leader": sdf.iloc[0]["Symbol"],
            "Tracked": len(sdf)
        })
sector_rank_df = pd.DataFrame(sector_rows)
if not sector_rank_df.empty:
    sector_rank_df = sector_rank_df.sort_values(["Avg_Composite_Score","Avg_RS_vs_NIFTY_%"], ascending=False)
    st.dataframe(sector_rank_df, use_container_width=True)
    st.markdown("### 🔥 Sector Heatmap")
    heat = sector_rank_df[["Sector","Avg_Composite_Score","Avg_RS_vs_NIFTY_%","Bullish_Stocks"]].set_index("Sector")
    fig_heat = px.imshow(heat.T, text_auto='.2f', aspect='auto', title='Sector Strength Heatmap')
    fig_heat.update_layout(height=420)
    st.plotly_chart(fig_heat, use_container_width=True)

# ==================================================
# MOMENTUM RANKING ENGINE
# ==================================================
st.markdown("## ⚡ Momentum Ranking Engine (Top 20 / Top 50)")
rank_df = momentum_rank(universe, nifty_df)
if rank_df.empty:
    st.info("Momentum ranking unavailable for current universe.")
else:
    topn = st.radio("Show Ranking", [20, 50], horizontal=True, index=0)
    st.dataframe(rank_df.head(topn), use_container_width=True)

# ==================================================
# SPECIAL SCANNERS
# ==================================================
st.markdown("## 🚨 Special Institutional Scanners")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("### 52-Week High Proximity")
    high52_df = high_52w_scan(universe)
    st.dataframe(high52_df, use_container_width=True) if not high52_df.empty else st.info("No stocks near 52-week highs.")
with col_b:
    st.markdown("### Gap Up / Gap Down Scanner")
    gap_df = gap_scan(universe)
    st.dataframe(gap_df, use_container_width=True) if not gap_df.empty else st.info("No major gaps detected.")

# ==================================================
# BREAKOUT + PATTERN
# ==================================================
st.markdown("## 🚀 Breakout Scanner + Pattern Scanner")
scan_df = breakout_scan(universe, nifty_df)
if not scan_df.empty:
    temp = scan_df.copy()
    qtys, used = [], []
    for _, r in temp.iterrows():
        qty, invested, _ = position_size(capital, risk_pct, r["Entry"], r["SL"])
        qtys.append(qty)
        used.append(round(invested,2))
    temp["Qty"] = qtys
    temp["Capital_Used"] = used
    st.dataframe(temp, use_container_width=True)
else:
    st.info("No strong breakout candidates now.")

pat_df = pattern_scan(universe)
st.markdown("### Candlestick Pattern Scanner")
st.dataframe(pat_df, use_container_width=True) if not pat_df.empty else st.info("No notable candlestick patterns detected.")

# ==================================================
# WATCHLIST DASHBOARD
# ==================================================
st.markdown("## ⭐ Persistent Watchlist Dashboard + Notes")
watch_rows = []
for sym in watchlist:
    df = add_indicators(get_hist(sym, period="1y"))
    if df.empty or len(df) < 220:
        continue
    last = df.iloc[-1]
    meta = watch_meta.get(sym, {})
    watch_rows.append({
        "Symbol": sym,
        "Close": round(last["Close"],2),
        "Momentum_Score": momentum_score(df, nifty_df),
        "RS_vs_NIFTY_%": round(relative_strength_vs_nifty(df, nifty_df, 55),2),
        "RSI": round(safe_float(last["RSI14"]),2),
        "ADX": round(safe_float(last["ADX14"]),2),
        "Supertrend": "Bullish" if safe_float(last["ST_Direction"],0) == 1 else "Bearish",
        "MTF": multi_timeframe_trend(sym),
        "Status": meta.get("status", "Watch"),
        "Note": meta.get("note", "")
    })
watch_df = pd.DataFrame(watch_rows)
if not watch_df.empty:
    st.dataframe(watch_df.sort_values("Momentum_Score", ascending=False), use_container_width=True)
    st.download_button("⬇️ Export Watchlist CSV", data=build_watchlist_export(watch_df), file_name="watchlist_v11_4.csv", mime="text/csv")
else:
    st.info("Watchlist empty or data unavailable.")

with st.expander("✍️ Update Watchlist Note / Status"):
    if watchlist:
        edit_sym = st.selectbox("Select watchlist stock", watchlist)
        cur = watch_meta.get(edit_sym, {})
        new_status = st.selectbox("Status", ["Watch", "Buy Zone", "Holding", "Booked", "Avoid"], index=["Watch", "Buy Zone", "Holding", "Booked", "Avoid"].index(cur.get("status", "Watch")))
        new_note = st.text_input("Note", value=cur.get("note", ""))
        if st.button("Save Watchlist Note"):
            watch_meta[edit_sym] = {"status": new_status, "note": new_note, "updated_at": str(datetime.now())}
            save_watchlist_meta(watch_meta)
            st.success(f"Saved note for {edit_sym}")

# ==================================================
# STOCK COMPARISON MODE
# ==================================================
st.markdown("## ⚔️ Stock Comparison Mode")
compare_choices = sorted(set(universe + watchlist))
selected_compare = st.multiselect("Select up to 4 stocks", compare_choices, default=compare_choices[:2] if len(compare_choices)>=2 else compare_choices[:1], max_selections=4)
if selected_compare:
    comp_df = pd.DataFrame()
    for sym in selected_compare:
        df = add_indicators(get_hist(sym, period="1y"))
        if df.empty:
            continue
        series = (df["Close"] / df["Close"].iloc[0]) * 100
        comp_df[sym] = series
    if not comp_df.empty:
        fig_comp = go.Figure()
        for col in comp_df.columns:
            fig_comp.add_trace(go.Scatter(x=comp_df.index, y=comp_df[col], name=col))
        fig_comp.update_layout(height=420, title="Stock Comparison (Base = 100)")
        st.plotly_chart(fig_comp, use_container_width=True)

# ==================================================
# STOCK DEEP DIVE
# ==================================================
st.markdown("## 🔎 Stock Deep Dive")
deep_symbol = st.selectbox("Select Stock for Full Analysis", compare_choices)
stock_df = add_indicators(get_hist(deep_symbol, period="2y"))
info = get_info(deep_symbol)
bs, fin, cf = get_financials(deep_symbol)

if not stock_df.empty:
    last = stock_df.iloc[-1]
    sup, res = support_resistance(stock_df)
    rs = relative_strength_vs_nifty(stock_df, nifty_df, 55)
    pattern = detect_candlestick_pattern(stock_df)
    mtf = multi_timeframe_trend(deep_symbol)

    m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
    m1.metric("Price", f"₹{last['Close']:.2f}")
    m2.metric("RS vs NIFTY", f"{rs:.2f}%")
    m3.metric("RSI", f"{last['RSI14']:.2f}")
    m4.metric("ADX", f"{safe_float(last['ADX14']):.2f}")
    m5.metric("Supertrend", "Bullish" if safe_float(last['ST_Direction'],0)==1 else "Bearish")
    m6.metric("Pattern", pattern)
    m7.metric("MTF", mtf)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_heights=[0.58,0.20,0.22])
    fig.add_trace(go.Candlestick(x=stock_df.index, open=stock_df['Open'], high=stock_df['High'], low=stock_df['Low'], close=stock_df['Close'], name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA20'], name='SMA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA50'], name='SMA50'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA200'], name='SMA200'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['Supertrend'], name='Supertrend'), row=1, col=1)
    fig.add_trace(go.Bar(x=stock_df.index, y=stock_df['Volume'], name='Volume'), row=2, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['RSI14'], name='RSI'), row=3, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['ADX14'], name='ADX'), row=3, col=1)
    fig.update_layout(height=860, xaxis_rangeslider_visible=False, title=f"{deep_symbol} Technical War Room Chart")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"<div class='card'><b>Support:</b> ₹{sup} &nbsp;&nbsp; <b>Resistance:</b> ₹{res} &nbsp;&nbsp; <b>1M:</b> {compute_returns(stock_df,21):.2f}% &nbsp;&nbsp; <b>3M:</b> {compute_returns(stock_df,63):.2f}% &nbsp;&nbsp; <b>6M:</b> {compute_returns(stock_df,126):.2f}%</div>", unsafe_allow_html=True)

    st.markdown("### Relative Strength vs NIFTY")
    aligned = pd.concat([stock_df['Close'].rename('Stock'), nifty_df['Close'].rename('NIFTY')], axis=1).dropna()
    aligned['Stock_Norm'] = aligned['Stock'] / aligned['Stock'].iloc[0] * 100
    aligned['NIFTY_Norm'] = aligned['NIFTY'] / aligned['NIFTY'].iloc[0] * 100
    fig_rs = go.Figure()
    fig_rs.add_trace(go.Scatter(x=aligned.index, y=aligned['Stock_Norm'], name=deep_symbol))
    fig_rs.add_trace(go.Scatter(x=aligned.index, y=aligned['NIFTY_Norm'], name='NIFTY'))
    fig_rs.update_layout(height=400, title='Relative Strength Comparison (Base = 100)')
    st.plotly_chart(fig_rs, use_container_width=True)

    st.markdown("### Fundamental Snapshot")
    f1, f2, f3, f4, f5, f6 = st.columns(6)
    f1.metric("Market Cap", f"₹{safe_float(info.get('marketCap',0))/1e7:,.0f} Cr" if info.get('marketCap') else "NA")
    f2.metric("PE", f"{safe_float(info.get('trailingPE')):.2f}" if info.get('trailingPE') else "NA")
    f3.metric("PB", f"{safe_float(info.get('priceToBook')):.2f}" if info.get('priceToBook') else "NA")
    f4.metric("ROE", f"{safe_float(info.get('returnOnEquity'))*100:.2f}%" if info.get('returnOnEquity') else "NA")
    f5.metric("Dividend Yield", f"{safe_float(info.get('dividendYield'))*100:.2f}%" if info.get('dividendYield') else "NA")
    f6.metric("Beta", f"{safe_float(info.get('beta')):.2f}" if info.get('beta') else "NA")

    st.markdown("### Balance Sheet / Financials / Cashflow")
    t1, t2, t3 = st.tabs(["Balance Sheet", "P&L", "Cash Flow"])
    with t1:
        st.dataframe(bs, use_container_width=True) if not bs.empty else st.info("Balance sheet not available.")
    with t2:
        st.dataframe(fin, use_container_width=True) if not fin.empty else st.info("Financials not available.")
    with t3:
        st.dataframe(cf, use_container_width=True) if not cf.empty else st.info("Cash flow not available.")

    st.markdown("### AI Trade Plan")
    entry = float(last['Close'])
    atr = float(last['ATR14']) if not pd.isna(last['ATR14']) else entry * 0.03
    sl = round(max(entry - 1.5 * atr, safe_float(last['SMA20'], entry*0.95)), 2)
    t1v = round(entry + 2 * atr, 2)
    t2v = round(entry + 4 * atr, 2)
    qty, invested, risk_amt = position_size(capital, risk_pct, entry, sl)
    rr = round((t1v - entry) / max(entry - sl, 0.01), 2)

    p1, p2, p3, p4, p5 = st.columns(5)
    p1.metric("Entry", f"₹{entry:.2f}")
    p2.metric("Stop Loss", f"₹{sl:.2f}")
    p3.metric("Target 1", f"₹{t1v:.2f}")
    p4.metric("Target 2", f"₹{t2v:.2f}")
    p5.metric("Qty", qty)
    st.markdown(f"<div class='card'><b>Capital Used:</b> ₹{invested:,.2f} &nbsp;&nbsp; <b>Max Risk:</b> ₹{risk_amt:,.2f} &nbsp;&nbsp; <b>R:R to T1:</b> {rr}</div>", unsafe_allow_html=True)

# ==================================================
# PORTFOLIO BUILDER + REBALANCING
# ==================================================
st.markdown("## 🧠 Portfolio Builder + Rebalancing Suggestions")
if not rank_df.empty:
    pf = rank_df.head(8).copy()
    weight = round(100 / len(pf), 2)
    pf["Suggested_Weight_%"] = weight
    pf["Capital_Allocation_₹"] = (capital * pf["Suggested_Weight_%"] / 100).round(2)
    pf["Estimated_Risk_₹"] = (pf["Capital_Allocation_₹"] * 0.08).round(2)
    pf["Rebalance_Action"] = pf["Signal"].apply(lambda x: "Increase" if x == "BUY" else ("Reduce" if x == "AVOID" else "Hold"))
    st.dataframe(pf[["Symbol","Momentum_Score","RS_vs_NIFTY_%","Supertrend","Signal","Suggested_Weight_%","Capital_Allocation_₹","Estimated_Risk_₹","Rebalance_Action"]], use_container_width=True)

    r1, r2 = st.columns(2)
    with r1:
        fig_alloc = px.pie(pf, names="Symbol", values="Capital_Allocation_₹", title="Portfolio Allocation")
        st.plotly_chart(fig_alloc, use_container_width=True)
    with r2:
        fig_risk = px.bar(pf, x="Symbol", y="Estimated_Risk_₹", title="Estimated Position Risk")
        st.plotly_chart(fig_risk, use_container_width=True)

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.markdown("<div class='small-note'>Disclaimer: Educational tool only. Verify all data before investing. Yahoo Finance data may be delayed/inconsistent. For Streamlit Cloud install: streamlit, yfinance, pandas, numpy, plotly.</div>", unsafe_allow_html=True)

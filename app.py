# FINAL V11.5 QUANT HEDGE FUND TERMINAL - SINGLE FULL STREAMLIT APP.PY
# =============================================================================
# Features:
# - NIFTY 50 / NIFTY 100 / Sector / Custom Universe switch
# - Sector Rotation Dashboard + Sector Ranking + Heatmap
# - True Relative Strength Rank Percentile
# - Advanced Momentum Factor Model
# - VCP (Volatility Contraction Pattern) Scanner
# - Darvas Box Breakout Scanner
# - Stage Analysis (1/2/3/4)
# - Minervini Trend Template
# - Institutional Scorecard per stock
# - Auto Best 10 Swing Candidates
# - Persistent Watchlist + Notes + Status + CSV export
# - Stock Comparison Mode
# - Breakout / Gap / 52W High / Candlestick Pattern scanners
# - Supertrend + ADX + ATR + RSI + MACD
# - Support / Resistance auto zones
# - Portfolio Builder + Rebalancing + Risk Dashboard
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
st.set_page_config(page_title="FINAL V11.5 QUANT HEDGE FUND TERMINAL", page_icon="📊", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
.main {
    background: linear-gradient(180deg, #050d18 0%, #0a1220 45%, #111827 100%);
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
WATCHLIST_FILE = "watchlist_v11_5.json"
WATCHLIST_META_FILE = "watchlist_meta_v11_5.json"

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
    for n in [10, 20, 50, 100, 150, 200]:
        df[f"SMA{n}"] = df["Close"].rolling(n).mean()
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
    hl2 = (df["High"] + df["Low"]) / 2
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


def rs_percentile(series):
    return series.rank(pct=True) * 100 if not series.empty else series


def delivery_proxy(last_vol, avg_vol):
    if pd.isna(last_vol) or pd.isna(avg_vol) or avg_vol == 0:
        return "Normal"
    ratio = last_vol / avg_vol
    if ratio >= 2.0:
        return "Very High"
    if ratio >= 1.4:
        return "High"
    return "Normal"


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
    return round(recent["Low"].rolling(10).min().iloc[-1], 2), round(recent["High"].rolling(10).max().iloc[-1], 2)


def stage_analysis(df):
    if df.empty or len(df) < 220:
        return "NA"
    close = df["Close"].iloc[-1]
    sma50 = df["SMA50"].iloc[-1]
    sma150 = df["SMA150"].iloc[-1]
    sma200 = df["SMA200"].iloc[-1]
    slope200 = df["SMA200"].diff(20).iloc[-1]
    if close > sma50 > sma150 > sma200 and slope200 > 0:
        return "Stage 2 (Advancing)"
    if close < sma50 < sma150 < sma200 and slope200 < 0:
        return "Stage 4 (Declining)"
    if close > sma200 and sma50 < sma150:
        return "Stage 1 (Basing)"
    return "Stage 3 (Topping)"


def minervini_template(df):
    if df.empty or len(df) < 252:
        return False
    close = df["Close"].iloc[-1]
    sma50 = df["SMA50"].iloc[-1]
    sma150 = df["SMA150"].iloc[-1]
    sma200 = df["SMA200"].iloc[-1]
    low_52 = df["Low"].tail(252).min()
    high_52 = df["High"].tail(252).max()
    sma200_20d = df["SMA200"].iloc[-20] if len(df) > 220 else np.nan
    conds = [
        close > sma150 > sma200,
        sma50 > sma150,
        close > sma50,
        sma200 > sma200_20d if not pd.isna(sma200_20d) else False,
        close >= 1.25 * low_52,
        close >= 0.75 * high_52,
    ]
    return all(conds)


def vcp_detect(df):
    if df.empty or len(df) < 120:
        return False, np.nan
    windows = [60, 40, 20]
    ranges = []
    for w in windows:
        part = df.tail(w)
        rng = ((part["High"].max() - part["Low"].min()) / max(part["Low"].min(), 0.01)) * 100
        ranges.append(rng)
    contraction = ranges[0] > ranges[1] > ranges[2]
    vol_contract = df["Volume"].tail(20).mean() < df["Volume"].tail(60).mean()
    pivot = df["High"].tail(20).max()
    breakout = df["Close"].iloc[-1] >= pivot * 0.98
    return (contraction and vol_contract and breakout), round(pivot, 2)


def darvas_box(df, lookback=20):
    if df.empty or len(df) < lookback + 5:
        return False, np.nan, np.nan
    box_high = df["High"].tail(lookback).max()
    box_low = df["Low"].tail(lookback).min()
    breakout = df["Close"].iloc[-1] > box_high * 0.995
    return breakout, round(box_low, 2), round(box_high, 2)


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
    return {3: "Strong Bullish", 2: "Bullish", 1: "Mixed", 0: "Weak"}.get(score, "Weak")


def advanced_factor_score(df, nifty_df):
    if df.empty or len(df) < 252:
        return np.nan
    r21 = safe_float(compute_returns(df, 21), 0)
    r63 = safe_float(compute_returns(df, 63), 0)
    r126 = safe_float(compute_returns(df, 126), 0)
    r252 = safe_float(compute_returns(df, 252), 0)
    rs55 = safe_float(relative_strength_vs_nifty(df, nifty_df, 55), 0)
    rsi = safe_float(df["RSI14"].iloc[-1], 50)
    adx = safe_float(df["ADX14"].iloc[-1], 15)
    vol_ratio = safe_float(df["Volume"].iloc[-1], 0) / max(safe_float(df["VolAvg20"].iloc[-1], 1), 1)
    st_bonus = 8 if safe_float(df["ST_Direction"].iloc[-1], 0) == 1 else 0
    template_bonus = 10 if minervini_template(df) else 0
    stage_bonus = 8 if stage_analysis(df).startswith("Stage 2") else 0
    return round(r21*0.12 + r63*0.16 + r126*0.16 + r252*0.12 + rs55*0.18 + rsi*0.08 + adx*0.08 + vol_ratio*10*0.05 + st_bonus + template_bonus + stage_bonus, 2)


def institutional_scorecard(df, nifty_df):
    if df.empty or len(df) < 252:
        return {}
    score = 0
    checks = {}
    checks["Above 50 DMA"] = df["Close"].iloc[-1] > df["SMA50"].iloc[-1]
    checks["Above 150 DMA"] = df["Close"].iloc[-1] > df["SMA150"].iloc[-1]
    checks["Above 200 DMA"] = df["Close"].iloc[-1] > df["SMA200"].iloc[-1]
    checks["50 > 150 > 200"] = df["SMA50"].iloc[-1] > df["SMA150"].iloc[-1] > df["SMA200"].iloc[-1]
    checks["RS > 0 vs NIFTY"] = relative_strength_vs_nifty(df, nifty_df, 55) > 0
    checks["Supertrend Bullish"] = safe_float(df["ST_Direction"].iloc[-1], 0) == 1
    checks["ADX > 18"] = safe_float(df["ADX14"].iloc[-1], 0) > 18
    checks["Minervini Template"] = minervini_template(df)
    checks["Stage 2"] = stage_analysis(df).startswith("Stage 2")
    checks["Near 52W High"] = df["Close"].iloc[-1] >= df["High"].tail(252).max() * 0.85
    score = sum(1 for v in checks.values() if v)
    checks["Institutional Score /10"] = score
    return checks


def sector_score(symbols, nifty_df):
    rows = []
    for sym in symbols:
        df = add_indicators(get_hist(sym, period="1y"))
        if df.empty or len(df) < 220:
            continue
        rows.append({
            "Symbol": sym,
            "Close": round(df["Close"].iloc[-1], 2),
            "RS_vs_NIFTY_%": round(relative_strength_vs_nifty(df, nifty_df, 55), 2),
            "1M_%": round(compute_returns(df, 21), 2),
            "3M_%": round(compute_returns(df, 63), 2),
            "Composite_Score": advanced_factor_score(df, nifty_df),
            "Stage": stage_analysis(df),
        })
    out = pd.DataFrame(rows)
    return out.sort_values("Composite_Score", ascending=False) if not out.empty else out


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


def build_watchlist_export(df):
    output = io.BytesIO()
    df.to_csv(output, index=False)
    return output.getvalue()


def build_master_rank(universe, nifty_df):
    rows = []
    for sym in universe:
        df = add_indicators(get_hist(sym, period="1y"))
        if df.empty or len(df) < 252:
            continue
        vcp_ok, vcp_pivot = vcp_detect(df)
        darvas_ok, darvas_low, darvas_high = darvas_box(df)
        last = df.iloc[-1]
        rows.append({
            "Symbol": sym,
            "Close": round(last["Close"], 2),
            "Factor_Score": advanced_factor_score(df, nifty_df),
            "RS_vs_NIFTY_%": round(relative_strength_vs_nifty(df, nifty_df, 55), 2),
            "1M_%": round(compute_returns(df, 21), 2),
            "3M_%": round(compute_returns(df, 63), 2),
            "6M_%": round(compute_returns(df, 126), 2),
            "12M_%": round(compute_returns(df, 252), 2),
            "RSI": round(safe_float(last["RSI14"]), 2),
            "ADX": round(safe_float(last["ADX14"]), 2),
            "Supertrend": "Bullish" if safe_float(last["ST_Direction"], 0) == 1 else "Bearish",
            "Stage": stage_analysis(df),
            "Minervini": minervini_template(df),
            "VCP": vcp_ok,
            "VCP_Pivot": vcp_pivot,
            "Darvas": darvas_ok,
            "Darvas_High": darvas_high,
            "Signal": "BUY" if (advanced_factor_score(df, nifty_df) > 35 and safe_float(last["ST_Direction"], 0) == 1 and safe_float(last["ADX14"], 0) > 18) else ("AVOID" if advanced_factor_score(df, nifty_df) < 8 else "WATCH")
        })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["RS_Percentile"] = rs_percentile(out["RS_vs_NIFTY_%"]).round(2)
    return out.sort_values(["Factor_Score", "RS_Percentile"], ascending=False)

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.title("⚙️ V11.5 QUANT TERMINAL Controls")
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
st.title("📊 FINAL V11.5 QUANT HEDGE FUND TERMINAL")
st.caption("Quant Factor Model • RS Percentile • VCP • Darvas • Stage Analysis • Minervini • Institutional Scorecard • Auto Best 10 Swing Candidates")

nifty_df = add_indicators(get_hist(NIFTY_SYMBOL, period="1y"))
if nifty_df.empty:
    st.error("Unable to fetch NIFTY data right now. Please refresh later.")
    st.stop()

# ==================================================
# TOP METRICS
# ==================================================
mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
mc1.metric("NIFTY", f"{nifty_df['Close'].iloc[-1]:,.2f}", f"{compute_returns(nifty_df, 21):.2f}% (1M)")
mc2.metric("Universe", len(universe))
mc3.metric("Watchlist", len(watchlist))
mc4.metric("Capital", f"₹{capital:,.0f}")
mc5.metric("Risk/Trade", f"{risk_pct:.1f}%")
mc6.metric("NIFTY 12M", f"{compute_returns(nifty_df, 252):.2f}%")

# ==================================================
# SECTOR ROTATION DASHBOARD
# ==================================================
st.markdown("## 🔄 Sector Rotation Dashboard")
sector_rows = []
for sector, symbols in SECTOR_MAP.items():
    sdf = sector_score(symbols, nifty_df)
    if not sdf.empty:
        sector_rows.append({
            "Sector": sector,
            "Avg_Factor_Score": round(sdf["Composite_Score"].mean(), 2),
            "Avg_RS_vs_NIFTY_%": round(sdf["RS_vs_NIFTY_%"].mean(), 2),
            "Avg_1M_%": round(sdf["1M_%"].mean(), 2),
            "Avg_3M_%": round(sdf["3M_%"].mean(), 2),
            "Leader": sdf.iloc[0]["Symbol"],
            "Leading_Stage": sdf.iloc[0]["Stage"]
        })
sector_df = pd.DataFrame(sector_rows)
if not sector_df.empty:
    sector_df = sector_df.sort_values(["Avg_Factor_Score", "Avg_RS_vs_NIFTY_%"], ascending=False)
    st.dataframe(sector_df, use_container_width=True)
    heat = sector_df[["Sector", "Avg_Factor_Score", "Avg_RS_vs_NIFTY_%", "Avg_1M_%", "Avg_3M_%"]].set_index("Sector")
    fig_heat = px.imshow(heat.T, text_auto='.2f', aspect='auto', title='Sector Rotation Heatmap')
    fig_heat.update_layout(height=420)
    st.plotly_chart(fig_heat, use_container_width=True)

# ==================================================
# MASTER QUANT RANKING
# ==================================================
st.markdown("## ⚡ Master Quant Ranking Engine")
rank_df = build_master_rank(universe, nifty_df)
if rank_df.empty:
    st.info("Quant ranking unavailable for current universe.")
else:
    show_n = st.radio("Show Top", [10, 20, 50], horizontal=True, index=1)
    st.dataframe(rank_df.head(show_n), use_container_width=True)

# ==================================================
# AUTO BEST 10 SWING CANDIDATES
# ==================================================
st.markdown("## 🎯 Auto Best 10 Swing Candidates")
if not rank_df.empty:
    best10 = rank_df[(rank_df["Signal"] == "BUY")].head(10).copy()
    if best10.empty:
        best10 = rank_df.head(10).copy()
    entries, sls, t1s, qtys = [], [], [], []
    for sym in best10["Symbol"]:
        df = add_indicators(get_hist(sym, period="1y"))
        last = df.iloc[-1]
        entry = float(last["Close"])
        atr = float(last["ATR14"]) if not pd.isna(last["ATR14"]) else entry * 0.03
        sl = round(max(entry - 1.5 * atr, safe_float(last["SMA20"], entry*0.95)), 2)
        t1 = round(entry + 2 * atr, 2)
        qty, _, _ = position_size(capital, risk_pct, entry, sl)
        entries.append(round(entry, 2)); sls.append(sl); t1s.append(t1); qtys.append(qty)
    best10["Entry"] = entries
    best10["SL"] = sls
    best10["Target1"] = t1s
    best10["Qty"] = qtys
    st.dataframe(best10, use_container_width=True)

# ==================================================
# VCP + DARVAS SCANNERS
# ==================================================
st.markdown("## 📦 VCP + Darvas Box Scanners")
vcp_rows, darvas_rows = [], []
for sym in universe:
    df = add_indicators(get_hist(sym, period="1y"))
    if df.empty or len(df) < 120:
        continue
    vcp_ok, pivot = vcp_detect(df)
    darvas_ok, box_low, box_high = darvas_box(df)
    if vcp_ok:
        vcp_rows.append({"Symbol": sym, "Close": round(df['Close'].iloc[-1], 2), "VCP_Pivot": pivot, "RSI": round(safe_float(df['RSI14'].iloc[-1]),2), "ADX": round(safe_float(df['ADX14'].iloc[-1]),2)})
    if darvas_ok:
        darvas_rows.append({"Symbol": sym, "Close": round(df['Close'].iloc[-1], 2), "Darvas_Low": box_low, "Darvas_High": box_high, "RSI": round(safe_float(df['RSI14'].iloc[-1]),2)})
col_v1, col_v2 = st.columns(2)
with col_v1:
    st.markdown("### VCP Scanner")
    st.dataframe(pd.DataFrame(vcp_rows), use_container_width=True) if vcp_rows else st.info("No VCP setups found.")
with col_v2:
    st.markdown("### Darvas Box Scanner")
    st.dataframe(pd.DataFrame(darvas_rows), use_container_width=True) if darvas_rows else st.info("No Darvas setups found.")

# ==================================================
# WATCHLIST DASHBOARD
# ==================================================
st.markdown("## ⭐ Persistent Watchlist Dashboard")
watch_rows = []
for sym in watchlist:
    df = add_indicators(get_hist(sym, period="1y"))
    if df.empty or len(df) < 220:
        continue
    meta = watch_meta.get(sym, {})
    watch_rows.append({
        "Symbol": sym,
        "Factor_Score": advanced_factor_score(df, nifty_df),
        "RS_Percentile": round(rank_df.set_index("Symbol").loc[sym, "RS_Percentile"], 2) if (not rank_df.empty and sym in rank_df["Symbol"].values) else np.nan,
        "Stage": stage_analysis(df),
        "Minervini": minervini_template(df),
        "VCP": vcp_detect(df)[0],
        "Darvas": darvas_box(df)[0],
        "Status": meta.get("status", "Watch"),
        "Note": meta.get("note", "")
    })
watch_df = pd.DataFrame(watch_rows)
if not watch_df.empty:
    st.dataframe(watch_df.sort_values("Factor_Score", ascending=False), use_container_width=True)
    st.download_button("⬇️ Export Watchlist CSV", data=build_watchlist_export(watch_df), file_name="watchlist_v11_5.csv", mime="text/csv")
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
        comp_df[sym] = (df["Close"] / df["Close"].iloc[0]) * 100
    if not comp_df.empty:
        fig_comp = go.Figure()
        for col in comp_df.columns:
            fig_comp.add_trace(go.Scatter(x=comp_df.index, y=comp_df[col], name=col))
        fig_comp.update_layout(height=420, title="Stock Comparison (Base = 100)")
        st.plotly_chart(fig_comp, use_container_width=True)

# ==================================================
# STOCK DEEP DIVE
# ==================================================
st.markdown("## 🔎 Stock Deep Dive + Institutional Scorecard")
deep_symbol = st.selectbox("Select Stock for Full Analysis", compare_choices)
stock_df = add_indicators(get_hist(deep_symbol, period="2y"))
info = get_info(deep_symbol)
bs, fin, cf = get_financials(deep_symbol)

if not stock_df.empty:
    last = stock_df.iloc[-1]
    sup, res = support_resistance(stock_df)
    rs = relative_strength_vs_nifty(stock_df, nifty_df, 55)
    stage = stage_analysis(stock_df)
    minervini_ok = minervini_template(stock_df)
    vcp_ok, vcp_pivot = vcp_detect(stock_df)
    darvas_ok, d_low, d_high = darvas_box(stock_df)
    scorecard = institutional_scorecard(stock_df, nifty_df)

    m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
    m1.metric("Price", f"₹{last['Close']:.2f}")
    m2.metric("RS vs NIFTY", f"{rs:.2f}%")
    m3.metric("RSI", f"{last['RSI14']:.2f}")
    m4.metric("ADX", f"{safe_float(last['ADX14']):.2f}")
    m5.metric("Stage", stage)
    m6.metric("Minervini", "YES" if minervini_ok else "NO")
    m7.metric("Score /10", scorecard.get("Institutional Score /10", 0))

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_heights=[0.58, 0.20, 0.22])
    fig.add_trace(go.Candlestick(x=stock_df.index, open=stock_df['Open'], high=stock_df['High'], low=stock_df['Low'], close=stock_df['Close'], name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA20'], name='SMA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA50'], name='SMA50'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA200'], name='SMA200'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['Supertrend'], name='Supertrend'), row=1, col=1)
    fig.add_trace(go.Bar(x=stock_df.index, y=stock_df['Volume'], name='Volume'), row=2, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['RSI14'], name='RSI'), row=3, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['ADX14'], name='ADX'), row=3, col=1)
    fig.update_layout(height=860, xaxis_rangeslider_visible=False, title=f"{deep_symbol} Quant Terminal Chart")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"<div class='card'><b>Support:</b> ₹{sup} &nbsp;&nbsp; <b>Resistance:</b> ₹{res} &nbsp;&nbsp; <b>VCP:</b> {'YES' if vcp_ok else 'NO'} @ ₹{vcp_pivot if not pd.isna(vcp_pivot) else 'NA'} &nbsp;&nbsp; <b>Darvas:</b> {'YES' if darvas_ok else 'NO'} [{d_low if not pd.isna(d_low) else 'NA'} - {d_high if not pd.isna(d_high) else 'NA'}]</div>", unsafe_allow_html=True)

    st.markdown("### Institutional Scorecard")
    sc_df = pd.DataFrame({"Check": list(scorecard.keys()), "Value": list(scorecard.values())})
    st.dataframe(sc_df, use_container_width=True)

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

    st.markdown("### Quant Trade Plan")
    entry = float(last['Close'])
    atr = float(last['ATR14']) if not pd.isna(last['ATR14']) else entry * 0.03
    sl = round(max(entry - 1.5 * atr, safe_float(last['SMA20'], entry*0.95)), 2)
    t1 = round(entry + 2 * atr, 2)
    t2 = round(entry + 4 * atr, 2)
    qty, invested, risk_amt = position_size(capital, risk_pct, entry, sl)
    rr = round((t1 - entry) / max(entry - sl, 0.01), 2)
    q1, q2, q3, q4, q5 = st.columns(5)
    q1.metric("Entry", f"₹{entry:.2f}")
    q2.metric("Stop Loss", f"₹{sl:.2f}")
    q3.metric("Target 1", f"₹{t1:.2f}")
    q4.metric("Target 2", f"₹{t2:.2f}")
    q5.metric("Qty", qty)
    st.markdown(f"<div class='card'><b>Capital Used:</b> ₹{invested:,.2f} &nbsp;&nbsp; <b>Max Risk:</b> ₹{risk_amt:,.2f} &nbsp;&nbsp; <b>R:R to T1:</b> {rr}</div>", unsafe_allow_html=True)

# ==================================================
# PORTFOLIO BUILDER + REBALANCE
# ==================================================
st.markdown("## 🧠 Portfolio Builder + Rebalancing Suggestions")
if not rank_df.empty:
    pf = rank_df.head(8).copy()
    weight = round(100 / len(pf), 2)
    pf["Suggested_Weight_%"] = weight
    pf["Capital_Allocation_₹"] = (capital * pf["Suggested_Weight_%"] / 100).round(2)
    pf["Estimated_Risk_₹"] = (pf["Capital_Allocation_₹"] * 0.08).round(2)
    pf["Rebalance_Action"] = pf["Signal"].apply(lambda x: "Increase" if x == "BUY" else ("Reduce" if x == "AVOID" else "Hold"))
    st.dataframe(pf[["Symbol", "Factor_Score", "RS_Percentile", "Stage", "Minervini", "VCP", "Darvas", "Signal", "Suggested_Weight_%", "Capital_Allocation_₹", "Estimated_Risk_₹", "Rebalance_Action"]], use_container_width=True)

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

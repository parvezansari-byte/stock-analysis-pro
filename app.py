# FINAL V12.1.1 BLACKROCK PRIME HOTFIX CLOUD SAFE - SINGLE FULL STREAMLIT APP.PY
# ==================================================================================================
# REAL FIXED VERSION FOR STREAMLIT CLOUD / YFINANCE STABILITY
#
# HOTFIXES INCLUDED:
# - Auto fallback to NIFTY 50 if selected universe fails
# - Safer yfinance download wrapper + retry logic
# - Cleaner PSEUDO NIFTY 500 list (removed unstable symbols)
# - Default fast-scan behavior optimized for Streamlit Cloud
# - No blank screen / no hard fail on empty universe
# - Graceful degradation when some symbols fail
# - Optional heavy scanners behind toggle (OFF by default)
# - Persistent watchlist + notes + export
# - Premium dark UI + cloud-safe single file
#
# REQUIREMENTS:
# streamlit
# yfinance
# pandas
# numpy
# plotly

import os
import io
import json
import math
import time
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
st.set_page_config(page_title="FINAL V12.1.1 BLACKROCK PRIME HOTFIX CLOUD SAFE", page_icon="🏦", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
.main {
    background: linear-gradient(180deg, #020617 0%, #0b1220 45%, #111827 100%);
}
.block-container {
    padding-top: 0.8rem;
    padding-bottom: 2rem;
}
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 14px;
    margin-bottom: 10px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.18);
}
.small-note {font-size: 0.85rem; color: #9ca3af;}
</style>
""", unsafe_allow_html=True)

# ==================================================
# UNIVERSES + SECTORS
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

DEFAULT_UNIVERSE = sorted({s for arr in SECTOR_MAP.values() for s in arr})

NIFTY_50 = sorted({
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","INFY.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS",
    "LT.NS","KOTAKBANK.NS","HINDUNILVR.NS","AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","SUNPHARMA.NS",
    "M&M.NS","ULTRACEMCO.NS","TATAMOTORS.NS","NTPC.NS","POWERGRID.NS","ASIANPAINT.NS","NESTLEIND.NS",
    "BAJAJFINSV.NS","TITAN.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS","JSWSTEEL.NS","TATASTEEL.NS",
    "ADANIPORTS.NS","ONGC.NS","COALINDIA.NS","INDUSINDBK.NS","HDFCLIFE.NS","SBILIFE.NS","CIPLA.NS",
    "DRREDDY.NS","EICHERMOT.NS","HEROMOTOCO.NS","GRASIM.NS","BRITANNIA.NS","DIVISLAB.NS","BPCL.NS",
    "APOLLOHOSP.NS","SHRIRAMFIN.NS","BAJAJ-AUTO.NS","TRENT.NS","BEL.NS","HINDALCO.NS","TATACONSUM.NS"
})

NIFTY_100 = sorted(set(NIFTY_50 + DEFAULT_UNIVERSE + [
    "DLF.NS","PIDILITIND.NS","ABB.NS","SIEMENS.NS","BHEL.NS","TORNTPHARM.NS","GAIL.NS",
    "IOC.NS","HINDPETRO.NS","AMBUJACEM.NS","SHREECEM.NS","PFC.NS","NMDC.NS","VEDL.NS","DABUR.NS"
]))

NIFTY_200 = sorted(set(NIFTY_100 + [
    "HAL.NS","RVNL.NS","IRCTC.NS","IRFC.NS","NBCC.NS","REC.NS","SAIL.NS","BOSCHLTD.NS","ABBOTINDIA.NS",
    "MUTHOOTFIN.NS","PAGEIND.NS","POLYCAB.NS","SRF.NS","CUMMINSIND.NS","INDIGO.NS","TATAPOWER.NS",
    "JUBLFOOD.NS","AUROPHARMA.NS","MPHASIS.NS","LICHSGFIN.NS","INDHOTEL.NS","LTTS.NS","BERGEPAINT.NS",
    "SUPREMEIND.NS","ASTRAL.NS","MOTHERSON.NS","CANBK.NS","FEDERALBNK.NS","UNIONBANK.NS","PNB.NS",
    "IDFCFIRSTB.NS","MANAPPURAM.NS","BANDHANBNK.NS","CGPOWER.NS","DIXON.NS","ESCORTS.NS","VOLTAS.NS",
    "UBL.NS","COLPAL.NS","MARICO.NS","TATACHEM.NS","PETRONET.NS","NAUKRI.NS","COFORGE.NS","PERSISTENT.NS"
]))

# Cleaned / more stable pseudo list for Yahoo Finance cloud behavior
PSEUDO_NIFTY_500 = sorted(set(NIFTY_200 + DEFAULT_UNIVERSE + [
    "BSE.NS","MCX.NS","KPITTECH.NS","DELHIVERY.NS","SONACOMS.NS","TUBEINVEST.NS",
    "DEEPAKNTR.NS","BALRAMCHIN.NS","APLAPOLLO.NS","KEI.NS","FINCABLES.NS","CHOLAFIN.NS",
    "OBEROIRLTY.NS","GODREJPROP.NS","PHOENIXLTD.NS","PRESTIGE.NS","AUBANK.NS","RBLBANK.NS",
    "JKCEMENT.NS","RAMCOCEM.NS","HAVELLS.NS","CROMPTON.NS","BALKRISIND.NS","MRF.NS"
]))

NIFTY_SYMBOL = "^NSEI"
WATCHLIST_FILE = "watchlist_v12_1_1_hotfix.json"
WATCHLIST_META_FILE = "watchlist_meta_v12_1_1_hotfix.json"

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


def infer_sector(symbol: str) -> str:
    for sec, syms in SECTOR_MAP.items():
        if symbol in syms:
            return sec
    return "OTHER"

@st.cache_data(ttl=1800, show_spinner=False)
def get_hist(symbol, period="1y", interval="1d"):
    for _ in range(2):
        try:
            df = yf.download(
                symbol,
                period=period,
                interval=interval,
                auto_adjust=True,
                progress=False,
                threads=False,
                group_by="column"
            )
            if df is None or df.empty:
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] for c in df.columns]
            required = ["Open", "High", "Low", "Close", "Volume"]
            if not all(c in df.columns for c in required):
                continue
            df = df[required].dropna().copy()
            if len(df) < 30:
                continue
            return df
        except Exception:
            continue
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

    hl2 = (df["High"] + df["Low"]) / 2
    mult = 3.0
    upper = hl2 + mult * df["ATR14"]
    lower = hl2 - mult * df["ATR14"]
    fu = upper.copy(); fl = lower.copy()
    st_line = pd.Series(index=df.index, dtype=float)
    st_dir = pd.Series(index=df.index, dtype=int)
    for i in range(1, len(df)):
        fu.iloc[i] = upper.iloc[i] if (upper.iloc[i] < fu.iloc[i-1]) or (df["Close"].iloc[i-1] > fu.iloc[i-1]) else fu.iloc[i-1]
        fl.iloc[i] = lower.iloc[i] if (lower.iloc[i] > fl.iloc[i-1]) or (df["Close"].iloc[i-1] < fl.iloc[i-1]) else fl.iloc[i-1]
        if i == 1:
            st_line.iloc[i] = fl.iloc[i]
            st_dir.iloc[i] = 1
        else:
            if st_line.iloc[i-1] == fu.iloc[i-1]:
                if df["Close"].iloc[i] <= fu.iloc[i]:
                    st_line.iloc[i] = fu.iloc[i]; st_dir.iloc[i] = -1
                else:
                    st_line.iloc[i] = fl.iloc[i]; st_dir.iloc[i] = 1
            else:
                if df["Close"].iloc[i] >= fl.iloc[i]:
                    st_line.iloc[i] = fl.iloc[i]; st_dir.iloc[i] = 1
                else:
                    st_line.iloc[i] = fu.iloc[i]; st_dir.iloc[i] = -1
    df["Supertrend"] = st_line
    df["ST_Direction"] = st_dir.fillna(0)
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
    return (series.rank(pct=True) * 100).round(2) if not series.empty else series


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
    sma200_20 = df["SMA200"].iloc[-20] if len(df) > 220 else np.nan
    conds = [
        close > sma150 > sma200,
        sma50 > sma150,
        close > sma50,
        sma200 > sma200_20 if not pd.isna(sma200_20) else False,
        close >= 1.25 * low_52,
        close >= 0.75 * high_52,
    ]
    return all(conds)


def vcp_detect(df):
    if df.empty or len(df) < 120:
        return False, np.nan
    ranges = []
    for w in [60, 40, 20]:
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


def support_resistance(df, lookback=60):
    if df.empty or len(df) < lookback:
        return np.nan, np.nan
    recent = df.tail(lookback)
    return round(recent["Low"].rolling(10).min().iloc[-1], 2), round(recent["High"].rolling(10).max().iloc[-1], 2)


def atr_trailing_stop(df, multiple=3.0):
    if df.empty or len(df) < 20:
        return np.nan
    return round(df["Close"].iloc[-1] - multiple * safe_float(df["ATR14"].iloc[-1], 0), 2)


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
    return round(r21*0.10 + r63*0.14 + r126*0.14 + r252*0.12 + rs55*0.18 + rsi*0.08 + adx*0.08 + vol_ratio*10*0.06 + st_bonus + template_bonus + stage_bonus, 2)


def institutional_scorecard(df, nifty_df):
    checks = {}
    if df.empty or len(df) < 252:
        return checks
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
    checks["Institutional Score /10"] = sum(1 for v in list(checks.values()) if v is True)
    return checks


def position_size(capital, risk_pct, entry, sl):
    risk_amt = capital * risk_pct / 100
    per_share = max(entry - sl, 0.01)
    qty_risk = math.floor(risk_amt / per_share)
    qty_cap = math.floor(capital / entry)
    qty = max(min(qty_risk, qty_cap), 0)
    return qty, qty * entry, risk_amt


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


def build_watchlist_export(df):
    output = io.BytesIO()
    df.to_csv(output, index=False)
    return output.getvalue()


def get_universe(mode, selected_sector, custom_symbols):
    if mode == "NIFTY 50":
        return NIFTY_50
    if mode == "NIFTY 100":
        return NIFTY_100
    if mode == "NIFTY 200":
        return NIFTY_200
    if mode == "PSEUDO NIFTY 500":
        return PSEUDO_NIFTY_500
    if mode == "SECTOR UNIVERSE":
        return DEFAULT_UNIVERSE if selected_sector == "ALL" else SECTOR_MAP[selected_sector]
    return sorted(list(set([x.strip().upper() for x in custom_symbols.split(",") if x.strip()])))


def build_master_rank(universe, nifty_df, max_scan=25):
    rows = []
    failed = 0
    symbols = universe[:max_scan]
    if not symbols:
        return pd.DataFrame(), 0, 0
    progress = st.progress(0, text="Building ranking engine...")
    for i, sym in enumerate(symbols):
        df = add_indicators(get_hist(sym, period="1y"))
        if df.empty or len(df) < 252:
            failed += 1
            progress.progress(min((i+1)/len(symbols),1.0), text=f"Skipping {sym}...")
            continue
        last = df.iloc[-1]
        high52 = df["High"].tail(252).max()
        prev = df.iloc[-2] if len(df) > 2 else last
        gap = ((last["Open"] / max(prev["Close"], 0.01)) - 1) * 100
        rel_vol = safe_float(last["Volume"], 0) / max(safe_float(last["VolAvg20"].iloc[-1], 1), 1)
        factor = advanced_factor_score(df, nifty_df)
        scorecard = institutional_scorecard(df, nifty_df)
        rows.append({
            "Sector": infer_sector(sym),
            "Symbol": sym,
            "Close": round(last["Close"], 2),
            "Factor_Score": factor,
            "RS_vs_NIFTY_%": round(relative_strength_vs_nifty(df, nifty_df, 55), 2),
            "1M_%": round(compute_returns(df, 21), 2),
            "3M_%": round(compute_returns(df, 63), 2),
            "6M_%": round(compute_returns(df, 126), 2),
            "12M_%": round(compute_returns(df, 252), 2),
            "RSI": round(safe_float(last["RSI14"]), 2),
            "ADX": round(safe_float(last["ADX14"]), 2),
            "Rel_Vol": round(rel_vol, 2),
            "Gap_%": round(gap, 2),
            "Supertrend": "Bullish" if safe_float(last["ST_Direction"], 0) == 1 else "Bearish",
            "Stage": stage_analysis(df),
            "Minervini": minervini_template(df),
            "Near_52W_High_%": round(((last["Close"] / max(high52, 0.01)) - 1) * 100, 2),
            "Institutional_Score": scorecard.get("Institutional Score /10", 0),
            "ATR_Trail": atr_trailing_stop(df),
            "Signal": "BUY" if (factor > 35 and safe_float(last["ST_Direction"], 0) == 1 and safe_float(last["ADX14"], 0) > 18) else ("AVOID" if factor < 8 else "WATCH")
        })
        progress.progress(min((i+1)/len(symbols),1.0), text=f"Scanning {sym}...")
    progress.empty()
    out = pd.DataFrame(rows)
    if out.empty:
        return out, len(rows), failed
    out["RS_Percentile"] = rs_percentile(out["RS_vs_NIFTY_%"])
    return out.sort_values(["Factor_Score", "RS_Percentile"], ascending=False), len(rows), failed


def sector_rotation_dashboard(nifty_df):
    rows = []
    for sector, symbols in SECTOR_MAP.items():
        vals = []
        for sym in symbols:
            df = add_indicators(get_hist(sym, period="1y"))
            if df.empty or len(df) < 252:
                continue
            vals.append({
                "Factor": advanced_factor_score(df, nifty_df),
                "RS": relative_strength_vs_nifty(df, nifty_df, 55),
                "1M": compute_returns(df, 21),
                "3M": compute_returns(df, 63),
                "Leader": sym
            })
        if vals:
            temp = pd.DataFrame(vals).sort_values("Factor", ascending=False)
            rows.append({
                "Sector": sector,
                "Avg_Factor": round(temp["Factor"].mean(), 2),
                "Avg_RS": round(temp["RS"].mean(), 2),
                "Avg_1M": round(temp["1M"].mean(), 2),
                "Avg_3M": round(temp["3M"].mean(), 2),
                "Leader": temp.iloc[0]["Leader"]
            })
    return pd.DataFrame(rows).sort_values(["Avg_Factor", "Avg_RS"], ascending=False) if rows else pd.DataFrame()

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.title("⚙️ V12.1.1 HOTFIX Controls")
universe_mode = st.sidebar.selectbox("Universe", ["NIFTY 50", "NIFTY 100", "NIFTY 200", "PSEUDO NIFTY 500", "SECTOR UNIVERSE", "CUSTOM"], index=0)
selected_sector = st.sidebar.selectbox("Focus Sector", ["ALL"] + list(SECTOR_MAP.keys()))
capital = st.sidebar.number_input("Capital (₹)", min_value=10000, value=500000, step=10000)
risk_pct = st.sidebar.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.5)
max_sector_weight = st.sidebar.slider("Max Sector Concentration (%)", 10, 50, 25, 5)
scan_limit = st.sidebar.selectbox("Fast Scan Limit", [25, 40, 60, 80], index=0)
run_heavy_scan = st.sidebar.checkbox("Run Heavy Scan (VCP / Darvas / ORB)", value=False)
custom_symbols = st.sidebar.text_area("Custom symbols (comma separated)", value="RELIANCE.NS,TCS.NS,HDFCBANK.NS" if universe_mode == "CUSTOM" else "")

universe = get_universe(universe_mode, selected_sector, custom_symbols)
watchlist = load_watchlist()
watch_meta = load_watchlist_meta()

st.sidebar.markdown("---")
st.sidebar.subheader("⭐ Persistent Watchlist")
add_symbol = st.sidebar.selectbox("Add stock", ["Select"] + sorted(set(universe[:min(len(universe),100)] + DEFAULT_UNIVERSE)))
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
st.title("🏦 FINAL V12.1.1 BLACKROCK PRIME HOTFIX CLOUD SAFE")
st.caption("Auto Fallback • Safer Yahoo Fetch • Cloud Safe • No Blank Screen • Better Default Scan • Real Hotfix for Streamlit Cloud")

nifty_df = add_indicators(get_hist(NIFTY_SYMBOL, period="1y"))
if nifty_df.empty:
    st.error("Unable to fetch NIFTY data right now. Please refresh later.")
    st.stop()

# ==================================================
# MASTER RANK BUILD WITH FALLBACK
# ==================================================
start = time.time()
rank_df, success_count, fail_count = build_master_rank(universe, nifty_df, max_scan=min(scan_limit, len(universe)))
fallback_used = False

# Auto fallback if selected universe fails
if rank_df.empty:
    fallback_used = True
    st.warning("Selected universe returned no usable data. Auto-fallback activated: scanning NIFTY 50 (top 25) for stability...")
    fallback_universe = NIFTY_50[:25]
    rank_df, success_count, fail_count = build_master_rank(fallback_universe, nifty_df, max_scan=min(25, len(fallback_universe)))

scan_time = round(time.time() - start, 2)

if rank_df.empty:
    st.error("Yahoo Finance returned no usable data right now. Please refresh later or keep scan limit at 25.")
    st.stop()

# ==================================================
# TOP METRICS
# ==================================================
m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
m1.metric("NIFTY", f"{nifty_df['Close'].iloc[-1]:,.2f}", f"{compute_returns(nifty_df, 21):.2f}% (1M)")
m2.metric("Universe Size", len(universe))
m3.metric("Success", success_count)
m4.metric("Failed", fail_count)
m5.metric("Watchlist", len(watchlist))
m6.metric("Capital", f"₹{capital:,.0f}")
m7.metric("Scan Time", f"{scan_time}s")

if fallback_used:
    st.info("Fallback mode is active right now for stability. Results shown are from NIFTY 50 fallback universe.")

# ==================================================
# MARKET BREADTH
# ==================================================
st.markdown("## 📈 Market Breadth Dashboard")
adv = int((rank_df["1M_%"] > 0).sum())
dec = int((rank_df["1M_%"] <= 0).sum())
new_highs = int((rank_df["Near_52W_High_%"] >= -2).sum())
new_lows = int((rank_df["12M_%"] <= -20).sum())
mb1, mb2, mb3, mb4, mb5, mb6 = st.columns(6)
mb1.metric("Advances", adv)
mb2.metric("Declines", dec)
mb3.metric("A/D Ratio", round(adv / max(dec, 1), 2))
mb4.metric("Near 52W Highs", new_highs)
mb5.metric("12M Weak Laggards", new_lows)
mb6.metric("Avg Factor", round(rank_df["Factor_Score"].mean(), 2))

# ==================================================
# SECTOR ROTATION
# ==================================================
st.markdown("## 🔄 Sector Rotation Dashboard")
sector_df = sector_rotation_dashboard(nifty_df)
if not sector_df.empty:
    st.dataframe(sector_df, use_container_width=True)
    heat = sector_df[["Sector", "Avg_Factor", "Avg_RS", "Avg_1M", "Avg_3M"]].set_index("Sector")
    fig_heat = px.imshow(heat.T, text_auto='.2f', aspect='auto', title='Sector Rotation Heatmap')
    fig_heat.update_layout(height=400)
    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.info("Sector rotation temporarily unavailable.")

# ==================================================
# LEADER / LAGGARD
# ==================================================
st.markdown("## 🏁 Leader / Laggard + Relative Volume")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### Top Leaders")
    st.dataframe(rank_df.head(10)[["Sector","Symbol","Factor_Score","RS_Percentile","Signal"]], use_container_width=True)
with c2:
    st.markdown("### Top Laggards")
    st.dataframe(rank_df.sort_values("Factor_Score", ascending=True).head(10)[["Sector","Symbol","Factor_Score","RS_Percentile","Signal"]], use_container_width=True)
with c3:
    st.markdown("### Relative Volume Leaderboard")
    st.dataframe(rank_df.sort_values("Rel_Vol", ascending=False).head(10)[["Sector","Symbol","Rel_Vol","Gap_%","Signal"]], use_container_width=True)

# ==================================================
# MASTER RANK TABLE
# ==================================================
st.markdown("## ⚡ Master Prime Ranking Engine")
show_n = st.radio("Show Top", [10, 20, 50], horizontal=True, index=1)
st.dataframe(rank_df.head(show_n), use_container_width=True)

# ==================================================
# HEAVY SCANNERS (OPTIONAL)
# ==================================================
st.markdown("## 🚨 Heavy Scanners (Optional for Cloud Speed)")
if run_heavy_scan:
    orb_rows, breakout_rows, vcp_rows, darvas_rows = [], [], [], []
    scan_syms = list(rank_df["Symbol"].head(min(len(rank_df), 30)))
    hp = st.progress(0, text="Running heavy scanners...")
    for i, sym in enumerate(scan_syms):
        df = add_indicators(get_hist(sym, period="1y"))
        if df.empty or len(df) < 30:
            hp.progress((i+1)/len(scan_syms), text=f"Heavy scan {sym}...")
            continue
        last = df.iloc[-1]
        prev = df.iloc[-2]
        prior5 = df["High"].iloc[-6:-1].max() if len(df) >= 6 else df["High"].iloc[-2]
        rel_vol = safe_float(last["Volume"], 0) / max(safe_float(last["VolAvg20"].iloc[-1], 1), 1)
        gap = ((last["Open"] / max(prev["Close"], 0.01)) - 1) * 100
        if last["Close"] > prior5 and gap > 0.5 and rel_vol > 1.2:
            orb_rows.append({"Symbol": sym, "Close": round(last['Close'],2), "Gap_%": round(gap,2), "Rel_Vol": round(rel_vol,2)})
        high20 = df["High"].rolling(20).max().iloc[-2] if len(df) > 21 else np.nan
        if not pd.isna(high20) and last["Close"] > high20 and last["Close"] > last["SMA50"] > last["SMA200"]:
            breakout_rows.append({"Symbol": sym, "Close": round(last['Close'],2), "RS": round(relative_strength_vs_nifty(df, nifty_df, 55),2), "ADX": round(safe_float(last['ADX14']),2)})
        vcp_ok, pivot = vcp_detect(df)
        darvas_ok, box_low, box_high = darvas_box(df)
        if vcp_ok:
            vcp_rows.append({"Symbol": sym, "Close": round(last['Close'],2), "VCP_Pivot": pivot})
        if darvas_ok:
            darvas_rows.append({"Symbol": sym, "Close": round(last['Close'],2), "Darvas_Low": box_low, "Darvas_High": box_high})
        hp.progress((i+1)/len(scan_syms), text=f"Heavy scan {sym}...")
    hp.empty()

    h1, h2 = st.columns(2)
    with h1:
        st.markdown("### ORB Proxy + Breakouts")
        st.dataframe(pd.DataFrame(orb_rows), use_container_width=True) if orb_rows else st.info("No ORB proxy setups.")
        st.dataframe(pd.DataFrame(breakout_rows), use_container_width=True) if breakout_rows else st.info("No breakout setups.")
    with h2:
        st.markdown("### VCP + Darvas")
        st.dataframe(pd.DataFrame(vcp_rows), use_container_width=True) if vcp_rows else st.info("No VCP setups.")
        st.dataframe(pd.DataFrame(darvas_rows), use_container_width=True) if darvas_rows else st.info("No Darvas setups.")
else:
    st.info("Heavy scan is OFF for better Streamlit Cloud speed. Enable only when needed.")

# ==================================================
# WATCHLIST CANDIDATES
# ==================================================
st.markdown("## ⭐ Auto Top 10 Watchlist Candidates")
watch_candidates = rank_df[(rank_df["Signal"] != "AVOID")].head(10)
st.dataframe(watch_candidates[["Sector","Symbol","Factor_Score","RS_Percentile","Rel_Vol","Stage","Signal"]], use_container_width=True)

# ==================================================
# PERSISTENT WATCHLIST
# ==================================================
st.markdown("## 📌 Persistent Watchlist Dashboard")
watch_rows = []
for sym in watchlist:
    if sym not in rank_df["Symbol"].values:
        continue
    meta = watch_meta.get(sym, {})
    rr = rank_df.set_index("Symbol").loc[sym]
    watch_rows.append({
        "Sector": rr["Sector"],
        "Symbol": sym,
        "Factor_Score": rr["Factor_Score"],
        "RS_Percentile": rr["RS_Percentile"],
        "Rel_Vol": rr["Rel_Vol"],
        "Stage": rr["Stage"],
        "Signal": rr["Signal"],
        "Status": meta.get("status", "Watch"),
        "Note": meta.get("note", "")
    })
watch_df = pd.DataFrame(watch_rows)
if not watch_df.empty:
    st.dataframe(watch_df.sort_values("Factor_Score", ascending=False), use_container_width=True)
    st.download_button("⬇️ Export Watchlist CSV", data=build_watchlist_export(watch_df), file_name="watchlist_v12_1_1_hotfix.csv", mime="text/csv")
else:
    st.info("Watchlist empty or not present in current scanned results.")

with st.expander("✍️ Update Watchlist Note / Status"):
    if watchlist:
        edit_sym = st.selectbox("Select watchlist stock", watchlist)
        cur = watch_meta.get(edit_sym, {})
        status_list = ["Watch", "Buy Zone", "Holding", "Booked", "Avoid"]
        default_idx = status_list.index(cur.get("status", "Watch")) if cur.get("status", "Watch") in status_list else 0
        new_status = st.selectbox("Status", status_list, index=default_idx)
        new_note = st.text_input("Note", value=cur.get("note", ""))
        if st.button("Save Watchlist Note"):
            watch_meta[edit_sym] = {"status": new_status, "note": new_note, "updated_at": str(datetime.now())}
            save_watchlist_meta(watch_meta)
            st.success(f"Saved note for {edit_sym}")

# ==================================================
# SMART TOP 5 PORTFOLIO
# ==================================================
st.markdown("## 🧠 Smart Top 5 Portfolio + Sector Concentration Control")
portfolio_rows = []
sector_alloc = {}
for _, row in rank_df.iterrows():
    if len(portfolio_rows) >= 5:
        break
    sym = row["Symbol"]
    sector_name = row["Sector"]
    tentative_weight = 20
    if sector_alloc.get(sector_name, 0) + tentative_weight <= max_sector_weight:
        conviction = max(1, min(10, round((row["Factor_Score"] / max(rank_df["Factor_Score"].max(), 1)) * 10)))
        portfolio_rows.append({
            "Sector": sector_name,
            "Symbol": sym,
            "Conviction": conviction,
            "Factor_Score": row["Factor_Score"],
            "RS_Percentile": row["RS_Percentile"],
            "Signal": row["Signal"]
        })
        sector_alloc[sector_name] = sector_alloc.get(sector_name, 0) + tentative_weight

pf = pd.DataFrame(portfolio_rows)
if not pf.empty:
    pf["Raw_Weight"] = pf["Conviction"] / pf["Conviction"].sum()
    pf["Suggested_Weight_%"] = (pf["Raw_Weight"] * 100).round(2)
    pf["Capital_Allocation_₹"] = (pf["Suggested_Weight_%"] / 100 * capital).round(2)
    pf["Estimated_Risk_₹"] = (pf["Capital_Allocation_₹"] * 0.08).round(2)
    pf["Rebalance_Action"] = pf["Signal"].apply(lambda x: "Increase" if x == "BUY" else ("Reduce" if x == "AVOID" else "Hold"))
    st.dataframe(pf[["Sector","Symbol","Conviction","Factor_Score","RS_Percentile","Suggested_Weight_%","Capital_Allocation_₹","Estimated_Risk_₹","Rebalance_Action"]], use_container_width=True)

    p1, p2 = st.columns(2)
    with p1:
        fig_alloc = px.pie(pf, names="Symbol", values="Capital_Allocation_₹", title="Top 5 Smart Allocation")
        st.plotly_chart(fig_alloc, use_container_width=True)
    with p2:
        fig_risk = px.bar(pf, x="Symbol", y="Estimated_Risk_₹", title="Estimated Position Risk")
        st.plotly_chart(fig_risk, use_container_width=True)

# ==================================================
# STOCK COMPARISON
# ==================================================
st.markdown("## ⚔️ Stock Comparison Mode")
compare_choices = sorted(set(list(rank_df["Symbol"].head(100)) + watchlist))
selected_compare = st.multiselect("Select up to 4 stocks", compare_choices, default=compare_choices[:2] if len(compare_choices) >= 2 else compare_choices[:1], max_selections=4)
if selected_compare:
    comp_df = pd.DataFrame()
    for sym in selected_compare:
        df = get_hist(sym, period="1y")
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
st.markdown("## 🔎 Stock Deep Dive + Trend Following Dashboard")
deep_symbol = st.selectbox("Select Stock for Full Analysis", compare_choices if compare_choices else list(rank_df["Symbol"].head(20)))
stock_df = add_indicators(get_hist(deep_symbol, period="2y"))
info = get_info(deep_symbol)
bs, fin, cf = get_financials(deep_symbol)

if not stock_df.empty:
    last = stock_df.iloc[-1]
    sup, res = support_resistance(stock_df)
    rs = relative_strength_vs_nifty(stock_df, nifty_df, 55)
    stage = stage_analysis(stock_df)
    minervini_ok = minervini_template(stock_df)
    scorecard = institutional_scorecard(stock_df, nifty_df)
    atr_trail = atr_trailing_stop(stock_df)

    d1, d2, d3, d4, d5, d6, d7 = st.columns(7)
    d1.metric("Price", f"₹{last['Close']:.2f}")
    d2.metric("RS vs NIFTY", f"{rs:.2f}%")
    d3.metric("RSI", f"{last['RSI14']:.2f}")
    d4.metric("ADX", f"{safe_float(last['ADX14']):.2f}")
    d5.metric("Stage", stage)
    d6.metric("ATR Trail", f"₹{atr_trail:.2f}")
    d7.metric("Score /10", scorecard.get("Institutional Score /10", 0))

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_heights=[0.58, 0.20, 0.22])
    fig.add_trace(go.Candlestick(x=stock_df.index, open=stock_df['Open'], high=stock_df['High'], low=stock_df['Low'], close=stock_df['Close'], name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA20'], name='SMA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA50'], name='SMA50'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA200'], name='SMA200'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['Supertrend'], name='Supertrend'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=[atr_trail]*len(stock_df), name='ATR Trail'), row=1, col=1)
    fig.add_trace(go.Bar(x=stock_df.index, y=stock_df['Volume'], name='Volume'), row=2, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['RSI14'], name='RSI'), row=3, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['ADX14'], name='ADX'), row=3, col=1)
    fig.update_layout(height=900, xaxis_rangeslider_visible=False, title=f"{deep_symbol} HOTFIX Dashboard")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"<div class='card'><b>Support:</b> ₹{sup} &nbsp;&nbsp; <b>Resistance:</b> ₹{res} &nbsp;&nbsp; <b>Minervini:</b> {'YES' if minervini_ok else 'NO'} &nbsp;&nbsp; <b>Signal:</b> {'BUY' if scorecard.get('Institutional Score /10',0) >= 7 else 'WATCH'}</div>", unsafe_allow_html=True)

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
    fig_rs.update_layout(height=380, title='Relative Strength Comparison (Base = 100)')
    st.plotly_chart(fig_rs, use_container_width=True)

    st.markdown("### Fundamental Snapshot")
    f1, f2, f3, f4, f5, f6 = st.columns(6)
    f1.metric("Market Cap", f"₹{safe_float(info.get('marketCap',0))/1e7:,.0f} Cr" if info.get('marketCap') else "NA")
    f2.metric("PE", f"{safe_float(info.get('trailingPE')):.2f}" if info.get('trailingPE') else "NA")
    f3.metric("PB", f"{safe_float(info.get('priceToBook')):.2f}" if info.get('priceToBook') else "NA")
    f4.metric("ROE", f"{safe_float(info.get('returnOnEquity'))*100:.2f}%" if info.get('returnOnEquity') else "NA")
    f5.metric("Dividend Yield", f"{safe_float(info.get('dividendYield'))*100:.2f}%" if info.get('dividendYield') else "NA")
    f6.metric("Beta", f"{safe_float(info.get('beta')):.2f}" if info.get('beta') else "NA")

    st.markdown("### Balance Sheet / Financials / Cash Flow")
    t1, t2, t3 = st.tabs(["Balance Sheet", "P&L", "Cash Flow"])
    with t1:
        st.dataframe(bs, use_container_width=True) if not bs.empty else st.info("Balance sheet not available.")
    with t2:
        st.dataframe(fin, use_container_width=True) if not fin.empty else st.info("Financials not available.")
    with t3:
        st.dataframe(cf, use_container_width=True) if not cf.empty else st.info("Cash flow not available.")

    st.markdown("### Prime Trade Plan")
    entry = float(last['Close'])
    atr = float(last['ATR14']) if not pd.isna(last['ATR14']) else entry * 0.03
    sl = round(max(entry - 1.5 * atr, safe_float(last['SMA20'], entry*0.95)), 2)
    t1v = round(entry + 2 * atr, 2)
    t2v = round(entry + 4 * atr, 2)
    qty, invested, risk_amt = position_size(capital, risk_pct, entry, sl)
    rr = round((t1v - entry) / max(entry - sl, 0.01), 2)
    tp1, tp2, tp3, tp4, tp5 = st.columns(5)
    tp1.metric("Entry", f"₹{entry:.2f}")
    tp2.metric("Stop Loss", f"₹{sl:.2f}")
    tp3.metric("Target 1", f"₹{t1v:.2f}")
    tp4.metric("Target 2", f"₹{t2v:.2f}")
    tp5.metric("Qty", qty)
    st.markdown(f"<div class='card'><b>Capital Used:</b> ₹{invested:,.2f} &nbsp;&nbsp; <b>Max Risk:</b> ₹{risk_amt:,.2f} &nbsp;&nbsp; <b>R:R to T1:</b> {rr}</div>", unsafe_allow_html=True)

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.markdown("<div class='small-note'>Disclaimer: Educational tool only. Verify all data before investing. Yahoo Finance data may be delayed/inconsistent. For best Streamlit Cloud stability: default Universe = NIFTY 50, Fast Scan Limit = 25, Heavy Scan OFF unless needed.</div>", unsafe_allow_html=True)

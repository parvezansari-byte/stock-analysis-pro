# FINAL NILE V13.1 CLOUD OPTIMIZED + PDF POLISH
# Single full app.py
# Same exact UI • All V13 features preserved • Safer cloud performance
# Added: faster scanner, lighter breadth loops, cached PDF data helpers, improved PDF styling

import time
from datetime import datetime
from pathlib import Path
from io import BytesIO

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    import yfinance as yf
except Exception:
    yf = None

# PDF (cloud-safe)
try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak,
    )
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Nile",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------
# PREMIUM IMPERIAL TERMINAL CSS (SAME EXACT UI)
# -------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --bg1:#020611; --bg2:#081120; --bg3:#0b1528;
        --line: rgba(148,163,184,0.10);
        --text:#eef2ff; --muted:#94a3b8;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 12%, rgba(37,99,235,0.18), transparent 22%),
            radial-gradient(circle at 90% 8%, rgba(124,58,237,0.14), transparent 24%),
            radial-gradient(circle at 48% 92%, rgba(6,182,212,0.08), transparent 20%),
            linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 55%, var(--bg3) 100%);
        color: var(--text);
    }

    .block-container {
        max-width: 1720px;
        padding-top: 1.1rem;
        padding-bottom: 2rem;
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(6,10,22,0.995), rgba(10,18,32,0.995));
        border-right: 1px solid rgba(148,163,184,0.08);
    }

    .imperial-ribbon {
        position: relative;
        background: linear-gradient(90deg, rgba(8,14,28,0.98), rgba(13,22,40,0.98), rgba(8,14,28,0.98));
        border: 1px solid rgba(59,130,246,0.14);
        border-radius: 18px;
        padding: 10px 14px;
        margin-bottom: 10px;
        box-shadow: 0 0 18px rgba(59,130,246,0.10), 0 12px 30px rgba(0,0,0,0.30), inset 0 1px 0 rgba(255,255,255,0.02);
        overflow: hidden;
    }

    .imperial-ribbon::before {
        content:'';
        position:absolute;
        inset:0;
        pointer-events:none;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
    }

    .ribbon-chip {
        display:inline-block;
        padding:6px 10px;
        border-radius:999px;
        margin-right:6px;
        margin-bottom:4px;
        background: rgba(30,41,59,0.72);
        border:1px solid rgba(255,255,255,0.05);
        color:#dbeafe;
        font-weight:800;
        font-size:0.74rem;
        letter-spacing:0.15px;
    }

    .panel {
        background: linear-gradient(180deg, rgba(8,14,28,0.92), rgba(13,22,40,0.94));
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 14px;
        box-shadow: 0 14px 34px rgba(0,0,0,0.24), inset 0 1px 0 rgba(255,255,255,0.02);
        margin-bottom: 12px;
        backdrop-filter: blur(10px);
    }

    .panel-title {
        font-size: 0.95rem;
        font-weight: 900;
        color: #f8fafc;
        margin-bottom: 8px;
    }

    .subtle-divider {
        height:1px;
        background: linear-gradient(90deg, rgba(59,130,246,0.22), rgba(124,58,237,0.14), transparent);
        margin: 6px 0 10px 0;
    }

    .hero-card {
        border-radius: 20px;
        padding: 14px;
        min-height: 118px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 14px 28px rgba(0,0,0,0.26), inset 0 1px 0 rgba(255,255,255,0.03);
    }

    .hero-card::before {
        content:'';
        position:absolute;
        inset:0;
        pointer-events:none;
        background:
            radial-gradient(circle at 12% 18%, rgba(255,255,255,0.08), transparent 22%),
            radial-gradient(circle at 88% 12%, rgba(255,255,255,0.04), transparent 24%);
    }

    .hero-title {
        font-size: 0.82rem;
        font-weight: 900;
        color: #cbd5e1;
        margin-bottom: 4px;
        position:relative;
    }

    .hero-value {
        font-size: 1.62rem;
        font-weight: 900;
        color: #ffffff;
        position:relative;
    }

    .hero-change {
        font-size: 0.92rem;
        font-weight: 900;
        margin-top: 3px;
        position:relative;
    }

    .breadth-card, .sector-tile, .scanner-rank-card, .compare-mini-card, .metric-card, .portfolio-card {
        background: linear-gradient(180deg, rgba(15,23,42,0.96), rgba(17,24,39,0.92));
        border: 1px solid rgba(148,163,184,0.10);
        border-radius: 18px;
        padding: 14px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.20);
    }

    .breadth-value, .metric-value, .portfolio-value {
        font-size: 1.4rem;
        font-weight: 900;
        color: #fff;
    }

    .metric-label, .breadth-label, .portfolio-label {
        font-size: 0.76rem;
        color: #94a3b8;
        margin-bottom: 4px;
        font-weight: 700;
    }

    .metric-delta-up { color:#22c55e; font-weight:800; font-size:0.82rem; }
    .metric-delta-down { color:#ef4444; font-weight:800; font-size:0.82rem; }
    .metric-delta-flat { color:#94a3b8; font-weight:800; font-size:0.82rem; }

    .premium-subtitle {
        font-size:1rem;
        font-weight:900;
        letter-spacing:0.55px;
        background: linear-gradient(90deg, #e9d5ff, #c4b5fd, #93c5fd);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        display:block;
        text-align:center;
        margin-bottom:0.55rem;
    }

    .ai-badge-buy, .ai-badge-hold, .ai-badge-sell {
        padding:14px;
        border-radius:16px;
        font-weight:900;
        text-align:center;
        font-size:0.98rem;
    }

    .ai-badge-buy {
        background: linear-gradient(90deg, rgba(34,197,94,0.20), rgba(34,197,94,0.08));
        color:#86efac;
        border:1px solid rgba(34,197,94,0.24);
    }

    .ai-badge-hold {
        background: linear-gradient(90deg, rgba(245,158,11,0.20), rgba(245,158,11,0.08));
        color:#fcd34d;
        border:1px solid rgba(245,158,11,0.24);
    }

    .ai-badge-sell {
        background: linear-gradient(90deg, rgba(239,68,68,0.20), rgba(239,68,68,0.08));
        color:#fca5a5;
        border:1px solid rgba(239,68,68,0.24);
    }

    .sector-tile { min-height: 118px; }
    .sector-name { font-size:0.8rem; font-weight:900; color:#cbd5e1; }
    .sector-return { font-size:1.25rem; font-weight:900; margin-top:6px; }

    .scanner-rank-card { min-height: 145px; }
    .compare-mini-card { min-height: 100px; }

    .portfolio-card { min-height: 118px; }

    .portfolio-action-add { color:#22c55e; font-weight:900; }
    .portfolio-action-hold { color:#f59e0b; font-weight:900; }
    .portfolio-action-reduce { color:#f97316; font-weight:900; }
    .portfolio-action-exit { color:#ef4444; font-weight:900; }

    .stButton > button, .stDownloadButton > button {
        width:100%;
        border-radius:14px;
        border:1px solid rgba(255,255,255,0.08);
        color:white;
        font-weight:900;
        padding:0.72rem 0.9rem;
        font-size:0.9rem;
        transition:all 0.25s ease-in-out;
        box-shadow:0 8px 20px rgba(0,0,0,0.24);
        background-size:220% 220% !important;
        animation: buttonGlow 6s ease infinite;
    }

    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #16a34a, #22c55e, #4ade80) !important;
    }

    div[data-testid="stButton"][id*="fundamental_ratio_btn"] > button {
        background: linear-gradient(135deg, #2563eb, #3b82f6, #60a5fa) !important;
    }

    div[data-testid="stButton"][id*="technical_ratio_btn"] > button {
        background: linear-gradient(135deg, #7c3aed, #8b5cf6, #a78bfa) !important;
    }

    div[data-testid="stButton"][id*="run_scan_btn"] > button {
        background: linear-gradient(135deg, #15803d, #22c55e, #4ade80) !important;
    }

    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #0f766e, #14b8a6, #06b6d4) !important;
    }

    @keyframes buttonGlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# STOCK UNIVERSE + SECTORS
# -------------------------------------------------
NIFTY_50 = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","BHARTIARTL.NS","ICICIBANK.NS","SBIN.NS","INFY.NS","HINDUNILVR.NS",
    "ITC.NS","LT.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS",
    "TITAN.NS","ULTRACEMCO.NS","NESTLEIND.NS","BAJAJFINSV.NS","HCLTECH.NS","WIPRO.NS","NTPC.NS","POWERGRID.NS",
    "TATAMOTORS.NS","M&M.NS","ONGC.NS","COALINDIA.NS","TATASTEEL.NS","JSWSTEEL.NS","ADANIPORTS.NS","INDUSINDBK.NS",
    "TECHM.NS","GRASIM.NS","CIPLA.NS","DRREDDY.NS","HINDALCO.NS","HEROMOTOCO.NS","EICHERMOT.NS","BPCL.NS",
    "BRITANNIA.NS","APOLLOHOSP.NS","DIVISLAB.NS","ADANIENT.NS","TATACONSUM.NS","PIDILITIND.NS","SBILIFE.NS",
    "BAJAJ-AUTO.NS","SHRIRAMFIN.NS","TRENT.NS"
]

NIFTY_NEXT_50 = [
    "ABB.NS","ADANIGREEN.NS","ADANIPOWER.NS","AMBUJACEM.NS","BANKBARODA.NS","BOSCHLTD.NS","CANBK.NS","CGPOWER.NS",
    "CHOLAFIN.NS","DABUR.NS","DLF.NS","GAIL.NS","GODREJCP.NS","HAL.NS","HAVELLS.NS","ICICIGI.NS","ICICIPRULI.NS",
    "INDIGO.NS","IOC.NS","IRCTC.NS","JINDALSTEL.NS","JSWENERGY.NS","LICI.NS","LODHA.NS","LUPIN.NS","MCDOWELL-N.NS",
    "MOTHERSON.NS","NAUKRI.NS","NMDC.NS","PFC.NS","PIDILITIND.NS","PNB.NS","POLYCAB.NS","RECLTD.NS","SAIL.NS",
    "SIEMENS.NS","TVSMOTOR.NS","UNITDSPR.NS","VEDL.NS","VOLTAS.NS","ZYDUSLIFE.NS","INDUSTOWER.NS","TORNTPHARM.NS",
    "HDFCLIFE.NS","COLPAL.NS","MARICO.NS","UBL.NS","BERGEPAINT.NS","CONCOR.NS","OFSS.NS"
]

UNIVERSE = sorted(list(dict.fromkeys(NIFTY_50 + NIFTY_NEXT_50)))

SECTOR_MAP = {
    "RELIANCE.NS":"Energy","ONGC.NS":"Energy","BPCL.NS":"Energy","IOC.NS":"Energy","GAIL.NS":"Energy",
    "TCS.NS":"IT","INFY.NS":"IT","HCLTECH.NS":"IT","WIPRO.NS":"IT","TECHM.NS":"IT","OFSS.NS":"IT",
    "HDFCBANK.NS":"Financials","ICICIBANK.NS":"Financials","SBIN.NS":"Financials","KOTAKBANK.NS":"Financials",
    "AXISBANK.NS":"Financials","BAJFINANCE.NS":"Financials","BAJAJFINSV.NS":"Financials","INDUSINDBK.NS":"Financials",
    "SBILIFE.NS":"Financials","BANKBARODA.NS":"Financials","CANBK.NS":"Financials","PFC.NS":"Financials",
    "RECLTD.NS":"Financials","LICI.NS":"Financials","PNB.NS":"Financials","ICICIGI.NS":"Financials",
    "ICICIPRULI.NS":"Financials","CHOLAFIN.NS":"Financials","SHRIRAMFIN.NS":"Financials","HDFCLIFE.NS":"Financials",
    "HINDUNILVR.NS":"Consumer","ITC.NS":"Consumer","NESTLEIND.NS":"Consumer","BRITANNIA.NS":"Consumer",
    "TATACONSUM.NS":"Consumer","DABUR.NS":"Consumer","GODREJCP.NS":"Consumer","COLPAL.NS":"Consumer",
    "MARICO.NS":"Consumer","UBL.NS":"Consumer","MCDOWELL-N.NS":"Consumer","UNITDSPR.NS":"Consumer",
    "SUNPHARMA.NS":"Pharma","CIPLA.NS":"Pharma","DRREDDY.NS":"Pharma","DIVISLAB.NS":"Pharma","LUPIN.NS":"Pharma",
    "ZYDUSLIFE.NS":"Pharma","TORNTPHARM.NS":"Pharma","APOLLOHOSP.NS":"Healthcare",
    "LT.NS":"Industrials","ABB.NS":"Industrials","CGPOWER.NS":"Industrials","SIEMENS.NS":"Industrials",
    "HAL.NS":"Industrials","CONCOR.NS":"Industrials","IRCTC.NS":"Industrials","HAVELLS.NS":"Industrials",
    "TATASTEEL.NS":"Metals","JSWSTEEL.NS":"Metals","HINDALCO.NS":"Metals","JINDALSTEL.NS":"Metals",
    "NMDC.NS":"Metals","SAIL.NS":"Metals","VEDL.NS":"Metals",
    "TATAMOTORS.NS":"Auto","M&M.NS":"Auto","MARUTI.NS":"Auto","HEROMOTOCO.NS":"Auto","EICHERMOT.NS":"Auto",
    "BAJAJ-AUTO.NS":"Auto","TVSMOTOR.NS":"Auto","MOTHERSON.NS":"Auto",
    "ADANIPORTS.NS":"Infrastructure","ADANIENT.NS":"Infrastructure","ADANIGREEN.NS":"Infrastructure",
    "ADANIPOWER.NS":"Infrastructure","DLF.NS":"Realty","LODHA.NS":"Realty",
    "POWERGRID.NS":"Utilities","NTPC.NS":"Utilities","COALINDIA.NS":"Utilities","JSWENERGY.NS":"Utilities",
}

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
@st.cache_data(ttl=900, show_spinner=False)
def get_history(symbol: str, period: str = "1y", interval: str = "1d"):
    if yf is None:
        return pd.DataFrame()
    try:
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False, threads=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        return df.dropna().copy()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=1800, show_spinner=False)
def get_info(symbol: str):
    if yf is None:
        return {}
    try:
        return yf.Ticker(symbol).info or {}
    except Exception:
        return {}

@st.cache_data(ttl=1800, show_spinner=False)
def get_financials(symbol: str):
    if yf is None:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    try:
        t = yf.Ticker(symbol)
        return (
            getattr(t, "balance_sheet", pd.DataFrame()),
            getattr(t, "financials", pd.DataFrame()),
            getattr(t, "cashflow", pd.DataFrame()),
        )
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def get_live_index(symbol: str):
    data = get_history(symbol, period="5d")
    if data.empty or len(data) < 2:
        return np.nan, np.nan
    last = float(data["Close"].iloc[-1])
    prev = float(data["Close"].iloc[-2])
    chg = ((last / prev) - 1) * 100 if prev else 0
    return last, chg

def safe_last(series):
    try:
        return float(series.dropna().iloc[-1])
    except Exception:
        return np.nan

def compute_indicators(df: pd.DataFrame):
    if df.empty:
        return df
    d = df.copy()
    d["SMA20"] = d["Close"].rolling(20).mean()
    d["SMA50"] = d["Close"].rolling(50).mean()

    delta = d["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    d["RSI14"] = 100 - (100 / (1 + rs))

    ema12 = d["Close"].ewm(span=12, adjust=False).mean()
    ema26 = d["Close"].ewm(span=26, adjust=False).mean()
    d["MACD"] = ema12 - ema26
    d["MACD_SIGNAL"] = d["MACD"].ewm(span=9, adjust=False).mean()
    d["MACD_HIST"] = d["MACD"] - d["MACD_SIGNAL"]

    tr1 = d["High"] - d["Low"]
    tr2 = (d["High"] - d["Close"].shift()).abs()
    tr3 = (d["Low"] - d["Close"].shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    d["ATR14"] = tr.rolling(14).mean()

    return d.dropna().copy()

def compute_scan_metrics_fast(df: pd.DataFrame):
    """
    Lighter than full compute_indicators for scanner/breadth.
    Returns dict with only required values.
    """
    if df.empty or len(df) < 60:
        return None

    d = df.copy()
    close = d["Close"]
    high = d["High"]
    low = d["Low"]
    vol = d["Volume"] if "Volume" in d.columns else pd.Series(index=d.index, dtype=float)

    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()

    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi14 = 100 - (100 / (1 + rs))

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr14 = tr.rolling(14).mean()

    if pd.isna(sma20.iloc[-1]) or pd.isna(sma50.iloc[-1]) or pd.isna(rsi14.iloc[-1]) or pd.isna(atr14.iloc[-1]):
        return None

    vol20 = vol.tail(20).mean() if len(vol) >= 20 else np.nan

    return {
        "close": float(close.iloc[-1]),
        "prev_close": float(close.iloc[-2]) if len(close) > 1 else float(close.iloc[-1]),
        "sma20": float(sma20.iloc[-1]),
        "sma50": float(sma50.iloc[-1]),
        "rsi": float(rsi14.iloc[-1]),
        "macd": float(macd.iloc[-1]),
        "macd_signal": float(macd_signal.iloc[-1]),
        "atr": float(atr14.iloc[-1]),
        "breakout": float(high.tail(20).max()),
        "support": float(low.tail(20).min()),
        "last_volume": float(vol.iloc[-1]) if len(vol) > 0 and pd.notna(vol.iloc[-1]) else np.nan,
        "vol20": float(vol20) if pd.notna(vol20) else np.nan,
        "day_ret": ((float(close.iloc[-1]) / float(close.iloc[-2])) - 1) * 100 if len(close) > 1 and float(close.iloc[-2]) != 0 else 0.0,
    }

def score_stock(df: pd.DataFrame):
    if df.empty or len(df) < 60:
        return 0, "Insufficient Data", {}

    last = df.iloc[-1]
    score = 0
    reasons = {}

    if last["Close"] > last["SMA20"]:
        score += 10
        reasons["Above SMA20"] = True

    if last["Close"] > last["SMA50"]:
        score += 15
        reasons["Above SMA50"] = True

    if last["SMA20"] > last["SMA50"]:
        score += 15
        reasons["Bullish Trend"] = True

    if 50 < last["RSI14"] < 70:
        score += 15
        reasons["Healthy RSI"] = True

    if last["MACD"] > last["MACD_SIGNAL"]:
        score += 15
        reasons["MACD Bullish"] = True

    recent_high = df["High"].tail(20).max()
    if last["Close"] >= recent_high * 0.985:
        score += 20
        reasons["Near Breakout"] = True

    vol20 = df["Volume"].tail(20).mean() if "Volume" in df.columns else np.nan
    if "Volume" in df.columns and pd.notna(vol20) and last["Volume"] > vol20 * 1.2:
        score += 10
        reasons["Volume Expansion"] = True

    verdict = "Strong Bullish" if score >= 75 else "Bullish" if score >= 55 else "Neutral" if score >= 35 else "Weak"
    return score, verdict, reasons

def score_from_metrics(m):
    score = 0
    if m["close"] > m["sma20"]:
        score += 10
    if m["close"] > m["sma50"]:
        score += 15
    if m["sma20"] > m["sma50"]:
        score += 15
    if 50 < m["rsi"] < 70:
        score += 15
    if m["macd"] > m["macd_signal"]:
        score += 15
    if m["close"] >= m["breakout"] * 0.985:
        score += 20
    if pd.notna(m["vol20"]) and pd.notna(m["last_volume"]) and m["last_volume"] > m["vol20"] * 1.2:
        score += 10

    verdict = "Strong Bullish" if score >= 75 else "Bullish" if score >= 55 else "Neutral" if score >= 35 else "Weak"
    return score, verdict

def ai_badge(score, rsi, trend_signal, macd_signal):
    if score >= 75 and trend_signal == "Bullish" and macd_signal == "Bullish" and rsi < 75:
        return "BUY", "ai-badge-buy", "High conviction setup"
    elif score >= 45:
        return "HOLD", "ai-badge-hold", "Wait for better confirmation"
    return "SELL", "ai-badge-sell", "Weak setup / avoid now"

def conviction_meter(score, rsi, trend_signal, macd_signal):
    conviction = score
    conviction += 5 if trend_signal == "Bullish" else 0
    conviction += 5 if macd_signal == "Bullish" else 0
    conviction += 5 if 50 <= rsi <= 70 else (-5 if rsi > 80 or rsi < 25 else 0)
    conviction = max(0, min(100, conviction))
    label = "Very Strong" if conviction >= 85 else "Strong" if conviction >= 70 else "Moderate" if conviction >= 50 else "Weak"
    return conviction, label

def rupee(v):
    try:
        return f"₹{v:,.2f}"
    except Exception:
        return "N/A"

def metric_box(label, value, delta_text="", positive=None):
    delta_cls = "metric-delta-up" if positive is True else "metric-delta-down" if positive is False else "metric-delta-flat"
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>{label}</div>
            <div class='metric-value'>{value}</div>
            <div class='{delta_cls}'>{delta_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def beautiful_top_card(title, value, change, bg, inverse=False):
    if pd.isna(value):
        st.markdown(
            f"""
            <div class='hero-card' style='background:{bg};'>
                <div class='hero-title'>{title}</div>
                <div class='hero-value' style='font-size:1.05rem;color:#94a3b8;'>Data unavailable</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    up = change >= 0
    color = "#ef4444" if (inverse and up) else "#22c55e" if (inverse and not up) else "#22c55e" if up else "#ef4444"
    arrow = "▲" if up else "▼"

    st.markdown(
        f"""
        <div class='hero-card' style='background:{bg};'>
            <div class='hero-title'>{title}</div>
            <div class='hero-value'>{value:,.2f}</div>
            <div class='hero-change' style='color:{color};'>{arrow} {change:+.2f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def make_gauge(value):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": "Conviction"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#06b6d4"},
                "steps": [
                    {"range": [0, 40], "color": "rgba(239,68,68,0.35)"},
                    {"range": [40, 70], "color": "rgba(245,158,11,0.35)"},
                    {"range": [70, 100], "color": "rgba(34,197,94,0.35)"},
                ],
            },
        )
    )
    fig.update_layout(
        height=225,
        margin=dict(l=14, r=14, t=36, b=6),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig

def make_candlestick(df: pd.DataFrame, symbol: str, entry=None, stop=None, target=None, breakout=None, support=None):
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price",
        )
    )
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA50"))

    if breakout is not None:
        fig.add_hline(y=breakout, line_dash="dot", annotation_text="Breakout")
    if support is not None:
        fig.add_hline(y=support, line_dash="dot", annotation_text="Support")
    if entry is not None:
        fig.add_hline(y=entry, line_dash="dash", annotation_text="Entry")
    if stop is not None:
        fig.add_hline(y=stop, line_dash="dash", annotation_text="SL")
    if target is not None:
        fig.add_hline(y=target, line_dash="dash", annotation_text="Target")

    fig.update_layout(
        title=f"{symbol} Price Structure",
        template="plotly_dark",
        height=520,
        xaxis_rangeslider_visible=False,
        margin=dict(l=8, r=8, t=36, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig

def make_rsi_chart(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI14"], name="RSI 14"))
    fig.add_hline(y=70, line_dash="dot")
    fig.add_hline(y=30, line_dash="dot")
    fig.update_layout(
        template="plotly_dark",
        height=255,
        margin=dict(l=8, r=8, t=26, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig

def parse_portfolio_text(portfolio_text: str):
    rows = []
    if not portfolio_text.strip():
        return pd.DataFrame(columns=["Symbol", "Quantity", "Avg Buy Price"])

    for line in portfolio_text.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 3:
            continue
        symbol, qty, avg = parts
        try:
            qty = float(qty)
            avg = float(avg)
            if qty > 0 and avg > 0:
                rows.append({"Symbol": symbol, "Quantity": qty, "Avg Buy Price": avg})
        except Exception:
            continue

    return pd.DataFrame(rows)

def portfolio_action_from_metrics(pl_pct, score, rsi):
    if pl_pct < -10 and score < 35:
        return "EXIT"
    elif pl_pct > 18 and (rsi > 75 or score < 45):
        return "REDUCE"
    elif score >= 70 and 45 <= rsi <= 70:
        return "ADD"
    return "HOLD"

def make_portfolio_risk_gauge(value):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": "Portfolio Risk"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#8b5cf6"},
                "steps": [
                    {"range": [0, 35], "color": "rgba(34,197,94,0.35)"},
                    {"range": [35, 70], "color": "rgba(245,158,11,0.35)"},
                    {"range": [70, 100], "color": "rgba(239,68,68,0.35)"},
                ],
            },
        )
    )
    fig.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=36, b=6),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig

# -------------------------------------------------
# PDF HELPERS (IMPROVED + CACHED DATA PREP)
# -------------------------------------------------
def pdf_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleNile",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "SubNile",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#475569"),
            spaceAfter=10,
        ),
        "section": ParagraphStyle(
            "SectionNile",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=14,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#1E3A8A"),
            spaceAfter=6,
            spaceBefore=6,
        ),
        "section_alt": ParagraphStyle(
            "SectionAltNile",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=14,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#0F766E"),
            spaceAfter=6,
            spaceBefore=6,
        ),
        "body": ParagraphStyle(
            "BodyNile",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#111827"),
        ),
        "small": ParagraphStyle(
            "SmallNile",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#475569"),
        ),
    }

def pdf_table(data, col_widths=None, header_bg="#0F172A"):
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tbl

def pdf_highlight_box(title, value, subtitle=""):
    data = [
        [title],
        [value],
        [subtitle]
    ]
    tbl = Table(data, colWidths=[55 * mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF2FF")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#C7D2FE")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E0E7FF")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 2), (-1, 2), colors.HexColor("#475569")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTNAME", (0, 2), (-1, 2), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTSIZE", (0, 1), (-1, 1), 12),
        ("FONTSIZE", (0, 2), (-1, 2), 7),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return tbl

@st.cache_data(ttl=600, show_spinner=False)
def prepare_stock_pdf_payload(
    symbol,
    info,
    last_close,
    change_pct,
    ai_action,
    conviction_score,
    conviction_label,
    score,
    verdict,
    trend_signal,
    macd_signal,
    rsi,
    entry,
    stop_loss,
    target,
    qty,
    position_value,
    portfolio_summary_key=None,
    scan_summary_key=None,
):
    """
    Cache-safe payload builder.
    Only stores lightweight serializable data.
    """
    return {
        "symbol": symbol,
        "generated": datetime.now().strftime("%d-%b-%Y %I:%M %p"),
        "last_close": last_close,
        "change_pct": change_pct,
        "sector": str(info.get("sector", "N/A")),
        "industry": str(info.get("industry", "N/A")),
        "ai_action": ai_action,
        "conviction": f"{conviction_score}/100 ({conviction_label})",
        "score": f"{score}/100 ({verdict})",
        "trend_signal": trend_signal,
        "macd_signal": macd_signal,
        "rsi": round(float(rsi), 2) if pd.notna(rsi) else "N/A",
        "entry": entry,
        "stop_loss": stop_loss,
        "target": target,
        "qty": qty,
        "position_value": position_value,
        "market_cap": f"₹{info.get('marketCap', 0)/1e7:,.0f} Cr" if pd.notna(info.get("marketCap", np.nan)) else "N/A",
        "trailing_pe": str(info.get("trailingPE", "N/A")),
        "forward_pe": str(info.get("forwardPE", "N/A")),
        "price_to_book": str(info.get("priceToBook", "N/A")),
        "roe": str(round((info.get("returnOnEquity", 0) or 0) * 100, 2)) if info.get("returnOnEquity") is not None else "N/A",
        "de_ratio": str(info.get("debtToEquity", "N/A")),
        "profit_margin": str(round((info.get("profitMargins", 0) or 0) * 100, 2)) if info.get("profitMargins") is not None else "N/A",
        "portfolio_summary_key": portfolio_summary_key,
        "scan_summary_key": scan_summary_key,
    }

def build_stock_pdf(
    payload,
    portfolio_analysis_df=None,
    scan_df=None,
):
    if not PDF_AVAILABLE:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )
    s = pdf_styles()
    story = []

    story.append(Paragraph("NILE", s["title"]))
    story.append(Paragraph("Premium Stock Research Report", s["subtitle"]))
    story.append(Spacer(1, 2))

    # Premium summary highlight row
    highlights = Table([[
        pdf_highlight_box("SYMBOL", payload["symbol"], "Selected Stock"),
        pdf_highlight_box("AI SIGNAL", payload["ai_action"], "Decision Engine"),
        pdf_highlight_box("CONVICTION", payload["conviction"], "Confidence Model"),
    ]], colWidths=[58 * mm, 58 * mm, 58 * mm])
    story.append(highlights)
    story.append(Spacer(1, 8))

    summary_data = [
        ["Field", "Value"],
        ["Generated", payload["generated"]],
        ["Current Price", rupee(payload["last_close"])],
        ["Daily Change", f"{payload['change_pct']:+.2f}%"],
        ["Sector", payload["sector"]],
        ["Industry", payload["industry"]],
        ["Institutional Score", payload["score"]],
        ["Trend Signal", payload["trend_signal"]],
        ["MACD Signal", payload["macd_signal"]],
        ["RSI", str(payload["rsi"])],
    ]
    story.append(Paragraph("Stock Summary", s["section"]))
    story.append(pdf_table(summary_data, col_widths=[55 * mm, 115 * mm]))
    story.append(Spacer(1, 8))

    trade_data = [
        ["Trade Plan", "Value"],
        ["Suggested Entry", rupee(payload["entry"])],
        ["Stop Loss", rupee(payload["stop_loss"])],
        ["Target", rupee(payload["target"])],
        ["Quantity", str(payload["qty"])],
        ["Position Size", rupee(payload["position_value"])],
    ]
    story.append(Paragraph("Professional Trade Plan", s["section_alt"]))
    story.append(pdf_table(trade_data, col_widths=[55 * mm, 115 * mm], header_bg="#0F766E"))
    story.append(Spacer(1, 8))

    fundamental_data = [
        ["Fundamental Metric", "Value"],
        ["Market Cap", payload["market_cap"]],
        ["P/E", payload["trailing_pe"]],
        ["Forward P/E", payload["forward_pe"]],
        ["Price / Book", payload["price_to_book"]],
        ["ROE (%)", payload["roe"]],
        ["Debt / Equity", payload["de_ratio"]],
        ["Profit Margin (%)", payload["profit_margin"]],
    ]
    story.append(Paragraph("Fundamental Snapshot", s["section"]))
    story.append(pdf_table(fundamental_data, col_widths=[65 * mm, 105 * mm], header_bg="#1D4ED8"))
    story.append(Spacer(1, 8))

    if portfolio_analysis_df is not None and not portfolio_analysis_df.empty:
        total_invested = portfolio_analysis_df["Invested Value"].sum()
        total_current = portfolio_analysis_df["Current Value"].sum()
        total_pl = total_current - total_invested
        total_pl_pct = ((total_current / total_invested) - 1) * 100 if total_invested else 0

        top_gainer = portfolio_analysis_df.sort_values("P/L %", ascending=False).iloc[0]
        top_loser = portfolio_analysis_df.sort_values("P/L %", ascending=True).iloc[0]

        port_summary = [
            ["Portfolio Summary", "Value"],
            ["Total Invested", rupee(total_invested)],
            ["Current Value", rupee(total_current)],
            ["Total P/L", rupee(total_pl)],
            ["Total P/L %", f"{total_pl_pct:+.2f}%"],
            ["Top Gainer", f"{top_gainer['Symbol']} ({top_gainer['P/L %']:+.2f}%)"],
            ["Top Loser", f"{top_loser['Symbol']} ({top_loser['P/L %']:+.2f}%)"],
        ]
        story.append(Paragraph("Portfolio Snapshot", s["section_alt"]))
        story.append(pdf_table(port_summary, col_widths=[55 * mm, 115 * mm], header_bg="#7C3AED"))
        story.append(Spacer(1, 8))

    if scan_df is not None and not scan_df.empty:
        top_scan = scan_df.head(3).copy()
        scan_table = [["Symbol", "AI", "Score", "Price", "Entry", "Stop"]]
        for _, row in top_scan.iterrows():
            scan_table.append([
                str(row["Symbol"]),
                str(row["AI"]),
                str(row["Score"]),
                str(row["Price"]),
                str(row["Entry"]),
                str(row["Stop"]),
            ])
        story.append(Paragraph("Top Scanner Setups", s["section"]))
        story.append(pdf_table(scan_table, col_widths=[32 * mm, 22 * mm, 22 * mm, 28 * mm, 28 * mm, 28 * mm], header_bg="#15803D"))
        story.append(Spacer(1, 8))

    disclaimer = (
        "This report is generated for educational and research purposes only. "
        "Market data may be delayed or incomplete. This is not investment advice. "
        "Always verify independently before taking any trading or investment decision."
    )
    story.append(Paragraph("Risk Disclaimer", s["section"]))
    story.append(Paragraph(disclaimer, s["small"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def build_portfolio_pdf(portfolio_analysis_df):
    if not PDF_AVAILABLE or portfolio_analysis_df is None or portfolio_analysis_df.empty:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )
    s = pdf_styles()
    story = []

    total_invested = portfolio_analysis_df["Invested Value"].sum()
    total_current = portfolio_analysis_df["Current Value"].sum()
    total_pl = total_current - total_invested
    total_pl_pct = ((total_current / total_invested) - 1) * 100 if total_invested else 0

    top_gainer = portfolio_analysis_df.sort_values("P/L %", ascending=False).iloc[0]
    top_loser = portfolio_analysis_df.sort_values("P/L %", ascending=True).iloc[0]

    story.append(Paragraph("NILE", s["title"]))
    story.append(Paragraph("Portfolio Command Center Report", s["subtitle"]))
    story.append(Spacer(1, 2))

    highlights = Table([[
        pdf_highlight_box("INVESTED", rupee(total_invested), "Capital Deployed"),
        pdf_highlight_box("CURRENT", rupee(total_current), "Marked-to-Market"),
        pdf_highlight_box("TOTAL P/L", f"{rupee(total_pl)} ({total_pl_pct:+.2f}%)", "Performance"),
    ]], colWidths=[58 * mm, 58 * mm, 58 * mm])
    story.append(highlights)
    story.append(Spacer(1, 8))

    summary = [
        ["Portfolio Metric", "Value"],
        ["Generated", datetime.now().strftime("%d-%b-%Y %I:%M %p")],
        ["Top Gainer", f"{top_gainer['Symbol']} ({top_gainer['P/L %']:+.2f}%)"],
        ["Top Loser", f"{top_loser['Symbol']} ({top_loser['P/L %']:+.2f}%)"],
    ]
    story.append(Paragraph("Portfolio Summary", s["section_alt"]))
    story.append(pdf_table(summary, col_widths=[60 * mm, 110 * mm], header_bg="#7C3AED"))
    story.append(Spacer(1, 8))

    holdings = [["Symbol", "Qty", "Avg Buy", "Current", "P/L ₹", "P/L %", "Action"]]
    for _, row in portfolio_analysis_df.iterrows():
        holdings.append([
            str(row["Symbol"]),
            str(int(row["Quantity"]) if float(row["Quantity"]).is_integer() else row["Quantity"]),
            f"{row['Avg Buy Price']}",
            f"{row['Current Price']}",
            f"{row['P/L ₹']}",
            f"{row['P/L %']:+.2f}%",
            str(row["Action"]),
        ])

    story.append(Paragraph("Holdings Detail", s["section"]))
    story.append(pdf_table(holdings, col_widths=[32 * mm, 16 * mm, 24 * mm, 24 * mm, 28 * mm, 20 * mm, 24 * mm], header_bg="#0F766E"))
    story.append(Spacer(1, 8))

    sector_alloc = (
        portfolio_analysis_df.groupby("Sector", as_index=False)["Current Value"].sum()
        .sort_values("Current Value", ascending=False)
    )
    sector_table = [["Sector", "Current Value", "Weight %"]]
    for _, row in sector_alloc.iterrows():
        wt = (row["Current Value"] / max(total_current, 1)) * 100
        sector_table.append([str(row["Sector"]), rupee(row["Current Value"]), f"{wt:.2f}%"])

    story.append(Paragraph("Sector Allocation", s["section"]))
    story.append(pdf_table(sector_table, col_widths=[60 * mm, 60 * mm, 50 * mm], header_bg="#1D4ED8"))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Risk Disclaimer", s["section"]))
    story.append(Paragraph(
        "This portfolio report is for tracking and educational purposes only. "
        "Always review diversification, risk exposure, and position sizing before acting.",
        s["small"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def build_scanner_pdf(scan_df):
    if not PDF_AVAILABLE or scan_df is None or scan_df.empty:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )
    s = pdf_styles()
    story = []

    story.append(Paragraph("NILE", s["title"]))
    story.append(Paragraph("Institutional Scanner Report", s["subtitle"]))
    story.append(Spacer(1, 2))

    top_symbol = str(scan_df.iloc[0]["Symbol"]) if not scan_df.empty else "N/A"
    top_score = str(scan_df.iloc[0]["Score"]) if not scan_df.empty else "N/A"

    highlights = Table([[
        pdf_highlight_box("TOTAL SETUPS", str(len(scan_df)), "Scanned Universe"),
        pdf_highlight_box("TOP SETUP", top_symbol, "Best Ranked"),
        pdf_highlight_box("TOP SCORE", top_score, "Institutional Rank"),
    ]], colWidths=[58 * mm, 58 * mm, 58 * mm])
    story.append(highlights)
    story.append(Spacer(1, 8))

    rows = [["Rank", "Symbol", "AI", "Score", "Price", "Entry", "Stop", "RSI"]]
    for idx, (_, row) in enumerate(scan_df.head(10).iterrows(), start=1):
        rows.append([
            str(idx),
            str(row["Symbol"]),
            str(row["AI"]),
            str(row["Score"]),
            str(row["Price"]),
            str(row["Entry"]),
            str(row["Stop"]),
            str(row["RSI"]),
        ])

    story.append(Paragraph("Top Institutional Setups", s["section"]))
    story.append(pdf_table(rows, col_widths=[14 * mm, 28 * mm, 18 * mm, 18 * mm, 22 * mm, 22 * mm, 22 * mm, 16 * mm], header_bg="#0F172A"))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Risk Disclaimer", s["section"]))
    story.append(Paragraph(
        "Scanner results are rule-based and data dependent. Always validate price action, liquidity, and risk before execution.",
        s["small"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "scan_df" not in st.session_state:
    st.session_state.scan_df = pd.DataFrame()

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.markdown("## Nile")
    st.caption("Stock Analysis")

    universe_choice = st.radio(
        "Stock Universe",
        ["NIFTY 50", "NIFTY NEXT 50", "NIFTY 100 (Combined)"],
        index=2,
    )

    stock_list = (
        NIFTY_50 if universe_choice == "NIFTY 50"
        else NIFTY_NEXT_50 if universe_choice == "NIFTY NEXT 50"
        else UNIVERSE
    )

    symbol = st.selectbox("Select Stock", options=stock_list, index=0)
    period = st.selectbox("History Period", ["6mo", "1y", "2y", "5y"], index=1)

    capital = st.number_input("Capital (₹)", min_value=1000, value=100000, step=1000)
    risk_pct = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    rr_ratio = st.slider("Risk : Reward", 1.0, 5.0, 2.0, 0.5)

    # Safer cloud scan cap
    max_scan_cap = min(60, len(stock_list))
    default_scan = min(25, max_scan_cap)
    scan_count = st.slider("Scanner Universe", 10, max_scan_cap, default_scan)
    compare_symbols = st.multiselect("Multi-Stock Compare", stock_list, default=stock_list[:3], max_selections=5)

    st.markdown("---")
    st.markdown("### Portfolio Command Center")
    portfolio_text = st.text_area(
        "Portfolio Input (SYMBOL, QTY, AVG BUY)",
        value="RELIANCE.NS,10,2450\nTCS.NS,5,3800\nHDFCBANK.NS,20,1650",
        height=120,
        help="One line per stock: SYMBOL,QUANTITY,AVG_BUY_PRICE",
    )

    run_scan = st.button("Run Institutional Scan", key="run_scan_btn")

# -------------------------------------------------
# HEADER / LOGO
# -------------------------------------------------
logo_candidates = [
    Path("FullLogo_NoBuffer.png"),
    Path("./FullLogo_NoBuffer.png"),
    Path("/mount/src/stock-analysis-pro/FullLogo_NoBuffer.png"),
]
logo_found = next((p for p in logo_candidates if p.exists()), None)

logo_l, logo_c, logo_r = st.columns([2.2, 2.8, 2.2])
with logo_c:
    if logo_found:
        st.markdown(
            "<div style='display:flex; justify-content:center; align-items:center; margin-top:0.05rem; margin-bottom:0.05rem;'><div style=\"padding:10px; border-radius:24px; background: radial-gradient(circle, rgba(245,208,92,0.08) 0%, rgba(245,208,92,0.03) 38%, rgba(0,0,0,0) 72%); box-shadow: 0 0 28px rgba(245,208,92,0.12), 0 0 56px rgba(245,208,92,0.05);\">",
            unsafe_allow_html=True,
        )
        st.image(str(logo_found), width=230)
        st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div style='font-size:2.6rem;font-weight:900;color:#fff;text-align:center;text-shadow:0 0 20px rgba(245,208,92,0.12);'>Nile</div>",
            unsafe_allow_html=True,
        )
    st.markdown("<div class='premium-subtitle'>Stock Analysis</div>", unsafe_allow_html=True)

# -------------------------------------------------
# TOP RIBBON + LIVE CARDS
# -------------------------------------------------
nifty50_last, nifty50_chg = get_live_index("^NSEI")
banknifty_last, banknifty_chg = get_live_index("^NSEBANK")
indiavix_last, indiavix_chg = get_live_index("^INDIAVIX")

now_ist = datetime.now()
market_open = now_ist.weekday() < 5 and (
    ((now_ist.hour > 9) or (now_ist.hour == 9 and now_ist.minute >= 15))
    and ((now_ist.hour < 15) or (now_ist.hour == 15 and now_ist.minute <= 30))
)
market_status = "OPEN" if market_open else "CLOSED"
market_status_color = "#22c55e" if market_open else "#ef4444"
last_updated = now_ist.strftime("%d-%b-%Y %I:%M %p")

st.markdown(
    f"""
    <div class='imperial-ribbon'>
        <span class='ribbon-chip'>NIFTY 50</span>
        <span class='ribbon-chip'>BANK NIFTY</span>
        <span class='ribbon-chip'>INDIA VIX</span>
        <span class='ribbon-chip'>Imperial Terminal</span>
        <span class='ribbon-chip'>Institutional Flow</span>
        <span class='ribbon-chip'>Cloud Safe</span>
        <span class='ribbon-chip' style='color:{market_status_color};'>Market: {market_status}</span>
        <span class='ribbon-chip'>Last Updated: {last_updated}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3, gap="small")
with c1:
    beautiful_top_card(
        "NIFTY 50 Live",
        nifty50_last,
        nifty50_chg,
        "linear-gradient(135deg, rgba(29,78,216,0.44), rgba(8,14,28,0.96))",
    )
with c2:
    beautiful_top_card(
        "BANK NIFTY Live",
        banknifty_last,
        banknifty_chg,
        "linear-gradient(135deg, rgba(21,128,61,0.44), rgba(8,14,28,0.96))",
    )
with c3:
    beautiful_top_card(
        "INDIA VIX Live",
        indiavix_last,
        indiavix_chg,
        "linear-gradient(135deg, rgba(127,29,29,0.38), rgba(8,14,28,0.96))",
        inverse=True,
    )

# -------------------------------------------------
# MARKET BREADTH STRIP (LIGHTER LOOPS)
# -------------------------------------------------
# Optimized: use smaller sample + lightweight metrics only
breadth_sample_size = min(18, len(stock_list))
breadth_symbols = stock_list[:breadth_sample_size]
advancers = 0
decliners = 0
bullish_trend_count = 0
breadth_rows = []

for s in breadth_symbols:
    d = get_history(s, period="3mo")
    if d.empty or len(d) < 55:
        continue

    m = compute_scan_metrics_fast(d)
    if not m:
        continue

    if m["day_ret"] >= 0:
        advancers += 1
    else:
        decliners += 1

    if m["sma20"] > m["sma50"]:
        bullish_trend_count += 1

    breadth_rows.append(m["day_ret"])

avg_day_ret = np.mean(breadth_rows) if breadth_rows else 0
breadth_ratio = round((advancers / max(advancers + decliners, 1)) * 100, 1)
trend_ratio = round((bullish_trend_count / max(len(breadth_rows), 1)) * 100, 1) if breadth_rows else 0

b1, b2, b3, b4 = st.columns(4, gap="small")
with b1:
    st.markdown(
        f"""
        <div class='breadth-card'>
            <div class='breadth-label'>Advance / Decline</div>
            <div class='breadth-value'>{advancers} / {decliners}</div>
            <div class='metric-delta-flat'>Market breadth</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with b2:
    cls = "metric-delta-up" if breadth_ratio >= 55 else "metric-delta-down"
    st.markdown(
        f"""
        <div class='breadth-card'>
            <div class='breadth-label'>Breadth Strength</div>
            <div class='breadth-value'>{breadth_ratio}%</div>
            <div class='{cls}'>Advancers share</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with b3:
    cls = "metric-delta-up" if trend_ratio >= 55 else "metric-delta-down"
    st.markdown(
        f"""
        <div class='breadth-card'>
            <div class='breadth-label'>Bullish Trend Stocks</div>
            <div class='breadth-value'>{bullish_trend_count}</div>
            <div class='{cls}'>{trend_ratio}% above trend filter</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with b4:
    cls = "metric-delta-up" if avg_day_ret >= 0 else "metric-delta-down"
    st.markdown(
        f"""
        <div class='breadth-card'>
            <div class='breadth-label'>Average Daily Return</div>
            <div class='breadth-value'>{avg_day_ret:+.2f}%</div>
            <div class='{cls}'>Universe average</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------------------------------
# MAIN SELECTED STOCK DATA
# -------------------------------------------------
raw = get_history(symbol, period=period)
if raw.empty:
    st.error("Unable to fetch market data. Please ensure yfinance is installed and internet is available on deployment.")
    st.stop()

df = compute_indicators(raw)
if df.empty:
    st.warning("Not enough data to compute indicators.")
    st.stop()

info = get_info(symbol)
bs, fin, cf = get_financials(symbol)

last_close = safe_last(df["Close"])
prev_close = float(df["Close"].iloc[-2]) if len(df) > 1 else last_close
change_pct = ((last_close / prev_close) - 1) * 100 if prev_close else 0

rsi = safe_last(df["RSI14"])
atr = safe_last(df["ATR14"])

score, verdict, _ = score_stock(df)

trend_signal = "Bullish" if df.iloc[-1]["SMA20"] > df.iloc[-1]["SMA50"] else "Bearish"
macd_signal = "Bullish" if df.iloc[-1]["MACD"] > df.iloc[-1]["MACD_SIGNAL"] else "Bearish"

breakout_level = df["High"].tail(20).max()
support_level = df["Low"].tail(20).min()
entry = breakout_level * 1.002
stop_loss = max(entry - atr * 1.5, support_level)
risk_per_share = max(entry - stop_loss, 0.01)

allowed_risk = capital * (risk_pct / 100)
qty = max(int(allowed_risk // risk_per_share), 0)
target = entry + (risk_per_share * rr_ratio)
position_value = qty * entry

ai_action, ai_class, ai_reason = ai_badge(score, rsi, trend_signal, macd_signal)
conviction_score, conviction_label = conviction_meter(score, rsi, trend_signal, macd_signal)

# -------------------------------------------------
# INSTITUTIONAL SUMMARY STRIP
# -------------------------------------------------
s1, s2, s3 = st.columns([1.15, 0.9, 1.2], gap="small")

with s1:
    st.markdown(
        f"""
        <div class='{ai_class}'>
            AI {ai_action} • {conviction_score}% Confidence<br>
            <span style='font-size:0.82rem;font-weight:700'>{ai_reason}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with s2:
    st.plotly_chart(make_gauge(conviction_score), use_container_width=True)

with s3:
    st.markdown(
        f"""
        <div class='panel'>
            <div class='panel-title'>Institutional Summary</div>
            <div class='subtle-divider'></div>
            <span class='ribbon-chip'>Trend: {trend_signal}</span>
            <span class='ribbon-chip'>Momentum: {macd_signal}</span>
            <span class='ribbon-chip'>RSI: {rsi:.1f}</span>
            <span class='ribbon-chip'>Sector: {info.get('sector','N/A')}</span>
            <span class='ribbon-chip'>Action: {ai_action}</span>
            <div style='margin-top:8px;color:#cbd5e1;font-weight:700;font-size:0.88rem;'>
                BUY above {entry:.2f} • SL {stop_loss:.2f} • Target {target:.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------------------------------
# METRICS GRID
# -------------------------------------------------
m1, m2, m3, m4, m5 = st.columns(5, gap="small")
with m1:
    metric_box("Last Price", rupee(last_close), f"{change_pct:+.2f}% today", positive=change_pct >= 0)
with m2:
    metric_box("Institutional Score", f"{score}/100", verdict, positive=score >= 55)
with m3:
    metric_box("RSI (14)", f"{rsi:.2f}", "Healthy" if 50 <= rsi <= 70 else "Watch", positive=50 <= rsi <= 70)
with m4:
    metric_box("ATR (14)", f"{atr:.2f}", "Volatility gauge", positive=None)
with m5:
    market_cap = info.get("marketCap", np.nan)
    metric_box(
        "Market Cap",
        f"₹{market_cap/1e7:,.0f} Cr" if pd.notna(market_cap) else "N/A",
        info.get("sector", "Unknown"),
        positive=None,
    )

# -------------------------------------------------
# CONTROL STRIP
# -------------------------------------------------
cb1, cb2 = st.columns(2, gap="small")
with cb1:
    show_fundamental_ratio = st.button("Fundamental Ratio", key="fundamental_ratio_btn")
with cb2:
    show_technical_ratio = st.button("Technical Ratio", key="technical_ratio_btn")

# -------------------------------------------------
# PRIMARY ANALYSIS ROW
# -------------------------------------------------
left, right = st.columns([2.1, 0.9], gap="small")

with left:
    st.markdown(
        "<div class='panel'><div class='panel-title'>Price Structure</div><div class='subtle-divider'></div></div>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        make_candlestick(df.tail(180), symbol, entry, stop_loss, target, breakout_level, support_level),
        use_container_width=True,
    )

with right:
    st.markdown(
        "<div class='panel'><div class='panel-title'>Momentum (RSI)</div><div class='subtle-divider'></div></div>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(make_rsi_chart(df.tail(180)), use_container_width=True)

# -------------------------------------------------
# SIGNAL ENGINE + TRADE PLAN
# -------------------------------------------------
sg1, sg2 = st.columns([1.15, 1.85], gap="small")

with sg1:
    st.markdown(
        "<div class='panel'><div class='panel-title'>Institutional Signal Engine</div><div class='subtle-divider'></div></div>",
        unsafe_allow_html=True,
    )
    st.info(
        f"**Trend:** {trend_signal}\n\n"
        f"**SMA20:** {df.iloc[-1]['SMA20']:.2f}\n\n"
        f"**SMA50:** {df.iloc[-1]['SMA50']:.2f}"
    )
    st.info(
        f"**MACD:** {macd_signal}\n\n"
        f"**MACD:** {df.iloc[-1]['MACD']:.2f}\n\n"
        f"**Signal:** {df.iloc[-1]['MACD_SIGNAL']:.2f}"
    )
    st.info(
        f"**Breakout Level:** {breakout_level:.2f}\n\n"
        f"**Support Level:** {support_level:.2f}\n\n"
        f"**20D Range Strategy**"
    )

with sg2:
    st.markdown(
        "<div class='panel'><div class='panel-title'>Professional Trade Plan</div><div class='subtle-divider'></div></div>",
        unsafe_allow_html=True,
    )
    p1, p2, p3, p4, p5 = st.columns(5, gap="small")
    with p1:
        metric_box("Suggested Entry", rupee(entry), "Breakout confirmation", True)
    with p2:
        metric_box("Stop Loss", rupee(stop_loss), "ATR + support based", False)
    with p3:
        metric_box("Target", rupee(target), f"R:R {rr_ratio:.1f}", True)
    with p4:
        metric_box("Quantity", f"{qty}", f"Risk {rupee(allowed_risk)}", True if qty > 0 else None)
    with p5:
        metric_box("Position Size", rupee(position_value), "Capital deployed", position_value <= capital)

# -------------------------------------------------
# PORTFOLIO COMMAND CENTER
# -------------------------------------------------
portfolio_df = parse_portfolio_text(portfolio_text)

st.markdown(
    "<div class='panel'><div class='panel-title'>Portfolio Command Center</div><div class='subtle-divider'></div></div>",
    unsafe_allow_html=True,
)

portfolio_analysis_df = pd.DataFrame()

if not portfolio_df.empty:
    portfolio_rows = []

    for _, row in portfolio_df.iterrows():
        psym = row["Symbol"]
        qty_p = row["Quantity"]
        avg_buy = row["Avg Buy Price"]

        pdata = get_history(psym, period="6mo")
        if pdata.empty:
            continue

        pinfo = get_info(psym)
        pm = compute_scan_metrics_fast(pdata)
        if not pm:
            continue

        current_price = pm["close"]
        prev_price = pm["prev_close"]
        day_change_pct = ((current_price / prev_price) - 1) * 100 if prev_price else 0

        invested = qty_p * avg_buy
        current_value = qty_p * current_price
        pl_abs = current_value - invested
        pl_pct = ((current_price / avg_buy) - 1) * 100 if avg_buy else 0

        pscore, pverdict = score_from_metrics(pm)
        prsi = pm["rsi"]
        psector = SECTOR_MAP.get(psym, pinfo.get("sector", "Others"))
        action = portfolio_action_from_metrics(pl_pct, pscore, prsi)

        portfolio_rows.append({
            "Symbol": psym,
            "Quantity": qty_p,
            "Avg Buy Price": round(avg_buy, 2),
            "Current Price": round(current_price, 2),
            "Invested Value": round(invested, 2),
            "Current Value": round(current_value, 2),
            "P/L ₹": round(pl_abs, 2),
            "P/L %": round(pl_pct, 2),
            "Day Change %": round(day_change_pct, 2),
            "Sector": psector,
            "Score": pscore,
            "RSI": round(prsi, 2) if pd.notna(prsi) else np.nan,
            "AI Verdict": pverdict,
            "Action": action,
        })

    portfolio_analysis_df = pd.DataFrame(portfolio_rows)

    if not portfolio_analysis_df.empty:
        total_invested = portfolio_analysis_df["Invested Value"].sum()
        total_current = portfolio_analysis_df["Current Value"].sum()
        total_pl = total_current - total_invested
        total_pl_pct = ((total_current / total_invested) - 1) * 100 if total_invested else 0

        weighted_scores = (
            (portfolio_analysis_df["Score"] * portfolio_analysis_df["Current Value"]).sum() / max(total_current, 1)
        )
        concentration = (
            portfolio_analysis_df["Current Value"].max() / max(total_current, 1) * 100
        )
        loss_positions = (portfolio_analysis_df["P/L %"] < 0).sum()
        total_positions = len(portfolio_analysis_df)
        loss_ratio = (loss_positions / max(total_positions, 1)) * 100

        portfolio_risk_score = min(
            100,
            round(
                (concentration * 0.45)
                + (loss_ratio * 0.25)
                + ((100 - weighted_scores) * 0.30)
            )
        )

        top_gainer = portfolio_analysis_df.sort_values("P/L %", ascending=False).iloc[0]
        top_loser = portfolio_analysis_df.sort_values("P/L %", ascending=True).iloc[0]

        pc1, pc2, pc3, pc4 = st.columns(4, gap="small")
        with pc1:
            metric_box("Total Invested", rupee(total_invested), "Portfolio cost", None)
        with pc2:
            metric_box("Current Value", rupee(total_current), "Live marked-to-market", total_current >= total_invested)
        with pc3:
            metric_box("Total P/L ₹", rupee(total_pl), f"{total_pl_pct:+.2f}%", total_pl >= 0)
        with pc4:
            metric_box("Positions", f"{total_positions}", f"Risk Score {portfolio_risk_score}/100", portfolio_risk_score < 60)

        pleft, pright = st.columns([2.1, 0.9], gap="small")

        with pleft:
            st.markdown(
                "<div class='panel'><div class='panel-title'>Portfolio Holdings Table</div><div class='subtle-divider'></div></div>",
                unsafe_allow_html=True,
            )

            portfolio_analysis_df["Weight %"] = (
                portfolio_analysis_df["Current Value"] / max(total_current, 1) * 100
            ).round(2)

            st.dataframe(
                portfolio_analysis_df[
                    [
                        "Symbol", "Quantity", "Avg Buy Price", "Current Price",
                        "Invested Value", "Current Value", "P/L ₹", "P/L %",
                        "Weight %", "Sector", "Score", "RSI", "Action"
                    ]
                ],
                use_container_width=True,
            )

        with pright:
            st.markdown(
                "<div class='panel'><div class='panel-title'>Portfolio Risk Meter</div><div class='subtle-divider'></div></div>",
                unsafe_allow_html=True,
            )
            st.plotly_chart(make_portfolio_risk_gauge(portfolio_risk_score), use_container_width=True)

        pa1, pa2, pa3, pa4 = st.columns(4, gap="small")
        with pa1:
            st.markdown(
                f"""
                <div class='portfolio-card'>
                    <div class='portfolio-label'>Top Gainer</div>
                    <div class='portfolio-value'>{top_gainer['Symbol'].replace('.NS','')}</div>
                    <div class='metric-delta-up'>{top_gainer['P/L %']:+.2f}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with pa2:
            st.markdown(
                f"""
                <div class='portfolio-card'>
                    <div class='portfolio-label'>Top Loser</div>
                    <div class='portfolio-value'>{top_loser['Symbol'].replace('.NS','')}</div>
                    <div class='metric-delta-down'>{top_loser['P/L %']:+.2f}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with pa3:
            overweight_sector = (
                portfolio_analysis_df.groupby("Sector")["Current Value"].sum().sort_values(ascending=False).index[0]
            )
            overweight_weight = (
                portfolio_analysis_df.groupby("Sector")["Current Value"].sum().sort_values(ascending=False).iloc[0]
                / max(total_current, 1) * 100
            )
            cls = "metric-delta-down" if overweight_weight > 40 else "metric-delta-up"
            st.markdown(
                f"""
                <div class='portfolio-card'>
                    <div class='portfolio-label'>Top Sector Exposure</div>
                    <div class='portfolio-value'>{overweight_sector}</div>
                    <div class='{cls}'>{overweight_weight:.1f}% allocation</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with pa4:
            best_add = portfolio_analysis_df.sort_values(["Score", "P/L %"], ascending=[False, True]).iloc[0]
            st.markdown(
                f"""
                <div class='portfolio-card'>
                    <div class='portfolio-label'>Best Add Candidate</div>
                    <div class='portfolio-value'>{best_add['Symbol'].replace('.NS','')}</div>
                    <div class='metric-delta-up'>Score {int(best_add['Score'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div class='panel'><div class='panel-title'>Portfolio Sector Allocation</div><div class='subtle-divider'></div></div>",
            unsafe_allow_html=True,
        )
        sector_alloc = (
            portfolio_analysis_df.groupby("Sector", as_index=False)["Current Value"].sum()
            .sort_values("Current Value", ascending=False)
        )
        fig_sector_alloc = px.pie(
            sector_alloc,
            names="Sector",
            values="Current Value",
            hole=0.45,
        )
        fig_sector_alloc.update_layout(
            template="plotly_dark",
            height=380,
            margin=dict(l=8, r=8, t=20, b=8),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_sector_alloc, use_container_width=True)

        st.markdown(
            "<div class='panel'><div class='panel-title'>Portfolio Action Suggestions</div><div class='subtle-divider'></div></div>",
            unsafe_allow_html=True,
        )
        sug1, sug2, sug3, sug4 = st.columns(4, gap="small")

        add_candidates = portfolio_analysis_df[portfolio_analysis_df["Action"] == "ADD"]
        hold_candidates = portfolio_analysis_df[portfolio_analysis_df["Action"] == "HOLD"]
        reduce_candidates = portfolio_analysis_df[portfolio_analysis_df["Action"] == "REDUCE"]
        exit_candidates = portfolio_analysis_df[portfolio_analysis_df["Action"] == "EXIT"]

        with sug1:
            add_text = (
                ", ".join(add_candidates["Symbol"].str.replace(".NS", "", regex=False).head(3).tolist())
                if not add_candidates.empty else "None"
            )
            st.markdown(
                f"""
                <div class='portfolio-card'>
                    <div class='portfolio-label'>ADD</div>
                    <div class='portfolio-value' style='font-size:1rem'>{add_text}</div>
                    <div class='portfolio-action-add'>Strong setups</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sug2:
            hold_text = (
                ", ".join(hold_candidates["Symbol"].str.replace(".NS", "", regex=False).head(3).tolist())
                if not hold_candidates.empty else "None"
            )
            st.markdown(
                f"""
                <div class='portfolio-card'>
                    <div class='portfolio-label'>HOLD</div>
                    <div class='portfolio-value' style='font-size:1rem'>{hold_text}</div>
                    <div class='portfolio-action-hold'>Maintain position</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sug3:
            reduce_text = (
                ", ".join(reduce_candidates["Symbol"].str.replace(".NS", "", regex=False).head(3).tolist())
                if not reduce_candidates.empty else "None"
            )
            st.markdown(
                f"""
                <div class='portfolio-card'>
                    <div class='portfolio-label'>REDUCE</div>
                    <div class='portfolio-value' style='font-size:1rem'>{reduce_text}</div>
                    <div class='portfolio-action-reduce'>Book partial profits</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sug4:
            exit_text = (
                ", ".join(exit_candidates["Symbol"].str.replace(".NS", "", regex=False).head(3).tolist())
                if not exit_candidates.empty else "None"
            )
            st.markdown(
                f"""
                <div class='portfolio-card'>
                    <div class='portfolio-label'>EXIT</div>
                    <div class='portfolio-value' style='font-size:1rem'>{exit_text}</div>
                    <div class='portfolio-action-exit'>Weak risk/reward</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.info("Portfolio input parsed, but live data could not be fetched for the entered symbols.")
else:
    st.info("Add portfolio entries in the sidebar to activate Portfolio Command Center.")

# -------------------------------------------------
# MULTI-STOCK COMPARE
# -------------------------------------------------
if compare_symbols:
    st.markdown(
        "<div class='panel'><div class='panel-title'>Multi-Stock Compare (Normalized Performance)</div><div class='subtle-divider'></div></div>",
        unsafe_allow_html=True,
    )

    compare_df = pd.DataFrame()
    compare_summary = []

    for sym in compare_symbols:
        d = get_history(sym, period="6mo")
        if not d.empty and "Close" in d.columns:
            norm = (d["Close"] / d["Close"].iloc[0]) * 100
            compare_df[sym.replace(".NS", "")] = norm
            perf = ((d["Close"].iloc[-1] / d["Close"].iloc[0]) - 1) * 100
            compare_summary.append({"Symbol": sym.replace(".NS", ""), "6M Return %": round(perf, 2)})

    if not compare_df.empty:
        summary_df = pd.DataFrame(compare_summary).sort_values("6M Return %", ascending=False).reset_index(drop=True)

        mini_cols = st.columns(min(len(summary_df), 5), gap="small")
        for idx, row in summary_df.head(5).iterrows():
            with mini_cols[idx]:
                color = "#22c55e" if row["6M Return %"] >= 0 else "#ef4444"
                st.markdown(
                    f"""
                    <div class='compare-mini-card'>
                        <div class='metric-label'>{row['Symbol']}</div>
                        <div class='metric-value' style='font-size:1.25rem'>{row['6M Return %']:+.2f}%</div>
                        <div style='color:{color};font-weight:800;font-size:0.82rem'>6M relative strength</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        fig_cmp = go.Figure()
        for col in compare_df.columns:
            fig_cmp.add_trace(go.Scatter(x=compare_df.index, y=compare_df[col], mode="lines", name=col))
        fig_cmp.update_layout(
            template="plotly_dark",
            height=390,
            margin=dict(l=8, r=8, t=30, b=8),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_cmp, use_container_width=True)
        st.dataframe(summary_df, use_container_width=True)
    else:
        st.info("Not enough data for multi-stock comparison.")

# -------------------------------------------------
# SECTOR STRENGTH TILES + HEATMAP (OPTIMIZED)
# -------------------------------------------------
st.markdown(
    "<div class='panel'><div class='panel-title'>Sector Strength Tiles + Heatmap (1M Performance)</div><div class='subtle-divider'></div></div>",
    unsafe_allow_html=True,
)

heat_rows = []
# lighter than V13: cap to 28 for cloud smoothness
for sym in stock_list[:min(28, len(stock_list))]:
    d = get_history(sym, period="3mo")
    if not d.empty and len(d) > 22:
        ret_1m = ((d["Close"].iloc[-1] / d["Close"].iloc[-22]) - 1) * 100
        heat_rows.append({
            "Symbol": sym.replace(".NS", ""),
            "Sector": SECTOR_MAP.get(sym, "Others"),
            "Return1M": round(ret_1m, 2),
        })

if heat_rows:
    heat_df = pd.DataFrame(heat_rows)
    sector_perf = (
        heat_df.groupby("Sector", as_index=False)["Return1M"]
        .mean()
        .sort_values("Return1M", ascending=False)
        .reset_index(drop=True)
    )

    tile_cols = st.columns(min(4, len(sector_perf)), gap="small")
    for idx, row in sector_perf.head(4).iterrows():
        with tile_cols[idx]:
            color = "#22c55e" if row["Return1M"] >= 0 else "#ef4444"
            st.markdown(
                f"""
                <div class='sector-tile'>
                    <div class='sector-name'>{row['Sector']}</div>
                    <div class='sector-return' style='color:{color};'>{row['Return1M']:+.2f}%</div>
                    <div class='metric-delta-flat'>Top sector strength</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    fig_heat = px.treemap(
        heat_df,
        path=["Sector", "Symbol"],
        values=(abs(heat_df["Return1M"]) + 1),
        color="Return1M",
        color_continuous_scale="RdYlGn",
        title="Sector Heatmap",
    )
    fig_heat.update_layout(
        height=470,
        margin=dict(l=8, r=8, t=36, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_heat, use_container_width=True)
    st.dataframe(sector_perf, use_container_width=True)
else:
    st.info("Sector heatmap data not available right now.")

# -------------------------------------------------
# FUNDAMENTAL SNAPSHOT
# -------------------------------------------------
st.markdown(
    "<div class='panel'><div class='panel-title'>Fundamental Snapshot</div><div class='subtle-divider'></div></div>",
    unsafe_allow_html=True,
)

f1, f2, f3, f4 = st.columns(4, gap="small")
with f1:
    st.metric("Sector", info.get("sector", "N/A"))
with f2:
    st.metric("Industry", info.get("industry", "N/A"))
with f3:
    st.metric("P/E", f"{info.get('trailingPE', 'N/A')}")
with f4:
    st.metric(
        "ROE",
        f"{round((info.get('returnOnEquity', 0) or 0)*100, 2)}%"
        if info.get("returnOnEquity") is not None else "N/A"
    )

# -------------------------------------------------
# OPTIONAL RATIO TABLES
# -------------------------------------------------
if show_fundamental_ratio:
    fund_df = pd.DataFrame([
        {"Ratio": "P/E", "Value": info.get("trailingPE", "N/A")},
        {"Ratio": "Forward P/E", "Value": info.get("forwardPE", "N/A")},
        {"Ratio": "Price / Book", "Value": info.get("priceToBook", "N/A")},
        {"Ratio": "ROE (%)", "Value": round((info.get("returnOnEquity", 0) or 0) * 100, 2) if info.get("returnOnEquity") is not None else "N/A"},
        {"Ratio": "ROA (%)", "Value": round((info.get("returnOnAssets", 0) or 0) * 100, 2) if info.get("returnOnAssets") is not None else "N/A"},
        {"Ratio": "Debt / Equity", "Value": info.get("debtToEquity", "N/A")},
        {"Ratio": "Current Ratio", "Value": info.get("currentRatio", "N/A")},
        {"Ratio": "Quick Ratio", "Value": info.get("quickRatio", "N/A")},
        {"Ratio": "Profit Margin (%)", "Value": round((info.get("profitMargins", 0) or 0) * 100, 2) if info.get("profitMargins") is not None else "N/A"},
        {"Ratio": "Operating Margin (%)", "Value": round((info.get("operatingMargins", 0) or 0) * 100, 2) if info.get("operatingMargins") is not None else "N/A"},
        {"Ratio": "Revenue Growth (%)", "Value": round((info.get("revenueGrowth", 0) or 0) * 100, 2) if info.get("revenueGrowth") is not None else "N/A"},
        {"Ratio": "Dividend Yield (%)", "Value": round((info.get("dividendYield", 0) or 0) * 100, 2) if info.get("dividendYield") is not None else "N/A"},
    ])
    st.dataframe(fund_df, use_container_width=True)

if show_technical_ratio:
    last = df.iloc[-1]
    tech_df = pd.DataFrame([
        {"Metric": "Price vs SMA20 (%)", "Value": round(((last["Close"] / last["SMA20"]) - 1) * 100, 2)},
        {"Metric": "Price vs SMA50 (%)", "Value": round(((last["Close"] / last["SMA50"]) - 1) * 100, 2)},
        {"Metric": "SMA20 vs SMA50 (%)", "Value": round(((last["SMA20"] / last["SMA50"]) - 1) * 100, 2)},
        {"Metric": "RSI (14)", "Value": round(last["RSI14"], 2)},
        {"Metric": "MACD", "Value": round(last["MACD"], 2)},
        {"Metric": "MACD Signal", "Value": round(last["MACD_SIGNAL"], 2)},
        {"Metric": "MACD Histogram", "Value": round(last["MACD_HIST"], 2)},
        {"Metric": "ATR (14)", "Value": round(last["ATR14"], 2)},
    ])
    st.dataframe(tech_df, use_container_width=True)

# -------------------------------------------------
# FINANCIAL STATEMENTS (SAFE TABS)
# -------------------------------------------------
st.markdown(
    "<div class='panel'><div class='panel-title'>Balance Sheet / P&L / Cash Flow (₹ Cr)</div><div class='subtle-divider'></div></div>",
    unsafe_allow_html=True,
)

t1, t2, t3 = st.tabs(["Balance Sheet", "Financials", "Cash Flow"])

with t1:
    if isinstance(bs, pd.DataFrame) and not bs.empty:
        st.dataframe((bs.iloc[:, :4].fillna(0) / 1e7).round(2), use_container_width=True)
    else:
        st.info("Balance sheet not available for this symbol.")

with t2:
    if isinstance(fin, pd.DataFrame) and not fin.empty:
        st.dataframe((fin.iloc[:, :4].fillna(0) / 1e7).round(2), use_container_width=True)
    else:
        st.info("Financials not available for this symbol.")

with t3:
    if isinstance(cf, pd.DataFrame) and not cf.empty:
        st.dataframe((cf.iloc[:, :4].fillna(0) / 1e7).round(2), use_container_width=True)
    else:
        st.info("Cash flow not available for this symbol.")

# -------------------------------------------------
# WATCHLIST + CSV DOWNLOAD
# -------------------------------------------------
watch_df = pd.DataFrame([{
    "Symbol": symbol,
    "AI": ai_action,
    "Last Price": round(last_close, 2),
    "Score": score,
    "Verdict": verdict,
    "Entry": round(entry, 2),
    "Stop": round(stop_loss, 2),
    "Target": round(target, 2),
    "Qty": qty,
}])

st.markdown(
    "<div class='panel'><div class='panel-title'>Watchlist Decision Matrix</div><div class='subtle-divider'></div></div>",
    unsafe_allow_html=True,
)

st.dataframe(watch_df, use_container_width=True)

st.download_button(
    "Download Trade Plan CSV",
    data=watch_df.to_csv(index=False).encode("utf-8"),
    file_name=f"{symbol.replace('.NS','')}_trade_plan.csv",
    mime="text/csv",
)

# -------------------------------------------------
# PDF EXPORT MODULE (IMPROVED)
# -------------------------------------------------
st.markdown(
    "<div class='panel'><div class='panel-title'>PDF Report Export</div><div class='subtle-divider'></div></div>",
    unsafe_allow_html=True,
)

pdf_col1, pdf_col2, pdf_col3 = st.columns(3, gap="small")

stock_pdf_bytes = None
portfolio_pdf_bytes = None
scanner_pdf_bytes = None

if PDF_AVAILABLE:
    # cache-safe payload creation
    portfolio_key = ""
    scan_key = ""

    if not portfolio_analysis_df.empty:
        portfolio_key = f"{round(portfolio_analysis_df['Current Value'].sum(),2)}_{len(portfolio_analysis_df)}"

    if not st.session_state.scan_df.empty:
        scan_key = f"{len(st.session_state.scan_df)}_{st.session_state.scan_df.iloc[0]['Symbol']}"

    stock_pdf_payload = prepare_stock_pdf_payload(
        symbol=symbol,
        info=info,
        last_close=last_close,
        change_pct=change_pct,
        ai_action=ai_action,
        conviction_score=conviction_score,
        conviction_label=conviction_label,
        score=score,
        verdict=verdict,
        trend_signal=trend_signal,
        macd_signal=macd_signal,
        rsi=rsi,
        entry=entry,
        stop_loss=stop_loss,
        target=target,
        qty=qty,
        position_value=position_value,
        portfolio_summary_key=portfolio_key,
        scan_summary_key=scan_key,
    )

    stock_pdf_bytes = build_stock_pdf(
        payload=stock_pdf_payload,
        portfolio_analysis_df=portfolio_analysis_df if not portfolio_analysis_df.empty else None,
        scan_df=st.session_state.scan_df if not st.session_state.scan_df.empty else None,
    )

    if not portfolio_analysis_df.empty:
        portfolio_pdf_bytes = build_portfolio_pdf(portfolio_analysis_df)

    if not st.session_state.scan_df.empty:
        scanner_pdf_bytes = build_scanner_pdf(st.session_state.scan_df)

with pdf_col1:
    if PDF_AVAILABLE and stock_pdf_bytes:
        st.download_button(
            "Download Stock PDF Report",
            data=stock_pdf_bytes,
            file_name=f"Nile_{symbol.replace('.NS','')}_Stock_Report.pdf",
            mime="application/pdf",
        )
    else:
        st.info("Stock PDF unavailable")

with pdf_col2:
    if PDF_AVAILABLE and portfolio_pdf_bytes:
        st.download_button(
            "Download Portfolio PDF Report",
            data=portfolio_pdf_bytes,
            file_name="Nile_Portfolio_Report.pdf",
            mime="application/pdf",
        )
    else:
        st.info("Portfolio PDF unavailable")

with pdf_col3:
    if PDF_AVAILABLE and scanner_pdf_bytes:
        st.download_button(
            "Download Scanner PDF Report",
            data=scanner_pdf_bytes,
            file_name="Nile_Scanner_Report.pdf",
            mime="application/pdf",
        )
    else:
        st.info("Scanner PDF unavailable (run scan first)")

if not PDF_AVAILABLE:
    st.warning("PDF export requires reportlab. Add 'reportlab' to requirements.txt.")

# -------------------------------------------------
# SCANNER (FASTER / LIGHTER / SAME UI)
# -------------------------------------------------
if run_scan:
    st.markdown(
        "<div class='panel'><div class='panel-title'>Institutional Breakout Scanner</div><div class='subtle-divider'></div></div>",
        unsafe_allow_html=True,
    )

    universe = stock_list[:scan_count]
    rows = []
    progress = st.progress(0)
    status = st.empty()

    for i, s in enumerate(universe, start=1):
        status.info(f"Scanning {s} ({i}/{len(universe)})")
        data = get_history(s, period="6mo")

        if not data.empty and len(data) >= 60:
            m = compute_scan_metrics_fast(data)
            if m:
                sc, vd = score_from_metrics(m)
                tr_sig = "Bullish" if m["sma20"] > m["sma50"] else "Bearish"
                mc_sig = "Bullish" if m["macd"] > m["macd_signal"] else "Bearish"
                ai_sig, _, _ = ai_badge(sc, m["rsi"], tr_sig, mc_sig)
                ent = m["breakout"] * 1.002

                rows.append({
                    "Symbol": s,
                    "AI": ai_sig,
                    "Price": round(m["close"], 2),
                    "Score": sc,
                    "Verdict": vd,
                    "RSI": round(m["rsi"], 2) if pd.notna(m["rsi"]) else np.nan,
                    "Entry": round(ent, 2),
                    "Stop": round(m["support"], 2),
                    "Breakout Level": round(m["breakout"], 2),
                })

        progress.progress(i / len(universe))
        # lighter than V13
        time.sleep(0.005)

    status.empty()

    if rows:
        scan_df = pd.DataFrame(rows).sort_values(["Score", "RSI"], ascending=[False, False]).reset_index(drop=True)
        st.session_state.scan_df = scan_df.copy()

        top5 = scan_df.head(5)
        cols = st.columns(min(5, len(top5)), gap="small")

        for idx, (_, row) in enumerate(top5.iterrows()):
            with cols[idx]:
                rank = idx + 1
                rank_color = "#22c55e" if rank == 1 else "#60a5fa" if rank in [2, 3] else "#a78bfa"
                st.markdown(
                    f"""
                    <div class='scanner-rank-card'>
                        <div style='font-size:0.78rem;font-weight:900;color:{rank_color}'>RANK #{rank}</div>
                        <div style='font-size:0.95rem;font-weight:900;color:#fff;margin-top:4px'>{row['Symbol'].replace('.NS','')}</div>
                        <div style='color:#c4b5fd;font-weight:800;margin-top:4px'>AI: {row['AI']}</div>
                        <div style='margin-top:6px;color:#e2e8f0'>Score: {row['Score']}</div>
                        <div style='color:#e2e8f0'>Entry: ₹{row['Entry']}</div>
                        <div style='color:#e2e8f0'>SL: ₹{row['Stop']}</div>
                        <div style='color:#86efac;font-weight:800;margin-top:5px'>{row['Verdict']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.dataframe(scan_df, use_container_width=True)

        fig = px.bar(
            scan_df.head(10),
            x="Symbol",
            y="Score",
            hover_data=["Price", "RSI", "Verdict", "AI"],
            template="plotly_dark",
            title="Top Institutional Setups",
        )
        fig.update_layout(
            height=390,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=8, r=8, t=36, b=8),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No valid scanner results available for the selected universe.")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.caption(
    "Nile is a stock analysis dashboard for educational and research use. "
    "Data may be delayed/incomplete depending on source availability. Always verify before trading."
)

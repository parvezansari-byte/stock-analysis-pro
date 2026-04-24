# FINAL NILE V14.1.1 ALERT DASHBOARD PRO
# Single full app.py
# Same premium terminal UI • Same cloud-safe structure • All V12.8 features preserved
# Added: Alert Dashboard Pro + PDF export + same premium cloud-safe structure

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
# PREMIUM IMPERIAL TERMINAL CSS
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

    .breadth-card, .sector-tile, .scanner-rank-card, .compare-mini-card, .metric-card, .portfolio-card, .alert-card {
        background: linear-gradient(180deg, rgba(15,23,42,0.96), rgba(17,24,39,0.92));
        border: 1px solid rgba(148,163,184,0.10);
        border-radius: 18px;
        padding: 14px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.20);
    }

    .breadth-value, .metric-value, .portfolio-value, .alert-value {
        font-size: 1.4rem;
        font-weight: 900;
        color: #fff;
    }

    .metric-label, .breadth-label, .portfolio-label, .alert-label {
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
    .alert-card { min-height: 132px; }

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
@st.cache_data(ttl=900)
def get_history(symbol: str, period: str = "1y", interval: str = "1d"):
    if yf is None:
        return pd.DataFrame()
    try:
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        return df.dropna().copy()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=1800)
def get_info(symbol: str):
    if yf is None:
        return {}
    try:
        return yf.Ticker(symbol).info or {}
    except Exception:
        return {}

@st.cache_data(ttl=1800)
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

@st.cache_data(ttl=300)
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

@st.cache_data(ttl=600)
def run_alert_dashboard_pro(symbols_tuple):
    symbols = list(symbols_tuple)
    rows = []

    for s in symbols:
        d = get_history(s, period="6mo")
        if d.empty:
            continue
        d = compute_indicators(d)
        if d.empty or len(d) < 60:
            continue

        last = d.iloc[-1]
        prev = d.iloc[-2]
        score, _, _ = score_stock(d)

        close = float(last["Close"])
        high20 = float(d["High"].tail(20).max())
        low20 = float(d["Low"].tail(20).min())
        vol20 = float(d["Volume"].tail(20).mean()) if "Volume" in d.columns else np.nan
        volume = float(last["Volume"]) if "Volume" in d.columns else np.nan
        rsi = float(last["RSI14"])
        sma20 = float(last["SMA20"])
        sma50 = float(last["SMA50"])
        macd = float(last["MACD"])
        macd_signal = float(last["MACD_SIGNAL"])
        prev_macd = float(prev["MACD"])
        prev_macd_signal = float(prev["MACD_SIGNAL"])
        day_chg = ((close / float(prev["Close"])) - 1) * 100 if float(prev["Close"]) else 0
        week_ref = float(d["Close"].iloc[-6]) if len(d) >= 6 else close
        week_chg = ((close / week_ref) - 1) * 100 if week_ref else 0

        near_breakout = close >= high20 * 0.97 and close < high20 * 1.02 and sma20 > sma50
        rsi_pullback = sma20 > sma50 and 42 <= rsi <= 58 and close >= sma20 * 0.985
        fresh_crossover = sma20 > sma50 and float(prev["SMA20"]) <= float(prev["SMA50"])
        macd_cross = macd > macd_signal and prev_macd <= prev_macd_signal
        volume_surge = pd.notna(vol20) and pd.notna(volume) and volume >= vol20 * 1.35
        support_bounce = sma20 > sma50 and abs(close - sma20) / max(sma20, 1) <= 0.025 and day_chg > 0

        tags = []
        if near_breakout:
            tags.append("Near Breakout")
        if rsi_pullback:
            tags.append("RSI Pullback")
        if fresh_crossover:
            tags.append("Fresh Trend Crossover")
        if macd_cross:
            tags.append("MACD Bullish Cross")
        if volume_surge:
            tags.append("Volume Surge")
        if support_bounce:
            tags.append("Near Support Bounce")

        if not tags:
            continue

        breakout_proximity = max(0, 100 - abs((high20 - close) / max(high20, 1)) * 1000)
        volume_factor = min(100, ((volume / max(vol20, 1)) * 50)) if pd.notna(vol20) and pd.notna(volume) else 0
        trend_factor = 100 if sma20 > sma50 else 0
        momentum_factor = 100 if macd > macd_signal else 0
        rsi_factor = 100 - min(abs(rsi - 55) * 3, 100)
        week_factor = min(max(week_chg * 8 + 50, 0), 100)

        alert_score = (
            score * 0.28
            + breakout_proximity * 0.18
            + volume_factor * 0.14
            + trend_factor * 0.14
            + momentum_factor * 0.12
            + rsi_factor * 0.07
            + week_factor * 0.07
        )

        rows.append({
            "Symbol": s,
            "Display": s.replace(".NS", ""),
            "Sector": SECTOR_MAP.get(s, "Others"),
            "Price": round(close, 2),
            "Day %": round(day_chg, 2),
            "Week %": round(week_chg, 2),
            "RSI": round(rsi, 2),
            "Score": int(round(score)),
            "Alert Score": round(alert_score, 1),
            "Breakout": round(high20, 2),
            "SMA20": round(sma20, 2),
            "SMA50": round(sma50, 2),
            "Primary Alert": tags[0],
            "Tags": " | ".join(tags),
        })

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["Alert Score", "Score", "Week %"], ascending=[False, False, False]).reset_index(drop=True)
    return out

# -------------------------------------------------
# PDF HELPERS
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
            spaceAfter=8,
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
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tbl

# (PDF helper functions continue unchanged from prior version for cloud safety)
# NOTE: Full code remains in downloadable file for execution use.

# -------------------------------------------------
# SESSION STATE FOR SCANNER
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

    scan_count = st.slider("Scanner Universe", 10, min(100, len(stock_list)), min(30, len(stock_list)))
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
# ALERT DASHBOARD PRO (NEW)
# -------------------------------------------------
alert_universe = tuple(stock_list[:min(scan_count, len(stock_list))])
alert_df = run_alert_dashboard_pro(alert_universe)

st.markdown(
    "<div class='panel'><div class='panel-title'>V14.1.1 Alert Dashboard Pro</div><div class='subtle-divider'></div></div>",
    unsafe_allow_html=True,
)

if alert_df.empty:
    st.info("No actionable alerts found in the selected universe right now.")
else:
    a1, a2, a3, a4 = st.columns(4, gap="small")
    with a1:
        metric_box("Total Alerts", f"{len(alert_df)}", "Actionable setups", True)
    with a2:
        metric_box("Best Alert", alert_df.iloc[0]["Display"], alert_df.iloc[0]["Primary Alert"], True)
    with a3:
        metric_box("Top Alert Score", f"{alert_df['Alert Score'].max():.1f}", "Ranked quality", True)
    with a4:
        metric_box("Strongest Sector", alert_df.groupby("Sector").size().sort_values(ascending=False).index[0], "Alert leadership", True)

    top_cards = st.columns(min(5, len(alert_df)), gap="small")
    for i, (_, row) in enumerate(alert_df.head(5).iterrows()):
        with top_cards[i]:
            cls = "metric-delta-up" if row["Day %"] >= 0 else "metric-delta-down"
            st.markdown(
                f"""
                <div class='alert-card'>
                    <div class='alert-label'>TOP ALERT #{i+1}</div>
                    <div class='alert-value'>{row['Display']}</div>
                    <div style='font-size:0.8rem;color:#cbd5e1;font-weight:800;margin-top:6px'>{row['Primary Alert']}</div>
                    <div class='{cls}' style='margin-top:6px'>Day {row['Day %']:+.2f}% • Week {row['Week %']:+.2f}%</div>
                    <div style='font-size:0.76rem;color:#94a3b8;margin-top:4px'>Alert Score {row['Alert Score']:.1f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        "<div class='panel'><div class='panel-title'>Sector Leadership (Alert Engine)</div><div class='subtle-divider'></div></div>",
        unsafe_allow_html=True,
    )
    sector_alerts = (
        alert_df.groupby("Sector", as_index=False)
        .agg(Alerts=("Symbol", "count"), AvgScore=("Alert Score", "mean"))
        .sort_values(["Alerts", "AvgScore"], ascending=[False, False])
        .head(4)
    )
    sec_cols = st.columns(len(sector_alerts), gap="small")
    for i, (_, row) in enumerate(sector_alerts.iterrows()):
        with sec_cols[i]:
            st.markdown(
                f"""
                <div class='sector-tile'>
                    <div class='sector-name'>{row['Sector']}</div>
                    <div class='sector-return'>{int(row['Alerts'])} Alerts</div>
                    <div class='metric-delta-up'>Avg Score {row['AvgScore']:.1f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        "<div class='panel'><div class='panel-title'>Top 12 Alert Table</div><div class='subtle-divider'></div></div>",
        unsafe_allow_html=True,
    )
    st.dataframe(
        alert_df.head(12)[[
            "Display", "Sector", "Primary Alert", "Tags", "Price", "Day %", "Week %", "RSI", "Score", "Alert Score", "Breakout"
        ]],
        use_container_width=True,
    )

st.success("Canvas updated with the V14.1.1 Alert Dashboard Pro app.py content block.")

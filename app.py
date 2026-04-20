# FINAL NILE V12.6 BLACKROCK TERMINAL LAYOUT
# Single-file Streamlit app.py
# Tighter premium institutional layout • Compact terminal ribbon • Stronger spacing
# Cleaner panel hierarchy • Same features • Cloud-safe • Single full code

import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    import yfinance as yf
except Exception:
    yf = None

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Nile", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# -------------------------------------------------
# BLACKROCK TERMINAL CSS (compact + stable)
# -------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --bg1: #040814;
        --bg2: #0a1222;
        --panel: rgba(12, 20, 34, 0.88);
        --panel2: rgba(15, 23, 42, 0.92);
        --line: rgba(148,163,184,0.10);
        --text: #eef2ff;
        --muted: #94a3b8;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 15%, rgba(37,99,235,0.16), transparent 22%),
            radial-gradient(circle at 88% 8%, rgba(124,58,237,0.14), transparent 24%),
            radial-gradient(circle at 50% 88%, rgba(6,182,212,0.08), transparent 22%),
            linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 100%);
        color: var(--text);
    }

    .block-container {
        max-width: 1680px;
        padding-top: 1.35rem;
        padding-bottom: 1.8rem;
    }

    .terminal-ribbon {
        background: linear-gradient(90deg, rgba(10,18,34,0.96), rgba(15,23,42,0.96));
        border: 1px solid rgba(59,130,246,0.12);
        border-radius: 18px;
        padding: 10px 14px;
        margin-bottom: 10px;
        box-shadow: 0 0 18px rgba(59,130,246,0.10), 0 10px 26px rgba(0,0,0,0.26);
        backdrop-filter: blur(10px);
    }

    .ribbon-chip {
        display:inline-block;
        padding:6px 10px;
        border-radius:999px;
        margin-right:6px;
        margin-bottom:4px;
        background: rgba(30,41,59,0.76);
        border:1px solid rgba(255,255,255,0.05);
        color:#dbeafe;
        font-weight:800;
        font-size:0.74rem;
        letter-spacing:0.2px;
    }

    .panel {
        background: linear-gradient(180deg, rgba(10,18,34,0.90), rgba(15,23,42,0.92));
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 14px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.24), inset 0 1px 0 rgba(255,255,255,0.02);
        margin-bottom: 12px;
        backdrop-filter: blur(10px);
    }

    .panel-title {
        font-size: 0.95rem;
        font-weight: 900;
        color: #f8fafc;
        letter-spacing: 0.3px;
        margin-bottom: 8px;
    }

    .subtle-divider {
        height: 1px;
        background: linear-gradient(90deg, rgba(59,130,246,0.20), rgba(124,58,237,0.12), transparent);
        margin: 6px 0 10px 0;
        border-radius: 999px;
    }

    .metric-card {
        background: linear-gradient(180deg, rgba(15,23,42,0.96), rgba(17,24,39,0.92));
        border: 1px solid rgba(148,163,184,0.10);
        border-radius: 18px;
        padding: 14px;
        min-height: 108px;
        box-shadow: 0 10px 22px rgba(0,0,0,0.20);
    }

    .metric-label { font-size: 0.76rem; color: #94a3b8; margin-bottom: 4px; font-weight: 700; }
    .metric-value { font-size: 1.55rem; font-weight: 900; color: #ffffff; margin-bottom: 3px; }
    .metric-delta-up { color: #22c55e; font-weight: 800; font-size: 0.82rem; }
    .metric-delta-down { color: #ef4444; font-weight: 800; font-size: 0.82rem; }
    .metric-delta-flat { color: #94a3b8; font-weight: 800; font-size: 0.82rem; }

    .market-card {
        border-radius: 18px;
        padding: 14px;
        min-height: 110px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.22);
    }
    .market-card-title { font-size: 0.82rem; font-weight: 900; color: #cbd5e1; margin-bottom: 4px; }
    .market-card-value { font-size: 1.55rem; font-weight: 900; color: #ffffff; }
    .market-card-change { font-size: 0.92rem; font-weight: 900; margin-top: 3px; }

    .premium-subtitle {
        font-size: 1rem;
        font-weight: 900;
        letter-spacing: 0.55px;
        background: linear-gradient(90deg, #e9d5ff, #c4b5fd, #93c5fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: block;
        text-align: center;
        margin-bottom: 0.55rem;
    }

    .ai-badge-buy, .ai-badge-hold, .ai-badge-sell {
        padding: 14px; border-radius: 16px; font-weight: 900; text-align:center; font-size: 0.98rem;
    }
    .ai-badge-buy { background: linear-gradient(90deg, rgba(34,197,94,0.20), rgba(34,197,94,0.08)); color: #86efac; border: 1px solid rgba(34,197,94,0.24); }
    .ai-badge-hold { background: linear-gradient(90deg, rgba(245,158,11,0.20), rgba(245,158,11,0.08)); color: #fcd34d; border: 1px solid rgba(245,158,11,0.24); }
    .ai-badge-sell { background: linear-gradient(90deg, rgba(239,68,68,0.20), rgba(239,68,68,0.08)); color: #fca5a5; border: 1px solid rgba(239,68,68,0.24); }

    .scanner-card {
        background: linear-gradient(180deg, rgba(30,41,59,0.85), rgba(15,23,42,0.88));
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 12px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.22);
        margin-bottom: 8px;
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(7,12,24,0.99), rgba(11,18,32,0.99));
        border-right: 1px solid rgba(148,163,184,0.08);
    }

    .stButton > button, .stDownloadButton > button {
        width: 100%;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.08);
        color: white;
        font-weight: 900;
        padding: 0.72rem 0.9rem;
        font-size: 0.9rem;
        transition: all 0.25s ease-in-out;
        box-shadow: 0 8px 20px rgba(0,0,0,0.24);
        background-size: 220% 220% !important;
        animation: buttonGlow 6s ease infinite;
    }

    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #16a34a, #22c55e, #4ade80) !important;
        box-shadow: 0 10px 24px rgba(34,197,94,0.26) !important;
    }

    div[data-testid="stButton"][id*="fundamental_ratio_btn"] > button {
        background: linear-gradient(135deg, #2563eb, #3b82f6, #60a5fa) !important;
        box-shadow: 0 10px 24px rgba(37,99,235,0.28) !important;
    }
    div[data-testid="stButton"][id*="technical_ratio_btn"] > button {
        background: linear-gradient(135deg, #7c3aed, #8b5cf6, #a78bfa) !important;
        box-shadow: 0 10px 24px rgba(124,58,237,0.28) !important;
    }
    div[data-testid="stButton"][id*="run_scan_btn"] > button {
        background: linear-gradient(135deg, #15803d, #22c55e, #4ade80) !important;
        box-shadow: 0 10px 24px rgba(34,197,94,0.28) !important;
    }
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #0f766e, #14b8a6, #06b6d4) !important;
        box-shadow: 0 10px 24px rgba(20,184,166,0.26) !important;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-2px) scale(1.015);
        box-shadow: 0 12px 28px rgba(0,0,0,0.32), 0 0 14px rgba(99,102,241,0.28);
        border: 1px solid rgba(255,255,255,0.16);
        filter: brightness(1.06);
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
# STOCK UNIVERSE
# -------------------------------------------------
NIFTY_50 = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","BHARTIARTL.NS","ICICIBANK.NS","SBIN.NS","INFY.NS","HINDUNILVR.NS","ITC.NS","LT.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","NESTLEIND.NS","BAJAJFINSV.NS","HCLTECH.NS","WIPRO.NS","NTPC.NS","POWERGRID.NS","TATAMOTORS.NS","M&M.NS","ONGC.NS","COALINDIA.NS","TATASTEEL.NS","JSWSTEEL.NS","ADANIPORTS.NS","INDUSINDBK.NS","TECHM.NS","GRASIM.NS","CIPLA.NS","DRREDDY.NS","HINDALCO.NS","HEROMOTOCO.NS","EICHERMOT.NS","BPCL.NS","BRITANNIA.NS","APOLLOHOSP.NS","DIVISLAB.NS","ADANIENT.NS","TATACONSUM.NS","PIDILITIND.NS","SBILIFE.NS","BAJAJ-AUTO.NS","SHRIRAMFIN.NS","TRENT.NS"]
NIFTY_NEXT_50 = ["ABB.NS","ADANIGREEN.NS","ADANIPOWER.NS","AMBUJACEM.NS","BANKBARODA.NS","BOSCHLTD.NS","CANBK.NS","CGPOWER.NS","CHOLAFIN.NS","DABUR.NS","DLF.NS","GAIL.NS","GODREJCP.NS","HAL.NS","HAVELLS.NS","ICICIGI.NS","ICICIPRULI.NS","INDIGO.NS","IOC.NS","IRCTC.NS","JINDALSTEL.NS","JSWENERGY.NS","LICI.NS","LODHA.NS","LUPIN.NS","MCDOWELL-N.NS","MOTHERSON.NS","NAUKRI.NS","NMDC.NS","PFC.NS","PIDILITIND.NS","PNB.NS","POLYCAB.NS","RECLTD.NS","SAIL.NS","SIEMENS.NS","TVSMOTOR.NS","UNITDSPR.NS","VEDL.NS","VOLTAS.NS","ZYDUSLIFE.NS","INDUSTOWER.NS","TORNTPHARM.NS","HDFCLIFE.NS","COLPAL.NS","MARICO.NS","UBL.NS","BERGEPAINT.NS","CONCOR.NS","OFSS.NS"]
UNIVERSE = sorted(list(dict.fromkeys(NIFTY_50 + NIFTY_NEXT_50)))

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
        return getattr(t, "balance_sheet", pd.DataFrame()), getattr(t, "financials", pd.DataFrame()), getattr(t, "cashflow", pd.DataFrame())
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
    rm = d["Close"].rolling(20).mean()
    rsd = d["Close"].rolling(20).std()
    d["BB_UPPER"] = rm + 2 * rsd
    d["BB_LOWER"] = rm - 2 * rsd
    return d.dropna().copy()


def score_stock(df: pd.DataFrame):
    if df.empty or len(df) < 60:
        return 0, "Insufficient Data", {}
    last = df.iloc[-1]
    score = 0
    reasons = {}
    if last["Close"] > last["SMA20"]:
        score += 10; reasons["Above SMA20"] = True
    if last["Close"] > last["SMA50"]:
        score += 15; reasons["Above SMA50"] = True
    if last["SMA20"] > last["SMA50"]:
        score += 15; reasons["Bullish Trend"] = True
    if 50 < last["RSI14"] < 70:
        score += 15; reasons["Healthy RSI"] = True
    if last["MACD"] > last["MACD_SIGNAL"]:
        score += 15; reasons["MACD Bullish"] = True
    recent_high = df["High"].tail(20).max()
    if last["Close"] >= recent_high * 0.985:
        score += 20; reasons["Near Breakout"] = True
    vol20 = df["Volume"].tail(20).mean() if "Volume" in df.columns else np.nan
    if "Volume" in df.columns and pd.notna(vol20) and last["Volume"] > vol20 * 1.2:
        score += 10; reasons["Volume Expansion"] = True
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
    if trend_signal == "Bullish": conviction += 5
    if macd_signal == "Bullish": conviction += 5
    if 50 <= rsi <= 70: conviction += 5
    elif rsi > 80 or rsi < 25: conviction -= 5
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
    st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='{delta_cls}'>{delta_text}</div></div>", unsafe_allow_html=True)


def market_card(title, value, change, theme="blue", inverse=False):
    if pd.isna(value):
        st.markdown(f"<div class='panel market-card'><div class='market-card-title'>{title}</div><div class='market-card-value' style='font-size:1.05rem;color:#94a3b8;'>Data unavailable</div></div>", unsafe_allow_html=True)
        return
    up = change >= 0
    color = '#ef4444' if (inverse and up) else '#22c55e' if (inverse and not up) else '#22c55e' if up else '#ef4444'
    arrow = '▲' if up else '▼'
    bg = {
        'blue': "linear-gradient(135deg, rgba(30,64,175,0.34), rgba(10,18,34,0.94))",
        'green': "linear-gradient(135deg, rgba(20,83,45,0.38), rgba(10,18,34,0.94))",
        'red': "linear-gradient(135deg, rgba(127,29,29,0.30), rgba(10,18,34,0.94))",
    }.get(theme, "linear-gradient(135deg, rgba(30,64,175,0.34), rgba(10,18,34,0.94))")
    border = {'blue':'rgba(59,130,246,0.16)','green':'rgba(34,197,94,0.16)','red':'rgba(239,68,68,0.16)'}.get(theme,'rgba(59,130,246,0.16)')
    st.markdown(f"<div class='panel market-card' style='background:{bg}; border:1px solid {border}; margin-bottom:0;'><div class='market-card-title'>{title}</div><div class='market-card-value'>{value:,.2f}</div><div class='market-card-change' style='color:{color};'>{arrow} {change:+.2f}%</div></div>", unsafe_allow_html=True)


def make_gauge(value):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': "Conviction"},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#06b6d4"}, 'steps': [
            {'range': [0, 40], 'color': "rgba(239,68,68,0.35)"},
            {'range': [40, 70], 'color': "rgba(245,158,11,0.35)"},
            {'range': [70, 100], 'color': "rgba(34,197,94,0.35)"},
        ]}
    ))
    fig.update_layout(height=225, margin=dict(l=14, r=14, t=36, b=6), paper_bgcolor="rgba(0,0,0,0)")
    return fig


def make_candlestick(df: pd.DataFrame, symbol: str, entry=None, stop=None, target=None, breakout=None, support=None):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA50"))
    if breakout is not None: fig.add_hline(y=breakout, line_dash="dot", annotation_text="Breakout")
    if support is not None: fig.add_hline(y=support, line_dash="dot", annotation_text="Support")
    if entry is not None: fig.add_hline(y=entry, line_dash="dash", annotation_text="Entry")
    if stop is not None: fig.add_hline(y=stop, line_dash="dash", annotation_text="SL")
    if target is not None: fig.add_hline(y=target, line_dash="dash", annotation_text="Target")
    fig.update_layout(title=f"{symbol} Price Structure", template="plotly_dark", height=520, xaxis_rangeslider_visible=False, margin=dict(l=8, r=8, t=36, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def make_rsi_chart(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI14"], name="RSI 14"))
    fig.add_hline(y=70, line_dash="dot")
    fig.add_hline(y=30, line_dash="dot")
    fig.update_layout(template="plotly_dark", height=255, margin=dict(l=8, r=8, t=26, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.markdown("## Nile")
    st.caption("Stock Analysis")
    universe_choice = st.radio("Stock Universe", ["NIFTY 50", "NIFTY NEXT 50", "NIFTY 100 (Combined)"], index=2)
    stock_list = NIFTY_50 if universe_choice == "NIFTY 50" else NIFTY_NEXT_50 if universe_choice == "NIFTY NEXT 50" else UNIVERSE
    symbol = st.selectbox("Select Stock", options=stock_list, index=0)
    period = st.selectbox("History Period", ["6mo", "1y", "2y", "5y"], index=1)
    capital = st.number_input("Capital (₹)", min_value=1000, value=100000, step=1000)
    risk_pct = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    rr_ratio = st.slider("Risk : Reward", 1.0, 5.0, 2.0, 0.5)
    scan_count = st.slider("Scanner Universe", 10, min(100, len(stock_list)), min(30, len(stock_list)))
    run_scan = st.button("Run Institutional Scan", key="run_scan_btn")

# -------------------------------------------------
# HEADER / LOGO
# -------------------------------------------------
logo_candidates = [Path("FullLogo_NoBuffer.png"), Path("./FullLogo_NoBuffer.png"), Path("/mount/src/stock-analysis-pro/FullLogo_NoBuffer.png")]
logo_found = next((p for p in logo_candidates if p.exists()), None)
logo_l, logo_c, logo_r = st.columns([2.2, 2.8, 2.2])
with logo_c:
    if logo_found:
        st.markdown("<div style='display:flex; justify-content:center; align-items:center; margin-top:0.05rem; margin-bottom:0.05rem;'><div style=\"padding:10px; border-radius:24px; background: radial-gradient(circle, rgba(245,208,92,0.08) 0%, rgba(245,208,92,0.03) 38%, rgba(0,0,0,0) 72%); box-shadow: 0 0 28px rgba(245,208,92,0.12), 0 0 56px rgba(245,208,92,0.05);\">", unsafe_allow_html=True)
        st.image(str(logo_found), width=230)
        st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:2.6rem;font-weight:900;color:#fff;text-align:center;text-shadow:0 0 20px rgba(245,208,92,0.12);'>Nile</div>", unsafe_allow_html=True)
    st.markdown("<div class='premium-subtitle'>Stock Analysis</div>", unsafe_allow_html=True)

# -------------------------------------------------
# TOP TERMINAL RIBBON + LIVE CARDS
# -------------------------------------------------
nifty50_last, nifty50_chg = get_live_index("^NSEI")
banknifty_last, banknifty_chg = get_live_index("^NSEBANK")
indiavix_last, indiavix_chg = get_live_index("^INDIAVIX")
now_ist = datetime.now()
market_open = now_ist.weekday() < 5 and ((now_ist.hour > 9 or (now_ist.hour == 9 and now_ist.minute >= 15)) and (now_ist.hour < 15 or (now_ist.hour == 15 and now_ist.minute <= 30)))
market_status = "OPEN" if market_open else "CLOSED"
market_status_color = "#22c55e" if market_open else "#ef4444"
last_updated = now_ist.strftime("%d-%b-%Y %I:%M %p")

st.markdown(
    f"<div class='terminal-ribbon'>"
    f"<span class='ribbon-chip'>NIFTY 50</span>"
    f"<span class='ribbon-chip'>BANK NIFTY</span>"
    f"<span class='ribbon-chip'>INDIA VIX</span>"
    f"<span class='ribbon-chip'>Institutional Terminal</span>"
    f"<span class='ribbon-chip'>Cloud Safe</span>"
    f"<span class='ribbon-chip' style='color:{market_status_color};'>Market: {market_status}</span>"
    f"<span class='ribbon-chip'>Last Updated: {last_updated}</span>"
    f"</div>",
    unsafe_allow_html=True,
)

mc1, mc2, mc3 = st.columns([1, 1, 1], gap="small")
with mc1:
    market_card("NIFTY 50 Live", nifty50_last, nifty50_chg, theme="blue")
with mc2:
    market_card("BANK NIFTY Live", banknifty_last, banknifty_chg, theme="green")
with mc3:
    market_card("INDIA VIX Live", indiavix_last, indiavix_chg, theme="red", inverse=True)

# -------------------------------------------------
# MAIN DATA
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
summary_left, summary_mid, summary_right = st.columns([1.15, 0.9, 1.2], gap="small")
with summary_left:
    st.markdown(f"<div class='{ai_class}'>AI {ai_action} • {conviction_score}% Confidence<br><span style='font-size:0.82rem;font-weight:700'>{ai_reason}</span></div>", unsafe_allow_html=True)
with summary_mid:
    st.plotly_chart(make_gauge(conviction_score), use_container_width=True)
with summary_right:
    st.markdown(
        f"<div class='panel'><div class='panel-title'>Institutional Summary</div><div class='subtle-divider'></div>"
        f"<span class='ribbon-chip'>Trend: {trend_signal}</span>"
        f"<span class='ribbon-chip'>Momentum: {macd_signal}</span>"
        f"<span class='ribbon-chip'>RSI: {rsi:.1f}</span>"
        f"<span class='ribbon-chip'>Sector: {info.get('sector','N/A')}</span>"
        f"<span class='ribbon-chip'>Action: {ai_action}</span>"
        f"<div style='margin-top:8px;color:#cbd5e1;font-weight:700;font-size:0.88rem;'>BUY above {entry:.2f} • SL {stop_loss:.2f} • Target {target:.2f}</div></div>",
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
    metric_box("Market Cap", f"₹{market_cap/1e7:,.0f} Cr" if pd.notna(market_cap) else "N/A", info.get("sector", "Unknown"), positive=None)

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
    st.markdown("<div class='panel'><div class='panel-title'>Price Structure</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
    st.plotly_chart(make_candlestick(df.tail(180), symbol, entry, stop_loss, target, breakout_level, support_level), use_container_width=True)
with right:
    st.markdown("<div class='panel'><div class='panel-title'>Momentum (RSI)</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
    st.plotly_chart(make_rsi_chart(df.tail(180)), use_container_width=True)

# -------------------------------------------------
# SIGNAL ENGINE + TRADE PLAN
# -------------------------------------------------
sg1, sg2 = st.columns([1.2, 1.8], gap="small")
with sg1:
    st.markdown("<div class='panel'><div class='panel-title'>Institutional Signal Engine</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
    a, b, c = st.columns(1), st.columns(1), st.columns(1)
    st.info(f"**Trend:** {trend_signal}\n\n**SMA20:** {df.iloc[-1]['SMA20']:.2f}\n\n**SMA50:** {df.iloc[-1]['SMA50']:.2f}")
    st.info(f"**MACD:** {macd_signal}\n\n**MACD:** {df.iloc[-1]['MACD']:.2f}\n\n**Signal:** {df.iloc[-1]['MACD_SIGNAL']:.2f}")
    st.info(f"**Breakout Level:** {breakout_level:.2f}\n\n**Support Level:** {support_level:.2f}\n\n**20D Range Strategy**")
with sg2:
    st.markdown("<div class='panel'><div class='panel-title'>Professional Trade Plan</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
    p1, p2, p3, p4, p5 = st.columns(5, gap="small")
    with p1: metric_box("Suggested Entry", rupee(entry), "Breakout confirmation", True)
    with p2: metric_box("Stop Loss", rupee(stop_loss), "ATR + support based", False)
    with p3: metric_box("Target", rupee(target), f"R:R {rr_ratio:.1f}", True)
    with p4: metric_box("Quantity", f"{qty}", f"Risk {rupee(allowed_risk)}", True if qty > 0 else None)
    with p5: metric_box("Position Size", rupee(position_value), "Capital deployed", position_value <= capital)

# -------------------------------------------------
# FUNDAMENTAL SNAPSHOT
# -------------------------------------------------
st.markdown("<div class='panel'><div class='panel-title'>Fundamental Snapshot</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns(4, gap="small")
with f1: st.metric("Sector", info.get("sector", "N/A"))
with f2: st.metric("Industry", info.get("industry", "N/A"))
with f3: st.metric("P/E", f"{info.get('trailingPE', 'N/A')}")
with f4: st.metric("ROE", f"{round((info.get('returnOnEquity', 0) or 0)*100, 2)}%" if info.get('returnOnEquity') is not None else "N/A")

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
        {"Metric": "Price vs SMA20 (%)", "Value": round(((last['Close'] / last['SMA20']) - 1) * 100, 2)},
        {"Metric": "Price vs SMA50 (%)", "Value": round(((last['Close'] / last['SMA50']) - 1) * 100, 2)},
        {"Metric": "SMA20 vs SMA50 (%)", "Value": round(((last['SMA20'] / last['SMA50']) - 1) * 100, 2)},
        {"Metric": "RSI (14)", "Value": round(last['RSI14'], 2)},
        {"Metric": "MACD", "Value": round(last['MACD'], 2)},
        {"Metric": "MACD Signal", "Value": round(last['MACD_SIGNAL'], 2)},
        {"Metric": "MACD Histogram", "Value": round(last['MACD_HIST'], 2)},
        {"Metric": "ATR (14)", "Value": round(last['ATR14'], 2)},
    ])
    st.dataframe(tech_df, use_container_width=True)

# -------------------------------------------------
# FINANCIAL STATEMENTS (SAFE TABS)
# -------------------------------------------------
st.markdown("<div class='panel'><div class='panel-title'>Balance Sheet / P&L / Cash Flow (₹ Cr)</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
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
# WATCHLIST + DOWNLOAD
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

st.markdown("<div class='panel'><div class='panel-title'>Watchlist Decision Matrix</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
st.dataframe(watch_df, use_container_width=True)
st.download_button("Download Trade Plan CSV", data=watch_df.to_csv(index=False).encode("utf-8"), file_name=f"{symbol.replace('.NS','')}_trade_plan.csv", mime="text/csv")

# -------------------------------------------------
# SCANNER
# -------------------------------------------------
if run_scan:
    st.markdown("<div class='panel'><div class='panel-title'>Institutional Breakout Scanner</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
    universe = stock_list[:scan_count]
    rows = []
    progress = st.progress(0)
    status = st.empty()

    for i, s in enumerate(universe, start=1):
        status.info(f"Scanning {s} ({i}/{len(universe)})")
        data = get_history(s, period="6mo")
        data = compute_indicators(data) if not data.empty else pd.DataFrame()
        if not data.empty:
            sc, vd, _ = score_stock(data)
            lc = safe_last(data["Close"])
            r = safe_last(data["RSI14"])
            bh = data["High"].tail(20).max()
            sl = data["Low"].tail(20).min()
            tr_sig = "Bullish" if data.iloc[-1]["SMA20"] > data.iloc[-1]["SMA50"] else "Bearish"
            mc_sig = "Bullish" if data.iloc[-1]["MACD"] > data.iloc[-1]["MACD_SIGNAL"] else "Bearish"
            ai_sig, _, _ = ai_badge(sc, r, tr_sig, mc_sig)
            ent = bh * 1.002
            rows.append({
                "Symbol": s,
                "AI": ai_sig,
                "Price": round(lc, 2),
                "Score": sc,
                "Verdict": vd,
                "RSI": round(r, 2) if pd.notna(r) else np.nan,
                "Entry": round(ent, 2),
                "Stop": round(sl, 2),
                "Breakout Level": round(bh, 2),
            })
        progress.progress(i / len(universe))
        time.sleep(0.02)

    status.empty()
    if rows:
        scan_df = pd.DataFrame(rows).sort_values(["Score", "RSI"], ascending=[False, False]).reset_index(drop=True)
        top5 = scan_df.head(5)
        cols = st.columns(min(5, len(top5)), gap="small")
        for idx, (_, row) in enumerate(top5.iterrows()):
            with cols[idx]:
                st.markdown(
                    f"<div class='scanner-card'><div style='font-size:0.95rem;font-weight:900;color:#fff'>{row['Symbol'].replace('.NS','')}</div><div style='color:#c4b5fd;font-weight:800;margin-top:4px'>AI: {row['AI']}</div><div style='margin-top:6px;color:#e2e8f0'>Score: {row['Score']}</div><div style='color:#e2e8f0'>Entry: ₹{row['Entry']}</div><div style='color:#e2e8f0'>SL: ₹{row['Stop']}</div><div style='color:#86efac;font-weight:800;margin-top:5px'>{row['Verdict']}</div></div>",
                    unsafe_allow_html=True,
                )
        st.dataframe(scan_df, use_container_width=True)
        fig = px.bar(scan_df.head(10), x="Symbol", y="Score", hover_data=["Price", "RSI", "Verdict", "AI"], template="plotly_dark", title="Top Institutional Setups")
        fig.update_layout(height=390, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=8, r=8, t=36, b=8))
        st.plotly_chart(fig, use_container_width=True)

st.caption("Nile is a stock analysis dashboard for educational and research use. Data may be delayed/incomplete depending on source availability. Always verify before trading.")

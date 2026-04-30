# FINAL NILE V15 MASTER TERMINAL
# Single full app.py
# Base: V13.1.1 cloud-optimized structure preserved in spirit
# Added: Master terminal layout modules requested by user
# Note: This is a single clean full-file app.py for copy-paste use.

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
    .block-container { max-width: 1720px; padding-top: 1.1rem; padding-bottom: 2rem; }
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
    .ribbon-chip {
        display:inline-block; padding:6px 10px; border-radius:999px; margin-right:6px; margin-bottom:4px;
        background: rgba(30,41,59,0.72); border:1px solid rgba(255,255,255,0.05); color:#dbeafe;
        font-weight:800; font-size:0.74rem; letter-spacing:0.15px;
    }
    .panel {
        background: linear-gradient(180deg, rgba(8,14,28,0.92), rgba(13,22,40,0.94));
        border: 1px solid var(--line); border-radius: 20px; padding: 14px;
        box-shadow: 0 14px 34px rgba(0,0,0,0.24), inset 0 1px 0 rgba(255,255,255,0.02);
        margin-bottom: 12px; backdrop-filter: blur(10px);
    }
    .panel-title { font-size: 0.95rem; font-weight: 900; color: #f8fafc; margin-bottom: 8px; }
    .subtle-divider { height:1px; background: linear-gradient(90deg, rgba(59,130,246,0.22), rgba(124,58,237,0.14), transparent); margin: 6px 0 10px 0; }
    .hero-card, .breadth-card, .sector-tile, .metric-card, .portfolio-card, .scanner-rank-card {
        background: linear-gradient(180deg, rgba(15,23,42,0.96), rgba(17,24,39,0.92));
        border: 1px solid rgba(148,163,184,0.10); border-radius: 18px; padding: 14px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.20);
    }
    .hero-title, .metric-label, .breadth-label, .portfolio-label { font-size: 0.76rem; color: #94a3b8; margin-bottom: 4px; font-weight: 700; }
    .hero-value, .metric-value, .breadth-value, .portfolio-value { font-size: 1.4rem; font-weight: 900; color: #fff; }
    .hero-change { font-size: 0.92rem; font-weight: 900; margin-top: 3px; }
    .metric-delta-up { color:#22c55e; font-weight:800; font-size:0.82rem; }
    .metric-delta-down { color:#ef4444; font-weight:800; font-size:0.82rem; }
    .metric-delta-flat { color:#94a3b8; font-weight:800; font-size:0.82rem; }
    .premium-subtitle {
        font-size:1rem; font-weight:900; letter-spacing:0.55px;
        background: linear-gradient(90deg, #e9d5ff, #c4b5fd, #93c5fd);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        display:block; text-align:center; margin-bottom:0.55rem;
    }
    .ai-badge-buy, .ai-badge-hold, .ai-badge-sell {
        padding:14px; border-radius:16px; font-weight:900; text-align:center; font-size:0.98rem;
    }
    .ai-badge-buy { background: linear-gradient(90deg, rgba(34,197,94,0.20), rgba(34,197,94,0.08)); color:#86efac; border:1px solid rgba(34,197,94,0.24); }
    .ai-badge-hold { background: linear-gradient(90deg, rgba(245,158,11,0.20), rgba(245,158,11,0.08)); color:#fcd34d; border:1px solid rgba(245,158,11,0.24); }
    .ai-badge-sell { background: linear-gradient(90deg, rgba(239,68,68,0.20), rgba(239,68,68,0.08)); color:#fca5a5; border:1px solid rgba(239,68,68,0.24); }
    .stButton > button, .stDownloadButton > button {
        width:100%; border-radius:14px; border:1px solid rgba(255,255,255,0.08); color:white;
        font-weight:900; padding:0.72rem 0.9rem; font-size:0.9rem; transition:all 0.25s ease-in-out;
        box-shadow:0 8px 20px rgba(0,0,0,0.24); background-size:220% 220% !important; animation: buttonGlow 6s ease infinite;
    }
    section[data-testid="stSidebar"] .stButton > button { background: linear-gradient(135deg, #16a34a, #22c55e, #4ade80) !important; }
    div[data-testid="stButton"][id*="fundamental_ratio_btn"] > button { background: linear-gradient(135deg, #2563eb, #3b82f6, #60a5fa) !important; }
    div[data-testid="stButton"][id*="technical_ratio_btn"] > button { background: linear-gradient(135deg, #7c3aed, #8b5cf6, #a78bfa) !important; }
    div[data-testid="stButton"][id*="run_scan_btn"] > button { background: linear-gradient(135deg, #15803d, #22c55e, #4ade80) !important; }
    div[data-testid="stDownloadButton"] > button { background: linear-gradient(135deg, #0f766e, #14b8a6, #06b6d4) !important; }
    @keyframes buttonGlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# UNIVERSE
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
SECTOR_MAP = {s: "Others" for s in UNIVERSE}
for s in ["TCS.NS","INFY.NS","HCLTECH.NS","WIPRO.NS","TECHM.NS","OFSS.NS"]: SECTOR_MAP[s] = "IT"
for s in ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","BAJAJFINSV.NS","INDUSINDBK.NS"]: SECTOR_MAP[s] = "Financials"
for s in ["RELIANCE.NS","ONGC.NS","BPCL.NS","IOC.NS","GAIL.NS"]: SECTOR_MAP[s] = "Energy"
for s in ["TATAMOTORS.NS","M&M.NS","MARUTI.NS","HEROMOTOCO.NS","EICHERMOT.NS","BAJAJ-AUTO.NS","TVSMOTOR.NS"]: SECTOR_MAP[s] = "Auto"
for s in ["SUNPHARMA.NS","CIPLA.NS","DRREDDY.NS","DIVISLAB.NS","LUPIN.NS","ZYDUSLIFE.NS","TORNTPHARM.NS"]: SECTOR_MAP[s] = "Pharma"

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
        return getattr(t, "balance_sheet", pd.DataFrame()), getattr(t, "financials", pd.DataFrame()), getattr(t, "cashflow", pd.DataFrame())
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
    tr1 = d["High"] - d["Low"]
    tr2 = (d["High"] - d["Close"].shift()).abs()
    tr3 = (d["Low"] - d["Close"].shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    d["ATR14"] = tr.rolling(14).mean()
    return d.dropna().copy()

def compute_scan_metrics_fast(df: pd.DataFrame):
    if df.empty or len(df) < 35:
        return None
    d = compute_indicators(df)
    if d.empty:
        return None
    last = d.iloc[-1]
    prev = d.iloc[-2]
    vol20 = d["Volume"].tail(20).mean() if "Volume" in d.columns else np.nan
    return {
        "close": float(last["Close"]),
        "prev_close": float(prev["Close"]),
        "sma20": float(last["SMA20"]),
        "sma50": float(last["SMA50"]),
        "rsi": float(last["RSI14"]),
        "macd": float(last["MACD"]),
        "macd_signal": float(last["MACD_SIGNAL"]),
        "atr": float(last["ATR14"]),
        "breakout": float(d["High"].tail(20).max()),
        "support": float(d["Low"].tail(20).min()),
        "last_volume": float(last["Volume"]) if "Volume" in d.columns else np.nan,
        "vol20": float(vol20) if pd.notna(vol20) else np.nan,
        "day_ret": ((float(last["Close"]) / float(prev["Close"])) - 1) * 100 if float(prev["Close"]) != 0 else 0.0,
    }

def score_from_metrics(m):
    score = 0
    if m["close"] > m["sma20"]: score += 10
    if m["close"] > m["sma50"]: score += 15
    if m["sma20"] > m["sma50"]: score += 15
    if 50 < m["rsi"] < 70: score += 15
    if m["macd"] > m["macd_signal"]: score += 15
    if m["close"] >= m["breakout"] * 0.985: score += 20
    if pd.notna(m["vol20"]) and pd.notna(m["last_volume"]) and m["last_volume"] > m["vol20"] * 1.2: score += 10
    verdict = "Strong Bullish" if score >= 75 else "Bullish" if score >= 55 else "Neutral" if score >= 35 else "Weak"
    return score, verdict

def ai_badge(score, rsi, trend_signal, macd_signal):
    if score >= 75 and trend_signal == "Bullish" and macd_signal == "Bullish" and rsi < 75:
        return "BUY", "ai-badge-buy", "High conviction setup"
    elif score >= 45:
        return "HOLD", "ai-badge-hold", "Wait for better confirmation"
    return "SELL", "ai-badge-sell", "Weak setup / avoid now"

def conviction_meter(score, rsi, trend_signal, macd_signal):
    conviction = score + (5 if trend_signal == "Bullish" else 0) + (5 if macd_signal == "Bullish" else 0)
    conviction += 5 if 50 <= rsi <= 70 else (-5 if rsi > 80 or rsi < 25 else 0)
    conviction = max(0, min(100, conviction))
    label = "Very Strong" if conviction >= 85 else "Strong" if conviction >= 70 else "Moderate" if conviction >= 50 else "Weak"
    return conviction, label

def rupee(v):
    try: return f"₹{v:,.2f}"
    except Exception: return "N/A"

def metric_box(label, value, delta_text="", positive=None):
    delta_cls = "metric-delta-up" if positive is True else "metric-delta-down" if positive is False else "metric-delta-flat"
    st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='{delta_cls}'>{delta_text}</div></div>", unsafe_allow_html=True)

def beautiful_top_card(title, value, change, inverse=False):
    if pd.isna(value):
        st.markdown(f"<div class='hero-card'><div class='hero-title'>{title}</div><div class='hero-value' style='font-size:1.05rem;color:#94a3b8;'>Data unavailable</div></div>", unsafe_allow_html=True)
        return
    up = change >= 0
    color = "#ef4444" if (inverse and up) else "#22c55e" if (inverse and not up) else "#22c55e" if up else "#ef4444"
    arrow = "▲" if up else "▼"
    st.markdown(f"<div class='hero-card'><div class='hero-title'>{title}</div><div class='hero-value'>{value:,.2f}</div><div class='hero-change' style='color:{color};'>{arrow} {change:+.2f}%</div></div>", unsafe_allow_html=True)

def make_gauge(value):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=value, title={"text": "Conviction"}, gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#06b6d4"}, "steps": [{"range": [0, 40], "color": "rgba(239,68,68,0.35)"}, {"range": [40, 70], "color": "rgba(245,158,11,0.35)"}, {"range": [70, 100], "color": "rgba(34,197,94,0.35)"}] }))
    fig.update_layout(height=225, margin=dict(l=14, r=14, t=36, b=6), paper_bgcolor="rgba(0,0,0,0)")
    return fig

def make_candlestick(df, symbol, entry=None, stop=None, target=None, breakout=None, support=None):
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

def make_rsi_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI14"], name="RSI 14"))
    fig.add_hline(y=70, line_dash="dot")
    fig.add_hline(y=30, line_dash="dot")
    fig.update_layout(template="plotly_dark", height=255, margin=dict(l=8, r=8, t=26, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

def parse_portfolio_text(portfolio_text):
    rows = []
    if not portfolio_text.strip(): return pd.DataFrame(columns=["Symbol", "Quantity", "Avg Buy Price"])
    for line in portfolio_text.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 3: continue
        symbol, qty, avg = parts
        try:
            qty = float(qty); avg = float(avg)
            if qty > 0 and avg > 0: rows.append({"Symbol": symbol, "Quantity": qty, "Avg Buy Price": avg})
        except Exception:
            continue
    return pd.DataFrame(rows)

def portfolio_action_from_metrics(pl_pct, score, rsi):
    if pl_pct < -10 and score < 35: return "EXIT"
    elif pl_pct > 18 and (rsi > 75 or score < 45): return "REDUCE"
    elif score >= 70 and 45 <= rsi <= 70: return "ADD"
    return "HOLD"

def make_portfolio_risk_gauge(value):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=value, title={"text": "Portfolio Risk"}, gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#8b5cf6"}, "steps": [{"range": [0, 35], "color": "rgba(34,197,94,0.35)"}, {"range": [35, 70], "color": "rgba(245,158,11,0.35)"}, {"range": [70, 100], "color": "rgba(239,68,68,0.35)"}] }))
    fig.update_layout(height=260, margin=dict(l=10, r=10, t=36, b=6), paper_bgcolor="rgba(0,0,0,0)")
    return fig

# -------------------------------------------------
# PDF HELPERS
# -------------------------------------------------
def pdf_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("TitleNile", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, alignment=TA_CENTER, textColor=colors.HexColor("#0F172A"), spaceAfter=4),
        "subtitle": ParagraphStyle("SubNile", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#475569"), spaceAfter=10),
        "section": ParagraphStyle("SectionNile", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=14, alignment=TA_LEFT, textColor=colors.HexColor("#1E3A8A"), spaceAfter=6, spaceBefore=6),
        "body": ParagraphStyle("BodyNile", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=12, textColor=colors.HexColor("#111827")),
    }

def pdf_table(data, col_widths=None, header_bg="#0F172A"):
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8), ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")), ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1"))
    ]))
    return tbl

def build_stock_pdf(symbol, last_close, change_pct, ai_action, conviction_score, score, rsi, entry, stop_loss, target, qty, position_value):
    if not PDF_AVAILABLE: return None
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=12 * mm, bottomMargin=12 * mm)
    s = pdf_styles(); story = []
    story.append(Paragraph("NILE", s["title"])); story.append(Paragraph("Premium Stock Research Report", s["subtitle"])); story.append(Spacer(1, 6))
    summary = [["Field", "Value"], ["Symbol", symbol], ["Current Price", rupee(last_close)], ["Daily Change", f"{change_pct:+.2f}%"], ["AI Signal", ai_action], ["Conviction", f"{conviction_score}/100"], ["Score", f"{score}/100"], ["RSI", f"{rsi:.2f}"]]
    story.append(Paragraph("Stock Summary", s["section"])); story.append(pdf_table(summary, col_widths=[60 * mm, 110 * mm])); story.append(Spacer(1, 6))
    trade = [["Trade Plan", "Value"], ["Entry", rupee(entry)], ["Stop", rupee(stop_loss)], ["Target", rupee(target)], ["Qty", str(qty)], ["Position Size", rupee(position_value)]]
    story.append(Paragraph("Professional Trade Plan", s["section"])); story.append(pdf_table(trade, col_widths=[60 * mm, 110 * mm], header_bg="#0F766E"))
    doc.build(story); buffer.seek(0); return buffer.getvalue()

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
    universe_choice = st.radio("Stock Universe", ["NIFTY 50", "NIFTY NEXT 50", "NIFTY 100 (Combined)"], index=2)
    stock_list = NIFTY_50 if universe_choice == "NIFTY 50" else NIFTY_NEXT_50 if universe_choice == "NIFTY NEXT 50" else UNIVERSE
    symbol = st.selectbox("Select Stock", options=stock_list, index=0)
    period = st.selectbox("History Period", ["6mo", "1y", "2y", "5y"], index=1)
    capital = st.number_input("Capital (₹)", min_value=1000, value=100000, step=1000)
    risk_pct = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    rr_ratio = st.slider("Risk : Reward", 1.0, 5.0, 2.0, 0.5)
    max_scan_cap = min(60, len(stock_list)); default_scan = min(25, max_scan_cap)
    scan_count = st.slider("Scanner Universe", 10, max_scan_cap, default_scan)
    compare_symbols = st.multiselect("Multi-Stock Compare", stock_list, default=stock_list[:3], max_selections=5)
    st.markdown("---")
    st.markdown("### Portfolio Command Center")
    portfolio_text = st.text_area("Portfolio Input (SYMBOL, QTY, AVG BUY)", value="RELIANCE.NS,10,2450\nTCS.NS,5,3800\nHDFCBANK.NS,20,1650", height=120)
    run_scan = st.button("Run Institutional Scan", key="run_scan_btn")

# -------------------------------------------------
# HEADER / LOGO
# -------------------------------------------------
logo_candidates = [Path("FullLogo_NoBuffer.png"), Path("./FullLogo_NoBuffer.png")]
logo_found = next((p for p in logo_candidates if p.exists()), None)
logo_l, logo_c, logo_r = st.columns([2.2, 2.8, 2.2])
with logo_c:
    if logo_found:
        st.image(str(logo_found), width=230)
    else:
        st.markdown("<div style='font-size:2.6rem;font-weight:900;color:#fff;text-align:center;'>Nile</div>", unsafe_allow_html=True)
    st.markdown("<div class='premium-subtitle'>Stock Analysis</div>", unsafe_allow_html=True)

# -------------------------------------------------
# TOP RIBBON + LIVE CARDS
# -------------------------------------------------
nifty50_last, nifty50_chg = get_live_index("^NSEI")
banknifty_last, banknifty_chg = get_live_index("^NSEBANK")
indiavix_last, indiavix_chg = get_live_index("^INDIAVIX")
now_ist = datetime.now()
market_open = now_ist.weekday() < 5 and (((now_ist.hour > 9) or (now_ist.hour == 9 and now_ist.minute >= 15)) and ((now_ist.hour < 15) or (now_ist.hour == 15 and now_ist.minute <= 30)))
market_status = "OPEN" if market_open else "CLOSED"
market_status_color = "#22c55e" if market_open else "#ef4444"
last_updated = now_ist.strftime("%d-%b-%Y %I:%M %p")
st.markdown(f"<div class='imperial-ribbon'><span class='ribbon-chip'>NIFTY 50</span><span class='ribbon-chip'>BANK NIFTY</span><span class='ribbon-chip'>INDIA VIX</span><span class='ribbon-chip'>Imperial Terminal</span><span class='ribbon-chip'>Institutional Flow</span><span class='ribbon-chip'>Cloud Safe</span><span class='ribbon-chip' style='color:{market_status_color};'>Market: {market_status}</span><span class='ribbon-chip'>Last Updated: {last_updated}</span></div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="small")
with c1: beautiful_top_card("NIFTY 50 Live", nifty50_last, nifty50_chg)
with c2: beautiful_top_card("BANK NIFTY Live", banknifty_last, banknifty_chg)
with c3: beautiful_top_card("INDIA VIX Live", indiavix_last, indiavix_chg, inverse=True)

# -------------------------------------------------
# MARKET BREADTH
# -------------------------------------------------
breadth_sample_size = min(12, len(stock_list)); breadth_symbols = stock_list[:breadth_sample_size]
advancers = decliners = bullish_trend_count = valid_breadth_count = 0; breadth_rows = []
for s in breadth_symbols:
    d = get_history(s, period="6mo")
    if d.empty or len(d) < 35: continue
    m = compute_scan_metrics_fast(d)
    if not m: continue
    valid_breadth_count += 1
    day_ret = m.get("day_ret", 0.0)
    if day_ret >= 0: advancers += 1
    else: decliners += 1
    if m["sma20"] > m["sma50"]: bullish_trend_count += 1
    breadth_rows.append(day_ret)
if valid_breadth_count == 0:
    breadth_ratio = trend_ratio = avg_day_ret = 0.0
else:
    avg_day_ret = float(np.mean(breadth_rows)) if breadth_rows else 0.0
    breadth_ratio = round((advancers / max(valid_breadth_count, 1)) * 100, 1)
    trend_ratio = round((bullish_trend_count / max(valid_breadth_count, 1)) * 100, 1)

b1, b2, b3, b4 = st.columns(4, gap="small")
with b1: st.markdown(f"<div class='breadth-card'><div class='breadth-label'>Advance / Decline</div><div class='breadth-value'>{advancers} / {decliners}</div><div class='metric-delta-flat'>{valid_breadth_count} stocks sampled</div></div>", unsafe_allow_html=True)
with b2: st.markdown(f"<div class='breadth-card'><div class='breadth-label'>Breadth Strength</div><div class='breadth-value'>{breadth_ratio}%</div><div class='{'metric-delta-up' if breadth_ratio >= 55 else 'metric-delta-down'}'>Advancers share</div></div>", unsafe_allow_html=True)
with b3: st.markdown(f"<div class='breadth-card'><div class='breadth-label'>Bullish Trend Stocks</div><div class='breadth-value'>{bullish_trend_count}</div><div class='{'metric-delta-up' if trend_ratio >= 55 else 'metric-delta-down'}'>{trend_ratio}% above trend filter</div></div>", unsafe_allow_html=True)
with b4: st.markdown(f"<div class='breadth-card'><div class='breadth-label'>Average Daily Return</div><div class='breadth-value'>{avg_day_ret:+.2f}%</div><div class='{'metric-delta-up' if avg_day_ret >= 0 else 'metric-delta-down'}'>Universe average</div></div>", unsafe_allow_html=True)

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
rsi = safe_last(df["RSI14"]); atr = safe_last(df["ATR14"])
m = compute_scan_metrics_fast(raw)
score, verdict = score_from_metrics(m) if m else (0, "Weak")
trend_signal = "Bullish" if df.iloc[-1]["SMA20"] > df.iloc[-1]["SMA50"] else "Bearish"
macd_signal = "Bullish" if df.iloc[-1]["MACD"] > df.iloc[-1]["MACD_SIGNAL"] else "Bearish"
breakout_level = df["High"].tail(20).max(); support_level = df["Low"].tail(20).min(); entry = breakout_level * 1.002
stop_loss = max(entry - atr * 1.5, support_level); risk_per_share = max(entry - stop_loss, 0.01)
allowed_risk = capital * (risk_pct / 100); qty = max(int(allowed_risk // risk_per_share), 0); target = entry + (risk_per_share * rr_ratio); position_value = qty * entry
ai_action, ai_class, ai_reason = ai_badge(score, rsi, trend_signal, macd_signal)
conviction_score, conviction_label = conviction_meter(score, rsi, trend_signal, macd_signal)

# -------------------------------------------------
# INSTITUTIONAL SUMMARY + CONVICTION
# -------------------------------------------------
s1, s2, s3 = st.columns([1.15, 0.9, 1.2], gap="small")
with s1:
    st.markdown(f"<div class='{ai_class}'>AI {ai_action} • {conviction_score}% Confidence<br><span style='font-size:0.82rem;font-weight:700'>{ai_reason}</span></div>", unsafe_allow_html=True)
with s2:
    st.plotly_chart(make_gauge(conviction_score), use_container_width=True)
with s3:
    st.markdown(f"<div class='panel'><div class='panel-title'>Institutional Summary</div><div class='subtle-divider'></div><span class='ribbon-chip'>Trend: {trend_signal}</span><span class='ribbon-chip'>Momentum: {macd_signal}</span><span class='ribbon-chip'>RSI: {rsi:.1f}</span><span class='ribbon-chip'>Sector: {info.get('sector','N/A')}</span><span class='ribbon-chip'>Action: {ai_action}</span><div style='margin-top:8px;color:#cbd5e1;font-weight:700;font-size:0.88rem;'>BUY above {entry:.2f} • SL {stop_loss:.2f} • Target {target:.2f}</div></div>", unsafe_allow_html=True)

# -------------------------------------------------
# PRIMARY METRICS
# -------------------------------------------------
m1, m2, m3, m4, m5 = st.columns(5, gap="small")
with m1: metric_box("Last Price", rupee(last_close), f"{change_pct:+.2f}% today", positive=change_pct >= 0)
with m2: metric_box("Institutional Score", f"{score}/100", verdict, positive=score >= 55)
with m3: metric_box("RSI (14)", f"{rsi:.2f}", "Healthy" if 50 <= rsi <= 70 else "Watch", positive=50 <= rsi <= 70)
with m4: metric_box("ATR (14)", f"{atr:.2f}", "Volatility gauge")
market_cap = info.get("marketCap", np.nan)
with m5: metric_box("Market Cap", f"₹{market_cap/1e7:,.0f} Cr" if pd.notna(market_cap) else "N/A", info.get("sector", "Unknown"))

# -------------------------------------------------
# RATIO BUTTONS
# -------------------------------------------------
cb1, cb2 = st.columns(2, gap="small")
with cb1: show_fundamental_ratio = st.button("Fundamental Ratio", key="fundamental_ratio_btn")
with cb2: show_technical_ratio = st.button("Technical Ratio", key="technical_ratio_btn")

# -------------------------------------------------
# CHARTS
# -------------------------------------------------
left, right = st.columns([2.1, 0.9], gap="small")
with left:
    st.markdown("<div class='panel'><div class='panel-title'>Price Structure</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
    st.plotly_chart(make_candlestick(df.tail(180), symbol, entry, stop_loss, target, breakout_level, support_level), use_container_width=True)
with right:
    st.markdown("<div class='panel'><div class='panel-title'>Momentum (RSI)</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
    st.plotly_chart(make_rsi_chart(df.tail(180)), use_container_width=True)

# -------------------------------------------------
# RATIO PANELS
# -------------------------------------------------
if show_fundamental_ratio:
    st.markdown("<div class='panel'><div class='panel-title'>Fundamental Ratio</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
    fr = pd.DataFrame({"Metric": ["P/E", "Forward P/E", "Price/Book", "ROE %", "Debt/Equity", "Profit Margin %"], "Value": [info.get("trailingPE", "N/A"), info.get("forwardPE", "N/A"), info.get("priceToBook", "N/A"), round((info.get("returnOnEquity", 0) or 0) * 100, 2) if info.get("returnOnEquity") is not None else "N/A", info.get("debtToEquity", "N/A"), round((info.get("profitMargins", 0) or 0) * 100, 2) if info.get("profitMargins") is not None else "N/A"]})
    st.dataframe(fr, use_container_width=True)
if show_technical_ratio:
    st.markdown("<div class='panel'><div class='panel-title'>Technical Ratio</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
    tr = pd.DataFrame({"Metric": ["SMA20", "SMA50", "RSI14", "MACD", "MACD Signal", "ATR14"], "Value": [round(df.iloc[-1]["SMA20"], 2), round(df.iloc[-1]["SMA50"], 2), round(rsi, 2), round(df.iloc[-1]["MACD"], 2), round(df.iloc[-1]["MACD_SIGNAL"], 2), round(atr, 2)]})
    st.dataframe(tr, use_container_width=True)

# -------------------------------------------------
# SIGNAL ENGINE + TRADE PLAN
# -------------------------------------------------
sg1, sg2 = st.columns([1.15, 1.85], gap="small")
with sg1:
    st.markdown("<div class='panel'><div class='panel-title'>Institutional Signal Engine</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
    sig_df = pd.DataFrame({"Signal": ["Trend", "Momentum", "Breakout", "RSI", "Volume"], "Status": [trend_signal, macd_signal, "Active" if last_close >= breakout_level * 0.97 else "Watch", "Healthy" if 50 <= rsi <= 70 else "Extreme", "Elevated" if m and pd.notna(m['vol20']) and pd.notna(m['last_volume']) and m['last_volume'] > m['vol20'] else "Normal"]})
    st.dataframe(sig_df, use_container_width=True)
with sg2:
    st.markdown("<div class='panel'><div class='panel-title'>Professional Trade Plan</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
    p1, p2, p3, p4, p5 = st.columns(5, gap="small")
    with p1: metric_box("Suggested Entry", rupee(entry), "Breakout confirmation", True)
    with p2: metric_box("Stop Loss", rupee(stop_loss), "ATR + support based", False)
    with p3: metric_box("Target", rupee(target), f"R:R {rr_ratio:.1f}", True)
    with p4: metric_box("Quantity", f"{qty}", f"Risk {rupee(allowed_risk)}", True if qty > 0 else None)
    with p5: metric_box("Position Size", rupee(position_value), "Capital deployed", position_value <= capital)

# -------------------------------------------------
# SCANNER
# -------------------------------------------------
if run_scan:
    scan_rows = []
    scan_symbols = stock_list[:scan_count]
    progress = st.progress(0)
    for i, s in enumerate(scan_symbols, start=1):
        d = get_history(s, period="6mo")
        if d.empty or len(d) < 35:
            progress.progress(i / len(scan_symbols)); continue
        met = compute_scan_metrics_fast(d)
        if not met:
            progress.progress(i / len(scan_symbols)); continue
        sc, ver = score_from_metrics(met)
        trend = "Bullish" if met["sma20"] > met["sma50"] else "Bearish"
        macd = "Bullish" if met["macd"] > met["macd_signal"] else "Bearish"
        ai, _, _ = ai_badge(sc, met["rsi"], trend, macd)
        ent = round(met["breakout"] * 1.002, 2)
        stp = round(max(ent - met["atr"] * 1.5, met["support"]), 2)
        scan_rows.append({"Symbol": s, "AI": ai, "Score": sc, "Verdict": ver, "Price": round(met["close"], 2), "Entry": ent, "Stop": stp, "RSI": round(met["rsi"], 2), "Sector": SECTOR_MAP.get(s, "Others")})
        progress.progress(i / len(scan_symbols))
    progress.empty()
    st.session_state.scan_df = pd.DataFrame(scan_rows).sort_values(["Score", "RSI"], ascending=[False, True]).reset_index(drop=True) if scan_rows else pd.DataFrame()

if not st.session_state.scan_df.empty:
    st.markdown("<div class='panel'><div class='panel-title'>Watchlist Decision Matrix</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
    st.dataframe(st.session_state.scan_df.head(15), use_container_width=True)

# -------------------------------------------------
# PORTFOLIO COMMAND CENTER
# -------------------------------------------------
portfolio_df = parse_portfolio_text(portfolio_text)
portfolio_analysis_df = pd.DataFrame()
if not portfolio_df.empty:
    rows = []
    for _, row in portfolio_df.iterrows():
        s = row["Symbol"]
        d = get_history(s, period="6mo")
        if d.empty: continue
        dd = compute_indicators(d)
        if dd.empty: continue
        cp = float(dd["Close"].iloc[-1]); qty_h = float(row["Quantity"]); avg_buy = float(row["Avg Buy Price"])
        invested = qty_h * avg_buy; current = qty_h * cp; pl = current - invested; pl_pct = ((current / invested) - 1) * 100 if invested else 0
        met = compute_scan_metrics_fast(d); sc, _ = score_from_metrics(met) if met else (0, "Weak")
        r = float(dd["RSI14"].iloc[-1]); action = portfolio_action_from_metrics(pl_pct, sc, r)
        rows.append({"Symbol": s, "Sector": SECTOR_MAP.get(s, "Others"), "Quantity": qty_h, "Avg Buy Price": avg_buy, "Current Price": round(cp, 2), "Invested Value": round(invested, 2), "Current Value": round(current, 2), "P/L ₹": round(pl, 2), "P/L %": round(pl_pct, 2), "Action": action})
    portfolio_analysis_df = pd.DataFrame(rows)

st.markdown("<div class='panel'><div class='panel-title'>Portfolio Command Center</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
if portfolio_analysis_df.empty:
    st.info("Add portfolio entries in sidebar to activate Portfolio Command Center.")
else:
    total_invested = portfolio_analysis_df["Invested Value"].sum(); total_current = portfolio_analysis_df["Current Value"].sum(); total_pl = total_current - total_invested; total_pl_pct = ((total_current / total_invested) - 1) * 100 if total_invested else 0
    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1: metric_box("Invested", rupee(total_invested), "Capital deployed")
    with pc2: metric_box("Current Value", rupee(total_current), "Marked to market")
    with pc3: metric_box("P/L ₹", rupee(total_pl), f"{total_pl_pct:+.2f}%", positive=total_pl >= 0)
    risk_score = min(100, max(0, 50 + (portfolio_analysis_df["P/L %"].std() if len(portfolio_analysis_df) > 1 else 0)))
    with pc4: st.plotly_chart(make_portfolio_risk_gauge(risk_score), use_container_width=True)
    st.dataframe(portfolio_analysis_df, use_container_width=True)

# -------------------------------------------------
# PORTFOLIO ACTION SUGGESTIONS
# -------------------------------------------------
st.markdown("<div class='panel'><div class='panel-title'>Portfolio Action Suggestions</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
if portfolio_analysis_df.empty:
    st.info("Portfolio suggestions will appear after portfolio input.")
else:
    sugg = portfolio_analysis_df[["Symbol", "Sector", "P/L %", "Action"]].copy()
    st.dataframe(sugg, use_container_width=True)

# -------------------------------------------------
# SECTOR STRENGTH TILES + HEATMAP (1M PERFORMANCE)
# -------------------------------------------------
st.markdown("<div class='panel'><div class='panel-title'>Sector Strength Tiles + Heatmap (1M Performance)</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
sector_perf = []
for sector in sorted(set(SECTOR_MAP.values())):
    syms = [s for s, sec in SECTOR_MAP.items() if sec == sector][:5]
    rets = []
    for s in syms:
        d = get_history(s, period="3mo")
        if d.empty or len(d) < 22: continue
        rets.append(((float(d["Close"].iloc[-1]) / float(d["Close"].iloc[-22])) - 1) * 100)
    if rets:
        sector_perf.append({"Sector": sector, "1M Return %": round(float(np.mean(rets)), 2)})
sector_df = pd.DataFrame(sector_perf).sort_values("1M Return %", ascending=False) if sector_perf else pd.DataFrame(columns=["Sector", "1M Return %"])
if sector_df.empty:
    st.info("Sector heatmap unavailable currently.")
else:
    tile_cols = st.columns(min(4, len(sector_df)))
    for i, (_, row) in enumerate(sector_df.head(4).iterrows()):
        with tile_cols[i]:
            metric_box(row["Sector"], f"{row['1M Return %']:+.2f}%", "1M Performance", positive=row["1M Return %"] >= 0)
    heat_fig = px.bar(sector_df, x="Sector", y="1M Return %", title="Sector Heatmap (1M Performance)")
    heat_fig.update_layout(template="plotly_dark", height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(heat_fig, use_container_width=True)

# -------------------------------------------------
# FINANCIAL STATEMENTS
# -------------------------------------------------
st.markdown("<div class='panel'><div class='panel-title'>Balance Sheet / P&L / Cash Flow (₹ Cr)</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
ft1, ft2, ft3 = st.tabs(["Balance Sheet", "P&L", "Cash Flow"])
with ft1:
    st.dataframe((bs / 1e7).round(2) if not bs.empty else pd.DataFrame({"Info": ["No data available"]}), use_container_width=True)
with ft2:
    st.dataframe((fin / 1e7).round(2) if not fin.empty else pd.DataFrame({"Info": ["No data available"]}), use_container_width=True)
with ft3:
    st.dataframe((cf / 1e7).round(2) if not cf.empty else pd.DataFrame({"Info": ["No data available"]}), use_container_width=True)

# -------------------------------------------------
# MULTI-STOCK COMPARE
# -------------------------------------------------
if compare_symbols:
    st.markdown("<div class='panel'><div class='panel-title'>Multi-Stock Compare</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
    cmp_rows = []
    for s in compare_symbols:
        d = get_history(s, period="6mo")
        if d.empty: continue
        dd = compute_indicators(d)
        if dd.empty: continue
        met = compute_scan_metrics_fast(d); sc, ver = score_from_metrics(met) if met else (0, "Weak")
        cmp_rows.append({"Symbol": s, "Price": round(float(dd["Close"].iloc[-1]), 2), "RSI": round(float(dd["RSI14"].iloc[-1]), 2), "Score": sc, "Verdict": ver})
    if cmp_rows:
        st.dataframe(pd.DataFrame(cmp_rows), use_container_width=True)

# -------------------------------------------------
# PDF REPORT EXPORT
# -------------------------------------------------
st.markdown("<div class='panel'><div class='panel-title'>PDF Report Export</div><div class='subtle-divider'></div></div>", unsafe_allow_html=True)
pdf_bytes = build_stock_pdf(symbol, last_close, change_pct, ai_action, conviction_score, score, rsi, entry, stop_loss, target, qty, position_value)
if pdf_bytes:
    st.download_button("Download PDF Report", data=pdf_bytes, file_name=f"NILE_{symbol.replace('.NS','')}_Report.pdf", mime="application/pdf")
else:
    st.info("PDF export unavailable. Install reportlab in deployment.")

st.success("FINAL NILE V15 MASTER TERMINAL loaded successfully.")

# FINAL NILE V12.3 MASTERPIECE
# Single-file Streamlit app.py
# Visible app name: Nile
# Upgraded: NIFTY 50 + NIFTY NEXT 50 + Fundamental Ratio button + Technical Ratio button

import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# Optional safe import
try:
    import yfinance as yf
except Exception:
    yf = None

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
# PREMIUM MASTERPIECE CSS
# -------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --bg1: #050914;
        --bg2: #0b1220;
        --card: rgba(15, 23, 42, 0.85);
        --stroke: rgba(148, 163, 184, 0.16);
        --text: #e5e7eb;
        --muted: #94a3b8;
        --green: #22c55e;
        --red: #ef4444;
        --blue: #3b82f6;
        --violet: #8b5cf6;
        --gold: #f59e0b;
        --cyan: #06b6d4;
    }

    .stApp {
        background:
            radial-gradient(circle at 15% 20%, rgba(59,130,246,0.12), transparent 24%),
            radial-gradient(circle at 85% 8%, rgba(139,92,246,0.10), transparent 28%),
            radial-gradient(circle at 50% 85%, rgba(6,182,212,0.07), transparent 25%),
            linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 100%);
        color: var(--text);
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1650px;
    }

    .nile-title {
        font-size: 2.65rem;
        font-weight: 900;
        letter-spacing: 0.3px;
        color: #ffffff;
        margin-bottom: 0.15rem;
    }

    .nile-sub {
        color: #a5b4fc;
        font-size: 1rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }

    .card {
        background: linear-gradient(180deg, rgba(17,24,39,0.88), rgba(15,23,42,0.84));
        border: 1px solid var(--stroke);
        border-radius: 22px;
        padding: 16px;
        box-shadow: 0 12px 34px rgba(0,0,0,0.28);
        backdrop-filter: blur(10px);
        margin-bottom: 14px;
    }

    .metric-card {
        background: linear-gradient(180deg, rgba(15,23,42,0.96), rgba(17,24,39,0.88));
        border: 1px solid rgba(148,163,184,0.14);
        border-radius: 18px;
        padding: 16px;
        min-height: 118px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.22);
    }

    .metric-label { font-size: 0.82rem; color: #94a3b8; margin-bottom: 6px; }
    .metric-value { font-size: 1.75rem; font-weight: 800; color: #ffffff; margin-bottom: 4px; }
    .metric-delta-up { color: #22c55e; font-weight: 700; }
    .metric-delta-down { color: #ef4444; font-weight: 700; }
    .metric-delta-flat { color: #94a3b8; font-weight: 700; }
    .section-title { font-size: 1.08rem; font-weight: 800; color: #f8fafc; margin-bottom: 8px; }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(7,12,24,0.98), rgba(11,18,32,0.98));
        border-right: 1px solid rgba(148,163,184,0.08);
    }

    .stButton > button {
        width: 100%;
        border-radius: 14px;
        border: 1px solid rgba(148,163,184,0.18);
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        color: white;
        font-weight: 800;
        padding: 0.68rem 0.9rem;
    }

    .stDownloadButton > button {
        width: 100%;
        border-radius: 14px;
        border: 1px solid rgba(148,163,184,0.18);
        background: linear-gradient(90deg, #0f766e, #2563eb);
        color: white;
        font-weight: 800;
        padding: 0.68rem 0.9rem;
    }

    .pill {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 6px;
        margin-bottom: 6px;
        border: 1px solid rgba(148,163,184,0.14);
        background: rgba(30,41,59,0.65);
        color: #e2e8f0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# NIFTY 50 + NIFTY NEXT 50 (approx tradable Yahoo symbols)
# -------------------------------------------------
NIFTY_50 = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","BHARTIARTL.NS","ICICIBANK.NS","SBIN.NS","INFY.NS","HINDUNILVR.NS","ITC.NS","LT.NS",
    "KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","NESTLEIND.NS","BAJAJFINSV.NS",
    "HCLTECH.NS","WIPRO.NS","NTPC.NS","POWERGRID.NS","TATAMOTORS.NS","M&M.NS","ONGC.NS","COALINDIA.NS","TATASTEEL.NS","JSWSTEEL.NS",
    "ADANIPORTS.NS","INDUSINDBK.NS","TECHM.NS","GRASIM.NS","CIPLA.NS","DRREDDY.NS","HINDALCO.NS","HEROMOTOCO.NS","EICHERMOT.NS","BPCL.NS",
    "BRITANNIA.NS","APOLLOHOSP.NS","DIVISLAB.NS","ADANIENT.NS","TATACONSUM.NS","PIDILITIND.NS","SBILIFE.NS","BAJAJ-AUTO.NS","SHRIRAMFIN.NS","TRENT.NS"
]

NIFTY_NEXT_50 = [
    "ABB.NS","ADANIGREEN.NS","ADANIPOWER.NS","AMBUJACEM.NS","BANKBARODA.NS","BOSCHLTD.NS","CANBK.NS","CGPOWER.NS","CHOLAFIN.NS","DABUR.NS",
    "DLF.NS","GAIL.NS","GODREJCP.NS","HAL.NS","HAVELLS.NS","ICICIGI.NS","ICICIPRULI.NS","INDIGO.NS","IOC.NS","IRCTC.NS",
    "JINDALSTEL.NS","JSWENERGY.NS","LICI.NS","LODHA.NS","LUPIN.NS","MCDOWELL-N.NS","MOTHERSON.NS","NAUKRI.NS","NMDC.NS","PFC.NS",
    "PIDILITIND.NS","PNB.NS","POLYCAB.NS","RECLTD.NS","SAIL.NS","SIEMENS.NS","TVSMOTOR.NS","UNITDSPR.NS","VEDL.NS","VOLTAS.NS",
    "ZYDUSLIFE.NS","INDUSTOWER.NS","TORNTPHARM.NS","HDFCLIFE.NS","COLPAL.NS","MARICO.NS","UBL.NS","BERGEPAINT.NS","CONCOR.NS","OFSS.NS"
]

UNIVERSE = sorted(list(dict.fromkeys(NIFTY_50 + NIFTY_NEXT_50)))

# -------------------------------------------------
# DATA HELPERS
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
    d["EMA20"] = d["Close"].ewm(span=20, adjust=False).mean()
    d["EMA50"] = d["Close"].ewm(span=50, adjust=False).mean()

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


def rupee(v):
    try:
        return f"₹{v:,.2f}"
    except Exception:
        return "N/A"


def metric_box(label, value, delta_text="", positive=None):
    if positive is True:
        delta_cls = "metric-delta-up"
    elif positive is False:
        delta_cls = "metric-delta-down"
    else:
        delta_cls = "metric-delta-flat"
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>{label}</div>
            <div class='metric-value'>{value}</div>
            <div class='{delta_cls}'>{delta_text}</div>
        </div>
    """, unsafe_allow_html=True)


def make_candlestick(df: pd.DataFrame, symbol: str):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"
    ))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA20", line=dict(width=1.8)))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA50", line=dict(width=1.8)))
    fig.update_layout(
        title=f"{symbol} Price Structure",
        template="plotly_dark",
        height=520,
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def make_rsi_chart(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI14"], name="RSI 14"))
    fig.add_hline(y=70, line_dash="dot")
    fig.add_hline(y=30, line_dash="dot")
    fig.update_layout(template="plotly_dark", height=260, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.markdown("## Nile")
    st.caption("Stock Analysis")

    universe_choice = st.radio("Stock Universe", ["NIFTY 50", "NIFTY NEXT 50", "NIFTY 100 (Combined)"], index=2)
    if universe_choice == "NIFTY 50":
        stock_list = NIFTY_50
    elif universe_choice == "NIFTY NEXT 50":
        stock_list = NIFTY_NEXT_50
    else:
        stock_list = UNIVERSE

    symbol = st.selectbox("Select Stock", options=stock_list, index=0)
    period = st.selectbox("History Period", ["6mo", "1y", "2y", "5y"], index=1)
    capital = st.number_input("Capital (₹)", min_value=1000, value=100000, step=1000)
    risk_pct = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    rr_ratio = st.slider("Risk : Reward", 1.0, 5.0, 2.0, 0.5)
    scan_count = st.slider("Scanner Universe", 10, min(100, len(stock_list)), min(30, len(stock_list)))

    run_scan = st.button("Run Institutional Scan")

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("<div class='nile-title'>Nile</div>", unsafe_allow_html=True)
st.markdown("<div class='nile-sub'>Stock Analysis</div>", unsafe_allow_html=True)

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
score, verdict, reasons = score_stock(df)

# -------------------------------------------------
# TOP METRICS
# -------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    metric_box("Last Price", rupee(last_close), f"{change_pct:+.2f}% today", positive=change_pct >= 0)
with c2:
    metric_box("Institutional Score", f"{score}/100", verdict, positive=score >= 55)
with c3:
    rsi_state = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Healthy"
    metric_box("RSI (14)", f"{rsi:.2f}", rsi_state, positive=50 <= rsi <= 70)
with c4:
    metric_box("ATR (14)", f"{atr:.2f}", "Volatility gauge", positive=None)
with c5:
    market_cap = info.get("marketCap", np.nan)
    metric_box("Market Cap", f"₹{market_cap/1e7:,.0f} Cr" if pd.notna(market_cap) else "N/A", info.get("sector", "Unknown"), positive=None)

# -------------------------------------------------
# RATIO BUTTONS (NEW)
# -------------------------------------------------
st.markdown("<div class='card'><div class='section-title'>Ratio Controls</div></div>", unsafe_allow_html=True)
rb1, rb2 = st.columns(2)
with rb1:
    show_fundamental_ratio = st.button("Fundamental Ratio")
with rb2:
    show_technical_ratio = st.button("Technical Ratio")

# -------------------------------------------------
# CHARTS
# -------------------------------------------------
left, right = st.columns([2, 1])
with left:
    st.markdown("<div class='card'><div class='section-title'>Price Action & Trend Structure</div></div>", unsafe_allow_html=True)
    st.plotly_chart(make_candlestick(df.tail(180), symbol), use_container_width=True)
with right:
    st.markdown("<div class='card'><div class='section-title'>Momentum (RSI)</div></div>", unsafe_allow_html=True)
    st.plotly_chart(make_rsi_chart(df.tail(180)), use_container_width=True)

# -------------------------------------------------
# SIGNAL ENGINE
# -------------------------------------------------
st.markdown("<div class='card'><div class='section-title'>Institutional Signal Engine</div></div>", unsafe_allow_html=True)
col_a, col_b, col_c = st.columns(3)
trend_signal = "Bullish" if df.iloc[-1]["SMA20"] > df.iloc[-1]["SMA50"] else "Bearish"
macd_signal = "Bullish" if df.iloc[-1]["MACD"] > df.iloc[-1]["MACD_SIGNAL"] else "Bearish"
breakout_level = df["High"].tail(20).max()
support_level = df["Low"].tail(20).min()

with col_a:
    st.info(f"**Trend:** {trend_signal}\n\n**SMA20:** {df.iloc[-1]['SMA20']:.2f}\n\n**SMA50:** {df.iloc[-1]['SMA50']:.2f}")
with col_b:
    st.info(f"**MACD:** {macd_signal}\n\n**MACD:** {df.iloc[-1]['MACD']:.2f}\n\n**Signal:** {df.iloc[-1]['MACD_SIGNAL']:.2f}")
with col_c:
    st.info(f"**Breakout Level:** {breakout_level:.2f}\n\n**Support Level:** {support_level:.2f}\n\n**20D Range Strategy**")

# -------------------------------------------------
# TRADE PLAN
# -------------------------------------------------
st.markdown("<div class='card'><div class='section-title'>Professional Trade Plan</div></div>", unsafe_allow_html=True)
entry = breakout_level * 1.002
stop_loss = max(entry - atr * 1.5, support_level)
risk_per_share = max(entry - stop_loss, 0.01)
allowed_risk = capital * (risk_pct / 100)
qty = max(int(allowed_risk // risk_per_share), 0)
target = entry + (risk_per_share * rr_ratio)
position_value = qty * entry

p1, p2, p3, p4, p5 = st.columns(5)
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
# FUNDAMENTAL SNAPSHOT
# -------------------------------------------------
st.markdown("<div class='card'><div class='section-title'>Fundamental Snapshot</div></div>", unsafe_allow_html=True)
fc1, fc2, fc3, fc4 = st.columns(4)
with fc1:
    st.metric("Sector", info.get("sector", "N/A"))
with fc2:
    st.metric("Industry", info.get("industry", "N/A"))
with fc3:
    st.metric("P/E", f"{info.get('trailingPE', 'N/A')}")
with fc4:
    st.metric("ROE", f"{round((info.get('returnOnEquity', 0) or 0)*100, 2)}%" if info.get('returnOnEquity') is not None else "N/A")

fc5, fc6, fc7, fc8 = st.columns(4)
with fc5:
    st.metric("Debt / Equity", f"{info.get('debtToEquity', 'N/A')}")
with fc6:
    st.metric("Profit Margin", f"{round((info.get('profitMargins', 0) or 0)*100, 2)}%" if info.get('profitMargins') is not None else "N/A")
with fc7:
    st.metric("Revenue Growth", f"{round((info.get('revenueGrowth', 0) or 0)*100, 2)}%" if info.get('revenueGrowth') is not None else "N/A")
with fc8:
    st.metric("Dividend Yield", f"{round((info.get('dividendYield', 0) or 0)*100, 2)}%" if info.get('dividendYield') is not None else "N/A")

# -------------------------------------------------
# FUNDAMENTAL RATIO BUTTON SECTION (NEW)
# -------------------------------------------------
if show_fundamental_ratio:
    st.markdown("<div class='card'><div class='section-title'>Fundamental Ratio Analysis</div></div>", unsafe_allow_html=True)
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

# -------------------------------------------------
# TECHNICAL RATIO BUTTON SECTION (NEW)
# -------------------------------------------------
if show_technical_ratio:
    st.markdown("<div class='card'><div class='section-title'>Technical Ratio Analysis</div></div>", unsafe_allow_html=True)
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
        {"Metric": "Distance to 20D High (%)", "Value": round(((last['Close'] / breakout_level) - 1) * 100, 2)},
        {"Metric": "Distance to 20D Low (%)", "Value": round(((last['Close'] / support_level) - 1) * 100, 2)},
        {"Metric": "Bollinger Upper Gap (%)", "Value": round(((last['Close'] / last['BB_UPPER']) - 1) * 100, 2)},
        {"Metric": "Bollinger Lower Gap (%)", "Value": round(((last['Close'] / last['BB_LOWER']) - 1) * 100, 2)},
    ])
    st.dataframe(tech_df, use_container_width=True)

# -------------------------------------------------
# BALANCE SHEET / FINANCIALS
# -------------------------------------------------
st.markdown("<div class='card'><div class='section-title'>Balance Sheet / P&L / Cash Flow (Latest Available)</div></div>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["Balance Sheet", "Financials", "Cash Flow"])
with tab1:
    if isinstance(bs, pd.DataFrame) and not bs.empty:
        st.dataframe(bs.iloc[:, :4].fillna(0), use_container_width=True)
    else:
        st.info("Balance sheet not available for this symbol.")
with tab2:
    if isinstance(fin, pd.DataFrame) and not fin.empty:
        st.dataframe(fin.iloc[:, :4].fillna(0), use_container_width=True)
    else:
        st.info("Financials not available for this symbol.")
with tab3:
    if isinstance(cf, pd.DataFrame) and not cf.empty:
        st.dataframe(cf.iloc[:, :4].fillna(0), use_container_width=True)
    else:
        st.info("Cash flow not available for this symbol.")

# -------------------------------------------------
# WATCHLIST TABLE
# -------------------------------------------------
st.markdown("<div class='card'><div class='section-title'>Watchlist Decision Matrix</div></div>", unsafe_allow_html=True)
watch_df = pd.DataFrame([{
    "Symbol": symbol,
    "Last Price": round(last_close, 2),
    "Score": score,
    "Verdict": verdict,
    "Entry": round(entry, 2),
    "Stop": round(stop_loss, 2),
    "Target": round(target, 2),
    "Qty": qty,
}])
st.dataframe(watch_df, use_container_width=True)

csv = watch_df.to_csv(index=False).encode("utf-8")
st.download_button("Download Trade Plan CSV", data=csv, file_name=f"{symbol.replace('.NS','')}_trade_plan.csv", mime="text/csv")

# -------------------------------------------------
# SCANNER
# -------------------------------------------------
if run_scan:
    st.markdown("<div class='card'><div class='section-title'>Institutional Breakout Scanner</div></div>", unsafe_allow_html=True)
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
            rows.append({
                "Symbol": s,
                "Price": round(lc, 2),
                "Score": sc,
                "Verdict": vd,
                "RSI": round(r, 2) if pd.notna(r) else np.nan,
                "Breakout Level": round(bh, 2),
            })
        progress.progress(i / len(universe))
        time.sleep(0.02)

    status.empty()
    scan_df = pd.DataFrame(rows).sort_values(["Score", "RSI"], ascending=[False, False]).reset_index(drop=True)
    st.dataframe(scan_df, use_container_width=True)

    if not scan_df.empty:
        top = scan_df.head(10)
        fig = px.bar(top, x="Symbol", y="Score", hover_data=["Price", "RSI", "Verdict"], template="plotly_dark", title="Top Institutional Setups")
        fig.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.caption("Nile is a stock analysis dashboard for educational and research use. Data may be delayed/incomplete depending on source availability. Always verify before trading.")

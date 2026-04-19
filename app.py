import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="NILE • CLOUD HOTFIX MASTER",
    layout="wide",
    page_icon="📈"
)

# =========================================================
# PREMIUM CSS
# =========================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #081225 0%, #0b1020 35%, #0f172a 100%);
        color: #e5e7eb;
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #60a5fa, #22d3ee, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        font-size: 1rem;
        color: #cbd5e1;
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #f8fafc;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }

    .pulse-green {
        background: linear-gradient(135deg, rgba(6,78,59,0.96), rgba(5,150,105,0.86));
        border: 1px solid rgba(16,185,129,0.35);
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 8px 24px rgba(16,185,129,0.18);
    }

    .pulse-red {
        background: linear-gradient(135deg, rgba(127,29,29,0.96), rgba(220,38,38,0.84));
        border: 1px solid rgba(248,113,113,0.35);
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 8px 24px rgba(239,68,68,0.18);
    }

    .pulse-neutral {
        background: linear-gradient(135deg, rgba(30,41,59,0.96), rgba(51,65,85,0.90));
        border: 1px solid rgba(148,163,184,0.22);
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 8px 24px rgba(148,163,184,0.10);
    }

    .card-title {
        font-size: 0.9rem;
        color: #e2e8f0;
        font-weight: 800;
        margin-bottom: 8px;
        text-transform: uppercase;
    }

    .card-value {
        font-size: 1.85rem;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 4px;
    }

    .card-change {
        font-size: 0.95rem;
        font-weight: 700;
        color: #ecfeff;
    }

    .badge-buy {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 999px;
        background: linear-gradient(90deg, #10b981, #34d399);
        color: white;
        font-weight: 800;
        font-size: 0.9rem;
    }

    .badge-sell {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 999px;
        background: linear-gradient(90deg, #ef4444, #f87171);
        color: white;
        font-weight: 800;
        font-size: 0.9rem;
    }

    .badge-hold {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 999px;
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
        color: white;
        font-weight: 800;
        font-size: 0.9rem;
    }

    .stButton > button {
        width: 100%;
        border-radius: 14px;
        border: none;
        padding: 0.75rem 1rem;
        font-weight: 900;
        color: white;
        background: linear-gradient(90deg, #2563eb, #06b6d4);
        box-shadow: 0 10px 22px rgba(37,99,235,0.35);
        transition: all 0.2s ease-in-out;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 28px rgba(6,182,212,0.35);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #081225 0%, #0f172a 100%);
        border-right: 1px solid rgba(148,163,184,0.10);
    }

    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, rgba(17,24,39,0.95), rgba(30,41,59,0.92));
        border: 1px solid rgba(148,163,184,0.16);
        padding: 14px;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    }

    button[data-baseweb="tab"] {
        border-radius: 10px !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================
st.markdown('<div class="main-title">NILE • FINAL V12.4.2 CLOUD HOTFIX MASTER</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Institutional-style Indian Market Dashboard • Technical + Fundamental + Premium Visual • Cloud Safe Hotfix</div>', unsafe_allow_html=True)

# =========================================================
# NIFTY STOCKS
# =========================================================
NIFTY_100 = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "INFY": "INFY.NS",
    "SBIN": "SBIN.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "LT": "LT.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "AXISBANK": "AXISBANK.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "MARUTI": "MARUTI.NS",
    "HCLTECH": "HCLTECH.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
    "TITAN": "TITAN.NS",
    "WIPRO": "WIPRO.NS",
    "NESTLEIND": "NESTLEIND.NS",
    "POWERGRID": "POWERGRID.NS",
    "NTPC": "NTPC.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "M&M": "M&M.NS",
    "ADANIENT": "ADANIENT.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "ONGC": "ONGC.NS",
    "TECHM": "TECHM.NS",
    "COALINDIA": "COALINDIA.NS",
    "JSWSTEEL": "JSWSTEEL.NS",
    "TATASTEEL": "TATASTEEL.NS",
    "INDUSINDBK": "INDUSINDBK.NS",
    "HINDALCO": "HINDALCO.NS",
    "GRASIM": "GRASIM.NS",
    "CIPLA": "CIPLA.NS",
    "DRREDDY": "DRREDDY.NS",
    "APOLLOHOSP": "APOLLOHOSP.NS",
    "ADANIPORTS": "ADANIPORTS.NS",
    "EICHERMOT": "EICHERMOT.NS"
}

# NOTE:
# Yahoo sometimes fails for ^NSEBANK / ^INDIAVIX on cloud.
# We include safer alternate ETFs if index fails.
INDEX_SYMBOLS = {
    "NIFTY 50": ["^NSEI", "NIFTYBEES.NS"],
    "BANK NIFTY": ["^NSEBANK", "BANKBEES.NS"],
    "INDIA VIX": ["^INDIAVIX"]
}

# =========================================================
# HELPERS
# =========================================================
def safe_float(v, default=np.nan):
    try:
        if v is None:
            return default
        if isinstance(v, (pd.Series, pd.DataFrame)):
            return default
        val = float(v)
        if np.isinf(val):
            return default
        return val
    except Exception:
        return default

def safe_int_text(v):
    val = safe_float(v)
    if np.isnan(val):
        return "N/A"
    try:
        return f"{int(val):,}"
    except Exception:
        return "N/A"

def safe_money(v, prefix="₹ "):
    val = safe_float(v)
    if np.isnan(val):
        return "N/A"
    return f"{prefix}{val:,.2f}"

def safe_pct(v, multiplier=1):
    val = safe_float(v)
    if np.isnan(val):
        return "N/A"
    return f"{val * multiplier:.2f}%"

def flatten_columns(df):
    if df is None or df.empty:
        return df

    if isinstance(df.columns, pd.MultiIndex):
        try:
            df.columns = df.columns.get_level_values(0)
        except Exception:
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

    # remove duplicate columns if any
    df = df.loc[:, ~df.columns.duplicated()]
    return df

@st.cache_data(ttl=300, show_spinner=False)
def fetch_history(symbol, period="6mo", interval="1d"):
    try:
        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            auto_adjust=False,
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            return pd.DataFrame()

        df = flatten_columns(df)
        df = df.dropna(how="all")

        required_cols = ["Open", "High", "Low", "Close"]
        for col in required_cols:
            if col not in df.columns:
                return pd.DataFrame()

        # Make sure numeric columns are numeric
        for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def fetch_info(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if isinstance(info, dict):
            return info
        return {}
    except Exception:
        return {}

def calculate_rsi(series, period=14):
    series = pd.to_numeric(series, errors="coerce")
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    loss = loss.replace(0, np.nan)
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def add_indicators(df):
    if df.empty or "Close" not in df.columns:
        return df

    df = df.copy()
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["RSI"] = calculate_rsi(df["Close"], 14)
    df["52W_High"] = df["Close"].rolling(252, min_periods=1).max()
    df["52W_Low"] = df["Close"].rolling(252, min_periods=1).min()
    return df

def get_signal(df):
    if df.empty or len(df) < 60:
        return "HOLD", "Insufficient data"

    last = df.iloc[-1]

    price = safe_float(last.get("Close"))
    sma20 = safe_float(last.get("SMA20"))
    sma50 = safe_float(last.get("SMA50"))
    rsi = safe_float(last.get("RSI"))

    bullish = 0
    bearish = 0

    if not np.isnan(price) and not np.isnan(sma20) and not np.isnan(sma50):
        if price > sma20 > sma50:
            bullish += 1
        if price < sma20 < sma50:
            bearish += 1

    if not np.isnan(rsi):
        if 50 < rsi < 70:
            bullish += 1
        if rsi > 75:
            bearish += 1
        if rsi < 30:
            bullish += 1

    if bullish >= 2:
        return "BUY", "Trend + Momentum supportive"
    elif bearish >= 2:
        return "SELL", "Weak trend / overheated"
    else:
        return "HOLD", "Mixed structure"

def get_signal_badge(signal):
    if signal == "BUY":
        return '<span class="badge-buy">BUY</span>'
    elif signal == "SELL":
        return '<span class="badge-sell">SELL</span>'
    return '<span class="badge-hold">HOLD</span>'

def get_index_snapshot(symbol_candidates):
    # symbol_candidates is list for fallback support
    for symbol in symbol_candidates:
        df = fetch_history(symbol, period="7d", interval="1d")
        if df.empty or "Close" not in df.columns:
            continue

        df = df.dropna(subset=["Close"])
        if df.empty:
            continue

        last_close = safe_float(df["Close"].iloc[-1])
        prev_close = safe_float(df["Close"].iloc[-2]) if len(df) > 1 else last_close

        if np.isnan(last_close):
            continue

        if np.isnan(prev_close) or prev_close == 0:
            change = 0.0
            pct = 0.0
        else:
            change = last_close - prev_close
            pct = (change / prev_close) * 100

        return {
            "value": last_close,
            "change": change,
            "pct": pct,
            "source": symbol
        }

    return None

def render_market_card(title, data):
    if not data or np.isnan(safe_float(data.get("value"))):
        st.markdown(f"""
        <div class="pulse-neutral">
            <div class="card-title">{title}</div>
            <div class="card-value">N/A</div>
            <div class="card-change">Data unavailable</div>
        </div>
        """, unsafe_allow_html=True)
        return

    value = safe_float(data.get("value"))
    change = safe_float(data.get("change"), 0.0)
    pct = safe_float(data.get("pct"), 0.0)

    cls = "pulse-green" if change >= 0 else "pulse-red"
    arrow = "▲" if change >= 0 else "▼"

    st.markdown(f"""
    <div class="{cls}">
        <div class="card-title">{title}</div>
        <div class="card-value">{value:,.2f}</div>
        <div class="card-change">{arrow} {change:,.2f} ({pct:.2f}%)</div>
    </div>
    """, unsafe_allow_html=True)

def stock_score(df, info):
    if df.empty:
        return 0

    score = 0
    last = df.iloc[-1]

    price = safe_float(last.get("Close"))
    sma20 = safe_float(last.get("SMA20"))
    sma50 = safe_float(last.get("SMA50"))
    rsi = safe_float(last.get("RSI"))

    if not np.isnan(price) and not np.isnan(sma20) and price > sma20:
        score += 20
    if not np.isnan(price) and not np.isnan(sma50) and price > sma50:
        score += 20
    if not np.isnan(sma20) and not np.isnan(sma50) and sma20 > sma50:
        score += 15
    if not np.isnan(rsi) and 45 <= rsi <= 70:
        score += 15

    roe = safe_float(info.get("returnOnEquity"))
    if not np.isnan(roe):
        if roe > 0.15:
            score += 15
        elif roe > 0.08:
            score += 8

    pe = safe_float(info.get("trailingPE"))
    if not np.isnan(pe):
        if 0 < pe < 35:
            score += 15
        elif pe < 50:
            score += 8

    return min(score, 100)

def create_candlestick_chart(df, title):
    if df.empty:
        return go.Figure()

    plot_df = df.copy().dropna(subset=["Open", "High", "Low", "Close"])
    if plot_df.empty:
        return go.Figure()

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=plot_df.index,
        open=plot_df["Open"],
        high=plot_df["High"],
        low=plot_df["Low"],
        close=plot_df["Close"],
        name="Price"
    ))

    if "SMA20" in plot_df.columns:
        fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["SMA20"], mode="lines", name="SMA20"))
    if "SMA50" in plot_df.columns:
        fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["SMA50"], mode="lines", name="SMA50"))

    fig.update_layout(
        title=title,
        template="plotly_dark",
        height=520,
        xaxis_rangeslider_visible=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h")
    )
    return fig

def create_rsi_chart(df):
    fig = go.Figure()

    if not df.empty and "RSI" in df.columns:
        plot_df = df.dropna(subset=["RSI"])
        if not plot_df.empty:
            fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["RSI"], mode="lines", name="RSI"))

    fig.add_hline(y=70, line_dash="dash")
    fig.add_hline(y=30, line_dash="dash")
    fig.update_layout(
        title="RSI (14)",
        template="plotly_dark",
        height=260,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## ⚙️ Control Center")

selected_stock = st.sidebar.selectbox(
    "Select NSE Stock",
    options=list(NIFTY_100.keys()),
    index=2
)

symbol = NIFTY_100[selected_stock]

period = st.sidebar.selectbox(
    "Chart Period",
    ["3mo", "6mo", "1y", "2y", "5y"],
    index=1
)

scanner_limit = st.sidebar.slider("Scanner Stocks", 5, 20, 10)

refresh_btn = st.sidebar.button("🔄 Refresh Dashboard")
analyze_btn = st.sidebar.button("📊 Run Full Analysis")
scan_btn = st.sidebar.button("🚀 Run Scanner")

if refresh_btn:
    st.cache_data.clear()

# =========================================================
# TOP MARKET PULSE
# =========================================================
st.markdown('<div class="section-title">📡 Live Market Pulse</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    render_market_card("NIFTY 50", get_index_snapshot(INDEX_SYMBOLS["NIFTY 50"]))
with col2:
    render_market_card("BANK NIFTY", get_index_snapshot(INDEX_SYMBOLS["BANK NIFTY"]))
with col3:
    render_market_card("INDIA VIX", get_index_snapshot(INDEX_SYMBOLS["INDIA VIX"]))

# =========================================================
# MAIN STOCK DATA
# =========================================================
hist = fetch_history(symbol, period=period, interval="1d")
hist = add_indicators(hist)

if hist.empty:
    st.error("Unable to fetch stock data right now. Please refresh or choose another stock.")
    st.stop()

hist = hist.dropna(subset=["Close"])

if hist.empty:
    st.error("No valid close price data available for this stock right now.")
    st.stop()

info = fetch_info(symbol)

last = hist.iloc[-1]
prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else hist["Close"].iloc[-1]

price = safe_float(last.get("Close"))
prev_close_val = safe_float(prev_close)

if np.isnan(price):
    st.error("Latest price unavailable right now. Please refresh or choose another stock.")
    st.stop()

day_change = price - prev_close_val if not np.isnan(prev_close_val) else 0.0
day_change_pct = (day_change / prev_close_val * 100) if not np.isnan(prev_close_val) and prev_close_val != 0 else 0.0

signal, signal_reason = get_signal(hist)

# =========================================================
# HERO STOCK SUMMARY
# =========================================================
st.markdown('<div class="section-title">🎯 Selected Stock Command Center</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

safe_volume = safe_float(last.get("Volume")) if "Volume" in hist.columns else np.nan
safe_rsi = safe_float(last.get("RSI")) if "RSI" in hist.columns else np.nan

with c1:
    st.metric("Stock", selected_stock)

with c2:
    price_text = f"₹ {price:,.2f}" if not np.isnan(price) else "N/A"
    delta_text = f"{day_change:,.2f} ({day_change_pct:.2f}%)" if not np.isnan(day_change) and not np.isnan(day_change_pct) else "N/A"
    st.metric("Price", price_text, delta_text)

with c3:
    st.metric("Volume", safe_int_text(safe_volume))

with c4:
    rsi_text = f"{safe_rsi:.2f}" if not np.isnan(safe_rsi) else "N/A"
    st.metric("RSI", rsi_text)

with c5:
    st.markdown(get_signal_badge(signal), unsafe_allow_html=True)
    st.caption(signal_reason)

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Technical Analysis",
    "🏦 Fundamental Analysis",
    "🧾 Balance Sheet View",
    "🚀 Scanner",
    "⭐ Watchlist Snapshot"
])

# =========================================================
# TAB 1 - TECHNICAL
# =========================================================
with tab1:
    st.markdown('<div class="section-title">📈 Technical Analysis</div>', unsafe_allow_html=True)

    st.plotly_chart(
        create_candlestick_chart(hist.tail(180), f"{selected_stock} Price Action"),
        use_container_width=True
    )

    cta1, cta2, cta3 = st.columns(3)
    with cta1:
        st.button("🟢 BUY Zone")
    with cta2:
        st.button("🟡 HOLD Zone")
    with cta3:
        st.button("🔴 SELL Zone")

    last_sma20 = safe_float(last.get("SMA20"))
    last_sma50 = safe_float(last.get("SMA50"))
    last_52h = safe_float(last.get("52W_High"))
    last_52l = safe_float(last.get("52W_Low"))

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("SMA20", safe_money(last_sma20))
    r2.metric("SMA50", safe_money(last_sma50))
    r3.metric("52W High", safe_money(last_52h))
    r4.metric("52W Low", safe_money(last_52l))

    st.plotly_chart(create_rsi_chart(hist.tail(180)), use_container_width=True)

    price_vs_sma20 = "Above" if not np.isnan(last_sma20) and price > last_sma20 else "Below / N/A"
    price_vs_sma50 = "Above" if not np.isnan(last_sma50) and price > last_sma50 else "Below / N/A"
    rsi_display = f"{safe_rsi:.2f}" if not np.isnan(safe_rsi) else "N/A"

    st.info(
        f"""
**Trend Read:**  
- Price is **{price_vs_sma20} SMA20**  
- Price is **{price_vs_sma50} SMA50**  
- Current RSI = **{rsi_display}**  
- Signal = **{signal}**
"""
    )

# =========================================================
# TAB 2 - FUNDAMENTAL
# =========================================================
with tab2:
    st.markdown('<div class="section-title">🏦 Fundamental Analysis</div>', unsafe_allow_html=True)

    market_cap = safe_float(info.get("marketCap"))
    trailing_pe = safe_float(info.get("trailingPE"))
    forward_pe = safe_float(info.get("forwardPE"))
    pb = safe_float(info.get("priceToBook"))
    roe = safe_float(info.get("returnOnEquity"))
    roa = safe_float(info.get("returnOnAssets"))
    div_yield = safe_float(info.get("dividendYield"))
    beta = safe_float(info.get("beta"))
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    long_name = info.get("longName", selected_stock)

    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Company", str(long_name))
    f2.metric("Sector", str(sector))
    f3.metric("Industry", str(industry))
    f4.metric("Market Cap", f"₹ {market_cap:,.0f}" if not np.isnan(market_cap) else "N/A")

    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Trailing PE", f"{trailing_pe:.2f}" if not np.isnan(trailing_pe) else "N/A")
    g2.metric("Forward PE", f"{forward_pe:.2f}" if not np.isnan(forward_pe) else "N/A")
    g3.metric("Price to Book", f"{pb:.2f}" if not np.isnan(pb) else "N/A")
    g4.metric("Beta", f"{beta:.2f}" if not np.isnan(beta) else "N/A")

    h1, h2, h3 = st.columns(3)
    h1.metric("ROE", f"{roe*100:.2f}%" if not np.isnan(roe) else "N/A")
    h2.metric("ROA", f"{roa*100:.2f}%" if not np.isnan(roa) else "N/A")
    h3.metric("Dividend Yield", f"{div_yield*100:.2f}%" if not np.isnan(div_yield) else "N/A")

    fundamental_score = stock_score(hist, info)

    st.markdown("### Fundamental Verdict")
    if fundamental_score >= 75:
        st.success(f"Strong Fundamental + Technical Composite Score: **{fundamental_score}/100**")
    elif fundamental_score >= 50:
        st.warning(f"Balanced / Moderate Composite Score: **{fundamental_score}/100**")
    else:
        st.error(f"Weak / Risky Composite Score: **{fundamental_score}/100**")

# =========================================================
# TAB 3 - BALANCE SHEET VIEW
# =========================================================
with tab3:
    st.markdown('<div class="section-title">🧾 Balance Sheet Style Snapshot</div>', unsafe_allow_html=True)

    bs_rows = {
        "Total Revenue": safe_float(info.get("totalRevenue")),
        "Gross Profits": safe_float(info.get("grossProfits")),
        "EBITDA": safe_float(info.get("ebitda")),
        "Operating Cashflow": safe_float(info.get("operatingCashflow")),
        "Free Cashflow": safe_float(info.get("freeCashflow")),
        "Total Cash": safe_float(info.get("totalCash")),
        "Total Debt": safe_float(info.get("totalDebt")),
        "Book Value": safe_float(info.get("bookValue")),
        "Current Ratio": safe_float(info.get("currentRatio")),
        "Debt to Equity": safe_float(info.get("debtToEquity")),
        "Profit Margins": safe_float(info.get("profitMargins")),
        "Operating Margins": safe_float(info.get("operatingMargins"))
    }

    bs_df = pd.DataFrame({
        "Metric": list(bs_rows.keys()),
        "Value": list(bs_rows.values())
    })

    def format_value(metric, val):
        if np.isnan(val):
            return "N/A"
        if metric in ["Current Ratio", "Debt to Equity"]:
            return f"{val:.2f}"
        if metric in ["Profit Margins", "Operating Margins"]:
            return f"{val*100:.2f}%"
        return f"{val:,.0f}"

    bs_df["Formatted"] = [format_value(m, v) for m, v in zip(bs_df["Metric"], bs_df["Value"])]
    st.dataframe(bs_df[["Metric", "Formatted"]], use_container_width=True, hide_index=True)

    debt = safe_float(info.get("totalDebt"))
    cash = safe_float(info.get("totalCash"))

    st.markdown("### Quick Balance Sheet Read")
    if not np.isnan(debt) and not np.isnan(cash):
        if cash > debt:
            st.success("Cash position appears stronger than total debt.")
        else:
            st.warning("Debt is higher than cash — review leverage carefully.")
    else:
        st.info("Detailed balance sheet values partially unavailable from data source.")

# =========================================================
# TAB 4 - SCANNER
# =========================================================
with tab4:
    st.markdown('<div class="section-title">🚀 Mini Institutional Scanner</div>', unsafe_allow_html=True)

    if scan_btn or True:
        scan_symbols = list(NIFTY_100.items())[:scanner_limit]
        scan_results = []

        progress = st.progress(0)

        for idx, (name, sym) in enumerate(scan_symbols):
            try:
                df_scan = fetch_history(sym, period="6mo", interval="1d")
                df_scan = add_indicators(df_scan)

                if df_scan.empty:
                    progress.progress((idx + 1) / len(scan_symbols))
                    continue

                df_scan = df_scan.dropna(subset=["Close"])
                if df_scan.empty:
                    progress.progress((idx + 1) / len(scan_symbols))
                    continue

                info_scan = fetch_info(sym)
                sig, reason = get_signal(df_scan)
                score = stock_score(df_scan, info_scan)

                last_price = safe_float(df_scan["Close"].iloc[-1])
                rsi_val = safe_float(df_scan["RSI"].iloc[-1]) if "RSI" in df_scan.columns else np.nan

                scan_results.append({
                    "Stock": name,
                    "Symbol": sym,
                    "Price": round(last_price, 2) if not np.isnan(last_price) else None,
                    "RSI": round(rsi_val, 2) if not np.isnan(rsi_val) else None,
                    "Signal": sig,
                    "Score": score,
                    "Reason": reason
                })

            except Exception:
                pass

            progress.progress((idx + 1) / len(scan_symbols))

        progress.empty()

        if scan_results:
            scan_df = pd.DataFrame(scan_results).sort_values(by=["Score", "Stock"], ascending=[False, True])
            st.dataframe(scan_df, use_container_width=True, hide_index=True)

            st.markdown("### 🏆 Top 5 Scanner Picks")
            st.dataframe(scan_df.head(5), use_container_width=True, hide_index=True)
        else:
            st.warning("Scanner could not fetch enough data right now.")

# =========================================================
# TAB 5 - WATCHLIST
# =========================================================
with tab5:
    st.markdown('<div class="section-title">⭐ Premium Watchlist Snapshot</div>', unsafe_allow_html=True)

    watchlist_names = ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "SBIN"]
    watch_rows = []

    for nm in watchlist_names:
        sym = NIFTY_100.get(nm)
        if not sym:
            continue

        try:
            df_w = fetch_history(sym, period="3mo", interval="1d")
            df_w = add_indicators(df_w)

            if df_w.empty:
                continue

            df_w = df_w.dropna(subset=["Close"])
            if df_w.empty:
                continue

            sig, _ = get_signal(df_w)
            last_price = safe_float(df_w["Close"].iloc[-1])
            prev = safe_float(df_w["Close"].iloc[-2]) if len(df_w) > 1 else last_price

            if np.isnan(last_price):
                continue

            chg = last_price - prev if not np.isnan(prev) else 0
            chg_pct = (chg / prev * 100) if not np.isnan(prev) and prev != 0 else 0
            score = stock_score(df_w, fetch_info(sym))

            watch_rows.append({
                "Stock": nm,
                "Price": round(last_price, 2),
                "Day Change %": round(chg_pct, 2),
                "Signal": sig,
                "Score": score
            })
        except Exception:
            pass

    if watch_rows:
        watch_df = pd.DataFrame(watch_rows).sort_values(by="Score", ascending=False)
        st.dataframe(watch_df, use_container_width=True, hide_index=True)

        fig_watch = px.bar(
            watch_df,
            x="Stock",
            y="Score",
            title="Watchlist Score Comparison",
            text="Score"
        )
        fig_watch.update_layout(
            template="plotly_dark",
            height=420,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_watch, use_container_width=True)
    else:
        st.info("Watchlist data unavailable right now.")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption(
    f"Last refreshed: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} | "
    "Data Source: Yahoo Finance (via yfinance) | Educational use only"
)

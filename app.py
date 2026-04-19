import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="NILE • Visual Masterpiece Pro",
    layout="wide",
    page_icon="📈"
)

# =========================
# PREMIUM CSS THEME
# =========================
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0b1020 0%, #111827 35%, #0f172a 100%);
        color: #e5e7eb;
    }

    /* Header title */
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
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

    /* Premium card */
    .premium-card {
        background: linear-gradient(145deg, rgba(17,24,39,0.95), rgba(30,41,59,0.92));
        border: 1px solid rgba(148,163,184,0.18);
        border-radius: 20px;
        padding: 18px 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.35);
        margin-bottom: 12px;
    }

    .pulse-green {
        background: linear-gradient(135deg, rgba(6,78,59,0.95), rgba(5,150,105,0.85));
        border: 1px solid rgba(16,185,129,0.35);
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 8px 24px rgba(16,185,129,0.15);
    }

    .pulse-red {
        background: linear-gradient(135deg, rgba(127,29,29,0.95), rgba(220,38,38,0.82));
        border: 1px solid rgba(248,113,113,0.35);
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 8px 24px rgba(239,68,68,0.15);
    }

    .pulse-neutral {
        background: linear-gradient(135deg, rgba(30,41,59,0.95), rgba(51,65,85,0.9));
        border: 1px solid rgba(148,163,184,0.22);
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 8px 24px rgba(148,163,184,0.08);
    }

    .card-title {
        font-size: 0.9rem;
        color: #d1d5db;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .card-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 4px;
    }

    .card-change {
        font-size: 0.95rem;
        font-weight: 700;
        color: #d1fae5;
    }

    .section-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #f8fafc;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
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

    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 14px;
        border: none;
        padding: 0.7rem 1rem;
        font-weight: 800;
        color: white;
        background: linear-gradient(90deg, #2563eb, #06b6d4);
        box-shadow: 0 8px 18px rgba(37,99,235,0.35);
        transition: all 0.2s ease-in-out;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(6,182,212,0.35);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        border-right: 1px solid rgba(148,163,184,0.12);
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, rgba(17,24,39,0.95), rgba(30,41,59,0.92));
        border: 1px solid rgba(148,163,184,0.18);
        padding: 14px;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        border-radius: 10px !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.markdown('<div class="main-title">NILE • FINAL V12.4.1 VISUAL MASTERPIECE PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Institutional-style Indian Market Dashboard • Technical + Fundamental + Visual Premium • Cloud Safe</div>', unsafe_allow_html=True)

# =========================
# NIFTY 100 SYMBOL LIST (NSE)
# =========================
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

# Index symbols
INDEX_SYMBOLS = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "INDIA VIX": "^INDIAVIX"
}

# =========================
# HELPERS
# =========================
@st.cache_data(ttl=300, show_spinner=False)
def fetch_history(symbol, period="6mo", interval="1d"):
    try:
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=False, progress=False)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.dropna()
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def fetch_info(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info if isinstance(info, dict) else {}
    except Exception:
        return {}

def safe_float(v, default=np.nan):
    try:
        if v is None:
            return default
        return float(v)
    except Exception:
        return default

def format_indian_number(num):
    try:
        num = float(num)
        abs_num = abs(num)
        if abs_num >= 1e7:
            return f"₹ {num/1e7:,.2f} Cr"
        elif abs_num >= 1e5:
            return f"₹ {num/1e5:,.2f} L"
        else:
            return f"₹ {num:,.2f}"
    except Exception:
        return "N/A"

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def add_indicators(df):
    if df.empty or "Close" not in df.columns:
        return df
    df = df.copy()
    close = df["Close"]
    df["SMA20"] = close.rolling(20).mean()
    df["SMA50"] = close.rolling(50).mean()
    df["EMA20"] = close.ewm(span=20, adjust=False).mean()
    df["EMA50"] = close.ewm(span=50, adjust=False).mean()
    df["RSI"] = calculate_rsi(close, 14)
    df["52W_High"] = close.rolling(252, min_periods=1).max()
    df["52W_Low"] = close.rolling(252, min_periods=1).min()
    return df

def get_signal(df):
    if df.empty or len(df) < 60:
        return "HOLD", "Insufficient data"
    last = df.iloc[-1]
    price = safe_float(last["Close"])
    sma20 = safe_float(last["SMA20"])
    sma50 = safe_float(last["SMA50"])
    rsi = safe_float(last["RSI"])

    bullish = 0
    bearish = 0

    if price > sma20 > sma50:
        bullish += 1
    if price < sma20 < sma50:
        bearish += 1

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
    else:
        return '<span class="badge-hold">HOLD</span>'

def create_candlestick_chart(df, title):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price"
    ))
    if "SMA20" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], mode="lines", name="SMA20"))
    if "SMA50" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], mode="lines", name="SMA50"))

    fig.update_layout(
        title=title,
        template="plotly_dark",
        height=500,
        xaxis_rangeslider_visible=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h")
    )
    return fig

def create_rsi_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines", name="RSI"))
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

def get_index_snapshot(symbol):
    df = fetch_history(symbol, period="7d", interval="1d")
    if df.empty:
        return None
    last = df.iloc[-1]
    prev_close = df["Close"].iloc[-2] if len(df) > 1 else last["Close"]
    value = safe_float(last["Close"])
    change = value - safe_float(prev_close)
    pct = (change / safe_float(prev_close) * 100) if safe_float(prev_close) else 0
    return {
        "value": value,
        "change": change,
        "pct": pct
    }

def render_market_card(title, data):
    if not data:
        st.markdown(f"""
        <div class="pulse-neutral">
            <div class="card-title">{title}</div>
            <div class="card-value">N/A</div>
            <div class="card-change">Data unavailable</div>
        </div>
        """, unsafe_allow_html=True)
        return

    cls = "pulse-green" if data["change"] >= 0 else "pulse-red"
    arrow = "▲" if data["change"] >= 0 else "▼"
    st.markdown(f"""
    <div class="{cls}">
        <div class="card-title">{title}</div>
        <div class="card-value">{data["value"]:,.2f}</div>
        <div class="card-change">{arrow} {data["change"]:,.2f} ({data["pct"]:.2f}%)</div>
    </div>
    """, unsafe_allow_html=True)

def stock_score(df, info):
    if df.empty:
        return 0
    score = 0
    last = df.iloc[-1]
    price = safe_float(last["Close"])
    sma20 = safe_float(last.get("SMA20", np.nan))
    sma50 = safe_float(last.get("SMA50", np.nan))
    rsi = safe_float(last.get("RSI", np.nan))

    if price > sma20:
        score += 20
    if price > sma50:
        score += 20
    if sma20 > sma50:
        score += 15
    if 45 <= rsi <= 70:
        score += 15

    roe = safe_float(info.get("returnOnEquity", np.nan))
    if not np.isnan(roe):
        if roe > 0.15:
            score += 15
        elif roe > 0.08:
            score += 8

    pe = safe_float(info.get("trailingPE", np.nan))
    if not np.isnan(pe):
        if 0 < pe < 35:
            score += 15
        elif pe < 50:
            score += 8

    return min(score, 100)

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("## ⚙️ Control Center")

selected_stock = st.sidebar.selectbox(
    "Select NSE Stock",
    options=list(NIFTY_100.keys()),
    index=0
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

# =========================
# TOP MARKET PULSE CARDS
# =========================
st.markdown('<div class="section-title">📡 Live Market Pulse</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    render_market_card("NIFTY 50", get_index_snapshot(INDEX_SYMBOLS["NIFTY 50"]))
with col2:
    render_market_card("BANK NIFTY", get_index_snapshot(INDEX_SYMBOLS["BANK NIFTY"]))
with col3:
    render_market_card("INDIA VIX", get_index_snapshot(INDEX_SYMBOLS["INDIA VIX"]))

# =========================
# MAIN DATA
# =========================
if refresh_btn:
    st.cache_data.clear()

hist = fetch_history(symbol, period=period, interval="1d")
hist = add_indicators(hist)
info = fetch_info(symbol)

if hist.empty:
    st.error("Unable to fetch stock data right now. Please try another stock or refresh.")
    st.stop()

last = hist.iloc[-1]
prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else hist["Close"].iloc[-1]
price = safe_float(last["Close"])
day_change = price - safe_float(prev_close)
day_change_pct = (day_change / safe_float(prev_close) * 100) if safe_float(prev_close) else 0

signal, signal_reason = get_signal(hist)

# =========================
# HERO STOCK SUMMARY
# =========================
st.markdown('<div class="section-title">🎯 Selected Stock Command Center</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric("Stock", selected_stock)
with c2:
    st.metric("Price", f"₹ {price:,.2f}", f"{day_change:,.2f} ({day_change_pct:.2f}%)")
with c3:
    st.metric("Volume", f"{int(last['Volume']):,}" if "Volume" in hist.columns else "N/A")
with c4:
    st.metric("RSI", f"{safe_float(last['RSI']):.2f}" if "RSI" in hist.columns and not np.isnan(safe_float(last["RSI"])) else "N/A")
with c5:
    st.markdown(get_signal_badge(signal), unsafe_allow_html=True)
    st.caption(signal_reason)

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Technical Analysis",
    "🏦 Fundamental Analysis",
    "🧾 Balance Sheet View",
    "🚀 Scanner",
    "⭐ Watchlist Snapshot"
])

# =========================
# TAB 1 - TECHNICAL
# =========================
with tab1:
    st.markdown('<div class="section-title">📈 Technical Analysis</div>', unsafe_allow_html=True)

    fig = create_candlestick_chart(hist.tail(180), f"{selected_stock} Price Action")
    st.plotly_chart(fig, use_container_width=True)

    cta1, cta2, cta3 = st.columns(3)
    with cta1:
        st.button("🟢 BUY Zone")
    with cta2:
        st.button("🟡 HOLD Zone")
    with cta3:
        st.button("🔴 SELL Zone")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("SMA20", f"₹ {safe_float(last['SMA20']):.2f}" if not np.isnan(safe_float(last["SMA20"])) else "N/A")
    r2.metric("SMA50", f"₹ {safe_float(last['SMA50']):.2f}" if not np.isnan(safe_float(last["SMA50"])) else "N/A")
    r3.metric("52W High", f"₹ {safe_float(last['52W_High']):.2f}" if not np.isnan(safe_float(last["52W_High"])) else "N/A")
    r4.metric("52W Low", f"₹ {safe_float(last['52W_Low']):.2f}" if not np.isnan(safe_float(last["52W_Low"])) else "N/A")

    st.plotly_chart(create_rsi_chart(hist.tail(180)), use_container_width=True)

    st.markdown("### Technical Insight")
    price_vs_sma20 = "Above" if price > safe_float(last["SMA20"]) else "Below"
    price_vs_sma50 = "Above" if price > safe_float(last["SMA50"]) else "Below"
    st.info(
        f"""
        **Trend Read:**  
        - Price is **{price_vs_sma20} SMA20**
        - Price is **{price_vs_sma50} SMA50**
        - Current RSI = **{safe_float(last['RSI']):.2f}**
        - Signal = **{signal}**
        """
    )

# =========================
# TAB 2 - FUNDAMENTAL
# =========================
with tab2:
    st.markdown('<div class="section-title">🏦 Fundamental Analysis</div>', unsafe_allow_html=True)

    market_cap = safe_float(info.get("marketCap", np.nan))
    trailing_pe = safe_float(info.get("trailingPE", np.nan))
    forward_pe = safe_float(info.get("forwardPE", np.nan))
    pb = safe_float(info.get("priceToBook", np.nan))
    roe = safe_float(info.get("returnOnEquity", np.nan))
    roa = safe_float(info.get("returnOnAssets", np.nan))
    div_yield = safe_float(info.get("dividendYield", np.nan))
    beta = safe_float(info.get("beta", np.nan))
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    long_name = info.get("longName", selected_stock)

    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Company", long_name)
    f2.metric("Sector", sector)
    f3.metric("Industry", industry)
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

    st.markdown("### Fundamental Verdict")
    fundamental_score = stock_score(hist, info)

    if fundamental_score >= 75:
        st.success(f"Strong Fundamental + Technical Composite Score: **{fundamental_score}/100**")
    elif fundamental_score >= 50:
        st.warning(f"Balanced / Moderate Composite Score: **{fundamental_score}/100**")
    else:
        st.error(f"Weak / Risky Composite Score: **{fundamental_score}/100**")

# =========================
# TAB 3 - BALANCE SHEET VIEW
# =========================
with tab3:
    st.markdown('<div class="section-title">🧾 Balance Sheet Style Snapshot</div>', unsafe_allow_html=True)

    bs_rows = {
        "Total Revenue": safe_float(info.get("totalRevenue", np.nan)),
        "Gross Profits": safe_float(info.get("grossProfits", np.nan)),
        "EBITDA": safe_float(info.get("ebitda", np.nan)),
        "Operating Cashflow": safe_float(info.get("operatingCashflow", np.nan)),
        "Free Cashflow": safe_float(info.get("freeCashflow", np.nan)),
        "Total Cash": safe_float(info.get("totalCash", np.nan)),
        "Total Debt": safe_float(info.get("totalDebt", np.nan)),
        "Book Value": safe_float(info.get("bookValue", np.nan)),
        "Current Ratio": safe_float(info.get("currentRatio", np.nan)),
        "Debt to Equity": safe_float(info.get("debtToEquity", np.nan)),
        "Profit Margins": safe_float(info.get("profitMargins", np.nan)),
        "Operating Margins": safe_float(info.get("operatingMargins", np.nan))
    }

    bs_df = pd.DataFrame({
        "Metric": list(bs_rows.keys()),
        "Value": list(bs_rows.values())
    })

    def format_value(row):
        val = row["Value"]
        if np.isnan(val):
            return "N/A"
        if row["Metric"] in ["Current Ratio", "Debt to Equity"]:
            return f"{val:.2f}"
        if row["Metric"] in ["Profit Margins", "Operating Margins"]:
            return f"{val*100:.2f}%"
        return f"{val:,.0f}"

    bs_df["Formatted"] = bs_df.apply(format_value, axis=1)
    st.dataframe(bs_df[["Metric", "Formatted"]], use_container_width=True, hide_index=True)

    st.markdown("### Quick Balance Sheet Read")
    debt = safe_float(info.get("totalDebt", np.nan))
    cash = safe_float(info.get("totalCash", np.nan))
    if not np.isnan(debt) and not np.isnan(cash):
        if cash > debt:
            st.success("Cash position appears stronger than total debt.")
        else:
            st.warning("Debt is higher than cash — review leverage carefully.")
    else:
        st.info("Detailed balance sheet values partially unavailable from data source.")

# =========================
# TAB 4 - SCANNER
# =========================
with tab4:
    st.markdown('<div class="section-title">🚀 Mini Institutional Scanner</div>', unsafe_allow_html=True)

    if scan_btn or True:
        scan_symbols = list(NIFTY_100.items())[:scanner_limit]
        scan_results = []

        progress = st.progress(0)
        for idx, (name, sym) in enumerate(scan_symbols):
            df_scan = fetch_history(sym, period="6mo", interval="1d")
            df_scan = add_indicators(df_scan)
            info_scan = fetch_info(sym)

            if not df_scan.empty:
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

            progress.progress((idx + 1) / len(scan_symbols))

        progress.empty()

        if scan_results:
            scan_df = pd.DataFrame(scan_results).sort_values(by=["Score", "Signal"], ascending=[False, True])
            st.dataframe(scan_df, use_container_width=True, hide_index=True)

            top_picks = scan_df.head(5)
            st.markdown("### 🏆 Top 5 Scanner Picks")
            st.dataframe(top_picks, use_container_width=True, hide_index=True)
        else:
            st.warning("Scanner could not fetch enough data right now.")

# =========================
# TAB 5 - WATCHLIST SNAPSHOT
# =========================
with tab5:
    st.markdown('<div class="section-title">⭐ Premium Watchlist Snapshot</div>', unsafe_allow_html=True)

    watchlist_names = ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "SBIN"]
    watch_rows = []

    for nm in watchlist_names:
        sym = NIFTY_100.get(nm)
        if not sym:
            continue
        df_w = fetch_history(sym, period="3mo", interval="1d")
        df_w = add_indicators(df_w)
        if not df_w.empty:
            sig, _ = get_signal(df_w)
            last_price = safe_float(df_w["Close"].iloc[-1])
            prev = safe_float(df_w["Close"].iloc[-2]) if len(df_w) > 1 else last_price
            chg = last_price - prev
            chg_pct = (chg / prev * 100) if prev else 0
            score = stock_score(df_w, fetch_info(sym))

            watch_rows.append({
                "Stock": nm,
                "Price": round(last_price, 2),
                "Day Change %": round(chg_pct, 2),
                "Signal": sig,
                "Score": score
            })

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
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_watch, use_container_width=True)
    else:
        st.info("Watchlist data unavailable right now.")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption(
    f"Last refreshed: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} | "
    "Data Source: Yahoo Finance (via yfinance) | For educational use only"
)

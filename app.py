import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="NSE Stock Intelligence Pro MAX V5.1",
    page_icon="📈",
    layout="wide"
)

# =========================
# SAFE CSS
# =========================
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}
.metric-card {
    background: rgba(255,255,255,0.05);
    border-radius: 18px;
    padding: 16px;
    border: 1px solid rgba(255,255,255,0.08);
}
.big-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: white;
}
.small-sub {
    color: #cbd5e1;
    font-size: 0.95rem;
}
.stTabs [data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown('<div class="big-title">📊 NSE Stock Intelligence Pro MAX V5.1</div>', unsafe_allow_html=True)
st.markdown('<div class="small-sub">Cloud-Safe | Stable | Fast | Streamlit Deploy Ready</div>', unsafe_allow_html=True)
st.write("")

# =========================
# SAFE DEFAULT STOCK LIST
# =========================
NSE_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "LT.NS", "ITC.NS", "BHARTIARTL.NS", "AXISBANK.NS",
    "KOTAKBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS", "SUNPHARMA.NS"
]

# =========================
# SAFE DATA FUNCTIONS
# =========================
@st.cache_data(ttl=3600, show_spinner=False)
def get_stock_data(symbol, period="6mo"):
    try:
        df = yf.download(symbol, period=period, interval="1d", progress=False, auto_adjust=False)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def get_stock_info(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if not isinstance(info, dict):
            return {}
        return info
    except Exception:
        return {}

def calc_rsi(series, period=14):
    try:
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    except Exception:
        return pd.Series([50] * len(series), index=series.index)

def add_indicators(df):
    try:
        df = df.copy()
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["SMA50"] = df["Close"].rolling(50).mean()
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["RSI"] = calc_rsi(df["Close"], 14)
        return df
    except Exception:
        return df

def safe_float(val, default=0.0):
    try:
        if val is None:
            return default
        return float(val)
    except Exception:
        return default

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ Controls")
selected_stock = st.sidebar.selectbox("Select NSE Stock", NSE_STOCKS, index=0)
period = st.sidebar.selectbox("Select Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

st.sidebar.markdown("---")
investment_amount = st.sidebar.number_input("💰 Investment Amount (₹)", min_value=1000, value=100000, step=1000)
expected_return = st.sidebar.slider("📈 Expected Annual Return (%)", 1, 30, 12)
years = st.sidebar.slider("🕒 Years", 1, 30, 10)

# =========================
# LOAD DATA
# =========================
with st.spinner("Loading stock data safely..."):
    df = get_stock_data(selected_stock, period)
    info = get_stock_info(selected_stock)

# =========================
# HANDLE EMPTY DATA
# =========================
if df.empty:
    st.error("❌ Unable to fetch stock data right now. This is usually due to Yahoo Finance temporary issue or internet restriction.")
    st.info("✅ App is deployed correctly. Try changing stock or refresh after a minute.")
    st.stop()

# =========================
# PREP DATA
# =========================
df = add_indicators(df)

# Flatten columns if multiindex appears
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

latest_close = safe_float(df["Close"].iloc[-1])
prev_close = safe_float(df["Close"].iloc[-2]) if len(df) > 1 else latest_close
change = latest_close - prev_close
change_pct = (change / prev_close * 100) if prev_close != 0 else 0

# =========================
# TOP METRICS
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📌 Stock", selected_stock.replace(".NS", ""))
with col2:
    st.metric("💹 Current Price", f"₹{latest_close:,.2f}", f"{change_pct:.2f}%")
with col3:
    market_cap = safe_float(info.get("marketCap", 0)) / 1e7
    st.metric("🏦 Market Cap (Cr)", f"{market_cap:,.0f}" if market_cap > 0 else "N/A")
with col4:
    pe_ratio = info.get("trailingPE", "N/A")
    st.metric("📊 P/E Ratio", f"{pe_ratio}" if pe_ratio != "N/A" else "N/A")

st.markdown("---")

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Price Dashboard",
    "🧠 Technical Analysis",
    "💰 Investment Planner",
    "📋 Company Snapshot",
    "📊 Returns Analyzer"
])

# =========================
# TAB 1 - PRICE DASHBOARD
# =========================
with tab1:
    st.subheader("📈 Price Dashboard")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df["Date"],
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Candlestick"
    ))

    if "SMA20" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA20"], mode="lines", name="SMA20"))
    if "SMA50" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA50"], mode="lines", name="SMA50"))

    fig.update_layout(
        title=f"{selected_stock} Price Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Volume Analysis")
    vol_fig = px.bar(df, x="Date", y="Volume", title="Daily Volume")
    st.plotly_chart(vol_fig, use_container_width=True)

# =========================
# TAB 2 - TECHNICAL ANALYSIS
# =========================
with tab2:
    st.subheader("🧠 Technical Analysis")

    rsi_value = safe_float(df["RSI"].iloc[-1]) if "RSI" in df.columns else 50
    sma20 = safe_float(df["SMA20"].iloc[-1]) if "SMA20" in df.columns else latest_close
    sma50 = safe_float(df["SMA50"].iloc[-1]) if "SMA50" in df.columns else latest_close

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("RSI (14)", f"{rsi_value:.2f}")
    with c2:
        st.metric("SMA20", f"₹{sma20:,.2f}")
    with c3:
        st.metric("SMA50", f"₹{sma50:,.2f}")

    # Signals
    st.subheader("📢 Signal Engine")

    signal = "HOLD"
    signal_reason = []

    if latest_close > sma20 > sma50:
        signal = "BUY"
        signal_reason.append("Price above SMA20 and SMA50 (bullish trend)")
    elif latest_close < sma20 < sma50:
        signal = "SELL"
        signal_reason.append("Price below SMA20 and SMA50 (bearish trend)")
    else:
        signal_reason.append("Mixed moving average structure")

    if rsi_value > 70:
        signal_reason.append("RSI indicates overbought zone")
    elif rsi_value < 30:
        signal_reason.append("RSI indicates oversold zone")
    else:
        signal_reason.append("RSI is neutral")

    if signal == "BUY":
        st.success(f"✅ Signal: {signal}")
    elif signal == "SELL":
        st.error(f"❌ Signal: {signal}")
    else:
        st.warning(f"⚠️ Signal: {signal}")

    for reason in signal_reason:
        st.write(f"- {reason}")

    # RSI Chart
    rsi_fig = go.Figure()
    rsi_fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], mode="lines", name="RSI"))
    rsi_fig.add_hline(y=70, line_dash="dash")
    rsi_fig.add_hline(y=30, line_dash="dash")
    rsi_fig.update_layout(title="RSI Indicator", height=400)
    st.plotly_chart(rsi_fig, use_container_width=True)

# =========================
# TAB 3 - INVESTMENT PLANNER
# =========================
with tab3:
    st.subheader("💰 Investment Planner")

    future_value = investment_amount * ((1 + expected_return / 100) ** years)
    absolute_gain = future_value - investment_amount
    cagr = ((future_value / investment_amount) ** (1 / years) - 1) * 100 if investment_amount > 0 else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Invested Amount", f"₹{investment_amount:,.0f}")
    with c2:
        st.metric("Future Value", f"₹{future_value:,.0f}")
    with c3:
        st.metric("Absolute Gain", f"₹{absolute_gain:,.0f}")

    st.info(f"📌 Implied CAGR: {cagr:.2f}%")

    # Year-wise projection
    projection = []
    for yr in range(1, years + 1):
        val = investment_amount * ((1 + expected_return / 100) ** yr)
        projection.append({"Year": yr, "Projected Value": val})

    proj_df = pd.DataFrame(projection)

    proj_fig = px.line(proj_df, x="Year", y="Projected Value", markers=True, title="Wealth Projection")
    st.plotly_chart(proj_fig, use_container_width=True)

    st.dataframe(proj_df, use_container_width=True)

# =========================
# TAB 4 - COMPANY SNAPSHOT
# =========================
with tab4:
    st.subheader("📋 Company Snapshot")

    snapshot_data = {
        "Company Name": info.get("longName", "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Industry": info.get("industry", "N/A"),
        "52 Week High": info.get("fiftyTwoWeekHigh", "N/A"),
        "52 Week Low": info.get("fiftyTwoWeekLow", "N/A"),
        "Dividend Yield": info.get("dividendYield", "N/A"),
        "Book Value": info.get("bookValue", "N/A"),
        "ROE": info.get("returnOnEquity", "N/A"),
        "Debt to Equity": info.get("debtToEquity", "N/A"),
        "Current Ratio": info.get("currentRatio", "N/A"),
        "Profit Margins": info.get("profitMargins", "N/A")
    }

    snap_df = pd.DataFrame(list(snapshot_data.items()), columns=["Metric", "Value"])
    st.dataframe(snap_df, use_container_width=True)

    business_summary = info.get("longBusinessSummary", "Business summary not available.")
    st.text_area("📝 Business Summary", business_summary, height=250)

# =========================
# TAB 5 - RETURNS ANALYZER
# =========================
with tab5:
    st.subheader("📊 Returns Analyzer")

    df = df.copy()
    df["Daily Return %"] = df["Close"].pct_change() * 100
    df["Cumulative Return %"] = ((df["Close"] / df["Close"].iloc[0]) - 1) * 100

    c1, c2, c3 = st.columns(3)
    with c1:
        total_return = safe_float(df["Cumulative Return %"].iloc[-1])
        st.metric("Total Return", f"{total_return:.2f}%")
    with c2:
        volatility = safe_float(df["Daily Return %"].std()) * np.sqrt(252)
        st.metric("Annualized Volatility", f"{volatility:.2f}%")
    with c3:
        max_drawdown = ((df["Close"] / df["Close"].cummax()) - 1).min() * 100
        st.metric("Max Drawdown", f"{max_drawdown:.2f}%")

    ret_fig = px.line(df, x="Date", y="Cumulative Return %", title="Cumulative Return %")
    st.plotly_chart(ret_fig, use_container_width=True)

    daily_ret_fig = px.histogram(df.dropna(), x="Daily Return %", nbins=50, title="Daily Return Distribution")
    st.plotly_chart(daily_ret_fig, use_container_width=True)

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("🚀 FINAL V5.1 Cloud-Safe Build | Designed for Streamlit Cloud stability | If Yahoo Finance is slow, app still remains safe.")

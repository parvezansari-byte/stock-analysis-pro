import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============================================================
# FINAL V6 ULTRA PREMIUM CLOUD SAFE SINGLE app.py
# Streamlit Cloud safe | Lightweight | Premium UI | Deploy-ready
# ============================================================

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="NSE Stock Intelligence Pro MAX V6 ULTRA",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# PREMIUM CSS
# -------------------------------
st.markdown("""
<style>
:root {
    --bg1: #0b1220;
    --bg2: #111827;
    --card: rgba(255,255,255,0.06);
    --card2: rgba(255,255,255,0.04);
    --line: rgba(255,255,255,0.08);
    --text: #f8fafc;
    --muted: #cbd5e1;
    --green: #10b981;
    --red: #ef4444;
    --amber: #f59e0b;
    --blue: #3b82f6;
}

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, var(--bg1), var(--bg2));
    color: var(--text);
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 98%;
}

[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.03);
    border-right: 1px solid var(--line);
}

.hero {
    background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(16,185,129,0.10));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 22px;
    margin-bottom: 14px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}

.hero-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: white;
    margin-bottom: 4px;
}

.hero-sub {
    color: var(--muted);
    font-size: 0.98rem;
}

.pill {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    margin-right: 8px;
    margin-top: 10px;
    font-size: 0.82rem;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.04);
    color: #e2e8f0;
}

.card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.12);
}

.small-muted {
    color: var(--muted);
    font-size: 0.85rem;
}

.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 6px;
}

.stTabs [data-baseweb="tab"] {
    font-weight: 700;
    font-size: 15px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# SAFE STOCK UNIVERSE
# -------------------------------
NSE_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "LT.NS", "ITC.NS", "BHARTIARTL.NS", "AXISBANK.NS",
    "KOTAKBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS", "SUNPHARMA.NS",
    "HCLTECH.NS", "WIPRO.NS", "ULTRACEMCO.NS", "BAJFINANCE.NS", "NESTLEIND.NS"
]

WATCHLIST = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"
]

# -------------------------------
# HELPERS
# -------------------------------
def safe_float(val, default=0.0):
    try:
        if val is None:
            return default
        if isinstance(val, (list, tuple, dict)):
            return default
        return float(val)
    except Exception:
        return default


def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    try:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        return df
    except Exception:
        return df


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df = flatten_columns(df)
    for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
        if col not in df.columns:
            df[col] = np.nan
    if "Date" not in df.columns:
        df = df.reset_index()
        if "Date" not in df.columns:
            df["Date"] = pd.date_range(end=pd.Timestamp.today(), periods=len(df))
    return df


@st.cache_data(ttl=1800, show_spinner=False)
def get_stock_data(symbol: str, period: str = "6mo") -> pd.DataFrame:
    try:
        df = yf.download(symbol, period=period, interval="1d", progress=False, auto_adjust=False, threads=False)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        df = normalize_df(df)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=1800, show_spinner=False)
def get_stock_info(symbol: str) -> dict:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info if isinstance(info, dict) else {}
    except Exception:
        return {}


@st.cache_data(ttl=1800, show_spinner=False)
def get_watchlist_snapshot(symbols):
    rows = []
    for s in symbols:
        try:
            df = get_stock_data(s, "3mo")
            if df.empty or len(df) < 2:
                rows.append({"Symbol": s.replace('.NS',''), "Price": np.nan, "1D %": np.nan, "1M %": np.nan, "Score": 0, "Signal": "NA"})
                continue
            df = add_indicators(df)
            close = safe_float(df["Close"].iloc[-1])
            prev = safe_float(df["Close"].iloc[-2], close)
            one_day = ((close / prev) - 1) * 100 if prev else 0
            idx_1m = max(0, len(df) - 22)
            base_1m = safe_float(df["Close"].iloc[idx_1m], close)
            one_month = ((close / base_1m) - 1) * 100 if base_1m else 0
            score, signal, _ = technical_score(df)
            rows.append({
                "Symbol": s.replace('.NS',''),
                "Price": round(close, 2),
                "1D %": round(one_day, 2),
                "1M %": round(one_month, 2),
                "Score": score,
                "Signal": signal
            })
        except Exception:
            rows.append({"Symbol": s.replace('.NS',''), "Price": np.nan, "1D %": np.nan, "1M %": np.nan, "Score": 0, "Signal": "NA"})
    return pd.DataFrame(rows)


def calc_rsi(series, period=14):
    try:
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
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
        df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["RSI"] = calc_rsi(df["Close"], 14)
        df["Daily Return %"] = df["Close"].pct_change() * 100
        df["Volatility20"] = df["Daily Return %"].rolling(20).std() * np.sqrt(252)
        df["RollingHigh20"] = df["High"].rolling(20).max()
        df["RollingLow20"] = df["Low"].rolling(20).min()
        return df
    except Exception:
        return df


def technical_score(df):
    score = 0
    reasons = []
    try:
        close = safe_float(df["Close"].iloc[-1])
        sma20 = safe_float(df["SMA20"].iloc[-1], close)
        sma50 = safe_float(df["SMA50"].iloc[-1], close)
        ema20 = safe_float(df["EMA20"].iloc[-1], close)
        ema50 = safe_float(df["EMA50"].iloc[-1], close)
        rsi = safe_float(df["RSI"].iloc[-1], 50)

        if close > sma20:
            score += 15
            reasons.append("Price above SMA20")
        else:
            score -= 10

        if close > sma50:
            score += 20
            reasons.append("Price above SMA50")
        else:
            score -= 15

        if sma20 > sma50:
            score += 20
            reasons.append("SMA20 above SMA50")
        else:
            score -= 10

        if ema20 > ema50:
            score += 15
            reasons.append("EMA20 above EMA50")
        else:
            score -= 8

        if 45 <= rsi <= 65:
            score += 15
            reasons.append("RSI healthy zone")
        elif 30 <= rsi < 45:
            score += 5
        elif 65 < rsi <= 75:
            score += 5
            reasons.append("RSI strong momentum")
        elif rsi < 30:
            score += 8
            reasons.append("RSI oversold rebound zone")
        else:
            score -= 8

        # clamp
        score = max(0, min(100, int(score + 35)))

        if score >= 75:
            signal = "STRONG BUY"
        elif score >= 60:
            signal = "BUY"
        elif score >= 40:
            signal = "HOLD"
        elif score >= 25:
            signal = "WEAK"
        else:
            signal = "AVOID"

        return score, signal, reasons
    except Exception:
        return 50, "HOLD", ["Fallback scoring used"]


def support_resistance(df):
    try:
        support = safe_float(df["RollingLow20"].iloc[-1], safe_float(df["Low"].tail(20).min()))
        resistance = safe_float(df["RollingHigh20"].iloc[-1], safe_float(df["High"].tail(20).max()))
        return support, resistance
    except Exception:
        close = safe_float(df["Close"].iloc[-1])
        return close * 0.95, close * 1.05


def risk_badge(score):
    if score >= 75:
        return "Low Risk Momentum"
    elif score >= 55:
        return "Moderate Risk"
    elif score >= 35:
        return "Watch Carefully"
    return "High Risk"


def lumpsum_projection(amount, rate, years):
    fv = amount * ((1 + rate / 100) ** years)
    rows = []
    for yr in range(1, years + 1):
        val = amount * ((1 + rate / 100) ** yr)
        rows.append({"Year": yr, "Projected Value": val})
    return fv, pd.DataFrame(rows)


def sip_projection(monthly, rate, years):
    r = rate / 100 / 12
    n = years * 12
    if r == 0:
        fv = monthly * n
    else:
        fv = monthly * (((1 + r) ** n - 1) / r) * (1 + r)
    rows = []
    for yr in range(1, years + 1):
        m = yr * 12
        if r == 0:
            val = monthly * m
        else:
            val = monthly * (((1 + r) ** m - 1) / r) * (1 + r)
        rows.append({"Year": yr, "Projected Value": val})
    return fv, pd.DataFrame(rows)


def color_signal(signal):
    if signal in ["STRONG BUY", "BUY"]:
        return "green"
    if signal in ["WEAK", "AVOID"]:
        return "red"
    return "orange"

# -------------------------------
# HEADER
# -------------------------------
st.markdown("""
<div class='hero'>
  <div class='hero-title'>📊 NSE Stock Intelligence Pro MAX V6 ULTRA</div>
  <div class='hero-sub'>Premium dashboard • Technical score engine • Watchlist • Support/Resistance • Portfolio & Wealth planners • Streamlit Cloud Safe</div>
  <span class='pill'>Cloud Safe</span>
  <span class='pill'>No Heavy Dependencies</span>
  <span class='pill'>Deploy Ready</span>
  <span class='pill'>Single app.py</span>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# SIDEBAR CONTROLS
# -------------------------------
st.sidebar.title("⚙️ Control Center")
selected_stock = st.sidebar.selectbox("Select NSE Stock", NSE_STOCKS, index=0)
period = st.sidebar.selectbox("Data Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Wealth Planner Inputs")
lumpsum_amount = st.sidebar.number_input("Lumpsum (₹)", min_value=1000, value=100000, step=1000)
sip_amount = st.sidebar.number_input("Monthly SIP (₹)", min_value=500, value=10000, step=500)
expected_return = st.sidebar.slider("Expected Return (%)", 1, 30, 12)
planner_years = st.sidebar.slider("Years", 1, 30, 10)

# -------------------------------
# LOAD MAIN DATA
# -------------------------------
with st.spinner("Loading market data safely..."):
    df = get_stock_data(selected_stock, period)
    info = get_stock_info(selected_stock)

if df.empty:
    st.error("❌ Unable to fetch stock data right now. App is deployed correctly, but data source may be temporarily unavailable.")
    st.info("Try changing the stock, reducing the period, or refreshing after a minute.")
    st.stop()

df = add_indicators(df)
close = safe_float(df["Close"].iloc[-1])
prev_close = safe_float(df["Close"].iloc[-2], close) if len(df) > 1 else close
change = close - prev_close
change_pct = (change / prev_close * 100) if prev_close else 0
volume = safe_float(df["Volume"].iloc[-1])
score, signal, reasons = technical_score(df)
support, resistance = support_resistance(df)

# -------------------------------
# TOP METRICS
# -------------------------------
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric("📌 Stock", selected_stock.replace('.NS', ''))
with m2:
    st.metric("💹 Price", f"₹{close:,.2f}", f"{change_pct:.2f}%")
with m3:
    st.metric("🧠 Tech Score", f"{score}/100")
with m4:
    st.metric("📢 Signal", signal)
with m5:
    st.metric("📦 Volume", f"{volume:,.0f}")

st.markdown("---")

# -------------------------------
# TABS
# -------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 Dashboard",
    "🧠 Technical Lab",
    "🔥 Watchlist Scanner",
    "💼 Portfolio Planner",
    "💰 SIP & Lumpsum",
    "🏢 Company Snapshot",
    "📊 Returns Analyzer"
])

# -------------------------------
# TAB 1 - DASHBOARD
# -------------------------------
with tab1:
    c1, c2 = st.columns([2, 1])

    with c1:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df["Date"],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price"
        ))
        if "SMA20" in df.columns:
            fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA20"], mode="lines", name="SMA20"))
        if "SMA50" in df.columns:
            fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA50"], mode="lines", name="SMA50"))
        fig.update_layout(title=f"{selected_stock} Premium Price Dashboard", height=620)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🎯 Smart Insight")
        st.write(f"**Technical Score:** {score}/100")
        st.write(f"**Signal:** {signal}")
        st.write(f"**Support:** ₹{support:,.2f}")
        st.write(f"**Resistance:** ₹{resistance:,.2f}")
        st.write(f"**Risk View:** {risk_badge(score)}")
        st.markdown("**Why this score?**")
        for r in reasons[:5]:
            st.write(f"- {r}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.write("")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📍 Positioning")
        upside = ((resistance / close) - 1) * 100 if close else 0
        downside = ((close / support) - 1) * 100 if support else 0
        st.write(f"**Upside to Resistance:** {upside:.2f}%")
        st.write(f"**Downside to Support:** {downside:.2f}%")
        rr = upside / downside if downside > 0 else 0
        st.write(f"**Reward/Risk Ratio:** {rr:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("📊 Volume Trend")
    vol_fig = px.bar(df, x="Date", y="Volume", title="Daily Volume")
    st.plotly_chart(vol_fig, use_container_width=True)

# -------------------------------
# TAB 2 - TECHNICAL LAB
# -------------------------------
with tab2:
    rsi = safe_float(df["RSI"].iloc[-1], 50)
    sma20 = safe_float(df["SMA20"].iloc[-1], close)
    sma50 = safe_float(df["SMA50"].iloc[-1], close)
    ema20 = safe_float(df["EMA20"].iloc[-1], close)
    ema50 = safe_float(df["EMA50"].iloc[-1], close)
    vol20 = safe_float(df["Volatility20"].iloc[-1], 0)

    a, b, c, d, e = st.columns(5)
    a.metric("RSI (14)", f"{rsi:.2f}")
    b.metric("SMA20", f"₹{sma20:,.2f}")
    c.metric("SMA50", f"₹{sma50:,.2f}")
    d.metric("EMA20", f"₹{ema20:,.2f}")
    e.metric("Volatility", f"{vol20:.2f}%")

    st.subheader("📢 Technical Signal Engine")
    if signal in ["STRONG BUY", "BUY"]:
        st.success(f"✅ Current View: {signal}")
    elif signal in ["WEAK", "AVOID"]:
        st.error(f"❌ Current View: {signal}")
    else:
        st.warning(f"⚠️ Current View: {signal}")

    colr1, colr2 = st.columns(2)
    with colr1:
        st.markdown("### RSI Chart")
        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], mode="lines", name="RSI"))
        rsi_fig.add_hline(y=70, line_dash="dash")
        rsi_fig.add_hline(y=30, line_dash="dash")
        rsi_fig.update_layout(height=420)
        st.plotly_chart(rsi_fig, use_container_width=True)

    with colr2:
        st.markdown("### Support vs Resistance")
        sr_df = pd.DataFrame({
            "Level": ["Support", "Current Price", "Resistance"],
            "Value": [support, close, resistance]
        })
        sr_fig = px.bar(sr_df, x="Level", y="Value", title="Key Trading Levels")
        st.plotly_chart(sr_fig, use_container_width=True)

# -------------------------------
# TAB 3 - WATCHLIST SCANNER
# -------------------------------
with tab3:
    st.subheader("🔥 Watchlist Scanner (Cloud Safe)")
    st.caption("Scans a curated watchlist with lightweight technical score logic.")

    with st.spinner("Scanning watchlist..."):
        scan_df = get_watchlist_snapshot(WATCHLIST)

    st.dataframe(scan_df, use_container_width=True)

    if not scan_df.empty:
        best = scan_df.sort_values(by="Score", ascending=False).head(3)
        st.subheader("🏆 Top Opportunities")
        for _, row in best.iterrows():
            sig = row.get("Signal", "NA")
            if sig in ["STRONG BUY", "BUY"]:
                st.success(f"{row['Symbol']} | Score: {row['Score']} | Signal: {sig}")
            elif sig in ["WEAK", "AVOID"]:
                st.error(f"{row['Symbol']} | Score: {row['Score']} | Signal: {sig}")
            else:
                st.warning(f"{row['Symbol']} | Score: {row['Score']} | Signal: {sig}")

# -------------------------------
# TAB 4 - PORTFOLIO PLANNER
# -------------------------------
with tab4:
    st.subheader("💼 Simple Portfolio Planner")
    st.caption("Create a quick sample allocation model. This is a planning utility, not investment advice.")

    p1, p2, p3 = st.columns(3)
    with p1:
        allocation_large = st.slider("Large Cap %", 0, 100, 50)
    with p2:
        allocation_mid = st.slider("Mid Cap %", 0, 100, 30)
    with p3:
        allocation_small = st.slider("Small Cap %", 0, 100, 20)

    total_alloc = allocation_large + allocation_mid + allocation_small
    st.write(f"**Total Allocation:** {total_alloc}%")

    if total_alloc != 100:
        st.warning("⚠️ Allocation should total 100% for a balanced model.")

    portfolio_capital = st.number_input("Portfolio Capital (₹)", min_value=10000, value=500000, step=10000)

    alloc_df = pd.DataFrame({
        "Bucket": ["Large Cap", "Mid Cap", "Small Cap"],
        "Allocation %": [allocation_large, allocation_mid, allocation_small],
        "Amount": [
            portfolio_capital * allocation_large / 100,
            portfolio_capital * allocation_mid / 100,
            portfolio_capital * allocation_small / 100,
        ]
    })

    pie = px.pie(alloc_df, names="Bucket", values="Amount", title="Portfolio Allocation")
    st.plotly_chart(pie, use_container_width=True)
    st.dataframe(alloc_df, use_container_width=True)

# -------------------------------
# TAB 5 - SIP & LUMPSUM
# -------------------------------
with tab5:
    st.subheader("💰 Wealth Engine - SIP + Lumpsum")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 📦 Lumpsum Projection")
        lump_fv, lump_df = lumpsum_projection(lumpsum_amount, expected_return, planner_years)
        st.metric("Future Value", f"₹{lump_fv:,.0f}")
        st.metric("Absolute Gain", f"₹{(lump_fv - lumpsum_amount):,.0f}")
        lump_fig = px.line(lump_df, x="Year", y="Projected Value", markers=True, title="Lumpsum Growth")
        st.plotly_chart(lump_fig, use_container_width=True)

    with c2:
        st.markdown("### 🔁 SIP Projection")
        sip_fv, sip_df = sip_projection(sip_amount, expected_return, planner_years)
        total_invested = sip_amount * 12 * planner_years
        st.metric("Future Value", f"₹{sip_fv:,.0f}")
        st.metric("Total Invested", f"₹{total_invested:,.0f}")
        st.metric("Wealth Created", f"₹{(sip_fv - total_invested):,.0f}")
        sip_fig = px.line(sip_df, x="Year", y="Projected Value", markers=True, title="SIP Growth")
        st.plotly_chart(sip_fig, use_container_width=True)

# -------------------------------
# TAB 6 - COMPANY SNAPSHOT
# -------------------------------
with tab6:
    st.subheader("🏢 Company Snapshot")

    snapshot = {
        "Company Name": info.get("longName", "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Industry": info.get("industry", "N/A"),
        "Market Cap": info.get("marketCap", "N/A"),
        "P/E Ratio": info.get("trailingPE", "N/A"),
        "52W High": info.get("fiftyTwoWeekHigh", "N/A"),
        "52W Low": info.get("fiftyTwoWeekLow", "N/A"),
        "Book Value": info.get("bookValue", "N/A"),
        "Dividend Yield": info.get("dividendYield", "N/A"),
        "ROE": info.get("returnOnEquity", "N/A"),
        "Debt/Equity": info.get("debtToEquity", "N/A"),
        "Current Ratio": info.get("currentRatio", "N/A"),
        "Profit Margins": info.get("profitMargins", "N/A")
    }

    snap_df = pd.DataFrame(list(snapshot.items()), columns=["Metric", "Value"])
    st.dataframe(snap_df, use_container_width=True)

    summary = info.get("longBusinessSummary", "Business summary not available.")
    st.text_area("📝 Business Summary", summary, height=240)

# -------------------------------
# TAB 7 - RETURNS ANALYZER
# -------------------------------
with tab7:
    st.subheader("📊 Returns Analyzer")

    work = df.copy()
    work["Daily Return %"] = work["Close"].pct_change() * 100
    base = safe_float(work["Close"].iloc[0], close)
    work["Cumulative Return %"] = ((work["Close"] / base) - 1) * 100 if base else 0

    r1, r2, r3, r4 = st.columns(4)
    total_return = safe_float(work["Cumulative Return %"].iloc[-1], 0)
    annual_vol = safe_float(work["Daily Return %"].std(), 0) * np.sqrt(252)
    max_dd = ((work["Close"] / work["Close"].cummax()) - 1).min() * 100
    sharpe_like = (total_return / annual_vol) if annual_vol else 0

    r1.metric("Total Return", f"{total_return:.2f}%")
    r2.metric("Annualized Volatility", f"{annual_vol:.2f}%")
    r3.metric("Max Drawdown", f"{max_dd:.2f}%")
    r4.metric("Return/Vol Ratio", f"{sharpe_like:.2f}")

    cum_fig = px.line(work, x="Date", y="Cumulative Return %", title="Cumulative Return %")
    st.plotly_chart(cum_fig, use_container_width=True)

    hist_fig = px.histogram(work.dropna(), x="Daily Return %", nbins=50, title="Daily Return Distribution")
    st.plotly_chart(hist_fig, use_container_width=True)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("🚀 FINAL V6 ULTRA PREMIUM CLOUD SAFE BUILD | Designed for Streamlit Cloud stability | Lightweight, premium, deploy-ready single app.py")

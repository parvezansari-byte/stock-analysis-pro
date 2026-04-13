import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============================================================
# FINAL V7 ELITE CLOUD SAFE SINGLE app.py
# Premium | Fundamental + Technical | Portfolio | Scanner | Cloud-safe
# ============================================================

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="NSE Stock Intelligence Pro MAX V7 ELITE",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# ELITE CSS
# -------------------------------
st.markdown("""
<style>
:root {
    --bg1: #0b1020;
    --bg2: #111827;
    --card: rgba(255,255,255,0.05);
    --line: rgba(255,255,255,0.08);
    --text: #f8fafc;
    --muted: #cbd5e1;
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
    background: linear-gradient(135deg, rgba(59,130,246,0.14), rgba(16,185,129,0.10));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 22px;
    margin-bottom: 14px;
}
.hero-title {font-size: 2.1rem; font-weight: 800; color: white;}
.hero-sub {color: var(--muted); font-size: 0.96rem; margin-top: 4px;}
.pill {
    display: inline-block; padding: 6px 12px; border-radius: 999px; margin-right: 8px; margin-top: 10px;
    font-size: 0.82rem; border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.04); color: #e2e8f0;
}
.card {
    background: var(--card); border: 1px solid var(--line); border-radius: 20px; padding: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.12);
}
.stTabs [data-baseweb="tab"] { font-weight: 700; font-size: 15px; }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# STOCK LISTS
# -------------------------------
NSE_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "LT.NS", "ITC.NS", "BHARTIARTL.NS", "AXISBANK.NS",
    "KOTAKBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS", "SUNPHARMA.NS",
    "HCLTECH.NS", "WIPRO.NS", "ULTRACEMCO.NS", "BAJFINANCE.NS", "NESTLEIND.NS"
]
WATCHLIST = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "ITC.NS", "LT.NS"]

# -------------------------------
# SAFE HELPERS
# -------------------------------
def safe_float(val, default=0.0):
    try:
        if val is None or isinstance(val, (dict, list, tuple)):
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

# -------------------------------
# DATA FETCH
# -------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def get_stock_data(symbol: str, period: str = "6mo") -> pd.DataFrame:
    try:
        df = yf.download(symbol, period=period, interval="1d", progress=False, auto_adjust=False, threads=False)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        return normalize_df(df)
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

# -------------------------------
# INDICATORS
# -------------------------------
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

# -------------------------------
# SCORING ENGINES
# -------------------------------
def technical_score(df):
    score = 35
    reasons = []
    try:
        close = safe_float(df["Close"].iloc[-1])
        sma20 = safe_float(df["SMA20"].iloc[-1], close)
        sma50 = safe_float(df["SMA50"].iloc[-1], close)
        ema20 = safe_float(df["EMA20"].iloc[-1], close)
        ema50 = safe_float(df["EMA50"].iloc[-1], close)
        rsi = safe_float(df["RSI"].iloc[-1], 50)

        if close > sma20:
            score += 12; reasons.append("Price above SMA20")
        else:
            score -= 8
        if close > sma50:
            score += 18; reasons.append("Price above SMA50")
        else:
            score -= 12
        if sma20 > sma50:
            score += 15; reasons.append("SMA20 above SMA50")
        else:
            score -= 8
        if ema20 > ema50:
            score += 12; reasons.append("EMA20 above EMA50")
        else:
            score -= 6
        if 45 <= rsi <= 65:
            score += 12; reasons.append("RSI in healthy range")
        elif 30 <= rsi < 45 or 65 < rsi <= 75:
            score += 5
        elif rsi < 30:
            score += 8; reasons.append("Oversold rebound zone")
        else:
            score -= 8

        score = max(0, min(100, int(score)))
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
        return 50, "HOLD", ["Fallback technical scoring"]


def fundamental_score(info: dict):
    score = 40
    reasons = []
    try:
        pe = safe_float(info.get("trailingPE"), 0)
        pb = safe_float(info.get("priceToBook"), 0)
        roe = safe_float(info.get("returnOnEquity"), 0) * 100 if abs(safe_float(info.get("returnOnEquity"), 0)) < 2 else safe_float(info.get("returnOnEquity"), 0)
        debt_eq = safe_float(info.get("debtToEquity"), 0)
        current_ratio = safe_float(info.get("currentRatio"), 0)
        margins = safe_float(info.get("profitMargins"), 0) * 100 if abs(safe_float(info.get("profitMargins"), 0)) < 2 else safe_float(info.get("profitMargins"), 0)
        div = safe_float(info.get("dividendYield"), 0) * 100 if abs(safe_float(info.get("dividendYield"), 0)) < 2 else safe_float(info.get("dividendYield"), 0)

        if 0 < pe <= 25:
            score += 15; reasons.append("Reasonable P/E")
        elif 25 < pe <= 40:
            score += 7
        elif pe > 60:
            score -= 8

        if 0 < pb <= 5:
            score += 8; reasons.append("Healthy Price/Book")
        elif pb > 10:
            score -= 5

        if roe >= 15:
            score += 15; reasons.append("Strong ROE")
        elif roe >= 10:
            score += 8
        elif 0 < roe < 5:
            score -= 5

        if 0 < debt_eq <= 80:
            score += 10; reasons.append("Manageable Debt/Equity")
        elif debt_eq > 200:
            score -= 10

        if current_ratio >= 1.2:
            score += 6; reasons.append("Healthy liquidity")
        elif 0 < current_ratio < 0.8:
            score -= 4

        if margins >= 10:
            score += 10; reasons.append("Strong profit margins")
        elif 0 < margins < 5:
            score -= 4

        if div >= 1:
            score += 4

        score = max(0, min(100, int(score)))

        if score >= 75:
            rating = "STRONG"
        elif score >= 60:
            rating = "GOOD"
        elif score >= 40:
            rating = "AVERAGE"
        else:
            rating = "WEAK"
        return score, rating, reasons
    except Exception:
        return 50, "AVERAGE", ["Fallback fundamental scoring"]


def combined_score(tech, fund):
    score = int(round(tech * 0.55 + fund * 0.45))
    if score >= 78:
        verdict = "ELITE BUY"
    elif score >= 65:
        verdict = "QUALITY BUY"
    elif score >= 50:
        verdict = "HOLD / WATCH"
    elif score >= 35:
        verdict = "SPECULATIVE"
    else:
        verdict = "AVOID"
    return score, verdict

# -------------------------------
# ANALYTICS HELPERS
# -------------------------------
def support_resistance(df):
    try:
        support = safe_float(df["RollingLow20"].iloc[-1], safe_float(df["Low"].tail(20).min()))
        resistance = safe_float(df["RollingHigh20"].iloc[-1], safe_float(df["High"].tail(20).max()))
        return support, resistance
    except Exception:
        close = safe_float(df["Close"].iloc[-1])
        return close * 0.95, close * 1.05


def buy_sell_probability(tech_score, fund_score, close, support, resistance):
    try:
        rr = ((resistance - close) / max(close - support, 0.01)) if close > support else 1.0
        rr_bonus = min(max(rr * 5, 0), 15)
        buy_prob = min(95, max(5, int(tech_score * 0.55 + fund_score * 0.35 + rr_bonus)))
        sell_prob = 100 - buy_prob
        return buy_prob, sell_prob
    except Exception:
        return 50, 50


def breakout_status(df):
    try:
        close = safe_float(df["Close"].iloc[-1])
        recent_high = safe_float(df["High"].tail(20).max())
        recent_low = safe_float(df["Low"].tail(20).min())
        if close >= recent_high * 0.995:
            return "NEAR BREAKOUT"
        elif close <= recent_low * 1.005:
            return "NEAR BREAKDOWN"
        return "IN RANGE"
    except Exception:
        return "UNKNOWN"


def lumpsum_projection(amount, rate, years):
    fv = amount * ((1 + rate / 100) ** years)
    rows = []
    for yr in range(1, years + 1):
        rows.append({"Year": yr, "Projected Value": amount * ((1 + rate / 100) ** yr)})
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
        val = monthly * m if r == 0 else monthly * (((1 + r) ** m - 1) / r) * (1 + r)
        rows.append({"Year": yr, "Projected Value": val})
    return fv, pd.DataFrame(rows)

@st.cache_data(ttl=1800, show_spinner=False)
def get_watchlist_snapshot(symbols):
    rows = []
    for s in symbols:
        try:
            df = get_stock_data(s, "6mo")
            info = get_stock_info(s)
            if df.empty:
                rows.append({"Symbol": s.replace('.NS',''), "Price": np.nan, "Tech": 0, "Fund": 0, "Combined": 0, "Verdict": "NA", "Breakout": "NA"})
                continue
            df = add_indicators(df)
            close = safe_float(df["Close"].iloc[-1])
            tech, _, _ = technical_score(df)
            fund, _, _ = fundamental_score(info)
            comb, verdict = combined_score(tech, fund)
            rows.append({
                "Symbol": s.replace('.NS',''),
                "Price": round(close, 2),
                "Tech": tech,
                "Fund": fund,
                "Combined": comb,
                "Verdict": verdict,
                "Breakout": breakout_status(df)
            })
        except Exception:
            rows.append({"Symbol": s.replace('.NS',''), "Price": np.nan, "Tech": 0, "Fund": 0, "Combined": 0, "Verdict": "NA", "Breakout": "NA"})
    return pd.DataFrame(rows)

# -------------------------------
# HEADER
# -------------------------------
st.markdown("""
<div class='hero'>
  <div class='hero-title'>📊 NSE Stock Intelligence Pro MAX V7 ELITE</div>
  <div class='hero-sub'>Elite dashboard • Technical + Fundamental analysis • Buy/Sell probability • Breakout scanner • Portfolio tracker • Cloud-safe single app.py</div>
  <span class='pill'>Fundamental Analysis Added</span>
  <span class='pill'>Cloud Safe</span>
  <span class='pill'>Single File</span>
  <span class='pill'>Deploy Ready</span>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.title("⚙️ ELITE Control Center")
selected_stock = st.sidebar.selectbox("Select NSE Stock", NSE_STOCKS, index=0)
period = st.sidebar.selectbox("Data Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Wealth Planner")
lumpsum_amount = st.sidebar.number_input("Lumpsum (₹)", min_value=1000, value=100000, step=1000)
sip_amount = st.sidebar.number_input("Monthly SIP (₹)", min_value=500, value=10000, step=500)
expected_return = st.sidebar.slider("Expected Return (%)", 1, 30, 12)
planner_years = st.sidebar.slider("Years", 1, 30, 10)

st.sidebar.markdown("---")
st.sidebar.subheader("💼 Manual Portfolio Tracker")
holding_qty = st.sidebar.number_input("Holding Qty", min_value=0, value=100, step=1)
avg_buy_price = st.sidebar.number_input("Avg Buy Price (₹)", min_value=0.0, value=1000.0, step=1.0)

# -------------------------------
# LOAD DATA
# -------------------------------
with st.spinner("Loading market data safely..."):
    df = get_stock_data(selected_stock, period)
    info = get_stock_info(selected_stock)

if df.empty:
    st.error("❌ Unable to fetch stock data right now. App is deployed correctly, but data source may be temporarily unavailable.")
    st.info("Try changing stock, reducing period, or refresh after a minute.")
    st.stop()

df = add_indicators(df)
close = safe_float(df["Close"].iloc[-1])
prev_close = safe_float(df["Close"].iloc[-2], close) if len(df) > 1 else close
change_pct = ((close / prev_close) - 1) * 100 if prev_close else 0
volume = safe_float(df["Volume"].iloc[-1])
tech_score, tech_signal, tech_reasons = technical_score(df)
fund_score, fund_rating, fund_reasons = fundamental_score(info)
combo_score, combo_verdict = combined_score(tech_score, fund_score)
support, resistance = support_resistance(df)
buy_prob, sell_prob = buy_sell_probability(tech_score, fund_score, close, support, resistance)

# Portfolio tracker
invested_value = holding_qty * avg_buy_price
current_value = holding_qty * close
pnl = current_value - invested_value
pnl_pct = (pnl / invested_value * 100) if invested_value else 0

# -------------------------------
# TOP METRICS
# -------------------------------
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("📌 Stock", selected_stock.replace('.NS',''))
m2.metric("💹 Price", f"₹{close:,.2f}", f"{change_pct:.2f}%")
m3.metric("🧠 Tech Score", f"{tech_score}/100")
m4.metric("🏢 Fund Score", f"{fund_score}/100")
m5.metric("⭐ Combined", f"{combo_score}/100")
m6.metric("📢 Verdict", combo_verdict)

st.markdown("---")

# -------------------------------
# TABS
# -------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📈 Dashboard",
    "🧠 Technical Analysis",
    "🏢 Fundamental Analysis",
    "🔥 Scanner & Comparison",
    "💼 Portfolio Tracker",
    "💰 Wealth Planner",
    "🏢 Company Snapshot",
    "📊 Returns Analyzer"
])

# -------------------------------
# TAB 1 DASHBOARD
# -------------------------------
with tab1:
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"))
        fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA20"], mode="lines", name="SMA20"))
        fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA50"], mode="lines", name="SMA50"))
        fig.update_layout(title=f"{selected_stock} Elite Price Dashboard", height=620)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🎯 ELITE Signal Board")
        st.write(f"**Technical Signal:** {tech_signal}")
        st.write(f"**Fundamental Rating:** {fund_rating}")
        st.write(f"**Final Verdict:** {combo_verdict}")
        st.write(f"**Support:** ₹{support:,.2f}")
        st.write(f"**Resistance:** ₹{resistance:,.2f}")
        st.write(f"**Breakout Status:** {breakout_status(df)}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.write("")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🎲 Buy / Sell Probability")
        st.progress(buy_prob / 100)
        st.write(f"**Buy Probability:** {buy_prob}%")
        st.write(f"**Sell Probability:** {sell_prob}%")
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("📊 Volume Trend")
    vol_fig = px.bar(df, x="Date", y="Volume", title="Daily Volume")
    st.plotly_chart(vol_fig, use_container_width=True)

# -------------------------------
# TAB 2 TECHNICAL
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

    if tech_signal in ["STRONG BUY", "BUY"]:
        st.success(f"✅ Technical View: {tech_signal}")
    elif tech_signal in ["WEAK", "AVOID"]:
        st.error(f"❌ Technical View: {tech_signal}")
    else:
        st.warning(f"⚠️ Technical View: {tech_signal}")

    col1, col2 = st.columns(2)
    with col1:
        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], mode="lines", name="RSI"))
        rsi_fig.add_hline(y=70, line_dash="dash")
        rsi_fig.add_hline(y=30, line_dash="dash")
        rsi_fig.update_layout(title="RSI Indicator", height=420)
        st.plotly_chart(rsi_fig, use_container_width=True)
    with col2:
        sr_df = pd.DataFrame({"Level": ["Support", "Current", "Resistance"], "Value": [support, close, resistance]})
        sr_fig = px.bar(sr_df, x="Level", y="Value", title="Support / Resistance")
        st.plotly_chart(sr_fig, use_container_width=True)

    st.subheader("📝 Technical Reasons")
    for r in tech_reasons:
        st.write(f"- {r}")

# -------------------------------
# TAB 3 FUNDAMENTAL
# -------------------------------
with tab3:
    st.subheader("🏢 Fundamental Analysis Engine")

    pe = info.get("trailingPE", "N/A")
    pb = info.get("priceToBook", "N/A")
    roe = info.get("returnOnEquity", "N/A")
    debt_eq = info.get("debtToEquity", "N/A")
    current_ratio = info.get("currentRatio", "N/A")
    profit_margin = info.get("profitMargins", "N/A")
    div_yield = info.get("dividendYield", "N/A")
    book_value = info.get("bookValue", "N/A")

    f1, f2, f3, f4 = st.columns(4)
    f1.metric("P/E Ratio", f"{pe}")
    f2.metric("P/B Ratio", f"{pb}")
    f3.metric("ROE", f"{roe}")
    f4.metric("Debt/Equity", f"{debt_eq}")

    f5, f6, f7, f8 = st.columns(4)
    f5.metric("Current Ratio", f"{current_ratio}")
    f6.metric("Profit Margin", f"{profit_margin}")
    f7.metric("Dividend Yield", f"{div_yield}")
    f8.metric("Book Value", f"{book_value}")

    if fund_rating in ["STRONG", "GOOD"]:
        st.success(f"✅ Fundamental Rating: {fund_rating} ({fund_score}/100)")
    elif fund_rating == "AVERAGE":
        st.warning(f"⚠️ Fundamental Rating: {fund_rating} ({fund_score}/100)")
    else:
        st.error(f"❌ Fundamental Rating: {fund_rating} ({fund_score}/100)")

    st.subheader("📝 Fundamental Reasons")
    for r in fund_reasons:
        st.write(f"- {r}")

    score_df = pd.DataFrame({
        "Engine": ["Technical", "Fundamental", "Combined"],
        "Score": [tech_score, fund_score, combo_score]
    })
    score_fig = px.bar(score_df, x="Engine", y="Score", title="Score Comparison")
    st.plotly_chart(score_fig, use_container_width=True)

# -------------------------------
# TAB 4 SCANNER
# -------------------------------
with tab4:
    st.subheader("🔥 ELITE Watchlist Scanner + Multi-Stock Comparison")
    with st.spinner("Scanning watchlist..."):
        scan_df = get_watchlist_snapshot(WATCHLIST)
    st.dataframe(scan_df, use_container_width=True)

    if not scan_df.empty:
        top_df = scan_df.sort_values(by="Combined", ascending=False).head(5)
        st.subheader("🏆 Top Combined Score Leaders")
        st.dataframe(top_df, use_container_width=True)

        chart_df = top_df.copy()
        comp_fig = px.bar(chart_df, x="Symbol", y=["Tech", "Fund", "Combined"], barmode="group", title="Top 5 Multi-Stock Comparison")
        st.plotly_chart(comp_fig, use_container_width=True)

# -------------------------------
# TAB 5 PORTFOLIO TRACKER
# -------------------------------
with tab5:
    st.subheader("💼 Manual Portfolio Tracker")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Qty", f"{holding_qty}")
    p2.metric("Invested Value", f"₹{invested_value:,.2f}")
    p3.metric("Current Value", f"₹{current_value:,.2f}")
    p4.metric("PnL", f"₹{pnl:,.2f}", f"{pnl_pct:.2f}%")

    tracker_df = pd.DataFrame({
        "Metric": ["Avg Buy Price", "Current Price", "Qty", "Invested Value", "Current Value", "PnL", "PnL %"],
        "Value": [avg_buy_price, close, holding_qty, invested_value, current_value, pnl, pnl_pct]
    })
    st.dataframe(tracker_df, use_container_width=True)

# -------------------------------
# TAB 6 WEALTH PLANNER
# -------------------------------
with tab6:
    st.subheader("💰 Wealth Planner - SIP + Lumpsum")
    c1, c2 = st.columns(2)
    with c1:
        lump_fv, lump_df = lumpsum_projection(lumpsum_amount, expected_return, planner_years)
        st.metric("Lumpsum Future Value", f"₹{lump_fv:,.0f}")
        st.metric("Absolute Gain", f"₹{(lump_fv - lumpsum_amount):,.0f}")
        st.plotly_chart(px.line(lump_df, x="Year", y="Projected Value", markers=True, title="Lumpsum Growth"), use_container_width=True)
    with c2:
        sip_fv, sip_df = sip_projection(sip_amount, expected_return, planner_years)
        total_invested = sip_amount * 12 * planner_years
        st.metric("SIP Future Value", f"₹{sip_fv:,.0f}")
        st.metric("Total Invested", f"₹{total_invested:,.0f}")
        st.metric("Wealth Created", f"₹{(sip_fv - total_invested):,.0f}")
        st.plotly_chart(px.line(sip_df, x="Year", y="Projected Value", markers=True, title="SIP Growth"), use_container_width=True)

# -------------------------------
# TAB 7 COMPANY SNAPSHOT
# -------------------------------
with tab7:
    st.subheader("🏢 Company Snapshot")
    snapshot = {
        "Company Name": info.get("longName", "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Industry": info.get("industry", "N/A"),
        "Market Cap": info.get("marketCap", "N/A"),
        "P/E Ratio": info.get("trailingPE", "N/A"),
        "P/B Ratio": info.get("priceToBook", "N/A"),
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
    st.text_area("📝 Business Summary", info.get("longBusinessSummary", "Business summary not available."), height=240)

# -------------------------------
# TAB 8 RETURNS ANALYZER
# -------------------------------
with tab8:
    st.subheader("📊 Returns Analyzer")
    work = df.copy()
    work["Daily Return %"] = work["Close"].pct_change() * 100
    base = safe_float(work["Close"].iloc[0], close)
    work["Cumulative Return %"] = ((work["Close"] / base) - 1) * 100 if base else 0

    r1, r2, r3, r4 = st.columns(4)
    total_return = safe_float(work["Cumulative Return %"].iloc[-1], 0)
    annual_vol = safe_float(work["Daily Return %"].std(), 0) * np.sqrt(252)
    max_dd = ((work["Close"] / work["Close"].cummax()) - 1).min() * 100
    return_vol = (total_return / annual_vol) if annual_vol else 0
    r1.metric("Total Return", f"{total_return:.2f}%")
    r2.metric("Annualized Volatility", f"{annual_vol:.2f}%")
    r3.metric("Max Drawdown", f"{max_dd:.2f}%")
    r4.metric("Return/Vol Ratio", f"{return_vol:.2f}")

    st.plotly_chart(px.line(work, x="Date", y="Cumulative Return %", title="Cumulative Return %"), use_container_width=True)
    st.plotly_chart(px.histogram(work.dropna(), x="Daily Return %", nbins=50, title="Daily Return Distribution"), use_container_width=True)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("🚀 FINAL V7 ELITE CLOUD SAFE BUILD | Fundamental + Technical analysis included | Streamlit Cloud stable | Single deployable app.py")

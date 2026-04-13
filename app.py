import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# ============================================================
# FINAL V8 INSTITUTIONAL GRADE CLOUD SAFE SINGLE app.py
# Institutional UI | Technical + Fundamental + Scanner + Portfolio DB
# Risk/Reward | SL/Target | Export Excel | Streamlit Cloud Safe
# ============================================================

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="NSE Stock Intelligence Pro MAX V8 INSTITUTIONAL",
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
    --bg1:#0a1020;
    --bg2:#111827;
    --card:rgba(255,255,255,0.05);
    --line:rgba(255,255,255,0.08);
    --muted:#cbd5e1;
}
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, var(--bg1), var(--bg2));
    color: white;
}
.block-container {padding-top: 1rem; padding-bottom: 2rem; max-width: 98%;}
[data-testid="stSidebar"] {background: rgba(255,255,255,0.03); border-right:1px solid var(--line);}
.hero {
    background: linear-gradient(135deg, rgba(59,130,246,0.16), rgba(16,185,129,0.10));
    border:1px solid rgba(255,255,255,0.08); border-radius:24px; padding:22px; margin-bottom:14px;
}
.hero-title {font-size:2.05rem; font-weight:800; color:white;}
.hero-sub {color:var(--muted); font-size:0.95rem; margin-top:4px;}
.pill {display:inline-block; padding:6px 12px; border-radius:999px; margin-right:8px; margin-top:10px; font-size:0.82rem; border:1px solid rgba(255,255,255,0.08); background:rgba(255,255,255,0.04); color:#e2e8f0;}
.card {background:var(--card); border:1px solid var(--line); border-radius:20px; padding:16px;}
.stTabs [data-baseweb="tab"] {font-weight:700; font-size:15px;}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# UNIVERSE
# -------------------------------
NSE_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "LT.NS", "ITC.NS", "BHARTIARTL.NS", "AXISBANK.NS",
    "KOTAKBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS", "SUNPHARMA.NS",
    "HCLTECH.NS", "WIPRO.NS", "ULTRACEMCO.NS", "BAJFINANCE.NS", "NESTLEIND.NS"
]
WATCHLIST = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "ITC.NS", "LT.NS", "AXISBANK.NS", "BAJFINANCE.NS"
]
SECTOR_MAP = {
    "RELIANCE.NS":"Energy", "TCS.NS":"IT", "INFY.NS":"IT", "HDFCBANK.NS":"Banking", "ICICIBANK.NS":"Banking",
    "SBIN.NS":"Banking", "LT.NS":"Infra", "ITC.NS":"FMCG", "BHARTIARTL.NS":"Telecom", "AXISBANK.NS":"Banking",
    "KOTAKBANK.NS":"Banking", "ASIANPAINT.NS":"Consumer", "MARUTI.NS":"Auto", "TITAN.NS":"Consumer", "SUNPHARMA.NS":"Pharma",
    "HCLTECH.NS":"IT", "WIPRO.NS":"IT", "ULTRACEMCO.NS":"Cement", "BAJFINANCE.NS":"NBFC", "NESTLEIND.NS":"FMCG"
}

# -------------------------------
# HELPERS
# -------------------------------
def safe_float(val, default=0.0):
    try:
        if val is None or isinstance(val, (dict, list, tuple)):
            return default
        return float(val)
    except Exception:
        return default


def flatten_columns(df):
    try:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        return df
    except Exception:
        return df


def normalize_df(df):
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
# DATA FETCH (CLOUD SAFE)
# -------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def get_stock_data(symbol, period="6mo"):
    try:
        df = yf.download(symbol, period=period, interval="1d", progress=False, auto_adjust=False, threads=False)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        return normalize_df(df)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=1800, show_spinner=False)
def get_stock_info(symbol):
    try:
        t = yf.Ticker(symbol)
        info = t.info
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
        return pd.Series([50]*len(series), index=series.index)


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
        df["Momentum20"] = ((df["Close"] / df["Close"].shift(20)) - 1) * 100
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
        momentum = safe_float(df["Momentum20"].iloc[-1], 0)

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
            score += 10; reasons.append("EMA20 above EMA50")
        else:
            score -= 6
        if 45 <= rsi <= 65:
            score += 10; reasons.append("RSI healthy")
        elif 30 <= rsi < 45 or 65 < rsi <= 75:
            score += 4
        elif rsi < 30:
            score += 8; reasons.append("Oversold rebound zone")
        else:
            score -= 8
        if momentum > 8:
            score += 8; reasons.append("Strong 20D momentum")
        elif momentum < -8:
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


def fundamental_score(info):
    score = 40
    reasons = []
    try:
        pe = safe_float(info.get("trailingPE"), 0)
        pb = safe_float(info.get("priceToBook"), 0)
        roe = safe_float(info.get("returnOnEquity"), 0)
        roe = roe * 100 if abs(roe) < 2 else roe
        debt_eq = safe_float(info.get("debtToEquity"), 0)
        current_ratio = safe_float(info.get("currentRatio"), 0)
        margins = safe_float(info.get("profitMargins"), 0)
        margins = margins * 100 if abs(margins) < 2 else margins
        div = safe_float(info.get("dividendYield"), 0)
        div = div * 100 if abs(div) < 2 else div

        if 0 < pe <= 25:
            score += 15; reasons.append("Reasonable P/E")
        elif 25 < pe <= 40:
            score += 7
        elif pe > 60:
            score -= 8
        if 0 < pb <= 5:
            score += 8; reasons.append("Healthy P/B")
        elif pb > 10:
            score -= 5
        if roe >= 15:
            score += 15; reasons.append("Strong ROE")
        elif roe >= 10:
            score += 8
        elif 0 < roe < 5:
            score -= 5
        if 0 < debt_eq <= 80:
            score += 10; reasons.append("Manageable Debt")
        elif debt_eq > 200:
            score -= 10
        if current_ratio >= 1.2:
            score += 6; reasons.append("Healthy liquidity")
        elif 0 < current_ratio < 0.8:
            score -= 4
        if margins >= 10:
            score += 10; reasons.append("Strong margins")
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
# TRADING HELPERS
# -------------------------------
def support_resistance(df):
    try:
        support = safe_float(df["RollingLow20"].iloc[-1], safe_float(df["Low"].tail(20).min()))
        resistance = safe_float(df["RollingHigh20"].iloc[-1], safe_float(df["High"].tail(20).max()))
        return support, resistance
    except Exception:
        close = safe_float(df["Close"].iloc[-1])
        return close*0.95, close*1.05


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


def reversal_status(df):
    try:
        rsi = safe_float(df["RSI"].iloc[-1], 50)
        close = safe_float(df["Close"].iloc[-1])
        sma20 = safe_float(df["SMA20"].iloc[-1], close)
        if rsi < 35 and close > sma20 * 0.97:
            return "POTENTIAL BULLISH REVERSAL"
        if rsi > 70 and close < sma20 * 1.03:
            return "POTENTIAL BEARISH REVERSAL"
        return "NO CLEAR REVERSAL"
    except Exception:
        return "UNKNOWN"


def buy_sell_probability(tech_score_val, fund_score_val, close, support, resistance):
    try:
        rr = ((resistance - close) / max(close - support, 0.01)) if close > support else 1.0
        rr_bonus = min(max(rr * 5, 0), 15)
        buy_prob = min(95, max(5, int(tech_score_val * 0.55 + fund_score_val * 0.35 + rr_bonus)))
        sell_prob = 100 - buy_prob
        return buy_prob, sell_prob
    except Exception:
        return 50, 50


def risk_reward(close, support, resistance):
    try:
        downside = max(close - support, 0.01)
        upside = max(resistance - close, 0.0)
        rr = upside / downside if downside else 0
        return upside, downside, rr
    except Exception:
        return 0, 0, 0


def stoploss_target_plan(close, support, resistance, style="Swing"):
    try:
        if style == "Intraday":
            sl = max(close * 0.985, support)
            t1 = min(close * 1.015, resistance)
            t2 = min(close * 1.025, resistance * 1.02)
        else:
            sl = max(close * 0.95, support)
            t1 = min(close * 1.08, resistance)
            t2 = max(close * 1.12, resistance)
        return sl, t1, t2
    except Exception:
        return close*0.95, close*1.05, close*1.10

# -------------------------------
# WEALTH HELPERS
# -------------------------------
def lumpsum_projection(amount, rate, years):
    fv = amount * ((1 + rate / 100) ** years)
    rows = [{"Year": y, "Projected Value": amount * ((1 + rate / 100) ** y)} for y in range(1, years + 1)]
    return fv, pd.DataFrame(rows)


def sip_projection(monthly, rate, years):
    r = rate / 100 / 12
    n = years * 12
    if r == 0:
        fv = monthly * n
    else:
        fv = monthly * (((1 + r) ** n - 1) / r) * (1 + r)
    rows = []
    for y in range(1, years + 1):
        m = y * 12
        val = monthly * m if r == 0 else monthly * (((1 + r) ** m - 1) / r) * (1 + r)
        rows.append({"Year": y, "Projected Value": val})
    return fv, pd.DataFrame(rows)

# -------------------------------
# SCANNER DATA
# -------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def get_watchlist_snapshot(symbols):
    rows = []
    for s in symbols:
        try:
            df = get_stock_data(s, "6mo")
            info = get_stock_info(s)
            if df.empty:
                rows.append({"Symbol": s.replace('.NS',''), "Sector": SECTOR_MAP.get(s, "Other"), "Price": np.nan, "Tech": 0, "Fund": 0, "Combined": 0, "Verdict": "NA", "Breakout": "NA", "Reversal": "NA", "Momentum20": 0})
                continue
            df = add_indicators(df)
            close = safe_float(df["Close"].iloc[-1])
            tech, _, _ = technical_score(df)
            fund, _, _ = fundamental_score(info)
            comb, verdict = combined_score(tech, fund)
            rows.append({
                "Symbol": s.replace('.NS',''),
                "Sector": SECTOR_MAP.get(s, "Other"),
                "Price": round(close, 2),
                "Tech": tech,
                "Fund": fund,
                "Combined": comb,
                "Verdict": verdict,
                "Breakout": breakout_status(df),
                "Reversal": reversal_status(df),
                "Momentum20": round(safe_float(df["Momentum20"].iloc[-1], 0), 2)
            })
        except Exception:
            rows.append({"Symbol": s.replace('.NS',''), "Sector": SECTOR_MAP.get(s, "Other"), "Price": np.nan, "Tech": 0, "Fund": 0, "Combined": 0, "Verdict": "NA", "Breakout": "NA", "Reversal": "NA", "Momentum20": 0})
    return pd.DataFrame(rows)


def sector_rotation(scan_df):
    try:
        sec = scan_df.groupby("Sector", as_index=False).agg({"Combined":"mean", "Momentum20":"mean"})
        sec["Rotation Score"] = (sec["Combined"] * 0.7 + sec["Momentum20"] * 0.3).round(2)
        return sec.sort_values("Rotation Score", ascending=False)
    except Exception:
        return pd.DataFrame()

# -------------------------------
# EXCEL EXPORT
# -------------------------------
def make_excel_bytes(dfs: dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for sheet_name, df in dfs.items():
            try:
                df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
            except Exception:
                pass
    output.seek(0)
    return output.getvalue()

# -------------------------------
# HEADER
# -------------------------------
st.markdown("""
<div class='hero'>
  <div class='hero-title'>📊 NSE Stock Intelligence Pro MAX V8 INSTITUTIONAL</div>
  <div class='hero-sub'>Institutional-grade dashboard • Technical + Fundamental • Sector rotation • Breakout & reversal scanners • Risk/Reward • Stop-loss & target planner • Multi-holding portfolio DB • Excel export • Cloud-safe single app.py</div>
  <span class='pill'>Institutional Grade</span>
  <span class='pill'>Cloud Safe</span>
  <span class='pill'>Excel Export</span>
  <span class='pill'>Portfolio DB</span>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.title("⚙️ Institutional Control Center")
selected_stock = st.sidebar.selectbox("Select NSE Stock", NSE_STOCKS, index=0)
period = st.sidebar.selectbox("Data Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)
trade_style = st.sidebar.selectbox("Trade Style", ["Swing", "Intraday"], index=0)

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Wealth Planner")
lumpsum_amount = st.sidebar.number_input("Lumpsum (₹)", min_value=1000, value=100000, step=1000)
sip_amount = st.sidebar.number_input("Monthly SIP (₹)", min_value=500, value=10000, step=500)
expected_return = st.sidebar.slider("Expected Return (%)", 1, 30, 12)
planner_years = st.sidebar.slider("Years", 1, 30, 10)

# -------------------------------
# PORTFOLIO DB INIT
# -------------------------------
if "portfolio_db" not in st.session_state:
    st.session_state.portfolio_db = pd.DataFrame(columns=["Symbol", "Qty", "Avg Buy Price"])

# -------------------------------
# LOAD DATA
# -------------------------------
with st.spinner("Loading institutional market data safely..."):
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
tech_score_val, tech_signal, tech_reasons = technical_score(df)
fund_score_val, fund_rating, fund_reasons = fundamental_score(info)
combo_score, combo_verdict = combined_score(tech_score_val, fund_score_val)
support, resistance = support_resistance(df)
buy_prob, sell_prob = buy_sell_probability(tech_score_val, fund_score_val, close, support, resistance)
upside, downside, rr_ratio = risk_reward(close, support, resistance)
sl, t1, t2 = stoploss_target_plan(close, support, resistance, trade_style)

# -------------------------------
# TOP METRICS
# -------------------------------
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("📌 Stock", selected_stock.replace('.NS',''))
m2.metric("💹 Price", f"₹{close:,.2f}", f"{change_pct:.2f}%")
m3.metric("🧠 Tech Score", f"{tech_score_val}/100")
m4.metric("🏢 Fund Score", f"{fund_score_val}/100")
m5.metric("⭐ Combined", f"{combo_score}/100")
m6.metric("📢 Verdict", combo_verdict)

st.markdown("---")

# -------------------------------
# TABS
# -------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📈 Dashboard",
    "🧠 Technical Lab",
    "🏢 Fundamental Lab",
    "🔥 Institutional Scanner",
    "🏛️ Sector Rotation",
    "🎯 Trade Planner",
    "💼 Portfolio DB",
    "💰 Wealth Planner",
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
        fig.update_layout(title=f"{selected_stock} Institutional Dashboard", height=620)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🎯 Institutional Signal Board")
        st.write(f"**Technical Signal:** {tech_signal}")
        st.write(f"**Fundamental Rating:** {fund_rating}")
        st.write(f"**Final Verdict:** {combo_verdict}")
        st.write(f"**Breakout:** {breakout_status(df)}")
        st.write(f"**Reversal:** {reversal_status(df)}")
        st.write(f"**Support:** ₹{support:,.2f}")
        st.write(f"**Resistance:** ₹{resistance:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🎲 Probability + Risk")
        st.progress(buy_prob / 100)
        st.write(f"**Buy Probability:** {buy_prob}%")
        st.write(f"**Sell Probability:** {sell_prob}%")
        st.write(f"**Reward/Risk Ratio:** {rr_ratio:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# TAB 2 TECHNICAL LAB
# -------------------------------
with tab2:
    rsi = safe_float(df["RSI"].iloc[-1], 50)
    sma20 = safe_float(df["SMA20"].iloc[-1], close)
    sma50 = safe_float(df["SMA50"].iloc[-1], close)
    ema20 = safe_float(df["EMA20"].iloc[-1], close)
    ema50 = safe_float(df["EMA50"].iloc[-1], close)
    momentum20 = safe_float(df["Momentum20"].iloc[-1], 0)

    a,b,c,d,e = st.columns(5)
    a.metric("RSI", f"{rsi:.2f}")
    b.metric("SMA20", f"₹{sma20:,.2f}")
    c.metric("SMA50", f"₹{sma50:,.2f}")
    d.metric("EMA20", f"₹{ema20:,.2f}")
    e.metric("20D Momentum", f"{momentum20:.2f}%")

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
        sr_df = pd.DataFrame({"Level":["Support","Current","Resistance"], "Value":[support, close, resistance]})
        st.plotly_chart(px.bar(sr_df, x="Level", y="Value", title="Support / Resistance"), use_container_width=True)

    st.subheader("📝 Technical Reasons")
    for r in tech_reasons:
        st.write(f"- {r}")

# -------------------------------
# TAB 3 FUNDAMENTAL LAB
# -------------------------------
with tab3:
    st.subheader("🏢 Fundamental Analysis")
    snapshot = {
        "Company Name": info.get("longName", "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Industry": info.get("industry", "N/A"),
        "Market Cap": info.get("marketCap", "N/A"),
        "P/E Ratio": info.get("trailingPE", "N/A"),
        "P/B Ratio": info.get("priceToBook", "N/A"),
        "ROE": info.get("returnOnEquity", "N/A"),
        "Debt/Equity": info.get("debtToEquity", "N/A"),
        "Current Ratio": info.get("currentRatio", "N/A"),
        "Profit Margins": info.get("profitMargins", "N/A"),
        "Dividend Yield": info.get("dividendYield", "N/A"),
        "Book Value": info.get("bookValue", "N/A")
    }
    st.dataframe(pd.DataFrame(list(snapshot.items()), columns=["Metric", "Value"]), use_container_width=True)
    if fund_rating in ["STRONG", "GOOD"]:
        st.success(f"✅ Fundamental Rating: {fund_rating} ({fund_score_val}/100)")
    elif fund_rating == "AVERAGE":
        st.warning(f"⚠️ Fundamental Rating: {fund_rating} ({fund_score_val}/100)")
    else:
        st.error(f"❌ Fundamental Rating: {fund_rating} ({fund_score_val}/100)")
    st.subheader("📝 Fundamental Reasons")
    for r in fund_reasons:
        st.write(f"- {r}")
    st.text_area("📝 Business Summary", info.get("longBusinessSummary", "Business summary not available."), height=220)

# -------------------------------
# TAB 4 INSTITUTIONAL SCANNER
# -------------------------------
with tab4:
    st.subheader("🔥 Institutional Scanner")
    with st.spinner("Scanning watchlist..."):
        scan_df = get_watchlist_snapshot(WATCHLIST)
    st.dataframe(scan_df, use_container_width=True)

    if not scan_df.empty:
        st.subheader("🏆 Top 5 Leaders")
        top_df = scan_df.sort_values(by="Combined", ascending=False).head(5)
        st.dataframe(top_df, use_container_width=True)
        st.plotly_chart(px.bar(top_df, x="Symbol", y=["Tech", "Fund", "Combined"], barmode="group", title="Top 5 Multi-Stock Comparison"), use_container_width=True)

# -------------------------------
# TAB 5 SECTOR ROTATION
# -------------------------------
with tab5:
    st.subheader("🏛️ Sector Rotation Dashboard")
    with st.spinner("Building sector rotation model..."):
        scan_df = get_watchlist_snapshot(WATCHLIST)
        sector_df = sector_rotation(scan_df)
    if sector_df.empty:
        st.warning("Sector data unavailable.")
    else:
        st.dataframe(sector_df, use_container_width=True)
        st.plotly_chart(px.bar(sector_df, x="Sector", y="Rotation Score", title="Sector Rotation Score"), use_container_width=True)

# -------------------------------
# TAB 6 TRADE PLANNER
# -------------------------------
with tab6:
    st.subheader("🎯 Risk-Reward + Stop-Loss & Target Planner")
    t1c, t2c, t3c, t4c = st.columns(4)
    t1c.metric("Support", f"₹{support:,.2f}")
    t2c.metric("Resistance", f"₹{resistance:,.2f}")
    t3c.metric("Upside", f"₹{upside:,.2f}")
    t4c.metric("Downside", f"₹{downside:,.2f}")

    t5c, t6c, t7c, t8c = st.columns(4)
    t5c.metric("Reward/Risk", f"{rr_ratio:.2f}")
    t6c.metric("Stop Loss", f"₹{sl:,.2f}")
    t7c.metric("Target 1", f"₹{t1:,.2f}")
    t8c.metric("Target 2", f"₹{t2:,.2f}")

    if rr_ratio >= 2:
        st.success("✅ Attractive reward-to-risk setup")
    elif rr_ratio >= 1:
        st.warning("⚠️ Moderate reward-to-risk setup")
    else:
        st.error("❌ Weak reward-to-risk setup")

# -------------------------------
# TAB 7 PORTFOLIO DB
# -------------------------------
with tab7:
    st.subheader("💼 Multi-Holding Portfolio Database")

    with st.form("add_holding_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            new_symbol = st.selectbox("Symbol", NSE_STOCKS, key="pf_symbol")
        with c2:
            new_qty = st.number_input("Qty", min_value=1, value=10, step=1, key="pf_qty")
        with c3:
            new_avg = st.number_input("Avg Buy Price (₹)", min_value=1.0, value=1000.0, step=1.0, key="pf_avg")
        submitted = st.form_submit_button("➕ Add Holding")
        if submitted:
            new_row = pd.DataFrame([[new_symbol, new_qty, new_avg]], columns=["Symbol", "Qty", "Avg Buy Price"])
            st.session_state.portfolio_db = pd.concat([st.session_state.portfolio_db, new_row], ignore_index=True)
            st.success("Holding added.")

    portfolio_df = st.session_state.portfolio_db.copy()
    if portfolio_df.empty:
        st.info("No holdings added yet.")
    else:
        rows = []
        for _, row in portfolio_df.iterrows():
            sym = row["Symbol"]
            qty = safe_float(row["Qty"], 0)
            avg = safe_float(row["Avg Buy Price"], 0)
            dfx = get_stock_data(sym, "1mo")
            if dfx.empty:
                current = 0
            else:
                dfx = add_indicators(dfx)
                current = safe_float(dfx["Close"].iloc[-1], 0)
            invested = qty * avg
            current_val = qty * current
            pnl = current_val - invested
            pnl_pct = (pnl / invested * 100) if invested else 0
            rows.append({
                "Symbol": sym.replace('.NS',''), "Qty": qty, "Avg Buy": avg, "Current": current,
                "Invested": invested, "Current Value": current_val, "PnL": pnl, "PnL %": pnl_pct
            })
        live_pf = pd.DataFrame(rows)
        st.dataframe(live_pf, use_container_width=True)

        total_invested = live_pf["Invested"].sum()
        total_current = live_pf["Current Value"].sum()
        total_pnl = live_pf["PnL"].sum()
        total_pnl_pct = (total_pnl / total_invested * 100) if total_invested else 0

        p1,p2,p3,p4 = st.columns(4)
        p1.metric("Total Invested", f"₹{total_invested:,.2f}")
        p2.metric("Current Value", f"₹{total_current:,.2f}")
        p3.metric("Total PnL", f"₹{total_pnl:,.2f}")
        p4.metric("Total PnL %", f"{total_pnl_pct:.2f}%")

        export_bytes = make_excel_bytes({"Portfolio": live_pf})
        st.download_button("📥 Download Portfolio Excel", data=export_bytes, file_name="portfolio_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# -------------------------------
# TAB 8 WEALTH PLANNER
# -------------------------------
with tab8:
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
# TAB 9 RETURNS ANALYZER
# -------------------------------
with tab9:
    st.subheader("📊 Returns Analyzer")
    work = df.copy()
    work["Daily Return %"] = work["Close"].pct_change() * 100
    base = safe_float(work["Close"].iloc[0], close)
    work["Cumulative Return %"] = ((work["Close"] / base) - 1) * 100 if base else 0
    total_return = safe_float(work["Cumulative Return %"].iloc[-1], 0)
    annual_vol = safe_float(work["Daily Return %"].std(), 0) * np.sqrt(252)
    max_dd = ((work["Close"] / work["Close"].cummax()) - 1).min() * 100
    rv_ratio = (total_return / annual_vol) if annual_vol else 0

    r1,r2,r3,r4 = st.columns(4)
    r1.metric("Total Return", f"{total_return:.2f}%")
    r2.metric("Annualized Volatility", f"{annual_vol:.2f}%")
    r3.metric("Max Drawdown", f"{max_dd:.2f}%")
    r4.metric("Return/Vol Ratio", f"{rv_ratio:.2f}")

    st.plotly_chart(px.line(work, x="Date", y="Cumulative Return %", title="Cumulative Return %"), use_container_width=True)
    st.plotly_chart(px.histogram(work.dropna(), x="Daily Return %", nbins=50, title="Daily Return Distribution"), use_container_width=True)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("🚀 FINAL V8 INSTITUTIONAL GRADE CLOUD SAFE BUILD | Institutional scanner + sector rotation + trade planner + portfolio DB + Excel export | Single deployable app.py")

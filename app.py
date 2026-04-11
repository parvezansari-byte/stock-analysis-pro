import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="NSE Stock Intelligence Pro V3 ULTRA",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# THEME / STYLES
# =========================================================
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.15rem;
    }
    .sub-title {
        color: #9CA3AF;
        margin-bottom: 1rem;
        font-size: 1rem;
    }
    .small-note {
        color: #9CA3AF;
        font-size: 0.85rem;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 14px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# DEFAULT NSE UNIVERSE
# =========================================================
NIFTY_CORE = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "LT", "ITC",
    "HINDUNILVR", "BHARTIARTL", "KOTAKBANK", "AXISBANK", "ASIANPAINT", "MARUTI",
    "SUNPHARMA", "BAJFINANCE", "HCLTECH", "TITAN", "ULTRACEMCO", "NTPC",
    "POWERGRID", "M&M", "ADANIENT", "WIPRO", "NESTLEIND"
]

SECTOR_BANKING = ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK", "INDUSINDBK", "BANKBARODA", "PNB"]
SECTOR_IT = ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM", "LTIM", "PERSISTENT", "COFORGE"]
SECTOR_AUTO = ["MARUTI", "M&M", "TATAMOTORS", "EICHERMOT", "BAJAJ-AUTO", "HEROMOTOCO"]
SECTOR_PHARMA = ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "LUPIN", "TORNTPHARM"]
SECTOR_FMCG = ["ITC", "HINDUNILVR", "NESTLEIND", "BRITANNIA", "DABUR", "GODREJCP"]

SECTOR_MAP = {
    "Nifty Core 25": NIFTY_CORE,
    "Banking": SECTOR_BANKING,
    "IT": SECTOR_IT,
    "Auto": SECTOR_AUTO,
    "Pharma": SECTOR_PHARMA,
    "FMCG": SECTOR_FMCG,
}

# =========================================================
# HELPERS
# =========================================================
def to_ns_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if symbol.endswith(".NS"):
        return symbol
    return f"{symbol}.NS"

def safe_get(info, key, default=np.nan):
    try:
        return info.get(key, default)
    except Exception:
        return default

def format_large_number(x):
    if pd.isna(x):
        return "N/A"
    try:
        x = float(x)
    except:
        return str(x)

    if x >= 1e12:
        return f"₹ {x/1e12:.2f} T"
    elif x >= 1e9:
        return f"₹ {x/1e9:.2f} B"
    elif x >= 1e7:
        return f"₹ {x/1e7:.2f} Cr"
    elif x >= 1e5:
        return f"₹ {x/1e5:.2f} L"
    else:
        return f"₹ {x:,.2f}"

def format_percent(x):
    if pd.isna(x):
        return "N/A"
    try:
        x = float(x)
        if abs(x) <= 2:
            x = x * 100
        return f"{x:.2f}%"
    except:
        return str(x)

# =========================================================
# DATA FETCHING
# =========================================================
@st.cache_data(ttl=1800)
def fetch_stock_data(symbol: str, period: str = "1y"):
    ticker = yf.Ticker(to_ns_symbol(symbol))
    hist = ticker.history(period=period, auto_adjust=False)
    if hist.empty:
        return pd.DataFrame(), {}
    try:
        info = ticker.info
    except Exception:
        info = {}
    return hist.copy(), info

# =========================================================
# TECHNICAL INDICATORS
# =========================================================
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal
    return macd, macd_signal, macd_hist

def compute_bollinger(series, window=20, num_std=2):
    sma = series.rolling(window).mean()
    std = series.rolling(window).std()
    upper = sma + num_std * std
    lower = sma - num_std * std
    return sma, upper, lower

def compute_atr(df, period=14):
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    return atr

def add_indicators(df):
    df = df.copy()

    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()

    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()

    df["RSI14"] = compute_rsi(df["Close"], 14)

    macd, macd_signal, macd_hist = compute_macd(df["Close"])
    df["MACD"] = macd
    df["MACD_SIGNAL"] = macd_signal
    df["MACD_HIST"] = macd_hist

    bb_mid, bb_upper, bb_lower = compute_bollinger(df["Close"])
    df["BB_MID"] = bb_mid
    df["BB_UPPER"] = bb_upper
    df["BB_LOWER"] = bb_lower

    df["ATR14"] = compute_atr(df, 14)
    df["VOL20"] = df["Volume"].rolling(20).mean()

    if len(df) >= 252:
        df["52W_HIGH"] = df["High"].rolling(252).max()
        df["52W_LOW"] = df["Low"].rolling(252).min()
    else:
        df["52W_HIGH"] = df["High"].expanding().max()
        df["52W_LOW"] = df["Low"].expanding().min()

    return df

# =========================================================
# SCORING ENGINE
# =========================================================
def add_score_component(breakdown, label, points_awarded, max_points, available=True):
    breakdown.append({
        "Factor": label,
        "Points": points_awarded if available else "N/A",
        "Max": max_points if available else "N/A",
        "Available": available
    })

def normalize_score(raw_points, max_available_points):
    if max_available_points <= 0:
        return 50
    return round((raw_points / max_available_points) * 100, 2)

def calculate_fundamental_score(info):
    raw_score = 0
    max_score_available = 0
    breakdown = []

    pe = safe_get(info, "trailingPE", np.nan)
    pb = safe_get(info, "priceToBook", np.nan)
    roe = safe_get(info, "returnOnEquity", np.nan)
    de = safe_get(info, "debtToEquity", np.nan)
    pm = safe_get(info, "profitMargins", np.nan)
    om = safe_get(info, "operatingMargins", np.nan)
    rev_growth = safe_get(info, "revenueGrowth", np.nan)
    earn_growth = safe_get(info, "earningsGrowth", np.nan)
    dy = safe_get(info, "dividendYield", np.nan)

    # P/E (10)
    if pd.notna(pe) and pe > 0:
        max_score_available += 10
        pts = 10 if pe < 25 else 5 if pe < 40 else 0
        raw_score += pts
        add_score_component(breakdown, "P/E", pts, 10, True)
    else:
        add_score_component(breakdown, "P/E", 0, 10, False)

    # P/B (10)
    if pd.notna(pb) and pb > 0:
        max_score_available += 10
        pts = 10 if pb < 4 else 5 if pb < 8 else 0
        raw_score += pts
        add_score_component(breakdown, "P/B", pts, 10, True)
    else:
        add_score_component(breakdown, "P/B", 0, 10, False)

    # ROE (15)
    if pd.notna(roe):
        max_score_available += 15
        roe_pct = roe * 100 if abs(roe) <= 2 else roe
        pts = 15 if roe_pct > 15 else 8 if roe_pct > 8 else 0
        raw_score += pts
        add_score_component(breakdown, "ROE", pts, 15, True)
    else:
        add_score_component(breakdown, "ROE", 0, 15, False)

    # Debt to Equity (15)
    if pd.notna(de):
        max_score_available += 15
        pts = 15 if de < 80 else 8 if de < 150 else 0
        raw_score += pts
        add_score_component(breakdown, "Debt to Equity", pts, 15, True)
    else:
        add_score_component(breakdown, "Debt to Equity", 0, 15, False)

    # Profit Margin (10)
    if pd.notna(pm):
        max_score_available += 10
        pm_pct = pm * 100 if abs(pm) <= 2 else pm
        pts = 10 if pm_pct > 10 else 5 if pm_pct > 5 else 0
        raw_score += pts
        add_score_component(breakdown, "Profit Margin", pts, 10, True)
    else:
        add_score_component(breakdown, "Profit Margin", 0, 10, False)

    # Operating Margin (10)
    if pd.notna(om):
        max_score_available += 10
        om_pct = om * 100 if abs(om) <= 2 else om
        pts = 10 if om_pct > 15 else 5 if om_pct > 8 else 0
        raw_score += pts
        add_score_component(breakdown, "Operating Margin", pts, 10, True)
    else:
        add_score_component(breakdown, "Operating Margin", 0, 10, False)

    # Revenue Growth (10)
    if pd.notna(rev_growth):
        max_score_available += 10
        rg_pct = rev_growth * 100 if abs(rev_growth) <= 2 else rev_growth
        pts = 10 if rg_pct > 10 else 5 if rg_pct > 5 else 0
        raw_score += pts
        add_score_component(breakdown, "Revenue Growth", pts, 10, True)
    else:
        add_score_component(breakdown, "Revenue Growth", 0, 10, False)

    # Earnings Growth (10)
    if pd.notna(earn_growth):
        max_score_available += 10
        eg_pct = earn_growth * 100 if abs(earn_growth) <= 2 else earn_growth
        pts = 10 if eg_pct > 10 else 5 if eg_pct > 5 else 0
        raw_score += pts
        add_score_component(breakdown, "Earnings Growth", pts, 10, True)
    else:
        add_score_component(breakdown, "Earnings Growth", 0, 10, False)

    # Dividend Yield (10)
    if pd.notna(dy):
        max_score_available += 10
        dy_pct = dy * 100 if abs(dy) <= 2 else dy
        pts = 10 if dy_pct > 1 else 5 if dy_pct > 0 else 0
        raw_score += pts
        add_score_component(breakdown, "Dividend Yield", pts, 10, True)
    else:
        add_score_component(breakdown, "Dividend Yield", 0, 10, False)

    normalized = normalize_score(raw_score, max_score_available)
    return normalized, raw_score, max_score_available, breakdown

def calculate_technical_score(df):
    if df.empty or len(df) < 60:
        return 50, 0, 0, [{
            "Factor": "Not enough price history",
            "Points": "N/A",
            "Max": "N/A",
            "Available": False
        }]

    latest = df.iloc[-1]
    raw_score = 0
    max_score_available = 0
    breakdown = []

    # Price > 200 DMA (20)
    if pd.notna(latest["SMA200"]):
        max_score_available += 20
        pts = 20 if latest["Close"] > latest["SMA200"] else 0
        raw_score += pts
        add_score_component(breakdown, "Price > 200 DMA", pts, 20, True)
    else:
        add_score_component(breakdown, "Price > 200 DMA", 0, 20, False)

    # 50 DMA > 200 DMA (15)
    if pd.notna(latest["SMA50"]) and pd.notna(latest["SMA200"]):
        max_score_available += 15
        pts = 15 if latest["SMA50"] > latest["SMA200"] else 0
        raw_score += pts
        add_score_component(breakdown, "50 DMA > 200 DMA", pts, 15, True)
    else:
        add_score_component(breakdown, "50 DMA > 200 DMA", 0, 15, False)

    # EMA alignment (10)
    if pd.notna(latest["EMA20"]) and pd.notna(latest["EMA50"]):
        max_score_available += 10
        pts = 10 if latest["EMA20"] > latest["EMA50"] else 0
        raw_score += pts
        add_score_component(breakdown, "EMA20 > EMA50", pts, 10, True)
    else:
        add_score_component(breakdown, "EMA20 > EMA50", 0, 10, False)

    # RSI (15)
    rsi = latest["RSI14"]
    if pd.notna(rsi):
        max_score_available += 15
        if 55 <= rsi <= 70:
            pts = 15
        elif 45 <= rsi < 55:
            pts = 8
        elif 70 < rsi <= 80:
            pts = 5
        else:
            pts = 0
        raw_score += pts
        add_score_component(breakdown, "RSI Strength", pts, 15, True)
    else:
        add_score_component(breakdown, "RSI Strength", 0, 15, False)

    # MACD (10)
    if pd.notna(latest["MACD"]) and pd.notna(latest["MACD_SIGNAL"]):
        max_score_available += 10
        pts = 10 if latest["MACD"] > latest["MACD_SIGNAL"] else 0
        raw_score += pts
        add_score_component(breakdown, "MACD Bullish", pts, 10, True)
    else:
        add_score_component(breakdown, "MACD Bullish", 0, 10, False)

    # Volume (15)
    if pd.notna(latest["VOL20"]) and latest["VOL20"] > 0:
        max_score_available += 15
        if latest["Volume"] > 1.5 * latest["VOL20"]:
            pts = 15
        elif latest["Volume"] > latest["VOL20"]:
            pts = 8
        else:
            pts = 0
        raw_score += pts
        add_score_component(breakdown, "Volume Confirmation", pts, 15, True)
    else:
        add_score_component(breakdown, "Volume Confirmation", 0, 15, False)

    # Near 52W high (10)
    if pd.notna(latest["52W_HIGH"]) and latest["52W_HIGH"] > 0:
        max_score_available += 10
        dist = ((latest["52W_HIGH"] - latest["Close"]) / latest["52W_HIGH"]) * 100
        if dist < 10:
            pts = 10
        elif dist < 20:
            pts = 5
        else:
            pts = 0
        raw_score += pts
        add_score_component(breakdown, "Near 52W High", pts, 10, True)
    else:
        add_score_component(breakdown, "Near 52W High", 0, 10, False)

    # ATR risk (5)
    if pd.notna(latest["ATR14"]) and latest["Close"] > 0:
        max_score_available += 5
        atr_pct = (latest["ATR14"] / latest["Close"]) * 100
        pts = 5 if atr_pct < 4 else 0
        raw_score += pts
        add_score_component(breakdown, "Controlled Volatility", pts, 5, True)
    else:
        add_score_component(breakdown, "Controlled Volatility", 0, 5, False)

    normalized = normalize_score(raw_score, max_score_available)
    return normalized, raw_score, max_score_available, breakdown

# =========================================================
# VERDICT ENGINE
# =========================================================
def get_trend_label(df):
    if df.empty or len(df) < 60:
        return "Insufficient Data"

    latest = df.iloc[-1]
    close = latest["Close"]
    sma50 = latest["SMA50"]
    sma200 = latest["SMA200"]

    if pd.notna(sma50) and pd.notna(sma200):
        if close > sma50 > sma200:
            return "Strong Uptrend"
        elif close > sma50 and sma50 <= sma200:
            return "Early Uptrend"
        elif close < sma50 < sma200:
            return "Strong Downtrend"
        elif close < sma50 and sma50 >= sma200:
            return "Weak / Sideways"
    return "Sideways"

def get_risk_label(df):
    if df.empty:
        return "Unknown"
    latest = df.iloc[-1]
    if pd.notna(latest["ATR14"]) and latest["Close"] > 0:
        atr_pct = (latest["ATR14"] / latest["Close"]) * 100
        if atr_pct < 2.5:
            return "Low Risk"
        elif atr_pct < 4.5:
            return "Moderate Risk"
        else:
            return "High Risk"
    return "Unknown"

def get_verdict(combined_score):
    if combined_score >= 80:
        return "🔥 STRONG BUY / HIGH QUALITY"
    elif combined_score >= 65:
        return "✅ BUY / WATCHLIST PRIORITY"
    elif combined_score >= 50:
        return "👀 WATCHLIST / NEUTRAL"
    else:
        return "⚠️ AVOID / WEAK SETUP"

def get_position_plan(latest_close, df):
    latest = df.iloc[-1]
    atr = latest["ATR14"] if pd.notna(latest["ATR14"]) else np.nan
    sma20 = latest["SMA20"] if pd.notna(latest["SMA20"]) else np.nan
    sma50 = latest["SMA50"] if pd.notna(latest["SMA50"]) else np.nan

    if pd.notna(atr):
        stop_loss = round(latest_close - (1.5 * atr), 2)
        target1 = round(latest_close + (2 * atr), 2)
        target2 = round(latest_close + (4 * atr), 2)
    else:
        stop_loss = round(latest_close * 0.93, 2)
        target1 = round(latest_close * 1.08, 2)
        target2 = round(latest_close * 1.15, 2)

    support = round(sma20, 2) if pd.notna(sma20) else "N/A"
    swing_support = round(sma50, 2) if pd.notna(sma50) else "N/A"

    return {
        "Support": support,
        "Swing Support": swing_support,
        "Stop Loss": stop_loss,
        "Target 1": target1,
        "Target 2": target2
    }

# =========================================================
# CHARTS
# =========================================================
def create_price_chart(df, symbol):
    chart_df = df.tail(250).copy()

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.62, 0.18, 0.20]
    )

    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            name="Price"
        ),
        row=1, col=1
    )

    fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df["SMA20"], mode="lines", name="SMA20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df["SMA50"], mode="lines", name="SMA50"), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df["SMA200"], mode="lines", name="SMA200"), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df["BB_UPPER"], mode="lines", name="BB Upper"), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df["BB_LOWER"], mode="lines", name="BB Lower"), row=1, col=1)

    fig.add_trace(go.Bar(x=chart_df.index, y=chart_df["Volume"], name="Volume"), row=2, col=1)

    fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df["RSI14"], mode="lines", name="RSI14"), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", row=3, col=1)

    fig.update_layout(
        title=f"{symbol} - Price + Technical Analysis",
        xaxis_rangeslider_visible=False,
        height=860,
        legend=dict(orientation="h")
    )
    return fig

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("📊 NSE Stock Intelligence Pro")
page = st.sidebar.radio(
    "Choose Module",
    ["Single Stock Analysis", "Sector Screener", "Top Ranked Watchlist", "About"]
)

st.sidebar.markdown("---")
selected_symbol = st.sidebar.selectbox("Quick NSE Pick", NIFTY_CORE, index=0)
manual_symbol = st.sidebar.text_input("Or Enter NSE Symbol", value=selected_symbol).upper().strip()
period = st.sidebar.selectbox("Price History", ["6mo", "1y", "2y", "5y"], index=1)

symbol = manual_symbol if manual_symbol else selected_symbol

st.sidebar.markdown("---")
st.sidebar.caption("Built for Indian NSE (.NS) stocks")

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="main-title">📈 NSE Stock Intelligence Pro V3 ULTRA</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Production Pack • Fundamental + Technical + Sector Screener + Ranked Watchlist + Trade Plan</div>',
    unsafe_allow_html=True
)

# =========================================================
# PAGE 1: SINGLE STOCK ANALYSIS
# =========================================================
if page == "Single Stock Analysis":
    hist, info = fetch_stock_data(symbol, period)

    if hist.empty:
        st.error("No data found. Please check NSE symbol (example: RELIANCE, TCS, INFY, AXISBANK).")
    else:
        df = add_indicators(hist)

        latest = df.iloc[-1]
        prev_close = df["Close"].iloc[-2] if len(df) > 1 else latest["Close"]
        price_change = latest["Close"] - prev_close
        price_change_pct = (price_change / prev_close * 100) if prev_close != 0 else 0

        fundamental_score, f_raw, f_max, f_breakdown = calculate_fundamental_score(info)
        technical_score, t_raw, t_max, t_breakdown = calculate_technical_score(df)
        combined_score = round((0.6 * fundamental_score) + (0.4 * technical_score), 2)

        verdict = get_verdict(combined_score)
        trend = get_trend_label(df)
        risk = get_risk_label(df)
        plan = get_position_plan(latest["Close"], df)

        # Top metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Price", f"₹ {latest['Close']:.2f}", f"{price_change:+.2f} ({price_change_pct:+.2f}%)")
        c2.metric("Fundamental Score", f"{fundamental_score}/100")
        c3.metric("Technical Score", f"{technical_score}/100")
        c4.metric("Combined Score", f"{combined_score}/100")

        st.success(f"Verdict: {verdict}")
        st.info(f"Trend: **{trend}** | Risk: **{risk}**")

        d1, d2 = st.columns(2)
        d1.caption(f"Fundamental data availability: {f_max}/100 score-points available")
        d2.caption(f"Technical data availability: {t_max}/100 score-points available")

        st.plotly_chart(create_price_chart(df, symbol), use_container_width=True)

        # Trade Plan
        st.markdown("## 🎯 Trade Plan / Position Framework")
        p1, p2, p3, p4, p5 = st.columns(5)
        p1.metric("Support", plan["Support"])
        p2.metric("Swing Support", plan["Swing Support"])
        p3.metric("Stop Loss", plan["Stop Loss"])
        p4.metric("Target 1", plan["Target 1"])
        p5.metric("Target 2", plan["Target 2"])

        # Snapshots
        colA, colB = st.columns(2)

        with colA:
            st.markdown("## 🧾 Fundamental Snapshot")

            market_cap = safe_get(info, "marketCap", np.nan)
            pe = safe_get(info, "trailingPE", np.nan)
            pb = safe_get(info, "priceToBook", np.nan)
            roe = safe_get(info, "returnOnEquity", np.nan)
            de = safe_get(info, "debtToEquity", np.nan)
            pm = safe_get(info, "profitMargins", np.nan)
            om = safe_get(info, "operatingMargins", np.nan)
            rev_growth = safe_get(info, "revenueGrowth", np.nan)
            earn_growth = safe_get(info, "earningsGrowth", np.nan)
            dy = safe_get(info, "dividendYield", np.nan)
            sector = safe_get(info, "sector", "N/A")
            industry = safe_get(info, "industry", "N/A")

            fund_df = pd.DataFrame({
                "Metric": [
                    "Market Cap", "P/E", "P/B", "ROE", "Debt to Equity",
                    "Profit Margin", "Operating Margin", "Revenue Growth",
                    "Earnings Growth", "Dividend Yield", "Sector", "Industry"
                ],
                "Value": [
                    format_large_number(market_cap),
                    "N/A" if pd.isna(pe) else round(float(pe), 2),
                    "N/A" if pd.isna(pb) else round(float(pb), 2),
                    format_percent(roe),
                    "N/A" if pd.isna(de) else round(float(de), 2),
                    format_percent(pm),
                    format_percent(om),
                    format_percent(rev_growth),
                    format_percent(earn_growth),
                    format_percent(dy),
                    sector,
                    industry
                ]
            })
            st.dataframe(fund_df, use_container_width=True, hide_index=True)

        with colB:
            st.markdown("## 📉 Technical Snapshot")

            dist_52w_high = np.nan
            dist_52w_low = np.nan

            if latest["52W_HIGH"] > 0:
                dist_52w_high = ((latest["52W_HIGH"] - latest["Close"]) / latest["52W_HIGH"]) * 100
            if latest["52W_LOW"] > 0:
                dist_52w_low = ((latest["Close"] - latest["52W_LOW"]) / latest["52W_LOW"]) * 100

            tech_df = pd.DataFrame({
                "Metric": [
                    "SMA20", "SMA50", "SMA200", "EMA20", "EMA50",
                    "RSI14", "MACD", "MACD Signal", "ATR14",
                    "20D Avg Volume", "52W High", "52W Low",
                    "Distance from 52W High", "Distance above 52W Low"
                ],
                "Value": [
                    round(latest["SMA20"], 2) if pd.notna(latest["SMA20"]) else "N/A",
                    round(latest["SMA50"], 2) if pd.notna(latest["SMA50"]) else "N/A",
                    round(latest["SMA200"], 2) if pd.notna(latest["SMA200"]) else "N/A",
                    round(latest["EMA20"], 2) if pd.notna(latest["EMA20"]) else "N/A",
                    round(latest["EMA50"], 2) if pd.notna(latest["EMA50"]) else "N/A",
                    round(latest["RSI14"], 2) if pd.notna(latest["RSI14"]) else "N/A",
                    round(latest["MACD"], 2) if pd.notna(latest["MACD"]) else "N/A",
                    round(latest["MACD_SIGNAL"], 2) if pd.notna(latest["MACD_SIGNAL"]) else "N/A",
                    round(latest["ATR14"], 2) if pd.notna(latest["ATR14"]) else "N/A",
                    round(latest["VOL20"], 0) if pd.notna(latest["VOL20"]) else "N/A",
                    round(latest["52W_HIGH"], 2) if pd.notna(latest["52W_HIGH"]) else "N/A",
                    round(latest["52W_LOW"], 2) if pd.notna(latest["52W_LOW"]) else "N/A",
                    f"{dist_52w_high:.2f}%" if pd.notna(dist_52w_high) else "N/A",
                    f"{dist_52w_low:.2f}%" if pd.notna(dist_52w_low) else "N/A",
                ]
            })
            st.dataframe(tech_df, use_container_width=True, hide_index=True)

        # Score Breakdown
        st.markdown("## 🏅 Score Breakdown")
        s1, s2 = st.columns(2)
        with s1:
            st.markdown("### Fundamental Score Breakdown")
            st.dataframe(pd.DataFrame(f_breakdown), use_container_width=True, hide_index=True)
        with s2:
            st.markdown("### Technical Score Breakdown")
            st.dataframe(pd.DataFrame(t_breakdown), use_container_width=True, hide_index=True)

        # Recent Data
        st.markdown("## 📋 Recent Price Data")
        recent = df.tail(10)[["Open", "High", "Low", "Close", "Volume"]].round(2)
        st.dataframe(recent, use_container_width=True)

# =========================================================
# PAGE 2: SECTOR SCREENER
# =========================================================
elif page == "Sector Screener":
    st.markdown("## 🧮 Sector Screener")
    sector_choice = st.selectbox("Select Sector Basket", list(SECTOR_MAP.keys()))
    universe = SECTOR_MAP[sector_choice]

    if st.button("Run Sector Screener"):
        results = []
        progress = st.progress(0)
        status = st.empty()

        for i, sym in enumerate(universe):
            status.write(f"Scanning {sym}...")
            hist, info = fetch_stock_data(sym, "1y")

            if not hist.empty:
                try:
                    df = add_indicators(hist)
                    latest = df.iloc[-1]

                    f_score, f_raw, f_max, _ = calculate_fundamental_score(info)
                    t_score, t_raw, t_max, _ = calculate_technical_score(df)
                    combined = round((0.6 * f_score) + (0.4 * t_score), 2)

                    results.append({
                        "Symbol": sym,
                        "Close": round(latest["Close"], 2),
                        "Trend": get_trend_label(df),
                        "Risk": get_risk_label(df),
                        "RSI": round(latest["RSI14"], 2) if pd.notna(latest["RSI14"]) else np.nan,
                        "Fund Score": f_score,
                        "Tech Score": t_score,
                        "Combined": combined,
                        "F Raw": f"{f_raw}/{f_max if f_max > 0 else 'N/A'}",
                        "T Raw": f"{t_raw}/{t_max if t_max > 0 else 'N/A'}",
                        "Verdict": get_verdict(combined)
                    })
                except Exception:
                    pass

            progress.progress((i + 1) / len(universe))

        status.empty()

        if results:
            screener_df = pd.DataFrame(results).sort_values("Combined", ascending=False).reset_index(drop=True)
            st.dataframe(screener_df, use_container_width=True, hide_index=True)

            csv = screener_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download Sector Screener CSV",
                data=csv,
                file_name=f"{sector_choice.lower().replace(' ', '_')}_screener.csv",
                mime="text/csv"
            )
        else:
            st.warning("No results found. Try again later.")

# =========================================================
# PAGE 3: TOP RANKED WATCHLIST
# =========================================================
elif page == "Top Ranked Watchlist":
    st.markdown("## 🏆 Top Ranked Watchlist (Nifty Core 25)")

    if st.button("Generate Ranked Watchlist"):
        results = []
        progress = st.progress(0)
        status = st.empty()

        for i, sym in enumerate(NIFTY_CORE):
            status.write(f"Ranking {sym}...")
            hist, info = fetch_stock_data(sym, "1y")

            if not hist.empty:
                try:
                    df = add_indicators(hist)
                    latest = df.iloc[-1]

                    f_score, f_raw, f_max, _ = calculate_fundamental_score(info)
                    t_score, t_raw, t_max, _ = calculate_technical_score(df)
                    combined = round((0.6 * f_score) + (0.4 * t_score), 2)

                    plan = get_position_plan(latest["Close"], df)

                    results.append({
                        "Rank Candidate": sym,
                        "Close": round(latest["Close"], 2),
                        "Trend": get_trend_label(df),
                        "Risk": get_risk_label(df),
                        "Fund Score": f_score,
                        "Tech Score": t_score,
                        "Combined": combined,
                        "Support": plan["Support"],
                        "Stop Loss": plan["Stop Loss"],
                        "Target 1": plan["Target 1"],
                        "Verdict": get_verdict(combined)
                    })
                except Exception:
                    pass

            progress.progress((i + 1) / len(NIFTY_CORE))

        status.empty()

        if results:
            watchlist_df = pd.DataFrame(results).sort_values("Combined", ascending=False).reset_index(drop=True)
            watchlist_df.index = watchlist_df.index + 1
            st.dataframe(watchlist_df, use_container_width=True)

            top5 = watchlist_df.head(5)
            st.markdown("### ⭐ Top 5 Priority Watchlist")
            st.dataframe(top5, use_container_width=True)

            csv = watchlist_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download Ranked Watchlist CSV",
                data=csv,
                file_name="top_ranked_watchlist.csv",
                mime="text/csv"
            )
        else:
            st.warning("No watchlist generated. Try again later.")

# =========================================================
# PAGE 4: ABOUT
# =========================================================
else:
    st.markdown("## ℹ️ About This Production Pack")
    st.markdown("""
### NSE Stock Intelligence Pro V3 ULTRA

This is a **production-style Streamlit app** built for:

- **Single stock deep analysis**
- **Normalized fundamental scoring**
- **Technical trend scoring**
- **Sector basket screening**
- **Top ranked watchlist generation**
- **Basic trade plan / position framework**

### Core Logic
- **Fundamental Score** = normalized on available fundamental data
- **Technical Score** = normalized on available technical indicators
- **Combined Score** = `0.6 × Fundamental + 0.4 × Technical`

### Best For
- NSE stock shortlisting
- Watchlist preparation
- Client demo tool
- Advisory workflow support
- Daily research routine

### Disclaimer
- For **education / research only**
- Always validate before real investment decisions
- Yahoo Finance data for some NSE symbols may be incomplete
""")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption(f"Built with Streamlit + yfinance | NSE (.NS) | FINAL V3 ULTRA PRODUCTION | {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

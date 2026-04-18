import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import math
import time

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="NSE Stock Intelligence Pro MAX V9.1 LIGHT",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PREMIUM ATTRACTIVE UI
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
}

/* Main app background */
.stApp {
    background: linear-gradient(135deg, #0b1020 0%, #111827 35%, #0f172a 70%, #0b1120 100%);
    color: #ffffff;
}

/* Remove top white spacing */
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Hero */
.hero {
    padding: 1.3rem 1.5rem;
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.92), rgba(2,132,199,0.18));
    border: 1px solid rgba(56,189,248,0.20);
    box-shadow: 0 8px 30px rgba(0,0,0,0.28);
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
}
.hero-sub {
    color: #cbd5e1;
    font-size: 0.95rem;
    margin-top: 0.2rem;
}

/* Pills */
.pill {
    display: inline-block;
    padding: 0.35rem 0.8rem;
    margin-right: 0.35rem;
    margin-top: 0.5rem;
    border-radius: 999px;
    background: rgba(59,130,246,0.10);
    border: 1px solid rgba(59,130,246,0.25);
    color: #bfdbfe;
    font-size: 0.8rem;
    font-weight: 600;
}

/* Card */
.soft-card {
    padding: 1rem;
    border-radius: 18px;
    background: rgba(17,24,39,0.72);
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 6px 20px rgba(0,0,0,0.18);
    margin-bottom: 0.8rem;
}

/* Beautiful buttons */
.stButton>button {
    width: 100%;
    border-radius: 14px;
    border: 1px solid rgba(56,189,248,0.25);
    background: linear-gradient(135deg, #0284c7, #2563eb);
    color: white;
    font-weight: 700;
    padding: 0.55rem 1rem;
    box-shadow: 0 6px 18px rgba(37,99,235,0.25);
}
.stButton>button:hover {
    border: 1px solid rgba(125,211,252,0.45);
    background: linear-gradient(135deg, #0ea5e9, #3b82f6);
}

/* Inputs */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
.stTextInput > div > div,
.stNumberInput > div > div,
.stTextArea textarea {
    background: rgba(15,23,42,0.75) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: white !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: rgba(17,24,39,0.72);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 0.8rem;
    border-radius: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.14);
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(17,24,39,0.6);
    border-radius: 12px;
    padding: 10px 16px;
}

/* Status boxes */
.good-box {
    padding: 0.9rem 1rem;
    border-radius: 14px;
    background: rgba(34,197,94,0.14);
    border: 1px solid rgba(34,197,94,0.28);
    color: #86efac;
    font-weight: 700;
    margin-bottom: 0.6rem;
}
.warn-box {
    padding: 0.9rem 1rem;
    border-radius: 14px;
    background: rgba(245,158,11,0.14);
    border: 1px solid rgba(245,158,11,0.28);
    color: #fcd34d;
    font-weight: 700;
    margin-bottom: 0.6rem;
}
.bad-box {
    padding: 0.9rem 1rem;
    border-radius: 14px;
    background: rgba(239,68,68,0.14);
    border: 1px solid rgba(239,68,68,0.28);
    color: #fca5a5;
    font-weight: 700;
    margin-bottom: 0.6rem;
}
.info-box {
    padding: 0.9rem 1rem;
    border-radius: 14px;
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.26);
    color: #bfdbfe;
    font-weight: 600;
    margin-bottom: 0.6rem;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# NIFTY LISTS
# =========================================================
NIFTY_50 = sorted([
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK",
    "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BEL", "BHARTIARTL",
    "BPCL", "BRITANNIA", "CIPLA", "COALINDIA", "DRREDDY",
    "EICHERMOT", "ETERNAL", "GRASIM", "HCLTECH", "HDFCBANK",
    "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK",
    "INDUSINDBK", "INFY", "ITC", "JIOFIN", "JSWSTEEL",
    "KOTAKBANK", "LT", "M&M", "MARUTI", "NESTLEIND",
    "NTPC", "ONGC", "POWERGRID", "RELIANCE", "SBILIFE",
    "SBIN", "SHRIRAMFIN", "SUNPHARMA", "TATACONSUM", "TATAMOTORS",
    "TATASTEEL", "TCS", "TECHM", "TITAN", "TRENT"
])

NIFTY_NEXT_50 = sorted([
    "ABB", "ADANIENSOL", "ADANIGREEN", "ADANIPOWER", "AMBUJACEM",
    "BAJAJHLDNG", "BANKBARODA", "BOSCHLTD", "CANBK", "CGPOWER",
    "CHOLAFIN", "DABUR", "DIVISLAB", "DLF", "DMART",
    "GAIL", "GODREJCP", "HAL", "HAVELLS", "ICICIGI",
    "ICICIPRULI", "INDIGO", "INDUSTOWER", "IOC", "IRCTC",
    "JINDALSTEL", "LODHA", "MOTHERSON", "NAUKRI", "NMDC",
    "PIDILITIND", "PNB", "RECLTD", "SAIL", "SHREECEM",
    "SIEMENS", "TORNTPHARM", "TVSMOTOR", "UNITDSPR", "VBL",
    "VEDL", "ZYDUSLIFE", "PFC", "HINDPETRO", "BHEL",
    "BERGEPAINT", "CONCOR", "MARICO", "TATAPOWER", "UPL"
])

NIFTY_100 = sorted(list(set(NIFTY_50 + NIFTY_NEXT_50)))

# =========================================================
# SESSION STATE
# =========================================================
if "elite_watchlist" not in st.session_state:
    st.session_state.elite_watchlist = []

if "portfolio_db" not in st.session_state:
    st.session_state.portfolio_db = []

# =========================================================
# HELPERS
# =========================================================
def safe_num(x, default=np.nan):
    try:
        if x is None:
            return default
        v = float(x)
        if math.isinf(v):
            return default
        return v
    except:
        return default

def fmt(x, decimals=2):
    return f"{x:,.{decimals}f}" if pd.notna(x) else "N/A"

def get_nse_symbol(symbol):
    return f"{str(symbol).strip().upper().replace('.NS','')}.NS"

def clamp(v, lo=0, hi=100):
    try:
        return max(lo, min(hi, float(v)))
    except:
        return lo

def normalize_linear(x, low, high, invert=False):
    if pd.isna(x):
        return np.nan
    if high == low:
        return 50
    score = ((x - low) / (high - low)) * 100
    if invert:
        score = 100 - score
    return clamp(score)

def get_verdict(score):
    if score >= 80:
        return "🔥 STRONG BUY", "good"
    elif score >= 68:
        return "✅ BUY / ACCUMULATE", "good"
    elif score >= 55:
        return "🟡 HOLD / WATCH", "warn"
    elif score >= 42:
        return "⚠️ WAIT", "warn"
    else:
        return "❌ AVOID", "bad"

# =========================================================
# CACHE DATA
# =========================================================
@st.cache_data(ttl=900, show_spinner=False)
def fetch_stock_data(symbol: str, period: str = "1y"):
    try:
        ticker = yf.Ticker(get_nse_symbol(symbol))
        hist = ticker.history(period=period, auto_adjust=False)

        if hist is None or hist.empty:
            hist = ticker.history(period="6mo", auto_adjust=False)

        if hist is None or hist.empty:
            return None, None, "No data found"

        hist = hist.dropna(subset=["Open", "High", "Low", "Close"])
        if hist.empty:
            return None, None, "No valid OHLC data"

        try:
            info = ticker.info
            if not isinstance(info, dict):
                info = {}
        except:
            info = {}

        return hist, info, None
    except Exception as e:
        return None, None, str(e)

# =========================================================
# INDICATORS
# =========================================================
def add_indicators(df):
    df = df.copy()
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI14"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9, adjust=False).mean()

    mid = df["Close"].rolling(20).mean()
    std = df["Close"].rolling(20).std()
    df["BB_UPPER"] = mid + 2 * std
    df["BB_LOWER"] = mid - 2 * std

    prev_close = df["Close"].shift(1)
    tr1 = df["High"] - df["Low"]
    tr2 = (df["High"] - prev_close).abs()
    tr3 = (df["Low"] - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["ATR14"] = tr.rolling(14).mean()

    df["VOL20"] = df["Volume"].rolling(20).mean()
    return df

# =========================================================
# FUNDAMENTAL LIGHT SCORING
# =========================================================
def score_fundamentals_light(info):
    pe = safe_num(info.get("trailingPE"))
    pb = safe_num(info.get("priceToBook"))
    roe = safe_num(info.get("returnOnEquity"))
    debt = safe_num(info.get("debtToEquity"))
    margin = safe_num(info.get("profitMargins"))
    growth = safe_num(info.get("revenueGrowth"))
    div = safe_num(info.get("dividendYield"))

    if pd.notna(roe) and roe < 5:
        roe *= 100
    if pd.notna(margin) and margin < 5:
        margin *= 100
    if pd.notna(growth) and growth < 5:
        growth *= 100
    if pd.notna(div) and div < 5:
        div *= 100

    metrics = {
        "PE": normalize_linear(pe, 5, 40, invert=True) if pd.notna(pe) and pe > 0 else np.nan,
        "PB": normalize_linear(pb, 0.5, 8, invert=True) if pd.notna(pb) and pb > 0 else np.nan,
        "ROE": normalize_linear(roe, 5, 25),
        "Debt": normalize_linear(debt, 0, 2.5, invert=True),
        "Margin": normalize_linear(margin, 2, 25),
        "Growth": normalize_linear(growth, -5, 20),
        "Dividend": normalize_linear(div, 0, 5)
    }

    vals = [v for v in metrics.values() if pd.notna(v)]
    if not vals:
        return 50.0, metrics

    score = round(np.nanmean(vals), 1)
    return score, metrics

# =========================================================
# TECHNICAL SCORING
# =========================================================
def score_technical(df):
    if df is None or df.empty or len(df) < 50:
        return 45.0, "Neutral", {}

    last = df.iloc[-1]
    close = safe_num(last["Close"])
    sma20 = safe_num(last["SMA20"])
    sma50 = safe_num(last["SMA50"])
    sma200 = safe_num(last["SMA200"])
    rsi = safe_num(last["RSI14"])
    macd = safe_num(last["MACD"])
    macd_signal = safe_num(last["MACD_SIGNAL"])

    metrics = {
        "Above20DMA": 100 if pd.notna(close) and pd.notna(sma20) and close > sma20 else 30,
        "Above50DMA": 100 if pd.notna(close) and pd.notna(sma50) and close > sma50 else 30,
        "Above200DMA": 100 if pd.notna(close) and pd.notna(sma200) and close > sma200 else 20,
        "RSI": 90 if pd.notna(rsi) and 45 <= rsi <= 65 else 55 if pd.notna(rsi) and rsi < 35 else 40 if pd.notna(rsi) else np.nan,
        "MACD": 85 if pd.notna(macd) and pd.notna(macd_signal) and macd > macd_signal else 35
    }

    vals = [v for v in metrics.values() if pd.notna(v)]
    score = round(np.nanmean(vals), 1) if vals else 45.0

    trend = "Neutral"
    if pd.notna(close) and pd.notna(sma50) and pd.notna(sma200):
        if close > sma50 > sma200:
            trend = "Strong Uptrend"
        elif close > sma50:
            trend = "Uptrend"
        elif close < sma50 < sma200:
            trend = "Downtrend"
        else:
            trend = "Sideways"

    return score, trend, metrics

# =========================================================
# ANALYSIS ENGINE
# =========================================================
def analyze_stock(symbol, period="1y"):
    hist, info, err = fetch_stock_data(symbol, period)
    if err:
        return {"error": err}

    df = add_indicators(hist)
    last = df.iloc[-1]

    last_close = safe_num(last["Close"])
    prev_close = safe_num(df["Close"].iloc[-2]) if len(df) > 1 else np.nan
    change = last_close - prev_close if pd.notna(last_close) and pd.notna(prev_close) else np.nan
    change_pct = (change / prev_close * 100) if pd.notna(change) and pd.notna(prev_close) and prev_close != 0 else np.nan

    fund_score, fund_metrics = score_fundamentals_light(info)
    tech_score, trend, tech_metrics = score_technical(df)

    balanced = round((fund_score * 0.45) + (tech_score * 0.55), 1)
    swing = round((fund_score * 0.30) + (tech_score * 0.70), 1)
    long_term = round((fund_score * 0.65) + (tech_score * 0.35), 1)

    support = df["Low"].tail(30).min() if len(df) >= 30 else np.nan
    resistance = df["High"].tail(30).max() if len(df) >= 30 else np.nan
    atr = safe_num(last["ATR14"])

    stop_loss = round(last_close - 1.2 * atr, 2) if pd.notna(last_close) and pd.notna(atr) else np.nan
    target1 = round(last_close + 1.5 * atr, 2) if pd.notna(last_close) and pd.notna(atr) else np.nan
    target2 = round(last_close + 3.0 * atr, 2) if pd.notna(last_close) and pd.notna(atr) else np.nan

    breakout = False
    reversal = False
    try:
        recent_high = df["High"].tail(20).max()
        recent_low = df["Low"].tail(20).min()
        vol20 = safe_num(last["VOL20"])
        volume = safe_num(last["Volume"])
        rsi = safe_num(last["RSI14"])

        breakout = (last_close >= recent_high * 0.995) and (volume >= 1.2 * vol20) if pd.notna(vol20) else False
        reversal = (last_close <= recent_low * 1.08) and (rsi < 40) if pd.notna(rsi) else False
    except:
        pass

    company_name = info.get("longName") or info.get("shortName") or symbol
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    market_cap = safe_num(info.get("marketCap"))
    pe = safe_num(info.get("trailingPE"))
    pb = safe_num(info.get("priceToBook"))
    roe = safe_num(info.get("returnOnEquity"))
    if pd.notna(roe) and roe < 5:
        roe *= 100

    return {
        "df": df,
        "symbol": symbol,
        "company_name": company_name,
        "sector": sector,
        "industry": industry,
        "last_close": last_close,
        "change": change,
        "change_pct": change_pct,
        "market_cap": market_cap,
        "pe": pe,
        "pb": pb,
        "roe": roe,
        "fund_score": fund_score,
        "tech_score": tech_score,
        "balanced": balanced,
        "swing": swing,
        "long_term": long_term,
        "trend": trend,
        "support": support,
        "resistance": resistance,
        "stop_loss": stop_loss,
        "target1": target1,
        "target2": target2,
        "breakout": breakout,
        "reversal": reversal,
        "fund_metrics": fund_metrics,
        "tech_metrics": tech_metrics
    }

# =========================================================
# CHART
# =========================================================
def build_chart(df, symbol):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price"
    ))

    for col, name in [("SMA20", "20 DMA"), ("SMA50", "50 DMA"), ("SMA200", "200 DMA")]:
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], mode="lines", name=name))

    fig.update_layout(
        title=f"{symbol} Price Chart",
        template="plotly_dark",
        height=580,
        xaxis_rangeslider_visible=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.5)"
    )
    return fig

# =========================================================
# BULK SCAN
# =========================================================
def run_bulk_analysis(symbols, max_stocks=5):
    rows = []
    symbols = symbols[:max_stocks]

    progress = st.progress(0, text="Starting scan...")
    total = len(symbols)

    for idx, sym in enumerate(symbols, start=1):
        try:
            progress.progress(idx / total, text=f"Analyzing {sym} ({idx}/{total})")
            res = analyze_stock(sym, "1y")
            if "error" not in res:
                rows.append({
                    "Symbol": sym,
                    "Price": round(res["last_close"], 2) if pd.notna(res["last_close"]) else np.nan,
                    "Fund Score": res["fund_score"],
                    "Tech Score": res["tech_score"],
                    "Balanced Score": res["balanced"],
                    "Swing Score": res["swing"],
                    "Long Score": res["long_term"],
                    "Trend": res["trend"],
                    "Breakout": "YES" if res["breakout"] else "NO",
                    "Reversal": "YES" if res["reversal"] else "NO"
                })
        except:
            continue

    progress.empty()

    if rows:
        return pd.DataFrame(rows).sort_values("Balanced Score", ascending=False).reset_index(drop=True)
    return pd.DataFrame()

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="hero">
    <div class="hero-title">📈 NSE Stock Intelligence Pro MAX V9.1 LIGHT</div>
    <div class="hero-sub">Attractive • Simple • Premium UI • Streamlit Cloud Safe • Nifty 100 Master</div>
    <span class="pill">Nifty 50</span>
    <span class="pill">Nifty Next 50</span>
    <span class="pill">Nifty 100</span>
    <span class="pill">Watchlist</span>
    <span class="pill">Portfolio</span>
    <span class="pill">Cloud Safe</span>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## 🚀 Pro Navigation")

module = st.sidebar.radio(
    "Choose Module",
    [
        "Single Stock Analysis",
        "Nifty 50 Explorer",
        "Nifty Next 50 Explorer",
        "Nifty 100 Explorer",
        "Elite Watchlist",
        "Mini Screener",
        "Multi-Stock Compare",
        "Portfolio DB",
        "Trade Planner",
        "Wealth Planner",
        "About"
    ]
)

default_symbol = st.sidebar.selectbox("Quick Select", NIFTY_100, index=min(10, len(NIFTY_100)-1))
custom_symbol = st.sidebar.text_input("Or Enter NSE Symbol", value=default_symbol)

period_map = {"6 Months": "6mo", "1 Year": "1y", "2 Years": "2y", "5 Years": "5y"}
period_label = st.sidebar.selectbox("Price History", list(period_map.keys()), index=1)
period = period_map[period_label]

# =========================================================
# MODULES
# =========================================================
if module == "Single Stock Analysis":
    st.subheader("📊 Single Stock Analysis")

    symbol = custom_symbol.strip().upper().replace(".NS", "")

    if st.button("Analyze Stock"):
        with st.spinner(f"Analyzing {symbol}.NS ..."):
            result = analyze_stock(symbol, period)

        if "error" in result:
            st.error(result["error"])
        else:
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1:
                delta_txt = f"{fmt(result['change'])} ({fmt(result['change_pct'])}%)" if pd.notna(result["change"]) else "N/A"
                st.metric("Price", f"₹ {fmt(result['last_close'])}", delta_txt)
            with c2:
                st.metric("Fund Score", f"{result['fund_score']}/100")
            with c3:
                st.metric("Tech Score", f"{result['tech_score']}/100")
            with c4:
                st.metric("Balanced", f"{result['balanced']}/100")
            with c5:
                st.metric("Swing", f"{result['swing']}/100")
            with c6:
                st.metric("Long Term", f"{result['long_term']}/100")

            verdict, vtype = get_verdict(result["balanced"])
            if vtype == "good":
                st.markdown(f'<div class="good-box">{verdict}</div>', unsafe_allow_html=True)
            elif vtype == "warn":
                st.markdown(f'<div class="warn-box">{verdict}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bad-box">{verdict}</div>', unsafe_allow_html=True)

            st.markdown(
                f'<div class="info-box">Company: {result["company_name"]} | Sector: {result["sector"]} | Trend: {result["trend"]} | Breakout: {"YES" if result["breakout"] else "NO"} | Reversal: {"YES" if result["reversal"] else "NO"}</div>',
                unsafe_allow_html=True
            )

            tabs = st.tabs(["📈 Chart", "🏢 Fundamentals", "🧠 Score Breakdown", "⭐ Watchlist", "📂 Portfolio", "⬇️ Export"])

            with tabs[0]:
                st.plotly_chart(build_chart(result["df"], symbol), use_container_width=True)

                a, b, c, d, e = st.columns(5)
                with a: st.metric("Support", f"₹ {fmt(result['support'])}")
                with b: st.metric("Resistance", f"₹ {fmt(result['resistance'])}")
                with c: st.metric("Stop Loss", f"₹ {fmt(result['stop_loss'])}")
                with d: st.metric("Target 1", f"₹ {fmt(result['target1'])}")
                with e: st.metric("Target 2", f"₹ {fmt(result['target2'])}")

            with tabs[1]:
                fund_rows = [
                    ["Company", result["company_name"]],
                    ["Sector", result["sector"]],
                    ["Industry", result["industry"]],
                    ["Market Cap", f"₹ {result['market_cap']/1e7:,.2f} Cr" if pd.notna(result["market_cap"]) else "N/A"],
                    ["P/E", fmt(result["pe"])],
                    ["P/B", fmt(result["pb"])],
                    ["ROE %", fmt(result["roe"])]
                ]
                st.dataframe(pd.DataFrame(fund_rows, columns=["Metric", "Value"]), use_container_width=True, hide_index=True)

            with tabs[2]:
                st.markdown("### Fundamental Metrics Score")
                fdf = pd.DataFrame([[k, round(v, 1) if pd.notna(v) else "N/A"] for k, v in result["fund_metrics"].items()], columns=["Metric", "Score"])
                st.dataframe(fdf, use_container_width=True, hide_index=True)

                st.markdown("### Technical Metrics Score")
                tdf = pd.DataFrame([[k, round(v, 1) if pd.notna(v) else "N/A"] for k, v in result["tech_metrics"].items()], columns=["Metric", "Score"])
                st.dataframe(tdf, use_container_width=True, hide_index=True)

            with tabs[3]:
                note = st.text_input("Watchlist Note", value="High conviction / monitor")
                if st.button("Add to Elite Watchlist", key="add_watch_single"):
                    st.session_state.elite_watchlist.append({
                        "Symbol": symbol,
                        "Added At": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                        "Balanced Score": result["balanced"],
                        "Note": note
                    })
                    st.success(f"{symbol} added to watchlist.")

            with tabs[4]:
                qty = st.number_input("Qty", min_value=1, value=10, step=1, key="port_qty_single")
                avg = st.number_input("Avg Buy", min_value=0.0, value=float(result["last_close"]) if pd.notna(result["last_close"]) else 0.0, step=0.1, key="port_avg_single")
                if st.button("Add to Portfolio DB", key="add_port_single"):
                    st.session_state.portfolio_db.append({
                        "Symbol": symbol,
                        "Qty": qty,
                        "Avg Buy": avg,
                        "Added At": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    })
                    st.success(f"{symbol} added to portfolio.")

            with tabs[5]:
                csv = result["df"].reset_index().to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV", csv, f"{symbol}_analysis.csv", "text/csv")

elif module == "Nifty 50 Explorer":
    st.subheader("🇮🇳 Nifty 50 Explorer")
    selected = st.multiselect("Select Nifty 50 Stocks", NIFTY_50, default=["RELIANCE", "HDFCBANK", "ICICIBANK", "SBIN", "TCS"])
    max_stocks = st.slider("Max Scan", 3, 8, 5)

    if st.button("Run Nifty 50 Analysis"):
        with st.spinner("Running Nifty 50 analysis..."):
            out = run_bulk_analysis(selected if selected else NIFTY_50, max_stocks=max_stocks)
        if out.empty:
            st.warning("No data returned.")
        else:
            st.dataframe(out, use_container_width=True, hide_index=True)

elif module == "Nifty Next 50 Explorer":
    st.subheader("🚀 Nifty Next 50 Explorer")
    selected = st.multiselect("Select Nifty Next 50 Stocks", NIFTY_NEXT_50, default=["HAL", "DIVISLAB", "DMART", "SIEMENS", "VBL"])
    max_stocks = st.slider("Max Scan", 3, 8, 5, key="next50")

    if st.button("Run Nifty Next 50 Analysis"):
        with st.spinner("Running Nifty Next 50 analysis..."):
            out = run_bulk_analysis(selected if selected else NIFTY_NEXT_50, max_stocks=max_stocks)
        if out.empty:
            st.warning("No data returned.")
        else:
            st.dataframe(out, use_container_width=True, hide_index=True)

elif module == "Nifty 100 Explorer":
    st.subheader("🏛️ Nifty 100 Explorer")
    selected = st.multiselect("Select Nifty 100 Stocks", NIFTY_100, default=["RELIANCE", "HDFCBANK", "TCS", "HAL", "DIVISLAB"])
    max_stocks = st.slider("Max Scan", 3, 10, 6, key="n100")

    if st.button("Run Nifty 100 Analysis"):
        with st.spinner("Running Nifty 100 analysis..."):
            out = run_bulk_analysis(selected if selected else NIFTY_100, max_stocks=max_stocks)
        if out.empty:
            st.warning("No data returned.")
        else:
            st.dataframe(out, use_container_width=True, hide_index=True)

elif module == "Elite Watchlist":
    st.subheader("⭐ Elite Watchlist")

    c1, c2 = st.columns([2, 1])
    with c1:
        wl_symbol = st.selectbox("Select Symbol", NIFTY_100)
    with c2:
        st.write("")
        st.write("")
        if st.button("Add Manually"):
            st.session_state.elite_watchlist.append({
                "Symbol": wl_symbol,
                "Added At": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "Balanced Score": np.nan,
                "Note": "Manual add"
            })
            st.success(f"{wl_symbol} added.")

    if st.session_state.elite_watchlist:
        wl_df = pd.DataFrame(st.session_state.elite_watchlist)
        st.dataframe(wl_df, use_container_width=True, hide_index=True)

        if st.button("Analyze Watchlist + Auto Score"):
            rows = []
            symbols = list(dict.fromkeys([x["Symbol"] for x in st.session_state.elite_watchlist]))[:8]

            with st.spinner("Analyzing watchlist..."):
                for sym in symbols:
                    try:
                        res = analyze_stock(sym, "1y")
                        if "error" not in res:
                            rows.append({
                                "Symbol": sym,
                                "Price": round(res["last_close"], 2) if pd.notna(res["last_close"]) else np.nan,
                                "Fund Score": res["fund_score"],
                                "Tech Score": res["tech_score"],
                                "Balanced Score": res["balanced"],
                                "Swing Score": res["swing"],
                                "Long Score": res["long_term"],
                                "Trend": res["trend"],
                                "Breakout": "YES" if res["breakout"] else "NO",
                                "Reversal": "YES" if res["reversal"] else "NO"
                            })
                    except:
                        continue

            if rows:
                out = pd.DataFrame(rows).sort_values("Balanced Score", ascending=False).reset_index(drop=True)
                st.dataframe(out, use_container_width=True, hide_index=True)

                csv = out.to_csv(index=False).encode("utf-8")
                st.download_button("Download Watchlist CSV", csv, "watchlist_analysis.csv", "text/csv")
            else:
                st.warning("No valid watchlist data.")

        if st.button("Clear Watchlist"):
            st.session_state.elite_watchlist = []
            st.success("Watchlist cleared.")
    else:
        st.info("No watchlist stocks yet.")

elif module == "Mini Screener":
    st.subheader("🔎 Mini Screener")
    universe = st.selectbox("Choose Universe", ["Nifty 50", "Nifty Next 50", "Nifty 100"])
    max_stocks = st.slider("Max Stocks", 3, 10, 5, key="mini")

    if st.button("Run Screener"):
        symbols = NIFTY_50 if universe == "Nifty 50" else NIFTY_NEXT_50 if universe == "Nifty Next 50" else NIFTY_100
        with st.spinner("Running screener..."):
            out = run_bulk_analysis(symbols, max_stocks=max_stocks)

        if out.empty:
            st.warning("No data.")
        else:
            st.dataframe(out, use_container_width=True, hide_index=True)

elif module == "Multi-Stock Compare":
    st.subheader("📊 Multi-Stock Compare")
    compare_input = st.text_area("Enter comma-separated NSE symbols", value="RELIANCE,HDFCBANK,ICICIBANK,SBIN,TCS")
    max_stocks = st.slider("Max Compare Stocks", 2, 8, 5)

    if st.button("Run Compare"):
        symbols = [x.strip().upper().replace(".NS", "") for x in compare_input.split(",") if x.strip()]
        symbols = list(dict.fromkeys(symbols))[:max_stocks]

        with st.spinner("Running compare..."):
            out = run_bulk_analysis(symbols, max_stocks=max_stocks)

        if out.empty:
            st.warning("No data.")
        else:
            st.dataframe(out, use_container_width=True, hide_index=True)

elif module == "Portfolio DB":
    st.subheader("📂 Portfolio DB")

    c1, c2, c3 = st.columns(3)
    with c1:
        p_symbol = st.selectbox("Symbol", NIFTY_100, key="pdb_symbol")
    with c2:
        p_qty = st.number_input("Qty", min_value=1, value=10, step=1, key="pdb_qty")
    with c3:
        p_avg = st.number_input("Avg Buy", min_value=0.0, value=100.0, step=0.1, key="pdb_avg")

    if st.button("Add to Portfolio"):
        st.session_state.portfolio_db.append({
            "Symbol": p_symbol,
            "Qty": p_qty,
            "Avg Buy": p_avg,
            "Added At": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })
        st.success(f"{p_symbol} added.")

    if st.session_state.portfolio_db:
        db_df = pd.DataFrame(st.session_state.portfolio_db)
        st.dataframe(db_df, use_container_width=True, hide_index=True)

        if st.button("Analyze Portfolio"):
            rows = []
            with st.spinner("Analyzing portfolio..."):
                for row in st.session_state.portfolio_db[:8]:
                    sym = row["Symbol"]
                    qty = row["Qty"]
                    avg_buy = row["Avg Buy"]

                    try:
                        res = analyze_stock(sym, "1y")
                        if "error" not in res:
                            ltp = res["last_close"]
                            invested = qty * avg_buy
                            current_value = qty * ltp if pd.notna(ltp) else np.nan
                            pnl = current_value - invested if pd.notna(current_value) else np.nan
                            pnl_pct = (pnl / invested * 100) if pd.notna(pnl) and invested != 0 else np.nan

                            rows.append({
                                "Symbol": sym,
                                "Qty": qty,
                                "Avg Buy": avg_buy,
                                "LTP": round(ltp, 2) if pd.notna(ltp) else np.nan,
                                "Invested": round(invested, 2),
                                "Current Value": round(current_value, 2) if pd.notna(current_value) else np.nan,
                                "P&L": round(pnl, 2) if pd.notna(pnl) else np.nan,
                                "P&L %": round(pnl_pct, 2) if pd.notna(pnl_pct) else np.nan,
                                "Balanced Score": res["balanced"]
                            })
                    except:
                        continue

            if rows:
                out = pd.DataFrame(rows).sort_values("Balanced Score", ascending=False).reset_index(drop=True)
                st.dataframe(out, use_container_width=True, hide_index=True)

        if st.button("Clear Portfolio"):
            st.session_state.portfolio_db = []
            st.success("Portfolio cleared.")
    else:
        st.info("No stocks added yet.")

elif module == "Trade Planner":
    st.subheader("🎯 Trade Planner")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        entry = st.number_input("Entry", min_value=0.0, value=100.0, step=0.1)
    with c2:
        stop = st.number_input("Stop Loss", min_value=0.0, value=95.0, step=0.1)
    with c3:
        target = st.number_input("Target", min_value=0.0, value=110.0, step=0.1)
    with c4:
        capital = st.number_input("Capital", min_value=1000.0, value=100000.0, step=1000.0)

    risk = entry - stop
    reward = target - entry
    rr = reward / risk if risk > 0 else np.nan
    qty = math.floor(capital / entry) if entry > 0 else 0

    t1, t2, t3, t4 = st.columns(4)
    with t1: st.metric("Risk/Share", fmt(risk))
    with t2: st.metric("Reward/Share", fmt(reward))
    with t3: st.metric("R:R", fmt(rr))
    with t4: st.metric("Max Qty", f"{qty}")

elif module == "Wealth Planner":
    st.subheader("💰 Wealth Planner")

    tab1, tab2 = st.tabs(["📅 SIP Planner", "💵 Lumpsum Planner"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        with c1:
            monthly = st.number_input("Monthly SIP (₹)", min_value=500, value=10000, step=500)
        with c2:
            ret = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5)
        with c3:
            years = st.number_input("Years", min_value=1, value=10, step=1)

        r = ret / 12 / 100
        n = years * 12
        fv = monthly * (((1 + r) ** n - 1) / r) * (1 + r) if r != 0 else monthly * n
        invested = monthly * 12 * years

        s1, s2, s3 = st.columns(3)
        with s1: st.metric("Invested", f"₹ {fmt(invested)}")
        with s2: st.metric("Future Value", f"₹ {fmt(fv)}")
        with s3: st.metric("Gain", f"₹ {fmt(fv - invested)}")

    with tab2:
        c1, c2, c3 = st.columns(3)
        with c1:
            amount = st.number_input("Lumpsum (₹)", min_value=1000, value=100000, step=1000)
        with c2:
            ret2 = st.number_input("Expected Return (%)", min_value=0.0, value=12.0, step=0.5, key="lump_ret")
        with c3:
            years2 = st.number_input("Years", min_value=1, value=10, step=1, key="lump_yrs")

        fv2 = amount * ((1 + ret2 / 100) ** years2)

        l1, l2, l3 = st.columns(3)
        with l1: st.metric("Invested", f"₹ {fmt(amount)}")
        with l2: st.metric("Future Value", f"₹ {fmt(fv2)}")
        with l3: st.metric("Gain", f"₹ {fmt(fv2 - amount)}")

else:
    st.subheader("ℹ️ About This Version")
    st.markdown("""
<div class="soft-card">
<h4 style="margin-top:0;">FINAL V9.1 LIGHT CLOUD SAFE</h4>
<ul>
<li>Lightweight and more stable for Streamlit Cloud</li>
<li>Premium modern UI</li>
<li>Better font and attractive dark background</li>
<li>Simple and clean layout</li>
<li>Nifty 50 + Nifty Next 50 + Nifty 100</li>
<li>Watchlist + Portfolio + Screener + Compare</li>
</ul>
<p><b>Best for:</b> Fast deployment, stable running, clean premium appearance.</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption(
    f"NSE Stock Intelligence Pro MAX V9.1 LIGHT • Attractive UI • Streamlit Cloud Safe • {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)

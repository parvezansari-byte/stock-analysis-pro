import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="NSE Stock Analysis Pro V2 ELITE",
    page_icon="📈",
    layout="wide"
)

# =========================================================
# STYLING
# =========================================================
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #6b7280;
        margin-bottom: 1rem;
    }
    .metric-card {
        padding: 14px;
        border-radius: 16px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
    }
    .score-box {
        padding: 18px;
        border-radius: 16px;
        text-align: center;
        font-weight: 700;
        font-size: 1.1rem;
        border: 1px solid rgba(255,255,255,0.08);
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# DEFAULT NSE STOCKS
# =========================================================
DEFAULT_NSE_STOCKS = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "SBIN", "LT", "ITC", "HINDUNILVR", "BHARTIARTL",
    "KOTAKBANK", "AXISBANK", "ASIANPAINT", "MARUTI", "SUNPHARMA"
]

# =========================================================
# HELPERS
# =========================================================
def to_ns_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if symbol.endswith(".NS"):
        return symbol
    return f"{symbol}.NS"

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
    hist = hist.copy()
    return hist, info

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
# SCORING
# =========================================================
def calculate_fundamental_score(info):
    score = 0
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

    # PE
    if pd.notna(pe):
        if 0 < pe < 25:
            score += 10
            breakdown.append(("P/E Attractive", 10))
        elif pe < 40:
            score += 5
            breakdown.append(("P/E Moderate", 5))
        else:
            breakdown.append(("P/E Expensive", 0))
    else:
        breakdown.append(("P/E Unavailable", 0))

    # PB
    if pd.notna(pb):
        if 0 < pb < 4:
            score += 10
            breakdown.append(("P/B Healthy", 10))
        elif pb < 8:
            score += 5
            breakdown.append(("P/B Moderate", 5))
        else:
            breakdown.append(("P/B High", 0))
    else:
        breakdown.append(("P/B Unavailable", 0))

    # ROE
    if pd.notna(roe):
        roe_pct = roe * 100 if abs(roe) <= 2 else roe
        if roe_pct > 15:
            score += 15
            breakdown.append(("ROE Strong", 15))
        elif roe_pct > 8:
            score += 8
            breakdown.append(("ROE Decent", 8))
        else:
            breakdown.append(("ROE Weak", 0))
    else:
        breakdown.append(("ROE Unavailable", 0))

    # Debt to Equity
    if pd.notna(de):
        if de < 80:
            score += 15
            breakdown.append(("Debt Low", 15))
        elif de < 150:
            score += 8
            breakdown.append(("Debt Moderate", 8))
        else:
            breakdown.append(("Debt High", 0))
    else:
        breakdown.append(("Debt/Equity Unavailable", 0))

    # Profit Margin
    if pd.notna(pm):
        pm_pct = pm * 100 if abs(pm) <= 2 else pm
        if pm_pct > 10:
            score += 10
            breakdown.append(("Profit Margin Strong", 10))
        elif pm_pct > 5:
            score += 5
            breakdown.append(("Profit Margin Moderate", 5))
        else:
            breakdown.append(("Profit Margin Weak", 0))
    else:
        breakdown.append(("Profit Margin Unavailable", 0))

    # Operating Margin
    if pd.notna(om):
        om_pct = om * 100 if abs(om) <= 2 else om
        if om_pct > 15:
            score += 10
            breakdown.append(("Operating Margin Strong", 10))
        elif om_pct > 8:
            score += 5
            breakdown.append(("Operating Margin Moderate", 5))
        else:
            breakdown.append(("Operating Margin Weak", 0))
    else:
        breakdown.append(("Operating Margin Unavailable", 0))

    # Revenue Growth
    if pd.notna(rev_growth):
        rg_pct = rev_growth * 100 if abs(rev_growth) <= 2 else rev_growth
        if rg_pct > 10:
            score += 10
            breakdown.append(("Revenue Growth Strong", 10))
        elif rg_pct > 5:
            score += 5
            breakdown.append(("Revenue Growth Moderate", 5))
        else:
            breakdown.append(("Revenue Growth Weak", 0))
    else:
        breakdown.append(("Revenue Growth Unavailable", 0))

    # Earnings Growth
    if pd.notna(earn_growth):
        eg_pct = earn_growth * 100 if abs(earn_growth) <= 2 else earn_growth
        if eg_pct > 10:
            score += 10
            breakdown.append(("Earnings Growth Strong", 10))
        elif eg_pct > 5:
            score += 5
            breakdown.append(("Earnings Growth Moderate", 5))
        else:
            breakdown.append(("Earnings Growth Weak", 0))
    else:
        breakdown.append(("Earnings Growth Unavailable", 0))

    # Dividend Yield
    if pd.notna(dy):
        dy_pct = dy * 100 if abs(dy) <= 2 else dy
        if dy_pct > 1:
            score += 10
            breakdown.append(("Dividend Yield Positive", 10))
        elif dy_pct > 0:
            score += 5
            breakdown.append(("Dividend Yield Low", 5))
        else:
            breakdown.append(("No Dividend", 0))
    else:
        breakdown.append(("Dividend Yield Unavailable", 0))

    return min(score, 100), breakdown

def calculate_technical_score(df):
    if df.empty or len(df) < 60:
        return 0, [("Not enough price history", 0)]

    latest = df.iloc[-1]
    score = 0
    breakdown = []

    # Price above 200 DMA
    if pd.notna(latest["SMA200"]):
        if latest["Close"] > latest["SMA200"]:
            score += 20
            breakdown.append(("Price above 200 DMA", 20))
        else:
            breakdown.append(("Price below 200 DMA", 0))
    else:
        breakdown.append(("200 DMA unavailable", 0))

    # 50 > 200
    if pd.notna(latest["SMA50"]) and pd.notna(latest["SMA200"]):
        if latest["SMA50"] > latest["SMA200"]:
            score += 15
            breakdown.append(("50 DMA above 200 DMA", 15))
        else:
            breakdown.append(("50 DMA below 200 DMA", 0))
    else:
        breakdown.append(("DMA structure unavailable", 0))

    # EMA alignment
    if pd.notna(latest["EMA20"]) and pd.notna(latest["EMA50"]):
        if latest["EMA20"] > latest["EMA50"]:
            score += 10
            breakdown.append(("EMA20 above EMA50", 10))
        else:
            breakdown.append(("EMA20 below EMA50", 0))
    else:
        breakdown.append(("EMA alignment unavailable", 0))

    # RSI
    rsi = latest["RSI14"]
    if pd.notna(rsi):
        if 55 <= rsi <= 70:
            score += 15
            breakdown.append(("RSI healthy bullish zone", 15))
        elif 45 <= rsi < 55:
            score += 8
            breakdown.append(("RSI neutral-positive", 8))
        elif 70 < rsi <= 80:
            score += 5
            breakdown.append(("RSI strong but extended", 5))
        else:
            breakdown.append(("RSI weak/overstretched", 0))
    else:
        breakdown.append(("RSI unavailable", 0))

    # MACD
    if pd.notna(latest["MACD"]) and pd.notna(latest["MACD_SIGNAL"]):
        if latest["MACD"] > latest["MACD_SIGNAL"]:
            score += 10
            breakdown.append(("MACD bullish", 10))
        else:
            breakdown.append(("MACD bearish", 0))
    else:
        breakdown.append(("MACD unavailable", 0))

    # Volume
    if pd.notna(latest["VOL20"]) and latest["VOL20"] > 0:
        if latest["Volume"] > 1.5 * latest["VOL20"]:
            score += 15
            breakdown.append(("Strong volume breakout", 15))
        elif latest["Volume"] > latest["VOL20"]:
            score += 8
            breakdown.append(("Above-average volume", 8))
        else:
            breakdown.append(("Volume not confirming", 0))
    else:
        breakdown.append(("Volume average unavailable", 0))

    # 52W High proximity
    if pd.notna(latest["52W_HIGH"]) and latest["52W_HIGH"] > 0:
        dist = ((latest["52W_HIGH"] - latest["Close"]) / latest["52W_HIGH"]) * 100
        if dist < 10:
            score += 10
            breakdown.append(("Near 52W high", 10))
        elif dist < 20:
            score += 5
            breakdown.append(("Within 20% of 52W high", 5))
        else:
            breakdown.append(("Far from 52W high", 0))
    else:
        breakdown.append(("52W high unavailable", 0))

    # ATR risk
    if pd.notna(latest["ATR14"]) and latest["Close"] > 0:
        atr_pct = (latest["ATR14"] / latest["Close"]) * 100
        if atr_pct < 4:
            score += 5
            breakdown.append(("Volatility controlled", 5))
        else:
            breakdown.append(("Volatility elevated", 0))
    else:
        breakdown.append(("ATR unavailable", 0))

    return min(score, 100), breakdown

def get_verdict(combined_score):
    if combined_score >= 80:
        return "🔥 STRONG BUY / HIGH QUALITY"
    elif combined_score >= 65:
        return "✅ BUY / WATCHLIST PRIORITY"
    elif combined_score >= 50:
        return "👀 WATCHLIST / NEUTRAL"
    else:
        return "⚠️ AVOID / WEAK SETUP"

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

# =========================================================
# CHART
# =========================================================
def create_chart(df, symbol):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.6, 0.2, 0.2]
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price"
        ),
        row=1, col=1
    )

    # Moving averages + Bollinger
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], mode="lines", name="SMA20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], mode="lines", name="SMA50"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA200"], mode="lines", name="SMA200"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_UPPER"], mode="lines", name="BB Upper"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_LOWER"], mode="lines", name="BB Lower"), row=1, col=1)

    # Volume
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume"), row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI14"], mode="lines", name="RSI14"), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", row=3, col=1)

    fig.update_layout(
        title=f"{symbol} - Price + Technical Analysis",
        xaxis_rangeslider_visible=False,
        height=850,
        legend=dict(orientation="h")
    )

    return fig

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("📊 NSE Stock Analysis Pro")
page = st.sidebar.radio(
    "Choose Module",
    ["Single Stock Analysis", "Mini Screener", "About"]
)

st.sidebar.markdown("---")
selected_symbol = st.sidebar.selectbox("Quick NSE Pick", DEFAULT_NSE_STOCKS, index=0)
manual_symbol = st.sidebar.text_input("Or Enter NSE Symbol", value=selected_symbol).upper().strip()
period = st.sidebar.selectbox("Price History", ["6mo", "1y", "2y", "5y"], index=1)

symbol = manual_symbol if manual_symbol else selected_symbol

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="main-title">📈 NSE Stock Analysis Pro V2 ELITE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Fundamental + Technical + Scoring + Verdict (Streamlit Cloud Safe)</div>', unsafe_allow_html=True)

# =========================================================
# SINGLE STOCK ANALYSIS
# =========================================================
if page == "Single Stock Analysis":
    hist, info = fetch_stock_data(symbol, period)

    if hist.empty:
        st.error("No data found. Please check the NSE symbol (example: RELIANCE, TCS, INFY).")
    else:
        df = add_indicators(hist)

        latest = df.iloc[-1]
        prev_close = df["Close"].iloc[-2] if len(df) > 1 else latest["Close"]
        price_change = latest["Close"] - prev_close
        price_change_pct = (price_change / prev_close * 100) if prev_close != 0 else 0

        fundamental_score, f_breakdown = calculate_fundamental_score(info)
        technical_score, t_breakdown = calculate_technical_score(df)
        combined_score = round((0.6 * fundamental_score) + (0.4 * technical_score), 2)
        verdict = get_verdict(combined_score)
        trend = get_trend_label(df)

        # Top metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Price", f"₹ {latest['Close']:.2f}", f"{price_change:+.2f} ({price_change_pct:+.2f}%)")
        c2.metric("Fundamental Score", f"{fundamental_score}/100")
        c3.metric("Technical Score", f"{technical_score}/100")
        c4.metric("Combined Score", f"{combined_score}/100")

        st.success(f"Verdict: {verdict}")
        st.info(f"Trend: **{trend}**")

        # Chart
        st.plotly_chart(create_chart(df.tail(250), symbol), use_container_width=True)

        # Fundamental + Technical snapshots
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

        # Score breakdowns
        st.markdown("## 🏅 Score Breakdown")
        c5, c6 = st.columns(2)

        with c5:
            st.markdown("### Fundamental Score Breakdown")
            f_df = pd.DataFrame(f_breakdown, columns=["Factor", "Points"])
            st.dataframe(f_df, use_container_width=True, hide_index=True)

        with c6:
            st.markdown("### Technical Score Breakdown")
            t_df = pd.DataFrame(t_breakdown, columns=["Factor", "Points"])
            st.dataframe(t_df, use_container_width=True, hide_index=True)

        # Recent data
        st.markdown("## 📋 Recent Price Data")
        recent = df.tail(10).copy()
        recent_display = recent[["Open", "High", "Low", "Close", "Volume"]].round(2)
        st.dataframe(recent_display, use_container_width=True)

# =========================================================
# MINI SCREENER
# =========================================================
elif page == "Mini Screener":
    st.markdown("## 🧮 Mini NSE Screener (Top 15 Default Stocks)")
    st.caption("This scans a small basket for stability on Streamlit Cloud. Keep it lightweight.")

    if st.button("Run Screener"):
        results = []

        progress = st.progress(0)
        status = st.empty()

        for i, sym in enumerate(DEFAULT_NSE_STOCKS):
            status.write(f"Scanning {sym}...")
            hist, info = fetch_stock_data(sym, "1y")

            if not hist.empty:
                try:
                    df = add_indicators(hist)
                    latest = df.iloc[-1]

                    f_score, _ = calculate_fundamental_score(info)
                    t_score, _ = calculate_technical_score(df)
                    combined = round((0.6 * f_score) + (0.4 * t_score), 2)

                    results.append({
                        "Symbol": sym,
                        "Close": round(latest["Close"], 2),
                        "RSI": round(latest["RSI14"], 2) if pd.notna(latest["RSI14"]) else np.nan,
                        "Trend": get_trend_label(df),
                        "Fundamental Score": f_score,
                        "Technical Score": t_score,
                        "Combined Score": combined,
                        "Verdict": get_verdict(combined)
                    })
                except Exception:
                    pass

            progress.progress((i + 1) / len(DEFAULT_NSE_STOCKS))

        status.empty()

        if results:
            screener_df = pd.DataFrame(results).sort_values("Combined Score", ascending=False).reset_index(drop=True)
            st.dataframe(screener_df, use_container_width=True, hide_index=True)

            csv = screener_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download Screener CSV",
                data=csv,
                file_name="nse_mini_screener.csv",
                mime="text/csv"
            )
        else:
            st.warning("No screener results found. Try again later.")

# =========================================================
# ABOUT
# =========================================================
else:
    st.markdown("## ℹ️ About This App")
    st.markdown("""
### NSE Stock Analysis Pro V2 ELITE

This app provides:

- **NSE Stock Analysis** using `.NS`
- **Fundamental Score /100**
- **Technical Score /100**
- **Combined Score /100**
- **Trend classification**
- **Verdict: Buy / Watch / Avoid**
- **Mini Screener for default NSE basket**

### Notes
- Built for **education and research**
- Data source: **Yahoo Finance via yfinance**
- Always validate before investing
- Some fundamental fields may be missing for certain stocks

### Good NSE examples:
- RELIANCE
- TCS
- INFY
- HDFCBANK
- ICICIBANK
- SBIN
- LT
- ITC
""")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption("Built with Streamlit + yfinance | NSE (.NS) | FINAL V2 ELITE | For research & education only")

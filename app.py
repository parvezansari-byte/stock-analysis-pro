import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

st.set_page_config(
    page_title="NSE STOCK INTELLIGENCE PRO",
    page_icon="📈",
    layout="wide"
)

# =========================
# DEFAULT NSE STOCK LIST
# =========================
DEFAULT_NSE_STOCKS = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "LT",
    "ITC", "HINDUNILVR", "BHARTIARTL", "KOTAKBANK", "ASIANPAINT",
    "AXISBANK", "MARUTI", "SUNPHARMA", "TITAN", "ULTRACEMCO", "BAJFINANCE",
    "NESTLEIND", "WIPRO", "HCLTECH", "NTPC", "POWERGRID", "ONGC", "TATAMOTORS"
]

# =========================
# HELPERS
# =========================
def to_ns_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if symbol.endswith(".NS"):
        return symbol
    return f"{symbol}.NS"

@st.cache_data(ttl=3600)
def get_stock_data(symbol, period="2y", interval="1d"):
    ticker = yf.Ticker(to_ns_symbol(symbol))
    df = ticker.history(period=period, interval=interval, auto_adjust=False)
    if df.empty:
        return pd.DataFrame()
    df = df.reset_index()
    return df

@st.cache_data(ttl=3600)
def get_stock_info(symbol):
    try:
        ticker = yf.Ticker(to_ns_symbol(symbol))
        info = ticker.info
        return info
    except Exception:
        return {}

def safe_get(info, key, default=np.nan):
    try:
        return info.get(key, default)
    except Exception:
        return default

# =========================
# TECHNICAL INDICATORS
# =========================
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - macd_signal
    return macd, macd_signal, hist

def compute_bollinger(series, window=20, num_std=2):
    sma = series.rolling(window).mean()
    std = series.rolling(window).std()
    upper = sma + num_std * std
    lower = sma - num_std * std
    return sma, upper, lower

def compute_atr(df, period=14):
    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    return atr

def add_technical_indicators(df):
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
    df["52W_HIGH"] = df["High"].rolling(252).max()
    df["52W_LOW"] = df["Low"].rolling(252).min()

    return df

# =========================
# SCORING
# =========================
def fundamental_score(info):
    score = 0
    details = {}

    roe = safe_get(info, "returnOnEquity", np.nan)
    if pd.notna(roe):
        roe_pct = roe * 100 if roe < 5 else roe
        points = 10 if roe_pct > 15 else 5 if roe_pct > 8 else 0
        score += points
        details["ROE"] = points
    else:
        details["ROE"] = 0

    pe = safe_get(info, "trailingPE", np.nan)
    if pd.notna(pe):
        points = 10 if 0 < pe < 25 else 5 if pe < 40 else 0
        score += points
        details["PE"] = points
    else:
        details["PE"] = 0

    pb = safe_get(info, "priceToBook", np.nan)
    if pd.notna(pb):
        points = 10 if 0 < pb < 4 else 5 if pb < 8 else 0
        score += points
        details["PB"] = points
    else:
        details["PB"] = 0

    debt_to_equity = safe_get(info, "debtToEquity", np.nan)
    if pd.notna(debt_to_equity):
        points = 10 if debt_to_equity < 80 else 5 if debt_to_equity < 150 else 0
        score += points
        details["DebtToEquity"] = points
    else:
        details["DebtToEquity"] = 0

    profit_margin = safe_get(info, "profitMargins", np.nan)
    if pd.notna(profit_margin):
        pm_pct = profit_margin * 100 if profit_margin < 5 else profit_margin
        points = 10 if pm_pct > 10 else 5 if pm_pct > 5 else 0
        score += points
        details["ProfitMargin"] = points
    else:
        details["ProfitMargin"] = 0

    operating_margin = safe_get(info, "operatingMargins", np.nan)
    if pd.notna(operating_margin):
        om_pct = operating_margin * 100 if operating_margin < 5 else operating_margin
        points = 10 if om_pct > 15 else 5 if om_pct > 8 else 0
        score += points
        details["OperatingMargin"] = points
    else:
        details["OperatingMargin"] = 0

    revenue_growth = safe_get(info, "revenueGrowth", np.nan)
    if pd.notna(revenue_growth):
        rg_pct = revenue_growth * 100 if revenue_growth < 5 else revenue_growth
        points = 10 if rg_pct > 10 else 5 if rg_pct > 5 else 0
        score += points
        details["RevenueGrowth"] = points
    else:
        details["RevenueGrowth"] = 0

    earnings_growth = safe_get(info, "earningsGrowth", np.nan)
    if pd.notna(earnings_growth):
        eg_pct = earnings_growth * 100 if earnings_growth < 5 else earnings_growth
        points = 10 if eg_pct > 10 else 5 if eg_pct > 5 else 0
        score += points
        details["EarningsGrowth"] = points
    else:
        details["EarningsGrowth"] = 0

    current_ratio = safe_get(info, "currentRatio", np.nan)
    if pd.notna(current_ratio):
        points = 10 if current_ratio > 1.5 else 5 if current_ratio > 1 else 0
        score += points
        details["CurrentRatio"] = points
    else:
        details["CurrentRatio"] = 0

    dividend_yield = safe_get(info, "dividendYield", np.nan)
    if pd.notna(dividend_yield):
        dy_pct = dividend_yield * 100 if dividend_yield < 5 else dividend_yield
        points = 10 if dy_pct > 1 else 5 if dy_pct > 0 else 0
        score += points
        details["DividendYield"] = points
    else:
        details["DividendYield"] = 0

    return min(score, 100), details

def technical_score(df):
    if df.empty or len(df) < 220:
        return 0, {}

    latest = df.iloc[-1]
    score = 0
    details = {}

    # Trend
    if latest["Close"] > latest["SMA200"]:
        score += 15
        details["Above200DMA"] = 15
    else:
        details["Above200DMA"] = 0

    if latest["SMA50"] > latest["SMA200"]:
        score += 15
        details["GoldenStructure"] = 15
    else:
        details["GoldenStructure"] = 0

    # Momentum
    rsi = latest["RSI14"]
    if 55 <= rsi <= 70:
        score += 10
        details["RSI"] = 10
    elif 45 <= rsi < 55:
        score += 5
        details["RSI"] = 5
    else:
        details["RSI"] = 0

    if latest["MACD"] > latest["MACD_SIGNAL"]:
        score += 10
        details["MACD"] = 10
    else:
        details["MACD"] = 0

    # Volume
    if latest["Volume"] > 1.5 * latest["VOL20"]:
        score += 15
        details["VolumeBreakout"] = 15
    elif latest["Volume"] > latest["VOL20"]:
        score += 8
        details["VolumeBreakout"] = 8
    else:
        details["VolumeBreakout"] = 0

    # 52W High Proximity
    if latest["52W_HIGH"] > 0:
        dist = ((latest["52W_HIGH"] - latest["Close"]) / latest["52W_HIGH"]) * 100
        if dist < 10:
            score += 10
            details["Near52WHigh"] = 10
        elif dist < 20:
            score += 5
            details["Near52WHigh"] = 5
        else:
            details["Near52WHigh"] = 0
    else:
        details["Near52WHigh"] = 0

    # Bollinger
    if latest["Close"] > latest["BB_MID"]:
        score += 10
        details["BBPosition"] = 10
    else:
        details["BBPosition"] = 0

    # EMA structure
    if latest["EMA20"] > latest["EMA50"]:
        score += 10
        details["EMAAlignment"] = 10
    else:
        details["EMAAlignment"] = 0

    # Risk / ATR
    atr_pct = (latest["ATR14"] / latest["Close"]) * 100 if latest["Close"] > 0 else np.nan
    if pd.notna(atr_pct):
        if atr_pct < 4:
            score += 5
            details["ATRRisk"] = 5
        else:
            details["ATRRisk"] = 2
            score += 2
    else:
        details["ATRRisk"] = 0

    return min(score, 100), details

def get_verdict(f_score, t_score, combined):
    if combined >= 80:
        return "🔥 STRONG BUY / HIGH QUALITY"
    elif combined >= 65:
        return "✅ BUY / WATCHLIST PRIORITY"
    elif combined >= 50:
        return "👀 WATCHLIST / NEUTRAL"
    else:
        return "⚠️ AVOID / WEAK SETUP"

# =========================
# CHARTS
# =========================
def make_candlestick_chart(df, symbol):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2]
    )

    fig.add_trace(
        go.Candlestick(
            x=df["Date"],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price"
        ),
        row=1, col=1
    )

    fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA20"], mode="lines", name="SMA20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA50"], mode="lines", name="SMA50"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA200"], mode="lines", name="SMA200"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_UPPER"], mode="lines", name="BB Upper"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_LOWER"], mode="lines", name="BB Lower"), row=1, col=1)

    fig.add_trace(go.Bar(x=df["Date"], y=df["Volume"], name="Volume"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI14"], mode="lines", name="RSI14"), row=3, col=1)

    fig.update_layout(
        title=f"{symbol} - Candlestick + Technicals",
        xaxis_rangeslider_visible=False,
        height=850
    )
    return fig

# =========================
# DATA TABLES
# =========================
def build_fundamental_table(info):
    rows = [
        ("Market Cap", safe_get(info, "marketCap")),
        ("Current Price", safe_get(info, "currentPrice")),
        ("52W High", safe_get(info, "fiftyTwoWeekHigh")),
        ("52W Low", safe_get(info, "fiftyTwoWeekLow")),
        ("P/E", safe_get(info, "trailingPE")),
        ("Forward P/E", safe_get(info, "forwardPE")),
        ("P/B", safe_get(info, "priceToBook")),
        ("ROE", safe_get(info, "returnOnEquity")),
        ("Debt to Equity", safe_get(info, "debtToEquity")),
        ("Current Ratio", safe_get(info, "currentRatio")),
        ("Profit Margin", safe_get(info, "profitMargins")),
        ("Operating Margin", safe_get(info, "operatingMargins")),
        ("Revenue Growth", safe_get(info, "revenueGrowth")),
        ("Earnings Growth", safe_get(info, "earningsGrowth")),
        ("Dividend Yield", safe_get(info, "dividendYield")),
        ("Beta", safe_get(info, "beta")),
        ("Sector", safe_get(info, "sector")),
        ("Industry", safe_get(info, "industry")),
    ]
    return pd.DataFrame(rows, columns=["Metric", "Value"])

def format_value(metric, value):
    if pd.isna(value):
        return "N/A"

    percent_metrics = {"ROE", "Profit Margin", "Operating Margin", "Revenue Growth", "Earnings Growth", "Dividend Yield"}
    if metric in percent_metrics and isinstance(value, (int, float)):
        if value < 5:
            return f"{value*100:.2f}%"
        return f"{value:.2f}%"

    if metric == "Market Cap" and isinstance(value, (int, float)):
        return f"₹ {value:,.0f}"

    if isinstance(value, (int, float)):
        return f"{value:,.2f}"

    return str(value)

# =========================
# SCREENER
# =========================
@st.cache_data(ttl=3600)
def run_screener(symbols):
    results = []

    for symbol in symbols:
        try:
            df = get_stock_data(symbol, period="2y")
            if df.empty or len(df) < 220:
                continue

            df = add_technical_indicators(df)
            info = get_stock_info(symbol)

            f_score, _ = fundamental_score(info)
            t_score, _ = technical_score(df)
            combined = round(0.6 * f_score + 0.4 * t_score, 2)

            latest = df.iloc[-1]
            results.append({
                "Symbol": symbol,
                "Close": round(latest["Close"], 2),
                "RSI": round(latest["RSI14"], 2) if pd.notna(latest["RSI14"]) else np.nan,
                "Above_200DMA": latest["Close"] > latest["SMA200"],
                "Volume_Breakout": latest["Volume"] > latest["VOL20"],
                "Fundamental_Score": f_score,
                "Technical_Score": t_score,
                "Combined_Score": combined,
                "Verdict": get_verdict(f_score, t_score, combined)
            })
        except Exception:
            continue

    if not results:
        return pd.DataFrame()

    out = pd.DataFrame(results).sort_values("Combined_Score", ascending=False).reset_index(drop=True)
    return out

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📊 NSE STOCK INTELLIGENCE PRO")
page = st.sidebar.radio(
    "Select Module",
    ["Dashboard", "Single Stock Analysis", "NSE Screener", "Top Rankings"]
)

st.sidebar.markdown("---")
custom_input = st.sidebar.text_area(
    "Custom NSE symbols (comma separated)",
    value=",".join(DEFAULT_NSE_STOCKS[:10])
)
custom_symbols = [x.strip().upper() for x in custom_input.split(",") if x.strip()]

# =========================
# DASHBOARD
# =========================
if page == "Dashboard":
    st.title("📈 NSE STOCK INTELLIGENCE PRO")
    st.markdown("### Professional Fundamental + Technical Analysis for NSE Stocks")

    col1, col2, col3 = st.columns(3)
    col1.metric("Default Universe", len(DEFAULT_NSE_STOCKS))
    col2.metric("Custom Universe", len(custom_symbols))
    col3.metric("Last Updated", datetime.now().strftime("%d-%m-%Y %H:%M"))

    st.markdown("---")
    st.subheader("⚡ Quick Screener Snapshot")

    screener_df = run_screener(custom_symbols if custom_symbols else DEFAULT_NSE_STOCKS)

    if screener_df.empty:
        st.warning("No screener data available.")
    else:
        st.dataframe(screener_df, use_container_width=True)

        csv = screener_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Screener CSV",
            data=csv,
            file_name="nse_screener_snapshot.csv",
            mime="text/csv"
        )

        st.subheader("🏆 Top 5 Ranked Stocks")
        st.dataframe(screener_df.head(5), use_container_width=True)

# =========================
# SINGLE STOCK ANALYSIS
# =========================
elif page == "Single Stock Analysis":
    st.title("🔍 Single Stock Deep Analysis")

    symbol = st.selectbox("Select NSE Stock", custom_symbols if custom_symbols else DEFAULT_NSE_STOCKS)
    period = st.selectbox("Price History Period", ["6mo", "1y", "2y", "5y"], index=2)

    df = get_stock_data(symbol, period=period)
    info = get_stock_info(symbol)

    if df.empty:
        st.error("No data found for this symbol.")
    else:
        df = add_technical_indicators(df)

        f_score, f_details = fundamental_score(info)
        t_score, t_details = technical_score(df)
        combined = round(0.6 * f_score + 0.4 * t_score, 2)
        verdict = get_verdict(f_score, t_score, combined)

        latest = df.iloc[-1]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Price", f"₹ {latest['Close']:.2f}")
        c2.metric("Fundamental Score", f"{f_score}/100")
        c3.metric("Technical Score", f"{t_score}/100")
        c4.metric("Combined Score", f"{combined}/100")

        st.success(f"Verdict: {verdict}")

        st.plotly_chart(make_candlestick_chart(df, symbol), use_container_width=True)

        st.markdown("## 📌 Fundamental Metrics")
        fund_df = build_fundamental_table(info)
        fund_df["Formatted"] = fund_df.apply(lambda x: format_value(x["Metric"], x["Value"]), axis=1)
        st.dataframe(fund_df[["Metric", "Formatted"]], use_container_width=True)

        st.markdown("## 🧠 Technical Snapshot")
        tech_snapshot = pd.DataFrame({
            "Metric": [
                "Close", "SMA20", "SMA50", "SMA200", "EMA20", "EMA50",
                "RSI14", "MACD", "MACD Signal", "ATR14", "20D Avg Volume",
                "52W High", "52W Low"
            ],
            "Value": [
                latest["Close"], latest["SMA20"], latest["SMA50"], latest["SMA200"],
                latest["EMA20"], latest["EMA50"], latest["RSI14"], latest["MACD"],
                latest["MACD_SIGNAL"], latest["ATR14"], latest["VOL20"],
                latest["52W_HIGH"], latest["52W_LOW"]
            ]
        })
        st.dataframe(tech_snapshot, use_container_width=True)

        st.markdown("## 🏅 Score Breakdown")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Fundamental Score Breakdown")
            st.dataframe(pd.DataFrame(list(f_details.items()), columns=["Metric", "Points"]), use_container_width=True)
        with c2:
            st.subheader("Technical Score Breakdown")
            st.dataframe(pd.DataFrame(list(t_details.items()), columns=["Metric", "Points"]), use_container_width=True)

# =========================
# SCREENER PAGE
# =========================
elif page == "NSE Screener":
    st.title("🧮 NSE Stock Screener")

    symbols = custom_symbols if custom_symbols else DEFAULT_NSE_STOCKS
    screener_df = run_screener(symbols)

    if screener_df.empty:
        st.warning("No screener results available.")
    else:
        min_combined = st.slider("Minimum Combined Score", 0, 100, 60)
        only_above_200 = st.checkbox("Only Price > 200 DMA", value=False)
        only_volume = st.checkbox("Only Volume Breakout", value=False)

        filtered = screener_df[screener_df["Combined_Score"] >= min_combined]

        if only_above_200:
            filtered = filtered[filtered["Above_200DMA"] == True]

        if only_volume:
            filtered = filtered[filtered["Volume_Breakout"] == True]

        st.dataframe(filtered, use_container_width=True)

        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Filtered Screener CSV",
            data=csv,
            file_name="nse_filtered_screener.csv",
            mime="text/csv"
        )

# =========================
# TOP RANKINGS
# =========================
elif page == "Top Rankings":
    st.title("🏆 Top Ranked NSE Stocks")

    symbols = custom_symbols if custom_symbols else DEFAULT_NSE_STOCKS
    screener_df = run_screener(symbols)

    if screener_df.empty:
        st.warning("No ranking data available.")
    else:
        tab1, tab2, tab3 = st.tabs(["Combined Rank", "Fundamental Rank", "Technical Rank"])

        with tab1:
            st.dataframe(screener_df.sort_values("Combined_Score", ascending=False), use_container_width=True)

        with tab2:
            st.dataframe(screener_df.sort_values("Fundamental_Score", ascending=False), use_container_width=True)

        with tab3:
            st.dataframe(screener_df.sort_values("Technical_Score", ascending=False), use_container_width=True)

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("Built with Streamlit + yfinance for NSE (.NS). For education/research only. Validate before investing.")

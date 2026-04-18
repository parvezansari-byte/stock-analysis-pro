import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import math

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="FINAL V10.1 INSTITUTIONAL ULTRA PRO - NIFTY 50 + NEXT 50",
    page_icon="📈",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #111827 35%, #1e293b 100%);
        color: white;
    }
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #111827 35%, #1e293b 100%);
    }
    .hero-card {
        background: linear-gradient(135deg, rgba(30,41,59,0.95), rgba(15,23,42,0.95));
        border: 1px solid rgba(148,163,184,0.15);
        padding: 20px;
        border-radius: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        margin-bottom: 16px;
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(30,41,59,0.92), rgba(17,24,39,0.92));
        border: 1px solid rgba(148,163,184,0.12);
        padding: 16px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }
    .stock-card {
        background: linear-gradient(135deg, rgba(15,23,42,0.92), rgba(30,41,59,0.92));
        border: 1px solid rgba(59,130,246,0.15);
        padding: 14px;
        border-radius: 14px;
        margin-bottom: 10px;
    }
    .green-text {
        color: #22c55e;
        font-weight: 700;
    }
    .red-text {
        color: #ef4444;
        font-weight: 700;
    }
    .gold-text {
        color: #fbbf24;
        font-weight: 700;
    }
    .blue-text {
        color: #60a5fa;
        font-weight: 700;
    }
    h1, h2, h3, h4 {
        color: #f8fafc !important;
    }
    .small-note {
        color: #cbd5e1;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# STOCK UNIVERSE
# =========================
NIFTY_50 = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "INFY": "INFY.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "ITC": "ITC.NS",
    "SBIN": "SBIN.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "LT": "LT.NS",
    "AXISBANK": "AXISBANK.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "MARUTI": "MARUTI.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "HCLTECH": "HCLTECH.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "TITAN": "TITAN.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
    "NTPC": "NTPC.NS",
    "POWERGRID": "POWERGRID.NS",
    "NESTLEIND": "NESTLEIND.NS",
    "ONGC": "ONGC.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "M&M": "M&M.NS",
    "JSWSTEEL": "JSWSTEEL.NS",
    "TATASTEEL": "TATASTEEL.NS",
    "COALINDIA": "COALINDIA.NS",
    "INDUSINDBK": "INDUSINDBK.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS",
    "WIPRO": "WIPRO.NS",
    "HDFCLIFE": "HDFCLIFE.NS",
    "ADANIENT": "ADANIENT.NS",
    "ADANIPORTS": "ADANIPORTS.NS",
    "GRASIM": "GRASIM.NS",
    "CIPLA": "CIPLA.NS",
    "DRREDDY": "DRREDDY.NS",
    "TECHM": "TECHM.NS",
    "EICHERMOT": "EICHERMOT.NS",
    "APOLLOHOSP": "APOLLOHOSP.NS",
    "DIVISLAB": "DIVISLAB.NS",
    "BPCL": "BPCL.NS",
    "BRITANNIA": "BRITANNIA.NS",
    "HEROMOTOCO": "HEROMOTOCO.NS",
    "SHRIRAMFIN": "SHRIRAMFIN.NS",
    "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
    "TATACONSUM": "TATACONSUM.NS",
    "SBILIFE": "SBILIFE.NS",
    "HINDALCO": "HINDALCO.NS",
    "UPL": "UPL.NS"
}

NIFTY_NEXT_50 = {
    "DMART": "DMART.NS",
    "ZOMATO": "ZOMATO.NS",
    "HAL": "HAL.NS",
    "SIEMENS": "SIEMENS.NS",
    "PIDILITIND": "PIDILITIND.NS",
    "DABUR": "DABUR.NS",
    "GODREJCP": "GODREJCP.NS",
    "BANKBARODA": "BANKBARODA.NS",
    "PNB": "PNB.NS",
    "INDIGO": "INDIGO.NS",
    "TVSMOTOR": "TVSMOTOR.NS",
    "AMBUJACEM": "AMBUJACEM.NS",
    "BOSCHLTD": "BOSCHLTD.NS",
    "HAVELLS": "HAVELLS.NS",
    "ABB": "ABB.NS",
    "MCDOWELL-N": "MCDOWELL-N.NS",
    "BERGEPAINT": "BERGEPAINT.NS",
    "CHOLAFIN": "CHOLAFIN.NS",
    "TORNTPHARM": "TORNTPHARM.NS",
    "LODHA": "LODHA.NS",
    "DLF": "DLF.NS",
    "ICICIPRULI": "ICICIPRULI.NS",
    "NAUKRI": "NAUKRI.NS",
    "MOTHERSON": "MOTHERSON.NS",
    "INDUSTOWER": "INDUSTOWER.NS",
    "JINDALSTEL": "JINDALSTEL.NS",
    "CGPOWER": "CGPOWER.NS",
    "BHEL": "BHEL.NS",
    "IRCTC": "IRCTC.NS",
    "CANBK": "CANBK.NS",
    "PFC": "PFC.NS",
    "RECLTD": "RECLTD.NS",
    "ADANIENSOL": "ADANIENSOL.NS",
    "GAIL": "GAIL.NS",
    "MARICO": "MARICO.NS",
    "COLPAL": "COLPAL.NS",
    "BIOCON": "BIOCON.NS",
    "PAGEIND": "PAGEIND.NS",
    "UNIONBANK": "UNIONBANK.NS",
    "NMDC": "NMDC.NS",
    "HINDPETRO": "HINDPETRO.NS",
    "IOC": "IOC.NS",
    "LICI": "LICI.NS",
    "VEDL": "VEDL.NS",
    "SAIL": "SAIL.NS",
    "ICICIGI": "ICICIGI.NS",
    "SRF": "SRF.NS",
    "MPHASIS": "MPHASIS.NS",
    "TRENT": "TRENT.NS",
    "LTIM": "LTIM.NS"
}

ALL_STOCKS = {**NIFTY_50, **NIFTY_NEXT_50}

# =========================
# HELPERS
# =========================
@st.cache_data(ttl=3600)
def get_stock_data(symbol, period="1y", interval="1d"):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval, auto_adjust=True)
        info = ticker.info
        if hist is None or hist.empty:
            return None, None
        return hist, info
    except:
        return None, None

def safe_get(info, key, default=np.nan):
    try:
        val = info.get(key, default)
        if val is None:
            return default
        return val
    except:
        return default

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def compute_macd(close):
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist

def compute_technical_indicators(df):
    out = df.copy()
    out["SMA20"] = out["Close"].rolling(20).mean()
    out["SMA50"] = out["Close"].rolling(50).mean()
    out["SMA200"] = out["Close"].rolling(200).mean()
    out["EMA20"] = out["Close"].ewm(span=20, adjust=False).mean()
    out["RSI"] = compute_rsi(out["Close"], 14)
    out["MACD"], out["MACD_SIGNAL"], out["MACD_HIST"] = compute_macd(out["Close"])
    out["52W_HIGH"] = out["High"].rolling(252).max()
    out["52W_LOW"] = out["Low"].rolling(252).min()
    return out

def score_fundamentals(info):
    score = 0
    max_score = 100

    pe = safe_get(info, "trailingPE")
    pb = safe_get(info, "priceToBook")
    roe = safe_get(info, "returnOnEquity")
    de = safe_get(info, "debtToEquity")
    margin = safe_get(info, "profitMargins")
    growth = safe_get(info, "revenueGrowth")
    current_ratio = safe_get(info, "currentRatio")
    div_yield = safe_get(info, "dividendYield")

    # PE
    if pd.notna(pe):
        if pe < 20:
            score += 15
        elif pe < 30:
            score += 10
        elif pe < 50:
            score += 5

    # PB
    if pd.notna(pb):
        if pb < 3:
            score += 10
        elif pb < 6:
            score += 6
        elif pb < 10:
            score += 3

    # ROE
    if pd.notna(roe):
        roe_pct = roe * 100 if roe < 5 else roe
        if roe_pct > 20:
            score += 20
        elif roe_pct > 15:
            score += 15
        elif roe_pct > 10:
            score += 10
        elif roe_pct > 5:
            score += 5

    # Debt to Equity
    if pd.notna(de):
        if de < 50:
            score += 15
        elif de < 100:
            score += 10
        elif de < 200:
            score += 5

    # Profit Margin
    if pd.notna(margin):
        margin_pct = margin * 100 if margin < 5 else margin
        if margin_pct > 20:
            score += 15
        elif margin_pct > 10:
            score += 10
        elif margin_pct > 5:
            score += 5

    # Revenue Growth
    if pd.notna(growth):
        growth_pct = growth * 100 if growth < 5 else growth
        if growth_pct > 20:
            score += 15
        elif growth_pct > 10:
            score += 10
        elif growth_pct > 5:
            score += 5

    # Current Ratio
    if pd.notna(current_ratio):
        if current_ratio > 1.5:
            score += 5
        elif current_ratio > 1:
            score += 3

    # Dividend Yield
    if pd.notna(div_yield):
        dy_pct = div_yield * 100 if div_yield < 5 else div_yield
        if dy_pct > 2:
            score += 5

    return min(score, max_score)

def score_technicals(df):
    if df is None or df.empty:
        return 0

    latest = df.iloc[-1]
    score = 0

    close = latest["Close"]
    sma20 = latest.get("SMA20", np.nan)
    sma50 = latest.get("SMA50", np.nan)
    sma200 = latest.get("SMA200", np.nan)
    rsi = latest.get("RSI", np.nan)
    macd = latest.get("MACD", np.nan)
    macd_signal = latest.get("MACD_SIGNAL", np.nan)
    high_52 = latest.get("52W_HIGH", np.nan)
    low_52 = latest.get("52W_LOW", np.nan)

    # Trend
    if pd.notna(sma20) and close > sma20:
        score += 15
    if pd.notna(sma50) and close > sma50:
        score += 20
    if pd.notna(sma200) and close > sma200:
        score += 25

    # RSI
    if pd.notna(rsi):
        if 45 <= rsi <= 65:
            score += 15
        elif 35 <= rsi <= 75:
            score += 8

    # MACD
    if pd.notna(macd) and pd.notna(macd_signal):
        if macd > macd_signal:
            score += 15

    # Position in 52W range
    if pd.notna(high_52) and pd.notna(low_52) and high_52 != low_52:
        pos = (close - low_52) / (high_52 - low_52)
        if 0.6 <= pos <= 0.9:
            score += 10

    return min(score, 100)

def overall_rating(fund_score, tech_score):
    total = round((fund_score * 0.55) + (tech_score * 0.45), 2)
    if total >= 80:
        label = "STRONG BUY"
    elif total >= 65:
        label = "BUY"
    elif total >= 50:
        label = "HOLD"
    elif total >= 35:
        label = "WEAK"
    else:
        label = "AVOID"
    return total, label

def pct_change(series, days):
    if len(series) <= days:
        return np.nan
    return ((series.iloc[-1] / series.iloc[-days-1]) - 1) * 100

@st.cache_data(ttl=3600)
def analyze_stock(symbol):
    hist, info = get_stock_data(symbol, period="1y", interval="1d")
    if hist is None or hist.empty:
        return None

    df = compute_technical_indicators(hist)

    close = df["Close"]
    latest = df.iloc[-1]

    current_price = float(latest["Close"])
    returns_1m = pct_change(close, 21)
    returns_3m = pct_change(close, 63)
    returns_6m = pct_change(close, 126)
    returns_1y = pct_change(close, 252)

    fund_score = score_fundamentals(info if info else {})
    tech_score = score_technicals(df)
    total_score, label = overall_rating(fund_score, tech_score)

    market_cap = safe_get(info, "marketCap")
    pe = safe_get(info, "trailingPE")
    pb = safe_get(info, "priceToBook")
    roe = safe_get(info, "returnOnEquity")
    de = safe_get(info, "debtToEquity")
    margin = safe_get(info, "profitMargins")
    growth = safe_get(info, "revenueGrowth")
    div_yield = safe_get(info, "dividendYield")
    sector = safe_get(info, "sector", "Unknown")
    beta = safe_get(info, "beta")
    volume = safe_get(info, "volume")

    rsi = latest.get("RSI", np.nan)
    sma50 = latest.get("SMA50", np.nan)
    sma200 = latest.get("SMA200", np.nan)
    macd = latest.get("MACD", np.nan)
    macd_signal = latest.get("MACD_SIGNAL", np.nan)
    high_52 = latest.get("52W_HIGH", np.nan)
    low_52 = latest.get("52W_LOW", np.nan)

    return {
        "Symbol": symbol.replace(".NS", ""),
        "Ticker": symbol,
        "Sector": sector,
        "Price": current_price,
        "1M %": returns_1m,
        "3M %": returns_3m,
        "6M %": returns_6m,
        "1Y %": returns_1y,
        "Market Cap": market_cap,
        "PE": pe,
        "PB": pb,
        "ROE": roe * 100 if pd.notna(roe) and roe < 5 else roe,
        "Debt/Equity": de,
        "Profit Margin": margin * 100 if pd.notna(margin) and margin < 5 else margin,
        "Revenue Growth": growth * 100 if pd.notna(growth) and growth < 5 else growth,
        "Dividend Yield": div_yield * 100 if pd.notna(div_yield) and div_yield < 5 else div_yield,
        "Beta": beta,
        "Volume": volume,
        "RSI": rsi,
        "SMA50": sma50,
        "SMA200": sma200,
        "MACD": macd,
        "MACD Signal": macd_signal,
        "52W High": high_52,
        "52W Low": low_52,
        "Fundamental Score": fund_score,
        "Technical Score": tech_score,
        "Total Score": total_score,
        "Rating": label,
        "Hist": df
    }

def format_large_num(x):
    if pd.isna(x):
        return "N/A"
    try:
        x = float(x)
        if x >= 1e12:
            return f"₹{x/1e12:.2f} T"
        elif x >= 1e9:
            return f"₹{x/1e9:.2f} B"
        elif x >= 1e7:
            return f"₹{x/1e7:.2f} Cr"
        else:
            return f"₹{x:,.0f}"
    except:
        return "N/A"

def colorize_rating(rating):
    if rating == "STRONG BUY":
        return "green-text"
    elif rating == "BUY":
        return "blue-text"
    elif rating == "HOLD":
        return "gold-text"
    else:
        return "red-text"

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ V10.1 Institutional Control Panel")

universe_choice = st.sidebar.selectbox(
    "Select Universe",
    ["NIFTY 50", "NIFTY NEXT 50", "NIFTY 100 (Both)"]
)

if universe_choice == "NIFTY 50":
    selected_universe = NIFTY_50
elif universe_choice == "NIFTY NEXT 50":
    selected_universe = NIFTY_NEXT_50
else:
    selected_universe = ALL_STOCKS

top_n = st.sidebar.slider("Top Ranked Stocks", 5, 30, 15)
min_score_filter = st.sidebar.slider("Minimum Total Score Filter", 0, 100, 50)

sort_by = st.sidebar.selectbox(
    "Sort By",
    ["Total Score", "Fundamental Score", "Technical Score", "1M %", "3M %", "6M %", "1Y %", "PE", "ROE"]
)

show_only_buy = st.sidebar.checkbox("Show only BUY / STRONG BUY", value=False)

selected_stock = st.sidebar.selectbox(
    "Single Stock Deep Analysis",
    list(selected_universe.values())
)

run_scan = st.sidebar.button("🚀 Run Institutional Scan", use_container_width=True)

# =========================
# HEADER
# =========================
st.markdown("""
<div class="hero-card">
    <h1>📈 FINAL V10.1 INSTITUTIONAL ULTRA PRO</h1>
    <h3>NIFTY 50 + NIFTY NEXT 50 Master Scanner</h3>
    <p class="small-note">
        Premium institutional-grade stock analysis dashboard for Indian equities • 
        Fundamental + Technical + Smart Ranking + Portfolio Shortlisting
    </p>
</div>
""", unsafe_allow_html=True)

# =========================
# QUICK MARKET PANEL
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card"><h4>Universe</h4><h2>100</h2><p>NIFTY 50 + NEXT 50</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><h4>Focus</h4><h2>Institutional</h2><p>Quality + Momentum + Risk</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><h4>Modules</h4><h2>Fundamental</h2><p>+ Technical + Ranking</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card"><h4>Mode</h4><h2>Cloud Safe</h2><p>Single app.py</p></div>', unsafe_allow_html=True)

st.markdown("---")

# =========================
# MAIN TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs([
    "🏛️ Institutional Scanner",
    "🔍 Single Stock Deep Analysis",
    "📊 Compare Stocks",
    "📘 Methodology"
])

# =========================
# TAB 1: SCANNER
# =========================
with tab1:
    st.subheader("🏛️ Institutional Master Scanner")

    if run_scan:
        progress = st.progress(0)
        results = []

        stock_list = list(selected_universe.values())
        total = len(stock_list)

        for i, symbol in enumerate(stock_list):
            res = analyze_stock(symbol)
            if res:
                results.append(res)
            progress.progress((i + 1) / total)

        if results:
            df = pd.DataFrame(results)

            if show_only_buy:
                df = df[df["Rating"].isin(["BUY", "STRONG BUY"])]

            df = df[df["Total Score"] >= min_score_filter]

            if sort_by in df.columns:
                ascending = True if sort_by == "PE" else False
                df = df.sort_values(by=sort_by, ascending=ascending)

            top_df = df.head(top_n).copy()

            # Dashboard metrics
            c1, c2, c3, c4, c5 = st.columns(5)

            with c1:
                st.metric("Stocks Scanned", len(results))
            with c2:
                st.metric("After Filters", len(df))
            with c3:
                st.metric("STRONG BUY", int((df["Rating"] == "STRONG BUY").sum()))
            with c4:
                st.metric("BUY", int((df["Rating"] == "BUY").sum()))
            with c5:
                avg_score = round(df["Total Score"].mean(), 2) if len(df) else 0
                st.metric("Avg Score", avg_score)

            st.markdown("### 🏆 Top Institutional Ranked Stocks")

            display_df = top_df[[
                "Symbol", "Sector", "Price", "1M %", "3M %", "6M %", "1Y %",
                "PE", "ROE", "Debt/Equity", "RSI",
                "Fundamental Score", "Technical Score", "Total Score", "Rating"
            ]].copy()

            for col in ["Price", "1M %", "3M %", "6M %", "6M %", "1Y %", "PE", "ROE", "Debt/Equity", "RSI", "Fundamental Score", "Technical Score", "Total Score"]:
                if col in display_df.columns:
                    display_df[col] = pd.to_numeric(display_df[col], errors="coerce").round(2)

            st.dataframe(display_df, use_container_width=True, height=500)

            st.markdown("### 🎯 Premium Shortlist Cards")
            for _, row in top_df.iterrows():
                rating_class = colorize_rating(row["Rating"])
                st.markdown(f"""
                <div class="stock-card">
                    <h4>{row['Symbol']} <span class="{rating_class}">({row['Rating']})</span></h4>
                    <p><b>Sector:</b> {row['Sector']} | <b>Price:</b> ₹{row['Price']:.2f}</p>
                    <p><b>Total Score:</b> {row['Total Score']:.1f} | <b>Fundamental:</b> {row['Fundamental Score']} | <b>Technical:</b> {row['Technical Score']}</p>
                    <p><b>1M:</b> {row['1M %']:.2f}% | <b>3M:</b> {row['3M %']:.2f}% | <b>6M:</b> {row['6M %']:.2f}% | <b>1Y:</b> {row['1Y %']:.2f}%</p>
                    <p><b>PE:</b> {row['PE'] if pd.notna(row['PE']) else 'N/A'} | <b>ROE:</b> {row['ROE'] if pd.notna(row['ROE']) else 'N/A'} | <b>D/E:</b> {row['Debt/Equity'] if pd.notna(row['Debt/Equity']) else 'N/A'} | <b>RSI:</b> {row['RSI'] if pd.notna(row['RSI']) else 'N/A'}</p>
                </div>
                """, unsafe_allow_html=True)

            # Download CSV
            csv = display_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Top Ranked CSV",
                data=csv,
                file_name="v10_1_nifty_institutional_scan.csv",
                mime="text/csv"
            )
        else:
            st.warning("No stock data could be fetched. Try again later.")
    else:
        st.info("Click **🚀 Run Institutional Scan** from the sidebar to scan NIFTY 50 / NIFTY NEXT 50.")

# =========================
# TAB 2: SINGLE STOCK
# =========================
with tab2:
    st.subheader("🔍 Single Stock Deep Analysis")

    single_result = analyze_stock(selected_stock)

    if single_result:
        rating_class = colorize_rating(single_result["Rating"])

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Stock", single_result["Symbol"])
        with c2:
            st.metric("Current Price", f"₹{single_result['Price']:.2f}")
        with c3:
            st.metric("Total Score", f"{single_result['Total Score']:.2f}")
        with c4:
            st.markdown(f"<h3 class='{rating_class}'>{single_result['Rating']}</h3>", unsafe_allow_html=True)

        st.markdown("### 📈 Price Chart")
        hist_df = single_result["Hist"]
        st.line_chart(hist_df["Close"], height=350)

        st.markdown("### 📊 Technical Indicators")
        tc1, tc2, tc3, tc4 = st.columns(4)
        with tc1:
            st.metric("RSI", f"{single_result['RSI']:.2f}" if pd.notna(single_result["RSI"]) else "N/A")
        with tc2:
            st.metric("SMA50", f"₹{single_result['SMA50']:.2f}" if pd.notna(single_result["SMA50"]) else "N/A")
        with tc3:
            st.metric("SMA200", f"₹{single_result['SMA200']:.2f}" if pd.notna(single_result["SMA200"]) else "N/A")
        with tc4:
            st.metric("MACD", f"{single_result['MACD']:.2f}" if pd.notna(single_result["MACD"]) else "N/A")

        st.markdown("### 🏛️ Fundamental Snapshot")
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            st.metric("PE", f"{single_result['PE']:.2f}" if pd.notna(single_result["PE"]) else "N/A")
        with fc2:
            st.metric("PB", f"{single_result['PB']:.2f}" if pd.notna(single_result["PB"]) else "N/A")
        with fc3:
            st.metric("ROE", f"{single_result['ROE']:.2f}%" if pd.notna(single_result["ROE"]) else "N/A")
        with fc4:
            st.metric("Debt/Equity", f"{single_result['Debt/Equity']:.2f}" if pd.notna(single_result["Debt/Equity"]) else "N/A")

        st.markdown("### 💼 Advanced Institutional Data")
        adv_df = pd.DataFrame({
            "Metric": [
                "Sector", "Market Cap", "Profit Margin", "Revenue Growth",
                "Dividend Yield", "Beta", "Volume", "52W High", "52W Low",
                "1M Return", "3M Return", "6M Return", "1Y Return"
            ],
            "Value": [
                single_result["Sector"],
                format_large_num(single_result["Market Cap"]),
                f"{single_result['Profit Margin']:.2f}%" if pd.notna(single_result["Profit Margin"]) else "N/A",
                f"{single_result['Revenue Growth']:.2f}%" if pd.notna(single_result["Revenue Growth"]) else "N/A",
                f"{single_result['Dividend Yield']:.2f}%" if pd.notna(single_result["Dividend Yield"]) else "N/A",
                f"{single_result['Beta']:.2f}" if pd.notna(single_result["Beta"]) else "N/A",
                f"{int(single_result['Volume']):,}" if pd.notna(single_result["Volume"]) else "N/A",
                f"₹{single_result['52W High']:.2f}" if pd.notna(single_result["52W High"]) else "N/A",
                f"₹{single_result['52W Low']:.2f}" if pd.notna(single_result["52W Low"]) else "N/A",
                f"{single_result['1M %']:.2f}%" if pd.notna(single_result["1M %"]) else "N/A",
                f"{single_result['3M %']:.2f}%" if pd.notna(single_result["3M %"]) else "N/A",
                f"{single_result['6M %']:.2f}%" if pd.notna(single_result["6M %"]) else "N/A",
                f"{single_result['1Y %']:.2f}%" if pd.notna(single_result["1Y %"]) else "N/A",
            ]
        })
        st.dataframe(adv_df, use_container_width=True, height=460)

        st.markdown("### 🧠 Institutional Interpretation")
        interpretation = []
        if pd.notna(single_result["RSI"]):
            if single_result["RSI"] > 70:
                interpretation.append("• RSI indicates overbought zone.")
            elif single_result["RSI"] < 30:
                interpretation.append("• RSI indicates oversold zone.")
            else:
                interpretation.append("• RSI is in healthy momentum range.")

        if pd.notna(single_result["Price"]) and pd.notna(single_result["SMA50"]):
            if single_result["Price"] > single_result["SMA50"]:
                interpretation.append("• Price is above 50 DMA (bullish short-medium trend).")
            else:
                interpretation.append("• Price is below 50 DMA (trend weakness).")

        if pd.notna(single_result["Price"]) and pd.notna(single_result["SMA200"]):
            if single_result["Price"] > single_result["SMA200"]:
                interpretation.append("• Price is above 200 DMA (long-term bullish structure).")
            else:
                interpretation.append("• Price is below 200 DMA (long-term caution).")

        if pd.notna(single_result["ROE"]):
            if single_result["ROE"] > 15:
                interpretation.append("• ROE indicates strong business quality.")
            else:
                interpretation.append("• ROE is average or below elite quality threshold.")

        if pd.notna(single_result["Debt/Equity"]):
            if single_result["Debt/Equity"] < 100:
                interpretation.append("• Debt profile appears manageable.")
            else:
                interpretation.append("• Leverage is relatively high — monitor debt risk.")

        for line in interpretation:
            st.write(line)

# =========================
# TAB 3: COMPARE
# =========================
with tab3:
    st.subheader("📊 Compare Multiple Stocks")

    compare_options = list(selected_universe.values())
    selected_compare = st.multiselect(
        "Select up to 5 stocks to compare",
        options=compare_options,
        default=compare_options[:3]
    )

    if selected_compare:
        compare_results = []
        for sym in selected_compare[:5]:
            res = analyze_stock(sym)
            if res:
                compare_results.append(res)

        if compare_results:
            cmp_df = pd.DataFrame(compare_results)[[
                "Symbol", "Sector", "Price", "PE", "PB", "ROE", "Debt/Equity",
                "1M %", "3M %", "6M %", "1Y %", "RSI",
                "Fundamental Score", "Technical Score", "Total Score", "Rating"
            ]]

            numeric_cols = ["Price", "PE", "PB", "ROE", "Debt/Equity", "1M %", "3M %", "6M %", "1Y %", "RSI", "Fundamental Score", "Technical Score", "Total Score"]
            for col in numeric_cols:
                if col in cmp_df.columns:
                    cmp_df[col] = pd.to_numeric(cmp_df[col], errors="coerce").round(2)

            st.dataframe(cmp_df, use_container_width=True, height=400)

            st.markdown("### 📈 Price Performance Comparison (1Y)")
            perf_data = {}
            for item in compare_results:
                hist = item["Hist"]
                if hist is not None and not hist.empty:
                    base = hist["Close"].iloc[0]
                    perf = (hist["Close"] / base) * 100
                    perf_data[item["Symbol"]] = perf.values

            if perf_data:
                min_len = min(len(v) for v in perf_data.values())
                perf_df = pd.DataFrame({k: v[-min_len:] for k, v in perf_data.items()})
                st.line_chart(perf_df, height=350)

# =========================
# TAB 4: METHODOLOGY
# =========================
with tab4:
    st.subheader("📘 Institutional Scoring Methodology")

    st.markdown("""
### 🏛️ Fundamental Score (55% weight)
- **PE Ratio** → Lower reasonable valuation preferred
- **PB Ratio** → Better asset valuation efficiency
- **ROE** → Business quality & capital efficiency
- **Debt/Equity** → Balance sheet strength
- **Profit Margin** → Operational profitability
- **Revenue Growth** → Growth momentum
- **Current Ratio** → Liquidity quality
- **Dividend Yield** → Shareholder return bonus

### 📈 Technical Score (45% weight)
- **Price vs 20DMA**
- **Price vs 50DMA**
- **Price vs 200DMA**
- **RSI health zone**
- **MACD bullish crossover**
- **Position in 52-week range**

### 🎯 Final Rating Logic
- **80+** → STRONG BUY
- **65–79** → BUY
- **50–64** → HOLD
- **35–49** → WEAK
- **Below 35** → AVOID

### ⚠️ Important Note
This app is for **research, education, and professional screening**.  
Always combine with:
- Quarterly results
- Sector rotation
- Valuation context
- Management quality
- Macro environment
- Risk management / stop-loss / position sizing
""")

st.markdown("---")
st.caption("FINAL V10.1 INSTITUTIONAL ULTRA PRO • NIFTY 50 + NIFTY NEXT 50 • Single File • Streamlit Cloud Safe")

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="BLACKROCK PRIME MASTER | V12.1.2.1",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# SAFE HELPERS
# =========================
def safe_float(val, default=0.0):
    try:
        if val is None:
            return default
        if isinstance(val, str) and val.strip() == "":
            return default
        if pd.isna(val):
            return default
        return float(val)
    except:
        return default

def safe_int(val, default=0):
    try:
        if val is None:
            return default
        if isinstance(val, str) and val.strip() == "":
            return default
        if pd.isna(val):
            return default
        return int(val)
    except:
        return default

def fmt_num(val):
    try:
        if val is None or pd.isna(val):
            return "N/A"
        num = float(val)
        if abs(num) >= 1e12:
            return f"{num/1e12:.2f}T"
        elif abs(num) >= 1e9:
            return f"{num/1e9:.2f}B"
        elif abs(num) >= 1e7:
            return f"{num/1e7:.2f}Cr"
        elif abs(num) >= 1e5:
            return f"{num/1e5:.2f}L"
        else:
            return f"{num:,.2f}"
    except:
        return "N/A"

def fmt_pct(val):
    try:
        if val is None or pd.isna(val):
            return "N/A"
        return f"{float(val):.2f}%"
    except:
        return "N/A"

def fmt_currency(val):
    try:
        if val is None or pd.isna(val):
            return "N/A"
        return f"₹ {float(val):,.2f}"
    except:
        return "N/A"

def get_unique_key(prefix, suffix):
    return f"{prefix}_{suffix}_{abs(hash(str(suffix))) % 1000000}"

# =========================
# THEME / CSS
# =========================
st.markdown("""
<style>
    .main {
        background: linear-gradient(180deg, #0b1020 0%, #111827 100%);
        color: #f8fafc;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    .hero-box {
        background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.95));
        border: 1px solid rgba(148,163,184,0.15);
        border-radius: 20px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(17,24,39,0.95), rgba(31,41,55,0.95));
        border: 1px solid rgba(148,163,184,0.12);
        border-radius: 18px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 8px 22px rgba(0,0,0,0.18);
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .small-note {
        color: #94a3b8;
        font-size: 0.85rem;
    }

    div[data-testid="metric-container"] {
        background: rgba(15,23,42,0.75);
        border: 1px solid rgba(148,163,184,0.10);
        padding: 10px 12px;
        border-radius: 16px;
    }

    .stDataFrame, .stTable {
        border-radius: 14px;
        overflow: hidden;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 8px 14px;
        background: rgba(30,41,59,0.75);
    }

    .stButton>button {
        border-radius: 12px;
        border: 1px solid rgba(148,163,184,0.15);
    }
</style>
""", unsafe_allow_html=True)

# =========================
# DEFAULT STOCK LIST
# =========================
DEFAULT_STOCKS = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
    "LT": "LT.NS",
    "ITC": "ITC.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "AXISBANK": "AXISBANK.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "MARUTI": "MARUTI.NS",
    "TITAN": "TITAN.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
    "WIPRO": "WIPRO.NS",
    "NTPC": "NTPC.NS"
}

# =========================
# CACHE FUNCTIONS
# =========================
@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock_data(symbol, period="1y", interval="1d"):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval, auto_adjust=False)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600, show_spinner=False)
def fetch_stock_info(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if info is None:
            return {}
        return info
    except:
        return {}

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_financials(symbol):
    try:
        ticker = yf.Ticker(symbol)
        return {
            "financials": ticker.financials if ticker.financials is not None else pd.DataFrame(),
            "balance_sheet": ticker.balance_sheet if ticker.balance_sheet is not None else pd.DataFrame(),
            "cashflow": ticker.cashflow if ticker.cashflow is not None else pd.DataFrame()
        }
    except:
        return {
            "financials": pd.DataFrame(),
            "balance_sheet": pd.DataFrame(),
            "cashflow": pd.DataFrame()
        }

# =========================
# INDICATORS
# =========================
def add_indicators(df):
    if df.empty:
        return df

    d = df.copy()

    # Ensure required columns
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col not in d.columns:
            d[col] = np.nan

    d["SMA20"] = d["Close"].rolling(20).mean()
    d["SMA50"] = d["Close"].rolling(50).mean()
    d["EMA20"] = d["Close"].ewm(span=20, adjust=False).mean()

    # RSI
    delta = d["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    d["RSI"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = d["Close"].ewm(span=12, adjust=False).mean()
    ema26 = d["Close"].ewm(span=26, adjust=False).mean()
    d["MACD"] = ema12 - ema26
    d["Signal"] = d["MACD"].ewm(span=9, adjust=False).mean()

    # ATR
    high_low = d["High"] - d["Low"]
    high_close = np.abs(d["High"] - d["Close"].shift())
    low_close = np.abs(d["Low"] - d["Close"].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    d["ATR"] = tr.rolling(14).mean()

    # Bollinger Bands
    d["BB_MID"] = d["Close"].rolling(20).mean()
    bb_std = d["Close"].rolling(20).std()
    d["BB_UPPER"] = d["BB_MID"] + 2 * bb_std
    d["BB_LOWER"] = d["BB_MID"] - 2 * bb_std

    # Returns
    d["Daily_Return"] = d["Close"].pct_change() * 100

    return d

# =========================
# SIGNAL ENGINE
# =========================
def generate_signal(df):
    if df.empty or len(df) < 60:
        return "NO DATA", 0, []

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    score = 0
    reasons = []

    close = safe_float(latest.get("Close"))
    sma20 = safe_float(latest.get("SMA20"))
    sma50 = safe_float(latest.get("SMA50"))
    rsi = safe_float(latest.get("RSI"))
    macd = safe_float(latest.get("MACD"))
    signal = safe_float(latest.get("Signal"))
    volume = safe_float(latest.get("Volume"))
    avg_volume = safe_float(df["Volume"].tail(20).mean()) if "Volume" in df.columns else 0

    if close > sma20 > sma50 and sma20 > 0 and sma50 > 0:
        score += 25
        reasons.append("Strong uptrend (Price > SMA20 > SMA50)")
    elif close > sma20:
        score += 10
        reasons.append("Price above SMA20")

    if 50 < rsi < 70:
        score += 15
        reasons.append("Healthy RSI momentum")
    elif rsi >= 70:
        score -= 5
        reasons.append("RSI overbought")
    elif rsi < 35:
        score += 5
        reasons.append("RSI oversold recovery zone")

    if macd > signal:
        score += 20
        reasons.append("MACD bullish crossover")

    if volume > avg_volume * 1.3 and avg_volume > 0:
        score += 15
        reasons.append("Volume breakout")

    prev_close = safe_float(prev.get("Close"))
    if prev_close > 0:
        day_change = ((close - prev_close) / prev_close) * 100
        if day_change > 2:
            score += 10
            reasons.append("Strong price momentum")
        elif day_change < -2:
            score -= 10
            reasons.append("Weak price action")

    if score >= 60:
        signal_text = "STRONG BUY"
    elif score >= 40:
        signal_text = "BUY"
    elif score >= 25:
        signal_text = "WATCHLIST"
    else:
        signal_text = "AVOID"

    return signal_text, score, reasons

# =========================
# POSITION SIZING
# =========================
def calculate_trade_levels(df, capital=100000, risk_pct=1.0):
    if df.empty:
        return {}

    latest = df.iloc[-1]
    close = safe_float(latest.get("Close"))
    atr = safe_float(latest.get("ATR"))

    if close <= 0:
        return {}

    if atr <= 0:
        atr = close * 0.02

    entry = close
    sl = max(0.01, close - (1.5 * atr))
    target1 = close + (2 * atr)
    target2 = close + (3.5 * atr)

    risk_amount = capital * (risk_pct / 100)
    risk_per_share = max(0.01, entry - sl)
    qty = max(1, int(risk_amount / risk_per_share))
    invested = qty * entry

    return {
        "entry": entry,
        "sl": sl,
        "target1": target1,
        "target2": target2,
        "qty": qty,
        "invested": invested,
        "risk_amount": risk_amount
    }

# =========================
# CHART
# =========================
def plot_candlestick(df, symbol):
    if df.empty:
        return None

    required_cols = {"Date", "Open", "High", "Low", "Close", "Volume"}
    if not required_cols.issubset(set(df.columns)):
        return None

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.75, 0.25]
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

    if "SMA20" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA20"], mode="lines", name="SMA20"), row=1, col=1)
    if "SMA50" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA50"], mode="lines", name="SMA50"), row=1, col=1)
    if "BB_UPPER" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_UPPER"], mode="lines", name="BB Upper", opacity=0.4), row=1, col=1)
    if "BB_LOWER" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_LOWER"], mode="lines", name="BB Lower", opacity=0.4), row=1, col=1)

    fig.add_trace(
        go.Bar(x=df["Date"], y=df["Volume"], name="Volume"),
        row=2, col=1
    )

    fig.update_layout(
        title=f"{symbol} | Candlestick Chart",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=700,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig

# =========================
# SCANNER
# =========================
def run_scanner(stock_map, period="6mo"):
    results = []

    for name, symbol in stock_map.items():
        try:
            df = fetch_stock_data(symbol, period=period)
            if df.empty or len(df) < 60:
                continue

            df = add_indicators(df)
            signal, score, reasons = generate_signal(df)

            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest

            close = safe_float(latest.get("Close"))
            prev_close = safe_float(prev.get("Close"))
            change_pct = ((close - prev_close) / prev_close * 100) if prev_close > 0 else 0

            rsi = safe_float(latest.get("RSI"))
            volume = safe_float(latest.get("Volume"))
            avg_vol = safe_float(df["Volume"].tail(20).mean()) if "Volume" in df.columns else 0
            vol_ratio = (volume / avg_vol) if avg_vol > 0 else 0

            results.append({
                "Stock": name,
                "Symbol": symbol,
                "Price": round(close, 2),
                "Change %": round(change_pct, 2),
                "RSI": round(rsi, 2),
                "Volume Ratio": round(vol_ratio, 2),
                "Signal": signal,
                "Score": score,
                "Reason": " | ".join(reasons[:3]) if reasons else "No clear setup"
            })
        except:
            continue

    if not results:
        return pd.DataFrame()

    df_results = pd.DataFrame(results)
    signal_order = {"STRONG BUY": 4, "BUY": 3, "WATCHLIST": 2, "AVOID": 1}
    df_results["SignalRank"] = df_results["Signal"].map(signal_order).fillna(0)
    df_results = df_results.sort_values(by=["SignalRank", "Score"], ascending=[False, False]).drop(columns=["SignalRank"])
    return df_results

# =========================
# FUNDAMENTAL EXTRACT
# =========================
def get_fundamental_snapshot(info):
    if not info:
        return {}

    return {
        "Company": info.get("longName", info.get("shortName", "N/A")),
        "Sector": info.get("sector", "N/A"),
        "Industry": info.get("industry", "N/A"),
        "Market Cap": info.get("marketCap"),
        "PE Ratio": info.get("trailingPE"),
        "Forward PE": info.get("forwardPE"),
        "PB Ratio": info.get("priceToBook"),
        "ROE": safe_float(info.get("returnOnEquity")) * 100 if info.get("returnOnEquity") is not None else None,
        "ROA": safe_float(info.get("returnOnAssets")) * 100 if info.get("returnOnAssets") is not None else None,
        "Dividend Yield": safe_float(info.get("dividendYield")) * 100 if info.get("dividendYield") is not None else None,
        "52W High": info.get("fiftyTwoWeekHigh"),
        "52W Low": info.get("fiftyTwoWeekLow"),
        "Current Price": info.get("currentPrice"),
        "Book Value": info.get("bookValue"),
        "EPS": info.get("trailingEps"),
        "Debt to Equity": info.get("debtToEquity"),
        "Revenue Growth": safe_float(info.get("revenueGrowth")) * 100 if info.get("revenueGrowth") is not None else None,
        "Profit Margins": safe_float(info.get("profitMargins")) * 100 if info.get("profitMargins") is not None else None
    }

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## ⚙️ BLACKROCK PRIME MASTER")
    st.caption("FINAL V12.1.2.1 UI BUGFIX DEPLOY SAFE")

    mode = st.radio(
        "Select Module",
        ["Single Stock Analysis", "Breakout Scanner", "Portfolio Builder", "Watchlist"],
        key="sidebar_mode_main"
    )

    stock_name = st.selectbox(
        "Select Stock",
        list(DEFAULT_STOCKS.keys()),
        index=0,
        key="sidebar_stock_select"
    )
    selected_symbol = DEFAULT_STOCKS[stock_name]

    custom_symbol = st.text_input(
        "Or Enter Custom NSE Symbol (e.g. IRFC.NS)",
        value="",
        key="sidebar_custom_symbol"
    ).strip().upper()

    final_symbol = custom_symbol if custom_symbol else selected_symbol

    period = st.selectbox(
        "Chart Period",
        ["3mo", "6mo", "1y", "2y", "5y"],
        index=2,
        key="sidebar_period"
    )

    capital = st.number_input(
        "Capital (₹)",
        min_value=10000,
        max_value=100000000,
        value=100000,
        step=10000,
        key="sidebar_capital"
    )

    risk_pct = st.slider(
        "Risk per Trade (%)",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.5,
        key="sidebar_risk_pct"
    )

# =========================
# HEADER
# =========================
st.markdown(f"""
<div class="hero-box">
    <h1 style="margin:0; color:#f8fafc;">📈 BLACKROCK PRIME MASTER</h1>
    <p style="margin:6px 0 0 0; color:#94a3b8;">
        FINAL V12.1.2.1 UI BUGFIX DEPLOY SAFE | Institutional Style Stock Dashboard
    </p>
</div>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE INIT (BUGFIX)
# =========================
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# =========================
# MAIN MODULES
# =========================
if mode == "Single Stock Analysis":
    st.markdown('<div class="section-title">🔍 Single Stock Analysis</div>', unsafe_allow_html=True)

    with st.spinner(f"Fetching data for {final_symbol}..."):
        df = fetch_stock_data(final_symbol, period=period)
        info = fetch_stock_info(final_symbol)

    if df.empty:
        st.error("No data available. Please check symbol or try later.")
        st.stop()

    df = add_indicators(df)
    signal, score, reasons = generate_signal(df)
    trade = calculate_trade_levels(df, capital=capital, risk_pct=risk_pct)
    fundamentals = get_fundamental_snapshot(info)

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    ltp = safe_float(latest.get("Close"))
    prev_close = safe_float(prev.get("Close"))
    change = ltp - prev_close if prev_close > 0 else 0
    change_pct = (change / prev_close * 100) if prev_close > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("LTP", fmt_currency(ltp), f"{change_pct:.2f}%")
    c2.metric("Signal", signal, f"Score: {score}")
    c3.metric("RSI", f"{safe_float(latest.get('RSI')):.2f}", None)
    c4.metric("MACD", f"{safe_float(latest.get('MACD')):.2f}", None)
    c5.metric("Volume", fmt_num(latest.get("Volume")), None)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Chart", "🎯 Trade Setup", "🏢 Fundamentals", "📑 Financials", "🧠 Summary"
    ])

    with tab1:
        fig = plot_candlestick(df.tail(180), final_symbol)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True, key=get_unique_key("chart", final_symbol))
        else:
            st.warning("Chart data unavailable.")

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("SMA20", fmt_currency(latest.get("SMA20")))
        r2.metric("SMA50", fmt_currency(latest.get("SMA50")))
        r3.metric("ATR", fmt_currency(latest.get("ATR")))
        r4.metric("Daily Return", fmt_pct(latest.get("Daily_Return")))

    with tab2:
        if trade:
            t1, t2, t3, t4 = st.columns(4)
            t1.metric("Entry", fmt_currency(trade["entry"]))
            t2.metric("Stop Loss", fmt_currency(trade["sl"]))
            t3.metric("Target 1", fmt_currency(trade["target1"]))
            t4.metric("Target 2", fmt_currency(trade["target2"]))

            t5, t6, t7 = st.columns(3)
            t5.metric("Suggested Qty", trade["qty"])
            t6.metric("Capital Used", fmt_currency(trade["invested"]))
            t7.metric("Risk Amount", fmt_currency(trade["risk_amount"]))

            rr1 = (trade["target1"] - trade["entry"]) / max(0.01, trade["entry"] - trade["sl"])
            rr2 = (trade["target2"] - trade["entry"]) / max(0.01, trade["entry"] - trade["sl"])

            st.info(f"Risk:Reward → T1 = {rr1:.2f} | T2 = {rr2:.2f}")
        else:
            st.warning("Trade setup unavailable.")

    with tab3:
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Market Cap", fmt_num(fundamentals.get("Market Cap")))
        f2.metric("PE Ratio", fmt_num(fundamentals.get("PE Ratio")))
        f3.metric("PB Ratio", fmt_num(fundamentals.get("PB Ratio")))
        f4.metric("Dividend Yield", fmt_pct(fundamentals.get("Dividend Yield")))

        f5, f6, f7, f8 = st.columns(4)
        f5.metric("ROE", fmt_pct(fundamentals.get("ROE")))
        f6.metric("ROA", fmt_pct(fundamentals.get("ROA")))
        f7.metric("Revenue Growth", fmt_pct(fundamentals.get("Revenue Growth")))
        f8.metric("Profit Margin", fmt_pct(fundamentals.get("Profit Margins")))

        st.write("### Company Snapshot")
        company_df = pd.DataFrame({
            "Field": ["Company", "Sector", "Industry", "Current Price", "52W High", "52W Low", "Book Value", "EPS", "Debt to Equity"],
            "Value": [
                fundamentals.get("Company", "N/A"),
                fundamentals.get("Sector", "N/A"),
                fundamentals.get("Industry", "N/A"),
                fmt_currency(fundamentals.get("Current Price")),
                fmt_currency(fundamentals.get("52W High")),
                fmt_currency(fundamentals.get("52W Low")),
                fmt_num(fundamentals.get("Book Value")),
                fmt_num(fundamentals.get("EPS")),
                fmt_num(fundamentals.get("Debt to Equity")),
            ]
        })
        st.dataframe(company_df, use_container_width=True, hide_index=True)

    with tab4:
        fin = fetch_financials(final_symbol)

        sub1, sub2, sub3 = st.tabs(["P&L", "Balance Sheet", "Cash Flow"])

        with sub1:
            if not fin["financials"].empty:
                st.dataframe(fin["financials"], use_container_width=True)
            else:
                st.info("P&L data not available.")

        with sub2:
            if not fin["balance_sheet"].empty:
                st.dataframe(fin["balance_sheet"], use_container_width=True)
            else:
                st.info("Balance sheet data not available.")

        with sub3:
            if not fin["cashflow"].empty:
                st.dataframe(fin["cashflow"], use_container_width=True)
            else:
                st.info("Cash flow data not available.")

    with tab5:
        st.write("### AI-Style Institutional Summary")
        st.success(f"Primary Signal: **{signal}** (Score: {score}/100)")

        if reasons:
            st.write("#### Key Reasons")
            for r in reasons:
                st.write(f"- {r}")
        else:
            st.write("- No strong setup currently.")

        summary = []
        if signal in ["STRONG BUY", "BUY"]:
            summary.append("Trend structure is constructive.")
        else:
            summary.append("Trend is not strong enough for aggressive entry.")

        if safe_float(latest.get("RSI")) > 70:
            summary.append("Stock may be extended in short term.")
        elif safe_float(latest.get("RSI")) < 35:
            summary.append("Potential oversold recovery candidate.")
        else:
            summary.append("Momentum is in normal tradable range.")

        if trade:
            summary.append(
                f"Suggested trade plan: Entry near {trade['entry']:.2f}, SL {trade['sl']:.2f}, T1 {trade['target1']:.2f}, T2 {trade['target2']:.2f}."
            )

        for s in summary:
            st.write(f"- {s}")

        add_key = get_unique_key("watchlist_btn", final_symbol)
        if st.button("➕ Add to Watchlist", key=add_key):
            if final_symbol not in st.session_state.watchlist:
                st.session_state.watchlist.append(final_symbol)
                st.success(f"{final_symbol} added to watchlist.")
            else:
                st.info(f"{final_symbol} already in watchlist.")

elif mode == "Breakout Scanner":
    st.markdown('<div class="section-title">🚀 Breakout Scanner</div>', unsafe_allow_html=True)
    st.caption("Scans default NSE basket for momentum + trend + volume setups.")

    scan_key = get_unique_key("scan_button", "main")
    if st.button("🔍 Run Scanner", key=scan_key):
        with st.spinner("Running institutional scanner..."):
            scan_df = run_scanner(DEFAULT_STOCKS, period="6mo")

        if scan_df.empty:
            st.warning("No scanner results available right now.")
        else:
            st.success(f"Found {len(scan_df)} stocks.")
            st.dataframe(scan_df, use_container_width=True, hide_index=True)

            top_picks = scan_df[scan_df["Signal"].isin(["STRONG BUY", "BUY"])].head(5)
            if not top_picks.empty:
                st.write("### 🏆 Top Picks")
                for _, row in top_picks.iterrows():
                    st.write(
                        f"- **{row['Stock']} ({row['Symbol']})** | Signal: **{row['Signal']}** | Score: **{row['Score']}** | Price: **₹ {row['Price']}**"
                    )

elif mode == "Portfolio Builder":
    st.markdown('<div class="section-title">💼 Portfolio Builder</div>', unsafe_allow_html=True)

    total_capital = st.number_input(
        "Portfolio Capital (₹)",
        min_value=50000,
        max_value=100000000,
        value=500000,
        step=50000,
        key="portfolio_total_capital"
    )

    top_n = st.slider(
        "Number of Stocks",
        min_value=3,
        max_value=10,
        value=5,
        key="portfolio_top_n"
    )

    build_key = get_unique_key("portfolio_build", "main")
    if st.button("⚡ Build Portfolio", key=build_key):
        with st.spinner("Building institutional model portfolio..."):
            scan_df = run_scanner(DEFAULT_STOCKS, period="6mo")

        if scan_df.empty:
            st.warning("Unable to build portfolio right now.")
        else:
            filtered = scan_df[scan_df["Signal"].isin(["STRONG BUY", "BUY", "WATCHLIST"])].head(top_n).copy()

            if filtered.empty:
                st.warning("No suitable stocks found.")
            else:
                weight = 100 / len(filtered)
                allocation = total_capital / len(filtered)

                filtered["Weight %"] = round(weight, 2)
                filtered["Allocation ₹"] = round(allocation, 2)
                filtered["Qty Approx"] = (filtered["Allocation ₹"] / filtered["Price"]).fillna(0).astype(int)

                st.success("Portfolio created successfully.")
                st.dataframe(
                    filtered[["Stock", "Symbol", "Signal", "Score", "Price", "Weight %", "Allocation ₹", "Qty Approx"]],
                    use_container_width=True,
                    hide_index=True
                )

                st.info("Equal-weight model portfolio based on current scanner ranking.")

elif mode == "Watchlist":
    st.markdown('<div class="section-title">⭐ Watchlist</div>', unsafe_allow_html=True)

    if not st.session_state.watchlist:
        st.info("Your watchlist is empty. Add stocks from Single Stock Analysis.")
    else:
        watch_results = []

        for sym in st.session_state.watchlist:
            try:
                df = fetch_stock_data(sym, period="6mo")
                if df.empty:
                    continue
                df = add_indicators(df)
                signal, score, _ = generate_signal(df)

                latest = df.iloc[-1]
                prev = df.iloc[-2] if len(df) > 1 else latest

                close = safe_float(latest.get("Close"))
                prev_close = safe_float(prev.get("Close"))
                chg_pct = ((close - prev_close) / prev_close * 100) if prev_close > 0 else 0

                watch_results.append({
                    "Symbol": sym,
                    "Price": round(close, 2),
                    "Change %": round(chg_pct, 2),
                    "RSI": round(safe_float(latest.get("RSI")), 2),
                    "Signal": signal,
                    "Score": score
                })
            except:
                continue

        if watch_results:
            watch_df = pd.DataFrame(watch_results)
            st.dataframe(watch_df, use_container_width=True, hide_index=True)

            clear_key = get_unique_key("clear_watchlist", "main")
            if st.button("🗑️ Clear Watchlist", key=clear_key):
                st.session_state.watchlist = []
                st.success("Watchlist cleared.")
        else:
            st.warning("Unable to fetch watchlist data.")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption(
    f"BLACKROCK PRIME MASTER | FINAL V12.1.2.1 UI BUGFIX DEPLOY SAFE | "
    f"Last Loaded: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)
st.caption("Deploy-safe notes: duplicate keys fixed • empty-data UI handled • Cloud-safe financial tabs • robust metric formatting")

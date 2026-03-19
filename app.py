import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Stock Analysis Pro V1.1", layout="wide")

# =========================================================
# FINAL STOCK ANALYSIS PRO APP V1.1 CLOUD SAFE PATCH
# - Better Streamlit Cloud stability
# - Safer yfinance handling
# - Better empty-data fallback
# - Cached downloads
# - Robust info extraction
# - Indian stock friendly
# =========================================================

# -----------------------------
# HELPERS
# -----------------------------
def safe_num(x, default=np.nan):
    try:
        if x is None:
            return default
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default


def format_num(x):
    try:
        if x is None or pd.isna(x):
            return "N/A"
        if abs(float(x)) >= 1_00_00_000:
            return f"{x:,.0f}"
        return f"{x:,.2f}"
    except Exception:
        return "N/A"


def format_pct(x):
    try:
        if x is None or pd.isna(x):
            return "N/A"
        return f"{x:.2f}%"
    except Exception:
        return "N/A"


def cagr(start, end, years):
    try:
        if start <= 0 or end <= 0 or years <= 0:
            return np.nan
        return ((end / start) ** (1 / years) - 1) * 100
    except Exception:
        return np.nan


def flatten_columns(df):
    try:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        return df
    except Exception:
        return df


def normalize_history(df):
    if df is None or df.empty:
        return pd.DataFrame()
    df = flatten_columns(df.copy())
    required = ["Open", "High", "Low", "Close", "Volume"]
    for col in required:
        if col not in df.columns:
            if col == "Volume":
                df[col] = 0
            else:
                return pd.DataFrame()
    return df.dropna(subset=["Close"]).copy()


def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.bfill().fillna(50)


def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist


def add_indicators(df):
    df = df.copy()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["SMA50"] = df["Close"].rolling(50, min_periods=1).mean()
    df["SMA200"] = df["Close"].rolling(200, min_periods=1).mean()
    df["RSI14"] = compute_rsi(df["Close"], 14)
    macd, signal, hist = compute_macd(df["Close"])
    df["MACD"] = macd
    df["MACD_SIGNAL"] = signal
    df["MACD_HIST"] = hist
    df["VOL20"] = df["Volume"].rolling(20, min_periods=1).mean()
    return df


def detect_support_resistance(df, lookback=60):
    recent = df.tail(min(lookback, len(df)))
    support = safe_num(recent["Low"].min())
    resistance = safe_num(recent["High"].max())
    return support, resistance


def get_financial_value(df, label_candidates):
    try:
        if df is None or df.empty:
            return None
        for label in label_candidates:
            if label in df.index:
                vals = pd.Series(df.loc[label]).dropna().values
                if len(vals) > 0:
                    return vals[0]
        return None
    except Exception:
        return None


def growth_from_statement(df, label_candidates, years=3):
    try:
        if df is None or df.empty:
            return np.nan
        for label in label_candidates:
            if label in df.index:
                row = pd.Series(df.loc[label]).dropna()
                if len(row) >= years + 1:
                    vals = row.iloc[: years + 1][::-1]  # oldest -> latest
                    start = safe_num(vals.iloc[0])
                    end = safe_num(vals.iloc[-1])
                    return cagr(start, end, years)
        return np.nan
    except Exception:
        return np.nan


def get_quarterly_growth(df, label_candidates):
    try:
        if df is None or df.empty:
            return np.nan
        for label in label_candidates:
            if label in df.index:
                row = pd.Series(df.loc[label]).dropna()
                if len(row) >= 4:
                    latest = safe_num(row.iloc[0])
                    year_ago = safe_num(row.iloc[3])
                    if not pd.isna(year_ago) and year_ago != 0:
                        return ((latest - year_ago) / abs(year_ago)) * 100
        return np.nan
    except Exception:
        return np.nan


def score_range(value, bands):
    if value is None or pd.isna(value):
        return 0
    for threshold, score in bands:
        if value >= threshold:
            return score
    return 0


def verdict_color(verdict):
    if "STRONG BUY" in verdict:
        return "#16a34a"
    if "BUY" in verdict:
        return "#22c55e"
    if "WATCHLIST" in verdict:
        return "#eab308"
    return "#ef4444"


# -----------------------------
# CLOUD SAFE DATA FETCHERS
# -----------------------------
@st.cache_data(ttl=900, show_spinner=False)
def fetch_history_cached(ticker, period):
    attempts = [
        {"auto_adjust": True, "repair": True},
        {"auto_adjust": False, "repair": True},
        {"auto_adjust": True, "repair": False},
    ]
    for a in attempts:
        try:
            df = yf.download(
                ticker,
                period=period,
                interval="1d",
                progress=False,
                threads=False,
                **a,
            )
            df = normalize_history(df)
            if not df.empty:
                return df
        except Exception:
            continue
    return pd.DataFrame()


@st.cache_data(ttl=900, show_spinner=False)
def fetch_benchmark_cached(period="6mo"):
    try:
        df = yf.download("^NSEI", period=period, interval="1d", progress=False, auto_adjust=True, threads=False)
        return normalize_history(df)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=900, show_spinner=False)
def fetch_fast_info_cached(ticker):
    # Safer than .info on cloud in many cases
    try:
        tk = yf.Ticker(ticker)
        fi = getattr(tk, "fast_info", None)
        if fi:
            try:
                return dict(fi)
            except Exception:
                return fi
        return {}
    except Exception:
        return {}


def safe_ticker(ticker):
    try:
        return yf.Ticker(ticker)
    except Exception:
        return None


# -----------------------------
# FUNDAMENTAL ANALYSIS
# -----------------------------
def fundamental_analysis(ticker_symbol, ticker_obj):
    info = {}
    fast_info = fetch_fast_info_cached(ticker_symbol)

    try:
        info = ticker_obj.info if ticker_obj else {}
        if not isinstance(info, dict):
            info = {}
    except Exception:
        info = {}

    try:
        income = ticker_obj.financials if ticker_obj else pd.DataFrame()
    except Exception:
        income = pd.DataFrame()

    try:
        cashflow = ticker_obj.cashflow if ticker_obj else pd.DataFrame()
    except Exception:
        cashflow = pd.DataFrame()

    try:
        q_income = ticker_obj.quarterly_financials if ticker_obj else pd.DataFrame()
    except Exception:
        q_income = pd.DataFrame()

    revenue_3y = growth_from_statement(income, ["Total Revenue", "Operating Revenue"], years=3)
    profit_3y = growth_from_statement(income, ["Net Income", "Net Income Common Stockholders", "Normalized Income"], years=3)
    q_sales_yoy = get_quarterly_growth(q_income, ["Total Revenue", "Operating Revenue"])
    q_profit_yoy = get_quarterly_growth(q_income, ["Net Income", "Net Income Common Stockholders", "Normalized Income"])

    roe = safe_num(info.get("returnOnEquity"))
    debt_to_equity = safe_num(info.get("debtToEquity"))
    profit_margin = safe_num(info.get("profitMargins"))
    operating_margin = safe_num(info.get("operatingMargins"))
    pe = safe_num(info.get("trailingPE"))
    pb = safe_num(info.get("priceToBook"))

    market_cap = info.get("marketCap", fast_info.get("marketCap") if isinstance(fast_info, dict) else None)
    current_price = info.get("currentPrice", info.get("regularMarketPrice", None))
    if current_price in [None, ""] and isinstance(fast_info, dict):
        current_price = fast_info.get("lastPrice", None)

    fifty_two_high = info.get("fiftyTwoWeekHigh", None)
    fifty_two_low = info.get("fiftyTwoWeekLow", None)
    if isinstance(fast_info, dict):
        fifty_two_high = fifty_two_high if fifty_two_high is not None else fast_info.get("yearHigh", None)
        fifty_two_low = fifty_two_low if fifty_two_low is not None else fast_info.get("yearLow", None)

    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    long_name = info.get("longName", info.get("shortName", ticker_symbol))

    cfo = get_financial_value(cashflow, ["Operating Cash Flow", "Total Cash From Operating Activities"])
    fcf = get_financial_value(cashflow, ["Free Cash Flow"])
    net_income_latest = get_financial_value(income, ["Net Income", "Net Income Common Stockholders", "Normalized Income"])

    cfo_vs_pat = np.nan
    try:
        if cfo is not None and net_income_latest not in [None, 0]:
            cfo_vs_pat = (safe_num(cfo) / abs(safe_num(net_income_latest))) * 100
    except Exception:
        cfo_vs_pat = np.nan

    score = 0
    score += score_range(revenue_3y, [(20, 15), (15, 12), (10, 9), (5, 5)])
    score += score_range(profit_3y, [(20, 15), (15, 12), (10, 9), (5, 5)])
    score += score_range(profit_3y, [(20, 10), (15, 8), (10, 6), (5, 3)])  # EPS proxy

    roe_pct = roe * 100 if not pd.isna(roe) else np.nan
    score += score_range(roe_pct, [(20, 15), (15, 12), (10, 8), (5, 4)])

    if not pd.isna(debt_to_equity):
        if debt_to_equity <= 50:
            score += 10
        elif debt_to_equity <= 100:
            score += 7
        elif debt_to_equity <= 200:
            score += 4
    else:
        score += 3

    opm_pct = operating_margin * 100 if not pd.isna(operating_margin) else np.nan
    score += score_range(opm_pct, [(20, 10), (15, 8), (10, 6), (5, 3)])

    if not pd.isna(cfo_vs_pat):
        if cfo_vs_pat >= 100:
            score += 10
        elif cfo_vs_pat >= 80:
            score += 8
        elif cfo_vs_pat >= 60:
            score += 5
    else:
        score += 3

    # Shareholding not available reliably on Yahoo for Indian stocks
    score += 3

    if not pd.isna(pe):
        if pe <= 20:
            score += 10
        elif pe <= 35:
            score += 7
        elif pe <= 50:
            score += 4
    else:
        score += 3

    return {
        "company": long_name,
        "sector": sector,
        "industry": industry,
        "market_cap": market_cap,
        "current_price": current_price,
        "52w_high": fifty_two_high,
        "52w_low": fifty_two_low,
        "sales_growth_3y": revenue_3y,
        "profit_growth_3y": profit_3y,
        "quarterly_sales_yoy": q_sales_yoy,
        "quarterly_profit_yoy": q_profit_yoy,
        "roe": roe_pct,
        "debt_to_equity": debt_to_equity,
        "opm": opm_pct,
        "npm": profit_margin * 100 if not pd.isna(profit_margin) else np.nan,
        "cfo": cfo,
        "fcf": fcf,
        "cfo_vs_pat": cfo_vs_pat,
        "pe": pe,
        "pb": pb,
        "fundamental_score": min(score, 100),
    }


# -----------------------------
# TECHNICAL ANALYSIS
# -----------------------------
def technical_analysis(df):
    df = add_indicators(df)
    latest = df.iloc[-1]

    price = safe_num(latest["Close"])
    ema20 = safe_num(latest["EMA20"])
    sma50 = safe_num(latest["SMA50"])
    sma200 = safe_num(latest["SMA200"])
    rsi = safe_num(latest["RSI14"])
    macd = safe_num(latest["MACD"])
    macd_signal = safe_num(latest["MACD_SIGNAL"])
    volume = safe_num(latest["Volume"], 0)
    vol20 = safe_num(latest["VOL20"], 0)

    support, resistance = detect_support_resistance(df, 60)

    trend_score = 0
    trend_label = "Neutral"
    if price > ema20 and price > sma50 and price > sma200 and sma50 > sma200:
        trend_score = 20
        trend_label = "Strong Bullish"
    elif price > sma50 and price > sma200:
        trend_score = 15
        trend_label = "Bullish"
    elif price > sma200:
        trend_score = 10
        trend_label = "Mild Bullish"
    elif price < sma200:
        trend_score = 4
        trend_label = "Weak / Bearish"

    ma_score = 0
    if price > ema20:
        ma_score += 5
    if price > sma50:
        ma_score += 5
    if price > sma200:
        ma_score += 5

    structure_score = 0
    if not pd.isna(support) and not pd.isna(resistance):
        if price >= resistance * 0.98:
            structure_score = 15
        elif price >= (support + resistance) / 2:
            structure_score = 10
        else:
            structure_score = 6

    volume_score = 0
    if vol20 > 0:
        if volume >= 1.5 * vol20:
            volume_score = 15
        elif volume >= 1.1 * vol20:
            volume_score = 10
        else:
            volume_score = 5
    else:
        volume_score = 3

    rsi_score = 0
    if rsi >= 60:
        rsi_score = 10
    elif rsi >= 50:
        rsi_score = 7
    elif rsi >= 40:
        rsi_score = 4
    else:
        rsi_score = 2

    macd_score = 10 if macd > macd_signal else 4

    rs_score = 5
    stock_ret = np.nan
    nifty_ret = np.nan
    try:
        nifty = fetch_benchmark_cached("6mo")
        if not nifty.empty and len(df) >= 2:
            stock_look = min(90, len(df) - 1)
            nifty_look = min(90, len(nifty) - 1)
            stock_ret = ((df["Close"].iloc[-1] / df["Close"].iloc[-(stock_look + 1)]) - 1) * 100
            nifty_ret = ((nifty["Close"].iloc[-1] / nifty["Close"].iloc[-(nifty_look + 1)]) - 1) * 100
            if stock_ret > nifty_ret + 5:
                rs_score = 10
            elif stock_ret > nifty_ret:
                rs_score = 8
            elif stock_ret > nifty_ret - 5:
                rs_score = 5
            else:
                rs_score = 2
    except Exception:
        rs_score = 5

    stop_loss = support if not pd.isna(support) else sma50
    if pd.isna(stop_loss):
        stop_loss = price * 0.92

    target1 = resistance if not pd.isna(resistance) else price * 1.08
    if target1 <= price:
        target1 = price * 1.06
    target2 = max(target1 * 1.08, price * 1.12)

    risk = max(price - stop_loss, 0.01)
    reward = max(target1 - price, 0.01)
    rr = reward / risk if risk > 0 else 1.0

    if rr >= 2:
        risk_reward_score = 5
    elif rr >= 1.2:
        risk_reward_score = 3
    else:
        risk_reward_score = 1

    technical_score = min(
        trend_score + ma_score + structure_score + volume_score + rsi_score + macd_score + rs_score + risk_reward_score,
        100,
    )

    return {
        "df": df,
        "price": price,
        "ema20": ema20,
        "sma50": sma50,
        "sma200": sma200,
        "rsi": rsi,
        "macd": macd,
        "macd_signal": macd_signal,
        "volume": volume,
        "vol20": vol20,
        "support": support,
        "resistance": resistance,
        "trend": trend_label,
        "stock_ret_90d": stock_ret,
        "nifty_ret_90d": nifty_ret,
        "entry_zone": f"{price * 0.98:.2f} - {price * 1.01:.2f}",
        "stop_loss": stop_loss,
        "target1": target1,
        "target2": target2,
        "rr": rr,
        "technical_score": technical_score,
    }


# -----------------------------
# DECISION ENGINE
# -----------------------------
def final_rating(score):
    if score >= 85:
        return "STRONG BUY CANDIDATE"
    elif score >= 75:
        return "BUY ON DIPS / ACCUMULATE"
    elif score >= 65:
        return "WATCHLIST / SELECTIVE BUY"
    elif score >= 50:
        return "AVOID FOR NOW"
    return "REJECT / WEAK"


# -----------------------------
# CHART
# -----------------------------
def create_chart(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price",
    ))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], mode="lines", name="EMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], mode="lines", name="SMA50"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA200"], mode="lines", name="SMA200"))
    fig.update_layout(
        title=f"{ticker} Price Chart",
        xaxis_rangeslider_visible=False,
        height=600,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


# -----------------------------
# UI
# -----------------------------
st.title("📊 STOCK ANALYSIS PRO APP V1.1 CLOUD SAFE PATCH")
st.caption("Fundamental + Technical + Scoring + Buy/Hold/Avoid | Streamlit Cloud Stable Version")

with st.sidebar:
    st.header("⚙️ Settings")
    ticker = st.text_input("Enter Stock Ticker", value="RELIANCE.NS").strip().upper()
    period = st.selectbox("Price History Period", ["6mo", "1y", "2y", "5y"], index=1)
    run = st.button("🚀 Analyze Stock", use_container_width=True)
    st.markdown("---")
    st.info("For Indian stocks use NSE format, e.g. RELIANCE.NS, TCS.NS, INFY.NS")

if run:
    if not ticker:
        st.error("Please enter a valid stock ticker.")
        st.stop()

    with st.spinner("Fetching data and running cloud-safe analysis..."):
        hist = fetch_history_cached(ticker, period)

        if hist.empty:
            st.error("No price data found. Please check ticker format (e.g. RELIANCE.NS) or try again after some time.")
            st.stop()

        stock = safe_ticker(ticker)
        fdata = fundamental_analysis(ticker, stock)
        tdata = technical_analysis(hist)

        # Fallback current price from chart if info missing
        if fdata.get("current_price") in [None, ""] or pd.isna(safe_num(fdata.get("current_price"))):
            fdata["current_price"] = safe_num(hist["Close"].iloc[-1])

        final_score = round((fdata["fundamental_score"] * 0.60) + (tdata["technical_score"] * 0.40), 2)
        verdict = final_rating(final_score)

    # TOP SUMMARY
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Price", format_num(fdata["current_price"]))
    c2.metric("Fundamental Score", f"{fdata['fundamental_score']}/100")
    c3.metric("Technical Score", f"{tdata['technical_score']}/100")
    c4.metric("Final Score", f"{final_score}/100")

    st.markdown(
        f"<div style='padding:12px;border-radius:12px;background:{verdict_color(verdict)};color:white;font-weight:700;text-align:center;'>FINAL VERDICT: {verdict}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # COMPANY + CHART
    left, right = st.columns([1, 2])
    with left:
        st.subheader("🏢 Company Snapshot")
        snapshot = pd.DataFrame({
            "Field": ["Company", "Sector", "Industry", "Market Cap", "52W High", "52W Low", "PE", "PB"],
            "Value": [
                fdata["company"],
                fdata["sector"],
                fdata["industry"],
                format_num(fdata["market_cap"]),
                format_num(fdata["52w_high"]),
                format_num(fdata["52w_low"]),
                format_num(fdata["pe"]),
                format_num(fdata["pb"]),
            ],
        })
        st.dataframe(snapshot, use_container_width=True, hide_index=True)

    with right:
        st.subheader("📈 Technical Price Chart")
        st.plotly_chart(create_chart(tdata["df"], ticker), use_container_width=True)

    # FUNDAMENTAL SECTION
    st.subheader("📘 Fundamental Analysis")
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        st.dataframe(
            pd.DataFrame({
                "Metric": [
                    "Sales Growth 3Y CAGR",
                    "Profit Growth 3Y CAGR",
                    "Quarterly Sales YoY",
                    "Quarterly Profit YoY",
                    "ROE",
                    "Debt to Equity",
                    "OPM",
                    "NPM",
                ],
                "Value": [
                    format_pct(fdata["sales_growth_3y"]),
                    format_pct(fdata["profit_growth_3y"]),
                    format_pct(fdata["quarterly_sales_yoy"]),
                    format_pct(fdata["quarterly_profit_yoy"]),
                    format_pct(fdata["roe"]),
                    format_num(fdata["debt_to_equity"]),
                    format_pct(fdata["opm"]),
                    format_pct(fdata["npm"]),
                ],
            }),
            use_container_width=True,
            hide_index=True,
        )

    with fcol2:
        st.dataframe(
            pd.DataFrame({
                "Metric": [
                    "Operating Cash Flow",
                    "Free Cash Flow",
                    "CFO vs PAT",
                    "Promoter Holding",
                    "Pledge",
                    "Fundamental Score",
                ],
                "Value": [
                    format_num(fdata["cfo"]),
                    format_num(fdata["fcf"]),
                    format_pct(fdata["cfo_vs_pat"]),
                    "N/A (Yahoo limitation)",
                    "N/A (Yahoo limitation)",
                    f"{fdata['fundamental_score']}/100",
                ],
            }),
            use_container_width=True,
            hide_index=True,
        )

    # TECHNICAL SECTION
    st.subheader("📙 Technical Analysis")
    tcol1, tcol2 = st.columns(2)
    with tcol1:
        st.dataframe(
            pd.DataFrame({
                "Metric": ["Trend", "EMA20", "SMA50", "SMA200", "RSI(14)", "MACD", "MACD Signal"],
                "Value": [
                    tdata["trend"],
                    format_num(tdata["ema20"]),
                    format_num(tdata["sma50"]),
                    format_num(tdata["sma200"]),
                    format_num(tdata["rsi"]),
                    format_num(tdata["macd"]),
                    format_num(tdata["macd_signal"]),
                ],
            }),
            use_container_width=True,
            hide_index=True,
        )

    with tcol2:
        st.dataframe(
            pd.DataFrame({
                "Metric": [
                    "Support",
                    "Resistance",
                    "90D Stock Return",
                    "90D Nifty Return",
                    "Entry Zone",
                    "Stop Loss",
                    "Target 1",
                    "Target 2",
                    "Risk/Reward",
                    "Technical Score",
                ],
                "Value": [
                    format_num(tdata["support"]),
                    format_num(tdata["resistance"]),
                    format_pct(tdata["stock_ret_90d"]),
                    format_pct(tdata["nifty_ret_90d"]),
                    tdata["entry_zone"],
                    format_num(tdata["stop_loss"]),
                    format_num(tdata["target1"]),
                    format_num(tdata["target2"]),
                    f"{tdata['rr']:.2f}",
                    f"{tdata['technical_score']}/100",
                ],
            }),
            use_container_width=True,
            hide_index=True,
        )

    # FINAL DECISION ENGINE
    st.subheader("🧠 Final Decision Engine")
    decision_df = pd.DataFrame({
        "Field": ["Fundamental Weight", "Technical Weight", "Combined Score", "Final Verdict", "Suggested Horizon", "Risk Note"],
        "Value": [
            "60%",
            "40%",
            f"{final_score}/100",
            verdict,
            "Long-term / Positional" if final_score >= 65 else "Watchlist / Avoid",
            "Model-based analysis only. Validate with latest quarterly results and management commentary.",
        ],
    })
    st.dataframe(decision_df, use_container_width=True, hide_index=True)

    # CLIENT SUMMARY
    st.subheader("📋 Client Summary (Copy Ready)")
    summary = f"""
STOCK ANALYSIS REPORT - {ticker}

Company: {fdata['company']}
Sector: {fdata['sector']}
Current Price: {format_num(fdata['current_price'])}

Fundamental Score: {fdata['fundamental_score']}/100
Technical Score: {tdata['technical_score']}/100
Final Combined Score: {final_score}/100
Final Verdict: {verdict}

Key Fundamental Highlights:
- Sales Growth 3Y: {format_pct(fdata['sales_growth_3y'])}
- Profit Growth 3Y: {format_pct(fdata['profit_growth_3y'])}
- ROE: {format_pct(fdata['roe'])}
- Debt to Equity: {format_num(fdata['debt_to_equity'])}
- OPM: {format_pct(fdata['opm'])}

Key Technical Highlights:
- Trend: {tdata['trend']}
- RSI: {format_num(tdata['rsi'])}
- Support: {format_num(tdata['support'])}
- Resistance: {format_num(tdata['resistance'])}
- Entry Zone: {tdata['entry_zone']}
- Stop Loss: {format_num(tdata['stop_loss'])}
- Target 1: {format_num(tdata['target1'])}
- Target 2: {format_num(tdata['target2'])}

Note: This is a model-driven screening tool. Please validate with latest quarterly results, annual report, and management commentary before investment.
"""
    st.text_area("Copy this summary", summary, height=350)

else:
    st.markdown("""
### ✅ What this app does
- Fundamental analysis (Sales, Profit, ROE, Debt, Margins, Cash Flow)
- Technical analysis (Trend, EMA20, SMA50, SMA200, RSI, MACD, Support/Resistance)
- Combined scoring model (60% Fundamental + 40% Technical)
- Final verdict: Strong Buy / Buy on Dips / Watchlist / Avoid
- Copy-ready client summary

### ▶️ How to use
1. Enter ticker like `RELIANCE.NS`
2. Select history period
3. Click **Analyze Stock**
4. Review full report

### ⚠️ Cloud Safe Notes
- Better handling for Streamlit Cloud + yfinance
- Uses cache for stability and speed
- Promoter holding / pledge may still show N/A for Indian stocks on Yahoo Finance
- For pro advisory, later we can connect Screener / NSE / CSV inputs
""")

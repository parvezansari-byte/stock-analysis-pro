
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Stock Analysis Pro V1", layout="wide")

# -----------------------------
# HELPERS
# -----------------------------
def safe_num(x, default=0.0):
    try:
        if x is None:
            return default
        if pd.isna(x):
            return default
        return float(x)
    except:
        return default


def format_num(x):
    try:
        if x is None or pd.isna(x):
            return "N/A"
        return f"{x:,.2f}"
    except:
        return "N/A"


def format_pct(x):
    try:
        if x is None or pd.isna(x):
            return "N/A"
        return f"{x:.2f}%"
    except:
        return "N/A"


def cagr(start, end, years):
    try:
        if start <= 0 or end <= 0 or years <= 0:
            return np.nan
        return ((end / start) ** (1 / years) - 1) * 100
    except:
        return np.nan


def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(method="bfill")


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
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()
    df["RSI14"] = compute_rsi(df["Close"], 14)
    macd, signal, hist = compute_macd(df["Close"])
    df["MACD"] = macd
    df["MACD_SIGNAL"] = signal
    df["MACD_HIST"] = hist
    df["VOL20"] = df["Volume"].rolling(20).mean()
    return df


def detect_support_resistance(df, lookback=60):
    recent = df.tail(lookback)
    support = recent["Low"].min()
    resistance = recent["High"].max()
    return support, resistance


def get_financial_value(df, label_candidates):
    if df is None or df.empty:
        return None
    for label in label_candidates:
        if label in df.index:
            vals = df.loc[label].dropna().values
            if len(vals) > 0:
                return vals[0]
    return None


def growth_from_statement(df, label_candidates, years=3):
    if df is None or df.empty:
        return np.nan
    for label in label_candidates:
        if label in df.index:
            row = df.loc[label].dropna()
            if len(row) >= years + 1:
                vals = row.iloc[: years + 1][::-1]  # oldest -> latest
                start = safe_num(vals.iloc[0], np.nan)
                end = safe_num(vals.iloc[-1], np.nan)
                return cagr(start, end, years)
    return np.nan


def get_quarterly_growth(df, label_candidates):
    if df is None or df.empty:
        return np.nan
    for label in label_candidates:
        if label in df.index:
            row = df.loc[label].dropna()
            if len(row) >= 4:
                latest = safe_num(row.iloc[0], np.nan)
                year_ago = safe_num(row.iloc[3], np.nan)
                if year_ago and not np.isnan(year_ago) and year_ago != 0:
                    return ((latest - year_ago) / abs(year_ago)) * 100
    return np.nan


def score_range(value, bands):
    # bands = [(threshold, score), ...] descending logic
    if value is None or pd.isna(value):
        return 0
    for threshold, score in bands:
        if value >= threshold:
            return score
    return 0


def fundamental_analysis(ticker_obj):
    info = ticker_obj.info if ticker_obj else {}
    income = ticker_obj.financials if ticker_obj else pd.DataFrame()
    balance = ticker_obj.balance_sheet if ticker_obj else pd.DataFrame()
    cashflow = ticker_obj.cashflow if ticker_obj else pd.DataFrame()
    q_income = ticker_obj.quarterly_financials if ticker_obj else pd.DataFrame()

    revenue_3y = growth_from_statement(income, ["Total Revenue", "Operating Revenue"], years=3)
    profit_3y = growth_from_statement(income, ["Net Income", "Net Income Common Stockholders", "Normalized Income"], years=3)
    q_sales_yoy = get_quarterly_growth(q_income, ["Total Revenue", "Operating Revenue"])
    q_profit_yoy = get_quarterly_growth(q_income, ["Net Income", "Net Income Common Stockholders", "Normalized Income"])

    roe = safe_num(info.get("returnOnEquity"), np.nan)
    roce = np.nan
    debt_to_equity = safe_num(info.get("debtToEquity"), np.nan)
    profit_margin = safe_num(info.get("profitMargins"), np.nan)
    operating_margin = safe_num(info.get("operatingMargins"), np.nan)
    promoter = np.nan  # not available in yfinance for most Indian stocks
    pledge = "N/A"
    pe = safe_num(info.get("trailingPE"), np.nan)
    pb = safe_num(info.get("priceToBook"), np.nan)
    market_cap = info.get("marketCap", None)
    current_price = info.get("currentPrice", info.get("regularMarketPrice", None))
    fifty_two_high = info.get("fiftyTwoWeekHigh", None)
    fifty_two_low = info.get("fiftyTwoWeekLow", None)
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    long_name = info.get("longName", info.get("shortName", "N/A"))

    # Cash flow check
    cfo = get_financial_value(cashflow, ["Operating Cash Flow", "Total Cash From Operating Activities"])
    fcf = get_financial_value(cashflow, ["Free Cash Flow"])
    net_income_latest = get_financial_value(income, ["Net Income", "Net Income Common Stockholders", "Normalized Income"])
    cfo_vs_pat = np.nan
    if cfo is not None and net_income_latest not in [None, 0]:
        try:
            cfo_vs_pat = (safe_num(cfo) / abs(safe_num(net_income_latest))) * 100
        except:
            cfo_vs_pat = np.nan

    # Fundamental score (100)
    score = 0
    score += score_range(revenue_3y, [(20, 15), (15, 12), (10, 9), (5, 5)])
    score += score_range(profit_3y, [(20, 15), (15, 12), (10, 9), (5, 5)])
    eps_growth_proxy = profit_3y
    score += score_range(eps_growth_proxy, [(20, 10), (15, 8), (10, 6), (5, 3)])
    roe_pct = roe * 100 if not pd.isna(roe) else np.nan
    score += score_range(roe_pct, [(20, 15), (15, 12), (10, 8), (5, 4)])

    if not pd.isna(debt_to_equity):
        if debt_to_equity <= 50:
            score += 10
        elif debt_to_equity <= 100:
            score += 7
        elif debt_to_equity <= 200:
            score += 4

    opm_pct = operating_margin * 100 if not pd.isna(operating_margin) else np.nan
    score += score_range(opm_pct, [(20, 10), (15, 8), (10, 6), (5, 3)])

    if not pd.isna(cfo_vs_pat):
        if cfo_vs_pat >= 100:
            score += 10
        elif cfo_vs_pat >= 80:
            score += 8
        elif cfo_vs_pat >= 60:
            score += 5

    # Shareholding unavailable in yfinance -> neutral partial score
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

    fundamentals = {
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
        "roce": roce,
        "debt_to_equity": debt_to_equity,
        "opm": opm_pct,
        "npm": profit_margin * 100 if not pd.isna(profit_margin) else np.nan,
        "cfo": cfo,
        "fcf": fcf,
        "cfo_vs_pat": cfo_vs_pat,
        "promoter_holding": promoter,
        "pledge": pledge,
        "pe": pe,
        "pb": pb,
        "fundamental_score": min(score, 100),
    }
    return fundamentals


def technical_analysis(df):
    df = add_indicators(df)
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    price = safe_num(latest["Close"])
    ema20 = safe_num(latest["EMA20"])
    sma50 = safe_num(latest["SMA50"])
    sma200 = safe_num(latest["SMA200"])
    rsi = safe_num(latest["RSI14"])
    macd = safe_num(latest["MACD"])
    macd_signal = safe_num(latest["MACD_SIGNAL"])
    volume = safe_num(latest["Volume"])
    vol20 = safe_num(latest["VOL20"])

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
    if price > support and price < resistance:
        structure_score = 8
    if price >= resistance * 0.98:
        structure_score = 15
    elif price >= (support + resistance) / 2:
        structure_score = 10

    volume_score = 0
    if vol20 > 0:
        if volume >= 1.5 * vol20:
            volume_score = 15
        elif volume >= 1.1 * vol20:
            volume_score = 10
        else:
            volume_score = 5

    rsi_score = 0
    if rsi >= 60:
        rsi_score = 10
    elif rsi >= 50:
        rsi_score = 7
    elif rsi >= 40:
        rsi_score = 4

    macd_score = 10 if macd > macd_signal else 4

    # Relative strength proxy vs 90-day return of NIFTY 50
    rs_score = 5
    try:
        nifty = yf.download("^NSEI", period="6mo", interval="1d", auto_adjust=True, progress=False)
        stock_ret = ((df["Close"].iloc[-1] / df["Close"].iloc[-90]) - 1) * 100 if len(df) >= 90 else ((df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1) * 100
        nifty_ret = ((nifty["Close"].iloc[-1] / nifty["Close"].iloc[-90]) - 1) * 100 if len(nifty) >= 90 else ((nifty["Close"].iloc[-1] / nifty["Close"].iloc[0]) - 1) * 100
        if stock_ret > nifty_ret + 5:
            rs_score = 10
        elif stock_ret > nifty_ret:
            rs_score = 8
        elif stock_ret > nifty_ret - 5:
            rs_score = 5
        else:
            rs_score = 2
    except:
        stock_ret = np.nan
        nifty_ret = np.nan

    risk_reward_score = 0
    stop_loss = max(support, sma50 if not np.isnan(sma50) else support)
    target1 = resistance
    target2 = resistance * 1.08
    risk = max(price - stop_loss, 0.01)
    reward = max(target1 - price, 0)
    rr = reward / risk if risk > 0 else 0
    if rr >= 2:
        risk_reward_score = 5
    elif rr >= 1.2:
        risk_reward_score = 3
    else:
        risk_reward_score = 1

    technical_score = min(trend_score + ma_score + structure_score + volume_score + rsi_score + macd_score + rs_score + risk_reward_score, 100)

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
        "stock_ret_90d": stock_ret if 'stock_ret' in locals() else np.nan,
        "nifty_ret_90d": nifty_ret if 'nifty_ret' in locals() else np.nan,
        "entry_zone": f"{price * 0.98:.2f} - {price * 1.01:.2f}",
        "stop_loss": stop_loss,
        "target1": target1,
        "target2": target2,
        "rr": rr,
        "technical_score": technical_score,
    }


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


def create_chart(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"
    ))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], mode="lines", name="EMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], mode="lines", name="SMA50"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA200"], mode="lines", name="SMA200"))
    fig.update_layout(title=f"{ticker} Price Chart", xaxis_rangeslider_visible=False, height=600)
    return fig


# -----------------------------
# UI
# -----------------------------
st.title("📊 STOCK ANALYSIS PRO APP V1")
st.caption("Fundamental + Technical + Scoring + Buy/Hold/Avoid | Single File Streamlit App")

with st.sidebar:
    st.header("⚙️ Settings")
    ticker = st.text_input("Enter Stock Ticker", value="RELIANCE.NS")
    period = st.selectbox("Price History Period", ["6mo", "1y", "2y", "5y"], index=1)
    run = st.button("🚀 Analyze Stock", use_container_width=True)
    st.markdown("---")
    st.info("For Indian stocks use NSE format, e.g. RELIANCE.NS, TCS.NS, INFY.NS")

if run:
    try:
        with st.spinner("Fetching data and running analysis..."):
            stock = yf.Ticker(ticker)
            hist = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False)

            if hist.empty:
                st.error("No price data found. Please check the ticker symbol.")
                st.stop()

            fdata = fundamental_analysis(stock)
            tdata = technical_analysis(hist)

            final_score = round((fdata["fundamental_score"] * 0.60) + (tdata["technical_score"] * 0.40), 2)
            verdict = final_rating(final_score)

        # Top summary
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Price", format_num(fdata["current_price"]))
        c2.metric("Fundamental Score", f"{fdata['fundamental_score']}/100")
        c3.metric("Technical Score", f"{tdata['technical_score']}/100")
        c4.metric("Final Score", f"{final_score}/100")

        st.success(f"FINAL VERDICT: {verdict}")

        # Company + chart
        left, right = st.columns([1, 2])
        with left:
            st.subheader("🏢 Company Snapshot")
            snapshot = pd.DataFrame({
                "Field": ["Company", "Sector", "Industry", "Market Cap", "52W High", "52W Low", "PE", "PB"],
                "Value": [
                    fdata["company"], fdata["sector"], fdata["industry"],
                    format_num(fdata["market_cap"]), format_num(fdata["52w_high"]), format_num(fdata["52w_low"]),
                    format_num(fdata["pe"]), format_num(fdata["pb"])
                ]
            })
            st.dataframe(snapshot, use_container_width=True, hide_index=True)

        with right:
            st.subheader("📈 Technical Price Chart")
            st.plotly_chart(create_chart(tdata["df"], ticker), use_container_width=True)

        # Fundamental section
        st.subheader("📘 Fundamental Analysis")
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            st.dataframe(pd.DataFrame({
                "Metric": [
                    "Sales Growth 3Y CAGR", "Profit Growth 3Y CAGR", "Quarterly Sales YoY", "Quarterly Profit YoY",
                    "ROE", "Debt to Equity", "OPM", "NPM"
                ],
                "Value": [
                    format_pct(fdata["sales_growth_3y"]), format_pct(fdata["profit_growth_3y"]),
                    format_pct(fdata["quarterly_sales_yoy"]), format_pct(fdata["quarterly_profit_yoy"]),
                    format_pct(fdata["roe"]), format_num(fdata["debt_to_equity"]),
                    format_pct(fdata["opm"]), format_pct(fdata["npm"])
                ]
            }), use_container_width=True, hide_index=True)

        with fcol2:
            st.dataframe(pd.DataFrame({
                "Metric": ["Operating Cash Flow", "Free Cash Flow", "CFO vs PAT", "Promoter Holding", "Pledge", "Fundamental Score"],
                "Value": [
                    format_num(fdata["cfo"]), format_num(fdata["fcf"]), format_pct(fdata["cfo_vs_pat"]),
                    "N/A (Yahoo limitation)", fdata["pledge"], f"{fdata['fundamental_score']}/100"
                ]
            }), use_container_width=True, hide_index=True)

        # Technical section
        st.subheader("📙 Technical Analysis")
        tcol1, tcol2 = st.columns(2)
        with tcol1:
            st.dataframe(pd.DataFrame({
                "Metric": ["Trend", "EMA20", "SMA50", "SMA200", "RSI(14)", "MACD", "MACD Signal"],
                "Value": [
                    tdata["trend"], format_num(tdata["ema20"]), format_num(tdata["sma50"]),
                    format_num(tdata["sma200"]), format_num(tdata["rsi"]), format_num(tdata["macd"]), format_num(tdata["macd_signal"])
                ]
            }), use_container_width=True, hide_index=True)

        with tcol2:
            st.dataframe(pd.DataFrame({
                "Metric": ["Support", "Resistance", "90D Stock Return", "90D Nifty Return", "Entry Zone", "Stop Loss", "Target 1", "Target 2", "Risk/Reward", "Technical Score"],
                "Value": [
                    format_num(tdata["support"]), format_num(tdata["resistance"]),
                    format_pct(tdata["stock_ret_90d"]), format_pct(tdata["nifty_ret_90d"]),
                    tdata["entry_zone"], format_num(tdata["stop_loss"]), format_num(tdata["target1"]),
                    format_num(tdata["target2"]), f"{tdata['rr']:.2f}", f"{tdata['technical_score']}/100"
                ]
            }), use_container_width=True, hide_index=True)

        # Final decision
        st.subheader("🧠 Final Decision Engine")
        decision_df = pd.DataFrame({
            "Field": ["Fundamental Weight", "Technical Weight", "Combined Score", "Final Verdict", "Suggested Horizon", "Risk Note"],
            "Value": [
                "60%", "40%", f"{final_score}/100", verdict,
                "Long-term / Positional" if final_score >= 65 else "Watchlist / Avoid",
                "Use stop-loss discipline. This is a model-based analysis, not investment advice."
            ]
        })
        st.dataframe(decision_df, use_container_width=True, hide_index=True)

        # Export summary
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

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Try another ticker like RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS")
else:
    st.markdown("""
### ✅ What this app does
- Fundamental analysis (Sales, Profit, ROE, Debt, Margins, Cash Flow)
- Technical analysis (Trend, EMA20, SMA50, SMA200, RSI, MACD, Support/Resistance)
- Combined scoring model (60% Fundamental + 40% Technical)
- Final verdict: Strong Buy / Buy on Dips / Watchlist / Avoid
- Copy-ready client summary

### ▶️ How to run
1. Save this file as `app.py`
2. Install packages:
   ```bash
   pip install streamlit yfinance pandas numpy plotly
   ```
3. Run:
   ```bash
   streamlit run app.py
   ```
4. Use Indian tickers like: `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `HDFCBANK.NS`

### ⚠️ Important
- Yahoo Finance data has limitations for some Indian fundamental fields.
- Promoter holding / pledge may show N/A.
- For production-grade advisory, you can later connect Screener / NSE / manual CSV imports.
""")

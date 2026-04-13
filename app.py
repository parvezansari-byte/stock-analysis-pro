import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="NSE Stock Intelligence Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# STYLES
# =========================================================
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #94a3b8;
        margin-bottom: 1rem;
    }
    .good-box {
        padding: 1rem;
        border-radius: 12px;
        background: rgba(22,163,74,0.18);
        border: 1px solid rgba(22,163,74,0.35);
        color: #86efac;
        font-weight: 700;
    }
    .warn-box {
        padding: 1rem;
        border-radius: 12px;
        background: rgba(245,158,11,0.15);
        border: 1px solid rgba(245,158,11,0.35);
        color: #fcd34d;
        font-weight: 700;
    }
    .bad-box {
        padding: 1rem;
        border-radius: 12px;
        background: rgba(239,68,68,0.15);
        border: 1px solid rgba(239,68,68,0.35);
        color: #fca5a5;
        font-weight: 700;
    }
    .info-box {
        padding: 0.8rem;
        border-radius: 12px;
        background: rgba(59,130,246,0.15);
        border: 1px solid rgba(59,130,246,0.35);
        color: #93c5fd;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# CONSTANTS
# =========================================================
QUICK_LIST = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "SBIN", "AXISBANK", "KOTAKBANK", "LT", "ITC",
    "HINDUNILVR", "BHARTIARTL", "ASIANPAINT", "SUNPHARMA", "MARUTI"
]

SECTOR_PACKS = {
    "Nifty Core": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "LT"],
    "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK"],
    "IT": ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM"],
    "Auto": ["MARUTI", "TATAMOTORS", "M&M", "EICHERMOT", "HEROMOTOCO"],
    "Pharma": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "LUPIN"]
}

# =========================================================
# HELPERS
# =========================================================
def safe_float(x, default=np.nan):
    try:
        if x is None:
            return default
        return float(x)
    except:
        return default

def fmt(x, decimals=2):
    if pd.isna(x):
        return "N/A"
    return f"{x:,.{decimals}f}"

def get_nse_symbol(symbol: str):
    symbol = str(symbol).strip().upper().replace(".NS", "")
    return f"{symbol}.NS"

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_data(symbol: str, period: str = "1y"):
    try:
        ticker = yf.Ticker(get_nse_symbol(symbol))
        hist = ticker.history(period=period, auto_adjust=False)

        if hist is None or hist.empty:
            hist = ticker.history(period="6mo", auto_adjust=False)

        if hist is None or hist.empty:
            return None, None, "No price data available."

        hist = hist.dropna(subset=["Open", "High", "Low", "Close"])
        if hist.empty:
            return None, None, "Price data became empty after cleaning."

        try:
            info = ticker.info
            if not isinstance(info, dict):
                info = {}
        except:
            info = {}

        return hist, info, None

    except Exception as e:
        return None, None, f"Data fetch failed: {str(e)}"

def add_indicators(df):
    df = df.copy()

    # Moving averages
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()

    # RSI
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI14"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # Bollinger
    mid = df["Close"].rolling(20).mean()
    std = df["Close"].rolling(20).std()
    df["BB_UPPER"] = mid + 2 * std
    df["BB_LOWER"] = mid - 2 * std

    # ATR
    prev_close = df["Close"].shift(1)
    tr1 = df["High"] - df["Low"]
    tr2 = (df["High"] - prev_close).abs()
    tr3 = (df["Low"] - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["ATR14"] = tr.rolling(14).mean()

    return df

def score_fundamentals(info):
    scores = []
    notes = []

    pe = safe_float(info.get("trailingPE"))
    if pd.isna(pe):
        pe = safe_float(info.get("forwardPE"))

    pb = safe_float(info.get("priceToBook"))
    roe = safe_float(info.get("returnOnEquity"))
    debt_equity = safe_float(info.get("debtToEquity"))
    profit_margin = safe_float(info.get("profitMargins"))
    revenue_growth = safe_float(info.get("revenueGrowth"))

    # PE
    if not pd.isna(pe):
        if 0 < pe <= 18:
            scores.append(100)
        elif pe <= 25:
            scores.append(80)
        elif pe <= 35:
            scores.append(60)
        elif pe <= 50:
            scores.append(40)
        else:
            scores.append(20)
        notes.append(("PE", pe))

    # PB
    if not pd.isna(pb):
        if pb <= 2:
            scores.append(100)
        elif pb <= 4:
            scores.append(80)
        elif pb <= 6:
            scores.append(60)
        else:
            scores.append(30)
        notes.append(("P/B", pb))

    # ROE
    if not pd.isna(roe):
        roe_pct = roe * 100 if roe < 5 else roe
        if roe_pct >= 20:
            scores.append(100)
        elif roe_pct >= 15:
            scores.append(85)
        elif roe_pct >= 10:
            scores.append(65)
        else:
            scores.append(35)
        notes.append(("ROE %", roe_pct))

    # Debt/Equity
    if not pd.isna(debt_equity):
        if debt_equity <= 0.5:
            scores.append(100)
        elif debt_equity <= 1.0:
            scores.append(75)
        elif debt_equity <= 2.0:
            scores.append(50)
        else:
            scores.append(20)
        notes.append(("Debt/Equity", debt_equity))

    # Profit Margin
    if not pd.isna(profit_margin):
        pm = profit_margin * 100 if profit_margin < 5 else profit_margin
        if pm >= 20:
            scores.append(100)
        elif pm >= 10:
            scores.append(75)
        elif pm >= 5:
            scores.append(55)
        else:
            scores.append(30)
        notes.append(("Profit Margin %", pm))

    # Revenue Growth
    if not pd.isna(revenue_growth):
        rg = revenue_growth * 100 if revenue_growth < 5 else revenue_growth
        if rg >= 15:
            scores.append(100)
        elif rg >= 8:
            scores.append(75)
        elif rg >= 0:
            scores.append(55)
        else:
            scores.append(25)
        notes.append(("Revenue Growth %", rg))

    if len(scores) == 0:
        return 50.0, "Limited Yahoo Finance data. Neutral fallback used.", notes

    return round(float(np.mean(scores)), 1), f"Based on {len(scores)} available metrics", notes

def score_technical(df):
    if df is None or df.empty or len(df) < 50:
        return 45.0, "Not enough data", "Neutral"

    last = df.iloc[-1]

    close = safe_float(last["Close"])
    sma20 = safe_float(last["SMA20"])
    sma50 = safe_float(last["SMA50"])
    sma200 = safe_float(last["SMA200"])
    rsi = safe_float(last["RSI14"])
    macd = safe_float(last["MACD"])
    macd_signal = safe_float(last["MACD_SIGNAL"])

    scores = []
    reasons = []

    # Price vs averages
    if not pd.isna(close) and not pd.isna(sma20):
        scores.append(100 if close > sma20 else 35)
        reasons.append("Above 20DMA" if close > sma20 else "Below 20DMA")

    if not pd.isna(close) and not pd.isna(sma50):
        scores.append(100 if close > sma50 else 35)
        reasons.append("Above 50DMA" if close > sma50 else "Below 50DMA")

    if not pd.isna(close) and not pd.isna(sma200):
        scores.append(100 if close > sma200 else 20)
        reasons.append("Above 200DMA" if close > sma200 else "Below 200DMA")

    # MA alignment
    if not pd.isna(sma20) and not pd.isna(sma50) and not pd.isna(sma200):
        if sma20 > sma50 > sma200:
            scores.append(100)
            reasons.append("Bullish alignment")
        elif sma20 > sma50:
            scores.append(70)
            reasons.append("Short-term bullish")
        else:
            scores.append(35)
            reasons.append("Weak alignment")

    # RSI
    if not pd.isna(rsi):
        if 45 <= rsi <= 65:
            scores.append(90)
            reasons.append("Healthy RSI")
        elif 35 <= rsi < 45 or 65 < rsi <= 75:
            scores.append(65)
            reasons.append("Moderate RSI")
        elif rsi < 35:
            scores.append(55)
            reasons.append("Oversold RSI")
        else:
            scores.append(40)
            reasons.append("Overheated RSI")

    # MACD
    if not pd.isna(macd) and not pd.isna(macd_signal):
        scores.append(85 if macd > macd_signal else 35)
        reasons.append("MACD bullish" if macd > macd_signal else "MACD bearish")

    if len(scores) == 0:
        return 45.0, "Indicators unavailable", "Neutral"

    score = round(float(np.mean(scores)), 1)

    trend = "Neutral"
    if not pd.isna(close) and not pd.isna(sma50) and not pd.isna(sma200):
        if close > sma50 > sma200:
            trend = "Strong Uptrend"
        elif close > sma50:
            trend = "Uptrend"
        elif close < sma50 < sma200:
            trend = "Strong Downtrend"
        else:
            trend = "Weak / Sideways"

    return score, ", ".join(reasons[:4]), trend

def support_resistance(df):
    if df is None or df.empty or len(df) < 30:
        return np.nan, np.nan

    recent = df.tail(30)
    return recent["Low"].min(), recent["High"].max()

def get_verdict(fund_score, tech_score, combined):
    if combined >= 80 and tech_score >= 70:
        return "🔥 STRONG BUY / HIGH QUALITY", "good"
    elif combined >= 68 and tech_score >= 60:
        return "✅ BUY / ACCUMULATE", "good"
    elif combined >= 55:
        return "🟡 HOLD / WATCHLIST", "warn"
    elif combined >= 42:
        return "⚠️ WAIT / AVOID FRESH ENTRY", "warn"
    else:
        return "❌ AVOID / WEAK SETUP", "bad"

def analyze_stock(symbol, period="1y", mode="Balanced"):
    hist, info, err = fetch_data(symbol, period)
    if err:
        return {"error": err}

    df = add_indicators(hist)

    last_close = safe_float(df["Close"].iloc[-1])
    prev_close = safe_float(df["Close"].iloc[-2]) if len(df) > 1 else np.nan
    change = last_close - prev_close if not pd.isna(last_close) and not pd.isna(prev_close) else np.nan
    change_pct = (change / prev_close * 100) if not pd.isna(change) and prev_close not in [0, np.nan] else np.nan

    fund_score, fund_note, fund_details = score_fundamentals(info)
    tech_score, tech_note, trend = score_technical(df)

    if mode == "Long-Term":
        fw, tw = 0.65, 0.35
    elif mode == "Swing":
        fw, tw = 0.30, 0.70
    else:
        fw, tw = 0.50, 0.50

    combined = round((fund_score * fw) + (tech_score * tw), 1)

    support, resistance = support_resistance(df)
    atr = safe_float(df["ATR14"].iloc[-1]) if "ATR14" in df.columns else np.nan

    stop_loss = round(last_close - 1.2 * atr, 2) if not pd.isna(last_close) and not pd.isna(atr) else np.nan
    target1 = round(last_close + 1.5 * atr, 2) if not pd.isna(last_close) and not pd.isna(atr) else np.nan
    target2 = round(last_close + 3.0 * atr, 2) if not pd.isna(last_close) and not pd.isna(atr) else np.nan

    verdict, verdict_type = get_verdict(fund_score, tech_score, combined)

    key_fund = {
        "Market Cap": safe_float(info.get("marketCap")),
        "PE": safe_float(info.get("trailingPE")) if not pd.isna(safe_float(info.get("trailingPE"))) else safe_float(info.get("forwardPE")),
        "P/B": safe_float(info.get("priceToBook")),
        "ROE %": (safe_float(info.get("returnOnEquity")) * 100) if not pd.isna(safe_float(info.get("returnOnEquity"))) else np.nan,
        "Debt/Equity": safe_float(info.get("debtToEquity")),
        "Profit Margin %": (safe_float(info.get("profitMargins")) * 100) if not pd.isna(safe_float(info.get("profitMargins"))) else np.nan,
    }

    return {
        "df": df,
        "last_close": last_close,
        "change": change,
        "change_pct": change_pct,
        "fund_score": fund_score,
        "fund_note": fund_note,
        "fund_details": fund_details,
        "tech_score": tech_score,
        "tech_note": tech_note,
        "trend": trend,
        "combined": combined,
        "support": support,
        "resistance": resistance,
        "stop_loss": stop_loss,
        "target1": target1,
        "target2": target2,
        "verdict": verdict,
        "verdict_type": verdict_type,
        "key_fund": key_fund
    }

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

    if "SMA20" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], mode="lines", name="20DMA"))
    if "SMA50" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], mode="lines", name="50DMA"))
    if "SMA200" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA200"], mode="lines", name="200DMA"))
    if "BB_UPPER" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_UPPER"], mode="lines", name="BB Upper", line=dict(dash="dot")))
    if "BB_LOWER" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_LOWER"], mode="lines", name="BB Lower", line=dict(dash="dot")))

    fig.update_layout(
        title=f"{symbol} - Price + Moving Averages + Bollinger Bands",
        template="plotly_dark",
        height=700,
        xaxis_rangeslider_visible=False
    )
    return fig

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## 📊 NSE Stock Intelligence Pro")
st.sidebar.caption("Simple + Stable + Streamlit Cloud Friendly")

module = st.sidebar.radio(
    "Choose Module",
    ["Single Stock Analysis", "Mini Screener", "Portfolio Ranker", "About"]
)

mode = st.sidebar.selectbox(
    "Analysis Mode",
    ["Balanced", "Long-Term", "Swing"]
)

quick_pick = st.sidebar.selectbox("Quick NSE Pick", QUICK_LIST, index=6)
manual_symbol = st.sidebar.text_input("Or Enter NSE Symbol", value=quick_pick)

period_map = {
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y"
}
period_label = st.sidebar.selectbox("Price History", list(period_map.keys()), index=1)
period = period_map[period_label]

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="main-title">📈 NSE Stock Intelligence Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Fundamental + Technical + Safer Cloud Runtime + Single File Deployment</div>', unsafe_allow_html=True)

# =========================================================
# SINGLE STOCK ANALYSIS
# =========================================================
if module == "Single Stock Analysis":
    symbol = manual_symbol.strip().upper().replace(".NS", "")

    if not symbol:
        st.warning("Please enter a valid NSE symbol.")
        st.stop()

    with st.spinner(f"Analyzing {symbol}.NS ..."):
        result = analyze_stock(symbol, period, mode)

    if "error" in result:
        st.error(result["error"])
        st.info("Try another NSE symbol or use 6 Months / 1 Year period.")
        st.stop()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        delta_text = f"{fmt(result['change'])} ({fmt(result['change_pct'])}%)" if not pd.isna(result["change"]) else "N/A"
        st.metric("Current Price", f"₹ {fmt(result['last_close'])}", delta_text)

    with c2:
        st.metric("Fundamental Score", f"{result['fund_score']}/100", result["fund_note"])

    with c3:
        st.metric("Technical Score", f"{result['tech_score']}/100", result["trend"])

    with c4:
        st.metric("Combined Score", f"{result['combined']}/100", f"Mode: {mode}")

    if result["verdict_type"] == "good":
        st.markdown(f'<div class="good-box">Verdict: {result["verdict"]}</div>', unsafe_allow_html=True)
    elif result["verdict_type"] == "warn":
        st.markdown(f'<div class="warn-box">Verdict: {result["verdict"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bad-box">Verdict: {result["verdict"]}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="info-box">Trend: {result["trend"]} | Technical Note: {result["tech_note"]}</div>', unsafe_allow_html=True)

    st.plotly_chart(build_chart(result["df"], symbol), use_container_width=True)

    z1, z2, z3, z4, z5 = st.columns(5)
    with z1:
        st.metric("Support", f"₹ {fmt(result['support'])}")
    with z2:
        st.metric("Resistance", f"₹ {fmt(result['resistance'])}")
    with z3:
        st.metric("Stop Loss", f"₹ {fmt(result['stop_loss'])}")
    with z4:
        st.metric("Target 1", f"₹ {fmt(result['target1'])}")
    with z5:
        st.metric("Target 2", f"₹ {fmt(result['target2'])}")

    st.subheader("📌 Key Fundamental Snapshot")
    fund_df = pd.DataFrame(
        [{"Metric": k, "Value": ("₹ " + f"{v/1e7:,.0f} Cr") if k == "Market Cap" and not pd.isna(v) else fmt(v)}
         for k, v in result["key_fund"].items()]
    )
    st.dataframe(fund_df, use_container_width=True, hide_index=True)

    st.subheader("🧠 Fundamental Metrics Used")
    if result["fund_details"]:
        fd = pd.DataFrame(result["fund_details"], columns=["Metric", "Value"])
        st.dataframe(fd, use_container_width=True, hide_index=True)
    else:
        st.info("No reliable fundamentals available from Yahoo Finance. Neutral fallback used.")

    st.subheader("⬇️ Download Price + Indicators")
    csv = result["df"].reset_index().to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV",
        data=csv,
        file_name=f"{symbol}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# =========================================================
# MINI SCREENER
# =========================================================
elif module == "Mini Screener":
    st.subheader("🔎 Mini Screener")

    pack = st.selectbox("Choose Sector Pack", list(SECTOR_PACKS.keys()))
    symbols = SECTOR_PACKS[pack]

    if st.button("Run Screener", use_container_width=True):
        rows = []
        progress = st.progress(0)

        for i, sym in enumerate(symbols):
            try:
                res = analyze_stock(sym, "1y", mode)
                if "error" not in res:
                    rows.append({
                        "Symbol": sym,
                        "Price": round(res["last_close"], 2) if not pd.isna(res["last_close"]) else np.nan,
                        "Fundamental Score": res["fund_score"],
                        "Technical Score": res["tech_score"],
                        "Combined Score": res["combined"],
                        "Trend": res["trend"],
                        "Verdict": res["verdict"]
                    })
            except:
                pass

            progress.progress((i + 1) / len(symbols))

        if rows:
            out = pd.DataFrame(rows).sort_values("Combined Score", ascending=False).reset_index(drop=True)
            st.dataframe(out, use_container_width=True, hide_index=True)

            csv = out.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Screener CSV",
                data=csv,
                file_name=f"{pack.replace(' ', '_').lower()}_screener.csv",
                mime="text/csv"
            )
        else:
            st.error("Could not analyze stocks right now. Please try again later.")

# =========================================================
# PORTFOLIO RANKER
# =========================================================
elif module == "Portfolio Ranker":
    st.subheader("📂 Portfolio Ranker")

    portfolio_input = st.text_area(
        "Enter comma-separated NSE symbols",
        value="HDFCBANK,ICICIBANK,SBIN,ITC,TCS"
    )

    if st.button("Rank Portfolio", use_container_width=True):
        symbols = [x.strip().upper().replace(".NS", "") for x in portfolio_input.split(",") if x.strip()]
        symbols = list(dict.fromkeys(symbols))[:12]

        if not symbols:
            st.warning("Please enter at least one valid symbol.")
            st.stop()

        rows = []
        progress = st.progress(0)

        for i, sym in enumerate(symbols):
            try:
                res = analyze_stock(sym, "1y", mode)
                if "error" not in res:
                    rows.append({
                        "Symbol": sym,
                        "Price": round(res["last_close"], 2) if not pd.isna(res["last_close"]) else np.nan,
                        "Fundamental Score": res["fund_score"],
                        "Technical Score": res["tech_score"],
                        "Combined Score": res["combined"],
                        "Trend": res["trend"],
                        "Verdict": res["verdict"]
                    })
            except:
                pass

            progress.progress((i + 1) / len(symbols))

        if rows:
            out = pd.DataFrame(rows).sort_values("Combined Score", ascending=False).reset_index(drop=True)
            st.dataframe(out, use_container_width=True, hide_index=True)

            st.markdown("### 🏆 Top 3")
            st.dataframe(out.head(3), use_container_width=True, hide_index=True)

            csv = out.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Portfolio Ranking CSV",
                data=csv,
                file_name=f"portfolio_rank_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.error("No portfolio symbols could be analyzed.")

# =========================================================
# ABOUT
# =========================================================
else:
    st.subheader("ℹ️ About")
    st.markdown("""
### NSE Stock Intelligence Pro

This is a **single-file Streamlit Cloud friendly app** for:

- Fundamental analysis
- Technical analysis
- Combined scoring
- Mini screener
- Portfolio ranker
- NSE (.NS) stocks

### Best for:
- Daily research
- Watchlist creation
- Client demo
- Advisory support

### Important:
This app uses **Yahoo Finance via yfinance**.  
Some NSE fundamentals may be incomplete.

### Disclaimer:
For educational and research purposes only. Not investment advice.
""")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption(
    f"Built with Streamlit + yfinance | NSE (.NS) | {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)

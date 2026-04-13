import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="NSE AI Advisor Master Pack V4.1",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM STYLES
# ============================================================
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background: rgba(17,24,39,0.85);
        border: 1px solid rgba(255,255,255,0.06);
        padding: 1rem;
        border-radius: 16px;
    }
    .good-box {
        padding: 1rem;
        border-radius: 14px;
        background: rgba(22, 163, 74, 0.18);
        border: 1px solid rgba(22, 163, 74, 0.35);
        color: #86efac;
        font-weight: 700;
    }
    .warn-box {
        padding: 1rem;
        border-radius: 14px;
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.35);
        color: #fcd34d;
        font-weight: 700;
    }
    .bad-box {
        padding: 1rem;
        border-radius: 14px;
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.35);
        color: #fca5a5;
        font-weight: 700;
    }
    .info-box {
        padding: 1rem;
        border-radius: 14px;
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.35);
        color: #93c5fd;
        font-weight: 600;
    }
    .small-note {
        color: #94a3b8;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONSTANTS
# ============================================================
QUICK_LIST = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "SBIN", "AXISBANK", "KOTAKBANK", "LT", "ITC",
    "HINDUNILVR", "BHARTIARTL", "ASIANPAINT", "SUNPHARMA", "MARUTI",
    "TITAN", "BAJFINANCE", "HCLTECH", "WIPRO", "ULTRACEMCO"
]

SECTOR_PACKS = {
    "Nifty Core 10": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "LT", "BHARTIARTL", "HINDUNILVR"],
    "Banking Leaders": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "INDUSINDBK"],
    "IT Leaders": ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM"],
    "Auto Leaders": ["MARUTI", "TATAMOTORS", "M&M", "EICHERMOT", "HEROMOTOCO"],
    "Pharma Leaders": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "LUPIN"],
    "FMCG Leaders": ["ITC", "HINDUNILVR", "NESTLEIND", "BRITANNIA", "DABUR"]
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def safe_float(x, default=np.nan):
    try:
        if x is None:
            return default
        return float(x)
    except:
        return default

def clamp(value, low=0, high=100):
    return max(low, min(high, value))

def fmt_num(x, decimals=2, prefix=""):
    if pd.isna(x):
        return "N/A"
    return f"{prefix}{x:,.{decimals}f}"

def get_nse_symbol(symbol: str) -> str:
    symbol = str(symbol).strip().upper().replace(".NS", "")
    return f"{symbol}.NS"

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_price_data(symbol: str, period: str = "1y"):
    """
    Safe price fetch for Streamlit Cloud.
    """
    try:
        ticker = yf.Ticker(get_nse_symbol(symbol))
        hist = ticker.history(period=period, auto_adjust=False)

        if hist is None or hist.empty:
            # fallback shorter period
            hist = ticker.history(period="6mo", auto_adjust=False)

        if hist is None or hist.empty:
            return None, "No price history available."

        # normalize columns
        hist = hist.copy()
        hist = hist.dropna(subset=["Open", "High", "Low", "Close"], how="any")
        if hist.empty:
            return None, "Price history is empty after cleaning."

        return hist, None
    except Exception as e:
        return None, f"Price fetch failed: {str(e)}"

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_info_safe(symbol: str):
    """
    Safe info fetch. yfinance .info can be slow/incomplete for NSE.
    We keep it guarded.
    """
    try:
        ticker = yf.Ticker(get_nse_symbol(symbol))
        info = ticker.info
        if not isinstance(info, dict):
            info = {}
        return info
    except:
        return {}

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # EMA / SMA
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
    bb_mid = df["Close"].rolling(20).mean()
    bb_std = df["Close"].rolling(20).std()
    df["BB_UPPER"] = bb_mid + 2 * bb_std
    df["BB_LOWER"] = bb_mid - 2 * bb_std

    # ATR
    prev_close = df["Close"].shift(1)
    tr1 = df["High"] - df["Low"]
    tr2 = (df["High"] - prev_close).abs()
    tr3 = (df["Low"] - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["ATR14"] = tr.rolling(14).mean()

    return df

def score_fundamentals(info: dict):
    """
    Normalized scoring:
    Only available metrics count.
    Avoid punishing missing NSE data too harshly.
    """
    checks = []
    details = []

    trailing_pe = safe_float(info.get("trailingPE"))
    forward_pe = safe_float(info.get("forwardPE"))
    pb = safe_float(info.get("priceToBook"))
    roe = safe_float(info.get("returnOnEquity"))
    profit_margin = safe_float(info.get("profitMargins"))
    debt_to_equity = safe_float(info.get("debtToEquity"))
    revenue_growth = safe_float(info.get("revenueGrowth"))
    earnings_growth = safe_float(info.get("earningsGrowth"))
    current_ratio = safe_float(info.get("currentRatio"))
    operating_margin = safe_float(info.get("operatingMargins"))

    # PE
    pe_used = trailing_pe if not pd.isna(trailing_pe) else forward_pe
    if not pd.isna(pe_used):
        if 0 < pe_used <= 18:
            checks.append(100)
        elif pe_used <= 25:
            checks.append(80)
        elif pe_used <= 35:
            checks.append(55)
        elif pe_used <= 50:
            checks.append(35)
        else:
            checks.append(15)
        details.append(("PE", pe_used))

    # PB
    if not pd.isna(pb):
        if pb <= 2:
            checks.append(100)
        elif pb <= 4:
            checks.append(80)
        elif pb <= 6:
            checks.append(60)
        elif pb <= 8:
            checks.append(40)
        else:
            checks.append(20)
        details.append(("P/B", pb))

    # ROE
    if not pd.isna(roe):
        roe_pct = roe * 100 if roe < 5 else roe
        if roe_pct >= 20:
            checks.append(100)
        elif roe_pct >= 15:
            checks.append(85)
        elif roe_pct >= 10:
            checks.append(65)
        elif roe_pct >= 5:
            checks.append(40)
        else:
            checks.append(20)
        details.append(("ROE %", roe_pct))

    # Profit Margin
    if not pd.isna(profit_margin):
        pm = profit_margin * 100 if profit_margin < 5 else profit_margin
        if pm >= 20:
            checks.append(100)
        elif pm >= 12:
            checks.append(80)
        elif pm >= 8:
            checks.append(65)
        elif pm >= 4:
            checks.append(45)
        else:
            checks.append(20)
        details.append(("Profit Margin %", pm))

    # Debt to Equity
    if not pd.isna(debt_to_equity):
        if debt_to_equity <= 0.3:
            checks.append(100)
        elif debt_to_equity <= 0.7:
            checks.append(85)
        elif debt_to_equity <= 1.5:
            checks.append(60)
        elif debt_to_equity <= 2.5:
            checks.append(35)
        else:
            checks.append(15)
        details.append(("Debt/Equity", debt_to_equity))

    # Revenue Growth
    if not pd.isna(revenue_growth):
        rg = revenue_growth * 100 if revenue_growth < 5 else revenue_growth
        if rg >= 20:
            checks.append(100)
        elif rg >= 12:
            checks.append(85)
        elif rg >= 6:
            checks.append(65)
        elif rg >= 0:
            checks.append(45)
        else:
            checks.append(20)
        details.append(("Revenue Growth %", rg))

    # Earnings Growth
    if not pd.isna(earnings_growth):
        eg = earnings_growth * 100 if earnings_growth < 5 else earnings_growth
        if eg >= 20:
            checks.append(100)
        elif eg >= 12:
            checks.append(85)
        elif eg >= 6:
            checks.append(65)
        elif eg >= 0:
            checks.append(45)
        else:
            checks.append(20)
        details.append(("Earnings Growth %", eg))

    # Current Ratio
    if not pd.isna(current_ratio):
        if current_ratio >= 2:
            checks.append(100)
        elif current_ratio >= 1.5:
            checks.append(80)
        elif current_ratio >= 1:
            checks.append(60)
        else:
            checks.append(35)
        details.append(("Current Ratio", current_ratio))

    # Operating Margin
    if not pd.isna(operating_margin):
        om = operating_margin * 100 if operating_margin < 5 else operating_margin
        if om >= 20:
            checks.append(100)
        elif om >= 12:
            checks.append(80)
        elif om >= 8:
            checks.append(65)
        elif om >= 4:
            checks.append(45)
        else:
            checks.append(20)
        details.append(("Operating Margin %", om))

    if len(checks) == 0:
        # if absolutely no data, neutral fallback instead of 0
        return 50.0, "Limited Yahoo fundamentals. Using neutral fallback.", details

    score = round(float(np.mean(checks)), 1)

    if len(checks) < 3:
        note = "Limited fundamental data available. Score based on few metrics."
    elif len(checks) < 6:
        note = "Partial fundamental data available. Score normalized on available metrics."
    else:
        note = "Good fundamental coverage from Yahoo Finance."

    return score, note, details

def technical_score(df: pd.DataFrame):
    if df is None or df.empty or len(df) < 50:
        return 40.0, "Insufficient data for robust technical scoring.", "Neutral"

    last = df.iloc[-1]
    checks = []
    reasons = []

    close = safe_float(last["Close"])
    sma20 = safe_float(last["SMA20"])
    sma50 = safe_float(last["SMA50"])
    sma200 = safe_float(last["SMA200"])
    rsi = safe_float(last["RSI14"])
    macd = safe_float(last["MACD"])
    macd_signal = safe_float(last["MACD_SIGNAL"])
    bb_upper = safe_float(last["BB_UPPER"])
    bb_lower = safe_float(last["BB_LOWER"])

    # Trend stack
    if not pd.isna(close) and not pd.isna(sma20):
        if close > sma20:
            checks.append(100)
            reasons.append("Price > 20DMA")
        else:
            checks.append(35)
            reasons.append("Price < 20DMA")

    if not pd.isna(close) and not pd.isna(sma50):
        if close > sma50:
            checks.append(100)
            reasons.append("Price > 50DMA")
        else:
            checks.append(35)
            reasons.append("Price < 50DMA")

    if not pd.isna(close) and not pd.isna(sma200):
        if close > sma200:
            checks.append(100)
            reasons.append("Price > 200DMA")
        else:
            checks.append(20)
            reasons.append("Price < 200DMA")

    # Moving average alignment
    if not pd.isna(sma20) and not pd.isna(sma50) and not pd.isna(sma200):
        if sma20 > sma50 > sma200:
            checks.append(100)
            reasons.append("Bullish MA alignment")
        elif sma20 > sma50:
            checks.append(70)
            reasons.append("Short-term bullish alignment")
        else:
            checks.append(35)
            reasons.append("Weak MA alignment")

    # RSI
    if not pd.isna(rsi):
        if 45 <= rsi <= 65:
            checks.append(90)
            reasons.append("Healthy RSI")
        elif 35 <= rsi < 45 or 65 < rsi <= 75:
            checks.append(65)
            reasons.append("Moderate RSI")
        elif rsi < 35:
            checks.append(55)  # could be oversold bounce
            reasons.append("RSI oversold")
        else:
            checks.append(40)
            reasons.append("RSI overheated")

    # MACD
    if not pd.isna(macd) and not pd.isna(macd_signal):
        if macd > macd_signal:
            checks.append(85)
            reasons.append("MACD bullish")
        else:
            checks.append(35)
            reasons.append("MACD bearish")

    # Bollinger positioning
    if not pd.isna(close) and not pd.isna(bb_upper) and not pd.isna(bb_lower):
        if bb_lower < close < bb_upper:
            checks.append(75)
            reasons.append("Within Bollinger range")
        else:
            checks.append(45)
            reasons.append("Outside Bollinger comfort zone")

    if len(checks) == 0:
        return 45.0, "Indicators unavailable.", "Neutral"

    score = round(float(np.mean(checks)), 1)

    # Trend label
    trend = "Neutral"
    if not pd.isna(close) and not pd.isna(sma50) and not pd.isna(sma200):
        if close > sma50 > sma200:
            trend = "Strong Uptrend"
        elif close > sma50:
            trend = "Uptrend"
        elif close < sma50 < sma200:
            trend = "Strong Downtrend"
        elif close < sma50:
            trend = "Weak / Downtrend"

    return score, ", ".join(reasons[:5]), trend

def support_resistance(df: pd.DataFrame):
    if df is None or df.empty or len(df) < 30:
        return np.nan, np.nan

    recent = df.tail(30)
    support = recent["Low"].min()
    resistance = recent["High"].max()
    return support, resistance

def verdict_logic(fund_score, tech_score, combined_score, trend):
    if combined_score >= 80 and tech_score >= 70:
        return "🔥 STRONG BUY / HIGH QUALITY SETUP", "good"
    elif combined_score >= 68 and tech_score >= 60:
        return "✅ BUY / ACCUMULATE ON DIPS", "good"
    elif combined_score >= 55:
        return "🟡 HOLD / WATCHLIST CANDIDATE", "warn"
    elif combined_score >= 42:
        return "⚠️ AVOID FRESH ENTRY / WAIT FOR BETTER SETUP", "warn"
    else:
        return "❌ AVOID / WEAK SETUP", "bad"

def advisor_weighting(mode: str):
    if mode == "Long-Term Investor":
        return 0.65, 0.35
    elif mode == "Swing Trader":
        return 0.30, 0.70
    elif mode == "Positional Trader":
        return 0.40, 0.60
    elif mode == "Conservative Wealth Builder":
        return 0.75, 0.25
    return 0.60, 0.40

def build_price_chart(df: pd.DataFrame, symbol: str):
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.75, 0.25]
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

    # MAs
    for col, name in [("SMA20", "20DMA"), ("SMA50", "50DMA"), ("SMA200", "200DMA")]:
        if col in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df[col],
                    mode="lines",
                    name=name
                ),
                row=1, col=1
            )

    # Bollinger
    if "BB_UPPER" in df.columns and "BB_LOWER" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["BB_UPPER"],
                mode="lines",
                name="BB Upper",
                line=dict(dash="dot")
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["BB_LOWER"],
                mode="lines",
                name="BB Lower",
                line=dict(dash="dot")
            ),
            row=1, col=1
        )

    # RSI
    if "RSI14" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df["RSI14"],
                mode="lines",
                name="RSI(14)"
            ),
            row=2, col=1
        )
        fig.add_hline(y=70, row=2, col=1, line_dash="dot")
        fig.add_hline(y=30, row=2, col=1, line_dash="dot")

    fig.update_layout(
        title=f"{symbol} - Price + Technical Analysis",
        template="plotly_dark",
        height=760,
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )
    return fig

def analyze_symbol(symbol: str, period: str, mode: str):
    hist, err = fetch_price_data(symbol, period)
    if err or hist is None:
        return {"error": err or "Unable to fetch price data."}

    if len(hist) < 30:
        return {"error": "Not enough historical data to analyze."}

    df = add_indicators(hist)
    info = fetch_info_safe(symbol)

    last_close = safe_float(df["Close"].iloc[-1])
    prev_close = safe_float(df["Close"].iloc[-2]) if len(df) > 1 else np.nan
    chg = last_close - prev_close if not pd.isna(last_close) and not pd.isna(prev_close) else np.nan
    chg_pct = (chg / prev_close * 100) if not pd.isna(chg) and prev_close not in [0, np.nan] else np.nan

    fund_score, fund_note, fund_details = score_fundamentals(info)
    tech_score, tech_note, trend = technical_score(df)

    fw, tw = advisor_weighting(mode)
    combined = round((fund_score * fw) + (tech_score * tw), 1)

    support, resistance = support_resistance(df)
    atr = safe_float(df["ATR14"].iloc[-1]) if "ATR14" in df.columns else np.nan

    # Safer target / stop zones
    if not pd.isna(last_close) and not pd.isna(atr):
        stop_loss = round(last_close - (1.2 * atr), 2)
        target1 = round(last_close + (1.5 * atr), 2)
        target2 = round(last_close + (3.0 * atr), 2)
    else:
        stop_loss = np.nan
        target1 = np.nan
        target2 = np.nan

    verdict, verdict_type = verdict_logic(fund_score, tech_score, combined, trend)

    # Key fundamentals display
    key_data = {
        "Market Cap": safe_float(info.get("marketCap")),
        "PE": safe_float(info.get("trailingPE")) if not pd.isna(safe_float(info.get("trailingPE"))) else safe_float(info.get("forwardPE")),
        "P/B": safe_float(info.get("priceToBook")),
        "ROE %": (safe_float(info.get("returnOnEquity")) * 100) if not pd.isna(safe_float(info.get("returnOnEquity"))) else np.nan,
        "Profit Margin %": (safe_float(info.get("profitMargins")) * 100) if not pd.isna(safe_float(info.get("profitMargins"))) else np.nan,
        "Debt/Equity": safe_float(info.get("debtToEquity")),
        "Revenue Growth %": (safe_float(info.get("revenueGrowth")) * 100) if not pd.isna(safe_float(info.get("revenueGrowth"))) else np.nan,
    }

    return {
        "df": df,
        "info": info,
        "last_close": last_close,
        "chg": chg,
        "chg_pct": chg_pct,
        "fund_score": fund_score,
        "fund_note": fund_note,
        "fund_details": fund_details,
        "tech_score": tech_score,
        "tech_note": tech_note,
        "trend": trend,
        "combined": combined,
        "support": support,
        "resistance": resistance,
        "atr": atr,
        "stop_loss": stop_loss,
        "target1": target1,
        "target2": target2,
        "verdict": verdict,
        "verdict_type": verdict_type,
        "key_data": key_data
    }

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("## 📊 NSE Stock Analysis Pro")
st.sidebar.caption("FINAL V4.1 STREAMLIT CLOUD SAFE HARDENED")

module = st.sidebar.radio(
    "Choose Module",
    ["Single Stock Analysis", "Mini Screener", "Portfolio Ranker", "About"]
)

advisor_mode = st.sidebar.selectbox(
    "AI Advisor Mode",
    ["Long-Term Investor", "Swing Trader", "Positional Trader", "Conservative Wealth Builder"]
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

# ============================================================
# HEADER
# ============================================================
st.markdown('<div class="main-title">📈 NSE AI Advisor Master Pack V4.1</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Fundamental + Technical + Normalized Scoring + Safer Cloud Runtime (NSE / Streamlit Cloud Hardened)</div>',
    unsafe_allow_html=True
)

# ============================================================
# SINGLE STOCK ANALYSIS
# ============================================================
if module == "Single Stock Analysis":
    symbol = manual_symbol.strip().upper().replace(".NS", "")

    if not symbol:
        st.warning("Please enter a valid NSE symbol.")
        st.stop()

    with st.spinner(f"Analyzing {symbol}.NS safely..."):
        result = analyze_symbol(symbol, period, advisor_mode)

    if "error" in result:
        st.error(result["error"])
        st.info("Try another NSE symbol or switch to a shorter price period like 6 Months / 1 Year.")
        st.stop()

    df = result["df"]

    # Metrics row
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Current Price",
            f"₹ {fmt_num(result['last_close'])}",
            f"{fmt_num(result['chg'])} ({fmt_num(result['chg_pct'])}%)" if not pd.isna(result["chg"]) else "N/A"
        )

    with c2:
        st.metric("Fundamental Score", f"{result['fund_score']}/100", result["fund_note"])

    with c3:
        st.metric("Technical Score", f"{result['tech_score']}/100", result["trend"])

    with c4:
        st.metric("Combined Score", f"{result['combined']}/100", f"Mode: {advisor_mode}")

    # Verdict
    if result["verdict_type"] == "good":
        st.markdown(f'<div class="good-box">Verdict: {result["verdict"]}</div>', unsafe_allow_html=True)
    elif result["verdict_type"] == "warn":
        st.markdown(f'<div class="warn-box">Verdict: {result["verdict"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bad-box">Verdict: {result["verdict"]}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="info-box">Trend: {result["trend"]} | Technical Note: {result["tech_note"]}</div>', unsafe_allow_html=True)

    # Chart
    fig = build_price_chart(df, symbol)
    st.plotly_chart(fig, use_container_width=True)

    # Zones
    z1, z2, z3, z4, z5 = st.columns(5)
    with z1:
        st.metric("Support", f"₹ {fmt_num(result['support'])}")
    with z2:
        st.metric("Resistance", f"₹ {fmt_num(result['resistance'])}")
    with z3:
        st.metric("Stop Loss", f"₹ {fmt_num(result['stop_loss'])}")
    with z4:
        st.metric("Target 1", f"₹ {fmt_num(result['target1'])}")
    with z5:
        st.metric("Target 2", f"₹ {fmt_num(result['target2'])}")

    # Key fundamentals
    st.subheader("📌 Key Fundamental Snapshot")
    k1, k2, k3, k4 = st.columns(4)
    keys = list(result["key_data"].items())

    for idx, (label, value) in enumerate(keys):
        col = [k1, k2, k3, k4][idx % 4]
        with col:
            if label == "Market Cap":
                if pd.isna(value):
                    st.metric(label, "N/A")
                else:
                    st.metric(label, f"₹ {value/1e7:,.0f} Cr")
            else:
                st.metric(label, fmt_num(value))

    # Fundamental detail table
    st.subheader("🧠 Normalized Fundamental Inputs Used")
    if result["fund_details"]:
        fd = pd.DataFrame(result["fund_details"], columns=["Metric", "Value"])
        st.dataframe(fd, use_container_width=True, hide_index=True)
    else:
        st.info("No reliable Yahoo Finance fundamentals were available. Neutral fallback used.")

    # Download latest enriched dataframe
    st.subheader("⬇️ Download Price + Indicators")
    download_df = df.reset_index().copy()
    csv = download_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV",
        data=csv,
        file_name=f"{symbol}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# ============================================================
# MINI SCREENER
# ============================================================
elif module == "Mini Screener":
    st.subheader("🔎 Mini Screener (NSE Sector Packs)")

    sector_choice = st.selectbox("Choose Pack", list(SECTOR_PACKS.keys()))
    screener_symbols = SECTOR_PACKS[sector_choice]

    if st.button("Run Mini Screener", use_container_width=True):
        rows = []

        progress = st.progress(0)
        status = st.empty()

        for i, sym in enumerate(screener_symbols):
            status.info(f"Analyzing {sym}...")
            try:
                res = analyze_symbol(sym, "1y", advisor_mode)
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

            progress.progress((i + 1) / len(screener_symbols))

        status.empty()

        if rows:
            out = pd.DataFrame(rows).sort_values("Combined Score", ascending=False).reset_index(drop=True)
            st.dataframe(out, use_container_width=True, hide_index=True)

            csv = out.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Screener CSV",
                data=csv,
                file_name=f"{sector_choice.replace(' ', '_').lower()}_screener.csv",
                mime="text/csv"
            )

            st.success("Mini Screener completed.")
        else:
            st.error("No stocks could be analyzed. Try again later or use Single Stock Analysis.")

# ============================================================
# PORTFOLIO RANKER
# ============================================================
elif module == "Portfolio Ranker":
    st.subheader("📂 Portfolio Ranker")

    st.markdown("Enter comma-separated NSE symbols (example: `HDFCBANK,ICICIBANK,SBIN,ITC,TCS`)")

    portfolio_input = st.text_area(
        "Portfolio Symbols",
        value="HDFCBANK,ICICIBANK,SBIN,ITC,TCS"
    )

    if st.button("Rank My Portfolio", use_container_width=True):
        symbols = [x.strip().upper().replace(".NS", "") for x in portfolio_input.split(",") if x.strip()]
        symbols = list(dict.fromkeys(symbols))[:15]  # limit to 15 for Cloud safety

        if not symbols:
            st.warning("Please enter at least one valid symbol.")
            st.stop()

        rows = []
        progress = st.progress(0)
        status = st.empty()

        for i, sym in enumerate(symbols):
            status.info(f"Ranking {sym}...")
            try:
                res = analyze_symbol(sym, "1y", advisor_mode)
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

        status.empty()

        if rows:
            out = pd.DataFrame(rows).sort_values("Combined Score", ascending=False).reset_index(drop=True)
            st.dataframe(out, use_container_width=True, hide_index=True)

            st.markdown("### 🏆 Top 3 Portfolio Candidates")
            st.dataframe(out.head(3), use_container_width=True, hide_index=True)

            csv = out.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Portfolio Ranking CSV",
                data=csv,
                file_name=f"portfolio_rank_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.error("No portfolio symbols could be analyzed. Try again later.")

# ============================================================
# ABOUT
# ============================================================
else:
    st.subheader("ℹ️ About This App")

    st.markdown("""
### FINAL V4.1 STREAMLIT CLOUD SAFE HARDENED

This version is designed specifically for:

- **NSE stock analysis**
- **Safer Streamlit Cloud runtime**
- **Better handling of missing Yahoo Finance data**
- **Normalized fundamental scoring**
- **Safer technical indicator calculations**
- **Mini screener**
- **Portfolio ranking**
- **Single-file GitHub + Streamlit deployment**

### Best Use Cases

- Daily research
- Watchlist creation
- Client demo
- Advisory support
- Shortlisting quality NSE ideas

### Important Note

This app uses **Yahoo Finance via yfinance**.  
Some NSE fundamentals may be incomplete.  
The app is designed to handle missing data better than earlier versions.

### Disclaimer

For educational and research purposes only. Not investment advice.
""")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption(
    f"Built with Streamlit + yfinance | NSE (.NS) | FINAL V4.1 STREAMLIT CLOUD SAFE HARDENED | {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)

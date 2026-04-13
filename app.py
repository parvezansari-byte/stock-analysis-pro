import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import math

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="NSE Stock Intelligence Pro MAX",
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
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #94a3b8;
        margin-bottom: 1rem;
    }
    .hero-box {
        padding: 1.2rem 1.4rem;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(14,116,144,0.25));
        border: 1px solid rgba(59,130,246,0.25);
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
    .pill {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        border: 1px solid rgba(148,163,184,0.25);
        margin-right: 0.4rem;
        margin-top: 0.25rem;
        color: #cbd5e1;
        font-size: 0.85rem;
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
def safe_num(x, default=np.nan):
    try:
        if x is None:
            return default
        if isinstance(x, str) and x.strip() == "":
            return default
        v = float(x)
        if math.isinf(v):
            return default
        return v
    except:
        return default

def fmt(x, decimals=2):
    if pd.isna(x):
        return "N/A"
    return f"{x:,.{decimals}f}"

def get_nse_symbol(symbol: str):
    symbol = str(symbol).strip().upper().replace(".NS", "")
    return f"{symbol}.NS"

def get_safe_series_value(df, row_name):
    try:
        if df is None or df.empty:
            return np.nan
        if row_name not in df.index:
            return np.nan
        row = df.loc[row_name]
        if isinstance(row, pd.Series):
            for val in row:
                if pd.notna(val):
                    return safe_num(val)
        return np.nan
    except:
        return np.nan

# =========================================================
# DATA FETCH
# =========================================================
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_full_stock_data(symbol: str, period: str = "1y"):
    try:
        ticker = yf.Ticker(get_nse_symbol(symbol))

        # Price history
        hist = ticker.history(period=period, auto_adjust=False)
        if hist is None or hist.empty:
            hist = ticker.history(period="6mo", auto_adjust=False)

        if hist is None or hist.empty:
            return None, None, None, None, None, None, None, "No price history found."

        hist = hist.dropna(subset=["Open", "High", "Low", "Close"])
        if hist.empty:
            return None, None, None, None, None, None, None, "Price history empty after cleaning."

        # info
        try:
            info = ticker.info
            if not isinstance(info, dict):
                info = {}
        except:
            info = {}

        # fast_info
        try:
            fast_info = ticker.fast_info
            if fast_info is None:
                fast_info = {}
        except:
            fast_info = {}

        # statements
        try:
            financials = ticker.financials
        except:
            financials = pd.DataFrame()

        try:
            balance_sheet = ticker.balance_sheet
        except:
            balance_sheet = pd.DataFrame()

        try:
            cashflow = ticker.cashflow
        except:
            cashflow = pd.DataFrame()

        try:
            q_financials = ticker.quarterly_financials
        except:
            q_financials = pd.DataFrame()

        try:
            q_balance_sheet = ticker.quarterly_balance_sheet
        except:
            q_balance_sheet = pd.DataFrame()

        extra_data = {
            "q_financials": q_financials,
            "q_balance_sheet": q_balance_sheet
        }

        return hist, info, fast_info, financials, balance_sheet, cashflow, extra_data, None

    except Exception as e:
        return None, None, None, None, None, None, None, f"Fetch failed: {str(e)}"

# =========================================================
# TECHNICAL INDICATORS
# =========================================================
def add_indicators(df):
    df = df.copy()

    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
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

    return df

# =========================================================
# FUNDAMENTAL EXTRACTION (ROBUST FIX)
# =========================================================
def extract_fundamentals_robust(symbol, info, fast_info, financials, balance_sheet, cashflow, extra_data=None):
    extra_data = extra_data or {}
    q_financials = extra_data.get("q_financials", pd.DataFrame())
    q_balance_sheet = extra_data.get("q_balance_sheet", pd.DataFrame())

    company_name = info.get("longName") or info.get("shortName") or symbol
    sector = info.get("sector")
    industry = info.get("industry")

    market_cap = safe_num(info.get("marketCap"))
    if pd.isna(market_cap):
        try:
            market_cap = safe_num(fast_info.get("market_cap"))
        except:
            pass

    current_price = safe_num(info.get("currentPrice"))
    if pd.isna(current_price):
        current_price = safe_num(info.get("regularMarketPrice"))
    if pd.isna(current_price):
        try:
            current_price = safe_num(fast_info.get("lastPrice"))
        except:
            pass

    pe = safe_num(info.get("trailingPE"))
    if pd.isna(pe):
        pe = safe_num(info.get("forwardPE"))

    pb = safe_num(info.get("priceToBook"))

    roe = safe_num(info.get("returnOnEquity"))
    if not pd.isna(roe) and roe < 5:
        roe = roe * 100

    debt_equity = safe_num(info.get("debtToEquity"))

    profit_margin = safe_num(info.get("profitMargins"))
    if not pd.isna(profit_margin) and profit_margin < 5:
        profit_margin = profit_margin * 100

    revenue_growth = safe_num(info.get("revenueGrowth"))
    if not pd.isna(revenue_growth) and revenue_growth < 5:
        revenue_growth = revenue_growth * 100

    book_value = safe_num(info.get("bookValue"))
    eps = safe_num(info.get("trailingEps"))
    dividend_yield = safe_num(info.get("dividendYield"))
    if not pd.isna(dividend_yield) and dividend_yield < 5:
        dividend_yield = dividend_yield * 100

    shares_outstanding = safe_num(info.get("sharesOutstanding"))

    net_income = get_safe_series_value(financials, "Net Income")
    if pd.isna(net_income):
        net_income = get_safe_series_value(financials, "Net Income Common Stockholders")

    total_revenue = get_safe_series_value(financials, "Total Revenue")
    if pd.isna(total_revenue):
        total_revenue = get_safe_series_value(q_financials, "Total Revenue")

    ebitda = get_safe_series_value(financials, "EBITDA")
    operating_income = get_safe_series_value(financials, "Operating Income")

    total_equity = get_safe_series_value(balance_sheet, "Stockholders Equity")
    if pd.isna(total_equity):
        total_equity = get_safe_series_value(balance_sheet, "Total Equity Gross Minority Interest")

    total_debt = get_safe_series_value(balance_sheet, "Total Debt")
    if pd.isna(total_debt):
        long_term_debt = get_safe_series_value(balance_sheet, "Long Term Debt")
        current_debt = get_safe_series_value(balance_sheet, "Current Debt")
        if pd.notna(long_term_debt) or pd.notna(current_debt):
            total_debt = np.nansum([long_term_debt, current_debt])

    cash = get_safe_series_value(balance_sheet, "Cash And Cash Equivalents")
    if pd.isna(cash):
        cash = get_safe_series_value(balance_sheet, "Cash Cash Equivalents And Short Term Investments")

    # Derived fallbacks
    if pd.isna(pb) and pd.notna(market_cap) and pd.notna(total_equity) and total_equity > 0:
        pb = market_cap / total_equity

    if pd.isna(roe) and pd.notna(net_income) and pd.notna(total_equity) and total_equity > 0:
        roe = (net_income / total_equity) * 100

    if pd.isna(debt_equity) and pd.notna(total_debt) and pd.notna(total_equity) and total_equity > 0:
        debt_equity = total_debt / total_equity

    if pd.isna(profit_margin) and pd.notna(net_income) and pd.notna(total_revenue) and total_revenue > 0:
        profit_margin = (net_income / total_revenue) * 100

    if pd.isna(book_value) and pd.notna(total_equity) and pd.notna(shares_outstanding) and shares_outstanding > 0:
        book_value = total_equity / shares_outstanding

    if pd.isna(eps) and pd.notna(net_income) and pd.notna(shares_outstanding) and shares_outstanding > 0:
        eps = net_income / shares_outstanding

    if pd.isna(pe) and pd.notna(current_price) and pd.notna(eps) and eps > 0:
        pe = current_price / eps

    if pd.isna(revenue_growth):
        try:
            if q_financials is not None and not q_financials.empty and "Total Revenue" in q_financials.index:
                row = q_financials.loc["Total Revenue"]
                vals = [safe_num(v) for v in row if pd.notna(v)]
                if len(vals) >= 2 and vals[1] not in [0, np.nan]:
                    revenue_growth = ((vals[0] - vals[1]) / abs(vals[1])) * 100
        except:
            pass

    return {
        "Company Name": company_name,
        "Sector": sector,
        "Industry": industry,
        "Market Cap": market_cap,
        "Current Price": current_price,
        "P/E Ratio": pe,
        "P/B Ratio": pb,
        "ROE %": roe,
        "Debt/Equity": debt_equity,
        "Profit Margin %": profit_margin,
        "Revenue Growth %": revenue_growth,
        "Book Value": book_value,
        "EPS": eps,
        "Dividend Yield %": dividend_yield,
        "Net Income": net_income,
        "Total Revenue": total_revenue,
        "EBITDA": ebitda,
        "Operating Income": operating_income,
        "Total Equity": total_equity,
        "Total Debt": total_debt,
        "Cash": cash
    }

# =========================================================
# SCORING
# =========================================================
def score_fundamentals_from_data(fd):
    scores = []

    pe = safe_num(fd.get("P/E Ratio"))
    pb = safe_num(fd.get("P/B Ratio"))
    roe = safe_num(fd.get("ROE %"))
    debt_equity = safe_num(fd.get("Debt/Equity"))
    profit_margin = safe_num(fd.get("Profit Margin %"))
    revenue_growth = safe_num(fd.get("Revenue Growth %"))

    if pd.notna(pe):
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

    if pd.notna(pb):
        if pb <= 2:
            scores.append(100)
        elif pb <= 4:
            scores.append(80)
        elif pb <= 6:
            scores.append(60)
        else:
            scores.append(30)

    if pd.notna(roe):
        if roe >= 20:
            scores.append(100)
        elif roe >= 15:
            scores.append(85)
        elif roe >= 10:
            scores.append(65)
        else:
            scores.append(35)

    if pd.notna(debt_equity):
        if debt_equity <= 0.5:
            scores.append(100)
        elif debt_equity <= 1.0:
            scores.append(75)
        elif debt_equity <= 2.0:
            scores.append(50)
        else:
            scores.append(20)

    if pd.notna(profit_margin):
        if profit_margin >= 20:
            scores.append(100)
        elif profit_margin >= 10:
            scores.append(75)
        elif profit_margin >= 5:
            scores.append(55)
        else:
            scores.append(30)

    if pd.notna(revenue_growth):
        if revenue_growth >= 15:
            scores.append(100)
        elif revenue_growth >= 8:
            scores.append(75)
        elif revenue_growth >= 0:
            scores.append(55)
        else:
            scores.append(25)

    if len(scores) == 0:
        return 50.0, "Fallback neutral score (limited fundamentals)"

    return round(float(np.mean(scores)), 1), f"Scored from {len(scores)} metrics"

def score_technical(df):
    if df is None or df.empty or len(df) < 50:
        return 45.0, "Not enough data", "Neutral"

    last = df.iloc[-1]

    close = safe_num(last["Close"])
    sma20 = safe_num(last["SMA20"])
    sma50 = safe_num(last["SMA50"])
    sma200 = safe_num(last["SMA200"])
    rsi = safe_num(last["RSI14"])
    macd = safe_num(last["MACD"])
    macd_signal = safe_num(last["MACD_SIGNAL"])

    scores = []
    reasons = []

    if pd.notna(close) and pd.notna(sma20):
        scores.append(100 if close > sma20 else 35)
        reasons.append("Above 20DMA" if close > sma20 else "Below 20DMA")

    if pd.notna(close) and pd.notna(sma50):
        scores.append(100 if close > sma50 else 35)
        reasons.append("Above 50DMA" if close > sma50 else "Below 50DMA")

    if pd.notna(close) and pd.notna(sma200):
        scores.append(100 if close > sma200 else 20)
        reasons.append("Above 200DMA" if close > sma200 else "Below 200DMA")

    if pd.notna(sma20) and pd.notna(sma50) and pd.notna(sma200):
        if sma20 > sma50 > sma200:
            scores.append(100)
            reasons.append("Bullish MA alignment")
        elif sma20 > sma50:
            scores.append(70)
            reasons.append("Short-term bullish")
        else:
            scores.append(35)
            reasons.append("Weak alignment")

    if pd.notna(rsi):
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

    if pd.notna(macd) and pd.notna(macd_signal):
        scores.append(85 if macd > macd_signal else 35)
        reasons.append("MACD bullish" if macd > macd_signal else "MACD bearish")

    if len(scores) == 0:
        return 45.0, "Indicators unavailable", "Neutral"

    score = round(float(np.mean(scores)), 1)

    trend = "Neutral"
    if pd.notna(close) and pd.notna(sma50) and pd.notna(sma200):
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

# =========================================================
# ANALYSIS ENGINE
# =========================================================
def analyze_stock(symbol, period="1y", mode="Balanced"):
    hist, info, fast_info, financials, balance_sheet, cashflow, extra_data, err = fetch_full_stock_data(symbol, period)

    if err:
        return {"error": err}

    df = add_indicators(hist)

    last_close = safe_num(df["Close"].iloc[-1])
    prev_close = safe_num(df["Close"].iloc[-2]) if len(df) > 1 else np.nan
    change = last_close - prev_close if pd.notna(last_close) and pd.notna(prev_close) else np.nan
    change_pct = (change / prev_close * 100) if pd.notna(change) and pd.notna(prev_close) and prev_close != 0 else np.nan

    fundamental_data = extract_fundamentals_robust(
        symbol=symbol,
        info=info,
        fast_info=fast_info,
        financials=financials,
        balance_sheet=balance_sheet,
        cashflow=cashflow,
        extra_data=extra_data
    )

    fund_score, fund_note = score_fundamentals_from_data(fundamental_data)
    tech_score, tech_note, trend = score_technical(df)

    if mode == "Long-Term":
        fw, tw = 0.65, 0.35
    elif mode == "Swing":
        fw, tw = 0.30, 0.70
    else:
        fw, tw = 0.50, 0.50

    combined = round((fund_score * fw) + (tech_score * tw), 1)

    support, resistance = support_resistance(df)
    atr = safe_num(df["ATR14"].iloc[-1]) if "ATR14" in df.columns else np.nan

    stop_loss = round(last_close - 1.2 * atr, 2) if pd.notna(last_close) and pd.notna(atr) else np.nan
    target1 = round(last_close + 1.5 * atr, 2) if pd.notna(last_close) and pd.notna(atr) else np.nan
    target2 = round(last_close + 3.0 * atr, 2) if pd.notna(last_close) and pd.notna(atr) else np.nan

    verdict, verdict_type = get_verdict(fund_score, tech_score, combined)

    return {
        "df": df,
        "last_close": last_close,
        "change": change,
        "change_pct": change_pct,
        "fund_score": fund_score,
        "fund_note": fund_note,
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
        "fundamental_data": fundamental_data
    }

# =========================================================
# CHARTS
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
        title=f"{symbol} - Price + MA + Bollinger Bands",
        template="plotly_dark",
        height=700,
        xaxis_rangeslider_visible=False
    )
    return fig

def build_rsi_chart(df, symbol):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI14"], mode="lines", name="RSI 14"))
    fig.add_hline(y=70, line_dash="dash")
    fig.add_hline(y=30, line_dash="dash")

    fig.update_layout(
        title=f"{symbol} - RSI (14)",
        template="plotly_dark",
        height=300
    )
    return fig

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## 📈 NSE Stock Intelligence Pro MAX")
st.sidebar.caption("Single-file • Cloud Safe • Fundamental Fix")

module = st.sidebar.radio(
    "Choose Module",
    ["Single Stock Analysis", "Mini Screener", "Portfolio Ranker", "About"]
)

mode = st.sidebar.selectbox(
    "Analysis Mode",
    ["Balanced", "Long-Term", "Swing"]
)

quick_pick = st.sidebar.selectbox("Quick NSE Pick", QUICK_LIST, index=0)
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
st.markdown("""
<div class="hero-box">
    <div class="main-title">📈 NSE Stock Intelligence Pro MAX</div>
    <div class="sub-title">Technical + Fundamental + Robust NSE Fallback + Screener + Portfolio Ranker</div>
    <span class="pill">Cloud Safe</span>
    <span class="pill">Single app.py</span>
    <span class="pill">Fundamental Fix</span>
    <span class="pill">NSE Ready</span>
</div>
""", unsafe_allow_html=True)

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

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        delta_text = f"{fmt(result['change'])} ({fmt(result['change_pct'])}%)" if pd.notna(result["change"]) else "N/A"
        st.metric("Current Price", f"₹ {fmt(result['last_close'])}", delta_text)

    with c2:
        st.metric("Fundamental Score", f"{result['fund_score']}/100", result["fund_note"])

    with c3:
        st.metric("Technical Score", f"{result['tech_score']}/100", result["trend"])

    with c4:
        st.metric("Combined Score", f"{result['combined']}/100", f"Mode: {mode}")

    with c5:
        st.metric("Verdict", result["verdict"].replace("🔥 ", "").replace("✅ ", "").replace("🟡 ", "").replace("⚠️ ", "").replace("❌ ", ""))

    if result["verdict_type"] == "good":
        st.markdown(f'<div class="good-box">Verdict: {result["verdict"]}</div>', unsafe_allow_html=True)
    elif result["verdict_type"] == "warn":
        st.markdown(f'<div class="warn-box">Verdict: {result["verdict"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bad-box">Verdict: {result["verdict"]}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="info-box">Trend: {result["trend"]} | Technical Note: {result["tech_note"]}</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Price Chart", "🏢 Fundamental Analysis", "🧠 Technical Details", "⬇️ Export"])

    with tab1:
        st.plotly_chart(build_chart(result["df"], symbol), use_container_width=True)
        st.plotly_chart(build_rsi_chart(result["df"], symbol), use_container_width=True)

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

    with tab2:
        st.subheader("🏢 Fundamental Analysis")

        fd = result["fundamental_data"]

        display_rows = []
        rupee_cr_fields = ["Market Cap", "Net Income", "Total Revenue", "EBITDA", "Operating Income", "Total Equity", "Total Debt", "Cash"]

        for k, v in fd.items():
            if k in rupee_cr_fields:
                if pd.notna(v):
                    display_rows.append([k, f"₹ {v/1e7:,.2f} Cr"])
                else:
                    display_rows.append([k, "N/A"])
            elif k in ["ROE %", "Profit Margin %", "Revenue Growth %", "Dividend Yield %"]:
                display_rows.append([k, f"{v:.2f}%" if pd.notna(v) else "N/A"])
            elif k == "Current Price":
                display_rows.append([k, f"₹ {v:,.2f}" if pd.notna(v) else "N/A"])
            else:
                if isinstance(v, (int, float, np.floating)) and pd.notna(v):
                    display_rows.append([k, f"{v:,.2f}"])
                else:
                    display_rows.append([k, str(v) if v is not None else "N/A"])

        fundamental_df = pd.DataFrame(display_rows, columns=["Metric", "Value"])
        st.dataframe(fundamental_df, use_container_width=True, hide_index=True)

        st.info("Note: NSE fundamentals depend on Yahoo Finance availability. This version uses multi-source fallback to reduce N/A values.")

    with tab3:
        df = result["df"]
        last = df.iloc[-1]

        tech_rows = [
            ["Close", f"₹ {fmt(last['Close'])}"],
            ["20 DMA", f"₹ {fmt(last['SMA20'])}"],
            ["50 DMA", f"₹ {fmt(last['SMA50'])}"],
            ["200 DMA", f"₹ {fmt(last['SMA200'])}"],
            ["RSI 14", fmt(last["RSI14"])],
            ["MACD", fmt(last["MACD"])],
            ["MACD Signal", fmt(last["MACD_SIGNAL"])],
            ["BB Upper", f"₹ {fmt(last['BB_UPPER'])}"],
            ["BB Lower", f"₹ {fmt(last['BB_LOWER'])}"],
            ["ATR 14", fmt(last["ATR14"])]
        ]

        tech_df = pd.DataFrame(tech_rows, columns=["Indicator", "Value"])
        st.dataframe(tech_df, use_container_width=True, hide_index=True)

    with tab4:
        st.subheader("⬇️ Download Price + Indicators")
        csv = result["df"].reset_index().to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Full Analysis CSV",
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
                        "Price": round(res["last_close"], 2) if pd.notna(res["last_close"]) else np.nan,
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
        value="RELIANCE,HDFCBANK,ICICIBANK,SBIN,ITC"
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
                        "Price": round(res["last_close"], 2) if pd.notna(res["last_close"]) else np.nan,
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

            st.markdown("### 🏆 Top 3 Ranked")
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
### NSE Stock Intelligence Pro MAX

This is a **single-file Streamlit Cloud friendly app** for:

- Fundamental analysis with robust fallback
- Technical analysis
- Combined scoring
- Mini screener
- Portfolio ranker
- NSE (.NS) stocks

### Fundamental Fix Included
This version reduces **N/A problem for NSE stocks** by using:

- `ticker.info`
- `ticker.fast_info`
- `ticker.financials`
- `ticker.balance_sheet`
- `ticker.cashflow`
- derived ratios (P/B, ROE, Debt/Equity, Margin, PE)

### Best Use Cases
- Daily research
- Watchlist creation
- Client demo
- Advisory support

### Important
This app uses **Yahoo Finance via yfinance**.  
Some NSE fundamentals may still be incomplete depending on Yahoo source quality.

### Disclaimer
For educational and research purposes only. Not investment advice.
""")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption(
    f"Built with Streamlit + yfinance | NSE (.NS) | FINAL MAX SINGLE FILE | {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)

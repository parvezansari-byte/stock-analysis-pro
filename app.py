import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="FINAL V10.2 INSTITUTIONAL MASTER ELITE",
    page_icon="📈",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0b1220 0%, #111827 45%, #1e293b 100%);
        color: white;
    }
    .hero-card {
        background: linear-gradient(135deg, rgba(30,41,59,0.96), rgba(15,23,42,0.96));
        border: 1px solid rgba(148,163,184,0.12);
        padding: 22px;
        border-radius: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        margin-bottom: 16px;
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(30,41,59,0.92), rgba(17,24,39,0.92));
        border: 1px solid rgba(148,163,184,0.10);
        padding: 16px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.18);
    }
    .stock-card {
        background: linear-gradient(135deg, rgba(15,23,42,0.92), rgba(30,41,59,0.92));
        border: 1px solid rgba(59,130,246,0.14);
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
# NIFTY 50 + NIFTY NEXT 50 STOCK LIST
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
def safe_get(info, key, default=np.nan):
    try:
        val = info.get(key, default)
        if val is None:
            return default
        return val
    except:
        return default

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

def pct_change(series, days):
    if len(series) <= days:
        return np.nan
    return ((series.iloc[-1] / series.iloc[-days-1]) - 1) * 100

def score_fundamentals(info):
    score = 0
    pe = safe_get(info, "trailingPE")
    pb = safe_get(info, "priceToBook")
    roe = safe_get(info, "returnOnEquity")
    de = safe_get(info, "debtToEquity")
    margin = safe_get(info, "profitMargins")
    growth = safe_get(info, "revenueGrowth")
    current_ratio = safe_get(info, "currentRatio")
    div_yield = safe_get(info, "dividendYield")

    if pd.notna(pe):
        if pe < 20: score += 15
        elif pe < 30: score += 10
        elif pe < 50: score += 5

    if pd.notna(pb):
        if pb < 3: score += 10
        elif pb < 6: score += 6
        elif pb < 10: score += 3

    if pd.notna(roe):
        roe_pct = roe * 100 if roe < 5 else roe
        if roe_pct > 20: score += 20
        elif roe_pct > 15: score += 15
        elif roe_pct > 10: score += 10
        elif roe_pct > 5: score += 5

    if pd.notna(de):
        if de < 50: score += 15
        elif de < 100: score += 10
        elif de < 200: score += 5

    if pd.notna(margin):
        margin_pct = margin * 100 if margin < 5 else margin
        if margin_pct > 20: score += 15
        elif margin_pct > 10: score += 10
        elif margin_pct > 5: score += 5

    if pd.notna(growth):
        growth_pct = growth * 100 if growth < 5 else growth
        if growth_pct > 20: score += 15
        elif growth_pct > 10: score += 10
        elif growth_pct > 5: score += 5

    if pd.notna(current_ratio):
        if current_ratio > 1.5: score += 5
        elif current_ratio > 1: score += 3

    if pd.notna(div_yield):
        dy_pct = div_yield * 100 if div_yield < 5 else div_yield
        if dy_pct > 2: score += 5

    return min(score, 100)

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

    if pd.notna(sma20) and close > sma20: score += 15
    if pd.notna(sma50) and close > sma50: score += 20
    if pd.notna(sma200) and close > sma200: score += 25

    if pd.notna(rsi):
        if 45 <= rsi <= 65: score += 15
        elif 35 <= rsi <= 75: score += 8

    if pd.notna(macd) and pd.notna(macd_signal):
        if macd > macd_signal: score += 15

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
# PER-STOCK ANALYSIS HELPERS
# =========================
def get_fundamental_analysis_text(row):
    analysis = []

    pe = row.get("PE", np.nan)
    pb = row.get("PB", np.nan)
    roe = row.get("ROE", np.nan)
    de = row.get("Debt/Equity", np.nan)
    margin = row.get("Profit Margin", np.nan)
    growth = row.get("Revenue Growth", np.nan)
    div_yield = row.get("Dividend Yield", np.nan)
    fund_score = row.get("Fundamental Score", 0)

    if pd.notna(pe):
        if pe < 20:
            analysis.append(("PE Ratio", f"{pe:.2f}", "Attractive valuation (reasonably valued)"))
        elif pe < 35:
            analysis.append(("PE Ratio", f"{pe:.2f}", "Fair valuation"))
        else:
            analysis.append(("PE Ratio", f"{pe:.2f}", "Premium / expensive valuation"))
    else:
        analysis.append(("PE Ratio", "N/A", "Data not available"))

    if pd.notna(pb):
        if pb < 3:
            analysis.append(("PB Ratio", f"{pb:.2f}", "Healthy price-to-book valuation"))
        elif pb < 6:
            analysis.append(("PB Ratio", f"{pb:.2f}", "Acceptable premium"))
        else:
            analysis.append(("PB Ratio", f"{pb:.2f}", "Rich valuation vs book value"))
    else:
        analysis.append(("PB Ratio", "N/A", "Data not available"))

    if pd.notna(roe):
        if roe > 20:
            analysis.append(("ROE", f"{roe:.2f}%", "Excellent capital efficiency (elite quality)"))
        elif roe > 15:
            analysis.append(("ROE", f"{roe:.2f}%", "Strong business quality"))
        elif roe > 10:
            analysis.append(("ROE", f"{roe:.2f}%", "Average to good"))
        else:
            analysis.append(("ROE", f"{roe:.2f}%", "Weak or average quality"))
    else:
        analysis.append(("ROE", "N/A", "Data not available"))

    if pd.notna(de):
        if de < 50:
            analysis.append(("Debt/Equity", f"{de:.2f}", "Strong balance sheet / low leverage"))
        elif de < 100:
            analysis.append(("Debt/Equity", f"{de:.2f}", "Manageable leverage"))
        else:
            analysis.append(("Debt/Equity", f"{de:.2f}", "Higher debt risk - monitor carefully"))
    else:
        analysis.append(("Debt/Equity", "N/A", "Data not available"))

    if pd.notna(margin):
        if margin > 20:
            analysis.append(("Profit Margin", f"{margin:.2f}%", "Excellent profitability"))
        elif margin > 10:
            analysis.append(("Profit Margin", f"{margin:.2f}%", "Healthy profitability"))
        elif margin > 5:
            analysis.append(("Profit Margin", f"{margin:.2f}%", "Moderate profitability"))
        else:
            analysis.append(("Profit Margin", f"{margin:.2f}%", "Thin profitability"))
    else:
        analysis.append(("Profit Margin", "N/A", "Data not available"))

    if pd.notna(growth):
        if growth > 20:
            analysis.append(("Revenue Growth", f"{growth:.2f}%", "High growth business"))
        elif growth > 10:
            analysis.append(("Revenue Growth", f"{growth:.2f}%", "Healthy growth"))
        elif growth > 5:
            analysis.append(("Revenue Growth", f"{growth:.2f}%", "Moderate growth"))
        else:
            analysis.append(("Revenue Growth", f"{growth:.2f}%", "Low growth / mature business"))
    else:
        analysis.append(("Revenue Growth", "N/A", "Data not available"))

    if pd.notna(div_yield):
        if div_yield > 2:
            analysis.append(("Dividend Yield", f"{div_yield:.2f}%", "Good shareholder payout support"))
        elif div_yield > 0:
            analysis.append(("Dividend Yield", f"{div_yield:.2f}%", "Moderate dividend support"))
        else:
            analysis.append(("Dividend Yield", f"{div_yield:.2f}%", "Low / no dividend"))
    else:
        analysis.append(("Dividend Yield", "N/A", "Data not available"))

    if fund_score >= 80:
        summary = "Institutional Fundamental View: ELITE QUALITY / STRONG FUNDAMENTAL COMPOUNDER"
    elif fund_score >= 65:
        summary = "Institutional Fundamental View: STRONG FUNDAMENTAL PROFILE"
    elif fund_score >= 50:
        summary = "Institutional Fundamental View: DECENT / MIXED FUNDAMENTALS"
    else:
        summary = "Institutional Fundamental View: WEAK / NEEDS CAUTION"

    return analysis, summary

def get_technical_analysis_text(row):
    analysis = []

    price = row.get("Price", np.nan)
    rsi = row.get("RSI", np.nan)
    hist_df = row.get("Hist", None)
    sma20 = hist_df.iloc[-1]["SMA20"] if hist_df is not None and not hist_df.empty and "SMA20" in hist_df.columns else np.nan
    sma50 = row.get("SMA50", np.nan)
    sma200 = row.get("SMA200", np.nan)
    macd = row.get("MACD", np.nan)
    macd_signal = row.get("MACD Signal", np.nan)
    high_52 = row.get("52W High", np.nan)
    low_52 = row.get("52W Low", np.nan)
    ret_1m = row.get("1M %", np.nan)
    ret_3m = row.get("3M %", np.nan)
    ret_6m = row.get("6M %", np.nan)
    ret_1y = row.get("1Y %", np.nan)
    tech_score = row.get("Technical Score", 0)

    if pd.notna(price) and pd.notna(sma20):
        verdict = "Bullish above 20DMA" if price > sma20 else "Below 20DMA (short-term weakness)"
        analysis.append(("Price vs 20DMA", f"₹{price:.2f} vs ₹{sma20:.2f}", verdict))

    if pd.notna(price) and pd.notna(sma50):
        verdict = "Bullish above 50DMA" if price > sma50 else "Below 50DMA (medium-term caution)"
        analysis.append(("Price vs 50DMA", f"₹{price:.2f} vs ₹{sma50:.2f}", verdict))

    if pd.notna(price) and pd.notna(sma200):
        verdict = "Bullish above 200DMA" if price > sma200 else "Below 200DMA (long-term weak structure)"
        analysis.append(("Price vs 200DMA", f"₹{price:.2f} vs ₹{sma200:.2f}", verdict))

    if pd.notna(rsi):
        if rsi > 70:
            verdict = "Overbought zone - strong momentum but caution"
        elif rsi < 30:
            verdict = "Oversold zone - possible bounce candidate"
        elif 45 <= rsi <= 65:
            verdict = "Healthy momentum zone"
        else:
            verdict = "Neutral momentum zone"
        analysis.append(("RSI", f"{rsi:.2f}", verdict))

    if pd.notna(macd) and pd.notna(macd_signal):
        verdict = "Bullish MACD crossover / momentum positive" if macd > macd_signal else "Bearish MACD setup / momentum weak"
        analysis.append(("MACD", f"{macd:.2f} vs Signal {macd_signal:.2f}", verdict))

    if pd.notna(price) and pd.notna(high_52) and pd.notna(low_52) and high_52 != low_52:
        pos = ((price - low_52) / (high_52 - low_52)) * 100
        if pos > 80:
            verdict = "Trading near 52W high (leadership strength)"
        elif pos > 60:
            verdict = "Upper range strength"
        elif pos > 40:
            verdict = "Mid range"
        else:
            verdict = "Lower range / weak structure"
        analysis.append(("52W Range Position", f"{pos:.2f}%", verdict))

    momentum_text = (
        f"1M: {ret_1m:.2f}% | 3M: {ret_3m:.2f}% | "
        f"6M: {ret_6m:.2f}% | 1Y: {ret_1y:.2f}%"
    ) if all(pd.notna(x) for x in [ret_1m, ret_3m, ret_6m, ret_1y]) else "Partial data"

    if pd.notna(ret_3m) and pd.notna(ret_6m):
        if ret_3m > 0 and ret_6m > 0:
            momentum_verdict = "Positive multi-timeframe momentum"
        else:
            momentum_verdict = "Mixed / weak momentum"
    else:
        momentum_verdict = "Momentum data partially unavailable"

    analysis.append(("Momentum", momentum_text, momentum_verdict))

    if tech_score >= 80:
        summary = "Institutional Technical View: STRONG UPTREND / MOMENTUM LEADER"
    elif tech_score >= 65:
        summary = "Institutional Technical View: BULLISH TECHNICAL STRUCTURE"
    elif tech_score >= 50:
        summary = "Institutional Technical View: NEUTRAL TO POSITIVE"
    else:
        summary = "Institutional Technical View: WEAK / CAUTION"

    return analysis, summary

def get_institutional_strategy_view(row):
    styles = []

    fund_score = row.get("Fundamental Score", 0)
    tech_score = row.get("Technical Score", 0)
    total_score = row.get("Total Score", 0)
    pe = row.get("PE", np.nan)
    roe = row.get("ROE", np.nan)
    de = row.get("Debt/Equity", np.nan)
    ret_3m = row.get("3M %", np.nan)
    ret_6m = row.get("6M %", np.nan)
    price = row.get("Price", np.nan)
    sma50 = row.get("SMA50", np.nan)

    if pd.notna(pe) and pe < 25 and fund_score >= 65:
        styles.append("✅ Value / GARP Candidate")
    if pd.notna(roe) and roe > 15 and pd.notna(de) and de < 100:
        styles.append("✅ Quality Compounder Candidate")
    if pd.notna(ret_3m) and pd.notna(ret_6m) and ret_3m > 0 and ret_6m > 0 and tech_score >= 65:
        styles.append("✅ Momentum Candidate")
    if pd.notna(price) and pd.notna(sma50) and price > sma50 and tech_score >= 60:
        styles.append("✅ Swing / Positional Candidate")
    if total_score < 50:
        styles.append("⚠️ Not ideal for fresh aggressive entry")

    if pd.notna(price) and pd.notna(sma50):
        if price > sma50:
            entry_view = "Preferred on dips near 20DMA / 50DMA support"
        else:
            entry_view = "Wait for trend confirmation above 50DMA"
    else:
        entry_view = "Wait for confirmation setup"

    if tech_score >= 70 and fund_score >= 65:
        action_bias = "🏛️ Institutional Bias: ACCUMULATE ON DIPS"
    elif total_score >= 60:
        action_bias = "🏛️ Institutional Bias: SELECTIVE BUY / WATCHLIST"
    elif total_score >= 50:
        action_bias = "🏛️ Institutional Bias: HOLD / MONITOR"
    else:
        action_bias = "🏛️ Institutional Bias: AVOID / WAIT"

    return styles, entry_view, action_bias

# =========================
# ANALYZE STOCK
# =========================
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

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ V10.2 Institutional Control Panel")

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
    <h1>📈 FINAL V10.2 INSTITUTIONAL MASTER ELITE</h1>
    <h3>NIFTY 50 + NIFTY NEXT 50 Institutional Stock Analysis Platform</h3>
    <p class="small-note">
        Premium institutional-grade stock research dashboard • Fundamental + Technical + Per-Stock Deep Analysis + Ranking + Compare
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card"><h4>Universe</h4><h2>100</h2><p>NIFTY 50 + NEXT 50</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><h4>Focus</h4><h2>Institutional</h2><p>Quality + Momentum + Risk</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><h4>Modules</h4><h2>Full Deep Analysis</h2><p>Scanner + Per Stock + Compare</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card"><h4>Deploy</h4><h2>Cloud Safe</h2><p>Single app.py</p></div>', unsafe_allow_html=True)

st.markdown("---")

# =========================
# TABS
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

            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                st.metric("Stocks Scanned", len(results))
            with c2:
                st.metric("After Filters", len(df))
            with c3:
                st.metric("STRONG BUY", int((df["Rating"] == "STRONG BUY").sum()) if len(df) else 0)
            with c4:
                st.metric("BUY", int((df["Rating"] == "BUY").sum()) if len(df) else 0)
            with c5:
                avg_score = round(df["Total Score"].mean(), 2) if len(df) else 0
                st.metric("Avg Score", avg_score)

            st.markdown("### 🏆 Top Institutional Ranked Stocks")

            display_df = top_df[[
                "Symbol", "Sector", "Price", "1M %", "3M %", "6M %", "1Y %",
                "PE", "ROE", "Debt/Equity", "RSI",
                "Fundamental Score", "Technical Score", "Total Score", "Rating"
            ]].copy()

            numeric_cols = ["Price", "1M %", "3M %", "6M %", "1Y %", "PE", "ROE", "Debt/Equity", "RSI", "Fundamental Score", "Technical Score", "Total Score"]
            for col in numeric_cols:
                if col in display_df.columns:
                    display_df[col] = pd.to_numeric(display_df[col], errors="coerce").round(2)

            st.dataframe(display_df, use_container_width=True, height=520)

            st.markdown("### 🎯 Premium Shortlist Cards")
            for _, row in top_df.iterrows():
                rating_class = colorize_rating(row["Rating"])
                st.markdown(f"""
                <div class="stock-card">
                    <h4>{row['Symbol']} <span class="{rating_class}">({row['Rating']})</span></h4>
                    <p><b>Sector:</b> {row['Sector']} | <b>Price:</b> ₹{row['Price']:.2f}</p>
                    <p><b>Total Score:</b> {row['Total Score']:.1f} | <b>Fundamental:</b> {row['Fundamental Score']} | <b>Technical:</b> {row['Technical Score']}</p>
                    <p><b>1M:</b> {row['1M %']:.2f}% | <b>3M:</b> {row['3M %']:.2f}% | <b>6M:</b> {row['6M %']:.2f}% | <b>1Y:</b> {row['1Y %']:.2f}%</p>
                </div>
                """, unsafe_allow_html=True)

            csv = display_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Top Ranked CSV",
                data=csv,
                file_name="v10_2_institutional_master_scan.csv",
                mime="text/csv"
            )
        else:
            st.warning("No stock data could be fetched. Try again later.")
    else:
        st.info("Click **🚀 Run Institutional Scan** from the sidebar to scan NIFTY 50 / NIFTY NEXT 50.")

# =========================
# TAB 2: SINGLE STOCK DEEP ANALYSIS
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

        # SCORECARDS
        st.markdown("### 🏛️ Institutional Scorecards")
        s1, s2, s3 = st.columns(3)
        with s1:
            st.metric("Fundamental Score", f"{single_result['Fundamental Score']}/100")
        with s2:
            st.metric("Technical Score", f"{single_result['Technical Score']}/100")
        with s3:
            st.metric("Final Institutional Score", f"{single_result['Total Score']}/100")

        # FUNDAMENTAL SNAPSHOT
        st.markdown("### 🏦 Fundamental Snapshot")
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            st.metric("PE", f"{single_result['PE']:.2f}" if pd.notna(single_result["PE"]) else "N/A")
        with fc2:
            st.metric("PB", f"{single_result['PB']:.2f}" if pd.notna(single_result["PB"]) else "N/A")
        with fc3:
            st.metric("ROE", f"{single_result['ROE']:.2f}%" if pd.notna(single_result["ROE"]) else "N/A")
        with fc4:
            st.metric("Debt/Equity", f"{single_result['Debt/Equity']:.2f}" if pd.notna(single_result["Debt/Equity"]) else "N/A")

        fc5, fc6, fc7, fc8 = st.columns(4)
        with fc5:
            st.metric("Profit Margin", f"{single_result['Profit Margin']:.2f}%" if pd.notna(single_result["Profit Margin"]) else "N/A")
        with fc6:
            st.metric("Revenue Growth", f"{single_result['Revenue Growth']:.2f}%" if pd.notna(single_result["Revenue Growth"]) else "N/A")
        with fc7:
            st.metric("Dividend Yield", f"{single_result['Dividend Yield']:.2f}%" if pd.notna(single_result["Dividend Yield"]) else "N/A")
        with fc8:
            st.metric("Market Cap", format_large_num(single_result["Market Cap"]))

        # TECHNICAL SNAPSHOT
        st.markdown("### 📊 Technical Snapshot")
        tc1, tc2, tc3, tc4 = st.columns(4)
        with tc1:
            st.metric("RSI", f"{single_result['RSI']:.2f}" if pd.notna(single_result["RSI"]) else "N/A")
        with tc2:
            st.metric("SMA50", f"₹{single_result['SMA50']:.2f}" if pd.notna(single_result["SMA50"]) else "N/A")
        with tc3:
            st.metric("SMA200", f"₹{single_result['SMA200']:.2f}" if pd.notna(single_result["SMA200"]) else "N/A")
        with tc4:
            st.metric("MACD", f"{single_result['MACD']:.2f}" if pd.notna(single_result["MACD"]) else "N/A")

        tc5, tc6, tc7, tc8 = st.columns(4)
        with tc5:
            st.metric("1M Return", f"{single_result['1M %']:.2f}%" if pd.notna(single_result["1M %"]) else "N/A")
        with tc6:
            st.metric("3M Return", f"{single_result['3M %']:.2f}%" if pd.notna(single_result["3M %"]) else "N/A")
        with tc7:
            st.metric("6M Return", f"{single_result['6M %']:.2f}%" if pd.notna(single_result["6M %"]) else "N/A")
        with tc8:
            st.metric("1Y Return", f"{single_result['1Y %']:.2f}%" if pd.notna(single_result["1Y %"]) else "N/A")

        # PER-STOCK FUNDAMENTAL ANALYSIS
        st.markdown("### 🧾 Per-Stock Fundamental Analysis")
        fund_analysis, fund_summary = get_fundamental_analysis_text(single_result)
        fund_df = pd.DataFrame(fund_analysis, columns=["Fundamental Metric", "Value", "Institutional Interpretation"])
        st.dataframe(fund_df, use_container_width=True, height=320)
        st.success(fund_summary)

        # PER-STOCK TECHNICAL ANALYSIS
        st.markdown("### 📉 Per-Stock Technical Analysis")
        tech_analysis, tech_summary = get_technical_analysis_text(single_result)
        tech_df = pd.DataFrame(tech_analysis, columns=["Technical Metric", "Value", "Institutional Interpretation"])
        st.dataframe(tech_df, use_container_width=True, height=320)
        st.info(tech_summary)

        # ADVANCED INSTITUTIONAL DATA
        st.markdown("### 💼 Advanced Institutional Data")
        adv_df = pd.DataFrame({
            "Metric": [
                "Sector", "Market Cap", "Beta", "Volume", "52W High", "52W Low",
                "Price vs 52W High %", "Price vs 52W Low %", "Final Rating"
            ],
            "Value": [
                single_result["Sector"],
                format_large_num(single_result["Market Cap"]),
                f"{single_result['Beta']:.2f}" if pd.notna(single_result["Beta"]) else "N/A",
                f"{int(single_result['Volume']):,}" if pd.notna(single_result["Volume"]) else "N/A",
                f"₹{single_result['52W High']:.2f}" if pd.notna(single_result["52W High"]) else "N/A",
                f"₹{single_result['52W Low']:.2f}" if pd.notna(single_result["52W Low"]) else "N/A",
                f"{((single_result['Price'] / single_result['52W High']) - 1) * 100:.2f}%" if pd.notna(single_result["52W High"]) and single_result["52W High"] != 0 else "N/A",
                f"{((single_result['Price'] / single_result['52W Low']) - 1) * 100:.2f}%" if pd.notna(single_result["52W Low"]) and single_result["52W Low"] != 0 else "N/A",
                single_result["Rating"]
            ]
        })
        st.dataframe(adv_df, use_container_width=True, height=300)

        # INSTITUTIONAL STRATEGY VIEW
        st.markdown("### 🧠 Institutional Strategy View")
        styles, entry_view, action_bias = get_institutional_strategy_view(single_result)

        if styles:
            for style in styles:
                st.write(style)

        st.write(f"📌 Entry View: {entry_view}")
        st.write(action_bias)

        # FINAL VERDICT
        st.markdown("### 🎯 Final Per-Stock Institutional Verdict")
        if single_result["Total Score"] >= 80:
            st.success("This stock qualifies as a HIGH-CONVICTION institutional-grade candidate. Best suited for accumulation on dips if market trend supports.")
        elif single_result["Total Score"] >= 65:
            st.success("This stock is a strong watchlist / buy candidate with healthy fundamentals and/or technical structure.")
        elif single_result["Total Score"] >= 50:
            st.warning("This stock is acceptable but mixed. Better to wait for stronger setup or better valuation.")
        else:
            st.error("This stock currently lacks strong institutional conviction. Avoid aggressive fresh entry until improvement.")
    else:
        st.warning("Unable to fetch stock data for selected stock.")

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

            st.dataframe(cmp_df, use_container_width=True, height=420)

            st.markdown("### 📈 Price Performance Comparison (1Y = Base 100)")
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
- **Current Ratio** → Liquidity quality (if available)
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

### 🔍 V10.2 Upgrade
This version adds **per-stock full institutional deep analysis**:
- Detailed fundamental interpretation
- Detailed technical interpretation
- Institutional style fit (Value / Quality / Momentum / Swing)
- Final action bias and verdict

### ⚠️ Important Note
This app is for **research, education, and professional screening only**.  
Always combine with:
- Quarterly results
- Management quality
- Sector rotation
- Valuation context
- Macro environment
- Position sizing & risk management
""")

st.markdown("---")
st.caption("FINAL V10.2 INSTITUTIONAL MASTER ELITE • NIFTY 50 + NIFTY NEXT 50 • Single File • Streamlit Cloud Safe")

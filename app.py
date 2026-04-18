import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="FINAL V11.1 INSTITUTIONAL AI ELITE PRO MAX",
    page_icon="📈",
    layout="wide"
)

# ==========================================
# CUSTOM CSS
# ==========================================
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
    .green-text { color: #22c55e; font-weight: 700; }
    .red-text { color: #ef4444; font-weight: 700; }
    .gold-text { color: #fbbf24; font-weight: 700; }
    .blue-text { color: #60a5fa; font-weight: 700; }
    h1, h2, h3, h4 { color: #f8fafc !important; }
    .small-note { color: #cbd5e1; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# STOCK UNIVERSE
# ==========================================
NIFTY_50 = {
    "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS", "HDFCBANK": "HDFCBANK.NS", "ICICIBANK": "ICICIBANK.NS",
    "INFY": "INFY.NS", "HINDUNILVR": "HINDUNILVR.NS", "ITC": "ITC.NS", "SBIN": "SBIN.NS",
    "BHARTIARTL": "BHARTIARTL.NS", "KOTAKBANK": "KOTAKBANK.NS", "LT": "LT.NS", "AXISBANK": "AXISBANK.NS",
    "ASIANPAINT": "ASIANPAINT.NS", "MARUTI": "MARUTI.NS", "BAJFINANCE": "BAJFINANCE.NS", "HCLTECH": "HCLTECH.NS",
    "SUNPHARMA": "SUNPHARMA.NS", "TITAN": "TITAN.NS", "ULTRACEMCO": "ULTRACEMCO.NS", "NTPC": "NTPC.NS",
    "POWERGRID": "POWERGRID.NS", "NESTLEIND": "NESTLEIND.NS", "ONGC": "ONGC.NS", "TATAMOTORS": "TATAMOTORS.NS",
    "M&M": "M&M.NS", "JSWSTEEL": "JSWSTEEL.NS", "TATASTEEL": "TATASTEEL.NS", "COALINDIA": "COALINDIA.NS",
    "INDUSINDBK": "INDUSINDBK.NS", "BAJAJFINSV": "BAJAJFINSV.NS", "WIPRO": "WIPRO.NS", "HDFCLIFE": "HDFCLIFE.NS",
    "ADANIENT": "ADANIENT.NS", "ADANIPORTS": "ADANIPORTS.NS", "GRASIM": "GRASIM.NS", "CIPLA": "CIPLA.NS",
    "DRREDDY": "DRREDDY.NS", "TECHM": "TECHM.NS", "EICHERMOT": "EICHERMOT.NS", "APOLLOHOSP": "APOLLOHOSP.NS",
    "DIVISLAB": "DIVISLAB.NS", "BPCL": "BPCL.NS", "BRITANNIA": "BRITANNIA.NS", "HEROMOTOCO": "HEROMOTOCO.NS",
    "SHRIRAMFIN": "SHRIRAMFIN.NS", "BAJAJ-AUTO": "BAJAJ-AUTO.NS", "TATACONSUM": "TATACONSUM.NS", "SBILIFE": "SBILIFE.NS",
    "HINDALCO": "HINDALCO.NS", "UPL": "UPL.NS"
}

NIFTY_NEXT_50 = {
    "DMART": "DMART.NS", "ZOMATO": "ZOMATO.NS", "HAL": "HAL.NS", "SIEMENS": "SIEMENS.NS",
    "PIDILITIND": "PIDILITIND.NS", "DABUR": "DABUR.NS", "GODREJCP": "GODREJCP.NS", "BANKBARODA": "BANKBARODA.NS",
    "PNB": "PNB.NS", "INDIGO": "INDIGO.NS", "TVSMOTOR": "TVSMOTOR.NS", "AMBUJACEM": "AMBUJACEM.NS",
    "BOSCHLTD": "BOSCHLTD.NS", "HAVELLS": "HAVELLS.NS", "ABB": "ABB.NS", "MCDOWELL-N": "MCDOWELL-N.NS",
    "BERGEPAINT": "BERGEPAINT.NS", "CHOLAFIN": "CHOLAFIN.NS", "TORNTPHARM": "TORNTPHARM.NS", "LODHA": "LODHA.NS",
    "DLF": "DLF.NS", "ICICIPRULI": "ICICIPRULI.NS", "NAUKRI": "NAUKRI.NS", "MOTHERSON": "MOTHERSON.NS",
    "INDUSTOWER": "INDUSTOWER.NS", "JINDALSTEL": "JINDALSTEL.NS", "CGPOWER": "CGPOWER.NS", "BHEL": "BHEL.NS",
    "IRCTC": "IRCTC.NS", "CANBK": "CANBK.NS", "PFC": "PFC.NS", "RECLTD": "RECLTD.NS",
    "ADANIENSOL": "ADANIENSOL.NS", "GAIL": "GAIL.NS", "MARICO": "MARICO.NS", "COLPAL": "COLPAL.NS",
    "BIOCON": "BIOCON.NS", "PAGEIND": "PAGEIND.NS", "UNIONBANK": "UNIONBANK.NS", "NMDC": "NMDC.NS",
    "HINDPETRO": "HINDPETRO.NS", "IOC": "IOC.NS", "LICI": "LICI.NS", "VEDL": "VEDL.NS",
    "SAIL": "SAIL.NS", "ICICIGI": "ICICIGI.NS", "SRF": "SRF.NS", "MPHASIS": "MPHASIS.NS",
    "TRENT": "TRENT.NS", "LTIM": "LTIM.NS"
}

ALL_STOCKS = {**NIFTY_50, **NIFTY_NEXT_50}

# ==========================================
# SESSION STATE
# ==========================================
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = []

if "scan_results" not in st.session_state:
    st.session_state["scan_results"] = []

# ==========================================
# HELPERS
# ==========================================
def safe_get(info, key, default=np.nan):
    try:
        val = info.get(key, default)
        if val is None:
            return default
        return val
    except:
        return default

def to_pct(x):
    if pd.isna(x):
        return np.nan
    return x * 100 if abs(x) < 5 else x

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
    return "red-text"

# ==========================================
# FAST DATA FETCH
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
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

# ==========================================
# TECHNICAL CALCULATIONS
# ==========================================
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def compute_macd(close):
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist

def compute_atr(df, period=14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def compute_technical_indicators(df):
    out = df.copy()
    out["SMA20"] = out["Close"].rolling(20).mean()
    out["SMA50"] = out["Close"].rolling(50).mean()
    out["SMA200"] = out["Close"].rolling(200).mean()
    out["EMA20"] = out["Close"].ewm(span=20, adjust=False).mean()
    out["RSI"] = compute_rsi(out["Close"], 14)
    out["MACD"], out["MACD_SIGNAL"], out["MACD_HIST"] = compute_macd(out["Close"])
    out["ATR14"] = compute_atr(out, 14)
    out["52W_HIGH"] = out["High"].rolling(252).max()
    out["52W_LOW"] = out["Low"].rolling(252).min()
    out["AVG_VOL20"] = out["Volume"].rolling(20).mean()
    return out

def pct_change(series, days):
    if len(series) <= days:
        return np.nan
    return ((series.iloc[-1] / series.iloc[-days-1]) - 1) * 100

# ==========================================
# SCORING
# ==========================================
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
        roe_pct = to_pct(roe)
        if roe_pct > 20: score += 20
        elif roe_pct > 15: score += 15
        elif roe_pct > 10: score += 10
        elif roe_pct > 5: score += 5

    if pd.notna(de):
        if de < 50: score += 15
        elif de < 100: score += 10
        elif de < 200: score += 5

    if pd.notna(margin):
        margin_pct = to_pct(margin)
        if margin_pct > 20: score += 15
        elif margin_pct > 10: score += 10
        elif margin_pct > 5: score += 5

    if pd.notna(growth):
        growth_pct = to_pct(growth)
        if growth_pct > 20: score += 15
        elif growth_pct > 10: score += 10
        elif growth_pct > 5: score += 5

    if pd.notna(current_ratio):
        if current_ratio > 1.5: score += 5
        elif current_ratio > 1: score += 3

    if pd.notna(div_yield):
        dy_pct = to_pct(div_yield)
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

    if pd.notna(macd) and pd.notna(macd_signal) and macd > macd_signal:
        score += 15

    if pd.notna(high_52) and pd.notna(low_52) and high_52 != low_52:
        pos = (close - low_52) / (high_52 - low_52)
        if 0.6 <= pos <= 0.95:
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

# ==========================================
# BREAKOUT / SWING / TRADE PLAN
# ==========================================
def get_breakout_signal(df):
    if df is None or df.empty or len(df) < 60:
        return "NO DATA", np.nan, False

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    close = latest["Close"]
    high_52 = latest.get("52W_HIGH", np.nan)
    avg_vol20 = latest.get("AVG_VOL20", np.nan)
    volume = latest.get("Volume", np.nan)
    sma20 = latest.get("SMA20", np.nan)
    sma50 = latest.get("SMA50", np.nan)

    volume_ratio = volume / avg_vol20 if pd.notna(volume) and pd.notna(avg_vol20) and avg_vol20 != 0 else np.nan

    breakout = False
    signal = "NO BREAKOUT"

    if pd.notna(high_52) and close >= (0.98 * high_52):
        if pd.notna(volume_ratio) and volume_ratio >= 1.3:
            breakout = True
            signal = "52W HIGH BREAKOUT ZONE"
        else:
            signal = "NEAR 52W HIGH"

    if pd.notna(sma20) and pd.notna(sma50):
        if close > sma20 > sma50 and prev["Close"] <= prev["SMA20"]:
            signal = "SHORT TERM TREND BREAKOUT"

    return signal, round(volume_ratio, 2) if pd.notna(volume_ratio) else np.nan, breakout

def get_swing_signal(df):
    if df is None or df.empty or len(df) < 60:
        return "NO DATA", 0

    latest = df.iloc[-1]
    close = latest["Close"]
    sma20 = latest.get("SMA20", np.nan)
    sma50 = latest.get("SMA50", np.nan)
    rsi = latest.get("RSI", np.nan)
    macd = latest.get("MACD", np.nan)
    macd_signal = latest.get("MACD_SIGNAL", np.nan)

    score = 0

    if pd.notna(close) and pd.notna(sma20) and close > sma20: score += 20
    if pd.notna(close) and pd.notna(sma50) and close > sma50: score += 25
    if pd.notna(rsi) and 45 <= rsi <= 65: score += 20
    elif pd.notna(rsi) and 35 <= rsi <= 75: score += 10
    if pd.notna(macd) and pd.notna(macd_signal) and macd > macd_signal: score += 20
    if pd.notna(sma20) and pd.notna(sma50) and sma20 > sma50: score += 15

    if score >= 75:
        signal = "HIGH PROBABILITY SWING"
    elif score >= 55:
        signal = "SWING CANDIDATE"
    elif score >= 40:
        signal = "WATCHLIST"
    else:
        signal = "NO SWING SETUP"

    return signal, score

def build_trade_plan(price, hist):
    if hist is None or hist.empty or pd.isna(price):
        return {"Entry": np.nan, "SL": np.nan, "Target1": np.nan, "Target2": np.nan, "RR": np.nan}

    latest = hist.iloc[-1]
    atr = latest.get("ATR14", np.nan)
    sma20 = latest.get("SMA20", np.nan)
    sma50 = latest.get("SMA50", np.nan)

    if pd.isna(atr) or atr <= 0:
        atr = price * 0.03

    entry = price
    support = sma20 if pd.notna(sma20) and price > sma20 else (sma50 if pd.notna(sma50) else price * 0.95)
    sl = min(support, price - 1.2 * atr)
    if sl >= price:
        sl = price - 1.2 * atr

    risk = max(price - sl, price * 0.01)
    target1 = price + (risk * 1.5)
    target2 = price + (risk * 2.5)
    rr = (target2 - price) / risk if risk > 0 else np.nan

    return {
        "Entry": round(entry, 2),
        "SL": round(sl, 2),
        "Target1": round(target1, 2),
        "Target2": round(target2, 2),
        "RR": round(rr, 2) if pd.notna(rr) else np.nan
    }

def calculate_position_size(capital, risk_pct, entry, sl):
    if any(pd.isna(x) for x in [capital, risk_pct, entry, sl]):
        return {
            "Risk Amount": np.nan,
            "Per Share Risk": np.nan,
            "Qty": np.nan,
            "Capital Used": np.nan
        }

    risk_amount = capital * (risk_pct / 100)
    per_share_risk = max(entry - sl, 0)

    if per_share_risk <= 0:
        qty = 0
    else:
        qty = int(risk_amount // per_share_risk)

    capital_used = qty * entry

    return {
        "Risk Amount": round(risk_amount, 2),
        "Per Share Risk": round(per_share_risk, 2),
        "Qty": int(qty),
        "Capital Used": round(capital_used, 2)
    }

# ==========================================
# FUNDAMENTAL ANALYSIS TEXT
# ==========================================
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
            analysis.append(("PE Ratio", f"{pe:.2f}", "Attractive valuation"))
        elif pe < 35:
            analysis.append(("PE Ratio", f"{pe:.2f}", "Fair valuation"))
        else:
            analysis.append(("PE Ratio", f"{pe:.2f}", "Premium / expensive"))
    else:
        analysis.append(("PE Ratio", "N/A", "Data unavailable"))

    if pd.notna(pb):
        if pb < 3:
            analysis.append(("PB Ratio", f"{pb:.2f}", "Healthy valuation vs book"))
        elif pb < 6:
            analysis.append(("PB Ratio", f"{pb:.2f}", "Acceptable premium"))
        else:
            analysis.append(("PB Ratio", f"{pb:.2f}", "Rich valuation"))
    else:
        analysis.append(("PB Ratio", "N/A", "Data unavailable"))

    if pd.notna(roe):
        if roe > 20:
            analysis.append(("ROE", f"{roe:.2f}%", "Excellent business quality"))
        elif roe > 15:
            analysis.append(("ROE", f"{roe:.2f}%", "Strong quality"))
        elif roe > 10:
            analysis.append(("ROE", f"{roe:.2f}%", "Average to good"))
        else:
            analysis.append(("ROE", f"{roe:.2f}%", "Weak or average"))
    else:
        analysis.append(("ROE", "N/A", "Data unavailable"))

    if pd.notna(de):
        if de < 50:
            analysis.append(("Debt/Equity", f"{de:.2f}", "Low leverage / strong balance sheet"))
        elif de < 100:
            analysis.append(("Debt/Equity", f"{de:.2f}", "Manageable leverage"))
        else:
            analysis.append(("Debt/Equity", f"{de:.2f}", "Higher debt risk"))
    else:
        analysis.append(("Debt/Equity", "N/A", "Data unavailable"))

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
        analysis.append(("Profit Margin", "N/A", "Data unavailable"))

    if pd.notna(growth):
        if growth > 20:
            analysis.append(("Revenue Growth", f"{growth:.2f}%", "High growth"))
        elif growth > 10:
            analysis.append(("Revenue Growth", f"{growth:.2f}%", "Healthy growth"))
        elif growth > 5:
            analysis.append(("Revenue Growth", f"{growth:.2f}%", "Moderate growth"))
        else:
            analysis.append(("Revenue Growth", f"{growth:.2f}%", "Low / mature growth"))
    else:
        analysis.append(("Revenue Growth", "N/A", "Data unavailable"))

    if pd.notna(div_yield):
        if div_yield > 2:
            analysis.append(("Dividend Yield", f"{div_yield:.2f}%", "Good payout support"))
        elif div_yield > 0:
            analysis.append(("Dividend Yield", f"{div_yield:.2f}%", "Moderate payout"))
        else:
            analysis.append(("Dividend Yield", f"{div_yield:.2f}%", "Low / no dividend"))
    else:
        analysis.append(("Dividend Yield", "N/A", "Data unavailable"))

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
        analysis.append(("Price vs 20DMA", f"₹{price:.2f} vs ₹{sma20:.2f}", "Bullish above 20DMA" if price > sma20 else "Below 20DMA"))

    if pd.notna(price) and pd.notna(sma50):
        analysis.append(("Price vs 50DMA", f"₹{price:.2f} vs ₹{sma50:.2f}", "Bullish above 50DMA" if price > sma50 else "Below 50DMA"))

    if pd.notna(price) and pd.notna(sma200):
        analysis.append(("Price vs 200DMA", f"₹{price:.2f} vs ₹{sma200:.2f}", "Bullish above 200DMA" if price > sma200 else "Below 200DMA"))

    if pd.notna(rsi):
        if rsi > 70:
            verdict = "Overbought"
        elif rsi < 30:
            verdict = "Oversold"
        elif 45 <= rsi <= 65:
            verdict = "Healthy momentum"
        else:
            verdict = "Neutral"
        analysis.append(("RSI", f"{rsi:.2f}", verdict))

    if pd.notna(macd) and pd.notna(macd_signal):
        analysis.append(("MACD", f"{macd:.2f} vs {macd_signal:.2f}", "Bullish MACD" if macd > macd_signal else "Bearish MACD"))

    if pd.notna(price) and pd.notna(high_52) and pd.notna(low_52) and high_52 != low_52:
        pos = ((price - low_52) / (high_52 - low_52)) * 100
        if pos > 80:
            verdict = "Near 52W high"
        elif pos > 60:
            verdict = "Upper range strength"
        elif pos > 40:
            verdict = "Mid range"
        else:
            verdict = "Lower range weakness"
        analysis.append(("52W Range Position", f"{pos:.2f}%", verdict))

    momentum_text = "Partial data"
    if all(pd.notna(x) for x in [ret_1m, ret_3m, ret_6m, ret_1y]):
        momentum_text = f"1M: {ret_1m:.2f}% | 3M: {ret_3m:.2f}% | 6M: {ret_6m:.2f}% | 1Y: {ret_1y:.2f}%"

    if pd.notna(ret_3m) and pd.notna(ret_6m):
        momentum_verdict = "Positive multi-timeframe momentum" if (ret_3m > 0 and ret_6m > 0) else "Mixed / weak momentum"
    else:
        momentum_verdict = "Momentum partial"

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
        styles.append("⚠️ Not ideal for aggressive fresh entry")

    if pd.notna(price) and pd.notna(sma50):
        entry_view = "Preferred on dips near 20DMA / 50DMA" if price > sma50 else "Wait for trend confirmation above 50DMA"
    else:
        entry_view = "Wait for confirmation"

    if tech_score >= 70 and fund_score >= 65:
        action_bias = "🏛️ Institutional Bias: ACCUMULATE ON DIPS"
    elif total_score >= 60:
        action_bias = "🏛️ Institutional Bias: SELECTIVE BUY / WATCHLIST"
    elif total_score >= 50:
        action_bias = "🏛️ Institutional Bias: HOLD / MONITOR"
    else:
        action_bias = "🏛️ Institutional Bias: AVOID / WAIT"

    return styles, entry_view, action_bias

# ==========================================
# BALANCE SHEET STYLE FUNDAMENTAL PANEL
# ==========================================
def build_balance_sheet_fundamental_table(result):
    data = [
        ("Sector", result.get("Sector", "N/A")),
        ("Industry", result.get("Industry", "N/A")),
        ("Market Cap", format_large_num(result.get("Market Cap", np.nan))),
        ("Enterprise Value", format_large_num(result.get("Enterprise Value", np.nan))),
        ("Total Cash", format_large_num(result.get("Total Cash", np.nan))),
        ("Total Debt", format_large_num(result.get("Total Debt", np.nan))),
        ("Free Cash Flow", format_large_num(result.get("Free Cash Flow", np.nan))),
        ("Current Ratio", f"{result.get('Current Ratio', np.nan):.2f}" if pd.notna(result.get("Current Ratio", np.nan)) else "N/A"),
        ("Debt / Equity", f"{result.get('Debt/Equity', np.nan):.2f}" if pd.notna(result.get("Debt/Equity", np.nan)) else "N/A"),
        ("Book Value", f"{result.get('Book Value', np.nan):.2f}" if pd.notna(result.get("Book Value", np.nan)) else "N/A"),
        ("Price / Book", f"{result.get('PB', np.nan):.2f}" if pd.notna(result.get("PB", np.nan)) else "N/A"),
        ("PE Ratio", f"{result.get('PE', np.nan):.2f}" if pd.notna(result.get("PE", np.nan)) else "N/A"),
        ("ROE", f"{result.get('ROE', np.nan):.2f}%" if pd.notna(result.get("ROE", np.nan)) else "N/A"),
        ("ROA", f"{result.get('ROA', np.nan):.2f}%" if pd.notna(result.get("ROA", np.nan)) else "N/A"),
        ("Operating Margin", f"{result.get('Operating Margin', np.nan):.2f}%" if pd.notna(result.get("Operating Margin", np.nan)) else "N/A"),
        ("Profit Margin", f"{result.get('Profit Margin', np.nan):.2f}%" if pd.notna(result.get("Profit Margin", np.nan)) else "N/A"),
        ("Revenue Growth", f"{result.get('Revenue Growth', np.nan):.2f}%" if pd.notna(result.get("Revenue Growth", np.nan)) else "N/A"),
        ("Dividend Yield", f"{result.get('Dividend Yield', np.nan):.2f}%" if pd.notna(result.get("Dividend Yield", np.nan)) else "N/A"),
    ]
    return pd.DataFrame(data, columns=["Balance Sheet / Fundamental Item", "Value"])

# ==========================================
# CANDLESTICK CHART
# ==========================================
def make_candlestick_chart(df, title="Candlestick Chart"):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price"
    )])

    if "SMA20" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], mode="lines", name="SMA20"))
    if "SMA50" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], mode="lines", name="SMA50"))
    if "SMA200" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA200"], mode="lines", name="SMA200"))

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark",
        height=550,
        xaxis_rangeslider_visible=False
    )
    return fig

# ==========================================
# ANALYZE STOCK
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
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
    roe = to_pct(safe_get(info, "returnOnEquity"))
    roa = to_pct(safe_get(info, "returnOnAssets"))
    de = safe_get(info, "debtToEquity")
    margin = to_pct(safe_get(info, "profitMargins"))
    operating_margin = to_pct(safe_get(info, "operatingMargins"))
    growth = to_pct(safe_get(info, "revenueGrowth"))
    div_yield = to_pct(safe_get(info, "dividendYield"))
    sector = safe_get(info, "sector", "Unknown")
    industry = safe_get(info, "industry", "Unknown")
    beta = safe_get(info, "beta")
    volume = safe_get(info, "volume")
    current_ratio = safe_get(info, "currentRatio")
    book_value = safe_get(info, "bookValue")
    total_cash = safe_get(info, "totalCash")
    total_debt = safe_get(info, "totalDebt")
    enterprise_value = safe_get(info, "enterpriseValue")
    free_cash_flow = safe_get(info, "freeCashflow")

    rsi = latest.get("RSI", np.nan)
    sma50 = latest.get("SMA50", np.nan)
    sma200 = latest.get("SMA200", np.nan)
    macd = latest.get("MACD", np.nan)
    macd_signal = latest.get("MACD_SIGNAL", np.nan)
    high_52 = latest.get("52W_HIGH", np.nan)
    low_52 = latest.get("52W_LOW", np.nan)

    breakout_signal, vol_ratio, breakout_flag = get_breakout_signal(df)
    swing_signal, swing_score = get_swing_signal(df)
    trade_plan = build_trade_plan(current_price, df)

    return {
        "Symbol": symbol.replace(".NS", ""),
        "Ticker": symbol,
        "Sector": sector,
        "Industry": industry,
        "Price": current_price,
        "1M %": returns_1m,
        "3M %": returns_3m,
        "6M %": returns_6m,
        "1Y %": returns_1y,
        "Market Cap": market_cap,
        "Enterprise Value": enterprise_value,
        "Total Cash": total_cash,
        "Total Debt": total_debt,
        "Free Cash Flow": free_cash_flow,
        "Current Ratio": current_ratio,
        "Book Value": book_value,
        "PE": pe,
        "PB": pb,
        "ROE": roe,
        "ROA": roa,
        "Debt/Equity": de,
        "Profit Margin": margin,
        "Operating Margin": operating_margin,
        "Revenue Growth": growth,
        "Dividend Yield": div_yield,
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
        "Breakout Signal": breakout_signal,
        "Volume Ratio": vol_ratio,
        "Breakout Flag": breakout_flag,
        "Swing Signal": swing_signal,
        "Swing Score": swing_score,
        "Entry": trade_plan["Entry"],
        "SL": trade_plan["SL"],
        "Target1": trade_plan["Target1"],
        "Target2": trade_plan["Target2"],
        "Risk Reward": trade_plan["RR"],
        "Hist": df
    }

# ==========================================
# FAST SCAN
# ==========================================
def run_fast_scan(stock_list, max_scan):
    results = []
    limited_list = stock_list[:max_scan]
    progress = st.progress(0)

    for i, symbol in enumerate(limited_list):
        res = analyze_stock(symbol)
        if res:
            results.append(res)
        progress.progress((i + 1) / len(limited_list))

    return results

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.title("⚙️ V11.1 Institutional AI Control")

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
max_scan = st.sidebar.slider("Fast Scan Limit", 10, len(selected_universe), min(40, len(selected_universe)))

sort_by = st.sidebar.selectbox(
    "Sort By",
    ["Total Score", "Fundamental Score", "Technical Score", "Swing Score", "1M %", "3M %", "6M %", "1Y %", "PE", "ROE"]
)

show_only_buy = st.sidebar.checkbox("Show only BUY / STRONG BUY", value=False)
selected_stock = st.sidebar.selectbox("Single Stock Deep Analysis", list(selected_universe.values()))

# Capital-based position sizing inputs
st.sidebar.markdown("---")
st.sidebar.subheader("💰 Capital-Based Position Sizing")
capital_input = st.sidebar.number_input("Trading Capital (₹)", min_value=10000.0, value=100000.0, step=10000.0)
risk_pct_input = st.sidebar.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)

run_scan = st.sidebar.button("🚀 Run Faster Institutional Scan", use_container_width=True)

# ==========================================
# HEADER
# ==========================================
st.markdown("""
<div class="hero-card">
    <h1>📈 FINAL V11.1 INSTITUTIONAL AI ELITE PRO MAX</h1>
    <h3>NIFTY 50 + NIFTY NEXT 50 | Faster Scan + Candlestick + Watchlist + Position Sizing</h3>
    <p class="small-note">
        Premium institutional-grade stock research dashboard • Fundamental + Technical + Balance Sheet Style Fundamental Panel + Breakout + Swing + Portfolio + Capital-Based Position Sizing
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card"><h4>Universe</h4><h2>100</h2><p>NIFTY 50 + NEXT 50</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><h4>Scan Mode</h4><h2>Faster</h2><p>Cached + Scan Limit</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><h4>Charts</h4><h2>Candlestick</h2><p>Plotly Institutional View</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card"><h4>Risk Engine</h4><h2>Capital Based</h2><p>Qty + Risk + Allocation</p></div>', unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# TABS
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏛️ Institutional Scanner",
    "🔍 Single Stock Deep Analysis",
    "🚀 Breakout Scanner",
    "⚡ Swing Trade Scanner",
    "💼 Portfolio Builder",
    "⭐ Watchlist",
    "📊 Compare + Methodology"
])

# ==========================================
# TAB 1: SCANNER
# ==========================================
with tab1:
    st.subheader("🏛️ Faster Institutional Scanner")

    if run_scan:
        stock_list = list(selected_universe.values())
        results = run_fast_scan(stock_list, max_scan)

        if results:
            st.session_state["scan_results"] = results
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
                st.metric("Breakout Candidates", int((df["Breakout Flag"] == True).sum()) if len(df) else 0)
            with c5:
                st.metric("Swing Candidates", int((df["Swing Score"] >= 55).sum()) if len(df) else 0)

            st.markdown("### 🏆 Top Institutional Ranked Stocks")
            display_cols = [
                "Symbol", "Sector", "Price", "1M %", "3M %", "6M %", "1Y %",
                "Fundamental Score", "Technical Score", "Total Score",
                "Breakout Signal", "Swing Signal", "Entry", "SL", "Target2", "Risk Reward", "Rating"
            ]
            display_df = top_df[display_cols].copy()

            numeric_cols = ["Price", "1M %", "3M %", "6M %", "1Y %", "Fundamental Score", "Technical Score", "Total Score", "Entry", "SL", "Target2", "Risk Reward"]
            for col in numeric_cols:
                display_df[col] = pd.to_numeric(display_df[col], errors="coerce").round(2)

            st.dataframe(display_df, use_container_width=True, height=550)

            # Quick add to watchlist
            st.markdown("### ⭐ Add Scanner Stock to Watchlist")
            add_watch_symbol = st.selectbox("Select stock from scan to add", top_df["Ticker"].tolist() if len(top_df) else [])
            if st.button("➕ Add to Watchlist"):
                if add_watch_symbol and add_watch_symbol not in st.session_state["watchlist"]:
                    st.session_state["watchlist"].append(add_watch_symbol)
                    st.success(f"{add_watch_symbol} added to watchlist.")
                else:
                    st.warning("Stock already in watchlist or invalid.")

            csv = display_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Institutional Scan CSV",
                data=csv,
                file_name="v11_1_institutional_ai_elite_scan.csv",
                mime="text/csv"
            )
        else:
            st.warning("No stock data could be fetched. Try again later.")
    else:
        st.info("Click **🚀 Run Faster Institutional Scan** from the sidebar.")

# ==========================================
# TAB 2: SINGLE STOCK DEEP ANALYSIS
# ==========================================
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

        # Watchlist actions
        w1, w2 = st.columns(2)
        with w1:
            if st.button("⭐ Add Selected Stock to Watchlist"):
                if selected_stock not in st.session_state["watchlist"]:
                    st.session_state["watchlist"].append(selected_stock)
                    st.success(f"{selected_stock} added to watchlist.")
                else:
                    st.warning("Already in watchlist.")
        with w2:
            if st.button("❌ Remove Selected Stock from Watchlist"):
                if selected_stock in st.session_state["watchlist"]:
                    st.session_state["watchlist"].remove(selected_stock)
                    st.success(f"{selected_stock} removed from watchlist.")
                else:
                    st.warning("Not in watchlist.")

        st.markdown("### 🕯️ Candlestick Chart (Institutional View)")
        hist_df = single_result["Hist"].copy()
        fig = make_candlestick_chart(hist_df.tail(180), title=f"{single_result['Symbol']} - Last 180 Sessions")
        st.plotly_chart(fig, use_container_width=True)

        # Scorecards
        st.markdown("### 🏛️ Institutional Scorecards")
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.metric("Fundamental Score", f"{single_result['Fundamental Score']}/100")
        with s2:
            st.metric("Technical Score", f"{single_result['Technical Score']}/100")
        with s3:
            st.metric("Swing Score", f"{single_result['Swing Score']}/100")
        with s4:
            st.metric("Risk Reward", f"{single_result['Risk Reward']:.2f}" if pd.notna(single_result["Risk Reward"]) else "N/A")

        # Fundamental snapshot
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

        # NEW BALANCE SHEET STYLE FUNDAMENTAL PANEL
        st.markdown("### 📒 Balance Sheet Style Fundamental Panel (Sector + Financial Health)")
        bs_df = build_balance_sheet_fundamental_table(single_result)
        st.dataframe(bs_df, use_container_width=True, height=520)

        # Technical snapshot
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

        # Breakout + swing
        st.markdown("### 🚀 Breakout + Swing View")
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            st.metric("Breakout Signal", single_result["Breakout Signal"])
        with b2:
            st.metric("Volume Ratio", f"{single_result['Volume Ratio']:.2f}" if pd.notna(single_result["Volume Ratio"]) else "N/A")
        with b3:
            st.metric("Swing Signal", single_result["Swing Signal"])
        with b4:
            st.metric("Swing Score", single_result["Swing Score"])

        # Trade plan
        st.markdown("### 🎯 Trade Plan (Entry / SL / Targets)")
        tp1, tp2, tp3, tp4, tp5 = st.columns(5)
        with tp1:
            st.metric("Entry", f"₹{single_result['Entry']:.2f}" if pd.notna(single_result["Entry"]) else "N/A")
        with tp2:
            st.metric("Stop Loss", f"₹{single_result['SL']:.2f}" if pd.notna(single_result["SL"]) else "N/A")
        with tp3:
            st.metric("Target 1", f"₹{single_result['Target1']:.2f}" if pd.notna(single_result["Target1"]) else "N/A")
        with tp4:
            st.metric("Target 2", f"₹{single_result['Target2']:.2f}" if pd.notna(single_result["Target2"]) else "N/A")
        with tp5:
            st.metric("Risk Reward", f"{single_result['Risk Reward']:.2f}" if pd.notna(single_result["Risk Reward"]) else "N/A")

        # Capital-based position sizing
        st.markdown("### 💰 Capital-Based Position Sizing")
        pos = calculate_position_size(
            capital=capital_input,
            risk_pct=risk_pct_input,
            entry=single_result["Entry"],
            sl=single_result["SL"]
        )

        p1, p2, p3, p4 = st.columns(4)
        with p1:
            st.metric("Risk Amount", f"₹{pos['Risk Amount']:.2f}" if pd.notna(pos["Risk Amount"]) else "N/A")
        with p2:
            st.metric("Per Share Risk", f"₹{pos['Per Share Risk']:.2f}" if pd.notna(pos["Per Share Risk"]) else "N/A")
        with p3:
            st.metric("Suggested Qty", f"{int(pos['Qty'])}" if pd.notna(pos["Qty"]) else "N/A")
        with p4:
            st.metric("Capital Used", f"₹{pos['Capital Used']:.2f}" if pd.notna(pos["Capital Used"]) else "N/A")

        # Detailed per-stock fundamental analysis
        st.markdown("### 🧾 Per-Stock Fundamental Analysis")
        fund_analysis, fund_summary = get_fundamental_analysis_text(single_result)
        st.dataframe(pd.DataFrame(fund_analysis, columns=["Metric", "Value", "Institutional Interpretation"]),
                     use_container_width=True, height=320)
        st.success(fund_summary)

        # Detailed per-stock technical analysis
        st.markdown("### 📉 Per-Stock Technical Analysis")
        tech_analysis, tech_summary = get_technical_analysis_text(single_result)
        st.dataframe(pd.DataFrame(tech_analysis, columns=["Metric", "Value", "Institutional Interpretation"]),
                     use_container_width=True, height=320)
        st.info(tech_summary)

        # Strategy view
        st.markdown("### 🧠 Institutional Strategy View")
        styles, entry_view, action_bias = get_institutional_strategy_view(single_result)
        for style in styles:
            st.write(style)
        st.write(f"📌 Entry View: {entry_view}")
        st.write(action_bias)

# ==========================================
# TAB 3: BREAKOUT SCANNER
# ==========================================
with tab3:
    st.subheader("🚀 Breakout Scanner")

    results = st.session_state.get("scan_results", [])
    if results:
        df = pd.DataFrame(results)
        breakout_df = df[
            (df["Breakout Flag"] == True) |
            (df["Breakout Signal"].isin(["NEAR 52W HIGH", "SHORT TERM TREND BREAKOUT"]))
        ].copy()

        if len(breakout_df):
            breakout_df = breakout_df.sort_values(
                by=["Breakout Flag", "Volume Ratio", "Total Score"],
                ascending=[False, False, False]
            )

            show_df = breakout_df[[
                "Symbol", "Sector", "Price", "Breakout Signal", "Volume Ratio",
                "Swing Signal", "Fundamental Score", "Technical Score", "Total Score",
                "Entry", "SL", "Target1", "Target2", "Risk Reward", "Rating"
            ]].copy()

            numeric_cols = ["Price", "Volume Ratio", "Fundamental Score", "Technical Score", "Total Score", "Entry", "SL", "Target1", "Target2", "Risk Reward"]
            for col in numeric_cols:
                show_df[col] = pd.to_numeric(show_df[col], errors="coerce").round(2)

            st.dataframe(show_df, use_container_width=True, height=500)
        else:
            st.warning("No breakout candidates found in current scan.")
    else:
        st.info("Run Faster Institutional Scan first.")

# ==========================================
# TAB 4: SWING TRADE SCANNER
# ==========================================
with tab4:
    st.subheader("⚡ Swing Trade Scanner")

    results = st.session_state.get("scan_results", [])
    if results:
        df = pd.DataFrame(results)
        swing_df = df[df["Swing Score"] >= 55].copy()

        if len(swing_df):
            swing_df = swing_df.sort_values(by=["Swing Score", "Total Score", "Risk Reward"], ascending=[False, False, False])

            show_df = swing_df[[
                "Symbol", "Sector", "Price", "Swing Signal", "Swing Score", "Breakout Signal",
                "RSI", "1M %", "3M %", "6M %",
                "Entry", "SL", "Target1", "Target2", "Risk Reward", "Rating"
            ]].copy()

            numeric_cols = ["Price", "Swing Score", "RSI", "1M %", "3M %", "6M %", "Entry", "SL", "Target1", "Target2", "Risk Reward"]
            for col in numeric_cols:
                show_df[col] = pd.to_numeric(show_df[col], errors="coerce").round(2)

            st.dataframe(show_df, use_container_width=True, height=500)
        else:
            st.warning("No strong swing candidates found in current scan.")
    else:
        st.info("Run Faster Institutional Scan first.")

# ==========================================
# TAB 5: PORTFOLIO BUILDER
# ==========================================
with tab5:
    st.subheader("💼 Portfolio Builder (Top 5 / Top 10 Institutional Basket)")

    results = st.session_state.get("scan_results", [])
    portfolio_size = st.radio("Portfolio Size", ["Top 5", "Top 10"], horizontal=True)
    n = 5 if portfolio_size == "Top 5" else 10

    if results:
        df = pd.DataFrame(results).copy()

        df["Portfolio Score"] = (
            df["Total Score"] * 0.50 +
            df["Swing Score"] * 0.20 +
            np.where(df["Breakout Flag"], 15, 0) +
            np.where(df["Risk Reward"].fillna(0) >= 2, 10, 0)
        )

        df = df.sort_values(by="Portfolio Score", ascending=False)
        portfolio_df = df.head(n).copy()
        portfolio_df["Suggested Weight %"] = round(100 / n, 2)

        show_df = portfolio_df[[
            "Symbol", "Sector", "Price", "Fundamental Score", "Technical Score", "Total Score",
            "Breakout Signal", "Swing Signal", "Swing Score",
            "Entry", "SL", "Target2", "Risk Reward", "Suggested Weight %", "Rating"
        ]].copy()

        numeric_cols = ["Price", "Fundamental Score", "Technical Score", "Total Score", "Swing Score", "Entry", "SL", "Target2", "Risk Reward", "Suggested Weight %"]
        for col in numeric_cols:
            show_df[col] = pd.to_numeric(show_df[col], errors="coerce").round(2)

        st.dataframe(show_df, use_container_width=True, height=520)

        csv = show_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            f"📥 Download {portfolio_size} Portfolio CSV",
            data=csv,
            file_name=f"v11_1_portfolio_{n}.csv",
            mime="text/csv"
        )
    else:
        st.info("Run Faster Institutional Scan first to build portfolio.")

# ==========================================
# TAB 6: WATCHLIST
# ==========================================
with tab6:
    st.subheader("⭐ Session Watchlist")

    watchlist = st.session_state.get("watchlist", [])

    if watchlist:
        st.write("### Current Watchlist")
        st.write(", ".join(watchlist))

        if st.button("🗑️ Clear Entire Watchlist"):
            st.session_state["watchlist"] = []
            st.success("Watchlist cleared.")

        st.markdown("### 📋 Watchlist Deep Table")
        watch_results = []
        for sym in watchlist:
            res = analyze_stock(sym)
            if res:
                watch_results.append(res)

        if watch_results:
            watch_df = pd.DataFrame(watch_results)[[
                "Symbol", "Sector", "Price", "Fundamental Score", "Technical Score", "Total Score",
                "Breakout Signal", "Swing Signal", "Swing Score",
                "Entry", "SL", "Target2", "Risk Reward", "Rating"
            ]].copy()

            numeric_cols = ["Price", "Fundamental Score", "Technical Score", "Total Score", "Swing Score", "Entry", "SL", "Target2", "Risk Reward"]
            for col in numeric_cols:
                watch_df[col] = pd.to_numeric(watch_df[col], errors="coerce").round(2)

            st.dataframe(watch_df, use_container_width=True, height=500)
    else:
        st.info("Your watchlist is empty. Add stocks from Scanner or Single Stock Analysis.")

# ==========================================
# TAB 7: COMPARE + METHODOLOGY
# ==========================================
with tab7:
    st.subheader("📊 Compare Stocks")

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
                "RSI", "1M %", "3M %", "6M %", "1Y %",
                "Breakout Signal", "Swing Signal", "Swing Score",
                "Entry", "SL", "Target2", "Risk Reward",
                "Fundamental Score", "Technical Score", "Total Score", "Rating"
            ]]

            numeric_cols = ["Price", "PE", "PB", "ROE", "Debt/Equity", "RSI", "1M %", "3M %", "6M %", "1Y %", "Swing Score", "Entry", "SL", "Target2", "Risk Reward", "Fundamental Score", "Technical Score", "Total Score"]
            for col in numeric_cols:
                cmp_df[col] = pd.to_numeric(cmp_df[col], errors="coerce").round(2)

            st.dataframe(cmp_df, use_container_width=True, height=450)

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

    st.markdown("---")
    st.subheader("📘 V11.1 Methodology")

    st.markdown("""
### 🏛️ Core Institutional Score
- **Fundamental Score (55%)**
- **Technical Score (45%)**

### 📒 Balance Sheet Style Fundamental Panel
- Sector
- Industry
- Market Cap
- Enterprise Value
- Total Cash
- Total Debt
- Free Cash Flow
- Current Ratio
- Debt/Equity
- Book Value
- PB / PE / ROE / ROA
- Operating Margin / Profit Margin / Revenue Growth / Dividend Yield

### 🚀 Breakout Scanner
- Near or at **52-week high**
- Volume confirmation using **Volume / 20-day average volume**
- Short-term trend breakout logic

### ⚡ Swing Trade Scanner
- Price above **20DMA / 50DMA**
- **RSI healthy zone**
- **MACD bullish**
- **20DMA > 50DMA**
- Swing score based ranking

### 🎯 Trade Plan Engine
- **Entry = current price**
- **SL = support / ATR based**
- **Target1 = 1.5R**
- **Target2 = 2.5R**
- **Risk Reward** auto calculated

### 💰 Capital-Based Position Sizing
- Input your capital
- Input risk %
- Auto calculates:
  - Risk amount
  - Per share risk
  - Suggested quantity
  - Capital used

### ⭐ Watchlist
- Add / remove stocks in current session
- Review watchlist with full scan table

### ⚠️ Important
This app is for **research, education, and professional screening only**.
Always validate with:
- Quarterly results
- Management quality
- Sector trend
- News flow
- Market condition
- Proper position sizing
""")

st.markdown("---")
st.caption("FINAL V11.1 INSTITUTIONAL AI ELITE PRO MAX • NIFTY 50 + NIFTY NEXT 50 • Single File • Streamlit Cloud Safe")

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Nile",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SAFE HELPERS
# =========================================================
def safe_float(val, default=0.0):
    try:
        if val is None or (isinstance(val, str) and val.strip() == "") or pd.isna(val):
            return default
        return float(val)
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

def unique_key(prefix, suffix):
    return f"{prefix}_{suffix}_{abs(hash(str(suffix))) % 1000000}"

def safe_df(df):
    return pd.DataFrame() if df is None else df.copy()

def to_csv_download(df):
    if df is None or df.empty:
        return None
    return df.to_csv(index=False).encode("utf-8")

# =========================================================
# LOGO RENDER
# =========================================================
def render_logo():
    try:
        col1, col2 = st.columns([1, 8])
        with col1:
            st.image("nile_logo.png", width=70)
        with col2:
            st.markdown("<h1 style='margin:0;color:#f8fafc;'>Nile</h1>", unsafe_allow_html=True)
            st.markdown("<div style='color:#93c5fd;font-weight:600;'>Analysis</div>", unsafe_allow_html=True)
    except:
        st.markdown("<h1 style='color:#f8fafc;'>📈 Nile</h1>", unsafe_allow_html=True)
        st.markdown("<div style='color:#93c5fd;font-weight:600;'>Analysis</div>", unsafe_allow_html=True)

# =========================================================
# UI / SOLID COLOR / ATTRACTIVE BUTTONS
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #0f172a;
        color: #f8fafc;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }

    h1, h2, h3, h4, h5 {
        font-family: 'Poppins', sans-serif !important;
    }

    .hero-box {
        background: linear-gradient(135deg, rgba(15,23,42,0.98), rgba(30,41,59,0.96));
        border: 1px solid rgba(148,163,184,0.12);
        border-radius: 24px;
        padding: 22px 26px;
        margin-bottom: 18px;
        box-shadow: 0 18px 45px rgba(0,0,0,0.28);
    }

    .section-title {
        font-size: 1.18rem;
        font-weight: 800;
        color: #e2e8f0;
        margin-top: 8px;
        margin-bottom: 10px;
        font-family: 'Poppins', sans-serif !important;
    }

    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(15,23,42,0.88), rgba(30,41,59,0.76));
        border: 1px solid rgba(148,163,184,0.10);
        padding: 12px 14px;
        border-radius: 18px;
        box-shadow: 0 8px 22px rgba(0,0,0,0.18);
    }

    div[data-testid="metric-container"] label {
        color: #93c5fd !important;
        font-weight: 700 !important;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-weight: 800 !important;
        font-size: 1.18rem !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 14px;
        padding: 10px 16px;
        background: rgba(30,41,59,0.90);
        border: 1px solid rgba(148,163,184,0.08);
        font-weight: 700;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(30,64,175,0.55), rgba(14,165,233,0.25)) !important;
        border: 1px solid rgba(96,165,250,0.22) !important;
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 16px !important;
        border: 1px solid rgba(96,165,250,0.35) !important;
        background: linear-gradient(135deg, #2563eb, #0ea5e9) !important;
        color: white !important;
        font-weight: 800 !important;
        padding: 0.55rem 1.2rem !important;
        box-shadow: 0 10px 25px rgba(37,99,235,0.25) !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 28px rgba(14,165,233,0.30) !important;
        border: 1px solid rgba(125,211,252,0.55) !important;
    }

    .stDataFrame, .stTable {
        border-radius: 16px;
        overflow: hidden;
    }

    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid rgba(148,163,184,0.08);
    }

    hr {
        border-color: rgba(148,163,184,0.12);
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 100 STOCK UNIVERSE
# =========================================================
DEFAULT_STOCKS = {
    "RELIANCE": ("RELIANCE.NS", "Energy"),
    "TCS": ("TCS.NS", "IT"),
    "INFY": ("INFY.NS", "IT"),
    "HDFCBANK": ("HDFCBANK.NS", "Banking"),
    "ICICIBANK": ("ICICIBANK.NS", "Banking"),
    "SBIN": ("SBIN.NS", "Banking"),
    "LT": ("LT.NS", "Capital Goods"),
    "ITC": ("ITC.NS", "FMCG"),
    "BHARTIARTL": ("BHARTIARTL.NS", "Telecom"),
    "HINDUNILVR": ("HINDUNILVR.NS", "FMCG"),
    "KOTAKBANK": ("KOTAKBANK.NS", "Banking"),
    "AXISBANK": ("AXISBANK.NS", "Banking"),
    "ASIANPAINT": ("ASIANPAINT.NS", "Paints"),
    "BAJFINANCE": ("BAJFINANCE.NS", "NBFC"),
    "MARUTI": ("MARUTI.NS", "Auto"),
    "TITAN": ("TITAN.NS", "Consumer"),
    "SUNPHARMA": ("SUNPHARMA.NS", "Pharma"),
    "ULTRACEMCO": ("ULTRACEMCO.NS", "Cement"),
    "WIPRO": ("WIPRO.NS", "IT"),
    "NTPC": ("NTPC.NS", "Power"),
    "POWERGRID": ("POWERGRID.NS", "Power"),
    "TATAMOTORS": ("TATAMOTORS.NS", "Auto"),
    "M&M": ("M&M.NS", "Auto"),
    "ADANIPORTS": ("ADANIPORTS.NS", "Infra"),
    "NESTLEIND": ("NESTLEIND.NS", "FMCG"),
    "INDUSINDBK": ("INDUSINDBK.NS", "Banking"),
    "HCLTECH": ("HCLTECH.NS", "IT"),
    "TECHM": ("TECHM.NS", "IT"),
    "BAJAJFINSV": ("BAJAJFINSV.NS", "Financials"),
    "JSWSTEEL": ("JSWSTEEL.NS", "Metals"),
    "TATASTEEL": ("TATASTEEL.NS", "Metals"),
    "ONGC": ("ONGC.NS", "Energy"),
    "COALINDIA": ("COALINDIA.NS", "Mining"),
    "HINDALCO": ("HINDALCO.NS", "Metals"),
    "GRASIM": ("GRASIM.NS", "Cement"),
    "BPCL": ("BPCL.NS", "Energy"),
    "CIPLA": ("CIPLA.NS", "Pharma"),
    "DRREDDY": ("DRREDDY.NS", "Pharma"),
    "EICHERMOT": ("EICHERMOT.NS", "Auto"),
    "HEROMOTOCO": ("HEROMOTOCO.NS", "Auto"),
    "DIVISLAB": ("DIVISLAB.NS", "Pharma"),
    "BRITANNIA": ("BRITANNIA.NS", "FMCG"),
    "APOLLOHOSP": ("APOLLOHOSP.NS", "Healthcare"),
    "ADANIENT": ("ADANIENT.NS", "Infra"),
    "BAJAJ-AUTO": ("BAJAJ-AUTO.NS", "Auto"),
    "SHRIRAMFIN": ("SHRIRAMFIN.NS", "Financials"),
    "SBILIFE": ("SBILIFE.NS", "Insurance"),
    "HDFCLIFE": ("HDFCLIFE.NS", "Insurance"),
    "TRENT": ("TRENT.NS", "Retail"),
    "DMART": ("DMART.NS", "Retail"),
    "PIDILITIND": ("PIDILITIND.NS", "Chemicals"),
    "AMBUJACEM": ("AMBUJACEM.NS", "Cement"),
    "ACC": ("ACC.NS", "Cement"),
    "INDIGO": ("INDIGO.NS", "Aviation"),
    "SIEMENS": ("SIEMENS.NS", "Capital Goods"),
    "ABB": ("ABB.NS", "Capital Goods"),
    "DLF": ("DLF.NS", "Real Estate"),
    "GODREJPROP": ("GODREJPROP.NS", "Real Estate"),
    "LODHA": ("LODHA.NS", "Real Estate"),
    "IRCTC": ("IRCTC.NS", "Railways"),
    "IRFC": ("IRFC.NS", "Railways"),
    "RVNL": ("RVNL.NS", "Railways"),
    "BHEL": ("BHEL.NS", "Capital Goods"),
    "BEL": ("BEL.NS", "Defense"),
    "HAL": ("HAL.NS", "Defense"),
    "BDL": ("BDL.NS", "Defense"),
    "COCHINSHIP": ("COCHINSHIP.NS", "Defense"),
    "TATAPOWER": ("TATAPOWER.NS", "Power"),
    "ADANIGREEN": ("ADANIGREEN.NS", "Power"),
    "ADANIPOWER": ("ADANIPOWER.NS", "Power"),
    "TORNTPOWER": ("TORNTPOWER.NS", "Power"),
    "CANBK": ("CANBK.NS", "Banking"),
    "PNB": ("PNB.NS", "Banking"),
    "BANKBARODA": ("BANKBARODA.NS", "Banking"),
    "UNIONBANK": ("UNIONBANK.NS", "Banking"),
    "FEDERALBNK": ("FEDERALBNK.NS", "Banking"),
    "IDFCFIRSTB": ("IDFCFIRSTB.NS", "Banking"),
    "AUROPHARMA": ("AUROPHARMA.NS", "Pharma"),
    "LUPIN": ("LUPIN.NS", "Pharma"),
    "MANKIND": ("MANKIND.NS", "Pharma"),
    "ZYDUSLIFE": ("ZYDUSLIFE.NS", "Pharma"),
    "DABUR": ("DABUR.NS", "FMCG"),
    "MARICO": ("MARICO.NS", "FMCG"),
    "COLPAL": ("COLPAL.NS", "FMCG"),
    "UBL": ("UBL.NS", "Consumer"),
    "HAVELLS": ("HAVELLS.NS", "Consumer"),
    "VOLTAS": ("VOLTAS.NS", "Consumer"),
    "WHIRLPOOL": ("WHIRLPOOL.NS", "Consumer"),
    "TATACONSUM": ("TATACONSUM.NS", "FMCG"),
    "MOTHERSON": ("MOTHERSON.NS", "Auto Ancillary"),
    "BOSCHLTD": ("BOSCHLTD.NS", "Auto Ancillary"),
    "SONACOMS": ("SONACOMS.NS", "Auto Ancillary"),
    "PERSISTENT": ("PERSISTENT.NS", "IT"),
    "COFORGE": ("COFORGE.NS", "IT"),
    "LTIM": ("LTIM.NS", "IT"),
    "MPHASIS": ("MPHASIS.NS", "IT"),
    "INDUSTOWER": ("INDUSTOWER.NS", "Telecom"),
    "GAIL": ("GAIL.NS", "Energy"),
    "PETRONET": ("PETRONET.NS", "Energy"),
    "IOC": ("IOC.NS", "Energy"),
    "VEDL": ("VEDL.NS", "Metals"),
    "NMDC": ("NMDC.NS", "Metals")
}

# =========================================================
# CACHE DATA
# =========================================================
@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock_data(symbol, period="1y", interval="1d"):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval, auto_adjust=False)
        if df is None or df.empty:
            return pd.DataFrame()
        return df.reset_index()
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600, show_spinner=False)
def fetch_stock_info(symbol):
    try:
        info = yf.Ticker(symbol).info
        return info if info else {}
    except:
        return {}

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_financials(symbol):
    try:
        t = yf.Ticker(symbol)
        return {
            "financials": safe_df(t.financials),
            "balance_sheet": safe_df(t.balance_sheet),
            "cashflow": safe_df(t.cashflow)
        }
    except:
        return {
            "financials": pd.DataFrame(),
            "balance_sheet": pd.DataFrame(),
            "cashflow": pd.DataFrame()
        }

# =========================================================
# INDICATORS
# =========================================================
def add_indicators(df):
    if df.empty:
        return df
    d = df.copy()

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col not in d.columns:
            d[col] = np.nan

    d["SMA20"] = d["Close"].rolling(20).mean()
    d["SMA50"] = d["Close"].rolling(50).mean()
    d["SMA200"] = d["Close"].rolling(200).mean()

    delta = d["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    d["RSI"] = 100 - (100 / (1 + rs))

    ema12 = d["Close"].ewm(span=12, adjust=False).mean()
    ema26 = d["Close"].ewm(span=26, adjust=False).mean()
    d["MACD"] = ema12 - ema26
    d["Signal"] = d["MACD"].ewm(span=9, adjust=False).mean()

    high_low = d["High"] - d["Low"]
    high_close = np.abs(d["High"] - d["Close"].shift())
    low_close = np.abs(d["Low"] - d["Close"].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    d["ATR"] = tr.rolling(14).mean()

    d["BB_MID"] = d["Close"].rolling(20).mean()
    bb_std = d["Close"].rolling(20).std()
    d["BB_UPPER"] = d["BB_MID"] + 2 * bb_std
    d["BB_LOWER"] = d["BB_MID"] - 2 * bb_std

    d["VOL20"] = d["Volume"].rolling(20).mean()
    d["Prev20High"] = d["High"].rolling(20).max().shift(1)
    d["Prev20Low"] = d["Low"].rolling(20).min().shift(1)
    d["ROC20"] = d["Close"].pct_change(20) * 100
    d["ROC50"] = d["Close"].pct_change(50) * 100
    d["Daily_Return"] = d["Close"].pct_change() * 100
    return d

# =========================================================
# PATTERNS / LEVELS / SIGNAL
# =========================================================
def detect_candlestick_patterns(df):
    if df.empty or len(df) < 2:
        return []
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    patterns = []

    o, h, l, c = map(safe_float, [latest["Open"], latest["High"], latest["Low"], latest["Close"]])
    po, pc = map(safe_float, [prev["Open"], prev["Close"]])

    body = abs(c - o)
    candle_range = max(0.01, h - l)
    upper_wick = h - max(o, c)
    lower_wick = min(o, c) - l

    if body / candle_range < 0.1:
        patterns.append("Doji")
    if lower_wick > body * 2 and upper_wick < max(body * 1.2, 0.01):
        patterns.append("Hammer")
    if pc < po and c > o and c > po and o < pc:
        patterns.append("Bullish Engulfing")
    if pc > po and c < o and o > pc and c < po:
        patterns.append("Bearish Engulfing")
    return patterns

def calculate_support_resistance(df, window=20):
    if df.empty or len(df) < window:
        return None, None
    recent = df.tail(window)
    return recent["Low"].min(), recent["High"].max()

def generate_signal(df):
    if df.empty or len(df) < 60:
        return "NO DATA", 0, []

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    score = 0
    reasons = []

    close = safe_float(latest["Close"])
    sma20 = safe_float(latest["SMA20"])
    sma50 = safe_float(latest["SMA50"])
    sma200 = safe_float(latest["SMA200"])
    rsi = safe_float(latest["RSI"])
    macd = safe_float(latest["MACD"])
    signal = safe_float(latest["Signal"])
    volume = safe_float(latest["Volume"])
    avg_volume = safe_float(latest["VOL20"])
    prev20high = safe_float(latest["Prev20High"])
    prev_close = safe_float(prev["Close"])
    roc20 = safe_float(latest["ROC20"])
    roc50 = safe_float(latest["ROC50"])

    if close > sma20 > sma50:
        score += 18; reasons.append("Price > SMA20 > SMA50")
    if sma50 > 0 and close > sma50 > sma200:
        score += 14; reasons.append("Bullish medium-term trend")
    if sma200 > 0 and close > sma200:
        score += 8; reasons.append("Above SMA200")
    if 52 <= rsi <= 68:
        score += 12; reasons.append("Healthy RSI zone")
    elif rsi > 70:
        score -= 4; reasons.append("RSI overbought")
    elif 35 <= rsi <= 45:
        score += 4; reasons.append("Early recovery RSI")
    if macd > signal:
        score += 14; reasons.append("MACD bullish crossover")

    vol_ratio = (volume / avg_volume) if avg_volume > 0 else 0
    if vol_ratio >= 1.8:
        score += 18; reasons.append("Strong volume expansion")
    elif vol_ratio >= 1.3:
        score += 10; reasons.append("Volume confirmation")

    if prev20high > 0 and close > prev20high:
        score += 18; reasons.append("20-day breakout")
    if roc20 > 5:
        score += 8; reasons.append("Strong 20D momentum")
    if roc50 > 10:
        score += 8; reasons.append("Strong 50D momentum")

    if prev_close > 0:
        day_change = ((close - prev_close) / prev_close) * 100
        if day_change > 2:
            score += 8; reasons.append("Strong daily price action")
        elif day_change < -2:
            score -= 6; reasons.append("Weak daily action")

    if score >= 78:
        signal_text = "STRONG BUY"
    elif score >= 55:
        signal_text = "BUY"
    elif score >= 35:
        signal_text = "WATCHLIST"
    else:
        signal_text = "AVOID"

    return signal_text, score, reasons

def calculate_trade_levels(df, capital=100000, risk_pct=1.0):
    if df.empty:
        return {}
    latest = df.iloc[-1]
    close = safe_float(latest["Close"])
    atr = safe_float(latest["ATR"])
    if close <= 0:
        return {}
    if atr <= 0:
        atr = close * 0.02

    support, resistance = calculate_support_resistance(df, 20)

    entry = close
    sl = max(0.01, close - (1.5 * atr))
    if support is not None and support > 0:
        sl = max(0.01, min(sl, support * 0.995))

    target1 = close + (2 * atr)
    target2 = close + (4 * atr)
    if resistance is not None and resistance > close:
        target1 = max(target1, resistance)

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
        "risk_amount": risk_amount,
        "rr1": (target1 - entry) / risk_per_share,
        "rr2": (target2 - entry) / risk_per_share
    }

# =========================================================
# CHART
# =========================================================
def plot_candlestick(df, symbol):
    if df.empty:
        return None
    required_cols = {"Date", "Open", "High", "Low", "Close", "Volume"}
    if not required_cols.issubset(set(df.columns)):
        return None

    chart_df = df.copy()
    vol_colors = np.where(chart_df["Close"] >= chart_df["Open"], "#22c55e", "#ef4444")

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.035,
        row_heights=[0.64, 0.16, 0.20]
    )

    fig.add_trace(
        go.Candlestick(
            x=chart_df["Date"],
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            name="Price",
            increasing_line_color="#22c55e",
            decreasing_line_color="#ef4444",
            increasing_fillcolor="#22c55e",
            decreasing_fillcolor="#ef4444"
        ),
        row=1, col=1
    )

    for col, name, color in [
        ("SMA20", "SMA20", "#38bdf8"),
        ("SMA50", "SMA50", "#f59e0b"),
        ("SMA200", "SMA200", "#a78bfa")
    ]:
        if col in chart_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=chart_df["Date"],
                    y=chart_df[col],
                    mode="lines",
                    name=name,
                    line=dict(width=2.2, color=color)
                ),
                row=1, col=1
            )

    if "BB_UPPER" in chart_df.columns:
        fig.add_trace(go.Scatter(
            x=chart_df["Date"], y=chart_df["BB_UPPER"], mode="lines",
            name="BB Upper", line=dict(width=1.1, color="rgba(148,163,184,0.55)")
        ), row=1, col=1)

    if "BB_LOWER" in chart_df.columns:
        fig.add_trace(go.Scatter(
            x=chart_df["Date"], y=chart_df["BB_LOWER"], mode="lines",
            name="BB Lower", line=dict(width=1.1, color="rgba(148,163,184,0.55)")
        ), row=1, col=1)

    fig.add_trace(
        go.Bar(
            x=chart_df["Date"],
            y=chart_df["Volume"],
            name="Volume",
            marker_color=vol_colors,
            opacity=0.9
        ),
        row=2, col=1
    )

    if "RSI" in chart_df.columns:
        fig.add_trace(
            go.Scatter(
                x=chart_df["Date"],
                y=chart_df["RSI"],
                mode="lines",
                name="RSI",
                line=dict(width=2.2, color="#22d3ee")
            ),
            row=3, col=1
        )
        fig.add_hline(y=70, line_dash="dot", line_color="rgba(239,68,68,0.7)", row=3, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="rgba(34,197,94,0.7)", row=3, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="rgba(148,163,184,0.35)", row=3, col=1)

    fig.update_layout(
        title=f"{symbol} | Nile Chart",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=900,
        margin=dict(l=18, r=18, t=58, b=18),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.85)",
        font=dict(color="#e5e7eb", size=13)
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148,163,184,0.08)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.08)", zeroline=False)
    return fig

# =========================================================
# SCANNER / SECTOR / PORTFOLIO
# =========================================================
def run_scanner(stock_map, period="6mo"):
    results = []
    progress = st.progress(0)
    total = len(stock_map)

    for i, (name, (symbol, sector)) in enumerate(stock_map.items(), start=1):
        try:
            df = fetch_stock_data(symbol, period=period)
            if df.empty or len(df) < 60:
                progress.progress(i / total)
                continue

            df = add_indicators(df)
            signal, score, reasons = generate_signal(df)

            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest

            close = safe_float(latest["Close"])
            prev_close = safe_float(prev["Close"])
            change_pct = ((close - prev_close) / prev_close * 100) if prev_close > 0 else 0
            rsi = safe_float(latest["RSI"])
            volume = safe_float(latest["Volume"])
            avg_vol = safe_float(latest["VOL20"])
            vol_ratio = (volume / avg_vol) if avg_vol > 0 else 0

            patterns = detect_candlestick_patterns(df)
            support, resistance = calculate_support_resistance(df)
            breakout_flag = "YES" if safe_float(latest["Prev20High"]) > 0 and close > safe_float(latest["Prev20High"]) else "NO"

            results.append({
                "Stock": name,
                "Symbol": symbol,
                "Sector": sector,
                "Price": round(close, 2),
                "Change %": round(change_pct, 2),
                "RSI": round(rsi, 2),
                "Vol Ratio": round(vol_ratio, 2),
                "ROC20": round(safe_float(latest["ROC20"]), 2),
                "ROC50": round(safe_float(latest["ROC50"]), 2),
                "Breakout": breakout_flag,
                "Support": round(safe_float(support), 2),
                "Resistance": round(safe_float(resistance), 2),
                "Pattern": ", ".join(patterns) if patterns else "-",
                "Signal": signal,
                "Score": score,
                "Reason": " | ".join(reasons[:4]) if reasons else "No clear setup"
            })
        except:
            pass
        progress.progress(i / total)

    progress.empty()

    if not results:
        return pd.DataFrame()

    out = pd.DataFrame(results)
    signal_order = {"STRONG BUY": 4, "BUY": 3, "WATCHLIST": 2, "AVOID": 1}
    out["SignalRank"] = out["Signal"].map(signal_order).fillna(0)
    out = out.sort_values(by=["SignalRank", "Score", "Vol Ratio", "ROC20"], ascending=[False, False, False, False]).drop(columns=["SignalRank"])
    return out

def build_sector_summary(scan_df):
    if scan_df.empty:
        return pd.DataFrame()

    temp = scan_df.copy()
    temp["Bullish"] = temp["Signal"].isin(["STRONG BUY", "BUY"]).astype(int)

    summary = temp.groupby("Sector").agg(
        Stocks=("Stock", "count"),
        AvgScore=("Score", "mean"),
        AvgChange=("Change %", "mean"),
        AvgROC20=("ROC20", "mean"),
        BullishCount=("Bullish", "sum")
    ).reset_index()

    summary["Bullish %"] = np.where(summary["Stocks"] > 0, (summary["BullishCount"] / summary["Stocks"]) * 100, 0)
    summary["AvgScore"] = summary["AvgScore"].round(2)
    summary["AvgChange"] = summary["AvgChange"].round(2)
    summary["AvgROC20"] = summary["AvgROC20"].round(2)
    summary["Bullish %"] = summary["Bullish %"].round(2)

    return summary.sort_values(by=["Bullish %", "AvgScore", "AvgROC20"], ascending=[False, False, False])

def build_portfolio_tracker(symbols, total_capital):
    rows = []
    valid_symbols = [s.strip().upper() for s in symbols if s and s.strip()]
    if not valid_symbols:
        return pd.DataFrame()

    allocation = total_capital / len(valid_symbols)

    for sym in valid_symbols:
        try:
            df = fetch_stock_data(sym, period="6mo")
            if df.empty:
                continue
            df = add_indicators(df)
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest

            price = safe_float(latest["Close"])
            prev_close = safe_float(prev["Close"])
            chg_pct = ((price - prev_close) / prev_close * 100) if prev_close > 0 else 0
            qty = int(allocation / price) if price > 0 else 0
            value = qty * price
            signal, score, _ = generate_signal(df)

            rows.append({
                "Symbol": sym,
                "Price": round(price, 2),
                "Day Change %": round(chg_pct, 2),
                "Allocation ₹": round(allocation, 2),
                "Qty": qty,
                "Current Value ₹": round(value, 2),
                "Signal": signal,
                "Score": score
            })
        except:
            continue

    return pd.DataFrame(rows) if rows else pd.DataFrame()

# =========================================================
# SESSION STATE
# =========================================================
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## ⚙️ Nile")
    st.caption("Analysis")

    mode = st.radio(
        "Select Module",
        [
            "Single Stock Analysis",
            "100 Stock Scanner",
            "Swing Trade Finder",
            "Portfolio Builder",
            "Portfolio Tracker",
            "Watchlist",
            "Sector Dashboard"
        ],
        key="main_mode_nile"
    )

    stock_name = st.selectbox(
        "Select Stock",
        list(DEFAULT_STOCKS.keys()),
        index=0,
        key="stock_select_nile"
    )

    default_symbol = DEFAULT_STOCKS[stock_name][0]

    custom_symbol = st.text_input(
        "Or Enter Custom NSE Symbol (e.g. IRFC.NS)",
        value="",
        key="custom_symbol_nile"
    ).strip().upper()

    final_symbol = custom_symbol if custom_symbol else default_symbol

    period = st.selectbox(
        "Chart Period",
        ["3mo", "6mo", "1y", "2y", "5y"],
        index=2,
        key="period_nile"
    )

    capital = st.number_input(
        "Capital (₹)",
        min_value=10000,
        max_value=100000000,
        value=100000,
        step=10000,
        key="capital_nile"
    )

    risk_pct = st.slider(
        "Risk per Trade (%)",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.5,
        key="risk_nile"
    )

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="hero-box">', unsafe_allow_html=True)
render_logo()
st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# MODULE 1: SINGLE STOCK ANALYSIS
# =========================================================
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
    fundamentals = fetch_stock_info(final_symbol)
    patterns = detect_candlestick_patterns(df)
    support, resistance = calculate_support_resistance(df)

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    ltp = safe_float(latest["Close"])
    prev_close = safe_float(prev["Close"])
    change_pct = ((ltp - prev_close) / prev_close * 100) if prev_close > 0 else 0
    vol_ratio = safe_float(latest["Volume"]) / max(safe_float(latest["VOL20"]), 1)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("LTP", fmt_currency(ltp), f"{change_pct:.2f}%")
    c2.metric("Signal", signal, f"Score: {score}")
    c3.metric("RSI", f"{safe_float(latest['RSI']):.2f}")
    c4.metric("MACD", f"{safe_float(latest['MACD']):.2f}")
    c5.metric("Vol Ratio", f"{vol_ratio:.2f}")
    c6.metric("ROC20", fmt_pct(safe_float(latest["ROC20"])))

    tabs = st.tabs(["📊 Chart", "🎯 Trade Setup", "🏢 Fundamentals", "📑 Financials", "🕯️ Pattern & Levels", "🧠 AI Summary"])

    with tabs[0]:
        fig = plot_candlestick(df.tail(260), final_symbol)
        if fig:
            st.plotly_chart(fig, use_container_width=True, key=unique_key("chart_nile", final_symbol))
        else:
            st.warning("Chart unavailable.")

    with tabs[1]:
        if trade:
            t1, t2, t3, t4 = st.columns(4)
            t1.metric("Entry", fmt_currency(trade["entry"]))
            t2.metric("Stop Loss", fmt_currency(trade["sl"]))
            t3.metric("Target 1", fmt_currency(trade["target1"]))
            t4.metric("Target 2", fmt_currency(trade["target2"]))

            t5, t6, t7, t8 = st.columns(4)
            t5.metric("Qty", trade["qty"])
            t6.metric("Capital Used", fmt_currency(trade["invested"]))
            t7.metric("Risk Amount", fmt_currency(trade["risk_amount"]))
            t8.metric("R:R (T1)", f"{trade['rr1']:.2f}")

    with tabs[2]:
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Market Cap", fmt_num(fundamentals.get("marketCap")))
        f2.metric("PE Ratio", fmt_num(fundamentals.get("trailingPE")))
        f3.metric("PB Ratio", fmt_num(fundamentals.get("priceToBook")))
        f4.metric("Dividend Yield", fmt_pct(safe_float(fundamentals.get("dividendYield")) * 100 if fundamentals.get("dividendYield") is not None else None))

        info_df = pd.DataFrame({
            "Field": ["Company", "Sector", "Industry", "52W High", "52W Low", "Book Value", "EPS", "Debt/Equity"],
            "Value": [
                fundamentals.get("longName", fundamentals.get("shortName", "N/A")),
                fundamentals.get("sector", "N/A"),
                fundamentals.get("industry", "N/A"),
                fmt_currency(fundamentals.get("fiftyTwoWeekHigh")),
                fmt_currency(fundamentals.get("fiftyTwoWeekLow")),
                fmt_num(fundamentals.get("bookValue")),
                fmt_num(fundamentals.get("trailingEps")),
                fmt_num(fundamentals.get("debtToEquity"))
            ]
        })
        st.dataframe(info_df, use_container_width=True, hide_index=True)

    with tabs[3]:
        fin = fetch_financials(final_symbol)
        sub = st.tabs(["P&L", "Balance Sheet", "Cash Flow"])

        with sub[0]:
            st.dataframe(fin["financials"], use_container_width=True) if not fin["financials"].empty else st.info("P&L data not available.")
        with sub[1]:
            st.dataframe(fin["balance_sheet"], use_container_width=True) if not fin["balance_sheet"].empty else st.info("Balance sheet data not available.")
        with sub[2]:
            st.dataframe(fin["cashflow"], use_container_width=True) if not fin["cashflow"].empty else st.info("Cash flow data not available.")

    with tabs[4]:
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Support", fmt_currency(support))
        p2.metric("Resistance", fmt_currency(resistance))
        p3.metric("20D Breakout", "YES" if ltp > safe_float(latest["Prev20High"]) > 0 else "NO")
        p4.metric("Patterns", ", ".join(patterns) if patterns else "None")

    with tabs[5]:
        st.success(f"Primary Signal: **{signal}** | Score: **{score}/100**")
        for r in reasons:
            st.write(f"- {r}")
        if st.button("➕ Add to Watchlist", key=unique_key("watch_nile", final_symbol)):
            if final_symbol not in st.session_state.watchlist:
                st.session_state.watchlist.append(final_symbol)
                st.success(f"{final_symbol} added to watchlist.")
            else:
                st.info(f"{final_symbol} already in watchlist.")

# =========================================================
# MODULE 2: 100 STOCK SCANNER
# =========================================================
elif mode == "100 Stock Scanner":
    st.markdown('<div class="section-title">🚀 100 Stock Scanner</div>', unsafe_allow_html=True)

    if st.button("🔍 Run 100 Stock Scanner", key="scanner_nile_100"):
        with st.spinner("Scanning 100 stocks... please wait..."):
            scan_df = run_scanner(DEFAULT_STOCKS, period="6mo")

        if scan_df.empty:
            st.warning("No scanner results available.")
        else:
            st.success(f"Scan completed successfully. {len(scan_df)} stocks evaluated.")
            st.dataframe(scan_df, use_container_width=True, hide_index=True)

            csv_data = to_csv_download(scan_df)
            if csv_data:
                st.download_button(
                    "⬇️ Download Scanner CSV",
                    data=csv_data,
                    file_name="nile_100_stock_scanner.csv",
                    mime="text/csv",
                    key="download_scanner_nile"
                )

# =========================================================
# MODULE 3: SWING TRADE FINDER
# =========================================================
elif mode == "Swing Trade Finder":
    st.markdown('<div class="section-title">🎯 Swing Trade Finder</div>', unsafe_allow_html=True)

    if st.button("⚡ Find Best Swing Trades", key="swing_nile"):
        with st.spinner("Finding best swing setups..."):
            scan_df = run_scanner(DEFAULT_STOCKS, period="6mo")

        if scan_df.empty:
            st.warning("No swing candidates available.")
        else:
            swing_df = scan_df[
                (scan_df["Signal"].isin(["STRONG BUY", "BUY"])) &
                (scan_df["RSI"].between(50, 70)) &
                (scan_df["Vol Ratio"] >= 1.0) &
                (scan_df["ROC20"] > 0)
            ].copy()

            if swing_df.empty:
                st.info("No ideal swing setups right now.")
            else:
                st.success(f"Found {len(swing_df)} swing trade candidates.")
                st.dataframe(swing_df, use_container_width=True, hide_index=True)

# =========================================================
# MODULE 4: PORTFOLIO BUILDER
# =========================================================
elif mode == "Portfolio Builder":
    st.markdown('<div class="section-title">💼 Portfolio Builder</div>', unsafe_allow_html=True)

    total_capital = st.number_input("Portfolio Capital (₹)", 50000, 100000000, 500000, 50000, key="pf_cap_nile")
    top_n = st.slider("Number of Stocks", 3, 15, 8, key="pf_top_n_nile")

    if st.button("🧠 Build Smart Portfolio", key="build_pf_nile"):
        with st.spinner("Building portfolio from 100-stock universe..."):
            scan_df = run_scanner(DEFAULT_STOCKS, period="6mo")

        if scan_df.empty:
            st.warning("Unable to build portfolio.")
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

                out_df = filtered[["Stock", "Symbol", "Sector", "Signal", "Score", "Price", "Weight %", "Allocation ₹", "Qty Approx"]]
                st.success("Portfolio created successfully.")
                st.dataframe(out_df, use_container_width=True, hide_index=True)

# =========================================================
# MODULE 5: PORTFOLIO TRACKER
# =========================================================
elif mode == "Portfolio Tracker":
    st.markdown('<div class="section-title">📦 Portfolio Tracker</div>', unsafe_allow_html=True)

    cols1 = st.columns(4)
    cols2 = st.columns(4)
    defaults = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "", "", "", ""]
    syms = []
    for i in range(4):
        syms.append(cols1[i].text_input(f"Symbol {i+1}", value=defaults[i], key=f"trk1_{i}"))
    for i in range(4):
        syms.append(cols2[i].text_input(f"Symbol {i+5}", value=defaults[i+4], key=f"trk2_{i}"))

    total_capital = st.number_input("Tracker Capital (₹)", 50000, 100000000, 500000, 50000, key="tracker_cap_nile")

    if st.button("📊 Track Portfolio", key="track_pf_nile"):
        with st.spinner("Tracking portfolio..."):
            pf = build_portfolio_tracker(syms, total_capital)

        if pf.empty:
            st.warning("No valid portfolio data.")
        else:
            total_value = pf["Current Value ₹"].sum()
            total_alloc = pf["Allocation ₹"].sum()
            pnl = total_value - total_alloc
            pnl_pct = (pnl / total_alloc * 100) if total_alloc > 0 else 0

            p1, p2, p3 = st.columns(3)
            p1.metric("Allocated", fmt_currency(total_alloc))
            p2.metric("Current Value", fmt_currency(total_value))
            p3.metric("P&L", fmt_currency(pnl), f"{pnl_pct:.2f}%")

            st.dataframe(pf, use_container_width=True, hide_index=True)

# =========================================================
# MODULE 6: WATCHLIST
# =========================================================
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
                close = safe_float(latest["Close"])
                prev_close = safe_float(prev["Close"])
                chg_pct = ((close - prev_close) / prev_close * 100) if prev_close > 0 else 0

                watch_results.append({
                    "Symbol": sym,
                    "Price": round(close, 2),
                    "Change %": round(chg_pct, 2),
                    "RSI": round(safe_float(latest["RSI"]), 2),
                    "ROC20": round(safe_float(latest["ROC20"]), 2),
                    "Signal": signal,
                    "Score": score
                })
            except:
                continue

        if watch_results:
            watch_df = pd.DataFrame(watch_results)
            st.dataframe(watch_df, use_container_width=True, hide_index=True)
            if st.button("🗑️ Clear Watchlist", key="clear_watch_nile"):
                st.session_state.watchlist = []
                st.success("Watchlist cleared.")
        else:
            st.warning("Unable to fetch watchlist data.")

# =========================================================
# MODULE 7: SECTOR DASHBOARD
# =========================================================
elif mode == "Sector Dashboard":
    st.markdown('<div class="section-title">🏭 Sector Dashboard</div>', unsafe_allow_html=True)

    if st.button("📈 Build Sector Dashboard", key="sector_nile"):
        with st.spinner("Analyzing sectors from 100 stocks..."):
            scan_df = run_scanner(DEFAULT_STOCKS, period="6mo")
            sector_df = build_sector_summary(scan_df)

        if sector_df.empty:
            st.warning("Sector data unavailable.")
        else:
            st.dataframe(sector_df, use_container_width=True, hide_index=True)

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption(f"Nile | Last Loaded: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

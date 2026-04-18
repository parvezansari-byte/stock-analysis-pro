# FINAL V10 FULL FUNDAMENTAL + FULL TECHNICAL ELITE CLOUD SAFE SINGLE FULL app.py
# Streamlit Cloud Safe | Single File | Paste-Ready
# --------------------------------------------------
# Features:
# - Indian stocks via yfinance (NSE/BSE supported using .NS / .BO suffix)
# - FULL Fundamental Dashboard
# - FULL Technical Dashboard
# - Scorecards + Signal Engine + Watchlist
# - Attractive UI (custom CSS, cards, gradients)
# - Cloud-safe (no unsupported local dependencies)
#
# Recommended requirements.txt:
# streamlit
# yfinance
# pandas
# numpy
# plotly
#
# Run:
# streamlit run app.py

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="FINAL V10 ELITE STOCK ANALYZER",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# CUSTOM CSS (ELITE LOOK)
# -------------------------------
st.markdown("""
<style>
:root {
    --bg1: #0b1220;
    --bg2: #111827;
    --card: rgba(255,255,255,0.06);
    --card2: rgba(255,255,255,0.09);
    --border: rgba(255,255,255,0.08);
    --text: #f9fafb;
    --muted: #cbd5e1;
    --green: #10b981;
    --red: #ef4444;
    --blue: #60a5fa;
    --gold: #f59e0b;
}
.stApp {
    background: radial-gradient(circle at top right, #1e3a8a 0%, #0f172a 35%, #020617 100%);
    color: var(--text);
}
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}
.main-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #93c5fd, #c4b5fd, #f9a8d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.sub-title {
    color: #d1d5db;
    font-size: 1rem;
    margin-bottom: 1rem;
}
.card {
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}
.metric-card {
    background: linear-gradient(135deg, rgba(59,130,246,0.18), rgba(168,85,247,0.12));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 14px;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0,0,0,0.2);
}
.metric-label {
    font-size: 0.9rem;
    color: #cbd5e1;
}
.metric-value {
    font-size: 1.35rem;
    font-weight: 800;
    color: white;
}
.section-title {
    font-size: 1.25rem;
    font-weight: 800;
    margin: 0.5rem 0 0.8rem 0;
    color: #e2e8f0;
}
.score-box {
    padding: 16px;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(16,185,129,0.16), rgba(59,130,246,0.12));
    border: 1px solid rgba(255,255,255,0.08);
    text-align: center;
}
.small-note {
    color: #cbd5e1;
    font-size: 0.82rem;
}
hr {
    border-color: rgba(255,255,255,0.08) !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# HELPERS
# -------------------------------
def fmt_num(x, digits=2):
    try:
        if x is None or (isinstance(x, float) and np.isnan(x)):
            return "N/A"
        return f"{x:,.{digits}f}"
    except:
        return "N/A"


def fmt_cr(x):
    try:
        if x is None or pd.isna(x):
            return "N/A"
        return f"₹ {x/1e7:,.2f} Cr"
    except:
        return "N/A"


def safe_get(d, keys, default=np.nan):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


def add_nse_suffix(symbol: str):
    symbol = symbol.strip().upper()
    if symbol.endswith('.NS') or symbol.endswith('.BO'):
        return symbol
    return symbol + '.NS'


@st.cache_data(ttl=900)
def get_stock_data(symbol, period='2y', interval='1d'):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period, interval=interval, auto_adjust=False)
    info = ticker.info
    financials = ticker.financials if hasattr(ticker, 'financials') else pd.DataFrame()
    balance_sheet = ticker.balance_sheet if hasattr(ticker, 'balance_sheet') else pd.DataFrame()
    cashflow = ticker.cashflow if hasattr(ticker, 'cashflow') else pd.DataFrame()
    quarterly_financials = ticker.quarterly_financials if hasattr(ticker, 'quarterly_financials') else pd.DataFrame()
    return hist, info, financials, balance_sheet, cashflow, quarterly_financials


# -------------------------------
# TECHNICAL INDICATORS
# -------------------------------
def sma(series, n):
    return series.rolling(n).mean()


def ema(series, n):
    return series.ewm(span=n, adjust=False).mean()


def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(series):
    ema12 = ema(series, 12)
    ema26 = ema(series, 26)
    macd_line = ema12 - ema26
    signal = ema(macd_line, 9)
    hist = macd_line - signal
    return macd_line, signal, hist


def bollinger(series, period=20, std=2):
    mid = sma(series, period)
    sd = series.rolling(period).std()
    upper = mid + std * sd
    lower = mid - std * sd
    return upper, mid, lower


def atr(df, period=14):
    high = df['High']
    low = df['Low']
    close = df['Close']
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def stochastic(df, period=14, smooth_k=3, smooth_d=3):
    low_min = df['Low'].rolling(period).min()
    high_max = df['High'].rolling(period).max()
    k = 100 * ((df['Close'] - low_min) / (high_max - low_min).replace(0, np.nan))
    k = k.rolling(smooth_k).mean()
    d = k.rolling(smooth_d).mean()
    return k, d


def adx(df, period=14):
    high = df['High']
    low = df['Low']
    close = df['Close']

    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0.0)
    minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0.0)

    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)

    atr_val = tr.rolling(period).mean()
    plus_di = 100 * (pd.Series(plus_dm, index=df.index).rolling(period).mean() / atr_val.replace(0, np.nan))
    minus_di = 100 * (pd.Series(minus_dm, index=df.index).rolling(period).mean() / atr_val.replace(0, np.nan))
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)) * 100
    adx_val = dx.rolling(period).mean()
    return adx_val, plus_di, minus_di


def obv(df):
    direction = np.sign(df['Close'].diff()).fillna(0)
    return (direction * df['Volume']).fillna(0).cumsum()


def mfi(df, period=14):
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    mf = tp * df['Volume']
    positive = np.where(tp > tp.shift(1), mf, 0)
    negative = np.where(tp < tp.shift(1), mf, 0)
    pos_mf = pd.Series(positive, index=df.index).rolling(period).sum()
    neg_mf = pd.Series(negative, index=df.index).rolling(period).sum()
    ratio = pos_mf / neg_mf.replace(0, np.nan)
    return 100 - (100 / (1 + ratio))


def cci(df, period=20):
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    sma_tp = tp.rolling(period).mean()
    mad = tp.rolling(period).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    return (tp - sma_tp) / (0.015 * mad.replace(0, np.nan))


def williams_r(df, period=14):
    hh = df['High'].rolling(period).max()
    ll = df['Low'].rolling(period).min()
    return -100 * ((hh - df['Close']) / (hh - ll).replace(0, np.nan))


def add_indicators(df):
    df = df.copy()
    df['SMA20'] = sma(df['Close'], 20)
    df['SMA50'] = sma(df['Close'], 50)
    df['SMA200'] = sma(df['Close'], 200)
    df['EMA20'] = ema(df['Close'], 20)
    df['EMA50'] = ema(df['Close'], 50)
    df['RSI14'] = rsi(df['Close'], 14)
    df['MACD'], df['MACD_SIGNAL'], df['MACD_HIST'] = macd(df['Close'])
    df['BB_UPPER'], df['BB_MID'], df['BB_LOWER'] = bollinger(df['Close'])
    df['ATR14'] = atr(df, 14)
    df['STOCH_K'], df['STOCH_D'] = stochastic(df)
    df['ADX14'], df['PLUS_DI'], df['MINUS_DI'] = adx(df)
    df['OBV'] = obv(df)
    df['MFI14'] = mfi(df)
    df['CCI20'] = cci(df)
    df['WILLR14'] = williams_r(df)
    return df


# -------------------------------
# FUNDAMENTAL SCORING
# -------------------------------
def calculate_fundamental_score(info):
    score = 0
    max_score = 10

    roe = safe_get(info, ['returnOnEquity'])
    de = safe_get(info, ['debtToEquity'])
    pe = safe_get(info, ['trailingPE', 'forwardPE'])
    pb = safe_get(info, ['priceToBook'])
    pm = safe_get(info, ['profitMargins'])
    rg = safe_get(info, ['revenueGrowth'])
    eg = safe_get(info, ['earningsGrowth'])
    cr = safe_get(info, ['currentRatio'])
    dy = safe_get(info, ['dividendYield'])

    if pd.notna(roe) and roe > 0.15: score += 1
    if pd.notna(de) and de < 100: score += 1
    if pd.notna(pe) and pe < 30: score += 1
    if pd.notna(pb) and pb < 6: score += 1
    if pd.notna(pm) and pm > 0.10: score += 1
    if pd.notna(rg) and rg > 0.10: score += 1
    if pd.notna(eg) and eg > 0.10: score += 1
    if pd.notna(cr) and cr > 1: score += 1
    if pd.notna(dy) and dy > 0: score += 1
    if safe_get(info, ['marketCap']) and safe_get(info, ['marketCap']) > 1e10: score += 1

    pct = round((score / max_score) * 100, 1)
    return score, max_score, pct


# -------------------------------
# TECHNICAL SCORING
# -------------------------------
def calculate_technical_score(df):
    latest = df.iloc[-1]
    score = 0
    max_score = 10

    if latest['Close'] > latest['SMA20']: score += 1
    if latest['Close'] > latest['SMA50']: score += 1
    if latest['Close'] > latest['SMA200']: score += 1
    if pd.notna(latest['RSI14']) and 45 <= latest['RSI14'] <= 70: score += 1
    if latest['MACD'] > latest['MACD_SIGNAL']: score += 1
    if latest['STOCH_K'] > latest['STOCH_D']: score += 1
    if pd.notna(latest['ADX14']) and latest['ADX14'] > 20: score += 1
    if latest['PLUS_DI'] > latest['MINUS_DI']: score += 1
    if latest['Close'] > latest['BB_MID']: score += 1
    if pd.notna(latest['MFI14']) and 40 <= latest['MFI14'] <= 80: score += 1

    pct = round((score / max_score) * 100, 1)
    return score, max_score, pct


def get_signal(df, f_score_pct):
    latest = df.iloc[-1]
    tech_score = calculate_technical_score(df)[2]
    total = (tech_score * 0.6) + (f_score_pct * 0.4)

    if total >= 80:
        signal = "STRONG BUY"
    elif total >= 65:
        signal = "BUY"
    elif total >= 50:
        signal = "HOLD"
    elif total >= 35:
        signal = "WEAK"
    else:
        signal = "AVOID"

    stop_loss = latest['Close'] - (1.5 * latest['ATR14']) if pd.notna(latest['ATR14']) else np.nan
    target1 = latest['Close'] + (2 * latest['ATR14']) if pd.notna(latest['ATR14']) else np.nan
    target2 = latest['Close'] + (4 * latest['ATR14']) if pd.notna(latest['ATR14']) else np.nan

    return signal, total, stop_loss, target1, target2


# -------------------------------
# CHARTS
# -------------------------------
def candlestick_chart(df, symbol):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03,
                        row_heights=[0.6, 0.2, 0.2])

    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='SMA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], name='SMA50'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], name='SMA200'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_UPPER'], name='BB Upper', line=dict(dash='dot')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_LOWER'], name='BB Lower', line=dict(dash='dot')), row=1, col=1)

    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI14'], name='RSI'), row=3, col=1)

    fig.update_layout(
        title=f"{symbol} Price + Volume + RSI",
        template='plotly_dark',
        height=850,
        xaxis_rangeslider_visible=False,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def indicator_chart(df):
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03,
                        row_heights=[0.25, 0.25, 0.25, 0.25])

    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_SIGNAL'], name='Signal'), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_HIST'], name='Hist'), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['STOCH_K'], name='%K'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['STOCH_D'], name='%D'), row=2, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['ADX14'], name='ADX'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['PLUS_DI'], name='+DI'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MINUS_DI'], name='-DI'), row=3, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['MFI14'], name='MFI'), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['CCI20'], name='CCI'), row=4, col=1)

    fig.update_layout(template='plotly_dark', height=900, title='Advanced Technical Indicators')
    return fig


# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.markdown("## ⚙️ Control Panel")
default_watchlist = "RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK, SBIN, LT, ITC, AXISBANK, BHARTIARTL"

symbol_input = st.sidebar.text_input("Enter NSE/BSE Symbol", value="RELIANCE")
symbol = add_nse_suffix(symbol_input)
period = st.sidebar.selectbox("History Period", ['6mo', '1y', '2y', '5y'], index=2)
watchlist_text = st.sidebar.text_area("Watchlist (comma separated, without suffix)", value=default_watchlist, height=120)
show_raw = st.sidebar.checkbox("Show Raw Data", value=False)

# -------------------------------
# HEADER
# -------------------------------
st.markdown('<div class="main-title">FINAL V10 FULL FUNDAMENTAL + FULL TECHNICAL ELITE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Cloud-safe single file stock analysis system for Indian markets (NSE/BSE) • Fundamental + Technical + Scoring + Signal Engine</div>', unsafe_allow_html=True)

# -------------------------------
# MAIN STOCK ANALYSIS
# -------------------------------
try:
    hist, info, financials, balance_sheet, cashflow, quarterly_financials = get_stock_data(symbol, period=period)

    if hist.empty:
        st.error("No price data found. Try correct symbol like RELIANCE, TCS, INFY, HDFCBANK or use suffix .NS/.BO")
        st.stop()

    df = add_indicators(hist)
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    f_score, f_max, f_pct = calculate_fundamental_score(info)
    t_score, t_max, t_pct = calculate_technical_score(df)
    signal, total_score, stop_loss, target1, target2 = get_signal(df, f_pct)

    company_name = safe_get(info, ['longName', 'shortName'], symbol)
    sector = safe_get(info, ['sector'], 'N/A')
    industry = safe_get(info, ['industry'], 'N/A')
    cmp = latest['Close']
    change = cmp - prev['Close']
    change_pct = (change / prev['Close'] * 100) if prev['Close'] else 0

    # Top Summary Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, 'Company', company_name),
        (c2, 'CMP', f"₹ {fmt_num(cmp)}"),
        (c3, 'Change %', f"{fmt_num(change_pct)}%"),
        (c4, 'Fundamental', f"{f_pct}%"),
        (c5, 'Technical', f"{t_pct}%"),
    ]
    for col, label, value in cards:
        with col:
            st.markdown(f'''<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Signal Box
    st.markdown(f'''
    <div class="score-box">
        <div class="metric-label">Overall Signal</div>
        <div class="metric-value">{signal}</div>
        <div class="small-note">Composite Score: {fmt_num(total_score)}% | Stop Loss: ₹ {fmt_num(stop_loss)} | Target 1: ₹ {fmt_num(target1)} | Target 2: ₹ {fmt_num(target2)}</div>
    </div>
    ''', unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        '📊 Price Chart', '📈 Technical', '🏦 Fundamental', '🧠 Decision Engine', '📋 Watchlist Scanner'
    ])

    with tab1:
        st.markdown('<div class="section-title">Candlestick + Moving Averages + Bollinger + Volume + RSI</div>', unsafe_allow_html=True)
        st.plotly_chart(candlestick_chart(df, symbol), use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">Advanced Technical Indicators</div>', unsafe_allow_html=True)
        t1, t2, t3, t4, t5 = st.columns(5)
        tech_metrics = [
            ('RSI 14', latest['RSI14']),
            ('MACD', latest['MACD']),
            ('ADX 14', latest['ADX14']),
            ('MFI 14', latest['MFI14']),
            ('ATR 14', latest['ATR14'])
        ]
        for col, (lab, val) in zip([t1,t2,t3,t4,t5], tech_metrics):
            with col:
                st.markdown(f'''<div class="metric-card"><div class="metric-label">{lab}</div><div class="metric-value">{fmt_num(val)}</div></div>''', unsafe_allow_html=True)

        st.plotly_chart(indicator_chart(df), use_container_width=True)

        tech_df = pd.DataFrame({
            'Indicator': ['Close vs SMA20', 'Close vs SMA50', 'Close vs SMA200', 'RSI', 'MACD', 'Stochastic', 'ADX', 'DI Trend', 'BB Mid', 'MFI'],
            'Status': [
                'Bullish' if latest['Close'] > latest['SMA20'] else 'Bearish',
                'Bullish' if latest['Close'] > latest['SMA50'] else 'Bearish',
                'Bullish' if latest['Close'] > latest['SMA200'] else 'Bearish',
                'Healthy' if 45 <= latest['RSI14'] <= 70 else ('Overbought' if latest['RSI14'] > 70 else 'Weak'),
                'Bullish' if latest['MACD'] > latest['MACD_SIGNAL'] else 'Bearish',
                'Bullish' if latest['STOCH_K'] > latest['STOCH_D'] else 'Bearish',
                'Strong Trend' if latest['ADX14'] > 20 else 'Weak Trend',
                'Bullish' if latest['PLUS_DI'] > latest['MINUS_DI'] else 'Bearish',
                'Bullish' if latest['Close'] > latest['BB_MID'] else 'Bearish',
                'Healthy' if 40 <= latest['MFI14'] <= 80 else 'Extreme'
            ]
        })
        st.dataframe(tech_df, use_container_width=True)

    with tab3:
        st.markdown('<div class="section-title">Full Fundamental Analysis</div>', unsafe_allow_html=True)

        f1, f2, f3, f4 = st.columns(4)
        fundamental_cards = [
            ('Market Cap', fmt_cr(safe_get(info, ['marketCap']))),
            ('PE Ratio', fmt_num(safe_get(info, ['trailingPE', 'forwardPE']))),
            ('PB Ratio', fmt_num(safe_get(info, ['priceToBook']))),
            ('ROE', f"{fmt_num(safe_get(info, ['returnOnEquity'])*100 if pd.notna(safe_get(info, ['returnOnEquity'])) else np.nan)}%"),
        ]
        for col, (lab, val) in zip([f1,f2,f3,f4], fundamental_cards):
            with col:
                st.markdown(f'''<div class="metric-card"><div class="metric-label">{lab}</div><div class="metric-value">{val}</div></div>''', unsafe_allow_html=True)

        f5, f6, f7, f8 = st.columns(4)
        fundamental_cards2 = [
            ('Debt/Equity', fmt_num(safe_get(info, ['debtToEquity']))),
            ('Profit Margin', f"{fmt_num(safe_get(info, ['profitMargins'])*100 if pd.notna(safe_get(info, ['profitMargins'])) else np.nan)}%"),
            ('Revenue Growth', f"{fmt_num(safe_get(info, ['revenueGrowth'])*100 if pd.notna(safe_get(info, ['revenueGrowth'])) else np.nan)}%"),
            ('Dividend Yield', f"{fmt_num(safe_get(info, ['dividendYield'])*100 if pd.notna(safe_get(info, ['dividendYield'])) else np.nan)}%"),
        ]
        for col, (lab, val) in zip([f5,f6,f7,f8], fundamental_cards2):
            with col:
                st.markdown(f'''<div class="metric-card"><div class="metric-label">{lab}</div><div class="metric-value">{val}</div></div>''', unsafe_allow_html=True)

        base_info = pd.DataFrame({
            'Field': ['Company', 'Sector', 'Industry', '52W High', '52W Low', 'Current Ratio', 'Quick Ratio', 'Book Value', 'EPS', 'Beta'],
            'Value': [
                company_name,
                sector,
                industry,
                fmt_num(safe_get(info, ['fiftyTwoWeekHigh'])),
                fmt_num(safe_get(info, ['fiftyTwoWeekLow'])),
                fmt_num(safe_get(info, ['currentRatio'])),
                fmt_num(safe_get(info, ['quickRatio'])),
                fmt_num(safe_get(info, ['bookValue'])),
                fmt_num(safe_get(info, ['trailingEps', 'forwardEps'])),
                fmt_num(safe_get(info, ['beta']))
            ]
        })
        st.dataframe(base_info, use_container_width=True)

        if not financials.empty:
            st.markdown('#### Annual Financials')
            st.dataframe(financials, use_container_width=True)
        if not balance_sheet.empty:
            st.markdown('#### Balance Sheet')
            st.dataframe(balance_sheet, use_container_width=True)
        if not cashflow.empty:
            st.markdown('#### Cash Flow')
            st.dataframe(cashflow, use_container_width=True)
        if not quarterly_financials.empty:
            st.markdown('#### Quarterly Financials')
            st.dataframe(quarterly_financials, use_container_width=True)

    with tab4:
        st.markdown('<div class="section-title">AI-Style Decision Engine (Rules Based)</div>', unsafe_allow_html=True)

        d1, d2, d3 = st.columns(3)
        with d1:
            st.markdown(f'''<div class="score-box"><div class="metric-label">Fundamental Score</div><div class="metric-value">{f_score}/{f_max}</div><div class="small-note">{f_pct}%</div></div>''', unsafe_allow_html=True)
        with d2:
            st.markdown(f'''<div class="score-box"><div class="metric-label">Technical Score</div><div class="metric-value">{t_score}/{t_max}</div><div class="small-note">{t_pct}%</div></div>''', unsafe_allow_html=True)
        with d3:
            st.markdown(f'''<div class="score-box"><div class="metric-label">Final Decision</div><div class="metric-value">{signal}</div><div class="small-note">Composite {fmt_num(total_score)}%</div></div>''', unsafe_allow_html=True)

        reasons = []
        risks = []

        if latest['Close'] > latest['SMA50']:
            reasons.append('Price is above 50 DMA (medium-term bullish structure).')
        else:
            risks.append('Price is below 50 DMA (medium-term weakness).')

        if latest['Close'] > latest['SMA200']:
            reasons.append('Price is above 200 DMA (long-term trend positive).')
        else:
            risks.append('Price is below 200 DMA (long-term caution).')

        if latest['MACD'] > latest['MACD_SIGNAL']:
            reasons.append('MACD bullish crossover / positive momentum.')
        else:
            risks.append('MACD below signal (momentum weak).')

        if pd.notna(latest['RSI14']) and latest['RSI14'] < 70:
            reasons.append('RSI not overheated.')
        elif pd.notna(latest['RSI14']):
            risks.append('RSI is overbought.')

        if f_pct >= 70:
            reasons.append('Fundamentals are strong based on profitability/growth/valuation mix.')
        elif f_pct < 40:
            risks.append('Fundamental quality is weak / incomplete.')

        st.markdown('#### Why it looks good')
        for r in reasons:
            st.success(r)

        st.markdown('#### Key risks')
        if risks:
            for r in risks:
                st.warning(r)
        else:
            st.info('No major rule-based risk flagged currently.')

        st.markdown('#### Trade Plan')
        plan_df = pd.DataFrame({
            'Metric': ['CMP', 'Signal', 'Stop Loss', 'Target 1', 'Target 2', 'ATR'],
            'Value': [
                f'₹ {fmt_num(cmp)}',
                signal,
                f'₹ {fmt_num(stop_loss)}',
                f'₹ {fmt_num(target1)}',
                f'₹ {fmt_num(target2)}',
                fmt_num(latest['ATR14'])
            ]
        })
        st.dataframe(plan_df, use_container_width=True)

    with tab5:
        st.markdown('<div class="section-title">Watchlist Scanner</div>', unsafe_allow_html=True)
        watchlist = [add_nse_suffix(x.strip()) for x in watchlist_text.split(',') if x.strip()]
        results = []

        progress = st.progress(0)
        for i, sym in enumerate(watchlist):
            try:
                h, inf, *_ = get_stock_data(sym, period='1y')
                if not h.empty and len(h) > 50:
                    h = add_indicators(h)
                    fs, fm, fp = calculate_fundamental_score(inf)
                    ts, tm, tp = calculate_technical_score(h)
                    sig, tot, sl, tg1, tg2 = get_signal(h, fp)
                    last = h.iloc[-1]
                    results.append({
                        'Symbol': sym,
                        'CMP': round(last['Close'], 2),
                        'Fundamental %': fp,
                        'Technical %': tp,
                        'Composite %': round(tot, 2),
                        'Signal': sig,
                        'RSI': round(last['RSI14'], 2) if pd.notna(last['RSI14']) else np.nan,
                        'ADX': round(last['ADX14'], 2) if pd.notna(last['ADX14']) else np.nan,
                        'Stop Loss': round(sl, 2) if pd.notna(sl) else np.nan,
                        'Target 1': round(tg1, 2) if pd.notna(tg1) else np.nan,
                        'Target 2': round(tg2, 2) if pd.notna(tg2) else np.nan,
                    })
            except:
                pass
            progress.progress((i + 1) / max(len(watchlist), 1))

        if results:
            res_df = pd.DataFrame(results).sort_values(by='Composite %', ascending=False)
            st.dataframe(res_df, use_container_width=True)
            st.download_button(
                '⬇️ Download Watchlist CSV',
                data=res_df.to_csv(index=False).encode('utf-8'),
                file_name='watchlist_scan.csv',
                mime='text/csv'
            )
        else:
            st.warning('No watchlist data could be loaded.')

    if show_raw:
        st.markdown('---')
        st.markdown('### Raw Price Data')
        st.dataframe(df.tail(300), use_container_width=True)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Tips: Use valid NSE symbols like RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, SBIN")

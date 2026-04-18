# FINAL V11.2 PRO INSTITUTIONAL ULTIMATE - SINGLE FILE STREAMLIT APP
# Features:
# - Sector Ranking
# - Relative Strength vs NIFTY
# - Sector Heatmap
# - Persistent Watchlist
# - Breakout Scanner
# - Swing Trade Levels
# - Portfolio Builder
# - Fundamental + Technical Analysis
# - Cloud-safe single file app.py

import os
import json
import math
import warnings
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")

# =========================
# PAGE CONFIG + THEME
# =========================
st.set_page_config(
    page_title="FINAL V11.2 PRO INSTITUTIONAL ULTIMATE",
    page_icon="📈",
    layout="wide",
)

st.markdown("""
<style>
.main {background: linear-gradient(180deg, #0b1220 0%, #111827 100%);} 
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
[data-testid="stMetricValue"] {font-size: 1.35rem;}
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 10px;
}
.small-note {font-size: 0.85rem; color: #9ca3af;}
</style>
""", unsafe_allow_html=True)

# =========================
# DATA UNIVERSE
# =========================
SECTOR_MAP = {
    "BANKING": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "INDUSINDBK.NS"],
    "IT": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTIM.NS"],
    "AUTO": ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "HEROMOTOCO.NS"],
    "PHARMA": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "LUPIN.NS", "TORNTPHARM.NS"],
    "FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS", "GODREJCP.NS"],
    "METALS": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "JINDALSTEL.NS", "NMDC.NS"],
    "ENERGY": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS", "IOC.NS", "GAIL.NS", "HINDPETRO.NS"],
    "INFRA": ["LT.NS", "ULTRACEMCO.NS", "ADANIPORTS.NS", "GRASIM.NS", "AMBUJACEM.NS", "SHREECEM.NS"],
    "FINANCIAL": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "SBILIFE.NS", "HDFCLIFE.NS", "ICICIPRULI.NS", "PFC.NS"],
}

DEFAULT_UNIVERSE = sorted({s for arr in SECTOR_MAP.values() for s in arr})
NIFTY_SYMBOL = "^NSEI"
WATCHLIST_FILE = "watchlist_v11_2.json"

# =========================
# UTILITIES
# =========================
def safe_float(x, default=np.nan):
    try:
        if x is None:
            return default
        return float(x)
    except:
        return default

@st.cache_data(ttl=3600, show_spinner=False)
def get_hist(symbol, period="1y", interval="1d"):
    try:
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        return df.dropna().copy()
    except:
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def get_info(symbol):
    try:
        return yf.Ticker(symbol).info
    except:
        return {}

@st.cache_data(ttl=3600, show_spinner=False)
def get_financials(symbol):
    try:
        tk = yf.Ticker(symbol)
        bs = tk.balance_sheet
        fin = tk.financials
        cf = tk.cashflow
        return bs, fin, cf
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


def add_indicators(df):
    if df.empty:
        return df
    df = df.copy()
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI14"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9, adjust=False).mean()

    tr1 = df["High"] - df["Low"]
    tr2 = (df["High"] - df["Close"].shift()).abs()
    tr3 = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["ATR14"] = tr.rolling(14).mean()

    df["VolAvg20"] = df["Volume"].rolling(20).mean()
    return df


def compute_returns(df, days):
    if df.empty or len(df) <= days:
        return np.nan
    return (df["Close"].iloc[-1] / df["Close"].iloc[-days - 1] - 1) * 100


def relative_strength_vs_nifty(stock_df, nifty_df, days=55):
    if stock_df.empty or nifty_df.empty or len(stock_df) <= days or len(nifty_df) <= days:
        return np.nan
    s = stock_df["Close"].iloc[-1] / stock_df["Close"].iloc[-days - 1]
    n = nifty_df["Close"].iloc[-1] / nifty_df["Close"].iloc[-days - 1]
    return (s / n - 1) * 100


def sector_score(symbols, nifty_df):
    rows = []
    for sym in symbols:
        df = add_indicators(get_hist(sym, period="1y"))
        if df.empty or len(df) < 220:
            continue
        close = df["Close"].iloc[-1]
        sma50 = df["SMA50"].iloc[-1]
        sma200 = df["SMA200"].iloc[-1]
        rsi = df["RSI14"].iloc[-1]
        rs55 = relative_strength_vs_nifty(df, nifty_df, 55)
        ret21 = compute_returns(df, 21)
        ret63 = compute_returns(df, 63)
        trend = 0
        if close > sma50: trend += 1
        if close > sma200: trend += 1
        if sma50 > sma200: trend += 1
        score = (safe_float(ret21,0)*0.25 + safe_float(ret63,0)*0.35 + safe_float(rs55,0)*0.30 + safe_float(rsi,50)*0.10)
        rows.append({
            "Symbol": sym,
            "Close": round(close,2),
            "RS_vs_NIFTY_%": round(rs55,2),
            "1M_%": round(ret21,2),
            "3M_%": round(ret63,2),
            "RSI": round(rsi,2),
            "Trend_Score": trend,
            "Composite_Score": round(score,2)
        })
    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["Composite_Score", "Trend_Score"], ascending=False)
    return out


def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except:
            pass
    return ["RELIANCE.NS", "HDFCBANK.NS", "TCS.NS"]


def save_watchlist(lst):
    try:
        with open(WATCHLIST_FILE, "w") as f:
            json.dump(sorted(list(set(lst))), f)
    except:
        pass


def breakout_scan(universe, nifty_df):
    rows = []
    for sym in universe:
        df = add_indicators(get_hist(sym, period="1y"))
        if df.empty or len(df) < 260:
            continue
        last = df.iloc[-1]
        prev = df.iloc[-2]
        high_20 = df["High"].rolling(20).max().iloc[-2]
        high_55 = df["High"].rolling(55).max().iloc[-2]
        rs = relative_strength_vs_nifty(df, nifty_df, 55)
        breakout = last["Close"] > high_20
        strong_breakout = last["Close"] > high_55
        vol_boost = safe_float(last["Volume"]) > safe_float(last["VolAvg20"], 0) * 1.3
        bullish = last["Close"] > last["SMA50"] > last["SMA200"]
        if breakout and bullish:
            atr = safe_float(last["ATR14"], 0)
            entry = safe_float(last["Close"], 0)
            sl = round(max(entry - 1.5 * atr, safe_float(last["SMA20"], entry*0.95)), 2)
            t1 = round(entry + 2 * atr, 2)
            t2 = round(entry + 4 * atr, 2)
            rows.append({
                "Symbol": sym,
                "Close": round(entry,2),
                "Breakout_20D": breakout,
                "Breakout_55D": strong_breakout,
                "Volume_Boost": vol_boost,
                "RS_vs_NIFTY_%": round(rs,2),
                "RSI": round(safe_float(last["RSI14"]),2),
                "Entry": round(entry,2),
                "SL": sl,
                "Target1": t1,
                "Target2": t2,
            })
    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["Breakout_55D", "Volume_Boost", "RS_vs_NIFTY_%"], ascending=False)
    return out


def position_size(capital, risk_pct, entry, sl):
    risk_amt = capital * risk_pct / 100
    per_share = max(entry - sl, 0.01)
    qty_risk = math.floor(risk_amt / per_share)
    qty_cap = math.floor(capital / entry)
    qty = max(min(qty_risk, qty_cap), 0)
    return qty, qty * entry, risk_amt

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ V11.2 PRO Controls")
selected_sector = st.sidebar.selectbox("Select Sector", ["ALL"] + list(SECTOR_MAP.keys()))
capital = st.sidebar.number_input("Capital (₹)", min_value=10000, value=500000, step=10000)
risk_pct = st.sidebar.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.5)

watchlist = load_watchlist()
st.sidebar.markdown("---")
st.sidebar.subheader("⭐ Persistent Watchlist")
add_symbol = st.sidebar.selectbox("Add stock", ["Select"] + DEFAULT_UNIVERSE)
if st.sidebar.button("Add to Watchlist") and add_symbol != "Select":
    if add_symbol not in watchlist:
        watchlist.append(add_symbol)
        save_watchlist(watchlist)
        st.sidebar.success(f"Added {add_symbol}")

remove_symbol = st.sidebar.selectbox("Remove stock", ["Select"] + watchlist)
if st.sidebar.button("Remove from Watchlist") and remove_symbol != "Select":
    watchlist = [x for x in watchlist if x != remove_symbol]
    save_watchlist(watchlist)
    st.sidebar.success(f"Removed {remove_symbol}")

if st.sidebar.button("Reset Default Watchlist"):
    watchlist = ["RELIANCE.NS", "HDFCBANK.NS", "TCS.NS"]
    save_watchlist(watchlist)
    st.sidebar.success("Watchlist reset")

universe = DEFAULT_UNIVERSE if selected_sector == "ALL" else SECTOR_MAP[selected_sector]

# =========================
# HEADER
# =========================
st.title("🏦 FINAL V11.2 PRO INSTITUTIONAL ULTIMATE")
st.caption("Sector Ranking • Relative Strength vs NIFTY • Sector Heatmap • Persistent Watchlist • Breakout Scanner • Swing Trade Engine • Fundamental + Technical")

nifty_df = add_indicators(get_hist(NIFTY_SYMBOL, period="1y"))
if nifty_df.empty:
    st.error("Unable to fetch NIFTY data right now. Please refresh later.")
    st.stop()

# =========================
# TOP METRICS
# =========================
col1, col2, col3, col4 = st.columns(4)
with col1:
    nifty_last = nifty_df["Close"].iloc[-1]
    nifty_ret = compute_returns(nifty_df, 21)
    st.metric("NIFTY", f"{nifty_last:,.2f}", f"{nifty_ret:.2f}% (1M)")
with col2:
    st.metric("Universe Stocks", len(universe))
with col3:
    st.metric("Watchlist Count", len(watchlist))
with col4:
    st.metric("Risk / Trade", f"{risk_pct:.1f}%")

# =========================
# SECTOR RANKING
# =========================
st.markdown("## 🏆 Sector Ranking")
sector_rows = []
sector_stock_tables = {}
for sector, symbols in SECTOR_MAP.items():
    sdf = sector_score(symbols, nifty_df)
    sector_stock_tables[sector] = sdf
    if not sdf.empty:
        sector_rows.append({
            "Sector": sector,
            "Avg_Composite_Score": round(sdf["Composite_Score"].mean(), 2),
            "Avg_RS_vs_NIFTY_%": round(sdf["RS_vs_NIFTY_%"].mean(), 2),
            "Avg_1M_%": round(sdf["1M_%"].mean(), 2),
            "Avg_3M_%": round(sdf["3M_%"].mean(), 2),
            "Bullish_Stocks": int((sdf["Trend_Score"] >= 2).sum()),
            "Stocks_Tracked": len(sdf)
        })

sector_rank_df = pd.DataFrame(sector_rows).sort_values(["Avg_Composite_Score", "Avg_RS_vs_NIFTY_%"], ascending=False)
st.dataframe(sector_rank_df, use_container_width=True)

# =========================
# SECTOR HEATMAP
# =========================
st.markdown("## 🔥 Sector Heatmap")
if not sector_rank_df.empty:
    heat = sector_rank_df[["Sector", "Avg_Composite_Score", "Avg_RS_vs_NIFTY_%", "Avg_1M_%", "Avg_3M_%"]].set_index("Sector")
    fig_heat = px.imshow(
        heat.T,
        text_auto='.2f',
        aspect='auto',
        title='Sector Strength Heatmap'
    )
    fig_heat.update_layout(height=450)
    st.plotly_chart(fig_heat, use_container_width=True)

# =========================
# TOP STOCKS BY SELECTED SECTOR
# =========================
st.markdown(f"## 📊 Top Stocks in {selected_sector}")
if selected_sector == "ALL":
    merged = []
    for s, sdf in sector_stock_tables.items():
        if not sdf.empty:
            x = sdf.copy()
            x["Sector"] = s
            merged.append(x)
    if merged:
        top_df = pd.concat(merged).sort_values("Composite_Score", ascending=False).head(20)
        st.dataframe(top_df, use_container_width=True)
else:
    st.dataframe(sector_stock_tables[selected_sector], use_container_width=True)

# =========================
# BREAKOUT SCANNER
# =========================
st.markdown("## 🚀 Breakout Scanner + Swing Trade Setup")
scan_df = breakout_scan(universe, nifty_df)
if scan_df.empty:
    st.info("No strong breakout candidates in current universe right now.")
else:
    scan_df_display = scan_df.copy()
    pos_sizes = []
    invested_vals = []
    for _, r in scan_df.iterrows():
        qty, invested, _ = position_size(capital, risk_pct, r["Entry"], r["SL"])
        pos_sizes.append(qty)
        invested_vals.append(round(invested, 2))
    scan_df_display["Qty"] = pos_sizes
    scan_df_display["Capital_Used"] = invested_vals
    st.dataframe(scan_df_display, use_container_width=True)

# =========================
# WATCHLIST DASHBOARD
# =========================
st.markdown("## ⭐ Persistent Watchlist Dashboard")
watch_rows = []
for sym in watchlist:
    df = add_indicators(get_hist(sym, period="1y"))
    if df.empty or len(df) < 220:
        continue
    last = df.iloc[-1]
    rs = relative_strength_vs_nifty(df, nifty_df, 55)
    signal = "Bullish" if last["Close"] > last["SMA50"] > last["SMA200"] else "Neutral/Weak"
    watch_rows.append({
        "Symbol": sym,
        "Close": round(last["Close"],2),
        "1M_%": round(compute_returns(df, 21),2),
        "3M_%": round(compute_returns(df, 63),2),
        "RS_vs_NIFTY_%": round(rs,2),
        "RSI": round(last["RSI14"],2),
        "Signal": signal,
    })
watch_df = pd.DataFrame(watch_rows)
if not watch_df.empty:
    st.dataframe(watch_df.sort_values("RS_vs_NIFTY_%", ascending=False), use_container_width=True)
else:
    st.info("Watchlist is empty or data unavailable.")

# =========================
# STOCK DEEP DIVE
# =========================
st.markdown("## 🔎 Stock Deep Dive")
deep_symbol = st.selectbox("Select Stock for Full Analysis", universe if selected_sector != "ALL" else DEFAULT_UNIVERSE)
stock_df = add_indicators(get_hist(deep_symbol, period="2y"))
info = get_info(deep_symbol)
bs, fin, cf = get_financials(deep_symbol)

if not stock_df.empty:
    last = stock_df.iloc[-1]
    rs_stock = relative_strength_vs_nifty(stock_df, nifty_df, 55)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Price", f"₹{last['Close']:.2f}")
    c2.metric("RS vs NIFTY (55D)", f"{rs_stock:.2f}%")
    c3.metric("RSI 14", f"{last['RSI14']:.2f}")
    c4.metric("1M Return", f"{compute_returns(stock_df, 21):.2f}%")
    c5.metric("3M Return", f"{compute_returns(stock_df, 63):.2f}%")

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(
        x=stock_df.index,
        open=stock_df['Open'], high=stock_df['High'], low=stock_df['Low'], close=stock_df['Close'],
        name='Price'
    ), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA20'], name='SMA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA50'], name='SMA50'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA200'], name='SMA200'), row=1, col=1)
    fig.add_trace(go.Bar(x=stock_df.index, y=stock_df['Volume'], name='Volume'), row=2, col=1)
    fig.update_layout(height=700, xaxis_rangeslider_visible=False, title=f"{deep_symbol} Technical Chart")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Relative Strength vs NIFTY (Normalized)")
    aligned = pd.concat([
        stock_df['Close'].rename('Stock'),
        nifty_df['Close'].rename('NIFTY')
    ], axis=1).dropna()
    aligned['Stock_Norm'] = aligned['Stock'] / aligned['Stock'].iloc[0] * 100
    aligned['NIFTY_Norm'] = aligned['NIFTY'] / aligned['NIFTY'].iloc[0] * 100
    fig_rs = go.Figure()
    fig_rs.add_trace(go.Scatter(x=aligned.index, y=aligned['Stock_Norm'], name=deep_symbol))
    fig_rs.add_trace(go.Scatter(x=aligned.index, y=aligned['NIFTY_Norm'], name='NIFTY'))
    fig_rs.update_layout(height=400, title='Relative Strength Comparison (Base = 100)')
    st.plotly_chart(fig_rs, use_container_width=True)

    st.markdown("### Fundamental Snapshot")
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Market Cap", f"₹{safe_float(info.get('marketCap',0))/1e7:,.0f} Cr" if info.get('marketCap') else "NA")
    f2.metric("PE", f"{safe_float(info.get('trailingPE')):.2f}" if info.get('trailingPE') else "NA")
    f3.metric("PB", f"{safe_float(info.get('priceToBook')):.2f}" if info.get('priceToBook') else "NA")
    f4.metric("ROE", f"{safe_float(info.get('returnOnEquity'))*100:.2f}%" if info.get('returnOnEquity') else "NA")

    st.markdown("### Balance Sheet / Financials / Cashflow")
    t1, t2, t3 = st.tabs(["Balance Sheet", "P&L", "Cash Flow"])
    with t1:
        if not bs.empty:
            st.dataframe(bs, use_container_width=True)
        else:
            st.info("Balance sheet not available.")
    with t2:
        if not fin.empty:
            st.dataframe(fin, use_container_width=True)
        else:
            st.info("Financials not available.")
    with t3:
        if not cf.empty:
            st.dataframe(cf, use_container_width=True)
        else:
            st.info("Cash flow not available.")

    st.markdown("### Trade Plan")
    entry = float(last['Close'])
    atr = float(last['ATR14']) if not pd.isna(last['ATR14']) else entry * 0.03
    sl = round(max(entry - 1.5 * atr, float(last['SMA20']) if not pd.isna(last['SMA20']) else entry*0.95), 2)
    t1v = round(entry + 2 * atr, 2)
    t2v = round(entry + 4 * atr, 2)
    qty, invested, risk_amt = position_size(capital, risk_pct, entry, sl)

    p1, p2, p3, p4, p5 = st.columns(5)
    p1.metric("Entry", f"₹{entry:.2f}")
    p2.metric("Stop Loss", f"₹{sl:.2f}")
    p3.metric("Target 1", f"₹{t1v:.2f}")
    p4.metric("Target 2", f"₹{t2v:.2f}")
    p5.metric("Qty", qty)

    st.markdown(f"<div class='card'><b>Capital Used:</b> ₹{invested:,.2f} &nbsp;&nbsp; <b>Max Risk:</b> ₹{risk_amt:,.2f}</div>", unsafe_allow_html=True)

# =========================
# MODEL PORTFOLIO BUILDER
# =========================
st.markdown("## 🧠 Institutional Model Portfolio Builder")
portfolio_candidates = []
for sec, sdf in sector_stock_tables.items():
    if not sdf.empty:
        topn = sdf.head(2).copy()
        topn['Sector'] = sec
        portfolio_candidates.append(topn)

if portfolio_candidates:
    pf = pd.concat(portfolio_candidates).sort_values("Composite_Score", ascending=False)
    pf = pf.head(8).copy()
    weight = round(100 / len(pf), 2)
    pf["Suggested_Weight_%"] = weight
    pf["Capital_Allocation_₹"] = (capital * pf["Suggested_Weight_%"] / 100).round(2)
    st.dataframe(pf[["Sector", "Symbol", "Close", "RS_vs_NIFTY_%", "Composite_Score", "Suggested_Weight_%", "Capital_Allocation_₹"]], use_container_width=True)

st.markdown("---")
st.markdown("<div class='small-note'>Disclaimer: Educational tool only. Verify data before investing. Yahoo Finance data may have delays/inconsistencies.</div>", unsafe_allow_html=True)

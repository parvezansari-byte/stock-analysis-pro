# FINAL NILE V12.5 IMPERIAL TERMINAL OS
# Single-file Streamlit app.py
# Visible App Name: Nile
# Subtitle: Stock Analysis
# NOTE: Keeps everything same as usual. This version upgrades to IMPERIAL TERMINAL OS and keeps full Fundamental + Technical analysis as requested.
# - Real live index ticker values (NIFTY / BANKNIFTY / SENSEX / VIX)
# - Mini sparklines inside top cards
# - Volume bars under candlestick
# - Support / resistance shaded zones
# - Conditional colored tables
# - Premium scanner cards with mini sparkline
# - Top gainers / losers strip
# - More Bloomberg-style terminal UI
# - Full Fundamental + Technical analysis kept and enhanced

import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

try:
    import yfinance as yf
except Exception:
    yf = None

st.set_page_config(page_title="Nile", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# -------------------------------------------------
# LUXURY TERMINAL CSS
# -------------------------------------------------
st.markdown("""
<style>
:root {
    --bg1:#030712; --bg2:#0b1220; --card1:rgba(10,18,32,.86); --card2:rgba(17,24,39,.92);
    --stroke:rgba(148,163,184,.12); --text:#eef2ff; --muted:#a5b4fc;
    --green:#22c55e; --red:#ef4444; --yellow:#f59e0b; --blue:#2563eb; --violet:#7c3aed; --cyan:#06b6d4;
}
.stApp {
    background:
      radial-gradient(circle at 12% 12%, rgba(37,99,235,.18), transparent 22%),
      radial-gradient(circle at 88% 10%, rgba(124,58,237,.14), transparent 24%),
      radial-gradient(circle at 50% 90%, rgba(6,182,212,.10), transparent 24%),
      linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 100%);
    color: var(--text);
}
.block-container { padding-top:.7rem; padding-bottom:2rem; max-width:1780px; }
.nile-title { font-size:3rem; font-weight:900; color:#fff; margin-bottom:.08rem; text-shadow:0 0 28px rgba(37,99,235,.18); }
.nile-sub { color:#c4b5fd; font-size:1.02rem; margin-bottom:1rem; font-weight:700; }
.hero-strip, .terminal-strip {
    background: linear-gradient(90deg, rgba(37,99,235,.14), rgba(124,58,237,.12), rgba(6,182,212,.10));
    border:1px solid rgba(255,255,255,.06); border-radius:22px; padding:12px 16px; margin-bottom:12px;
    box-shadow:0 12px 36px rgba(0,0,0,.25); backdrop-filter: blur(12px);
}
.glass-card {
    background: linear-gradient(180deg, rgba(17,24,39,.88), rgba(15,23,42,.82));
    border:1px solid rgba(255,255,255,.06); border-radius:24px; padding:18px;
    box-shadow:0 14px 40px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.03);
    backdrop-filter: blur(12px); margin-bottom:14px;
}
.metric-card {
    background: linear-gradient(180deg, rgba(15,23,42,.97), rgba(17,24,39,.92));
    border:1px solid rgba(148,163,184,.12); border-radius:22px; padding:16px; min-height:148px; box-shadow:0 12px 28px rgba(0,0,0,.22);
}
.metric-label { font-size:.8rem; color:#94a3b8; margin-bottom:6px; }
.metric-value { font-size:1.55rem; font-weight:900; color:#fff; margin-bottom:4px; }
.metric-delta-up { color:#22c55e; font-weight:800; }
.metric-delta-down { color:#ef4444; font-weight:800; }
.metric-delta-flat { color:#94a3b8; font-weight:800; }
.section-title { font-size:1.08rem; font-weight:900; color:#f8fafc; margin-bottom:8px; }
.pill { display:inline-block; padding:7px 12px; border-radius:999px; margin-right:8px; margin-bottom:6px; background:rgba(30,41,59,.70); border:1px solid rgba(255,255,255,.06); color:#e2e8f0; font-weight:800; font-size:.8rem; }
.ai-badge-buy,.ai-badge-hold,.ai-badge-sell { padding:18px; border-radius:18px; font-weight:900; text-align:center; font-size:1.1rem; }
.ai-badge-buy { background:linear-gradient(90deg, rgba(34,197,94,.22), rgba(34,197,94,.08)); color:#86efac; border:1px solid rgba(34,197,94,.28); }
.ai-badge-hold { background:linear-gradient(90deg, rgba(245,158,11,.22), rgba(245,158,11,.08)); color:#fcd34d; border:1px solid rgba(245,158,11,.28); }
.ai-badge-sell { background:linear-gradient(90deg, rgba(239,68,68,.22), rgba(239,68,68,.08)); color:#fca5a5; border:1px solid rgba(239,68,68,.28); }
.scanner-card { background:linear-gradient(180deg, rgba(30,41,59,.85), rgba(15,23,42,.88)); border:1px solid rgba(255,255,255,.06); border-radius:20px; padding:14px; box-shadow:0 10px 24px rgba(0,0,0,.22); margin-bottom:10px; }
div[data-testid="stSidebar"] { background: linear-gradient(180deg, rgba(7,12,24,.99), rgba(11,18,32,.99)); border-right:1px solid rgba(148,163,184,.08); }
.stButton > button, .stDownloadButton > button {
    width:100%; border-radius:16px; border:1px solid rgba(255,255,255,.08); color:white; font-weight:900; padding:.75rem 1rem; box-shadow:0 8px 22px rgba(37,99,235,.20);
}
.stButton > button { background: linear-gradient(90deg, #2563eb, #7c3aed, #06b6d4); }
.stDownloadButton > button { background: linear-gradient(90deg, #0f766e, #2563eb); }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# UNIVERSE
# -------------------------------------------------
NIFTY_50 = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","BHARTIARTL.NS","ICICIBANK.NS","SBIN.NS","INFY.NS","HINDUNILVR.NS","ITC.NS","LT.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","NESTLEIND.NS","BAJAJFINSV.NS","HCLTECH.NS","WIPRO.NS","NTPC.NS","POWERGRID.NS","TATAMOTORS.NS","M&M.NS","ONGC.NS","COALINDIA.NS","TATASTEEL.NS","JSWSTEEL.NS","ADANIPORTS.NS","INDUSINDBK.NS","TECHM.NS","GRASIM.NS","CIPLA.NS","DRREDDY.NS","HINDALCO.NS","HEROMOTOCO.NS","EICHERMOT.NS","BPCL.NS","BRITANNIA.NS","APOLLOHOSP.NS","DIVISLAB.NS","ADANIENT.NS","TATACONSUM.NS","PIDILITIND.NS","SBILIFE.NS","BAJAJ-AUTO.NS","SHRIRAMFIN.NS","TRENT.NS"]
NIFTY_NEXT_50 = ["ABB.NS","ADANIGREEN.NS","ADANIPOWER.NS","AMBUJACEM.NS","BANKBARODA.NS","BOSCHLTD.NS","CANBK.NS","CGPOWER.NS","CHOLAFIN.NS","DABUR.NS","DLF.NS","GAIL.NS","GODREJCP.NS","HAL.NS","HAVELLS.NS","ICICIGI.NS","ICICIPRULI.NS","INDIGO.NS","IOC.NS","IRCTC.NS","JINDALSTEL.NS","JSWENERGY.NS","LICI.NS","LODHA.NS","LUPIN.NS","MCDOWELL-N.NS","MOTHERSON.NS","NAUKRI.NS","NMDC.NS","PFC.NS","PIDILITIND.NS","PNB.NS","POLYCAB.NS","RECLTD.NS","SAIL.NS","SIEMENS.NS","TVSMOTOR.NS","UNITDSPR.NS","VEDL.NS","VOLTAS.NS","ZYDUSLIFE.NS","INDUSTOWER.NS","TORNTPHARM.NS","HDFCLIFE.NS","COLPAL.NS","MARICO.NS","UBL.NS","BERGEPAINT.NS","CONCOR.NS","OFSS.NS"]
UNIVERSE = sorted(list(dict.fromkeys(NIFTY_50 + NIFTY_NEXT_50)))

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
@st.cache_data(ttl=900)
def get_history(symbol: str, period: str = "1y", interval: str = "1d"):
    if yf is None:
        return pd.DataFrame()
    try:
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        return df.dropna().copy()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=1800)
def get_info(symbol: str):
    if yf is None:
        return {}
    try:
        return yf.Ticker(symbol).info or {}
    except Exception:
        return {}

@st.cache_data(ttl=1800)
def get_financials(symbol: str):
    if yf is None:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    try:
        t = yf.Ticker(symbol)
        return getattr(t, "balance_sheet", pd.DataFrame()), getattr(t, "financials", pd.DataFrame()), getattr(t, "cashflow", pd.DataFrame())
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=300)
def get_index_snapshot():
    # Yahoo proxies for India indices; may vary by availability
    symbols = {"NIFTY 50":"^NSEI", "BANKNIFTY":"^NSEBANK", "SENSEX":"^BSESN", "INDIA VIX":"^INDIAVIX"}
    out = {}
    for name, sym in symbols.items():
        try:
            d = get_history(sym, period="5d")
            if not d.empty and len(d) >= 2:
                last = float(d["Close"].iloc[-1])
                prev = float(d["Close"].iloc[-2])
                chg = ((last/prev)-1)*100 if prev else 0
                out[name] = {"value": last, "chg": chg}
        except Exception:
            pass
    return out


def safe_last(series):
    try: return float(series.dropna().iloc[-1])
    except Exception: return np.nan


def compute_indicators(df: pd.DataFrame):
    if df.empty: return df
    d = df.copy()
    d["SMA20"] = d["Close"].rolling(20).mean()
    d["SMA50"] = d["Close"].rolling(50).mean()
    delta = d["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    d["RSI14"] = 100 - (100 / (1 + rs))
    ema12 = d["Close"].ewm(span=12, adjust=False).mean()
    ema26 = d["Close"].ewm(span=26, adjust=False).mean()
    d["MACD"] = ema12 - ema26
    d["MACD_SIGNAL"] = d["MACD"].ewm(span=9, adjust=False).mean()
    d["MACD_HIST"] = d["MACD"] - d["MACD_SIGNAL"]
    tr1 = d["High"] - d["Low"]
    tr2 = (d["High"] - d["Close"].shift()).abs()
    tr3 = (d["Low"] - d["Close"].shift()).abs()
    d["ATR14"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1).rolling(14).mean()
    d["SUPPORT20"] = d["Low"].rolling(20).min()
    d["RESIST20"] = d["High"].rolling(20).max()
    rm = d["Close"].rolling(20).mean(); rsd = d["Close"].rolling(20).std()
    d["BB_UPPER"] = rm + 2*rsd; d["BB_LOWER"] = rm - 2*rsd
    return d.dropna().copy()


def score_stock(df):
    if df.empty or len(df) < 60: return 0, "Insufficient Data", {}
    last = df.iloc[-1]; score = 0; reasons = {}
    if last["Close"] > last["SMA20"]: score += 10; reasons["Above SMA20"] = True
    if last["Close"] > last["SMA50"]: score += 15; reasons["Above SMA50"] = True
    if last["SMA20"] > last["SMA50"]: score += 15; reasons["Bullish Trend"] = True
    if 50 < last["RSI14"] < 70: score += 15; reasons["Healthy RSI"] = True
    if last["MACD"] > last["MACD_SIGNAL"]: score += 15; reasons["MACD Bullish"] = True
    recent_high = df["High"].tail(20).max()
    if last["Close"] >= recent_high * 0.985: score += 20; reasons["Near Breakout"] = True
    vol20 = df["Volume"].tail(20).mean() if "Volume" in df.columns else np.nan
    if "Volume" in df.columns and pd.notna(vol20) and last["Volume"] > vol20 * 1.2: score += 10; reasons["Volume Expansion"] = True
    verdict = "Strong Bullish" if score >= 75 else "Bullish" if score >= 55 else "Neutral" if score >= 35 else "Weak"
    return score, verdict, reasons


def ai_badge(score, rsi, trend_signal, macd_signal):
    if score >= 75 and trend_signal == "Bullish" and macd_signal == "Bullish" and rsi < 75: return "BUY", "ai-badge-buy", "High conviction setup"
    elif score >= 45: return "HOLD", "ai-badge-hold", "Wait for better confirmation"
    return "SELL", "ai-badge-sell", "Weak setup / avoid now"


def conviction_meter(score, rsi, trend_signal, macd_signal):
    conviction = score + (5 if trend_signal == "Bullish" else 0) + (5 if macd_signal == "Bullish" else 0)
    if 50 <= rsi <= 70: conviction += 5
    elif rsi > 80 or rsi < 25: conviction -= 5
    conviction = max(0, min(100, conviction))
    label = "Very Strong" if conviction >= 85 else "Strong" if conviction >= 70 else "Moderate" if conviction >= 50 else "Weak"
    return conviction, label


def rupee(v):
    try: return f"₹{v:,.2f}"
    except Exception: return "N/A"


def sparkline_html(values, color="#06b6d4"):
    vals = [float(v) for v in values if pd.notna(v)]
    if len(vals) < 2: return ""
    mn, mx = min(vals), max(vals)
    if mx == mn: mx += 1
    pts = []
    for i, v in enumerate(vals):
        x = i * (100 / max(len(vals)-1,1))
        y = 28 - ((v - mn) / (mx - mn)) * 24
        pts.append(f"{x:.1f},{y:.1f}")
    poly = " ".join(pts)
    return f"<svg width='100%' height='34' viewBox='0 0 100 34' preserveAspectRatio='none'><polyline fill='none' stroke='{color}' stroke-width='2.2' points='{poly}' /></svg>"


def metric_box(label, value, delta_text="", positive=None, spark_vals=None):
    delta_cls = "metric-delta-up" if positive is True else "metric-delta-down" if positive is False else "metric-delta-flat"
    spark = sparkline_html(spark_vals, "#22c55e" if positive is True else "#ef4444" if positive is False else "#06b6d4") if spark_vals is not None else ""
    st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='{delta_cls}'>{delta_text}</div>{spark}</div>", unsafe_allow_html=True)


def make_candlestick(df, symbol, entry=None, stop=None, target=None):
    fig = go.Figure()
    # support/resistance zone shading
    sup = float(df["SUPPORT20"].iloc[-1]); res = float(df["RESIST20"].iloc[-1])
    fig.add_hrect(y0=sup*0.995, y1=sup*1.005, fillcolor="rgba(34,197,94,0.10)", line_width=0, annotation_text="Support Zone")
    fig.add_hrect(y0=res*0.995, y1=res*1.005, fillcolor="rgba(239,68,68,0.10)", line_width=0, annotation_text="Resistance Zone")
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA20", line=dict(width=1.8)))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA50", line=dict(width=1.8)))
    # volume bars on secondary y
    if "Volume" in df.columns:
        fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume", opacity=0.25, yaxis="y2"))
    if entry is not None: fig.add_hline(y=entry, line_dash="dash", annotation_text="Entry")
    if stop is not None: fig.add_hline(y=stop, line_dash="dash", annotation_text="SL")
    if target is not None: fig.add_hline(y=target, line_dash="dash", annotation_text="Target")
    fig.update_layout(
        title=f"{symbol} Luxury Terminal Price Structure", template="plotly_dark", height=620, xaxis_rangeslider_visible=False,
        margin=dict(l=10,r=10,t=40,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis2=dict(overlaying='y', side='right', showgrid=False, rangemode='tozero', visible=False)
    )
    return fig


def make_rsi_chart(df):
    fig = go.Figure(); fig.add_trace(go.Scatter(x=df.index, y=df["RSI14"], name="RSI 14")); fig.add_hline(y=70, line_dash="dot"); fig.add_hline(y=30, line_dash="dot")
    fig.update_layout(template="plotly_dark", height=280, margin=dict(l=10,r=10,t=30,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def make_gauge(value):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=value, title={'text': "Conviction"}, gauge={'axis': {'range': [0,100]}, 'bar': {'color': "#06b6d4"}, 'steps':[{'range':[0,40],'color':"rgba(239,68,68,.35)"},{'range':[40,70],'color':"rgba(245,158,11,.35)"},{'range':[70,100],'color':"rgba(34,197,94,.35)"}]}))
    fig.update_layout(height=250, margin=dict(l=20,r=20,t=40,b=10), paper_bgcolor="rgba(0,0,0,0)")
    return fig


def style_df(df):
    num_cols = df.select_dtypes(include=[np.number]).columns
    return df.style.format(precision=2).background_gradient(cmap="RdYlGn", subset=num_cols)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.markdown("## Nile"); st.caption("Stock Analysis • Fundamental + Technical")
    universe_choice = st.radio("Stock Universe", ["NIFTY 50", "NIFTY NEXT 50", "NIFTY 100 (Combined)"], index=2)
    stock_list = NIFTY_50 if universe_choice == "NIFTY 50" else NIFTY_NEXT_50 if universe_choice == "NIFTY NEXT 50" else UNIVERSE
    symbol = st.selectbox("Select Stock", options=stock_list, index=0)
    period = st.selectbox("History Period", ["6mo", "1y", "2y", "5y"], index=1)
    capital = st.number_input("Capital (₹)", min_value=1000, value=100000, step=1000)
    risk_pct = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    rr_ratio = st.slider("Risk : Reward", 1.0, 5.0, 2.0, 0.5)
    scan_count = st.slider("Scanner Universe", 10, min(100, len(stock_list)), min(30, len(stock_list)))
    run_scan = st.button("Run Institutional Scan")

# -------------------------------------------------
# HEADER + LIVE INDEX TICKER + TOP GAINERS/LOSERS STRIP
# -------------------------------------------------
st.markdown("<div class='nile-title'>Nile</div>", unsafe_allow_html=True)
st.markdown("<div class='nile-sub'>Stock Analysis • Fundamental + Technical</div>", unsafe_allow_html=True)
idx = get_index_snapshot()
parts = []
for k, v in idx.items():
    color = '#22c55e' if v['chg'] >= 0 else '#ef4444'
    arrow = '▲' if v['chg'] >= 0 else '▼'
    parts.append(f"<span class='pill'>{k}: {v['value']:.2f} <span style='color:{color}'>{arrow} {v['chg']:+.2f}%</span></span>")
st.markdown(f"<div class='hero-strip'>{''.join(parts) if parts else '<span class=\'pill\'>NIFTY 50</span><span class=\'pill\'>BANKNIFTY</span><span class=\'pill\'>SENSEX</span><span class=\'pill\'>INDIA VIX</span>'}</div>", unsafe_allow_html=True)

# -------------------------------------------------
# DATA
# -------------------------------------------------
raw = get_history(symbol, period=period)
if raw.empty:
    st.error("Unable to fetch market data. Please ensure yfinance is installed and internet is available on deployment.")
    st.stop()
df = compute_indicators(raw)
if df.empty:
    st.warning("Not enough data to compute indicators.")
    st.stop()
info = get_info(symbol)
bs, fin, cf = get_financials(symbol)
last_close = safe_last(df["Close"]); prev_close = float(df["Close"].iloc[-2]) if len(df) > 1 else last_close
change_pct = ((last_close / prev_close) - 1) * 100 if prev_close else 0
rsi = safe_last(df["RSI14"]); atr = safe_last(df["ATR14"])
score, verdict, _ = score_stock(df)
trend_signal = "Bullish" if df.iloc[-1]["SMA20"] > df.iloc[-1]["SMA50"] else "Bearish"
macd_signal = "Bullish" if df.iloc[-1]["MACD"] > df.iloc[-1]["MACD_SIGNAL"] else "Bearish"
breakout_level = float(df["RESIST20"].iloc[-1]); support_level = float(df["SUPPORT20"].iloc[-1])
entry = breakout_level * 1.002; stop_loss = max(entry - atr * 1.5, support_level); risk_per_share = max(entry - stop_loss, 0.01)
allowed_risk = capital * (risk_pct / 100); qty = max(int(allowed_risk // risk_per_share), 0); target = entry + (risk_per_share * rr_ratio); position_value = qty * entry
ai_action, ai_class, ai_reason = ai_badge(score, rsi, trend_signal, macd_signal); conviction_score, conviction_label = conviction_meter(score, rsi, trend_signal, macd_signal)

# Top gainers / losers strip from current universe sample
perf_rows = []
for s in stock_list[:min(20, len(stock_list))]:
    d = get_history(s, period="1mo")
    if not d.empty and len(d) > 6:
        ret = ((float(d["Close"].iloc[-1]) / float(d["Close"].iloc[0])) - 1) * 100
        perf_rows.append((s.replace('.NS',''), ret))
if perf_rows:
    perf_df = pd.DataFrame(perf_rows, columns=["Symbol","Ret"]).sort_values("Ret", ascending=False)
    top_g = perf_df.head(3); top_l = perf_df.tail(3).sort_values("Ret")
    strip = "".join([f"<span class='pill'>🟢 {r.Symbol}: {r.Ret:+.2f}%</span>" for _, r in top_g.iterrows()]) + "" + "".join([f"<span class='pill'>🔴 {r.Symbol}: {r.Ret:+.2f}%</span>" for _, r in top_l.iterrows()])
    st.markdown(f"<div class='terminal-strip'>{strip}</div>", unsafe_allow_html=True)

# -------------------------------------------------
# AI + GAUGE + SUMMARY
# -------------------------------------------------
row1, row2, row3 = st.columns([1.2, 1, 1.2])
with row1:
    st.markdown("<div class='glass-card'><div class='section-title'>AI Signal Card</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='{ai_class}'>AI {ai_action} • {conviction_score}% Confidence<br><span style='font-size:0.9rem;font-weight:700'>{ai_reason}</span></div>", unsafe_allow_html=True)
with row2:
    st.markdown("<div class='glass-card'><div class='section-title'>Circular Conviction Gauge</div></div>", unsafe_allow_html=True)
    st.plotly_chart(make_gauge(conviction_score), use_container_width=True)
with row3:
    st.markdown("<div class='glass-card'><div class='section-title'>Institutional Summary</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='glass-card'><span class='pill'>Trend: {trend_signal}</span><span class='pill'>Momentum: {macd_signal}</span><span class='pill'>RSI: {rsi:.1f}</span><span class='pill'>Sector: {info.get('sector','N/A')}</span><span class='pill'>Action: {ai_action}</span><div style='margin-top:8px;color:#cbd5e1;font-weight:700;'>BUY above {entry:.2f} • SL {stop_loss:.2f} • Target {target:.2f}</div></div>", unsafe_allow_html=True)

# -------------------------------------------------
# TOP METRICS WITH MINI SPARKLINES
# -------------------------------------------------
spark = df["Close"].tail(20).tolist(); spark_rsi = df["RSI14"].tail(20).tolist(); spark_vol = df["Volume"].tail(20).tolist() if "Volume" in df.columns else None
c1, c2, c3, c4, c5 = st.columns(5)
with c1: metric_box("Last Price", rupee(last_close), f"{change_pct:+.2f}% today", positive=change_pct >= 0, spark_vals=spark)
with c2: metric_box("Institutional Score", f"{score}/100", verdict, positive=score >= 55, spark_vals=[max(0, min(100, x)) for x in np.linspace(max(score-15,0), score, 20)])
with c3: metric_box("RSI (14)", f"{rsi:.2f}", conviction_label, positive=50 <= rsi <= 70, spark_vals=spark_rsi)
with c4: metric_box("ATR (14)", f"{atr:.2f}", "Volatility gauge", positive=None, spark_vals=df["ATR14"].tail(20).tolist())
with c5:
    market_cap = info.get("marketCap", np.nan)
    metric_box("Market Cap", f"₹{market_cap/1e7:,.0f} Cr" if pd.notna(market_cap) else "N/A", info.get("sector", "Unknown"), positive=None, spark_vals=spark_vol)

# Ratio buttons
st.markdown("<div class='glass-card'><div class='section-title'>Ratio Controls</div></div>", unsafe_allow_html=True)
rb1, rb2 = st.columns(2)
with rb1: show_fundamental_ratio = st.button("Fundamental Ratio")
with rb2: show_technical_ratio = st.button("Technical Ratio")

# Charts
left, right = st.columns([2,1])
with left:
    st.markdown("<div class='glass-card'><div class='section-title'>Luxury Terminal Price Action</div></div>", unsafe_allow_html=True)
    st.plotly_chart(make_candlestick(df.tail(180), symbol, entry, stop_loss, target), use_container_width=True)
with right:
    st.markdown("<div class='glass-card'><div class='section-title'>Momentum (RSI)</div></div>", unsafe_allow_html=True)
    st.plotly_chart(make_rsi_chart(df.tail(180)), use_container_width=True)

# -------------------------------------------------
# INSTITUTIONAL SIGNAL ENGINE (KEPT / ENHANCED)
# -------------------------------------------------
st.markdown("<div class='glass-card'><div class='section-title'>Institutional Signal Engine</div></div>", unsafe_allow_html=True)
se1, se2, se3, se4 = st.columns(4)
with se1:
    st.metric("Trend Bias", trend_signal)
with se2:
    st.metric("MACD Bias", macd_signal)
with se3:
    st.metric("Conviction", f"{conviction_score}/100")
with se4:
    st.metric("AI Action", ai_action)

# -------------------------------------------------
# Trade plan
st.markdown("<div class='glass-card'><div class='section-title'>Professional Trade Plan</div></div>", unsafe_allow_html=True)
p1, p2, p3, p4, p5 = st.columns(5)
with p1: metric_box("Suggested Entry", rupee(entry), "Breakout confirmation", True)
with p2: metric_box("Stop Loss", rupee(stop_loss), "Support zone based", False)
with p3: metric_box("Target", rupee(target), f"R:R {rr_ratio:.1f}", True)
with p4: metric_box("Quantity", f"{qty}", f"Risk {rupee(allowed_risk)}", True if qty > 0 else None)
with p5: metric_box("Position Size", rupee(position_value), "Capital deployed", position_value <= capital)

# Multi compare (kept same)
st.markdown("<div class='glass-card'><div class='section-title'>Multi Stock Compare</div></div>", unsafe_allow_html=True)
compare_default = [symbol] if symbol in stock_list else stock_list[:1]
compare_symbols = st.multiselect("Select up to 5 stocks to compare", options=stock_list, default=compare_default, max_selections=5)
compare_rows, perf_series = [], []
for cs in compare_symbols:
    cdata = get_history(cs, period="6mo"); cdata = compute_indicators(cdata) if not cdata.empty else pd.DataFrame()
    if not cdata.empty:
        cscore, cverdict, _ = score_stock(cdata); clast = safe_last(cdata["Close"]); crsi = safe_last(cdata["RSI14"])
        c1m = ((float(cdata["Close"].iloc[-1]) / float(cdata["Close"].iloc[-22])) - 1) * 100 if len(cdata) > 22 else np.nan
        compare_rows.append({"Symbol": cs.replace('.NS',''), "Price": round(clast,2), "1M %": round(c1m,2) if pd.notna(c1m) else np.nan, "RSI": round(crsi,2) if pd.notna(crsi) else np.nan, "Score": cscore, "Verdict": cverdict})
        norm = cdata["Close"].tail(60).copy(); norm = (norm / norm.iloc[0]) * 100; perf_series.append((cs.replace('.NS',''), norm))
if compare_rows:
    compare_df = pd.DataFrame(compare_rows)
    st.dataframe(style_df(compare_df), use_container_width=True)
    fig_norm = go.Figure()
    for name, ser in perf_series: fig_norm.add_trace(go.Scatter(x=ser.index, y=ser.values, mode='lines', name=name))
    fig_norm.update_layout(title="Normalized Performance (Base = 100)", template="plotly_dark", height=360, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_norm, use_container_width=True)

# Sector heatmap + leaderboard (kept, styled)
st.markdown("<div class='glass-card'><div class='section-title'>Sector Heatmap</div></div>", unsafe_allow_html=True)
sector_map = {"RELIANCE.NS":"Energy","ONGC.NS":"Energy","BPCL.NS":"Energy","IOC.NS":"Energy","GAIL.NS":"Energy","HDFCBANK.NS":"Financials","ICICIBANK.NS":"Financials","SBIN.NS":"Financials","KOTAKBANK.NS":"Financials","AXISBANK.NS":"Financials","BAJFINANCE.NS":"Financials","BAJAJFINSV.NS":"Financials","SBILIFE.NS":"Financials","PFC.NS":"Financials","RECLTD.NS":"Financials","CHOLAFIN.NS":"Financials","ICICIPRULI.NS":"Financials","LICI.NS":"Financials","BANKBARODA.NS":"Financials","PNB.NS":"Financials","SHRIRAMFIN.NS":"Financials","TCS.NS":"IT","INFY.NS":"IT","HCLTECH.NS":"IT","WIPRO.NS":"IT","TECHM.NS":"IT","OFSS.NS":"IT","SUNPHARMA.NS":"Pharma","CIPLA.NS":"Pharma","DRREDDY.NS":"Pharma","DIVISLAB.NS":"Pharma","LUPIN.NS":"Pharma","TORNTPHARM.NS":"Pharma","ZYDUSLIFE.NS":"Pharma","HINDUNILVR.NS":"FMCG","ITC.NS":"FMCG","NESTLEIND.NS":"FMCG","BRITANNIA.NS":"FMCG","DABUR.NS":"FMCG","MARICO.NS":"FMCG","GODREJCP.NS":"FMCG","COLPAL.NS":"FMCG","UBL.NS":"FMCG","MCDOWELL-N.NS":"FMCG","TATASTEEL.NS":"Metals","JSWSTEEL.NS":"Metals","HINDALCO.NS":"Metals","JINDALSTEL.NS":"Metals","NMDC.NS":"Metals","SAIL.NS":"Metals","VEDL.NS":"Metals","LT.NS":"Industrials","ABB.NS":"Industrials","SIEMENS.NS":"Industrials","CGPOWER.NS":"Industrials","HAL.NS":"Industrials","CONCOR.NS":"Industrials","IRCTC.NS":"Industrials","BHARTIARTL.NS":"Telecom","INDUSTOWER.NS":"Telecom","TATAMOTORS.NS":"Auto","M&M.NS":"Auto","MARUTI.NS":"Auto","HEROMOTOCO.NS":"Auto","EICHERMOT.NS":"Auto","BAJAJ-AUTO.NS":"Auto","TVSMOTOR.NS":"Auto","MOTHERSON.NS":"Auto","ULTRACEMCO.NS":"Cement","GRASIM.NS":"Cement","AMBUJACEM.NS":"Cement","ADANIPORTS.NS":"Infrastructure","ADANIENT.NS":"Infrastructure","ADANIGREEN.NS":"Infrastructure","ADANIPOWER.NS":"Infrastructure","POWERGRID.NS":"Infrastructure","NTPC.NS":"Infrastructure","JSWENERGY.NS":"Infrastructure"}
heat_rows = []
for s in stock_list[:min(20, len(stock_list))]:
    d = get_history(s, period="3mo")
    if not d.empty and len(d) > 22:
        ret = ((float(d["Close"].iloc[-1]) / float(d["Close"].iloc[-22])) - 1) * 100
        heat_rows.append({"Symbol": s.replace('.NS',''), "Sector": sector_map.get(s, "Others"), "Return": round(ret, 2)})
if heat_rows:
    heat_df = pd.DataFrame(heat_rows)
    fig_heat = px.treemap(heat_df, path=["Sector", "Symbol"], values="Return", color="Return", color_continuous_scale="RdYlGn")
    fig_heat.update_layout(height=520, margin=dict(l=10,r=10,t=20,b=10), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_heat, use_container_width=True)
    sector_leader = heat_df.groupby("Sector", as_index=False)["Return"].mean().sort_values("Return", ascending=False); sector_leader["Return"] = sector_leader["Return"].round(2)
    st.dataframe(style_df(sector_leader), use_container_width=True)

# -------------------------------------------------
# FUNDAMENTAL SNAPSHOT (ENHANCED)
# -------------------------------------------------
st.markdown("<div class='glass-card'><div class='section-title'>Fundamental Snapshot</div></div>", unsafe_allow_html=True)
fs1, fs2, fs3, fs4 = st.columns(4)
with fs1: st.metric("Sector", info.get("sector", "N/A"))
with fs2: st.metric("Industry", info.get("industry", "N/A"))
with fs3: st.metric("P/E", f"{info.get('trailingPE', 'N/A')}")
with fs4: st.metric("Market Cap", f"₹{(info.get('marketCap', 0) or 0)/1e7:,.0f} Cr" if info.get('marketCap') else "N/A")
fs5, fs6, fs7, fs8 = st.columns(4)
with fs5: st.metric("ROE", f"{round((info.get('returnOnEquity', 0) or 0)*100, 2)}%" if info.get('returnOnEquity') is not None else "N/A")
with fs6: st.metric("Debt / Equity", f"{info.get('debtToEquity', 'N/A')}")
with fs7: st.metric("Revenue Growth", f"{round((info.get('revenueGrowth', 0) or 0)*100, 2)}%" if info.get('revenueGrowth') is not None else "N/A")
with fs8: st.metric("Profit Margin", f"{round((info.get('profitMargins', 0) or 0)*100, 2)}%" if info.get('profitMargins') is not None else "N/A")

# -------------------------------------------------
# TECHNICAL SNAPSHOT (ENHANCED)
# -------------------------------------------------
st.markdown("<div class='glass-card'><div class='section-title'>Technical Snapshot</div></div>", unsafe_allow_html=True)
ts1, ts2, ts3, ts4 = st.columns(4)
with ts1: st.metric("SMA20", f"{df.iloc[-1]['SMA20']:.2f}")
with ts2: st.metric("SMA50", f"{df.iloc[-1]['SMA50']:.2f}")
with ts3: st.metric("MACD", f"{df.iloc[-1]['MACD']:.2f}")
with ts4: st.metric("MACD Signal", f"{df.iloc[-1]['MACD_SIGNAL']:.2f}")
ts5, ts6, ts7, ts8 = st.columns(4)
with ts5: st.metric("RSI (14)", f"{rsi:.2f}")
with ts6: st.metric("ATR (14)", f"{atr:.2f}")
with ts7: st.metric("20D Support", f"{support_level:.2f}")
with ts8: st.metric("20D Resistance", f"{breakout_level:.2f}")

# -------------------------------------------------
# FUNDAMENTAL RATIO BUTTON (VISIBLE SECTION)
# -------------------------------------------------
st.markdown("<div class='glass-card'><div class='section-title'>Fundamental Ratio Controls</div></div>", unsafe_allow_html=True)
fr1, fr2 = st.columns(2)
with fr1:
    show_fundamental_ratio = st.button("Fundamental Ratio")
with fr2:
    show_technical_ratio = st.button("Technical Ratio")

if show_fundamental_ratio:
    fund_df = pd.DataFrame([
        {"Ratio":"P/E","Value":info.get("trailingPE","N/A")},{"Ratio":"Forward P/E","Value":info.get("forwardPE","N/A")},{"Ratio":"Price / Book","Value":info.get("priceToBook","N/A")},
        {"Ratio":"ROE (%)","Value":round((info.get("returnOnEquity",0) or 0)*100,2) if info.get("returnOnEquity") is not None else "N/A"},{"Ratio":"ROA (%)","Value":round((info.get("returnOnAssets",0) or 0)*100,2) if info.get("returnOnAssets") is not None else "N/A"},
        {"Ratio":"Debt / Equity","Value":info.get("debtToEquity","N/A")},{"Ratio":"Current Ratio","Value":info.get("currentRatio","N/A")},{"Ratio":"Quick Ratio","Value":info.get("quickRatio","N/A")},
        {"Ratio":"Profit Margin (%)","Value":round((info.get("profitMargins",0) or 0)*100,2) if info.get("profitMargins") is not None else "N/A"},{"Ratio":"Operating Margin (%)","Value":round((info.get("operatingMargins",0) or 0)*100,2) if info.get("operatingMargins") is not None else "N/A"},
        {"Ratio":"Revenue Growth (%)","Value":round((info.get("revenueGrowth",0) or 0)*100,2) if info.get("revenueGrowth") is not None else "N/A"},{"Ratio":"Dividend Yield (%)","Value":round((info.get("dividendYield",0) or 0)*100,2) if info.get("dividendYield") is not None else "N/A"},
    ])
    st.markdown("<div class='glass-card'><div class='section-title'>Fundamental Ratio Analysis</div></div>", unsafe_allow_html=True)
    st.dataframe(style_df(fund_df), use_container_width=True)

if show_technical_ratio:
    last = df.iloc[-1]
    tech_df = pd.DataFrame([
        {"Metric":"Price vs SMA20 (%)","Value":round(((last['Close']/last['SMA20'])-1)*100,2)},{"Metric":"Price vs SMA50 (%)","Value":round(((last['Close']/last['SMA50'])-1)*100,2)},
        {"Metric":"SMA20 vs SMA50 (%)","Value":round(((last['SMA20']/last['SMA50'])-1)*100,2)},{"Metric":"RSI (14)","Value":round(last['RSI14'],2)},{"Metric":"MACD","Value":round(last['MACD'],2)},
        {"Metric":"MACD Signal","Value":round(last['MACD_SIGNAL'],2)},{"Metric":"MACD Histogram","Value":round(last['MACD_HIST'],2)},{"Metric":"ATR (14)","Value":round(last['ATR14'],2)},
        {"Metric":"Distance to 20D High (%)","Value":round(((last['Close']/breakout_level)-1)*100,2)},{"Metric":"Distance to 20D Low (%)","Value":round(((last['Close']/support_level)-1)*100,2)},
        {"Metric":"Bollinger Upper Gap (%)","Value":round(((last['Close']/last['BB_UPPER'])-1)*100,2)},{"Metric":"Bollinger Lower Gap (%)","Value":round(((last['Close']/last['BB_LOWER'])-1)*100,2)},
    ])
    st.markdown("<div class='glass-card'><div class='section-title'>Technical Ratio Analysis</div></div>", unsafe_allow_html=True)
    st.dataframe(style_df(tech_df), use_container_width=True)

# -------------------------------------------------
# BALANCE SHEET / FINANCIALS / CASH FLOW (VISIBLE SECTION)
# -------------------------------------------------
st.markdown("<div class='glass-card'><div class='section-title'>Balance Sheet / Financials / Cash Flow (₹ Cr)</div></div>", unsafe_allow_html=True)
btab1, btab2, btab3 = st.tabs(["Balance Sheet", "Financials", "Cash Flow"])
with btab1:
    if isinstance(bs, pd.DataFrame) and not bs.empty:
        st.dataframe(style_df((bs.iloc[:, :4].fillna(0) / 1e7).round(2)), use_container_width=True)
    else:
        st.info("Balance sheet not available for this symbol.")
with btab2:
    if isinstance(fin, pd.DataFrame) and not fin.empty:
        st.dataframe(style_df((fin.iloc[:, :4].fillna(0) / 1e7).round(2)), use_container_width=True)
    else:
        st.info("Financials not available for this symbol.")
with btab3:
    if isinstance(cf, pd.DataFrame) and not cf.empty:
        st.dataframe(style_df((cf.iloc[:, :4].fillna(0) / 1e7).round(2)), use_container_width=True)
    else:
        st.info("Cash flow not available for this symbol.")

# Ratios
if show_fundamental_ratio:
    fund_df = pd.DataFrame([
        {"Ratio":"P/E","Value":info.get("trailingPE","N/A")},{"Ratio":"Forward P/E","Value":info.get("forwardPE","N/A")},{"Ratio":"Price / Book","Value":info.get("priceToBook","N/A")},
        {"Ratio":"ROE (%)","Value":round((info.get("returnOnEquity",0) or 0)*100,2) if info.get("returnOnEquity") is not None else "N/A"},{"Ratio":"ROA (%)","Value":round((info.get("returnOnAssets",0) or 0)*100,2) if info.get("returnOnAssets") is not None else "N/A"},
        {"Ratio":"Debt / Equity","Value":info.get("debtToEquity","N/A")},{"Ratio":"Current Ratio","Value":info.get("currentRatio","N/A")},{"Ratio":"Quick Ratio","Value":info.get("quickRatio","N/A")},
        {"Ratio":"Profit Margin (%)","Value":round((info.get("profitMargins",0) or 0)*100,2) if info.get("profitMargins") is not None else "N/A"},{"Ratio":"Operating Margin (%)","Value":round((info.get("operatingMargins",0) or 0)*100,2) if info.get("operatingMargins") is not None else "N/A"},
        {"Ratio":"Revenue Growth (%)","Value":round((info.get("revenueGrowth",0) or 0)*100,2) if info.get("revenueGrowth") is not None else "N/A"},{"Ratio":"Dividend Yield (%)","Value":round((info.get("dividendYield",0) or 0)*100,2) if info.get("dividendYield") is not None else "N/A"},
    ])
    st.markdown("<div class='glass-card'><div class='section-title'>Fundamental Ratio Analysis</div></div>", unsafe_allow_html=True)
    st.dataframe(style_df(fund_df), use_container_width=True)
if show_technical_ratio:
    last = df.iloc[-1]
    tech_df = pd.DataFrame([
        {"Metric":"Price vs SMA20 (%)","Value":round(((last['Close']/last['SMA20'])-1)*100,2)},{"Metric":"Price vs SMA50 (%)","Value":round(((last['Close']/last['SMA50'])-1)*100,2)},
        {"Metric":"SMA20 vs SMA50 (%)","Value":round(((last['SMA20']/last['SMA50'])-1)*100,2)},{"Metric":"RSI (14)","Value":round(last['RSI14'],2)},{"Metric":"MACD","Value":round(last['MACD'],2)},
        {"Metric":"MACD Signal","Value":round(last['MACD_SIGNAL'],2)},{"Metric":"MACD Histogram","Value":round(last['MACD_HIST'],2)},{"Metric":"ATR (14)","Value":round(last['ATR14'],2)},
        {"Metric":"Distance to 20D High (%)","Value":round(((last['Close']/breakout_level)-1)*100,2)},{"Metric":"Distance to 20D Low (%)","Value":round(((last['Close']/support_level)-1)*100,2)},
        {"Metric":"Bollinger Upper Gap (%)","Value":round(((last['Close']/last['BB_UPPER'])-1)*100,2)},{"Metric":"Bollinger Lower Gap (%)","Value":round(((last['Close']/last['BB_LOWER'])-1)*100,2)},
    ])
    st.markdown("<div class='glass-card'><div class='section-title'>Technical Ratio Analysis</div></div>", unsafe_allow_html=True)
    st.dataframe(style_df(tech_df), use_container_width=True)

# Balance / P&L / CF in Cr with styling
st.markdown("<div class='glass-card'><div class='section-title'>Balance Sheet / P&L / Cash Flow (₹ Cr)</div></div>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["Balance Sheet", "Financials", "Cash Flow"])
with tab1:
    if isinstance(bs, pd.DataFrame) and not bs.empty: st.dataframe(style_df((bs.iloc[:, :4].fillna(0) / 1e7).round(2)), use_container_width=True)
    else: st.info("Balance sheet not available for this symbol.")
with tab2:
    if isinstance(fin, pd.DataFrame) and not fin.empty: st.dataframe(style_df((fin.iloc[:, :4].fillna(0) / 1e7).round(2)), use_container_width=True)
    else: st.info("Financials not available for this symbol.")
with tab3:
    if isinstance(cf, pd.DataFrame) and not cf.empty: st.dataframe(style_df((cf.iloc[:, :4].fillna(0) / 1e7).round(2)), use_container_width=True)
    else: st.info("Cash flow not available for this symbol.")

# Watchlist
watch_df = pd.DataFrame([{"Symbol": symbol, "AI": ai_action, "Last Price": round(last_close, 2), "Score": score, "Verdict": verdict, "Entry": round(entry, 2), "Stop": round(stop_loss, 2), "Target": round(target, 2), "Qty": qty}])
st.markdown("<div class='glass-card'><div class='section-title'>Watchlist Decision Matrix</div></div>", unsafe_allow_html=True)
st.dataframe(style_df(watch_df), use_container_width=True)
st.download_button("Download Trade Plan CSV", data=watch_df.to_csv(index=False).encode("utf-8"), file_name=f"{symbol.replace('.NS','')}_trade_plan.csv", mime="text/csv")

# Scanner with premium cards + mini sparklines
if run_scan:
    st.markdown("<div class='glass-card'><div class='section-title'>Institutional Breakout Scanner</div></div>", unsafe_allow_html=True)
    rows = []; spark_map = {}
    progress = st.progress(0); status = st.empty(); universe = stock_list[:scan_count]
    for i, s in enumerate(universe, start=1):
        status.info(f"Scanning {s} ({i}/{len(universe)})")
        data = get_history(s, period="6mo"); data = compute_indicators(data) if not data.empty else pd.DataFrame()
        if not data.empty:
            sc, vd, _ = score_stock(data); lc = safe_last(data["Close"]); r = safe_last(data["RSI14"]); bh = float(data["RESIST20"].iloc[-1]); sl = float(data["SUPPORT20"].iloc[-1])
            tr_sig = "Bullish" if data.iloc[-1]["SMA20"] > data.iloc[-1]["SMA50"] else "Bearish"; mc_sig = "Bullish" if data.iloc[-1]["MACD"] > data.iloc[-1]["MACD_SIGNAL"] else "Bearish"
            ai_sig, _, _ = ai_badge(sc, r, tr_sig, mc_sig); ent = bh * 1.002
            rows.append({"Symbol": s, "AI": ai_sig, "Price": round(lc,2), "Score": sc, "Verdict": vd, "RSI": round(r,2) if pd.notna(r) else np.nan, "Entry": round(ent,2), "Stop": round(sl,2), "Breakout Level": round(bh,2)})
            spark_map[s] = data["Close"].tail(20).tolist()
        progress.progress(i / len(universe)); time.sleep(0.02)
    status.empty()
    scan_df = pd.DataFrame(rows).sort_values(["Score","RSI"], ascending=[False, False]).reset_index(drop=True)
    if not scan_df.empty:
        st.markdown("<div class='glass-card'><div class='section-title'>Top 5 Opportunity Cards</div></div>", unsafe_allow_html=True)
        top5 = scan_df.head(5); cols = st.columns(min(5, len(top5)))
        for idx2, (_, row) in enumerate(top5.iterrows()):
            with cols[idx2]:
                sp = sparkline_html(spark_map.get(row['Symbol'], []), "#22c55e")
                st.markdown(f"<div class='scanner-card'><div style='font-size:1rem;font-weight:900;color:#fff'>{row['Symbol'].replace('.NS','')}</div><div style='color:#c4b5fd;font-weight:800;margin-top:6px'>AI: {row['AI']}</div><div style='margin-top:8px;color:#e2e8f0'>Score: {row['Score']}</div><div style='color:#e2e8f0'>Entry: ₹{row['Entry']}</div><div style='color:#e2e8f0'>SL: ₹{row['Stop']}</div>{sp}<div style='color:#86efac;font-weight:800;margin-top:6px'>{row['Verdict']}</div></div>", unsafe_allow_html=True)
        st.dataframe(style_df(scan_df), use_container_width=True)
        fig = px.bar(scan_df.head(10), x="Symbol", y="Score", hover_data=["Price","RSI","Verdict","AI"], template="plotly_dark", title="Top Institutional Setups")
        fig.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No scan results available.")

st.caption("Nile is a stock analysis dashboard for educational and research use. Data may be delayed/incomplete depending on source availability. Always verify before trading.")

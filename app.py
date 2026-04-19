# FINAL NILE V12.6 BLACKROCK TERMINAL LAYOUT
# Single-file Streamlit app.py
# Visible App Name: Nile
# Subtitle: Stock Analysis • Fundamental + Technical
# NOTE: Same app name and same core features as before.
# This version ONLY changes the layout/structure to a true premium institutional terminal style.

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
# BLACKROCK TERMINAL CSS
# -------------------------------------------------
st.markdown("""
<style>
:root {
    --bg:#020617; --bg2:#071226; --panel:rgba(9,18,35,.92); --panel2:rgba(15,23,42,.92);
    --stroke:rgba(148,163,184,.10); --text:#f8fafc; --muted:#94a3b8;
    --green:#22c55e; --red:#ef4444; --amber:#f59e0b; --blue:#3b82f6; --cyan:#06b6d4; --violet:#8b5cf6;
}
.stApp {
    background:
      radial-gradient(circle at 8% 8%, rgba(59,130,246,.12), transparent 18%),
      radial-gradient(circle at 92% 10%, rgba(139,92,246,.10), transparent 20%),
      linear-gradient(180deg, var(--bg) 0%, var(--bg2) 100%);
    color:var(--text);
}
.block-container { max-width: 1850px; padding-top: .5rem; padding-bottom: 2rem; }
.nile-title { font-size: 2.8rem; font-weight: 900; color:#fff; margin-bottom:.05rem; }
.nile-sub { color:#c4b5fd; font-size:1rem; font-weight:700; margin-bottom:.8rem; }
.terminal-bar, .top-ribbon {
    background: linear-gradient(90deg, rgba(30,41,59,.92), rgba(15,23,42,.94));
    border:1px solid rgba(255,255,255,.06); border-radius:20px; padding:10px 14px; margin-bottom:12px;
    box-shadow:0 10px 30px rgba(0,0,0,.22); backdrop-filter: blur(10px);
}
.panel {
    background: linear-gradient(180deg, rgba(9,18,35,.94), rgba(15,23,42,.92));
    border:1px solid rgba(255,255,255,.06); border-radius:22px; padding:16px;
    box-shadow:0 12px 34px rgba(0,0,0,.24); margin-bottom:12px;
}
.panel-title { font-size:1rem; font-weight:900; color:#fff; margin-bottom:10px; }
.pill { display:inline-block; padding:6px 10px; border-radius:999px; margin:0 6px 6px 0; background:rgba(30,41,59,.8); border:1px solid rgba(255,255,255,.06); color:#e2e8f0; font-size:.78rem; font-weight:800; }
.big-badge-buy,.big-badge-hold,.big-badge-sell { padding:18px; border-radius:18px; font-weight:900; text-align:center; font-size:1.05rem; }
.big-badge-buy { background:linear-gradient(90deg, rgba(34,197,94,.22), rgba(34,197,94,.08)); color:#86efac; border:1px solid rgba(34,197,94,.28); }
.big-badge-hold { background:linear-gradient(90deg, rgba(245,158,11,.22), rgba(245,158,11,.08)); color:#fcd34d; border:1px solid rgba(245,158,11,.28); }
.big-badge-sell { background:linear-gradient(90deg, rgba(239,68,68,.22), rgba(239,68,68,.08)); color:#fca5a5; border:1px solid rgba(239,68,68,.28); }
.metric-mini { background:rgba(15,23,42,.7); border:1px solid rgba(255,255,255,.05); border-radius:16px; padding:12px; margin-bottom:10px; }
.metric-lbl { color:#94a3b8; font-size:.75rem; margin-bottom:4px; }
.metric-val { color:#fff; font-size:1.35rem; font-weight:900; }
.small { color:#cbd5e1; font-size:.85rem; font-weight:700; }
.scanner-card { background:linear-gradient(180deg, rgba(30,41,59,.85), rgba(15,23,42,.88)); border:1px solid rgba(255,255,255,.06); border-radius:18px; padding:12px; min-height:180px; }
.stButton > button, .stDownloadButton > button { width:100%; border-radius:14px; border:1px solid rgba(255,255,255,.08); color:white; font-weight:900; padding:.7rem .9rem; }
.stButton > button { background: linear-gradient(90deg, #2563eb, #7c3aed); }
.stDownloadButton > button { background: linear-gradient(90deg, #0f766e, #2563eb); }
div[data-testid="stSidebar"] { background: linear-gradient(180deg, rgba(7,12,24,.99), rgba(11,18,32,.99)); border-right:1px solid rgba(148,163,184,.08); }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# UNIVERSE
# -------------------------------------------------
NIFTY_50 = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","BHARTIARTL.NS","ICICIBANK.NS","SBIN.NS","INFY.NS","HINDUNILVR.NS","ITC.NS","LT.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","NESTLEIND.NS","BAJAJFINSV.NS","HCLTECH.NS","WIPRO.NS","NTPC.NS","POWERGRID.NS","TATAMOTORS.NS","M&M.NS","ONGC.NS","COALINDIA.NS","TATASTEEL.NS","JSWSTEEL.NS","ADANIPORTS.NS","INDUSINDBK.NS","TECHM.NS","GRASIM.NS","CIPLA.NS","DRREDDY.NS","HINDALCO.NS","HEROMOTOCO.NS","EICHERMOT.NS","BPCL.NS","BRITANNIA.NS","APOLLOHOSP.NS","DIVISLAB.NS","ADANIENT.NS","TATACONSUM.NS","PIDILITIND.NS","SBILIFE.NS","BAJAJ-AUTO.NS","SHRIRAMFIN.NS","TRENT.NS"]
NIFTY_NEXT_50 = ["ABB.NS","ADANIGREEN.NS","ADANIPOWER.NS","AMBUJACEM.NS","BANKBARODA.NS","BOSCHLTD.NS","CANBK.NS","CGPOWER.NS","CHOLAFIN.NS","DABUR.NS","DLF.NS","GAIL.NS","GODREJCP.NS","HAL.NS","HAVELLS.NS","ICICIGI.NS","ICICIPRULI.NS","INDIGO.NS","IOC.NS","IRCTC.NS","JINDALSTEL.NS","JSWENERGY.NS","LICI.NS","LODHA.NS","LUPIN.NS","MCDOWELL-N.NS","MOTHERSON.NS","NAUKRI.NS","NMDC.NS","PFC.NS","PNB.NS","POLYCAB.NS","RECLTD.NS","SAIL.NS","SIEMENS.NS","TVSMOTOR.NS","UNITDSPR.NS","VEDL.NS","VOLTAS.NS","ZYDUSLIFE.NS","INDUSTOWER.NS","TORNTPHARM.NS","HDFCLIFE.NS","COLPAL.NS","MARICO.NS","UBL.NS","BERGEPAINT.NS","CONCOR.NS","OFSS.NS"]
UNIVERSE = sorted(list(dict.fromkeys(NIFTY_50 + NIFTY_NEXT_50)))

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
@st.cache_data(ttl=900)
def get_history(symbol: str, period: str = "1y", interval: str = "1d"):
    if yf is None: return pd.DataFrame()
    try:
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        return df.dropna().copy()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=1800)
def get_info(symbol: str):
    if yf is None: return {}
    try: return yf.Ticker(symbol).info or {}
    except Exception: return {}

@st.cache_data(ttl=1800)
def get_financials(symbol: str):
    if yf is None: return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    try:
        t = yf.Ticker(symbol)
        return getattr(t, "balance_sheet", pd.DataFrame()), getattr(t, "financials", pd.DataFrame()), getattr(t, "cashflow", pd.DataFrame())
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=300)
def get_index_snapshot():
    symbols = {"NIFTY 50":"^NSEI", "BANKNIFTY":"^NSEBANK", "SENSEX":"^BSESN", "INDIA VIX":"^INDIAVIX"}
    out = {}
    for name, sym in symbols.items():
        d = get_history(sym, period="5d")
        if not d.empty and len(d) >= 2:
            last = float(d["Close"].iloc[-1]); prev = float(d["Close"].iloc[-2]); chg = ((last/prev)-1)*100 if prev else 0
            out[name] = {"value": last, "chg": chg}
    return out


def safe_last(series):
    try: return float(series.dropna().iloc[-1])
    except Exception: return np.nan


def compute_indicators(df):
    if df.empty: return df
    d = df.copy()
    d["SMA20"] = d["Close"].rolling(20).mean(); d["SMA50"] = d["Close"].rolling(50).mean()
    delta = d["Close"].diff(); gain = delta.clip(lower=0).rolling(14).mean(); loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan); d["RSI14"] = 100 - (100 / (1 + rs))
    ema12 = d["Close"].ewm(span=12, adjust=False).mean(); ema26 = d["Close"].ewm(span=26, adjust=False).mean()
    d["MACD"] = ema12 - ema26; d["MACD_SIGNAL"] = d["MACD"].ewm(span=9, adjust=False).mean(); d["MACD_HIST"] = d["MACD"] - d["MACD_SIGNAL"]
    tr1 = d["High"] - d["Low"]; tr2 = (d["High"] - d["Close"].shift()).abs(); tr3 = (d["Low"] - d["Close"].shift()).abs()
    d["ATR14"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1).rolling(14).mean()
    d["SUPPORT20"] = d["Low"].rolling(20).min(); d["RESIST20"] = d["High"].rolling(20).max()
    rm = d["Close"].rolling(20).mean(); rsd = d["Close"].rolling(20).std(); d["BB_UPPER"] = rm + 2*rsd; d["BB_LOWER"] = rm - 2*rsd
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
    if score >= 75 and trend_signal == "Bullish" and macd_signal == "Bullish" and rsi < 75: return "BUY", "big-badge-buy", "High conviction setup"
    elif score >= 45: return "HOLD", "big-badge-hold", "Wait for better confirmation"
    return "SELL", "big-badge-sell", "Weak setup / avoid now"


def conviction_meter(score, rsi, trend_signal, macd_signal):
    conviction = score + (5 if trend_signal == "Bullish" else 0) + (5 if macd_signal == "Bullish" else 0)
    if 50 <= rsi <= 70: conviction += 5
    elif rsi > 80 or rsi < 25: conviction -= 5
    conviction = max(0, min(100, conviction))
    label = "Very Strong" if conviction >= 85 else "Strong" if conviction >= 70 else "Moderate" if conviction >= 50 else "Weak"
    return conviction, label


def sparkline_html(values, color="#06b6d4"):
    vals = [float(v) for v in values if pd.notna(v)]
    if len(vals) < 2: return ""
    mn, mx = min(vals), max(vals)
    if mx == mn: mx += 1
    pts = []
    for i, v in enumerate(vals):
        x = i * (100 / max(len(vals)-1,1)); y = 28 - ((v - mn) / (mx - mn)) * 24; pts.append(f"{x:.1f},{y:.1f}")
    return f"<svg width='100%' height='34' viewBox='0 0 100 34' preserveAspectRatio='none'><polyline fill='none' stroke='{color}' stroke-width='2.2' points='{' '.join(pts)}' /></svg>"


def style_df(df):
    num_cols = df.select_dtypes(include=[np.number]).columns
    return df.style.format(precision=2).background_gradient(cmap="RdYlGn", subset=num_cols)


def make_gauge(value):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=value, title={'text': "Conviction"}, gauge={'axis': {'range': [0,100]}, 'bar': {'color': "#06b6d4"}, 'steps':[{'range':[0,40],'color':"rgba(239,68,68,.35)"},{'range':[40,70],'color':"rgba(245,158,11,.35)"},{'range':[70,100],'color':"rgba(34,197,94,.35)"}]}))
    fig.update_layout(height=240, margin=dict(l=10,r=10,t=30,b=10), paper_bgcolor="rgba(0,0,0,0)")
    return fig


def make_candlestick(df, symbol, entry=None, stop=None, target=None):
    fig = go.Figure(); sup = float(df["SUPPORT20"].iloc[-1]); res = float(df["RESIST20"].iloc[-1])
    fig.add_hrect(y0=sup*0.995, y1=sup*1.005, fillcolor="rgba(34,197,94,0.10)", line_width=0)
    fig.add_hrect(y0=res*0.995, y1=res*1.005, fillcolor="rgba(239,68,68,0.10)", line_width=0)
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA20", line=dict(width=1.8)))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA50", line=dict(width=1.8)))
    if "Volume" in df.columns: fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume", opacity=0.22, yaxis="y2"))
    if entry is not None: fig.add_hline(y=entry, line_dash="dash", annotation_text="Entry")
    if stop is not None: fig.add_hline(y=stop, line_dash="dash", annotation_text="SL")
    if target is not None: fig.add_hline(y=target, line_dash="dash", annotation_text="Target")
    fig.update_layout(template="plotly_dark", title=f"{symbol} Terminal Price Structure", height=720, xaxis_rangeslider_visible=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis2=dict(overlaying='y', side='right', visible=False), margin=dict(l=10,r=10,t=40,b=10))
    return fig

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.markdown("## Nile")
    st.caption("Stock Analysis • Fundamental + Technical")
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
# HEADER + RIBBON
# -------------------------------------------------
st.markdown("<div class='nile-title'>Nile</div>", unsafe_allow_html=True)
st.markdown("<div class='nile-sub'>Stock Analysis • Fundamental + Technical</div>", unsafe_allow_html=True)
idx = get_index_snapshot()
parts = []
for k, v in idx.items():
    color = '#22c55e' if v['chg'] >= 0 else '#ef4444'; arrow = '▲' if v['chg'] >= 0 else '▼'
    parts.append(f"<span class='pill'>{k}: {v['value']:.2f} <span style='color:{color}'>{arrow} {v['chg']:+.2f}%</span></span>")
st.markdown(f"<div class='top-ribbon'>{''.join(parts) if parts else '<span class=\'pill\'>NIFTY 50</span><span class=\'pill\'>BANKNIFTY</span><span class=\'pill\'>SENSEX</span><span class=\'pill\'>INDIA VIX</span>'}</div>", unsafe_allow_html=True)

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
allowed_risk = capital * (risk_pct / 100); qty = max(int(allowed_risk // risk_per_share), 0); target = entry + (risk_per_share * rr_ratio)
ai_action, ai_class, ai_reason = ai_badge(score, rsi, trend_signal, macd_signal); conviction_score, conviction_label = conviction_meter(score, rsi, trend_signal, macd_signal)

# top movers sample
perf_rows = []
for s in stock_list[:min(20, len(stock_list))]:
    d = get_history(s, period="1mo")
    if not d.empty and len(d) > 6:
        ret = ((float(d["Close"].iloc[-1]) / float(d["Close"].iloc[0])) - 1) * 100
        perf_rows.append((s.replace('.NS',''), ret))
perf_df = pd.DataFrame(perf_rows, columns=["Symbol","Ret"]).sort_values("Ret", ascending=False) if perf_rows else pd.DataFrame()

# -------------------------------------------------
# TRUE 3-ZONE TERMINAL LAYOUT
# -------------------------------------------------
left_col, center_col, right_col = st.columns([1.1, 2.4, 1.1])

# LEFT SIGNAL PANEL
with left_col:
    st.markdown("<div class='panel'><div class='panel-title'>Signal Console</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='{ai_class}'>AI {ai_action} • {conviction_score}% Confidence<br><span style='font-size:.9rem;font-weight:700'>{ai_reason}</span></div>", unsafe_allow_html=True)
    st.plotly_chart(make_gauge(conviction_score), use_container_width=True)
    st.markdown(f"<div class='metric-mini'><div class='metric-lbl'>Last Price</div><div class='metric-val'>₹{last_close:,.2f}</div><div class='small'>{change_pct:+.2f}% today</div>{sparkline_html(df['Close'].tail(20).tolist(), '#22c55e' if change_pct >= 0 else '#ef4444')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-mini'><div class='metric-lbl'>Institutional Score</div><div class='metric-val'>{score}/100</div><div class='small'>{verdict}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-mini'><div class='metric-lbl'>Trade Plan</div><div class='small'>Entry: ₹{entry:,.2f}</div><div class='small'>SL: ₹{stop_loss:,.2f}</div><div class='small'>Target: ₹{target:,.2f}</div><div class='small'>Qty: {qty}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-mini'><div class='metric-lbl'>Bias</div><span class='pill'>Trend: {trend_signal}</span><span class='pill'>MACD: {macd_signal}</span><span class='pill'>RSI: {rsi:.1f}</span></div>", unsafe_allow_html=True)

# CENTER HERO PANEL
with center_col:
    st.markdown("<div class='panel'><div class='panel-title'>Hero Chart</div></div>", unsafe_allow_html=True)
    st.plotly_chart(make_candlestick(df.tail(220), symbol, entry, stop_loss, target), use_container_width=True)

# RIGHT INTELLIGENCE PANEL
with right_col:
    st.markdown("<div class='panel'><div class='panel-title'>Market Intelligence</div></div>", unsafe_allow_html=True)
    if not perf_df.empty:
        top_g = perf_df.head(3); top_l = perf_df.tail(3).sort_values('Ret')
        st.markdown("<div class='metric-mini'><div class='metric-lbl'>Top Gainers</div>" + ''.join([f"<div class='small'>🟢 {r.Symbol}: {r.Ret:+.2f}%</div>" for _, r in top_g.iterrows()]) + "</div>", unsafe_allow_html=True)
        st.markdown("<div class='metric-mini'><div class='metric-lbl'>Top Losers</div>" + ''.join([f"<div class='small'>🔴 {r.Symbol}: {r.Ret:+.2f}%</div>" for _, r in top_l.iterrows()]) + "</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-mini'><div class='metric-lbl'>Company Snapshot</div><div class='small'>Sector: {info.get('sector','N/A')}</div><div class='small'>Industry: {info.get('industry','N/A')}</div><div class='small'>Market Cap: {'₹'+format((info.get('marketCap',0) or 0)/1e7, ',.0f')+' Cr' if info.get('marketCap') else 'N/A'}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-mini'><div class='metric-lbl'>Technical Snapshot</div><div class='small'>SMA20: {df.iloc[-1]['SMA20']:.2f}</div><div class='small'>SMA50: {df.iloc[-1]['SMA50']:.2f}</div><div class='small'>MACD: {df.iloc[-1]['MACD']:.2f}</div><div class='small'>ATR: {atr:.2f}</div></div>", unsafe_allow_html=True)

# -------------------------------------------------
# TABBED MODULES (REAL DIFFERENT LOOK)
# -------------------------------------------------
overview_tab, tech_tab, fund_tab, bs_tab, fin_tab, cf_tab, compare_tab, sector_tab, scan_tab = st.tabs([
    "Overview", "Technical Analysis", "Fundamental Analysis", "Balance Sheet", "Financials", "Cash Flow", "Compare", "Sector View", "Scanner"
])

with overview_tab:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("RSI (14)", f"{rsi:.2f}")
    c2.metric("ATR (14)", f"{atr:.2f}")
    c3.metric("20D Support", f"{support_level:.2f}")
    c4.metric("20D Resistance", f"{breakout_level:.2f}")
    st.download_button("Download Trade Plan CSV", data=pd.DataFrame([{"Symbol": symbol, "AI": ai_action, "Price": round(last_close,2), "Score": score, "Entry": round(entry,2), "Stop": round(stop_loss,2), "Target": round(target,2), "Qty": qty}]).to_csv(index=False).encode('utf-8'), file_name=f"{symbol.replace('.NS','')}_trade_plan.csv", mime="text/csv")

with tech_tab:
    tech_df = pd.DataFrame([
        {"Metric":"Price vs SMA20 (%)","Value":round(((df.iloc[-1]['Close']/df.iloc[-1]['SMA20'])-1)*100,2)}, {"Metric":"Price vs SMA50 (%)","Value":round(((df.iloc[-1]['Close']/df.iloc[-1]['SMA50'])-1)*100,2)},
        {"Metric":"SMA20 vs SMA50 (%)","Value":round(((df.iloc[-1]['SMA20']/df.iloc[-1]['SMA50'])-1)*100,2)}, {"Metric":"RSI (14)","Value":round(df.iloc[-1]['RSI14'],2)},
        {"Metric":"MACD","Value":round(df.iloc[-1]['MACD'],2)}, {"Metric":"MACD Signal","Value":round(df.iloc[-1]['MACD_SIGNAL'],2)}, {"Metric":"MACD Histogram","Value":round(df.iloc[-1]['MACD_HIST'],2)},
        {"Metric":"ATR (14)","Value":round(df.iloc[-1]['ATR14'],2)}, {"Metric":"Distance to 20D High (%)","Value":round(((df.iloc[-1]['Close']/breakout_level)-1)*100,2)}, {"Metric":"Distance to 20D Low (%)","Value":round(((df.iloc[-1]['Close']/support_level)-1)*100,2)}
    ])
    st.dataframe(style_df(tech_df), use_container_width=True)

with fund_tab:
    fund_df = pd.DataFrame([
        {"Ratio":"Sector","Value":info.get("sector","N/A")}, {"Ratio":"Industry","Value":info.get("industry","N/A")}, {"Ratio":"P/E","Value":info.get("trailingPE","N/A")}, {"Ratio":"Forward P/E","Value":info.get("forwardPE","N/A")},
        {"Ratio":"Price / Book","Value":info.get("priceToBook","N/A")}, {"Ratio":"ROE (%)","Value":round((info.get("returnOnEquity",0) or 0)*100,2) if info.get("returnOnEquity") is not None else "N/A"},
        {"Ratio":"ROA (%)","Value":round((info.get("returnOnAssets",0) or 0)*100,2) if info.get("returnOnAssets") is not None else "N/A"}, {"Ratio":"Debt / Equity","Value":info.get("debtToEquity","N/A")},
        {"Ratio":"Current Ratio","Value":info.get("currentRatio","N/A")}, {"Ratio":"Quick Ratio","Value":info.get("quickRatio","N/A")}, {"Ratio":"Revenue Growth (%)","Value":round((info.get("revenueGrowth",0) or 0)*100,2) if info.get("revenueGrowth") is not None else "N/A"},
        {"Ratio":"Profit Margin (%)","Value":round((info.get("profitMargins",0) or 0)*100,2) if info.get("profitMargins") is not None else "N/A"}, {"Ratio":"Operating Margin (%)","Value":round((info.get("operatingMargins",0) or 0)*100,2) if info.get("operatingMargins") is not None else "N/A"},
        {"Ratio":"Dividend Yield (%)","Value":round((info.get("dividendYield",0) or 0)*100,2) if info.get("dividendYield") is not None else "N/A"}
    ])
    st.dataframe(style_df(fund_df), use_container_width=True)

with bs_tab:
    if isinstance(bs, pd.DataFrame) and not bs.empty: st.dataframe(style_df((bs.iloc[:, :4].fillna(0) / 1e7).round(2)), use_container_width=True)
    else: st.info("Balance sheet not available for this symbol.")

with fin_tab:
    if isinstance(fin, pd.DataFrame) and not fin.empty: st.dataframe(style_df((fin.iloc[:, :4].fillna(0) / 1e7).round(2)), use_container_width=True)
    else: st.info("Financials not available for this symbol.")

with cf_tab:
    if isinstance(cf, pd.DataFrame) and not cf.empty: st.dataframe(style_df((cf.iloc[:, :4].fillna(0) / 1e7).round(2)), use_container_width=True)
    else: st.info("Cash flow not available for this symbol.")

with compare_tab:
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
        cdf = pd.DataFrame(compare_rows); st.dataframe(style_df(cdf), use_container_width=True)
        fig_norm = go.Figure();
        for name, ser in perf_series: fig_norm.add_trace(go.Scatter(x=ser.index, y=ser.values, mode='lines', name=name))
        fig_norm.update_layout(title="Normalized Performance (Base = 100)", template="plotly_dark", height=360, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_norm, use_container_width=True)

with sector_tab:
    sector_map = {"RELIANCE.NS":"Energy","ONGC.NS":"Energy","BPCL.NS":"Energy","IOC.NS":"Energy","GAIL.NS":"Energy","HDFCBANK.NS":"Financials","ICICIBANK.NS":"Financials","SBIN.NS":"Financials","KOTAKBANK.NS":"Financials","AXISBANK.NS":"Financials","BAJFINANCE.NS":"Financials","BAJAJFINSV.NS":"Financials","SBILIFE.NS":"Financials","PFC.NS":"Financials","RECLTD.NS":"Financials","CHOLAFIN.NS":"Financials","ICICIPRULI.NS":"Financials","LICI.NS":"Financials","BANKBARODA.NS":"Financials","PNB.NS":"Financials","SHRIRAMFIN.NS":"Financials","TCS.NS":"IT","INFY.NS":"IT","HCLTECH.NS":"IT","WIPRO.NS":"IT","TECHM.NS":"IT","OFSS.NS":"IT"}
    heat_rows = []
    for s in stock_list[:min(20, len(stock_list))]:
        d = get_history(s, period="3mo")
        if not d.empty and len(d) > 22:
            ret = ((float(d["Close"].iloc[-1]) / float(d["Close"].iloc[-22])) - 1) * 100
            heat_rows.append({"Symbol": s.replace('.NS',''), "Sector": sector_map.get(s, "Others"), "Return": round(ret, 2)})
    if heat_rows:
        hdf = pd.DataFrame(heat_rows)
        fig_heat = px.treemap(hdf, path=["Sector", "Symbol"], values="Return", color="Return", color_continuous_scale="RdYlGn")
        fig_heat.update_layout(height=520, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_heat, use_container_width=True)
        sector_leader = hdf.groupby("Sector", as_index=False)["Return"].mean().sort_values("Return", ascending=False)
        st.dataframe(style_df(sector_leader), use_container_width=True)

with scan_tab:
    if run_scan:
        rows = []; spark_map = {}
        progress = st.progress(0); status = st.empty(); universe = stock_list[:scan_count]
        for i, s in enumerate(universe, start=1):
            status.info(f"Scanning {s} ({i}/{len(universe)})")
            data = get_history(s, period="6mo"); data = compute_indicators(data) if not data.empty else pd.DataFrame()
            if not data.empty:
                sc, vd, _ = score_stock(data); lc = safe_last(data["Close"]); rr = safe_last(data["RSI14"]); bh = float(data["RESIST20"].iloc[-1]); sl = float(data["SUPPORT20"].iloc[-1])
                tr_sig = "Bullish" if data.iloc[-1]["SMA20"] > data.iloc[-1]["SMA50"] else "Bearish"; mc_sig = "Bullish" if data.iloc[-1]["MACD"] > data.iloc[-1]["MACD_SIGNAL"] else "Bearish"
                ai_sig, _, _ = ai_badge(sc, rr, tr_sig, mc_sig); ent = bh * 1.002
                rows.append({"Symbol": s, "AI": ai_sig, "Price": round(lc,2), "Score": sc, "Verdict": vd, "RSI": round(rr,2) if pd.notna(rr) else np.nan, "Entry": round(ent,2), "Stop": round(sl,2)})
                spark_map[s] = data["Close"].tail(20).tolist()
            progress.progress(i / len(universe)); time.sleep(0.02)
        status.empty()
        sdf = pd.DataFrame(rows).sort_values(["Score","RSI"], ascending=[False, False]).reset_index(drop=True)
        if not sdf.empty:
            cols = st.columns(min(5, len(sdf.head(5))))
            for idx2, (_, row) in enumerate(sdf.head(5).iterrows()):
                with cols[idx2]:
                    sp = sparkline_html(spark_map.get(row['Symbol'], []), "#22c55e")
                    st.markdown(f"<div class='scanner-card'><div style='font-size:1rem;font-weight:900;color:#fff'>{row['Symbol'].replace('.NS','')}</div><div class='small'>AI: {row['AI']}</div><div class='small'>Score: {row['Score']}</div><div class='small'>Entry: ₹{row['Entry']}</div><div class='small'>SL: ₹{row['Stop']}</div>{sp}<div class='small' style='color:#86efac'>{row['Verdict']}</div></div>", unsafe_allow_html=True)
            st.dataframe(style_df(sdf), use_container_width=True)
    else:
        st.info("Click 'Run Institutional Scan' from the sidebar to load premium scanner results.")

st.caption("Nile is a stock analysis dashboard for educational and research use. Data may be delayed or unavailable depending on source availability.")

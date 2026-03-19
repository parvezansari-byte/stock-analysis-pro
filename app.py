import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Stock Analysis Pro V2 Groww Connect", layout="wide")

# =========================================================
# FINAL STOCK ANALYSIS PRO APP V2 GROWW CONNECT VERSION
# Single-file Streamlit App
# Features:
# - Fundamental + Technical analysis
# - Cloud-safe yfinance handling
# - Groww API connect (safe optional mode)
# - Holdings fetch + analyze my holdings
# - Positions fetch
# - Manual order section (SAFE MODE, disabled by default)
# - Streamlit secrets support
# =========================================================

# -----------------------------
# HELPERS
# -----------------------------
def safe_num(x, default=np.nan):
    try:
        if x is None:
            return default
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default


def format_num(x):
    try:
        if x is None or pd.isna(x):
            return "N/A"
        return f"{float(x):,.2f}"
    except Exception:
        return "N/A"


def format_pct(x):
    try:
        if x is None or pd.isna(x):
            return "N/A"
        return f"{float(x):.2f}%"
    except Exception:
        return "N/A"


def cagr(start, end, years):
    try:
        if start <= 0 or end <= 0 or years <= 0:
            return np.nan
        return ((end / start) ** (1 / years) - 1) * 100
    except Exception:
        return np.nan


def flatten_columns(df):
    try:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        return df
    except Exception:
        return df


def normalize_history(df):
    if df is None or df.empty:
        return pd.DataFrame()
    df = flatten_columns(df.copy())
    required = ["Open", "High", "Low", "Close", "Volume"]
    for col in required:
        if col not in df.columns:
            if col == "Volume":
                df[col] = 0
            else:
                return pd.DataFrame()
    return df.dropna(subset=["Close"]).copy()


def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.bfill().fillna(50)


def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist


def add_indicators(df):
    df = df.copy()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["SMA50"] = df["Close"].rolling(50, min_periods=1).mean()
    df["SMA200"] = df["Close"].rolling(200, min_periods=1).mean()
    df["RSI14"] = compute_rsi(df["Close"], 14)
    macd, signal, hist = compute_macd(df["Close"])
    df["MACD"] = macd
    df["MACD_SIGNAL"] = signal
    df["MACD_HIST"] = hist
    df["VOL20"] = df["Volume"].rolling(20, min_periods=1).mean()
    return df


def detect_support_resistance(df, lookback=60):
    recent = df.tail(min(lookback, len(df)))
    return safe_num(recent["Low"].min()), safe_num(recent["High"].max())


def score_range(value, bands):
    if value is None or pd.isna(value):
        return 0
    for threshold, score in bands:
        if value >= threshold:
            return score
    return 0


def final_rating(score):
    if score >= 85:
        return "STRONG BUY CANDIDATE"
    elif score >= 75:
        return "BUY ON DIPS / ACCUMULATE"
    elif score >= 65:
        return "WATCHLIST / SELECTIVE BUY"
    elif score >= 50:
        return "AVOID FOR NOW"
    return "REJECT / WEAK"


def verdict_color(verdict):
    if "STRONG BUY" in verdict:
        return "#16a34a"
    if "BUY" in verdict:
        return "#22c55e"
    if "WATCHLIST" in verdict:
        return "#eab308"
    return "#ef4444"


def yahoo_to_groww_symbol(ticker):
    if not ticker:
        return ""
    if ticker.endswith(".NS"):
        return ticker.replace(".NS", "")
    if ticker.endswith(".BO"):
        return ticker.replace(".BO", "")
    return ticker


def groww_to_yahoo_symbol(symbol):
    if not symbol:
        return ""
    symbol = str(symbol).strip().upper()
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        return symbol
    return f"{symbol}.NS"


# -----------------------------
# CACHE DATA FETCHERS
# -----------------------------
@st.cache_data(ttl=900, show_spinner=False)
def fetch_history_cached(ticker, period):
    attempts = [
        {"auto_adjust": True, "repair": True},
        {"auto_adjust": False, "repair": True},
        {"auto_adjust": True, "repair": False},
    ]
    for a in attempts:
        try:
            df = yf.download(
                ticker,
                period=period,
                interval="1d",
                progress=False,
                threads=False,
                **a,
            )
            df = normalize_history(df)
            if not df.empty:
                return df
        except Exception:
            continue
    return pd.DataFrame()


@st.cache_data(ttl=900, show_spinner=False)
def fetch_benchmark_cached(period="6mo"):
    try:
        df = yf.download("^NSEI", period=period, interval="1d", progress=False, auto_adjust=True, threads=False)
        return normalize_history(df)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=900, show_spinner=False)
def fetch_fast_info_cached(ticker):
    try:
        tk = yf.Ticker(ticker)
        fi = getattr(tk, "fast_info", None)
        if fi:
            try:
                return dict(fi)
            except Exception:
                return fi
        return {}
    except Exception:
        return {}


def safe_ticker(ticker):
    try:
        return yf.Ticker(ticker)
    except Exception:
        return None


# -----------------------------
# FINANCIAL HELPERS
# -----------------------------
def get_financial_value(df, label_candidates):
    try:
        if df is None or df.empty:
            return None
        for label in label_candidates:
            if label in df.index:
                vals = pd.Series(df.loc[label]).dropna().values
                if len(vals) > 0:
                    return vals[0]
        return None
    except Exception:
        return None


def growth_from_statement(df, label_candidates, years=3):
    try:
        if df is None or df.empty:
            return np.nan
        for label in label_candidates:
            if label in df.index:
                row = pd.Series(df.loc[label]).dropna()
                if len(row) >= years + 1:
                    vals = row.iloc[: years + 1][::-1]
                    start = safe_num(vals.iloc[0])
                    end = safe_num(vals.iloc[-1])
                    return cagr(start, end, years)
        return np.nan
    except Exception:
        return np.nan


def get_quarterly_growth(df, label_candidates):
    try:
        if df is None or df.empty:
            return np.nan
        for label in label_candidates:
            if label in df.index:
                row = pd.Series(df.loc[label]).dropna()
                if len(row) >= 4:
                    latest = safe_num(row.iloc[0])
                    year_ago = safe_num(row.iloc[3])
                    if not pd.isna(year_ago) and year_ago != 0:
                        return ((latest - year_ago) / abs(year_ago)) * 100
        return np.nan
    except Exception:
        return np.nan


# -----------------------------
# FUNDAMENTAL ANALYSIS
# -----------------------------
def fundamental_analysis(ticker_symbol, ticker_obj):
    info = {}
    fast_info = fetch_fast_info_cached(ticker_symbol)

    try:
        info = ticker_obj.info if ticker_obj else {}
        if not isinstance(info, dict):
            info = {}
    except Exception:
        info = {}

    try:
        income = ticker_obj.financials if ticker_obj else pd.DataFrame()
    except Exception:
        income = pd.DataFrame()

    try:
        cashflow = ticker_obj.cashflow if ticker_obj else pd.DataFrame()
    except Exception:
        cashflow = pd.DataFrame()

    try:
        q_income = ticker_obj.quarterly_financials if ticker_obj else pd.DataFrame()
    except Exception:
        q_income = pd.DataFrame()

    revenue_3y = growth_from_statement(income, ["Total Revenue", "Operating Revenue"], years=3)
    profit_3y = growth_from_statement(income, ["Net Income", "Net Income Common Stockholders", "Normalized Income"], years=3)
    q_sales_yoy = get_quarterly_growth(q_income, ["Total Revenue", "Operating Revenue"])
    q_profit_yoy = get_quarterly_growth(q_income, ["Net Income", "Net Income Common Stockholders", "Normalized Income"])

    roe = safe_num(info.get("returnOnEquity"))
    debt_to_equity = safe_num(info.get("debtToEquity"))
    profit_margin = safe_num(info.get("profitMargins"))
    operating_margin = safe_num(info.get("operatingMargins"))
    pe = safe_num(info.get("trailingPE"))
    pb = safe_num(info.get("priceToBook"))

    market_cap = info.get("marketCap", fast_info.get("marketCap") if isinstance(fast_info, dict) else None)
    current_price = info.get("currentPrice", info.get("regularMarketPrice", None))
    if current_price in [None, ""] and isinstance(fast_info, dict):
        current_price = fast_info.get("lastPrice", None)

    fifty_two_high = info.get("fiftyTwoWeekHigh", None)
    fifty_two_low = info.get("fiftyTwoWeekLow", None)
    if isinstance(fast_info, dict):
        fifty_two_high = fifty_two_high if fifty_two_high is not None else fast_info.get("yearHigh", None)
        fifty_two_low = fifty_two_low if fifty_two_low is not None else fast_info.get("yearLow", None)

    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    long_name = info.get("longName", info.get("shortName", ticker_symbol))

    cfo = get_financial_value(cashflow, ["Operating Cash Flow", "Total Cash From Operating Activities"])
    fcf = get_financial_value(cashflow, ["Free Cash Flow"])
    net_income_latest = get_financial_value(income, ["Net Income", "Net Income Common Stockholders", "Normalized Income"])

    cfo_vs_pat = np.nan
    try:
        if cfo is not None and net_income_latest not in [None, 0]:
            cfo_vs_pat = (safe_num(cfo) / abs(safe_num(net_income_latest))) * 100
    except Exception:
        cfo_vs_pat = np.nan

    score = 0
    score += score_range(revenue_3y, [(20, 15), (15, 12), (10, 9), (5, 5)])
    score += score_range(profit_3y, [(20, 15), (15, 12), (10, 9), (5, 5)])
    score += score_range(profit_3y, [(20, 10), (15, 8), (10, 6), (5, 3)])

    roe_pct = roe * 100 if not pd.isna(roe) else np.nan
    score += score_range(roe_pct, [(20, 15), (15, 12), (10, 8), (5, 4)])

    if not pd.isna(debt_to_equity):
        if debt_to_equity <= 50:
            score += 10
        elif debt_to_equity <= 100:
            score += 7
        elif debt_to_equity <= 200:
            score += 4
    else:
        score += 3

    opm_pct = operating_margin * 100 if not pd.isna(operating_margin) else np.nan
    score += score_range(opm_pct, [(20, 10), (15, 8), (10, 6), (5, 3)])

    if not pd.isna(cfo_vs_pat):
        if cfo_vs_pat >= 100:
            score += 10
        elif cfo_vs_pat >= 80:
            score += 8
        elif cfo_vs_pat >= 60:
            score += 5
    else:
        score += 3

    score += 3  # promoter / pledge unavailable on yahoo

    if not pd.isna(pe):
        if pe <= 20:
            score += 10
        elif pe <= 35:
            score += 7
        elif pe <= 50:
            score += 4
    else:
        score += 3

    return {
        "company": long_name,
        "sector": sector,
        "industry": industry,
        "market_cap": market_cap,
        "current_price": current_price,
        "52w_high": fifty_two_high,
        "52w_low": fifty_two_low,
        "sales_growth_3y": revenue_3y,
        "profit_growth_3y": profit_3y,
        "quarterly_sales_yoy": q_sales_yoy,
        "quarterly_profit_yoy": q_profit_yoy,
        "roe": roe_pct,
        "debt_to_equity": debt_to_equity,
        "opm": opm_pct,
        "npm": profit_margin * 100 if not pd.isna(profit_margin) else np.nan,
        "cfo": cfo,
        "fcf": fcf,
        "cfo_vs_pat": cfo_vs_pat,
        "pe": pe,
        "pb": pb,
        "fundamental_score": min(score, 100),
    }


# -----------------------------
# TECHNICAL ANALYSIS
# -----------------------------
def technical_analysis(df):
    df = add_indicators(df)
    latest = df.iloc[-1]

    price = safe_num(latest["Close"])
    ema20 = safe_num(latest["EMA20"])
    sma50 = safe_num(latest["SMA50"])
    sma200 = safe_num(latest["SMA200"])
    rsi = safe_num(latest["RSI14"])
    macd = safe_num(latest["MACD"])
    macd_signal = safe_num(latest["MACD_SIGNAL"])
    volume = safe_num(latest["Volume"], 0)
    vol20 = safe_num(latest["VOL20"], 0)

    support, resistance = detect_support_resistance(df, 60)

    trend_score = 0
    trend_label = "Neutral"
    if price > ema20 and price > sma50 and price > sma200 and sma50 > sma200:
        trend_score = 20
        trend_label = "Strong Bullish"
    elif price > sma50 and price > sma200:
        trend_score = 15
        trend_label = "Bullish"
    elif price > sma200:
        trend_score = 10
        trend_label = "Mild Bullish"
    elif price < sma200:
        trend_score = 4
        trend_label = "Weak / Bearish"

    ma_score = 0
    if price > ema20:
        ma_score += 5
    if price > sma50:
        ma_score += 5
    if price > sma200:
        ma_score += 5

    structure_score = 0
    if not pd.isna(support) and not pd.isna(resistance):
        if price >= resistance * 0.98:
            structure_score = 15
        elif price >= (support + resistance) / 2:
            structure_score = 10
        else:
            structure_score = 6

    volume_score = 0
    if vol20 > 0:
        if volume >= 1.5 * vol20:
            volume_score = 15
        elif volume >= 1.1 * vol20:
            volume_score = 10
        else:
            volume_score = 5
    else:
        volume_score = 3

    rsi_score = 10 if rsi >= 60 else 7 if rsi >= 50 else 4 if rsi >= 40 else 2
    macd_score = 10 if macd > macd_signal else 4

    rs_score = 5
    stock_ret = np.nan
    nifty_ret = np.nan
    try:
        nifty = fetch_benchmark_cached("6mo")
        if not nifty.empty and len(df) >= 2:
            stock_look = min(90, len(df) - 1)
            nifty_look = min(90, len(nifty) - 1)
            stock_ret = ((df["Close"].iloc[-1] / df["Close"].iloc[-(stock_look + 1)]) - 1) * 100
            nifty_ret = ((nifty["Close"].iloc[-1] / nifty["Close"].iloc[-(nifty_look + 1)]) - 1) * 100
            if stock_ret > nifty_ret + 5:
                rs_score = 10
            elif stock_ret > nifty_ret:
                rs_score = 8
            elif stock_ret > nifty_ret - 5:
                rs_score = 5
            else:
                rs_score = 2
    except Exception:
        rs_score = 5

    stop_loss = support if not pd.isna(support) else sma50
    if pd.isna(stop_loss):
        stop_loss = price * 0.92

    target1 = resistance if not pd.isna(resistance) else price * 1.08
    if target1 <= price:
        target1 = price * 1.06
    target2 = max(target1 * 1.08, price * 1.12)

    risk = max(price - stop_loss, 0.01)
    reward = max(target1 - price, 0.01)
    rr = reward / risk if risk > 0 else 1.0

    risk_reward_score = 5 if rr >= 2 else 3 if rr >= 1.2 else 1

    technical_score = min(
        trend_score + ma_score + structure_score + volume_score + rsi_score + macd_score + rs_score + risk_reward_score,
        100,
    )

    return {
        "df": df,
        "price": price,
        "ema20": ema20,
        "sma50": sma50,
        "sma200": sma200,
        "rsi": rsi,
        "macd": macd,
        "macd_signal": macd_signal,
        "support": support,
        "resistance": resistance,
        "trend": trend_label,
        "stock_ret_90d": stock_ret,
        "nifty_ret_90d": nifty_ret,
        "entry_zone": f"{price * 0.98:.2f} - {price * 1.01:.2f}",
        "stop_loss": stop_loss,
        "target1": target1,
        "target2": target2,
        "rr": rr,
        "technical_score": technical_score,
    }


# -----------------------------
# CORE ANALYSIS
# -----------------------------
def analyze_symbol(ticker, period="1y"):
    hist = fetch_history_cached(ticker, period)
    if hist.empty:
        return None
    stock = safe_ticker(ticker)
    fdata = fundamental_analysis(ticker, stock)
    tdata = technical_analysis(hist)
    if fdata.get("current_price") in [None, ""] or pd.isna(safe_num(fdata.get("current_price"))):
        fdata["current_price"] = safe_num(hist["Close"].iloc[-1])
    final_score = round((fdata["fundamental_score"] * 0.60) + (tdata["technical_score"] * 0.40), 2)
    verdict = final_rating(final_score)
    return {"fdata": fdata, "tdata": tdata, "final_score": final_score, "verdict": verdict}


# -----------------------------
# GROWW CONNECTOR (SAFE OPTIONAL)
# -----------------------------
def init_groww_client():
    """
    Flexible initialization because SDK versions may differ.
    Expects Streamlit secrets:
    GROWW_ACCESS_TOKEN OR GROWW_API_KEY + GROWW_API_SECRET
    """
    try:
        from growwapi import GrowwAPI
    except Exception as e:
        return None, f"growwapi package not installed: {e}"

    access_token = st.secrets.get("GROWW_ACCESS_TOKEN", None) if hasattr(st, "secrets") else None
    api_key = st.secrets.get("GROWW_API_KEY", None) if hasattr(st, "secrets") else None
    api_secret = st.secrets.get("GROWW_API_SECRET", None) if hasattr(st, "secrets") else None

    try:
        if access_token:
            try:
                client = GrowwAPI(access_token)
                return client, None
            except Exception:
                try:
                    client = GrowwAPI(access_token=access_token)
                    return client, None
                except Exception as e:
                    return None, f"Access token init failed: {e}"

        if api_key and api_secret:
            try:
                client = GrowwAPI(api_key=api_key, api_secret=api_secret)
                return client, None
            except Exception:
                try:
                    client = GrowwAPI(api_key, api_secret)
                    return client, None
                except Exception as e:
                    return None, f"API key/secret init failed: {e}"

        return None, "No Groww secrets found. Add GROWW_ACCESS_TOKEN or GROWW_API_KEY + GROWW_API_SECRET in Streamlit Secrets."
    except Exception as e:
        return None, f"Groww init error: {e}"


def try_methods(client, method_names, *args, **kwargs):
    for name in method_names:
        fn = getattr(client, name, None)
        if callable(fn):
            try:
                return fn(*args, **kwargs), None, name
            except Exception as e:
                last_error = str(e)
                continue
    return None, locals().get("last_error", "No compatible method found"), None


def extract_list_from_response(resp):
    if resp is None:
        return []
    if isinstance(resp, list):
        return resp
    if isinstance(resp, dict):
        for key in ["data", "holdings", "positions", "items", "results"]:
            if key in resp and isinstance(resp[key], list):
                return resp[key]
    return []


def get_groww_holdings(client):
    resp, err, method = try_methods(
        client,
        [
            "get_holdings_for_user",
            "get_holdings",
            "holdings",
        ],
        timeout=5,
    )
    if resp is not None:
        return extract_list_from_response(resp), None, method
    return [], err, None


def get_groww_positions(client):
    # Try with and without segment argument due to SDK differences
    resp, err, method = try_methods(client, ["get_positions_for_user", "get_positions", "positions"])
    if resp is not None:
        return extract_list_from_response(resp), None, method
    return [], err, None


def extract_symbol_from_holding(item):
    candidates = [
        item.get("tradingSymbol"), item.get("trading_symbol"), item.get("symbol"), item.get("ticker"),
        item.get("nseSymbol"), item.get("exchangeSymbol"), item.get("instrumentSymbol")
    ] if isinstance(item, dict) else []
    for c in candidates:
        if c:
            return groww_to_yahoo_symbol(str(c))
    return None


def place_groww_order_safe(client, symbol, qty, transaction="BUY"):
    """
    SAFE MODE ONLY: tries common SDK patterns, but disabled by default in UI.
    """
    try:
        groww_symbol = yahoo_to_groww_symbol(symbol)
        order_type = "MARKET"
        product = "CNC"
        exchange = "NSE"
        segment = "CASH"

        # Common method name attempts
        methods = ["place_order", "create_order"]
        for m in methods:
            fn = getattr(client, m, None)
            if callable(fn):
                try:
                    return fn(
                        trading_symbol=groww_symbol,
                        quantity=int(qty),
                        exchange=exchange,
                        segment=segment,
                        product=product,
                        order_type=order_type,
                        transaction_type=transaction,
                    ), None
                except Exception:
                    try:
                        return fn(groww_symbol, int(qty), transaction), None
                    except Exception as e:
                        last_error = str(e)
                        continue
        return None, locals().get("last_error", "No compatible order method found")
    except Exception as e:
        return None, str(e)


# -----------------------------
# CHART
# -----------------------------
def create_chart(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"
    ))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], mode="lines", name="EMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], mode="lines", name="SMA50"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA200"], mode="lines", name="SMA200"))
    fig.update_layout(title=f"{ticker} Price Chart", xaxis_rangeslider_visible=False, height=600)
    return fig


# -----------------------------
# UI
# -----------------------------
st.title("📊 STOCK ANALYSIS PRO APP V2 - GROWW CONNECT")
st.caption("Fundamental + Technical + Portfolio Analysis + Optional Groww Connect (Safe Mode)")

with st.sidebar:
    st.header("⚙️ Settings")
    ticker = st.text_input("Enter Stock Ticker", value="RELIANCE.NS").strip().upper()
    period = st.selectbox("Price History Period", ["6mo", "1y", "2y", "5y"], index=1)
    run = st.button("🚀 Analyze Stock", use_container_width=True)
    st.markdown("---")

    st.subheader("🔗 Groww Connect")
    use_groww = st.checkbox("Enable Groww Integration", value=False)
    analyze_holdings_btn = st.button("📦 Analyze My Holdings", use_container_width=True, disabled=not use_groww)
    show_positions_btn = st.button("📍 Show Positions", use_container_width=True, disabled=not use_groww)
    st.markdown("---")
    st.info("Use Indian tickers like RELIANCE.NS, TCS.NS, INFY.NS")

# -----------------------------
# MAIN STOCK ANALYSIS
# -----------------------------
if run:
    if not ticker:
        st.error("Please enter a valid stock ticker.")
        st.stop()

    with st.spinner("Running stock analysis..."):
        result = analyze_symbol(ticker, period)

    if result is None:
        st.error("No price data found. Please check ticker format (e.g. RELIANCE.NS).")
        st.stop()

    fdata = result["fdata"]
    tdata = result["tdata"]
    final_score = result["final_score"]
    verdict = result["verdict"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Price", format_num(fdata["current_price"]))
    c2.metric("Fundamental Score", f"{fdata['fundamental_score']}/100")
    c3.metric("Technical Score", f"{tdata['technical_score']}/100")
    c4.metric("Final Score", f"{final_score}/100")

    st.markdown(
        f"<div style='padding:12px;border-radius:12px;background:{verdict_color(verdict)};color:white;font-weight:700;text-align:center;'>FINAL VERDICT: {verdict}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1, 2])
    with left:
        st.subheader("🏢 Company Snapshot")
        snapshot = pd.DataFrame({
            "Field": ["Company", "Sector", "Industry", "Market Cap", "52W High", "52W Low", "PE", "PB"],
            "Value": [
                fdata["company"], fdata["sector"], fdata["industry"], format_num(fdata["market_cap"]),
                format_num(fdata["52w_high"]), format_num(fdata["52w_low"]), format_num(fdata["pe"]), format_num(fdata["pb"])
            ]
        })
        st.dataframe(snapshot, use_container_width=True, hide_index=True)

    with right:
        st.subheader("📈 Technical Price Chart")
        st.plotly_chart(create_chart(tdata["df"], ticker), use_container_width=True)

    st.subheader("📘 Fundamental Analysis")
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        st.dataframe(pd.DataFrame({
            "Metric": ["Sales Growth 3Y", "Profit Growth 3Y", "Quarterly Sales YoY", "Quarterly Profit YoY", "ROE", "Debt to Equity", "OPM", "NPM"],
            "Value": [
                format_pct(fdata["sales_growth_3y"]), format_pct(fdata["profit_growth_3y"]),
                format_pct(fdata["quarterly_sales_yoy"]), format_pct(fdata["quarterly_profit_yoy"]),
                format_pct(fdata["roe"]), format_num(fdata["debt_to_equity"]), format_pct(fdata["opm"]), format_pct(fdata["npm"])
            ]
        }), use_container_width=True, hide_index=True)

    with fcol2:
        st.dataframe(pd.DataFrame({
            "Metric": ["Operating Cash Flow", "Free Cash Flow", "CFO vs PAT", "Promoter Holding", "Pledge", "Fundamental Score"],
            "Value": [
                format_num(fdata["cfo"]), format_num(fdata["fcf"]), format_pct(fdata["cfo_vs_pat"]),
                "N/A (Yahoo limitation)", "N/A (Yahoo limitation)", f"{fdata['fundamental_score']}/100"
            ]
        }), use_container_width=True, hide_index=True)

    st.subheader("📙 Technical Analysis")
    tcol1, tcol2 = st.columns(2)
    with tcol1:
        st.dataframe(pd.DataFrame({
            "Metric": ["Trend", "EMA20", "SMA50", "SMA200", "RSI(14)", "MACD", "MACD Signal"],
            "Value": [
                tdata["trend"], format_num(tdata["ema20"]), format_num(tdata["sma50"]), format_num(tdata["sma200"]),
                format_num(tdata["rsi"]), format_num(tdata["macd"]), format_num(tdata["macd_signal"])
            ]
        }), use_container_width=True, hide_index=True)

    with tcol2:
        st.dataframe(pd.DataFrame({
            "Metric": ["Support", "Resistance", "90D Stock Return", "90D Nifty Return", "Entry Zone", "Stop Loss", "Target 1", "Target 2", "Risk/Reward", "Technical Score"],
            "Value": [
                format_num(tdata["support"]), format_num(tdata["resistance"]), format_pct(tdata["stock_ret_90d"]), format_pct(tdata["nifty_ret_90d"]),
                tdata["entry_zone"], format_num(tdata["stop_loss"]), format_num(tdata["target1"]), format_num(tdata["target2"]), f"{tdata['rr']:.2f}", f"{tdata['technical_score']}/100"
            ]
        }), use_container_width=True, hide_index=True)

    st.subheader("🧠 Final Decision Engine")
    decision_df = pd.DataFrame({
        "Field": ["Fundamental Weight", "Technical Weight", "Combined Score", "Final Verdict", "Suggested Horizon", "Risk Note"],
        "Value": [
            "60%", "40%", f"{final_score}/100", verdict,
            "Long-term / Positional" if final_score >= 65 else "Watchlist / Avoid",
            "Model-based analysis only. Validate with latest quarterly results and management commentary."
        ]
    })
    st.dataframe(decision_df, use_container_width=True, hide_index=True)

    st.subheader("📋 Client Summary (Copy Ready)")
    summary = f"""
STOCK ANALYSIS REPORT - {ticker}

Company: {fdata['company']}
Sector: {fdata['sector']}
Current Price: {format_num(fdata['current_price'])}

Fundamental Score: {fdata['fundamental_score']}/100
Technical Score: {tdata['technical_score']}/100
Final Combined Score: {final_score}/100
Final Verdict: {verdict}

Entry Zone: {tdata['entry_zone']}
Stop Loss: {format_num(tdata['stop_loss'])}
Target 1: {format_num(tdata['target1'])}
Target 2: {format_num(tdata['target2'])}

Note: Model-driven screening tool. Validate with latest results before investment.
"""
    st.text_area("Copy this summary", summary, height=280)

# -----------------------------
# GROWW SECTION
# -----------------------------
if use_groww:
    st.markdown("---")
    st.header("🔗 Groww Integration Panel")

    client, groww_error = init_groww_client()

    if client is None:
        st.error(f"Groww connection failed: {groww_error}")
        st.info("Add Streamlit Secrets: GROWW_ACCESS_TOKEN OR GROWW_API_KEY + GROWW_API_SECRET")
    else:
        st.success("Groww connected successfully (Safe Mode)")

        st.subheader("🔐 Streamlit Secrets Format")
        st.code(
            'GROWW_API_KEY = "your_api_key"\nGROWW_API_SECRET = "your_api_secret"\n# OR\nGROWW_ACCESS_TOKEN = "your_access_token"',
            language="toml",
        )

        if analyze_holdings_btn:
            with st.spinner("Fetching Groww holdings and analyzing portfolio..."):
                holdings, err, method = get_groww_holdings(client)

            if err and not holdings:
                st.error(f"Unable to fetch holdings: {err}")
            else:
                st.success(f"Holdings fetched successfully via method: {method}")
                if holdings:
                    st.subheader("📦 Raw Groww Holdings")
                    st.dataframe(pd.DataFrame(holdings), use_container_width=True)

                    st.subheader("📊 Analyzed Portfolio Holdings")
                    rows = []
                    progress = st.progress(0)

                    for idx, h in enumerate(holdings):
                        yahoo_symbol = extract_symbol_from_holding(h)
                        if yahoo_symbol:
                            result = analyze_symbol(yahoo_symbol, "1y")
                            if result:
                                rows.append({
                                    "Ticker": yahoo_symbol,
                                    "Fundamental Score": result["fdata"]["fundamental_score"],
                                    "Technical Score": result["tdata"]["technical_score"],
                                    "Final Score": result["final_score"],
                                    "Verdict": result["verdict"],
                                })
                        progress.progress((idx + 1) / max(len(holdings), 1))

                    if rows:
                        df_port = pd.DataFrame(rows).sort_values("Final Score", ascending=False)
                        st.dataframe(df_port, use_container_width=True, hide_index=True)

                        strong = df_port[df_port["Final Score"] >= 75]
                        weak = df_port[df_port["Final Score"] < 65]

                        c1, c2, c3 = st.columns(3)
                        c1.metric("Total Holdings Analyzed", len(df_port))
                        c2.metric("Strong Holdings (75+)", len(strong))
                        c3.metric("Weak / Review (<65)", len(weak))

                        st.subheader("📝 Portfolio Advisory Summary")
                        st.text_area(
                            "Copy portfolio summary",
                            f"Portfolio analyzed: {len(df_port)} holdings\nStrong holdings (75+): {len(strong)}\nWeak/review holdings (<65): {len(weak)}\nTop stock: {df_port.iloc[0]['Ticker']} ({df_port.iloc[0]['Final Score']}/100)\nConsider adding on dips for strong holdings and review weak holdings with poor technical structure.",
                            height=160,
                        )
                    else:
                        st.warning("Holdings fetched, but symbol mapping failed for analysis. Check raw holdings columns and adjust mapping if needed.")
                else:
                    st.info("No holdings found in response.")

        if show_positions_btn:
            with st.spinner("Fetching Groww positions..."):
                positions, err, method = get_groww_positions(client)

            if err and not positions:
                st.error(f"Unable to fetch positions: {err}")
            else:
                st.success(f"Positions fetched successfully via method: {method}")
                if positions:
                    st.dataframe(pd.DataFrame(positions), use_container_width=True)
                else:
                    st.info("No open positions found.")

        # SAFE MANUAL ORDER SECTION
        st.markdown("---")
        st.subheader("🛒 Safe Manual Order Console (Disabled by Default)")
        st.warning("IMPORTANT: Streamlit Cloud is NOT ideal for live order execution due to static IP / production controls. Use only after testing on a proper backend.")

        enable_orders = st.checkbox("I understand the risk and want to enable manual order section", value=False)

        if enable_orders:
            order_symbol = st.text_input("Order Symbol (Yahoo format)", value="RELIANCE.NS").strip().upper()
            qty = st.number_input("Quantity", min_value=1, value=1, step=1)
            transaction = st.selectbox("Transaction", ["BUY", "SELL"])
            confirm_order = st.checkbox("I confirm I want to place a real order")

            if st.button("🚨 Place Real Order"):
                if not confirm_order:
                    st.error("Please tick confirmation checkbox first.")
                else:
                    # Safety block: score threshold check
                    result = analyze_symbol(order_symbol, "1y")
                    if result and result["final_score"] < 65:
                        st.error(f"Order blocked: stock score is below threshold ({result['final_score']}/100).")
                    else:
                        with st.spinner("Attempting order placement..."):
                            resp, err = place_groww_order_safe(client, order_symbol, qty, transaction)
                        if err:
                            st.error(f"Order failed / blocked by SDK mismatch: {err}")
                        else:
                            st.success("Order request sent successfully")
                            st.write(resp)

else:
    st.markdown("""
### ✅ What this V2 app does
- Fundamental analysis (Sales, Profit, ROE, Debt, Margins, Cash Flow)
- Technical analysis (Trend, EMA20, SMA50, SMA200, RSI, MACD, Support/Resistance)
- Combined scoring model (60% Fundamental + 40% Technical)
- Final verdict: Strong Buy / Buy on Dips / Watchlist / Avoid
- Optional Groww integration:
  - Fetch holdings
  - Analyze all holdings
  - Fetch positions
  - Safe manual order section (disabled by default)

### 🔐 Required Streamlit Secrets for Groww
```toml
GROWW_API_KEY = "your_api_key"
GROWW_API_SECRET = "your_api_secret"
# OR
GROWW_ACCESS_TOKEN = "your_access_token"
```

### 📦 requirements.txt add this line
```txt
growwapi
```

### ⚠️ Important
- Groww SDK method names can vary by version, so this app includes flexible method detection.
- For real order placement, prefer a backend with static IP (VPS/Render/Railway) instead of only Streamlit Cloud.
- For first phase, use Groww mainly for holdings + positions + portfolio analysis.
""")

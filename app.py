import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import importlib.util

st.set_page_config(page_title="Stock Analysis Pro V3.1 Streamlit Safe", layout="wide")

# =========================================================
# FINAL V3.1 STREAMLIT SAFE GROWW PATCH
# Single-file Streamlit App
# - Crash-proof startup on Streamlit Cloud
# - NO hard dependency on growwapi at startup
# - Groww integration loads only when package exists + user enables it
# - App remains live even if growwapi fails
# =========================================================

# -----------------------------
# SAFE HELPERS
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
# SAFE PACKAGE CHECK (NO CRASH)
# -----------------------------
def is_growwapi_available():
    try:
        return importlib.util.find_spec("growwapi") is not None
    except Exception:
        return False


# -----------------------------
# YFINANCE SAFE DATA
# -----------------------------
@st.cache_data(ttl=900, show_spinner=False)
def fetch_history_yf(ticker, period):
    attempts = [
        {"auto_adjust": True, "repair": True},
        {"auto_adjust": False, "repair": True},
        {"auto_adjust": True, "repair": False},
    ]
    for a in attempts:
        try:
            df = yf.download(ticker, period=period, interval="1d", progress=False, threads=False, **a)
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
# GROWW SAFE LAZY INIT
# -----------------------------
def init_groww_client_safe(enable_groww=False):
    """
    NEVER crashes app.
    Imports growwapi only when explicitly needed and available.
    """
    if not enable_groww:
        return None, None, "Groww disabled by user"

    if not is_growwapi_available():
        return None, None, "growwapi package not installed or failed in Streamlit build"

    try:
        from growwapi import GrowwAPI
    except Exception as e:
        return None, None, f"growwapi import failed: {e}"

    try:
        api_key = st.secrets.get("GROWW_API_KEY", None)
        api_secret = st.secrets.get("GROWW_API_SECRET", None)
        access_token = st.secrets.get("GROWW_ACCESS_TOKEN", None)
    except Exception as e:
        return None, None, f"Streamlit Secrets read failed: {e}"

    if not access_token and api_key and api_secret:
        try:
            access_token = GrowwAPI.get_access_token(api_key=api_key, secret=api_secret)
        except Exception as e:
            return None, None, f"Access token generation failed: {e}"

    if not access_token:
        return None, None, "Add GROWW_API_KEY + GROWW_API_SECRET OR GROWW_ACCESS_TOKEN in Streamlit Secrets"

    try:
        try:
            client = GrowwAPI(access_token)
        except Exception:
            client = GrowwAPI(access_token=access_token)
        return client, access_token, None
    except Exception as e:
        return None, None, f"Groww init failed: {e}"


def try_methods(client, method_names, *args, **kwargs):
    last_error = None
    for name in method_names:
        fn = getattr(client, name, None)
        if callable(fn):
            try:
                return fn(*args, **kwargs), None, name
            except Exception as e:
                last_error = str(e)
                continue
    return None, last_error or "No compatible method found", None


def extract_list_from_response(resp):
    if resp is None:
        return []
    if isinstance(resp, list):
        return resp
    if isinstance(resp, dict):
        for key in ["data", "holdings", "positions", "items", "results", "candles"]:
            if key in resp and isinstance(resp[key], list):
                return resp[key]
    return []


def get_groww_holdings(client):
    resp, err, method = try_methods(client, ["get_holdings_for_user", "get_holdings", "holdings"], timeout=5)
    if resp is not None:
        return extract_list_from_response(resp), None, method
    return [], err, None


def get_groww_positions(client):
    resp, err, method = try_methods(client, ["get_positions_for_user", "get_positions", "positions"])
    if resp is not None:
        return extract_list_from_response(resp), None, method
    return [], err, None


def extract_symbol_from_holding(item):
    if not isinstance(item, dict):
        return None
    candidates = [
        item.get("tradingSymbol"), item.get("trading_symbol"), item.get("symbol"), item.get("ticker"),
        item.get("nseSymbol"), item.get("exchangeSymbol"), item.get("instrumentSymbol")
    ]
    for c in candidates:
        if c:
            return groww_to_yahoo_symbol(str(c))
    return None


def period_to_days(period):
    mapping = {"6mo": 180, "1y": 365, "2y": 730, "5y": 1825}
    return mapping.get(period, 365)


def parse_candle_rows(rows):
    parsed = []
    for r in rows:
        try:
            if isinstance(r, (list, tuple)) and len(r) >= 6:
                ts = r[0]
                o, h, l, c, v = r[1], r[2], r[3], r[4], r[5]
            elif isinstance(r, dict):
                ts = r.get("timestamp") or r.get("time") or r.get("date")
                o = r.get("open")
                h = r.get("high")
                l = r.get("low")
                c = r.get("close")
                v = r.get("volume", 0)
            else:
                continue

            ts_val = pd.to_datetime(ts, unit="s", errors="coerce") if isinstance(ts, (int, float)) else pd.to_datetime(ts, errors="coerce")
            if pd.isna(ts_val):
                continue

            parsed.append([ts_val, safe_num(o), safe_num(h), safe_num(l), safe_num(c), safe_num(v, 0)])
        except Exception:
            continue

    if not parsed:
        return pd.DataFrame()

    df = pd.DataFrame(parsed, columns=["Date", "Open", "High", "Low", "Close", "Volume"]).set_index("Date")
    return normalize_history(df)


def fetch_history_groww(client, ticker, period):
    if client is None:
        return pd.DataFrame(), "Groww client unavailable", None

    symbol = yahoo_to_groww_symbol(ticker)
    days = period_to_days(period)
    from_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    to_date = datetime.utcnow().strftime("%Y-%m-%d")

    method_candidates = [
        "get_historical_candle_data",
        "get_historical_data",
        "get_historical_candles",
        "historical_data",
        "get_candles",
    ]

    for m in method_candidates:
        fn = getattr(client, m, None)
        if callable(fn):
            attempts = [
                {"exchange": "NSE", "segment": "CASH", "trading_symbol": symbol, "interval": "DAY", "from_date": from_date, "to_date": to_date},
                {"exchange": "NSE", "segment": "CASH", "trading_symbol": symbol, "interval": "1d", "from_date": from_date, "to_date": to_date},
                {"trading_symbol": symbol, "interval": "DAY", "from_date": from_date, "to_date": to_date},
                {"symbol": symbol, "interval": "DAY", "from_date": from_date, "to_date": to_date},
            ]
            for kwargs in attempts:
                try:
                    resp = fn(**kwargs)
                    if isinstance(resp, dict):
                        rows = resp.get("candles") or resp.get("data") or resp.get("results") or []
                    elif isinstance(resp, list):
                        rows = resp
                    else:
                        rows = []
                    df = parse_candle_rows(rows)
                    if not df.empty:
                        return df, None, m
                except Exception:
                    continue

    return pd.DataFrame(), "No compatible Groww historical candle method worked", None


# -----------------------------
# FUNDAMENTAL MASTER + FALLBACK
# -----------------------------
def normalize_master_columns(df):
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def load_fundamental_master(uploaded_file):
    if uploaded_file is None:
        return None, "No CSV uploaded"
    try:
        df = pd.read_csv(uploaded_file)
        df = normalize_master_columns(df)
        if "symbol" not in df.columns:
            return None, "CSV must contain a 'symbol' column"
        df["symbol"] = df["symbol"].astype(str).str.strip().str.upper()
        return df, None
    except Exception as e:
        return None, str(e)


def get_master_row(master_df, ticker):
    if master_df is None or master_df.empty:
        return None
    symbol = yahoo_to_groww_symbol(ticker).upper()
    rows = master_df[master_df["symbol"] == symbol]
    if rows.empty:
        return None
    return rows.iloc[0].to_dict()


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


def fundamental_from_yf(ticker_symbol):
    ticker_obj = safe_ticker(ticker_symbol)
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
        "roe": roe * 100 if not pd.isna(roe) else np.nan,
        "roce": np.nan,
        "debt_to_equity": debt_to_equity,
        "opm": operating_margin * 100 if not pd.isna(operating_margin) else np.nan,
        "npm": profit_margin * 100 if not pd.isna(profit_margin) else np.nan,
        "cfo": cfo,
        "fcf": fcf,
        "cfo_vs_pat": cfo_vs_pat,
        "pe": pe,
        "pb": pb,
        "promoter_holding": np.nan,
        "pledge": np.nan,
        "source": "yfinance fallback",
    }


def build_fundamental_data(ticker, master_df=None):
    row = get_master_row(master_df, ticker) if master_df is not None else None
    if row:
        data = {
            "company": row.get("company", ticker),
            "sector": row.get("sector", "N/A"),
            "industry": row.get("industry", "N/A"),
            "market_cap": safe_num(row.get("market_cap")),
            "current_price": safe_num(row.get("current_price")),
            "52w_high": safe_num(row.get("52w_high")),
            "52w_low": safe_num(row.get("52w_low")),
            "sales_growth_3y": safe_num(row.get("sales_growth_3y")),
            "profit_growth_3y": safe_num(row.get("profit_growth_3y")),
            "quarterly_sales_yoy": safe_num(row.get("quarterly_sales_yoy")),
            "quarterly_profit_yoy": safe_num(row.get("quarterly_profit_yoy")),
            "roe": safe_num(row.get("roe")),
            "roce": safe_num(row.get("roce")),
            "debt_to_equity": safe_num(row.get("debt_to_equity")),
            "opm": safe_num(row.get("opm")),
            "npm": safe_num(row.get("npm")),
            "cfo": safe_num(row.get("cfo")),
            "fcf": safe_num(row.get("fcf")),
            "cfo_vs_pat": safe_num(row.get("cfo_vs_pat")),
            "pe": safe_num(row.get("pe")),
            "pb": safe_num(row.get("pb")),
            "promoter_holding": safe_num(row.get("promoter_holding")),
            "pledge": safe_num(row.get("pledge")),
            "source": "fundamental master CSV",
        }
    else:
        data = fundamental_from_yf(ticker)

    score = 0
    score += score_range(data.get("sales_growth_3y"), [(20, 12), (15, 10), (10, 8), (5, 4)])
    score += score_range(data.get("profit_growth_3y"), [(20, 12), (15, 10), (10, 8), (5, 4)])
    score += score_range(data.get("quarterly_profit_yoy"), [(20, 8), (10, 6), (5, 4), (0, 2)])
    score += score_range(data.get("roe"), [(20, 12), (15, 10), (10, 7), (5, 4)])
    score += score_range(data.get("roce"), [(20, 8), (15, 6), (10, 4), (5, 2)])

    dte = data.get("debt_to_equity")
    if not pd.isna(dte):
        if dte <= 0.5:
            score += 10
        elif dte <= 1.0:
            score += 7
        elif dte <= 2.0:
            score += 4
    else:
        score += 3

    score += score_range(data.get("opm"), [(20, 8), (15, 6), (10, 4), (5, 2)])
    score += score_range(data.get("npm"), [(15, 6), (10, 4), (5, 2)])

    cfo_pat = data.get("cfo_vs_pat")
    if not pd.isna(cfo_pat):
        if cfo_pat >= 100:
            score += 8
        elif cfo_pat >= 80:
            score += 6
        elif cfo_pat >= 60:
            score += 3
    else:
        score += 2

    promoter = data.get("promoter_holding")
    if not pd.isna(promoter):
        if promoter >= 50:
            score += 5
        elif promoter >= 35:
            score += 3
    else:
        score += 2

    pledge = data.get("pledge")
    if not pd.isna(pledge):
        if pledge == 0:
            score += 5
        elif pledge <= 5:
            score += 3
    else:
        score += 2

    pe = data.get("pe")
    if not pd.isna(pe):
        if pe <= 20:
            score += 6
        elif pe <= 35:
            score += 4
        elif pe <= 50:
            score += 2
    else:
        score += 2

    pb = data.get("pb")
    if not pd.isna(pb):
        if pb <= 3:
            score += 4
        elif pb <= 6:
            score += 2
    else:
        score += 1

    data["fundamental_score"] = min(score, 100)
    return data


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

    technical_score = min(trend_score + ma_score + structure_score + volume_score + rsi_score + macd_score + rs_score + risk_reward_score, 100)

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
# ANALYSIS ENGINE
# -----------------------------
def fetch_price_history(client, ticker, period, prefer_groww=True):
    if prefer_groww and client is not None:
        gdf, err, method = fetch_history_groww(client, ticker, period)
        if not gdf.empty:
            return gdf, f"Groww ({method})"
    ydf = fetch_history_yf(ticker, period)
    if not ydf.empty:
        return ydf, "yfinance fallback"
    return pd.DataFrame(), "No data source"


def analyze_symbol(ticker, period="1y", master_df=None, groww_client=None, prefer_groww=True):
    hist, price_source = fetch_price_history(groww_client, ticker, period, prefer_groww=prefer_groww)
    if hist.empty:
        return None

    fdata = build_fundamental_data(ticker, master_df=master_df)
    tdata = technical_analysis(hist)

    if fdata.get("current_price") in [None, ""] or pd.isna(safe_num(fdata.get("current_price"))):
        fdata["current_price"] = safe_num(hist["Close"].iloc[-1])

    final_score = round((fdata["fundamental_score"] * 0.60) + (tdata["technical_score"] * 0.40), 2)
    verdict = final_rating(final_score)

    return {"fdata": fdata, "tdata": tdata, "final_score": final_score, "verdict": verdict, "price_source": price_source}


def place_groww_order_safe(client, symbol, qty, transaction="BUY"):
    if client is None:
        return None, "Groww client unavailable"
    try:
        groww_symbol = yahoo_to_groww_symbol(symbol)
        for m in ["place_order", "create_order"]:
            fn = getattr(client, m, None)
            if callable(fn):
                try:
                    return fn(
                        trading_symbol=groww_symbol,
                        quantity=int(qty),
                        exchange="NSE",
                        segment="CASH",
                        product="CNC",
                        order_type="MARKET",
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


def create_chart(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], mode="lines", name="EMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], mode="lines", name="SMA50"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA200"], mode="lines", name="SMA200"))
    fig.update_layout(title=f"{ticker} Price Chart", xaxis_rangeslider_visible=False, height=600)
    return fig


# -----------------------------
# UI
# -----------------------------
st.title("📊 STOCK ANALYSIS PRO APP V3.1 - STREAMLIT SAFE GROWW PATCH")
st.caption("Crash-proof Streamlit version | Groww optional | yfinance fallback always live")

with st.sidebar:
    st.header("⚙️ Settings")
    ticker = st.text_input("Enter Stock Ticker", value="RELIANCE.NS").strip().upper()
    period = st.selectbox("Price History Period", ["6mo", "1y", "2y", "5y"], index=1)

    st.subheader("📁 Fundamental Master CSV")
    uploaded_file = st.file_uploader("Upload CSV (optional)", type=["csv"])

    st.subheader("🔗 Groww Connection")
    prefer_groww = st.checkbox("Prefer Groww for Technical Data", value=False)
    use_groww_features = st.checkbox("Enable Groww Holdings / Positions / Orders", value=False)

    run = st.button("🚀 Analyze Stock", use_container_width=True)
    analyze_holdings_btn = st.button("📦 Analyze My Groww Holdings", use_container_width=True, disabled=not use_groww_features)
    show_positions_btn = st.button("📍 Show Groww Positions", use_container_width=True, disabled=not use_groww_features)

    st.markdown("---")
    st.info("Safe default: Groww OFF. Turn it ON only after app is stable.")

master_df, master_err = load_fundamental_master(uploaded_file) if uploaded_file is not None else (None, None)

# SAFE startup status only (no Groww init here)
if is_growwapi_available():
    st.success("✅ growwapi package detected")
else:
    st.info("ℹ️ growwapi not available or build failed. App will still run with yfinance + CSV mode.")

if master_df is not None:
    st.success(f"✅ Fundamental master loaded: {len(master_df)} rows")
elif uploaded_file is not None and master_err:
    st.error(f"Fundamental CSV error: {master_err}")
else:
    st.info("No fundamental CSV uploaded. App will use yfinance fallback for fundamentals.")

# -----------------------------
# SINGLE STOCK ANALYSIS (ALWAYS WORKS WITHOUT GROWW)
# -----------------------------
if run:
    groww_client = None
    groww_status = "Disabled"

    if prefer_groww:
        groww_client, _, groww_err = init_groww_client_safe(enable_groww=True)
        if groww_client is not None:
            groww_status = "Connected"
        else:
            groww_status = f"Fallback to yfinance ({groww_err})"

    with st.spinner("Running stock analysis..."):
        result = analyze_symbol(ticker, period, master_df=master_df, groww_client=groww_client, prefer_groww=prefer_groww)

    if result is None:
        st.error("No price data found. Please check ticker format like RELIANCE.NS")
        st.stop()

    fdata = result["fdata"]
    tdata = result["tdata"]
    final_score = result["final_score"]
    verdict = result["verdict"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Current Price", format_num(fdata["current_price"]))
    c2.metric("Fundamental Score", f"{fdata['fundamental_score']}/100")
    c3.metric("Technical Score", f"{tdata['technical_score']}/100")
    c4.metric("Final Score", f"{final_score}/100")
    c5.metric("Groww Status", groww_status)

    st.markdown(f"<div style='padding:12px;border-radius:12px;background:{verdict_color(verdict)};color:white;font-weight:700;text-align:center;'>FINAL VERDICT: {verdict}</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1, 2])
    with left:
        st.subheader("🏢 Company Snapshot")
        snapshot = pd.DataFrame({
            "Field": ["Company", "Sector", "Industry", "Market Cap", "52W High", "52W Low", "PE", "PB", "Fundamental Source", "Price Source"],
            "Value": [
                fdata.get("company", ticker), fdata.get("sector", "N/A"), fdata.get("industry", "N/A"), format_num(fdata.get("market_cap")),
                format_num(fdata.get("52w_high")), format_num(fdata.get("52w_low")), format_num(fdata.get("pe")), format_num(fdata.get("pb")),
                fdata.get("source", "N/A"), result["price_source"]
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
            "Metric": ["Sales Growth 3Y", "Profit Growth 3Y", "Quarterly Sales YoY", "Quarterly Profit YoY", "ROE", "ROCE", "Debt to Equity", "OPM", "NPM"],
            "Value": [
                format_pct(fdata.get("sales_growth_3y")), format_pct(fdata.get("profit_growth_3y")), format_pct(fdata.get("quarterly_sales_yoy")),
                format_pct(fdata.get("quarterly_profit_yoy")), format_pct(fdata.get("roe")), format_pct(fdata.get("roce")),
                format_num(fdata.get("debt_to_equity")), format_pct(fdata.get("opm")), format_pct(fdata.get("npm"))
            ]
        }), use_container_width=True, hide_index=True)

    with fcol2:
        st.dataframe(pd.DataFrame({
            "Metric": ["Operating Cash Flow", "Free Cash Flow", "CFO vs PAT", "Promoter Holding", "Pledge", "Fundamental Score"],
            "Value": [
                format_num(fdata.get("cfo")), format_num(fdata.get("fcf")), format_pct(fdata.get("cfo_vs_pat")),
                format_pct(fdata.get("promoter_holding")), format_pct(fdata.get("pledge")), f"{fdata['fundamental_score']}/100"
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

    st.subheader("📋 Client Summary")
    summary = f"""
STOCK ANALYSIS REPORT - {ticker}
Company: {fdata.get('company', ticker)}
Fundamental Source: {fdata.get('source', 'N/A')}
Price Source: {result['price_source']}
Fundamental Score: {fdata['fundamental_score']}/100
Technical Score: {tdata['technical_score']}/100
Final Score: {final_score}/100
Final Verdict: {verdict}
Entry Zone: {tdata['entry_zone']}
Stop Loss: {format_num(tdata['stop_loss'])}
Target 1: {format_num(tdata['target1'])}
Target 2: {format_num(tdata['target2'])}
"""
    st.text_area("Copy summary", summary, height=220)

# -----------------------------
# GROWW PANEL (ONLY WHEN ENABLED)
# -----------------------------
if use_groww_features:
    st.markdown("---")
    st.header("🔗 Groww Portfolio + Execution Panel (Safe Lazy Load)")

    client, _, groww_error = init_groww_client_safe(enable_groww=True)

    if client is None:
        st.error(f"Groww not connected: {groww_error}")
        st.code('GROWW_API_KEY = "your_api_key"\nGROWW_API_SECRET = "your_api_secret"\n# OR\nGROWW_ACCESS_TOKEN = "your_access_token"', language="toml")
        st.info("App remains fully usable without Groww. Use stock analysis in yfinance + CSV mode.")
    else:
        st.success("✅ Groww connected successfully")

        if analyze_holdings_btn:
            with st.spinner("Fetching Groww holdings and analyzing..."):
                holdings, err, method = get_groww_holdings(client)
            if err and not holdings:
                st.error(f"Unable to fetch holdings: {err}")
            else:
                st.success(f"Holdings fetched via: {method}")
                if holdings:
                    st.dataframe(pd.DataFrame(holdings), use_container_width=True)
                    rows = []
                    progress = st.progress(0)
                    for idx, h in enumerate(holdings):
                        sym = extract_symbol_from_holding(h)
                        if sym:
                            r = analyze_symbol(sym, "1y", master_df=master_df, groww_client=client, prefer_groww=prefer_groww)
                            if r:
                                rows.append({
                                    "Ticker": sym,
                                    "Fundamental Score": r["fdata"]["fundamental_score"],
                                    "Technical Score": r["tdata"]["technical_score"],
                                    "Final Score": r["final_score"],
                                    "Verdict": r["verdict"],
                                })
                        progress.progress((idx + 1) / max(len(holdings), 1))
                    if rows:
                        df_port = pd.DataFrame(rows).sort_values("Final Score", ascending=False)
                        st.dataframe(df_port, use_container_width=True, hide_index=True)
                    else:
                        st.warning("Holdings fetched, but symbol mapping failed.")
                else:
                    st.info("No holdings found.")

        if show_positions_btn:
            with st.spinner("Fetching Groww positions..."):
                positions, err, method = get_groww_positions(client)
            if err and not positions:
                st.error(f"Unable to fetch positions: {err}")
            else:
                st.success(f"Positions fetched via: {method}")
                if positions:
                    st.dataframe(pd.DataFrame(positions), use_container_width=True)
                else:
                    st.info("No open positions found.")

        st.subheader("🛒 Safe Manual Order Console")
        enable_orders = st.checkbox("Enable manual order section", value=False)
        if enable_orders:
            order_symbol = st.text_input("Order Symbol", value="RELIANCE.NS").strip().upper()
            qty = st.number_input("Quantity", min_value=1, value=1, step=1)
            transaction = st.selectbox("Transaction", ["BUY", "SELL"])
            confirm_order = st.checkbox("I confirm real order placement")
            if st.button("🚨 Place Real Order"):
                if not confirm_order:
                    st.error("Please confirm first.")
                else:
                    r = analyze_symbol(order_symbol, "1y", master_df=master_df, groww_client=client, prefer_groww=prefer_groww)
                    if r and r["final_score"] < 65:
                        st.error(f"Order blocked: score below threshold ({r['final_score']}/100)")
                    else:
                        resp, err = place_groww_order_safe(client, order_symbol, qty, transaction)
                        if err:
                            st.error(f"Order failed: {err}")
                        else:
                            st.success("Order request sent")
                            st.write(resp)

# -----------------------------
# FOOTER HELP
# -----------------------------
st.markdown("---")
st.subheader("📌 Streamlit Safe Notes")
st.markdown("""
- V3.1 does **not** require Groww at startup.
- If `growwapi` is missing or broken, the app still works in **yfinance + CSV mode**.
- Turn ON Groww only after the base app is stable.
- For serious live execution, prefer **Groww Cloud / VPS / static IP backend**.
""")

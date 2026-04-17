import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import math
import time

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="NSE Stock Intelligence Pro MAX V9.1",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# UI / CSS
# =========================================================
st.markdown("""
<style>
    .main-title {
        font-size: 2.25rem;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .sub-title {
        font-size: 1rem;
        color: #cbd5e1;
        margin-bottom: 0.8rem;
    }
    .hero-box {
        padding: 1.2rem 1.4rem;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(15,23,42,0.96), rgba(14,116,144,0.20));
        border: 1px solid rgba(59,130,246,0.25);
        margin-bottom: 1rem;
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
    .good-box {
        padding: 1rem;
        border-radius: 12px;
        background: rgba(22,163,74,0.18);
        border: 1px solid rgba(22,163,74,0.35);
        color: #86efac;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }
    .warn-box {
        padding: 1rem;
        border-radius: 12px;
        background: rgba(245,158,11,0.15);
        border: 1px solid rgba(245,158,11,0.35);
        color: #fcd34d;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }
    .bad-box {
        padding: 1rem;
        border-radius: 12px;
        background: rgba(239,68,68,0.15);
        border: 1px solid rgba(239,68,68,0.35);
        color: #fca5a5;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }
    .info-box {
        padding: 0.85rem;
        border-radius: 12px;
        background: rgba(59,130,246,0.15);
        border: 1px solid rgba(59,130,246,0.35);
        color: #93c5fd;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# NIFTY 50
# =========================================================
NIFTY_50 = sorted([
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK",
    "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BEL", "BHARTIARTL",
    "BPCL", "BRITANNIA", "CIPLA", "COALINDIA", "DRREDDY",
    "EICHERMOT", "ETERNAL", "GRASIM", "HCLTECH", "HDFCBANK",
    "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK",
    "INDUSINDBK", "INFY", "ITC", "JIOFIN", "JSWSTEEL",
    "KOTAKBANK", "LT", "M&M", "MARUTI", "NESTLEIND",
    "NTPC", "ONGC", "POWERGRID", "RELIANCE", "SBILIFE",
    "SBIN", "SHRIRAMFIN", "SUNPHARMA", "TATACONSUM", "TATAMOTORS",
    "TATASTEEL", "TCS", "TECHM", "TITAN", "TRENT"
])

# =========================================================
# NIFTY NEXT 50 (Cloud-safe curated list)
# =========================================================
NIFTY_NEXT_50 = sorted([
    "ABB", "ADANIENSOL", "ADANIGREEN", "ADANIPOWER", "AMBUJACEM",
    "BAJAJHLDNG", "BANKBARODA", "BOSCHLTD", "CANBK", "CGPOWER",
    "CHOLAFIN", "DABUR", "DIVISLAB", "DLF", "DMART",
    "GAIL", "GODREJCP", "HAL", "HAVELLS", "ICICIGI",
    "ICICIPRULI", "INDIGO", "INDUSTOWER", "IOC", "IRCTC",
    "JINDALSTEL", "LODHA", "MOTHERSON", "NAUKRI", "NMDC",
    "PIDILITIND", "PNB", "RECLTD", "SAIL", "SHREECEM",
    "SIEMENS", "TORNTPHARM", "TVSMOTOR", "UNITDSPR", "VBL",
    "VEDL", "ZYDUSLIFE", "PFC", "HINDPETRO", "BHEL",
    "BERGEPAINT", "CONCOR", "MARICO", "TATAPOWER", "UPL"
])

NIFTY_100 = sorted(list(set(NIFTY_50 + NIFTY_NEXT_50)))

# =========================================================
# QUICK PICKS
# =========================================================
QUICK_LIST = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "SBIN", "TCS",
    "INFY", "ITC", "LT", "BHARTIARTL", "SUNPHARMA",
    "HAL", "DIVISLAB", "DMART", "SIEMENS", "VBL"
]

# =========================================================
# SECTOR PACKS
# =========================================================
SECTOR_PACKS = {
    "Nifty 50 Core": ["RELIANCE", "HDFCBANK", "ICICIBANK", "SBIN", "TCS", "INFY", "ITC", "LT"],
    "Nifty 50 Safe Scan": ["RELIANCE", "HDFCBANK", "ICICIBANK", "SBIN", "TCS", "INFY", "ITC", "LT"],
    "Nifty Next 50 Safe Scan": ["HAL", "DIVISLAB", "DMART", "SIEMENS", "VBL", "TVSMOTOR", "PIDILITIND", "DABUR"],
    "Nifty 100 Safe Scan": ["RELIANCE", "HDFCBANK", "ICICIBANK", "SBIN", "TCS", "INFY", "HAL", "DIVISLAB"],
    "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "INDUSINDBK", "BANKBARODA", "PNB", "CANBK"],
    "IT": ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM"],
    "Auto": ["MARUTI", "TATAMOTORS", "M&M", "EICHERMOT", "HEROMOTOCO", "BAJAJ-AUTO", "TVSMOTOR"],
    "Pharma": ["SUNPHARMA", "DRREDDY", "CIPLA", "APOLLOHOSP", "DIVISLAB", "TORNTPHARM", "ZYDUSLIFE"],
    "Energy": ["RELIANCE", "ONGC", "BPCL", "NTPC", "POWERGRID", "IOC", "HINDPETRO", "TATAPOWER"],
    "Consumer": ["ITC", "HINDUNILVR", "NESTLEIND", "BRITANNIA", "TATACONSUM", "TITAN", "DABUR", "MARICO", "VBL"]
}

UNIVERSE = sorted(list(set(NIFTY_100 + ["WIPRO"] + sum(SECTOR_PACKS.values(), []))))

# =========================================================
# FALLBACK MAP
# =========================================================
NSE_MASTER_FALLBACK = {
    "RELIANCE": {"sector": "Energy", "industry": "Oil & Gas / Conglomerate"},
    "TCS": {"sector": "Information Technology", "industry": "IT Services"},
    "INFY": {"sector": "Information Technology", "industry": "IT Services"},
    "HCLTECH": {"sector": "Information Technology", "industry": "IT Services"},
    "WIPRO": {"sector": "Information Technology", "industry": "IT Services"},
    "TECHM": {"sector": "Information Technology", "industry": "IT Services"},
    "HDFCBANK": {"sector": "Financial Services", "industry": "Private Sector Bank"},
    "ICICIBANK": {"sector": "Financial Services", "industry": "Private Sector Bank"},
    "SBIN": {"sector": "Financial Services", "industry": "Public Sector Bank"},
    "AXISBANK": {"sector": "Financial Services", "industry": "Private Sector Bank"},
    "KOTAKBANK": {"sector": "Financial Services", "industry": "Private Sector Bank"},
    "INDUSINDBK": {"sector": "Financial Services", "industry": "Private Sector Bank"},
    "BANKBARODA": {"sector": "Financial Services", "industry": "Public Sector Bank"},
    "PNB": {"sector": "Financial Services", "industry": "Public Sector Bank"},
    "CANBK": {"sector": "Financial Services", "industry": "Public Sector Bank"},
    "ITC": {"sector": "Consumer Defensive", "industry": "Diversified FMCG"},
    "LT": {"sector": "Industrials", "industry": "Engineering & Construction"},
    "BHARTIARTL": {"sector": "Communication Services", "industry": "Telecom"},
    "HINDUNILVR": {"sector": "Consumer Defensive", "industry": "FMCG"},
    "SUNPHARMA": {"sector": "Healthcare", "industry": "Pharmaceuticals"},
    "DRREDDY": {"sector": "Healthcare", "industry": "Pharmaceuticals"},
    "CIPLA": {"sector": "Healthcare", "industry": "Pharmaceuticals"},
    "APOLLOHOSP": {"sector": "Healthcare", "industry": "Hospitals"},
    "DIVISLAB": {"sector": "Healthcare", "industry": "Pharmaceuticals"},
    "TORNTPHARM": {"sector": "Healthcare", "industry": "Pharmaceuticals"},
    "ZYDUSLIFE": {"sector": "Healthcare", "industry": "Pharmaceuticals"},
    "MARUTI": {"sector": "Consumer Cyclical", "industry": "Automobiles"},
    "TATAMOTORS": {"sector": "Consumer Cyclical", "industry": "Automobiles"},
    "M&M": {"sector": "Consumer Cyclical", "industry": "Automobiles"},
    "EICHERMOT": {"sector": "Consumer Cyclical", "industry": "Automobiles"},
    "HEROMOTOCO": {"sector": "Consumer Cyclical", "industry": "Automobiles"},
    "BAJAJ-AUTO": {"sector": "Consumer Cyclical", "industry": "Automobiles"},
    "TVSMOTOR": {"sector": "Consumer Cyclical", "industry": "Automobiles"},
    "ASIANPAINT": {"sector": "Basic Materials", "industry": "Paints"},
    "ADANIENT": {"sector": "Industrials", "industry": "Trading / Infra"},
    "ADANIPORTS": {"sector": "Industrials", "industry": "Ports & Logistics"},
    "BAJFINANCE": {"sector": "Financial Services", "industry": "NBFC"},
    "BAJAJFINSV": {"sector": "Financial Services", "industry": "Financial Services"},
    "BEL": {"sector": "Industrials", "industry": "Defence Electronics"},
    "BPCL": {"sector": "Energy", "industry": "Oil & Gas"},
    "BRITANNIA": {"sector": "Consumer Defensive", "industry": "Food Products"},
    "COALINDIA": {"sector": "Energy", "industry": "Coal Mining"},
    "ETERNAL": {"sector": "Consumer Cyclical", "industry": "Internet Commerce"},
    "GRASIM": {"sector": "Basic Materials", "industry": "Diversified Materials"},
    "HDFCLIFE": {"sector": "Financial Services", "industry": "Life Insurance"},
    "HINDALCO": {"sector": "Basic Materials", "industry": "Metals"},
    "JIOFIN": {"sector": "Financial Services", "industry": "Financial Services"},
    "JSWSTEEL": {"sector": "Basic Materials", "industry": "Steel"},
    "NESTLEIND": {"sector": "Consumer Defensive", "industry": "FMCG"},
    "NTPC": {"sector": "Utilities", "industry": "Power Generation"},
    "ONGC": {"sector": "Energy", "industry": "Oil Exploration"},
    "POWERGRID": {"sector": "Utilities", "industry": "Power Transmission"},
    "SBILIFE": {"sector": "Financial Services", "industry": "Life Insurance"},
    "SHRIRAMFIN": {"sector": "Financial Services", "industry": "NBFC"},
    "TATACONSUM": {"sector": "Consumer Defensive", "industry": "FMCG"},
    "TATASTEEL": {"sector": "Basic Materials", "industry": "Steel"},
    "TITAN": {"sector": "Consumer Cyclical", "industry": "Retail / Jewellery"},
    "TRENT": {"sector": "Consumer Cyclical", "industry": "Retail"},
    "ABB": {"sector": "Industrials", "industry": "Electrical Equipment"},
    "ADANIENSOL": {"sector": "Utilities", "industry": "Renewable Energy"},
    "ADANIGREEN": {"sector": "Utilities", "industry": "Renewable Energy"},
    "ADANIPOWER": {"sector": "Utilities", "industry": "Power Generation"},
    "AMBUJACEM": {"sector": "Basic Materials", "industry": "Cement"},
    "BAJAJHLDNG": {"sector": "Financial Services", "industry": "Investment Holding"},
    "BOSCHLTD": {"sector": "Consumer Cyclical", "industry": "Auto Components"},
    "CGPOWER": {"sector": "Industrials", "industry": "Electrical Equipment"},
    "CHOLAFIN": {"sector": "Financial Services", "industry": "NBFC"},
    "DABUR": {"sector": "Consumer Defensive", "industry": "FMCG"},
    "DLF": {"sector": "Real Estate", "industry": "Real Estate Development"},
    "DMART": {"sector": "Consumer Defensive", "industry": "Retail"},
    "GAIL": {"sector": "Energy", "industry": "Gas Utility"},
    "GODREJCP": {"sector": "Consumer Defensive", "industry": "FMCG"},
    "HAL": {"sector": "Industrials", "industry": "Aerospace & Defence"},
    "HAVELLS": {"sector": "Industrials", "industry": "Electrical Equipment"},
    "ICICIGI": {"sector": "Financial Services", "industry": "General Insurance"},
    "ICICIPRULI": {"sector": "Financial Services", "industry": "Life Insurance"},
    "INDIGO": {"sector": "Industrials", "industry": "Airlines"},
    "INDUSTOWER": {"sector": "Communication Services", "industry": "Telecom Infra"},
    "IOC": {"sector": "Energy", "industry": "Oil & Gas"},
    "IRCTC": {"sector": "Industrials", "industry": "Railway Services"},
    "JINDALSTEL": {"sector": "Basic Materials", "industry": "Steel"},
    "LODHA": {"sector": "Real Estate", "industry": "Real Estate Development"},
    "MOTHERSON": {"sector": "Consumer Cyclical", "industry": "Auto Components"},
    "NAUKRI": {"sector": "Communication Services", "industry": "Internet Services"},
    "NMDC": {"sector": "Basic Materials", "industry": "Mining"},
    "PIDILITIND": {"sector": "Basic Materials", "industry": "Specialty Chemicals"},
    "RECLTD": {"sector": "Financial Services", "industry": "NBFC / PSU Lending"},
    "SAIL": {"sector": "Basic Materials", "industry": "Steel"},
    "SHREECEM": {"sector": "Basic Materials", "industry": "Cement"},
    "SIEMENS": {"sector": "Industrials", "industry": "Industrial Engineering"},
    "UNITDSPR": {"sector": "Consumer Defensive", "industry": "Beverages"},
    "VBL": {"sector": "Consumer Defensive", "industry": "Beverages"},
    "VEDL": {"sector": "Basic Materials", "industry": "Metals & Mining"},
    "PFC": {"sector": "Financial Services", "industry": "NBFC / PSU Lending"},
    "HINDPETRO": {"sector": "Energy", "industry": "Oil & Gas"},
    "BHEL": {"sector": "Industrials", "industry": "Capital Goods"},
    "BERGEPAINT": {"sector": "Basic Materials", "industry": "Paints"},
    "CONCOR": {"sector": "Industrials", "industry": "Logistics"},
    "MARICO": {"sector": "Consumer Defensive", "industry": "FMCG"},
    "TATAPOWER": {"sector": "Utilities", "industry": "Power"},
    "UPL": {"sector": "Basic Materials", "industry": "Agro Chemicals"}
}

# =========================================================
# SESSION STATE
# =========================================================
if "portfolio_db" not in st.session_state:
    st.session_state.portfolio_db = []

if "elite_watchlist" not in st.session_state:
    st.session_state.elite_watchlist = []

# =========================================================
# HELPERS
# =========================================================
def safe_num(x, default=np.nan):
    try:
        if x is None:
            return default
        if isinstance(x, str):
            if x.strip() == "" or x.strip().lower() == "nan":
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

def fmt_pct(x):
    return f"{x:.2f}%" if pd.notna(x) else "N/A"

def fmt_inr_cr(x):
    return f"₹ {x/1e7:,.2f} Cr" if pd.notna(x) else "N/A"

def get_nse_symbol(symbol):
    return f"{str(symbol).strip().upper().replace('.NS','')}.NS"

def clamp(v, lo=0, hi=100):
    try:
        return max(lo, min(hi, float(v)))
    except:
        return lo

def normalize_linear(x, low, high, invert=False):
    if pd.isna(x):
        return np.nan
    if high == low:
        return 50
    score = ((x - low) / (high - low)) * 100
    if invert:
        score = 100 - score
    return clamp(score)

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

def format_generic_value(v):
    if isinstance(v, (int, float, np.floating)):
        return f"{v:,.2f}" if pd.notna(v) else "N/A"
    if v is None:
        return "N/A"
    s = str(v).strip()
    if s == "" or s.lower() == "nan":
        return "N/A"
    return s

def safe_run_block(fn, label="module"):
    try:
        return fn()
    except Exception as e:
        st.error(f"{label} failed safely instead of crashing the whole app.")
        st.exception(e)
        return None

# =========================================================
# CACHE
# =========================================================
@st.cache_data(ttl=900, show_spinner=False)
def cached_fetch_serializable(symbol: str, period: str = "1y"):
    for attempt in range(2):
        try:
            ticker = yf.Ticker(get_nse_symbol(symbol))

            hist = ticker.history(period=period, auto_adjust=False)
            if hist is None or hist.empty:
                hist = ticker.history(period="6mo", auto_adjust=False)

            if hist is None or hist.empty:
                if attempt == 0:
                    time.sleep(1)
                    continue
                return None

            hist = hist.dropna(subset=["Open", "High", "Low", "Close"])
            if hist.empty:
                if attempt == 0:
                    time.sleep(1)
                    continue
                return None

            try:
                info = ticker.info
                if not isinstance(info, dict):
                    info = {}
            except:
                info = {}

            try:
                fi = ticker.fast_info
                fast_info = dict(fi) if fi is not None else {}
            except:
                fast_info = {}

            try:
                financials = ticker.financials
                if financials is None:
                    financials = pd.DataFrame()
                if not isinstance(financials, pd.DataFrame):
                    financials = pd.DataFrame(financials)
            except:
                financials = pd.DataFrame()

            try:
                balance_sheet = ticker.balance_sheet
                if balance_sheet is None:
                    balance_sheet = pd.DataFrame()
                if not isinstance(balance_sheet, pd.DataFrame):
                    balance_sheet = pd.DataFrame(balance_sheet)
            except:
                balance_sheet = pd.DataFrame()

            try:
                cashflow = ticker.cashflow
                if cashflow is None:
                    cashflow = pd.DataFrame()
                if not isinstance(cashflow, pd.DataFrame):
                    cashflow = pd.DataFrame(cashflow)
            except:
                cashflow = pd.DataFrame()

            try:
                q_financials = ticker.quarterly_financials
                if q_financials is None:
                    q_financials = pd.DataFrame()
                if not isinstance(q_financials, pd.DataFrame):
                    q_financials = pd.DataFrame(q_financials)
            except:
                q_financials = pd.DataFrame()

            return {
                "hist": hist,
                "info": info,
                "fast_info": fast_info,
                "financials": financials,
                "balance_sheet": balance_sheet,
                "cashflow": cashflow,
                "q_financials": q_financials
            }

        except:
            if attempt == 0:
                time.sleep(1)
                continue
            return None
    return None

def fetch_full_stock_data(symbol: str, period: str = "1y"):
    try:
        payload = cached_fetch_serializable(symbol, period)
        if payload is None:
            return None, None, None, None, None, None, None, "No price history found or Yahoo fetch failed."

        hist = payload.get("hist", pd.DataFrame())
        info = payload.get("info", {})
        fast_info = payload.get("fast_info", {})
        financials = payload.get("financials", pd.DataFrame())
        balance_sheet = payload.get("balance_sheet", pd.DataFrame())
        cashflow = payload.get("cashflow", pd.DataFrame())
        q_financials = payload.get("q_financials", pd.DataFrame())

        extra_data = {"q_financials": q_financials}
        return hist, info, fast_info, financials, balance_sheet, cashflow, extra_data, None

    except Exception as e:
        return None, None, None, None, None, None, None, f"Fetch failed: {str(e)}"

# =========================================================
# INDICATORS
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

    df["VOL20"] = df["Volume"].rolling(20).mean()
    df["RS_50"] = ((df["Close"] / df["SMA50"]) - 1) * 100
    df["RS_200"] = ((df["Close"] / df["SMA200"]) - 1) * 100

    return df

# =========================================================
# FUNDAMENTALS
# =========================================================
def extract_fundamentals_robust(symbol, info, fast_info, financials, balance_sheet, cashflow, extra_data=None):
    extra_data = extra_data or {}
    q_financials = extra_data.get("q_financials", pd.DataFrame())

    sym = symbol.upper().replace(".NS", "")
    fallback = NSE_MASTER_FALLBACK.get(sym, {})

    company_name = info.get("longName") or info.get("shortName") or sym
    sector = info.get("sector") or fallback.get("sector")
    industry = info.get("industry") or fallback.get("industry")

    market_cap = safe_num(info.get("marketCap"))
    if pd.isna(market_cap):
        market_cap = safe_num(fast_info.get("market_cap"))

    current_price = safe_num(info.get("currentPrice"))
    if pd.isna(current_price):
        current_price = safe_num(info.get("regularMarketPrice"))
    if pd.isna(current_price):
        current_price = safe_num(fast_info.get("lastPrice"))
    if pd.isna(current_price):
        current_price = safe_num(fast_info.get("last_price"))

    shares_outstanding = safe_num(info.get("sharesOutstanding"))
    if pd.isna(shares_outstanding):
        shares_outstanding = safe_num(info.get("impliedSharesOutstanding"))

    book_value = safe_num(info.get("bookValue"))
    eps = safe_num(info.get("trailingEps"))
    pe = safe_num(info.get("trailingPE"))
    if pd.isna(pe):
        pe = safe_num(info.get("forwardPE"))
    pb = safe_num(info.get("priceToBook"))

    roe = safe_num(info.get("returnOnEquity"))
    if not pd.isna(roe) and roe < 5:
        roe *= 100

    roa = safe_num(info.get("returnOnAssets"))
    if not pd.isna(roa) and roa < 5:
        roa *= 100

    debt_equity = safe_num(info.get("debtToEquity"))

    profit_margin = safe_num(info.get("profitMargins"))
    if not pd.isna(profit_margin) and profit_margin < 5:
        profit_margin *= 100

    operating_margin = safe_num(info.get("operatingMargins"))
    if not pd.isna(operating_margin) and operating_margin < 5:
        operating_margin *= 100

    gross_margin = safe_num(info.get("grossMargins"))
    if not pd.isna(gross_margin) and gross_margin < 5:
        gross_margin *= 100

    revenue_growth = safe_num(info.get("revenueGrowth"))
    if not pd.isna(revenue_growth) and revenue_growth < 5:
        revenue_growth *= 100

    earnings_growth = safe_num(info.get("earningsGrowth"))
    if not pd.isna(earnings_growth) and earnings_growth < 5:
        earnings_growth *= 100

    dividend_yield = safe_num(info.get("dividendYield"))
    if not pd.isna(dividend_yield) and dividend_yield < 5:
        dividend_yield *= 100

    current_ratio = safe_num(info.get("currentRatio"))
    quick_ratio = safe_num(info.get("quickRatio"))
    beta = safe_num(info.get("beta"))
    trailing_peg = safe_num(info.get("pegRatio"))

    net_income = get_safe_series_value(financials, "Net Income")
    if pd.isna(net_income):
        net_income = get_safe_series_value(financials, "Net Income Common Stockholders")

    total_revenue = get_safe_series_value(financials, "Total Revenue")
    if pd.isna(total_revenue):
        total_revenue = get_safe_series_value(q_financials, "Total Revenue")

    ebitda = get_safe_series_value(financials, "EBITDA")
    operating_income = get_safe_series_value(financials, "Operating Income")
    gross_profit = get_safe_series_value(financials, "Gross Profit")

    total_equity = get_safe_series_value(balance_sheet, "Stockholders Equity")
    if pd.isna(total_equity):
        total_equity = get_safe_series_value(balance_sheet, "Total Equity Gross Minority Interest")

    total_assets = get_safe_series_value(balance_sheet, "Total Assets")
    current_assets = get_safe_series_value(balance_sheet, "Current Assets")
    current_liabilities = get_safe_series_value(balance_sheet, "Current Liabilities")

    total_debt = get_safe_series_value(balance_sheet, "Total Debt")
    if pd.isna(total_debt):
        long_term_debt = get_safe_series_value(balance_sheet, "Long Term Debt")
        current_debt = get_safe_series_value(balance_sheet, "Current Debt")
        if pd.notna(long_term_debt) or pd.notna(current_debt):
            total_debt = np.nansum([long_term_debt, current_debt])

    cash = get_safe_series_value(balance_sheet, "Cash And Cash Equivalents")
    if pd.isna(cash):
        cash = get_safe_series_value(balance_sheet, "Cash Cash Equivalents And Short Term Investments")

    operating_cashflow = get_safe_series_value(cashflow, "Operating Cash Flow")
    free_cashflow = get_safe_series_value(cashflow, "Free Cash Flow")
    capex = get_safe_series_value(cashflow, "Capital Expenditure")

    if pd.isna(market_cap) and pd.notna(current_price) and pd.notna(shares_outstanding) and shares_outstanding > 0:
        market_cap = current_price * shares_outstanding

    if pd.isna(book_value) and pd.notna(total_equity) and pd.notna(shares_outstanding) and shares_outstanding > 0:
        book_value = total_equity / shares_outstanding

    if pd.isna(pb) and pd.notna(current_price) and pd.notna(book_value) and book_value > 0:
        pb = current_price / book_value
    if pd.isna(pb) and pd.notna(market_cap) and pd.notna(total_equity) and total_equity > 0:
        pb = market_cap / total_equity

    if pd.isna(eps) and pd.notna(net_income) and pd.notna(shares_outstanding) and shares_outstanding > 0:
        eps = net_income / shares_outstanding

    if pd.isna(pe) and pd.notna(current_price) and pd.notna(eps) and eps > 0:
        pe = current_price / eps

    if pd.isna(roe) and pd.notna(net_income) and pd.notna(total_equity) and total_equity > 0:
        roe = (net_income / total_equity) * 100

    if pd.isna(roa) and pd.notna(net_income) and pd.notna(total_assets) and total_assets > 0:
        roa = (net_income / total_assets) * 100

    if pd.isna(debt_equity) and pd.notna(total_debt) and pd.notna(total_equity) and total_equity > 0:
        debt_equity = total_debt / total_equity

    if pd.isna(profit_margin) and pd.notna(net_income) and pd.notna(total_revenue) and total_revenue > 0:
        profit_margin = (net_income / total_revenue) * 100

    if pd.isna(operating_margin) and pd.notna(operating_income) and pd.notna(total_revenue) and total_revenue > 0:
        operating_margin = (operating_income / total_revenue) * 100

    if pd.isna(gross_margin) and pd.notna(gross_profit) and pd.notna(total_revenue) and total_revenue > 0:
        gross_margin = (gross_profit / total_revenue) * 100

    if pd.isna(current_ratio) and pd.notna(current_assets) and pd.notna(current_liabilities) and current_liabilities > 0:
        current_ratio = current_assets / current_liabilities

    if pd.isna(revenue_growth):
        try:
            if q_financials is not None and not q_financials.empty and "Total Revenue" in q_financials.index:
                row = q_financials.loc["Total Revenue"]
                vals = [safe_num(v) for v in row if pd.notna(v)]
                if len(vals) >= 2 and pd.notna(vals[1]) and vals[1] != 0:
                    revenue_growth = ((vals[0] - vals[1]) / abs(vals[1])) * 100
        except:
            pass

    return {
        "Company Name": company_name,
        "Sector": sector,
        "Industry": industry,
        "Current Price": current_price,
        "Market Cap": market_cap,
        "Shares Outstanding": shares_outstanding,
        "P/E Ratio": pe,
        "EPS": eps,
        "P/B Ratio": pb,
        "Book Value": book_value,
        "ROE %": roe,
        "ROA %": roa,
        "Debt/Equity": debt_equity,
        "Profit Margin %": profit_margin,
        "Operating Margin %": operating_margin,
        "Gross Margin %": gross_margin,
        "Revenue Growth %": revenue_growth,
        "Earnings Growth %": earnings_growth,
        "Dividend Yield %": dividend_yield,
        "Current Ratio": current_ratio,
        "Quick Ratio": quick_ratio,
        "Beta": beta,
        "PEG Ratio": trailing_peg,
        "Total Revenue": total_revenue,
        "Gross Profit": gross_profit,
        "Operating Income": operating_income,
        "EBITDA": ebitda,
        "Net Income": net_income,
        "Operating Cash Flow": operating_cashflow,
        "Free Cash Flow": free_cashflow,
        "Capex": capex,
        "Total Assets": total_assets,
        "Total Equity": total_equity,
        "Total Debt": total_debt,
        "Cash": cash
    }

# =========================================================
# SCORING
# =========================================================
def score_fundamentals_normalized(fd):
    metrics = {}

    pe = safe_num(fd.get("P/E Ratio"))
    pb = safe_num(fd.get("P/B Ratio"))
    roe = safe_num(fd.get("ROE %"))
    roa = safe_num(fd.get("ROA %"))
    debt_equity = safe_num(fd.get("Debt/Equity"))
    profit_margin = safe_num(fd.get("Profit Margin %"))
    operating_margin = safe_num(fd.get("Operating Margin %"))
    revenue_growth = safe_num(fd.get("Revenue Growth %"))
    current_ratio = safe_num(fd.get("Current Ratio"))
    dividend_yield = safe_num(fd.get("Dividend Yield %"))

    metrics["P/E"] = normalize_linear(pe, 5, 40, invert=True) if pd.notna(pe) and pe > 0 else np.nan
    metrics["P/B"] = normalize_linear(pb, 0.5, 8, invert=True) if pd.notna(pb) and pb > 0 else np.nan
    metrics["ROE"] = normalize_linear(roe, 5, 25, invert=False)
    metrics["ROA"] = normalize_linear(roa, 2, 15, invert=False)
    metrics["Debt/Equity"] = normalize_linear(debt_equity, 0, 2.5, invert=True)
    metrics["Profit Margin"] = normalize_linear(profit_margin, 2, 25, invert=False)
    metrics["Operating Margin"] = normalize_linear(operating_margin, 5, 30, invert=False)
    metrics["Revenue Growth"] = normalize_linear(revenue_growth, -5, 20, invert=False)
    metrics["Current Ratio"] = normalize_linear(current_ratio, 0.8, 3.0, invert=False)
    metrics["Dividend Yield"] = normalize_linear(dividend_yield, 0, 5, invert=False)

    valid = [v for v in metrics.values() if pd.notna(v)]
    if not valid:
        return 50.0, "Fallback neutral score", metrics

    weights = {
        "P/E": 1.0,
        "P/B": 0.8,
        "ROE": 1.4,
        "ROA": 0.8,
        "Debt/Equity": 1.2,
        "Profit Margin": 1.2,
        "Operating Margin": 1.0,
        "Revenue Growth": 1.2,
        "Current Ratio": 0.6,
        "Dividend Yield": 0.3
    }

    num = 0
    den = 0
    for k, v in metrics.items():
        if pd.notna(v):
            w = weights.get(k, 1.0)
            num += v * w
            den += w

    score = round(num / den, 1) if den > 0 else 50.0
    return score, f"Normalized from {len(valid)} metrics", metrics

def score_technical_v91(df):
    if df is None or df.empty or len(df) < 50:
        return 45.0, "Not enough data", "Neutral", {}

    last = df.iloc[-1]

    close = safe_num(last["Close"])
    sma20 = safe_num(last["SMA20"])
    sma50 = safe_num(last["SMA50"])
    sma200 = safe_num(last["SMA200"])
    rsi = safe_num(last["RSI14"])
    macd = safe_num(last["MACD"])
    macd_signal = safe_num(last["MACD_SIGNAL"])
    rs50 = safe_num(last["RS_50"])
    rs200 = safe_num(last["RS_200"])

    metrics = {}
    metrics["Above 20DMA"] = 100 if pd.notna(close) and pd.notna(sma20) and close > sma20 else 30
    metrics["Above 50DMA"] = 100 if pd.notna(close) and pd.notna(sma50) and close > sma50 else 30
    metrics["Above 200DMA"] = 100 if pd.notna(close) and pd.notna(sma200) and close > sma200 else 20

    if pd.notna(sma20) and pd.notna(sma50) and pd.notna(sma200):
        if sma20 > sma50 > sma200:
            metrics["MA Alignment"] = 100
        elif sma20 > sma50:
            metrics["MA Alignment"] = 70
        else:
            metrics["MA Alignment"] = 35
    else:
        metrics["MA Alignment"] = np.nan

    if pd.notna(rsi):
        if 45 <= rsi <= 65:
            metrics["RSI"] = 90
        elif 35 <= rsi < 45 or 65 < rsi <= 75:
            metrics["RSI"] = 65
        elif rsi < 35:
            metrics["RSI"] = 55
        else:
            metrics["RSI"] = 40
    else:
        metrics["RSI"] = np.nan

    if pd.notna(macd) and pd.notna(macd_signal):
        metrics["MACD"] = 85 if macd > macd_signal else 35
    else:
        metrics["MACD"] = np.nan

    metrics["RS vs 50DMA"] = normalize_linear(rs50, -10, 15, invert=False)
    metrics["RS vs 200DMA"] = normalize_linear(rs200, -20, 30, invert=False)

    valid = [v for v in metrics.values() if pd.notna(v)]
    if not valid:
        return 45.0, "Indicators unavailable", "Neutral", metrics

    weights = {
        "Above 20DMA": 0.8,
        "Above 50DMA": 1.0,
        "Above 200DMA": 1.2,
        "MA Alignment": 1.2,
        "RSI": 0.8,
        "MACD": 0.8,
        "RS vs 50DMA": 1.0,
        "RS vs 200DMA": 1.2
    }

    num = 0
    den = 0
    for k, v in metrics.items():
        if pd.notna(v):
            w = weights.get(k, 1.0)
            num += v * w
            den += w

    score = round(num / den, 1) if den > 0 else 45.0

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

    note = f"Technical score from {len(valid)} normalized metrics"
    return score, note, trend, metrics

def support_resistance(df):
    if df is None or df.empty or len(df) < 30:
        return np.nan, np.nan
    recent = df.tail(30)
    return recent["Low"].min(), recent["High"].max()

def get_entry_zone(last_close, sma20, sma50, support):
    if pd.isna(last_close):
        return "N/A"
    vals = [v for v in [sma20, sma50, support] if pd.notna(v)]
    if not vals:
        return "N/A"
    anchor = np.nanmean(vals)
    diff_pct = ((last_close - anchor) / anchor) * 100 if anchor != 0 else np.nan

    if pd.isna(diff_pct):
        return "N/A"
    if diff_pct <= 2:
        return "🟢 Accumulation Zone"
    elif diff_pct <= 6:
        return "🟡 Buy on Dips"
    elif diff_pct <= 12:
        return "⚠️ Extended - Wait Better Entry"
    else:
        return "🔴 Overextended"

def get_verdict(score):
    if score >= 80:
        return "🔥 STRONG BUY / HIGH QUALITY", "good"
    elif score >= 68:
        return "✅ BUY / ACCUMULATE", "good"
    elif score >= 55:
        return "🟡 HOLD / WATCHLIST", "warn"
    elif score >= 42:
        return "⚠️ WAIT / AVOID FRESH ENTRY", "warn"
    else:
        return "❌ AVOID / WEAK SETUP", "bad"

# =========================================================
# ANALYSIS ENGINE
# =========================================================
def analyze_stock_v91(symbol, period="1y"):
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

    fund_score, fund_note, fund_metric_map = score_fundamentals_normalized(fundamental_data)
    tech_score, tech_note, trend, tech_metric_map = score_technical_v91(df)

    combined_long = round((fund_score * 0.65) + (tech_score * 0.35), 1)
    combined_swing = round((fund_score * 0.30) + (tech_score * 0.70), 1)
    combined_balanced = round((fund_score * 0.50) + (tech_score * 0.50), 1)

    support, resistance = support_resistance(df)
    atr = safe_num(df["ATR14"].iloc[-1]) if "ATR14" in df.columns else np.nan

    stop_loss = round(last_close - 1.2 * atr, 2) if pd.notna(last_close) and pd.notna(atr) else np.nan
    target1 = round(last_close + 1.5 * atr, 2) if pd.notna(last_close) and pd.notna(atr) else np.nan
    target2 = round(last_close + 3.0 * atr, 2) if pd.notna(last_close) and pd.notna(atr) else np.nan

    sma20 = safe_num(df["SMA20"].iloc[-1]) if "SMA20" in df.columns else np.nan
    sma50 = safe_num(df["SMA50"].iloc[-1]) if "SMA50" in df.columns else np.nan
    sma200 = safe_num(df["SMA200"].iloc[-1]) if "SMA200" in df.columns else np.nan

    entry_zone = get_entry_zone(last_close, sma20, sma50, support)

    long_verdict, long_type = get_verdict(combined_long)
    swing_verdict, swing_type = get_verdict(combined_swing)

    breakout = False
    reversal = False
    try:
        last = df.iloc[-1]
        recent_20_high = df["High"].tail(20).max()
        recent_20_low = df["Low"].tail(20).min()
        vol20 = safe_num(last["VOL20"])
        volume = safe_num(last["Volume"])
        rsi = safe_num(last["RSI14"])

        if pd.notna(last_close) and pd.notna(recent_20_high) and pd.notna(volume) and pd.notna(vol20):
            breakout = (last_close >= recent_20_high * 0.995) and (volume >= 1.2 * vol20)

        if pd.notna(last_close) and pd.notna(recent_20_low) and pd.notna(rsi):
            reversal = (last_close <= recent_20_low * 1.08) and (rsi < 40)
    except:
        pass

    rs_score = np.nan
    if pd.notna(sma50) and sma50 > 0 and pd.notna(sma200) and sma200 > 0:
        rs50 = ((last_close / sma50) - 1) * 100
        rs200 = ((last_close / sma200) - 1) * 100
        rs_score = round((normalize_linear(rs50, -10, 15) * 0.45) + (normalize_linear(rs200, -20, 30) * 0.55), 1)

    return {
        "df": df,
        "last_close": last_close,
        "change": change,
        "change_pct": change_pct,
        "fund_score": fund_score,
        "fund_note": fund_note,
        "fund_metric_map": fund_metric_map,
        "tech_score": tech_score,
        "tech_note": tech_note,
        "tech_metric_map": tech_metric_map,
        "trend": trend,
        "combined_balanced": combined_balanced,
        "combined_long": combined_long,
        "combined_swing": combined_swing,
        "support": support,
        "resistance": resistance,
        "stop_loss": stop_loss,
        "target1": target1,
        "target2": target2,
        "entry_zone": entry_zone,
        "long_verdict": long_verdict,
        "long_type": long_type,
        "swing_verdict": swing_verdict,
        "swing_type": swing_type,
        "fundamental_data": fundamental_data,
        "breakout": breakout,
        "reversal": reversal,
        "rs_score": rs_score
    }

# =========================================================
# CHARTS
# =========================================================
def build_price_chart(df, symbol):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price"
    ))

    for col, label in [("SMA20", "20DMA"), ("SMA50", "50DMA"), ("SMA200", "200DMA")]:
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], mode="lines", name=label))

    if "BB_UPPER" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_UPPER"], mode="lines", name="BB Upper", line=dict(dash="dot")))
    if "BB_LOWER" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_LOWER"], mode="lines", name="BB Lower", line=dict(dash="dot")))

    fig.update_layout(
        title=f"{symbol} - Price + MA + Bollinger Bands",
        template="plotly_dark",
        height=650,
        xaxis_rangeslider_visible=False
    )
    return fig

def build_rsi_chart(df, symbol):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI14"], mode="lines", name="RSI 14"))
    fig.add_hline(y=70, line_dash="dash")
    fig.add_hline(y=30, line_dash="dash")
    fig.update_layout(title=f"{symbol} - RSI (14)", template="plotly_dark", height=280)
    return fig

# =========================================================
# BULK ANALYSIS
# =========================================================
def run_pack_analysis(symbols, period="1y", max_stocks=5):
    rows = []
    symbols = symbols[:max_stocks]

    progress = st.progress(0, text="Preparing scan...")
    total = len(symbols)

    for idx, sym in enumerate(symbols, start=1):
        try:
            progress.progress(min(idx / max(total, 1), 1.0), text=f"Scanning {sym} ({idx}/{total})")
            res = analyze_stock_v91(sym, period)
            if "error" not in res:
                rows.append({
                    "Symbol": sym,
                    "Price": round(res["last_close"], 2) if pd.notna(res["last_close"]) else np.nan,
                    "Fund Score": res["fund_score"],
                    "Tech Score": res["tech_score"],
                    "RS Score": res["rs_score"],
                    "Balanced Score": res["combined_balanced"],
                    "Swing Score": res["combined_swing"],
                    "Long Score": res["combined_long"],
                    "Trend": res["trend"],
                    "Entry Zone": res["entry_zone"],
                    "Breakout": "YES" if res["breakout"] else "NO",
                    "Reversal": "YES" if res["reversal"] else "NO",
                    "Swing Verdict": res["swing_verdict"],
                    "Long Verdict": res["long_verdict"]
                })
        except:
            continue

    progress.empty()

    if rows:
        return pd.DataFrame(rows).sort_values("Balanced Score", ascending=False).reset_index(drop=True)
    return pd.DataFrame()

# =========================================================
# TOOLS
# =========================================================
def compute_trade_plan(entry, stop, target):
    entry = safe_num(entry)
    stop = safe_num(stop)
    target = safe_num(target)

    if pd.isna(entry) or pd.isna(stop) or pd.isna(target) or entry <= 0:
        return None

    risk = entry - stop
    reward = target - entry
    rr = reward / risk if risk > 0 else np.nan

    return {
        "Entry": entry,
        "Stop Loss": stop,
        "Target": target,
        "Risk/Share": risk,
        "Reward/Share": reward,
        "R:R": rr
    }

def future_value_sip(monthly, annual_return, years):
    r = annual_return / 12 / 100
    n = years * 12
    if r == 0:
        return monthly * n
    return monthly * (((1 + r) ** n - 1) / r) * (1 + r)

def future_value_lumpsum(amount, annual_return, years):
    return amount * ((1 + annual_return / 100) ** years)

def recommended_allocation(score):
    if pd.isna(score):
        return 0
    if score >= 80:
        return 20
    elif score >= 70:
        return 15
    elif score >= 60:
        return 10
    elif score >= 50:
        return 7
    elif score >= 40:
        return 4
    else:
        return 0

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## 📊 NSE Stock Intelligence Pro MAX")
st.sidebar.caption("V9.1 • Nifty 100 Master • Watchlist Scoring • Cloud Safe")

module_options = [
    "Single Stock Analysis",
    "Nifty 50 Explorer",
    "Nifty Next 50 Explorer",
    "Nifty 100 Explorer",
    "Elite Watchlist",
    "Institutional Dashboard",
    "Breakout Scanner",
    "Reversal Scanner",
    "Sector Rotation",
    "Trade Planner",
    "Portfolio DB",
    "Portfolio Allocation Engine",
    "Mini Screener",
    "Portfolio Ranker",
    "Multi-Stock Compare",
    "Portfolio Concentration Analysis",
    "Wealth Planner",
    "Returns Analyzer",
    "About"
]

module = st.sidebar.radio("Choose Module", module_options)

quick_pick = st.sidebar.selectbox("Quick NSE Pick", QUICK_LIST, index=0)
manual_symbol = st.sidebar.selectbox(
    "Select from Nifty 100",
    options=NIFTY_100,
    index=NIFTY_100.index(quick_pick) if quick_pick in NIFTY_100 else 0
)
custom_symbol = st.sidebar.text_input("Or Enter NSE Symbol Manually", value=manual_symbol)

period_map = {"6 Months": "6mo", "1 Year": "1y", "2 Years": "2y", "5 Years": "5y"}
period_label = st.sidebar.selectbox("Price History", list(period_map.keys()), index=1)
period = period_map[period_label]

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="hero-box">
    <div class="main-title">📊 NSE Stock Intelligence Pro MAX V9.1</div>
    <div class="sub-title">NIFTY 100 MASTER • AUTO WATCHLIST SCORING • MULTI-STOCK COMPARE • CLOUD SAFE • SINGLE FULL app.py</div>
    <span class="pill">Nifty 50</span>
    <span class="pill">Nifty Next 50</span>
    <span class="pill">Nifty 100</span>
    <span class="pill">Watchlist Auto Score</span>
    <span class="pill">Cloud Safe</span>
</div>
""", unsafe_allow_html=True)

# =========================================================
# MODULE: SINGLE STOCK ANALYSIS
# =========================================================
if module == "Single Stock Analysis":
    def render_single():
        st.subheader("📈 Single Stock Analysis")

        symbol = custom_symbol.strip().upper().replace(".NS", "")
        if not symbol:
            st.warning("Please enter a valid NSE symbol.")
            return

        if st.button("Analyze Stock", use_container_width=True):
            with st.spinner(f"Analyzing {symbol}.NS ..."):
                result = analyze_stock_v91(symbol, period)

            if "error" in result:
                st.error(result["error"])
                return

            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1:
                delta_text = f"{fmt(result['change'])} ({fmt(result['change_pct'])}%)" if pd.notna(result["change"]) else "N/A"
                st.metric("Price", f"₹ {fmt(result['last_close'])}", delta_text)
            with c2:
                st.metric("Fund Score", f"{result['fund_score']}/100")
            with c3:
                st.metric("Tech Score", f"{result['tech_score']}/100")
            with c4:
                st.metric("RS Score", f"{fmt(result['rs_score'])}")
            with c5:
                st.metric("Swing Score", f"{result['combined_swing']}/100")
            with c6:
                st.metric("Long Score", f"{result['combined_long']}/100")

            if result["swing_type"] == "good":
                st.markdown(f'<div class="good-box">SWING: {result["swing_verdict"]}</div>', unsafe_allow_html=True)
            elif result["swing_type"] == "warn":
                st.markdown(f'<div class="warn-box">SWING: {result["swing_verdict"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bad-box">SWING: {result["swing_verdict"]}</div>', unsafe_allow_html=True)

            if result["long_type"] == "good":
                st.markdown(f'<div class="good-box">LONG TERM: {result["long_verdict"]}</div>', unsafe_allow_html=True)
            elif result["long_type"] == "warn":
                st.markdown(f'<div class="warn-box">LONG TERM: {result["long_verdict"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bad-box">LONG TERM: {result["long_verdict"]}</div>', unsafe_allow_html=True)

            st.markdown(
                f'<div class="info-box">Trend: {result["trend"]} | Entry Zone: {result["entry_zone"]} | Breakout: {"YES" if result["breakout"] else "NO"} | Reversal: {"YES" if result["reversal"] else "NO"}</div>',
                unsafe_allow_html=True
            )

            tabs = st.tabs([
                "📈 Dashboard",
                "🧠 Technical Lab",
                "🏢 Fundamental Lab",
                "⚖️ Score Breakdown",
                "🎯 Trade Planner",
                "⭐ Add to Watchlist",
                "📂 Portfolio DB",
                "⬇️ Export"
            ])

            with tabs[0]:
                st.plotly_chart(build_price_chart(result["df"], symbol), use_container_width=True)
                st.plotly_chart(build_rsi_chart(result["df"], symbol), use_container_width=True)

                x1, x2, x3, x4, x5 = st.columns(5)
                with x1: st.metric("Support", f"₹ {fmt(result['support'])}")
                with x2: st.metric("Resistance", f"₹ {fmt(result['resistance'])}")
                with x3: st.metric("Stop Loss", f"₹ {fmt(result['stop_loss'])}")
                with x4: st.metric("Target 1", f"₹ {fmt(result['target1'])}")
                with x5: st.metric("Target 2", f"₹ {fmt(result['target2'])}")

            with tabs[1]:
                last = result["df"].iloc[-1]
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
                    ["ATR 14", fmt(last["ATR14"])],
                    ["Volume", fmt(last["Volume"], 0)],
                    ["20D Avg Vol", fmt(last["VOL20"], 0)]
                ]
                st.dataframe(pd.DataFrame(tech_rows, columns=["Indicator", "Value"]), use_container_width=True, hide_index=True)

            with tabs[2]:
                fd = result["fundamental_data"]
                ordered_keys = [
                    "Company Name", "Sector", "Industry", "Current Price", "Market Cap", "Shares Outstanding",
                    "P/E Ratio", "EPS", "P/B Ratio", "Book Value", "ROE %", "ROA %",
                    "Debt/Equity", "Profit Margin %", "Operating Margin %", "Gross Margin %",
                    "Revenue Growth %", "Earnings Growth %", "Dividend Yield %", "Current Ratio", "Quick Ratio",
                    "Beta", "PEG Ratio",
                    "Total Revenue", "Gross Profit", "Operating Income", "EBITDA", "Net Income",
                    "Operating Cash Flow", "Free Cash Flow", "Capex", "Total Assets", "Total Equity", "Total Debt", "Cash"
                ]

                rupee_cr_fields = {
                    "Market Cap", "Total Revenue", "Gross Profit", "Operating Income", "EBITDA",
                    "Net Income", "Operating Cash Flow", "Free Cash Flow", "Capex",
                    "Total Assets", "Total Equity", "Total Debt", "Cash"
                }
                percent_fields = {"ROE %", "ROA %", "Profit Margin %", "Operating Margin %", "Gross Margin %", "Revenue Growth %", "Earnings Growth %", "Dividend Yield %"}

                rows = []
                for k in ordered_keys:
                    v = fd.get(k, None)
                    if k == "Current Price":
                        value = f"₹ {v:,.2f}" if pd.notna(v) else "N/A"
                    elif k in rupee_cr_fields:
                        value = fmt_inr_cr(v)
                    elif k in percent_fields:
                        value = fmt_pct(v)
                    else:
                        value = format_generic_value(v)
                    rows.append([k, value])

                st.dataframe(pd.DataFrame(rows, columns=["Metric", "Value"]), use_container_width=True, hide_index=True)

                available = sum(1 for _, v in rows if v != "N/A")
                coverage = round((available / len(rows)) * 100, 1)
                st.info(f"Fundamental Coverage: {coverage}% | Uses info + fast_info + statements + derived ratios + fallback map.")

            with tabs[3]:
                st.markdown("### 🧮 Fundamental Score Breakdown")
                fund_breakdown = pd.DataFrame(
                    [[k, round(v, 1) if pd.notna(v) else "N/A"] for k, v in result["fund_metric_map"].items()],
                    columns=["Metric", "Score"]
                )
                st.dataframe(fund_breakdown, use_container_width=True, hide_index=True)

                st.markdown("### 📊 Technical Score Breakdown")
                tech_breakdown = pd.DataFrame(
                    [[k, round(v, 1) if pd.notna(v) else "N/A"] for k, v in result["tech_metric_map"].items()],
                    columns=["Metric", "Score"]
                )
                st.dataframe(tech_breakdown, use_container_width=True, hide_index=True)

            with tabs[4]:
                st.subheader("🎯 Trade Planner")
                default_entry = result["last_close"] if pd.notna(result["last_close"]) else 0
                default_stop = result["stop_loss"] if pd.notna(result["stop_loss"]) else 0
                default_target = result["target1"] if pd.notna(result["target1"]) else 0

                tp1, tp2, tp3, tp4 = st.columns(4)
                with tp1:
                    entry = st.number_input("Entry", min_value=0.0, value=float(default_entry) if pd.notna(default_entry) else 0.0, step=0.1, key="tp_entry_v91")
                with tp2:
                    stop = st.number_input("Stop Loss", min_value=0.0, value=float(default_stop) if pd.notna(default_stop) else 0.0, step=0.1, key="tp_stop_v91")
                with tp3:
                    target = st.number_input("Target", min_value=0.0, value=float(default_target) if pd.notna(default_target) else 0.0, step=0.1, key="tp_target_v91")
                with tp4:
                    capital = st.number_input("Capital", min_value=1000.0, value=100000.0, step=1000.0, key="tp_capital_v91")

                plan = compute_trade_plan(entry, stop, target)
                if plan:
                    risk_per_share = plan["Risk/Share"]
                    qty = math.floor(capital / entry) if entry > 0 else 0
                    total_risk = risk_per_share * qty if pd.notna(risk_per_share) else np.nan

                    p1, p2, p3, p4 = st.columns(4)
                    with p1: st.metric("Risk/Share", fmt(plan["Risk/Share"]))
                    with p2: st.metric("Reward/Share", fmt(plan["Reward/Share"]))
                    with p3: st.metric("R:R", fmt(plan["R:R"]))
                    with p4: st.metric("Max Qty", f"{qty}")

                    st.info(f"Estimated total position risk at full capital allocation: ₹ {fmt(total_risk)}")

            with tabs[5]:
                wl_note = st.text_input("Watchlist Note", value="High conviction / monitor", key="wl_note_v91")
                if st.button("Add to Elite Watchlist", use_container_width=True):
                    st.session_state.elite_watchlist.append({
                        "Symbol": symbol,
                        "Added At": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                        "Balanced Score": result["combined_balanced"],
                        "Swing Score": result["combined_swing"],
                        "Long Score": result["combined_long"],
                        "Entry Zone": result["entry_zone"],
                        "Trend": result["trend"],
                        "Note": wl_note
                    })
                    st.success(f"{symbol} added to Elite Watchlist.")

            with tabs[6]:
                st.subheader("📂 Add to Portfolio DB")
                add_qty = st.number_input("Quantity", min_value=1, value=10, step=1, key="single_add_qty_v91")
                add_avg = st.number_input("Average Buy Price", min_value=0.0, value=float(result["last_close"]) if pd.notna(result["last_close"]) else 0.0, step=0.1, key="single_add_avg_v91")

                if st.button("Add This Stock To Portfolio DB", use_container_width=True):
                    st.session_state.portfolio_db.append({
                        "Symbol": symbol,
                        "Qty": add_qty,
                        "Avg Buy": add_avg,
                        "Added At": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    })
                    st.success(f"{symbol} added to Portfolio DB.")

            with tabs[7]:
                csv = result["df"].reset_index().to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Full Price + Indicators CSV",
                    data=csv,
                    file_name=f"{symbol}_v91_nifty100_master_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("Click **Analyze Stock** to fetch data. This prevents heavy startup load on Streamlit Cloud.")

    safe_run_block(render_single, "Single Stock Analysis")

# =========================================================
# MODULE: NIFTY 50 EXPLORER
# =========================================================
elif module == "Nifty 50 Explorer":
    def render_nifty50():
        st.subheader("🇮🇳 Nifty 50 Explorer")
        st.success(f"Nifty 50 loaded: {len(NIFTY_50)} stocks")

        col1, col2 = st.columns([2, 1])
        with col1:
            selected = st.multiselect(
                "Select Nifty 50 stocks",
                options=NIFTY_50,
                default=["RELIANCE", "HDFCBANK", "ICICIBANK", "SBIN", "TCS"]
            )
        with col2:
            max_stocks = st.slider("Max Scan", 3, 8, 5, key="n50_max_v91")

        st.dataframe(pd.DataFrame({"Nifty 50 Stocks": NIFTY_50}), use_container_width=True, hide_index=True)

        if st.button("Run Nifty 50 Compare", use_container_width=True):
            symbols = selected[:max_stocks] if selected else NIFTY_50[:max_stocks]
            with st.spinner("Running Nifty 50 analysis..."):
                out = run_pack_analysis(symbols, period="1y", max_stocks=max_stocks)
            if out.empty:
                st.warning("No data returned.")
            else:
                st.dataframe(out, use_container_width=True, hide_index=True)
                st.markdown("### 🏆 Top Ranked")
                st.dataframe(out.head(3), use_container_width=True, hide_index=True)

    safe_run_block(render_nifty50, "Nifty 50 Explorer")

# =========================================================
# MODULE: NIFTY NEXT 50 EXPLORER
# =========================================================
elif module == "Nifty Next 50 Explorer":
    def render_nifty_next_50():
        st.subheader("🚀 Nifty Next 50 Explorer")
        st.success(f"Nifty Next 50 loaded: {len(NIFTY_NEXT_50)} stocks")

        col1, col2 = st.columns([2, 1])
        with col1:
            selected = st.multiselect(
                "Select Nifty Next 50 stocks",
                options=NIFTY_NEXT_50,
                default=["HAL", "DIVISLAB", "DMART", "SIEMENS", "VBL"]
            )
        with col2:
            max_stocks = st.slider("Max Scan", 3, 8, 5, key="next50_max_v91")

        st.dataframe(pd.DataFrame({"Nifty Next 50 Stocks": NIFTY_NEXT_50}), use_container_width=True, hide_index=True)

        if st.button("Run Nifty Next 50 Compare", use_container_width=True):
            symbols = selected[:max_stocks] if selected else NIFTY_NEXT_50[:max_stocks]
            with st.spinner("Running Nifty Next 50 analysis..."):
                out = run_pack_analysis(symbols, period="1y", max_stocks=max_stocks)
            if out.empty:
                st.warning("No data returned.")
            else:
                st.dataframe(out, use_container_width=True, hide_index=True)
                st.markdown("### 🏆 Top Ranked")
                st.dataframe(out.head(3), use_container_width=True, hide_index=True)

    safe_run_block(render_nifty_next_50, "Nifty Next 50 Explorer")

# =========================================================
# MODULE: NIFTY 100 EXPLORER
# =========================================================
elif module == "Nifty 100 Explorer":
    def render_nifty100():
        st.subheader("🏛️ Nifty 100 Explorer")
        st.success(f"Nifty 100 style universe loaded: {len(NIFTY_100)} stocks")

        col1, col2 = st.columns([2, 1])
        with col1:
            selected = st.multiselect(
                "Select Nifty 100 stocks",
                options=NIFTY_100,
                default=["RELIANCE", "HDFCBANK", "TCS", "HAL", "DIVISLAB"]
            )
        with col2:
            max_stocks = st.slider("Max Scan", 3, 10, 6, key="n100_max_v91")

        if st.button("Run Nifty 100 Compare", use_container_width=True):
            symbols = selected[:max_stocks] if selected else NIFTY_100[:max_stocks]
            with st.spinner("Running Nifty 100 analysis..."):
                out = run_pack_analysis(symbols, period="1y", max_stocks=max_stocks)
            if out.empty:
                st.warning("No data returned.")
            else:
                st.dataframe(out, use_container_width=True, hide_index=True)
                st.markdown("### 🏆 Top Ranked")
                st.dataframe(out.head(5), use_container_width=True, hide_index=True)

    safe_run_block(render_nifty100, "Nifty 100 Explorer")

# =========================================================
# MODULE: ELITE WATCHLIST
# =========================================================
elif module == "Elite Watchlist":
    def render_watchlist():
        st.subheader("⭐ Elite Watchlist")

        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            wl_symbol = st.selectbox("Select Symbol", NIFTY_100, key="wl_symbol_manual_v91")
        with c2:
            wl_note = st.text_input("Note", value="Monitor / High conviction", key="wl_manual_note_v91")
        with c3:
            st.write("")
            st.write("")
            if st.button("Add Manually", use_container_width=True):
                st.session_state.elite_watchlist.append({
                    "Symbol": wl_symbol,
                    "Added At": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                    "Balanced Score": np.nan,
                    "Swing Score": np.nan,
                    "Long Score": np.nan,
                    "Entry Zone": "Manual Add",
                    "Trend": "Pending",
                    "Note": wl_note
                })
                st.success(f"{wl_symbol} added to watchlist.")

        if st.session_state.elite_watchlist:
            wl_df = pd.DataFrame(st.session_state.elite_watchlist)
            st.dataframe(wl_df, use_container_width=True, hide_index=True)

            c1, c2 = st.columns(2)

            with c1:
                if st.button("Analyze Watchlist + Auto Score", use_container_width=True):
                    rows = []
                    symbols = list(dict.fromkeys([x["Symbol"] for x in st.session_state.elite_watchlist]))[:10]

                    with st.spinner("Analyzing watchlist and auto-scoring..."):
                        for sym in symbols:
                            try:
                                res = analyze_stock_v91(sym, "1y")
                                if "error" not in res:
                                    rows.append({
                                        "Symbol": sym,
                                        "Price": round(res["last_close"], 2) if pd.notna(res["last_close"]) else np.nan,
                                        "Fund Score": res["fund_score"],
                                        "Tech Score": res["tech_score"],
                                        "RS Score": res["rs_score"],
                                        "Balanced Score": res["combined_balanced"],
                                        "Swing Score": res["combined_swing"],
                                        "Long Score": res["combined_long"],
                                        "Trend": res["trend"],
                                        "Entry Zone": res["entry_zone"],
                                        "Breakout": "YES" if res["breakout"] else "NO",
                                        "Reversal": "YES" if res["reversal"] else "NO"
                                    })
                            except:
                                continue

                    if rows:
                        out = pd.DataFrame(rows).sort_values("Balanced Score", ascending=False).reset_index(drop=True)

                        st.markdown("### 📊 Watchlist Ranked Analysis")
                        st.dataframe(out, use_container_width=True, hide_index=True)

                        st.markdown("### 🏆 Top 10 Watchlist Leaders")
                        st.dataframe(out.head(10), use_container_width=True, hide_index=True)

                        csv = out.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "Download Watchlist Analysis CSV",
                            csv,
                            "elite_watchlist_analysis_v91.csv",
                            "text/csv"
                        )
                    else:
                        st.warning("No valid watchlist data returned.")

            with c2:
                if st.button("Clear Watchlist", use_container_width=True):
                    st.session_state.elite_watchlist = []
                    st.success("Watchlist cleared.")
        else:
            st.info("No stocks in Elite Watchlist yet. Add from Single Stock Analysis or manually here.")

    safe_run_block(render_watchlist, "Elite Watchlist")

# =========================================================
# MODULE: INSTITUTIONAL DASHBOARD
# =========================================================
elif module == "Institutional Dashboard":
    def render_institutional():
        st.subheader("🏛️ Institutional Dashboard (Cloud Safe)")

        col1, col2 = st.columns([1, 1])
        with col1:
            pack = st.selectbox("Choose Pack", list(SECTOR_PACKS.keys()), key="inst_pack_v91")
        with col2:
            max_stocks = st.slider("Max Stocks", 3, 8, 5, key="inst_max_v91")

        if st.button("Run Institutional Scan", use_container_width=True):
            with st.spinner("Scanning institutional universe..."):
                out = run_pack_analysis(SECTOR_PACKS[pack], period="1y", max_stocks=max_stocks)

            if not out.empty:
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Stocks Scanned", len(out))
                with c2: st.metric("Avg Balanced", round(out["Balanced Score"].mean(), 1))
                with c3: st.metric("Breakouts", int((out["Breakout"] == "YES").sum()))
                with c4: st.metric("Reversals", int((out["Reversal"] == "YES").sum()))

                st.dataframe(out, use_container_width=True, hide_index=True)
                st.markdown("### 🏆 Top Ranked")
                st.dataframe(out.head(3), use_container_width=True, hide_index=True)
            else:
                st.warning("No data returned from institutional scan.")
        else:
            st.info("Click **Run Institutional Scan** to start. No heavy scan runs automatically.")

    safe_run_block(render_institutional, "Institutional Dashboard")

# =========================================================
# MODULE: BREAKOUT SCANNER
# =========================================================
elif module == "Breakout Scanner":
    def render_breakout():
        st.subheader("🚀 Breakout Scanner")
        pack = st.selectbox("Choose Universe", list(SECTOR_PACKS.keys()), key="breakout_pack_v91")
        max_stocks = st.slider("Max Stocks", 3, 8, 5, key="breakout_max_v91")

        if st.button("Run Breakout Scan", use_container_width=True):
            with st.spinner("Scanning for breakout candidates..."):
                out = run_pack_analysis(SECTOR_PACKS[pack], period="1y", max_stocks=max_stocks)

            if out.empty:
                st.warning("No data available.")
            else:
                breakout_df = out[out["Breakout"] == "YES"].sort_values("Balanced Score", ascending=False)
                if breakout_df.empty:
                    st.info("No strong breakout candidate right now.")
                else:
                    st.dataframe(breakout_df, use_container_width=True, hide_index=True)
        else:
            st.info("Scanner runs only when you click the button.")

    safe_run_block(render_breakout, "Breakout Scanner")

# =========================================================
# MODULE: REVERSAL SCANNER
# =========================================================
elif module == "Reversal Scanner":
    def render_reversal():
        st.subheader("🔄 Reversal Scanner")
        pack = st.selectbox("Choose Universe", list(SECTOR_PACKS.keys()), key="reversal_pack_v91")
        max_stocks = st.slider("Max Stocks", 3, 8, 5, key="reversal_max_v91")

        if st.button("Run Reversal Scan", use_container_width=True):
            with st.spinner("Scanning for reversal candidates..."):
                out = run_pack_analysis(SECTOR_PACKS[pack], period="1y", max_stocks=max_stocks)

            if out.empty:
                st.warning("No data available.")
            else:
                reversal_df = out[out["Reversal"] == "YES"].sort_values("Balanced Score", ascending=False)
                if reversal_df.empty:
                    st.info("No strong reversal candidate right now.")
                else:
                    st.dataframe(reversal_df, use_container_width=True, hide_index=True)
        else:
            st.info("Scanner runs only when you click the button.")

    safe_run_block(render_reversal, "Reversal Scanner")

# =========================================================
# MODULE: SECTOR ROTATION
# =========================================================
elif module == "Sector Rotation":
    def render_sector_rotation():
        st.subheader("🏦 Sector Relative Strength Monitor")
        max_stocks = st.slider("Max Stocks Per Sector", 3, 6, 4, key="sector_rotation_max_v91")

        if st.button("Run Sector Rotation Monitor", use_container_width=True):
            rows = []
            with st.spinner("Running sector rotation monitor..."):
                for pack_name, symbols in SECTOR_PACKS.items():
                    out = run_pack_analysis(symbols, period="1y", max_stocks=max_stocks)
                    if not out.empty:
                        rows.append({
                            "Sector Pack": pack_name,
                            "Avg Balanced Score": round(out["Balanced Score"].mean(), 1),
                            "Avg RS Score": round(out["RS Score"].dropna().mean(), 1) if out["RS Score"].notna().any() else np.nan,
                            "Breakouts": int((out["Breakout"] == "YES").sum()),
                            "Reversals": int((out["Reversal"] == "YES").sum()),
                            "Top Stock": out.iloc[0]["Symbol"]
                        })

            if rows:
                sector_df = pd.DataFrame(rows).sort_values("Avg Balanced Score", ascending=False).reset_index(drop=True)
                st.dataframe(sector_df, use_container_width=True, hide_index=True)
                st.success(f"Leading sector pack: {sector_df.iloc[0]['Sector Pack']} | Top stock: {sector_df.iloc[0]['Top Stock']}")
            else:
                st.warning("Sector rotation data not available.")
        else:
            st.info("Sector rotation runs only when you click the button.")

    safe_run_block(render_sector_rotation, "Sector Rotation")

# =========================================================
# MODULE: TRADE PLANNER
# =========================================================
elif module == "Trade Planner":
    def render_trade_planner():
        st.subheader("🎯 Standalone Trade Planner")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            entry = st.number_input("Entry Price", min_value=0.0, value=100.0, step=0.1)
        with c2:
            stop = st.number_input("Stop Loss", min_value=0.0, value=95.0, step=0.1)
        with c3:
            target = st.number_input("Target", min_value=0.0, value=110.0, step=0.1)
        with c4:
            capital = st.number_input("Capital", min_value=1000.0, value=100000.0, step=1000.0)

        plan = compute_trade_plan(entry, stop, target)
        if plan:
            qty = math.floor(capital / entry) if entry > 0 else 0
            total_risk = plan["Risk/Share"] * qty if pd.notna(plan["Risk/Share"]) else np.nan
            total_reward = plan["Reward/Share"] * qty if pd.notna(plan["Reward/Share"]) else np.nan

            t1, t2, t3, t4, t5 = st.columns(5)
            with t1: st.metric("Risk/Share", fmt(plan["Risk/Share"]))
            with t2: st.metric("Reward/Share", fmt(plan["Reward/Share"]))
            with t3: st.metric("R:R", fmt(plan["R:R"]))
            with t4: st.metric("Max Qty", f"{qty}")
            with t5: st.metric("Position Value", f"₹ {fmt(qty * entry)}")

            st.info(f"Total Risk = ₹ {fmt(total_risk)} | Total Reward = ₹ {fmt(total_reward)}")

    safe_run_block(render_trade_planner, "Trade Planner")

# =========================================================
# MODULE: PORTFOLIO DB
# =========================================================
elif module == "Portfolio DB":
    def render_portfolio_db():
        st.subheader("📂 Portfolio Database (Session-Based)")

        c1, c2, c3 = st.columns(3)
        with c1:
            p_symbol = st.selectbox("Symbol", NIFTY_100 + [x for x in UNIVERSE if x not in NIFTY_100], key="pdb_symbol_v91")
        with c2:
            p_qty = st.number_input("Qty", min_value=1, value=10, step=1, key="pdb_qty_v91")
        with c3:
            p_avg = st.number_input("Avg Buy Price", min_value=0.0, value=100.0, step=0.1, key="pdb_avg_v91")

        if st.button("Add to Portfolio DB", use_container_width=True):
            st.session_state.portfolio_db.append({
                "Symbol": p_symbol,
                "Qty": p_qty,
                "Avg Buy": p_avg,
                "Added At": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            })
            st.success(f"{p_symbol} added.")

        if st.session_state.portfolio_db:
            db_df = pd.DataFrame(st.session_state.portfolio_db)
            st.dataframe(db_df, use_container_width=True, hide_index=True)

            if st.button("Analyze Portfolio DB", use_container_width=True):
                rows = []
                with st.spinner("Analyzing saved portfolio..."):
                    for row in st.session_state.portfolio_db[:10]:
                        sym = row["Symbol"]
                        qty = row["Qty"]
                        avg_buy = row["Avg Buy"]

                        try:
                            res = analyze_stock_v91(sym, "1y")
                            if "error" not in res:
                                ltp = res["last_close"]
                                invested = qty * avg_buy
                                current_value = qty * ltp if pd.notna(ltp) else np.nan
                                pnl = current_value - invested if pd.notna(current_value) else np.nan
                                pnl_pct = (pnl / invested * 100) if pd.notna(pnl) and invested != 0 else np.nan

                                rows.append({
                                    "Symbol": sym,
                                    "Qty": qty,
                                    "Avg Buy": avg_buy,
                                    "LTP": round(ltp, 2) if pd.notna(ltp) else np.nan,
                                    "Invested": round(invested, 2),
                                    "Current Value": round(current_value, 2) if pd.notna(current_value) else np.nan,
                                    "P&L": round(pnl, 2) if pd.notna(pnl) else np.nan,
                                    "P&L %": round(pnl_pct, 2) if pd.notna(pnl_pct) else np.nan,
                                    "Balanced Score": res["combined_balanced"],
                                    "Swing Score": res["combined_swing"],
                                    "Long Score": res["combined_long"]
                                })
                        except:
                            continue

                if rows:
                    out = pd.DataFrame(rows).sort_values("Balanced Score", ascending=False).reset_index(drop=True)
                    st.dataframe(out, use_container_width=True, hide_index=True)

            if st.button("Clear Portfolio DB", use_container_width=True):
                st.session_state.portfolio_db = []
                st.success("Portfolio DB cleared.")
        else:
            st.info("No stocks saved yet.")

    safe_run_block(render_portfolio_db, "Portfolio DB")

# =========================================================
# MODULE: PORTFOLIO ALLOCATION ENGINE
# =========================================================
elif module == "Portfolio Allocation Engine":
    def render_allocation_engine():
        st.subheader("🧠 Portfolio Allocation Engine")

        portfolio_input = st.text_area(
            "Enter comma-separated NSE symbols",
            value="RELIANCE,HDFCBANK,ICICIBANK,SBIN,ITC"
        )

        max_stocks = st.slider("Max Symbols", 3, 10, 5, key="alloc_max_v91")
        total_capital = st.number_input("Total Capital (₹)", min_value=10000.0, value=500000.0, step=10000.0)

        if st.button("Generate Allocation Plan", use_container_width=True):
            symbols = [x.strip().upper().replace(".NS", "") for x in portfolio_input.split(",") if x.strip()]
            symbols = list(dict.fromkeys(symbols))[:max_stocks]

            rows = []
            with st.spinner("Building allocation plan..."):
                for sym in symbols:
                    try:
                        res = analyze_stock_v91(sym, "1y")
                        if "error" not in res:
                            score = res["combined_balanced"]
                            alloc_pct = recommended_allocation(score)
                            rows.append({
                                "Symbol": sym,
                                "Price": round(res["last_close"], 2) if pd.notna(res["last_close"]) else np.nan,
                                "Balanced Score": score,
                                "Swing Score": res["combined_swing"],
                                "Long Score": res["combined_long"],
                                "Suggested Weight %": alloc_pct,
                                "Entry Zone": res["entry_zone"],
                                "Trend": res["trend"]
                            })
                    except:
                        continue

            if rows:
                out = pd.DataFrame(rows).sort_values("Balanced Score", ascending=False).reset_index(drop=True)
                total_weight = out["Suggested Weight %"].sum()

                if total_weight > 0:
                    out["Normalized Weight %"] = (out["Suggested Weight %"] / total_weight * 100).round(2)
                    out["Capital Allocation ₹"] = (out["Normalized Weight %"] / 100 * total_capital).round(2)
                    out["Suggested Qty"] = (out["Capital Allocation ₹"] / out["Price"]).replace([np.inf, -np.inf], np.nan).fillna(0).astype(int)
                else:
                    out["Normalized Weight %"] = 0
                    out["Capital Allocation ₹"] = 0
                    out["Suggested Qty"] = 0

                st.dataframe(out, use_container_width=True, hide_index=True)
                st.success("Allocation plan generated based on normalized balanced score.")
            else:
                st.warning("Could not generate allocation plan.")

    safe_run_block(render_allocation_engine, "Portfolio Allocation Engine")

# =========================================================
# MODULE: MINI SCREENER
# =========================================================
elif module == "Mini Screener":
    def render_mini_screener():
        st.subheader("🔎 Mini Screener")
        pack = st.selectbox("Choose Sector Pack", list(SECTOR_PACKS.keys()), key="mini_pack_v91")
        max_stocks = st.slider("Max Stocks", 3, 8, 5, key="mini_max_v91")

        if st.button("Run Screener", use_container_width=True):
            with st.spinner("Running screener..."):
                out = run_pack_analysis(SECTOR_PACKS[pack], period="1y", max_stocks=max_stocks)

            if out.empty:
                st.warning("No screener data.")
            else:
                st.dataframe(out, use_container_width=True, hide_index=True)
                csv = out.to_csv(index=False).encode("utf-8")
                st.download_button("Download Screener CSV", csv, f"{pack.lower().replace(' ','_')}_v91_screener.csv", "text/csv")
        else:
            st.info("Screener runs only when you click the button.")

    safe_run_block(render_mini_screener, "Mini Screener")

# =========================================================
# MODULE: PORTFOLIO RANKER
# =========================================================
elif module == "Portfolio Ranker":
    def render_portfolio_ranker():
        st.subheader("🏆 Portfolio Ranker")

        portfolio_input = st.text_area(
            "Enter comma-separated NSE symbols",
            value="RELIANCE,HDFCBANK,ICICIBANK,SBIN,ITC",
            key="ranker_input_v91"
        )

        max_stocks = st.slider("Max Symbols to Rank", 3, 10, 5, key="ranker_max_v91")

        if st.button("Rank Portfolio", use_container_width=True):
            symbols = [x.strip().upper().replace(".NS", "") for x in portfolio_input.split(",") if x.strip()]
            symbols = list(dict.fromkeys(symbols))[:max_stocks]

            if not symbols:
                st.warning("Please enter valid symbols.")
                return

            with st.spinner("Ranking portfolio..."):
                out = run_pack_analysis(symbols, period="1y", max_stocks=max_stocks)

            if out.empty:
                st.warning("No ranking data.")
            else:
                st.dataframe(out, use_container_width=True, hide_index=True)
                st.markdown("### 🏅 Top 3")
                st.dataframe(out.head(3), use_container_width=True, hide_index=True)
        else:
            st.info("Ranking runs only when you click the button.")

    safe_run_block(render_portfolio_ranker, "Portfolio Ranker")

# =========================================================
# MODULE: MULTI-STOCK COMPARE
# =========================================================
elif module == "Multi-Stock Compare":
    def render_multi_compare():
        st.subheader("📊 Multi-Stock Side-by-Side Compare")

        compare_input = st.text_area(
            "Enter comma-separated NSE symbols",
            value="RELIANCE,HDFCBANK,ICICIBANK,SBIN,TCS"
        )

        max_stocks = st.slider("Max Compare Stocks", 2, 8, 5, key="multi_compare_max_v91")

        if st.button("Run Side-by-Side Compare", use_container_width=True):
            symbols = [x.strip().upper().replace(".NS", "") for x in compare_input.split(",") if x.strip()]
            symbols = list(dict.fromkeys(symbols))[:max_stocks]

            with st.spinner("Running side-by-side compare..."):
                out = run_pack_analysis(symbols, period="1y", max_stocks=max_stocks)

            if out.empty:
                st.warning("No data available.")
            else:
                st.dataframe(out, use_container_width=True, hide_index=True)

                st.markdown("### 🏆 Best Ranked")
                st.dataframe(out.head(3), use_container_width=True, hide_index=True)

                csv = out.to_csv(index=False).encode("utf-8")
                st.download_button("Download Compare CSV", csv, "multi_stock_compare_v91.csv", "text/csv")

    safe_run_block(render_multi_compare, "Multi-Stock Compare")

# =========================================================
# MODULE: PORTFOLIO CONCENTRATION ANALYSIS
# =========================================================
elif module == "Portfolio Concentration Analysis":
    def render_concentration():
        st.subheader("🧠 Portfolio Concentration Analysis")

        if not st.session_state.portfolio_db:
            st.info("Add stocks first in Portfolio DB.")
            return

        db_df = pd.DataFrame(st.session_state.portfolio_db)
        db_df["Invested Value"] = db_df["Qty"] * db_df["Avg Buy"]

        total_invested = db_df["Invested Value"].sum()
        if total_invested <= 0:
            st.warning("Invalid invested values.")
            return

        db_df["Weight %"] = (db_df["Invested Value"] / total_invested * 100).round(2)
        db_df = db_df.sort_values("Weight %", ascending=False).reset_index(drop=True)

        st.metric("Total Invested", f"₹ {total_invested:,.2f}")
        st.dataframe(db_df, use_container_width=True, hide_index=True)

        top1 = db_df["Weight %"].iloc[0] if len(db_df) >= 1 else 0
        top3 = db_df["Weight %"].head(3).sum() if len(db_df) >= 3 else db_df["Weight %"].sum()
        top5 = db_df["Weight %"].head(5).sum() if len(db_df) >= 5 else db_df["Weight %"].sum()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Top 1 Weight", f"{top1:.2f}%")
        with c2:
            st.metric("Top 3 Weight", f"{top3:.2f}%")
        with c3:
            st.metric("Top 5 Weight", f"{top5:.2f}%")

        if top1 > 30:
            st.error("⚠️ Very high single-stock concentration risk.")
        elif top1 > 20:
            st.warning("⚠️ Moderate single-stock concentration risk.")
        else:
            st.success("✅ Concentration looks healthier.")

    safe_run_block(render_concentration, "Portfolio Concentration Analysis")

# =========================================================
# MODULE: WEALTH PLANNER
# =========================================================
elif module == "Wealth Planner":
    def render_wealth_planner():
        st.subheader("💰 Wealth Planner")

        tab1, tab2 = st.tabs(["📅 SIP Future Value", "💵 Lumpsum Future Value"])

        with tab1:
            c1, c2, c3 = st.columns(3)
            with c1:
                monthly_sip = st.number_input("Monthly SIP (₹)", min_value=500, value=10000, step=500)
            with c2:
                sip_return = st.number_input("Expected Annual Return (%)", min_value=0.0, value=12.0, step=0.5)
            with c3:
                sip_years = st.number_input("Years", min_value=1, value=10, step=1)

            fv = future_value_sip(monthly_sip, sip_return, sip_years)
            invested = monthly_sip * 12 * sip_years
            gain = fv - invested

            s1, s2, s3 = st.columns(3)
            with s1: st.metric("Total Invested", f"₹ {fmt(invested)}")
            with s2: st.metric("Estimated Value", f"₹ {fmt(fv)}")
            with s3: st.metric("Estimated Gain", f"₹ {fmt(gain)}")

        with tab2:
            c1, c2, c3 = st.columns(3)
            with c1:
                lumpsum = st.number_input("Lumpsum Amount (₹)", min_value=1000, value=100000, step=1000)
            with c2:
                lump_return = st.number_input("Expected Annual Return (%)", min_value=0.0, value=12.0, step=0.5, key="lump_return_v91")
            with c3:
                lump_years = st.number_input("Years", min_value=1, value=10, step=1, key="lump_years_v91")

            fv_lump = future_value_lumpsum(lumpsum, lump_return, lump_years)
            gain_lump = fv_lump - lumpsum

            l1, l2, l3 = st.columns(3)
            with l1: st.metric("Invested", f"₹ {fmt(lumpsum)}")
            with l2: st.metric("Estimated Value", f"₹ {fmt(fv_lump)}")
            with l3: st.metric("Estimated Gain", f"₹ {fmt(gain_lump)}")

    safe_run_block(render_wealth_planner, "Wealth Planner")

# =========================================================
# MODULE: RETURNS ANALYZER
# =========================================================
elif module == "Returns Analyzer":
    def render_returns():
        st.subheader("📈 Returns Analyzer")

        c1, c2, c3 = st.columns(3)
        with c1:
            buy_price = st.number_input("Buy Price", min_value=0.0, value=100.0, step=0.1)
        with c2:
            current_price = st.number_input("Current Price", min_value=0.0, value=120.0, step=0.1)
        with c3:
            qty = st.number_input("Quantity", min_value=1, value=100, step=1)

        invested = buy_price * qty
        current_value = current_price * qty
        pnl = current_value - invested
        pnl_pct = (pnl / invested * 100) if invested != 0 else np.nan

        r1, r2, r3, r4 = st.columns(4)
        with r1: st.metric("Invested", f"₹ {fmt(invested)}")
        with r2: st.metric("Current Value", f"₹ {fmt(current_value)}")
        with r3: st.metric("P&L", f"₹ {fmt(pnl)}")
        with r4: st.metric("Return %", f"{fmt(pnl_pct)}%")

    safe_run_block(render_returns, "Returns Analyzer")

# =========================================================
# MODULE: ABOUT
# =========================================================
else:
    def render_about():
        st.subheader("ℹ️ About V9.1")
        st.markdown(f"""
### FINAL V9.1 FULL MERGED STABLE SINGLE FULL app.py

This is your **full merged stable production-grade Streamlit Cloud build**.

### Major V9.1 Upgrades
- Full Nifty 50
- Full Nifty Next 50
- Nifty 100 Explorer
- Elite Watchlist
- **Auto Watchlist Scoring (fixed indentation)**
- Institutional Dashboard
- Multi-Stock Compare
- Portfolio Concentration Analysis
- Stable scanners (manual click only)
- Cloud-safe lazy loading
- Single-file architecture

### Universe Loaded
- **Nifty 50:** {len(NIFTY_50)}
- **Nifty Next 50:** {len(NIFTY_NEXT_50)}
- **Nifty 100 Combined:** {len(NIFTY_100)}

### Important Note
Yahoo Finance may still have partial NSE data for some symbols.  
This app uses fallback layers, but 100% perfect fundamentals for every NSE stock cannot be guaranteed.

### Disclaimer
For educational and research purposes only. Not investment advice.
""")

    safe_run_block(render_about, "About")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption(
    f"Built with Streamlit + yfinance | NSE (.NS) | FINAL V9.1 FULL MERGED STABLE SINGLE FULL app.py | {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)

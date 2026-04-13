import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import math

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="NSE Stock Intelligence Pro MAX V6 INSTITUTIONAL",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #cbd5e1;
        margin-bottom: 0.8rem;
    }
    .hero-box {
        padding: 1.2rem 1.4rem;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(14,116,144,0.22));
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
        padding: 0.8rem;
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
# CONSTANTS
# =========================================================
QUICK_LIST = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "SBIN", "AXISBANK", "KOTAKBANK", "LT", "ITC",
    "HINDUNILVR", "BHARTIARTL", "ASIANPAINT", "SUNPHARMA", "MARUTI"
]

SECTOR_PACKS = {
    "Nifty Core": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "LT"],
    "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK"],
    "IT": ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM"],
    "Auto": ["MARUTI", "TATAMOTORS", "M&M", "EICHERMOT", "HEROMOTOCO"],
    "Pharma": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "LUPIN"]
}

UNIVERSE = sorted(list(set(sum(SECTOR_PACKS.values(), []) + QUICK_LIST)))

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
    "ITC": {"sector": "Consumer Defensive", "industry": "Diversified FMCG"},
    "LT": {"sector": "Industrials", "industry": "Engineering & Construction"},
    "BHARTIARTL": {"sector": "Communication Services", "industry": "Telecom"},
    "HINDUNILVR": {"sector": "Consumer Defensive", "industry": "FMCG"},
    "SUNPHARMA": {"sector": "Healthcare", "industry": "Pharmaceuticals"},
    "DRREDDY": {"sector": "Healthcare", "industry": "Pharmaceuticals"},
    "CIPLA": {"sector": "Healthcare", "industry": "Pharmaceuticals"},
    "MARUTI": {"sector": "Consumer Cyclical", "industry": "Automobiles"},
    "TATAMOTORS": {"sector": "Consumer Cyclical", "industry": "Automobiles"},
    "M&M": {"sector": "Consumer Cyclical", "industry": "Automobiles"},
    "EICHERMOT": {"sector": "Consumer Cyclical", "industry": "Automobiles"},
    "HEROMOTOCO": {"sector": "Consumer Cyclical", "industry": "Automobiles"},
    "ASIANPAINT": {"sector": "Basic Materials", "industry": "Specialty Chemicals / Paints"}
}

# =========================================================
# SESSION STATE
# =========================================================
if "portfolio_db" not in st.session_state:
    st.session_state.portfolio_db = []

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

# =========================================================
# FETCH DATA (NO CACHING OF RAW OBJECTS)
# =========================================================
def fetch_full_stock_data(symbol: str, period: str = "1y"):
    try:
        ticker = yf.Ticker(get_nse_symbol(symbol))

        hist = ticker.history(period=period, auto_adjust=False)
        if hist is None or hist.empty:
            hist = ticker.history(period="6mo", auto_adjust=False)

        if hist is None or hist.empty:
            return None, None, None, None, None, None, None, "No price history found."

        hist = hist.dropna(subset=["Open", "High", "Low", "Close"])
        if hist.empty:
            return None, None, None, None, None, None, None, "Price history empty after cleaning."

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

        try:
            q_balance_sheet = ticker.quarterly_balance_sheet
            if q_balance_sheet is None:
                q_balance_sheet = pd.DataFrame()
            if not isinstance(q_balance_sheet, pd.DataFrame):
                q_balance_sheet = pd.DataFrame(q_balance_sheet)
        except:
            q_balance_sheet = pd.DataFrame()

        extra_data = {
            "q_financials": q_financials,
            "q_balance_sheet": q_balance_sheet
        }

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

    return df

# =========================================================
# FUNDAMENTALS ROBUST
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

    debt_equity = safe_num(info.get("debtToEquity"))

    profit_margin = safe_num(info.get("profitMargins"))
    if not pd.isna(profit_margin) and profit_margin < 5:
        profit_margin *= 100

    revenue_growth = safe_num(info.get("revenueGrowth"))
    if not pd.isna(revenue_growth) and revenue_growth < 5:
        revenue_growth *= 100

    dividend_yield = safe_num(info.get("dividendYield"))
    if not pd.isna(dividend_yield) and dividend_yield < 5:
        dividend_yield *= 100

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

    # derived
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

    if pd.isna(debt_equity) and pd.notna(total_debt) and pd.notna(total_equity) and total_equity > 0:
        debt_equity = total_debt / total_equity

    if pd.isna(profit_margin) and pd.notna(net_income) and pd.notna(total_revenue) and total_revenue > 0:
        profit_margin = (net_income / total_revenue) * 100

    if pd.isna(revenue_growth):
        try:
            if q_financials is not None and not q_financials.empty and "Total Revenue" in q_financials.index:
                row = q_financials.loc["Total Revenue"]
                vals = [safe_num(v) for v in row if pd.notna(v)]
                if len(vals) >= 2 and pd.notna(vals[1]) and vals[1] != 0:
                    revenue_growth = ((vals[0] - vals[1]) / abs(vals[1])) * 100
        except:
            pass

    current_ratio = np.nan
    if pd.notna(current_assets) and pd.notna(current_liabilities) and current_liabilities > 0:
        current_ratio = current_assets / current_liabilities

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
        "Debt/Equity": debt_equity,
        "Profit Margin %": profit_margin,
        "Revenue Growth %": revenue_growth,
        "Dividend Yield %": dividend_yield,
        "Current Ratio": current_ratio,
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
def score_fundamentals_from_data(fd):
    scores = []

    pe = safe_num(fd.get("P/E Ratio"))
    pb = safe_num(fd.get("P/B Ratio"))
    roe = safe_num(fd.get("ROE %"))
    debt_equity = safe_num(fd.get("Debt/Equity"))
    profit_margin = safe_num(fd.get("Profit Margin %"))
    revenue_growth = safe_num(fd.get("Revenue Growth %"))

    if pd.notna(pe):
        if 0 < pe <= 18: scores.append(100)
        elif pe <= 25: scores.append(80)
        elif pe <= 35: scores.append(60)
        elif pe <= 50: scores.append(40)
        else: scores.append(20)

    if pd.notna(pb):
        if pb <= 2: scores.append(100)
        elif pb <= 4: scores.append(80)
        elif pb <= 6: scores.append(60)
        else: scores.append(30)

    if pd.notna(roe):
        if roe >= 20: scores.append(100)
        elif roe >= 15: scores.append(85)
        elif roe >= 10: scores.append(65)
        else: scores.append(35)

    if pd.notna(debt_equity):
        if debt_equity <= 0.5: scores.append(100)
        elif debt_equity <= 1.0: scores.append(75)
        elif debt_equity <= 2.0: scores.append(50)
        else: scores.append(20)

    if pd.notna(profit_margin):
        if profit_margin >= 20: scores.append(100)
        elif profit_margin >= 10: scores.append(75)
        elif profit_margin >= 5: scores.append(55)
        else: scores.append(30)

    if pd.notna(revenue_growth):
        if revenue_growth >= 15: scores.append(100)
        elif revenue_growth >= 8: scores.append(75)
        elif revenue_growth >= 0: scores.append(55)
        else: scores.append(25)

    if not scores:
        return 50.0, "Fallback neutral score"
    return round(float(np.mean(scores)), 1), f"Scored from {len(scores)} metrics"

def score_technical(df):
    if df is None or df.empty or len(df) < 50:
        return 45.0, "Not enough data", "Neutral"

    last = df.iloc[-1]

    close = safe_num(last["Close"])
    sma20 = safe_num(last["SMA20"])
    sma50 = safe_num(last["SMA50"])
    sma200 = safe_num(last["SMA200"])
    rsi = safe_num(last["RSI14"])
    macd = safe_num(last["MACD"])
    macd_signal = safe_num(last["MACD_SIGNAL"])

    scores = []
    reasons = []

    if pd.notna(close) and pd.notna(sma20):
        scores.append(100 if close > sma20 else 35)
        reasons.append("Above 20DMA" if close > sma20 else "Below 20DMA")

    if pd.notna(close) and pd.notna(sma50):
        scores.append(100 if close > sma50 else 35)
        reasons.append("Above 50DMA" if close > sma50 else "Below 50DMA")

    if pd.notna(close) and pd.notna(sma200):
        scores.append(100 if close > sma200 else 20)
        reasons.append("Above 200DMA" if close > sma200 else "Below 200DMA")

    if pd.notna(sma20) and pd.notna(sma50) and pd.notna(sma200):
        if sma20 > sma50 > sma200:
            scores.append(100)
            reasons.append("Bullish MA alignment")
        elif sma20 > sma50:
            scores.append(70)
            reasons.append("Short-term bullish")
        else:
            scores.append(35)
            reasons.append("Weak alignment")

    if pd.notna(rsi):
        if 45 <= rsi <= 65:
            scores.append(90)
            reasons.append("Healthy RSI")
        elif 35 <= rsi < 45 or 65 < rsi <= 75:
            scores.append(65)
            reasons.append("Moderate RSI")
        elif rsi < 35:
            scores.append(55)
            reasons.append("Oversold RSI")
        else:
            scores.append(40)
            reasons.append("Overheated RSI")

    if pd.notna(macd) and pd.notna(macd_signal):
        scores.append(85 if macd > macd_signal else 35)
        reasons.append("MACD bullish" if macd > macd_signal else "MACD bearish")

    if not scores:
        return 45.0, "Indicators unavailable", "Neutral"

    score = round(float(np.mean(scores)), 1)

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

    return score, ", ".join(reasons[:4]), trend

def support_resistance(df):
    if df is None or df.empty or len(df) < 30:
        return np.nan, np.nan
    recent = df.tail(30)
    return recent["Low"].min(), recent["High"].max()

def get_verdict(fund_score, tech_score, combined):
    if combined >= 80 and tech_score >= 70:
        return "🔥 STRONG BUY / HIGH QUALITY", "good"
    elif combined >= 68 and tech_score >= 60:
        return "✅ BUY / ACCUMULATE", "good"
    elif combined >= 55:
        return "🟡 HOLD / WATCHLIST", "warn"
    elif combined >= 42:
        return "⚠️ WAIT / AVOID FRESH ENTRY", "warn"
    else:
        return "❌ AVOID / WEAK SETUP", "bad"

# =========================================================
# ANALYSIS ENGINE
# =========================================================
def analyze_stock(symbol, period="1y", mode="Balanced"):
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

    fund_score, fund_note = score_fundamentals_from_data(fundamental_data)
    tech_score, tech_note, trend = score_technical(df)

    if mode == "Long-Term":
        fw, tw = 0.65, 0.35
    elif mode == "Swing":
        fw, tw = 0.30, 0.70
    else:
        fw, tw = 0.50, 0.50

    combined = round((fund_score * fw) + (tech_score * tw), 1)

    support, resistance = support_resistance(df)
    atr = safe_num(df["ATR14"].iloc[-1]) if "ATR14" in df.columns else np.nan

    stop_loss = round(last_close - 1.2 * atr, 2) if pd.notna(last_close) and pd.notna(atr) else np.nan
    target1 = round(last_close + 1.5 * atr, 2) if pd.notna(last_close) and pd.notna(atr) else np.nan
    target2 = round(last_close + 3.0 * atr, 2) if pd.notna(last_close) and pd.notna(atr) else np.nan

    verdict, verdict_type = get_verdict(fund_score, tech_score, combined)

    # scanner flags
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

    return {
        "df": df,
        "last_close": last_close,
        "change": change,
        "change_pct": change_pct,
        "fund_score": fund_score,
        "fund_note": fund_note,
        "tech_score": tech_score,
        "tech_note": tech_note,
        "trend": trend,
        "combined": combined,
        "support": support,
        "resistance": resistance,
        "stop_loss": stop_loss,
        "target1": target1,
        "target2": target2,
        "verdict": verdict,
        "verdict_type": verdict_type,
        "fundamental_data": fundamental_data,
        "breakout": breakout,
        "reversal": reversal
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
# SCANNERS / UTILITIES
# =========================================================
def run_pack_analysis(symbols, mode="Balanced", period="1y"):
    rows = []
    for sym in symbols:
        try:
            res = analyze_stock(sym, period, mode)
            if "error" not in res:
                rows.append({
                    "Symbol": sym,
                    "Price": round(res["last_close"], 2) if pd.notna(res["last_close"]) else np.nan,
                    "Fundamental Score": res["fund_score"],
                    "Technical Score": res["tech_score"],
                    "Combined Score": res["combined"],
                    "Trend": res["trend"],
                    "Breakout": "YES" if res["breakout"] else "NO",
                    "Reversal": "YES" if res["reversal"] else "NO",
                    "Verdict": res["verdict"]
                })
        except:
            pass
    if rows:
        return pd.DataFrame(rows).sort_values("Combined Score", ascending=False).reset_index(drop=True)
    return pd.DataFrame()

def compute_trade_plan(entry, stop, target):
    entry = safe_num(entry)
    stop = safe_num(stop)
    target = safe_num(target)

    if pd.isna(entry) or pd.isna(stop) or pd.isna(target) or entry <= 0:
        return None

    risk = entry - stop
    reward = target - entry

    rr = np.nan
    if risk > 0:
        rr = reward / risk

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

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## 📊 NSE Stock Intelligence Pro MAX")
st.sidebar.caption("V6 INSTITUTIONAL • Single File • Cloud Safe")

module = st.sidebar.radio(
    "Choose Module",
    [
        "Institutional Dashboard",
        "Single Stock Analysis",
        "Breakout Scanner",
        "Reversal Scanner",
        "Sector Rotation",
        "Trade Planner",
        "Portfolio DB",
        "Mini Screener",
        "Portfolio Ranker",
        "Wealth Planner",
        "Returns Analyzer",
        "About"
    ]
)

mode = st.sidebar.selectbox("Analysis Mode", ["Balanced", "Long-Term", "Swing"])
quick_pick = st.sidebar.selectbox("Quick NSE Pick", QUICK_LIST, index=0)
manual_symbol = st.sidebar.text_input("Or Enter NSE Symbol", value=quick_pick)

period_map = {"6 Months": "6mo", "1 Year": "1y", "2 Years": "2y", "5 Years": "5y"}
period_label = st.sidebar.selectbox("Price History", list(period_map.keys()), index=1)
period = period_map[period_label]

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="hero-box">
    <div class="main-title">📊 NSE Stock Intelligence Pro MAX V6 INSTITUTIONAL</div>
    <div class="sub-title">Institutional-grade dashboard • Technical + Fundamental • Scanners • Sector Rotation • Trade Planner • Portfolio DB • Wealth tools • Single app.py</div>
    <span class="pill">Institutional Grade</span>
    <span class="pill">Cloud Safe</span>
    <span class="pill">Single app.py</span>
    <span class="pill">Portfolio DB</span>
    <span class="pill">Scanners</span>
</div>
""", unsafe_allow_html=True)

# =========================================================
# MODULE: INSTITUTIONAL DASHBOARD
# =========================================================
if module == "Institutional Dashboard":
    st.subheader("🏛️ Institutional Dashboard")

    col1, col2 = st.columns([1, 1])
    with col1:
        pack = st.selectbox("Choose Pack", list(SECTOR_PACKS.keys()), key="inst_pack")
    with col2:
        if st.button("Run Institutional Scan", use_container_width=True):
            pass

    with st.spinner("Scanning institutional universe..."):
        out = run_pack_analysis(SECTOR_PACKS[pack], mode=mode, period="1y")

    if not out.empty:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Stocks Scanned", len(out))
        with c2:
            st.metric("Avg Combined", round(out["Combined Score"].mean(), 1))
        with c3:
            st.metric("Breakouts", int((out["Breakout"] == "YES").sum()))
        with c4:
            st.metric("Reversals", int((out["Reversal"] == "YES").sum()))

        st.dataframe(out, use_container_width=True, hide_index=True)

        st.markdown("### 🏆 Top Ranked")
        st.dataframe(out.head(3), use_container_width=True, hide_index=True)

        st.markdown("### 🚀 Breakout Candidates")
        breakout_df = out[out["Breakout"] == "YES"]
        if breakout_df.empty:
            st.info("No strong breakout candidate in current selected pack.")
        else:
            st.dataframe(breakout_df, use_container_width=True, hide_index=True)

        st.markdown("### 🔄 Reversal Candidates")
        reversal_df = out[out["Reversal"] == "YES"]
        if reversal_df.empty:
            st.info("No strong reversal candidate in current selected pack.")
        else:
            st.dataframe(reversal_df, use_container_width=True, hide_index=True)

# =========================================================
# MODULE: SINGLE STOCK ANALYSIS
# =========================================================
elif module == "Single Stock Analysis":
    symbol = manual_symbol.strip().upper().replace(".NS", "")
    if not symbol:
        st.warning("Please enter a valid NSE symbol.")
        st.stop()

    with st.spinner(f"Analyzing {symbol}.NS ..."):
        result = analyze_stock(symbol, period, mode)

    if "error" in result:
        st.error(result["error"])
        st.stop()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        delta_text = f"{fmt(result['change'])} ({fmt(result['change_pct'])}%)" if pd.notna(result["change"]) else "N/A"
        st.metric("Price", f"₹ {fmt(result['last_close'])}", delta_text)
    with c2:
        st.metric("Tech Score", f"{result['tech_score']}/100")
    with c3:
        st.metric("Fund Score", f"{result['fund_score']}/100")
    with c4:
        st.metric("Combined", f"{result['combined']}/100")
    with c5:
        st.metric("Breakout", "YES" if result["breakout"] else "NO")
    with c6:
        st.metric("Reversal", "YES" if result["reversal"] else "NO")

    if result["verdict_type"] == "good":
        st.markdown(f'<div class="good-box">{result["verdict"]}</div>', unsafe_allow_html=True)
    elif result["verdict_type"] == "warn":
        st.markdown(f'<div class="warn-box">{result["verdict"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bad-box">{result["verdict"]}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="info-box">Trend: {result["trend"]} | {result["tech_note"]}</div>', unsafe_allow_html=True)

    tabs = st.tabs([
        "📈 Dashboard",
        "🧠 Technical Lab",
        "🏢 Fundamental Lab",
        "🎯 Trade Planner",
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
            "P/E Ratio", "EPS", "P/B Ratio", "Book Value", "ROE %", "Debt/Equity",
            "Profit Margin %", "Revenue Growth %", "Dividend Yield %", "Current Ratio",
            "Total Revenue", "Gross Profit", "Operating Income", "EBITDA", "Net Income",
            "Operating Cash Flow", "Free Cash Flow", "Capex", "Total Assets", "Total Equity", "Total Debt", "Cash"
        ]

        rupee_cr_fields = {
            "Market Cap", "Total Revenue", "Gross Profit", "Operating Income", "EBITDA",
            "Net Income", "Operating Cash Flow", "Free Cash Flow", "Capex",
            "Total Assets", "Total Equity", "Total Debt", "Cash"
        }
        percent_fields = {"ROE %", "Profit Margin %", "Revenue Growth %", "Dividend Yield %"}

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

        fund_df = pd.DataFrame(rows, columns=["Metric", "Value"])
        st.dataframe(fund_df, use_container_width=True, hide_index=True)

        available = sum(1 for _, v in rows if v != "N/A")
        coverage = round((available / len(rows)) * 100, 1)
        st.info(f"Fundamental Coverage: {coverage}% | V6 uses info + fast_info + statements + derived ratios + NSE fallback map.")

    with tabs[3]:
        st.subheader("🎯 Trade Planner")
        default_entry = result["last_close"] if pd.notna(result["last_close"]) else 0
        default_stop = result["stop_loss"] if pd.notna(result["stop_loss"]) else 0
        default_target = result["target1"] if pd.notna(result["target1"]) else 0

        tp1, tp2, tp3, tp4 = st.columns(4)
        with tp1:
            entry = st.number_input("Entry", min_value=0.0, value=float(default_entry) if pd.notna(default_entry) else 0.0, step=0.1, key="tp_entry_single")
        with tp2:
            stop = st.number_input("Stop Loss", min_value=0.0, value=float(default_stop) if pd.notna(default_stop) else 0.0, step=0.1, key="tp_stop_single")
        with tp3:
            target = st.number_input("Target", min_value=0.0, value=float(default_target) if pd.notna(default_target) else 0.0, step=0.1, key="tp_target_single")
        with tp4:
            capital = st.number_input("Capital", min_value=1000.0, value=100000.0, step=1000.0, key="tp_capital_single")

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

    with tabs[4]:
        st.subheader("📂 Add to Portfolio DB")
        add_qty = st.number_input("Quantity", min_value=1, value=10, step=1, key="single_add_qty")
        add_avg = st.number_input("Average Buy Price", min_value=0.0, value=float(result["last_close"]) if pd.notna(result["last_close"]) else 0.0, step=0.1, key="single_add_avg")

        if st.button("Add This Stock To Portfolio DB", use_container_width=True):
            st.session_state.portfolio_db.append({
                "Symbol": symbol,
                "Qty": add_qty,
                "Avg Buy": add_avg,
                "Added At": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            })
            st.success(f"{symbol} added to Portfolio DB.")

    with tabs[5]:
        csv = result["df"].reset_index().to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Full Price + Indicators CSV",
            data=csv,
            file_name=f"{symbol}_institutional_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# =========================================================
# MODULE: BREAKOUT SCANNER
# =========================================================
elif module == "Breakout Scanner":
    st.subheader("🚀 Breakout Scanner")
    pack = st.selectbox("Choose Universe", list(SECTOR_PACKS.keys()), key="breakout_pack")

    if st.button("Run Breakout Scan", use_container_width=True):
        with st.spinner("Scanning for breakout candidates..."):
            out = run_pack_analysis(SECTOR_PACKS[pack], mode=mode, period="1y")

        if out.empty:
            st.warning("No data available.")
        else:
            breakout_df = out[(out["Breakout"] == "YES")].sort_values("Combined Score", ascending=False)
            if breakout_df.empty:
                st.info("No strong breakout candidate right now.")
            else:
                st.dataframe(breakout_df, use_container_width=True, hide_index=True)

# =========================================================
# MODULE: REVERSAL SCANNER
# =========================================================
elif module == "Reversal Scanner":
    st.subheader("🔄 Reversal Scanner")
    pack = st.selectbox("Choose Universe", list(SECTOR_PACKS.keys()), key="reversal_pack")

    if st.button("Run Reversal Scan", use_container_width=True):
        with st.spinner("Scanning for reversal candidates..."):
            out = run_pack_analysis(SECTOR_PACKS[pack], mode=mode, period="1y")

        if out.empty:
            st.warning("No data available.")
        else:
            reversal_df = out[(out["Reversal"] == "YES")].sort_values("Combined Score", ascending=False)
            if reversal_df.empty:
                st.info("No strong reversal candidate right now.")
            else:
                st.dataframe(reversal_df, use_container_width=True, hide_index=True)

# =========================================================
# MODULE: SECTOR ROTATION
# =========================================================
elif module == "Sector Rotation":
    st.subheader("🏦 Sector Rotation Monitor")

    rows = []
    with st.spinner("Running sector rotation monitor..."):
        for pack_name, symbols in SECTOR_PACKS.items():
            out = run_pack_analysis(symbols, mode=mode, period="1y")
            if not out.empty:
                rows.append({
                    "Sector Pack": pack_name,
                    "Avg Combined Score": round(out["Combined Score"].mean(), 1),
                    "Avg Technical Score": round(out["Technical Score"].mean(), 1),
                    "Breakouts": int((out["Breakout"] == "YES").sum()),
                    "Reversals": int((out["Reversal"] == "YES").sum()),
                    "Top Stock": out.iloc[0]["Symbol"]
                })

    if rows:
        sector_df = pd.DataFrame(rows).sort_values("Avg Combined Score", ascending=False).reset_index(drop=True)
        st.dataframe(sector_df, use_container_width=True, hide_index=True)
        st.success(f"Leading sector pack now: {sector_df.iloc[0]['Sector Pack']} | Top stock: {sector_df.iloc[0]['Top Stock']}")
    else:
        st.warning("Sector rotation data not available.")

# =========================================================
# MODULE: TRADE PLANNER
# =========================================================
elif module == "Trade Planner":
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

# =========================================================
# MODULE: PORTFOLIO DB
# =========================================================
elif module == "Portfolio DB":
    st.subheader("📂 Portfolio Database (Session-Based)")

    c1, c2, c3 = st.columns(3)
    with c1:
        p_symbol = st.selectbox("Symbol", QUICK_LIST + [x for x in UNIVERSE if x not in QUICK_LIST], key="pdb_symbol")
    with c2:
        p_qty = st.number_input("Qty", min_value=1, value=10, step=1, key="pdb_qty")
    with c3:
        p_avg = st.number_input("Avg Buy Price", min_value=0.0, value=100.0, step=0.1, key="pdb_avg")

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
                for row in st.session_state.portfolio_db:
                    sym = row["Symbol"]
                    qty = row["Qty"]
                    avg_buy = row["Avg Buy"]

                    try:
                        res = analyze_stock(sym, "1y", mode)
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
                                "Combined Score": res["combined"],
                                "Verdict": res["verdict"]
                            })
                    except:
                        pass

            if rows:
                out = pd.DataFrame(rows).sort_values("Combined Score", ascending=False).reset_index(drop=True)
                st.dataframe(out, use_container_width=True, hide_index=True)

                total_invested = out["Invested"].sum()
                total_current = out["Current Value"].sum()
                total_pnl = total_current - total_invested
                total_pnl_pct = (total_pnl / total_invested * 100) if total_invested != 0 else np.nan

                s1, s2, s3 = st.columns(3)
                with s1: st.metric("Total Invested", f"₹ {fmt(total_invested)}")
                with s2: st.metric("Current Value", f"₹ {fmt(total_current)}")
                with s3: st.metric("Portfolio P&L", f"₹ {fmt(total_pnl)}", f"{fmt(total_pnl_pct)}%")

                csv = out.to_csv(index=False).encode("utf-8")
                st.download_button("Download Portfolio DB Analysis CSV", csv, "portfolio_db_analysis.csv", "text/csv")

        if st.button("Clear Portfolio DB", use_container_width=True):
            st.session_state.portfolio_db = []
            st.success("Portfolio DB cleared.")
    else:
        st.info("No stocks saved yet.")

# =========================================================
# MODULE: MINI SCREENER
# =========================================================
elif module == "Mini Screener":
    st.subheader("🔎 Mini Screener")
    pack = st.selectbox("Choose Sector Pack", list(SECTOR_PACKS.keys()), key="mini_pack")

    if st.button("Run Screener", use_container_width=True):
        with st.spinner("Running screener..."):
            out = run_pack_analysis(SECTOR_PACKS[pack], mode=mode, period="1y")

        if out.empty:
            st.warning("No screener data.")
        else:
            st.dataframe(out, use_container_width=True, hide_index=True)
            csv = out.to_csv(index=False).encode("utf-8")
            st.download_button("Download Screener CSV", csv, f"{pack.lower().replace(' ','_')}_screener.csv", "text/csv")

# =========================================================
# MODULE: PORTFOLIO RANKER
# =========================================================
elif module == "Portfolio Ranker":
    st.subheader("🏆 Portfolio Ranker")

    portfolio_input = st.text_area(
        "Enter comma-separated NSE symbols",
        value="RELIANCE,HDFCBANK,ICICIBANK,SBIN,ITC"
    )

    if st.button("Rank Portfolio", use_container_width=True):
        symbols = [x.strip().upper().replace(".NS", "") for x in portfolio_input.split(",") if x.strip()]
        symbols = list(dict.fromkeys(symbols))[:15]

        if not symbols:
            st.warning("Please enter valid symbols.")
            st.stop()

        with st.spinner("Ranking portfolio..."):
            out = run_pack_analysis(symbols, mode=mode, period="1y")

        if out.empty:
            st.warning("No ranking data.")
        else:
            st.dataframe(out, use_container_width=True, hide_index=True)
            st.markdown("### 🏅 Top 3")
            st.dataframe(out.head(3), use_container_width=True, hide_index=True)

# =========================================================
# MODULE: WEALTH PLANNER
# =========================================================
elif module == "Wealth Planner":
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
            lump_return = st.number_input("Expected Annual Return (%)", min_value=0.0, value=12.0, step=0.5, key="lump_return")
        with c3:
            lump_years = st.number_input("Years", min_value=1, value=10, step=1, key="lump_years")

        fv_lump = future_value_lumpsum(lumpsum, lump_return, lump_years)
        gain_lump = fv_lump - lumpsum

        l1, l2, l3 = st.columns(3)
        with l1: st.metric("Invested", f"₹ {fmt(lumpsum)}")
        with l2: st.metric("Estimated Value", f"₹ {fmt(fv_lump)}")
        with l3: st.metric("Estimated Gain", f"₹ {fmt(gain_lump)}")

# =========================================================
# MODULE: RETURNS ANALYZER
# =========================================================
elif module == "Returns Analyzer":
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

# =========================================================
# MODULE: ABOUT
# =========================================================
else:
    st.subheader("ℹ️ About V6 Institutional")
    st.markdown("""
### FINAL V6 INSTITUTIONAL PRO MAX (Single Full app.py)

This version is your **premium institutional-style Streamlit Cloud safe build**.

### Included Modules
- Institutional Dashboard
- Single Stock Analysis
- Breakout Scanner
- Reversal Scanner
- Sector Rotation
- Trade Planner
- Portfolio DB (session-based)
- Mini Screener
- Portfolio Ranker
- Wealth Planner
- Returns Analyzer

### Key Stability Improvements
- No Streamlit cache serialization issue
- Safer yfinance handling
- Robust NSE fallback for fundamentals
- Cleaner N/A handling
- Single-file architecture

### Important Note
Yahoo Finance may still have partial NSE data for some symbols.  
This app tries multiple fallbacks but cannot guarantee 100% complete fundamentals for every NSE stock.

### Disclaimer
For educational and research purposes only. Not investment advice.
""")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption(
    f"Built with Streamlit + yfinance | NSE (.NS) | FINAL V6 INSTITUTIONAL PRO MAX SINGLE FILE | {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)

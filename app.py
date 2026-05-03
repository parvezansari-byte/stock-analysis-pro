import streamlit as st

from modules.data_engine import get_history
from modules.technical_engine import compute_indicators
from modules.scoring_engine import score_stock
from modules.market_engine import analyze_universe, market_breadth, sector_distribution

st.set_page_config(page_title="Nile V17", layout="wide")

# -------------------------------
# UNIVERSE
# -------------------------------
NIFTY_50 = [
"RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","INFY.NS","ITC.NS","LT.NS",
"KOTAKBANK.NS","AXISBANK.NS","SBIN.NS","BHARTIARTL.NS","ASIANPAINT.NS",
"MARUTI.NS","HCLTECH.NS","BAJFINANCE.NS","SUNPHARMA.NS","TITAN.NS",
"ULTRACEMCO.NS","NESTLEIND.NS","WIPRO.NS","NTPC.NS","POWERGRID.NS",
"TATAMOTORS.NS","M&M.NS","ONGC.NS","COALINDIA.NS","JSWSTEEL.NS",
"TATASTEEL.NS","ADANIPORTS.NS","INDUSINDBK.NS","TECHM.NS","GRASIM.NS",
"CIPLA.NS","DRREDDY.NS","HINDALCO.NS","HEROMOTOCO.NS","EICHERMOT.NS",
"BPCL.NS","BRITANNIA.NS","APOLLOHOSP.NS","DIVISLAB.NS","ADANIENT.NS",
"TATACONSUM.NS","PIDILITIND.NS","SBILIFE.NS","BAJAJ-AUTO.NS",
"SHRIRAMFIN.NS","TRENT.NS"
]

NIFTY_NEXT_50 = [
"ABB.NS","ADANIGREEN.NS","ADANIPOWER.NS","AMBUJACEM.NS","BANKBARODA.NS",
"BOSCHLTD.NS","CANBK.NS","CGPOWER.NS","CHOLAFIN.NS","DABUR.NS",
"DLF.NS","GAIL.NS","GODREJCP.NS","HAL.NS","HAVELLS.NS","ICICIGI.NS",
"ICICIPRULI.NS","INDIGO.NS","IOC.NS","IRCTC.NS","JINDALSTEL.NS",
"JSWENERGY.NS","LICI.NS","LODHA.NS","LUPIN.NS","MCDOWELL-N.NS",
"MOTHERSON.NS","NAUKRI.NS","NMDC.NS","PFC.NS","PNB.NS","POLYCAB.NS",
"RECLTD.NS","SAIL.NS","SIEMENS.NS","TVSMOTOR.NS","VEDL.NS",
"VOLTAS.NS","ZYDUSLIFE.NS","INDUSTOWER.NS","TORNTPHARM.NS",
"HDFCLIFE.NS","COLPAL.NS","MARICO.NS","UBL.NS","BERGEPAINT.NS",
"CONCOR.NS","OFSS.NS"
]

# 🔥 FINAL COMBINED
NIFTY_100 = sorted(list(set(NIFTY_50 + NIFTY_NEXT_50)))
# -------------------------------
# UI
# -------------------------------
st.title("📊 Nile V17 - Modular Market Intelligence")

tabs = st.tabs(["Stock Analysis", "Market Analysis"])

# ===================================
# STOCK TAB
# ===================================
with tabs[0]:

    symbol = st.text_input("Stock", "RELIANCE.NS")

    if st.button("Analyze"):

        df = get_history(symbol)

        if df.empty:
            st.error("No data")
            st.stop()

        df = compute_indicators(df)
        last = df.iloc[-1]

        m = {
            "close": last["Close"],
            "sma20": last["SMA20"],
            "sma50": last["SMA50"],
            "rsi": last["RSI"]
        }

        score = score_stock(m)

        col1, col2, col3 = st.columns(3)
        col1.metric("Score", score)
        col2.metric("RSI", round(m["rsi"],2))
        col3.metric("Trend", "Bullish" if last["SMA20"] > last["SMA50"] else "Bearish")


# ===================================
# MARKET TAB
# ===================================
with tabs[1]:

    universe = st.selectbox(
        "Select Universe",
        ["NIFTY 50", "NIFTY NEXT 50", "FULL"]
    )

    if universe == "NIFTY 50":
        stocks = NIFTY_50
    elif universe == "NIFTY NEXT 50":
        stocks = NIFTY_NEXT_50
    else:
        stocks = NIFTY_50 + NIFTY_NEXT_50

    if st.button("Run Market Analysis"):

        results = analyze_universe(stocks)

        adv, dec, neutral, strength = market_breadth(results)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Advancers", adv)
        col2.metric("Decliners", dec)
        col3.metric("Neutral", neutral)
        col4.metric("Strength %", strength)

        st.subheader("📊 Sector Strength")
        sector = sector_distribution(results)
        st.bar_chart(sector)

        st.subheader("🔥 Top Stocks")
        top = sorted(results, key=lambda x: x["Score"], reverse=True)[:5]
        st.dataframe(top)

        st.subheader("⚠️ Weak Stocks")
        weak = sorted(results, key=lambda x: x["Score"])[:5]
        st.dataframe(weak)

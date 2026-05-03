import streamlit as st

from modules.data_engine import get_history
from modules.technical_engine import compute_indicators
from modules.scoring_engine import score_stock
from modules.ai_engine import ai_decision
from modules.trade_engine import trade_setup
from modules.scanner_engine import run_scan
from modules.report_engine import generate_pdf
from modules.market_engine import analyze_universe, market_breadth, sector_distribution

st.set_page_config(page_title="Nile V16", layout="wide")

st.title("📊 Nile V16 - Institutional Terminal")

tabs = st.tabs(["Stock Analysis", "Scanner"])

# ---------------- STOCK ANALYSIS ----------------
with tabs[0]:

    symbol = st.text_input("Stock", "RELIANCE.NS")
    capital = st.number_input("Capital", value=100000)
    risk = st.slider("Risk %", 0.5, 5.0, 1.0)

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
        decision = ai_decision(score)

        entry, stop, target, qty = trade_setup(df, capital, risk)

        col1, col2, col3 = st.columns(3)
        col1.metric("Score", score)
        col2.metric("Decision", decision)
        col3.metric("RSI", round(m["rsi"], 2))

        st.write("### Trade Setup")
        st.write(f"Entry: {entry:.2f}")
        st.write(f"Stop: {stop:.2f}")
        st.write(f"Target: {target:.2f}")
        st.write(f"Qty: {qty}")

        pdf = generate_pdf(symbol, score, decision, entry, stop, target)

        st.download_button("Download PDF", pdf, file_name="report.pdf")

# ---------------- SCANNER ----------------
with tabs[1]:

    stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]

    if st.button("Run Scan"):

        results = run_scan(stocks)

        st.dataframe(results)
# ---------------- UI INTEGRATION ----------------
with st.tab("Market Analysis"):

    universe = st.selectbox(
        "Universe",
        ["NIFTY 50", "NIFTY NEXT 50", "FULL 100"]
    )

    if universe == "NIFTY 50":
        stocks = NIFTY_50
    elif universe == "NIFTY NEXT 50":
        stocks = NIFTY_NEXT_50
    else:
        stocks = NIFTY_50 + NIFTY_NEXT_50

    if st.button("Run Market Analysis"):

        results = analyze_universe(stocks)

        # 🔹 Breadth
        breadth = market_breadth(results)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Advancers", breadth["Advancers"])
        col2.metric("Decliners", breadth["Decliners"])
        col3.metric("Neutral", breadth["Neutral"])
        col4.metric("Strength %", breadth["Strength %"])

        # 🔹 Sector
        sector = sector_distribution(results)

        st.subheader("Sector Strength")
        st.bar_chart(sector)

        # 🔹 Top Stocks
        st.subheader("Top 10 Stocks")
        top = sorted(results, key=lambda x: x["Score"], reverse=True)[:10]
        st.dataframe(top)

        # 🔹 Weak Stocks
        st.subheader("Weak Stocks")
        weak = sorted(results, key=lambda x: x["Score"])[:10]
        st.dataframe(weak)
        

import streamlit as st

from modules.data_engine import get_history
from modules.technical_engine import compute_indicators
from modules.scoring_engine import score_stock
from modules.ai_engine import ai_decision
from modules.trade_engine import trade_setup
from modules.scanner_engine import run_scan
from modules.report_engine import generate_pdf

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

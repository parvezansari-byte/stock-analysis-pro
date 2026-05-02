import streamlit as st

from data_engine import get_history, get_info
from technical_engine import compute_indicators
from scoring_engine import score_stock
from ai_engine import ai_decision
from trade_engine import trade_setup

st.set_page_config(page_title="Nile Safe", layout="wide")

st.title("📊 Nile - Deploy Safe Version")

symbol = st.text_input("Enter Stock", "RELIANCE.NS")
capital = st.number_input("Capital", value=100000)
risk = st.slider("Risk %", 0.5, 5.0, 1.0)

if st.button("Analyze"):

    df = get_history(symbol)

    if df.empty:
        st.error("No data found")
        st.stop()

    df = compute_indicators(df)

    last = df.iloc[-1]

    metrics = {
        "close": last["Close"],
        "sma20": last["SMA20"],
        "sma50": last["SMA50"],
        "rsi": last["RSI"]
    }

    score = score_stock(metrics)
    decision = ai_decision(score)

    entry, stop, target, qty = trade_setup(df, capital, risk)

    st.subheader("📊 Analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric("Score", score)
    col2.metric("Decision", decision)
    col3.metric("RSI", round(metrics["rsi"], 2))

    st.subheader("💰 Trade Setup")

    st.write(f"Entry: {entry:.2f}")
    st.write(f"Stop Loss: {stop:.2f}")
    st.write(f"Target: {target:.2f}")
    st.write(f"Quantity: {qty}")

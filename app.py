import streamlit as st

from modules.data_engine import get_history, get_info
from modules.technical_engine import compute_indicators
from modules.scoring_engine import score_stock
from modules.ai_engine import ai_decision
from modules.trade_engine import trade_setup

st.title("NILE V16 - Modular Terminal")

symbol = st.text_input("Stock", "RELIANCE.NS")

if st.button("Analyze"):

    df = get_history(symbol)
    info = get_info(symbol)

    df = compute_indicators(df)

    last = df.iloc[-1]

    metrics = {
        "close": last["Close"],
        "sma20": last["SMA20"],
        "sma50": last["SMA50"],
        "rsi": last["RSI"],
        "macd": last["MACD"],
        "macd_signal": last["MACD_SIGNAL"]
    }

    score = score_stock(metrics)

    decision = ai_decision(score, metrics["rsi"])

    entry, stop, target, qty = trade_setup(df, 100000, 1, 2)

    st.write("Score:", score)
    st.write("Decision:", decision)
    st.write("Trade:", entry, stop, target, qty)

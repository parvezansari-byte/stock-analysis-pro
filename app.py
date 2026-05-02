import streamlit as st

from modules.data import get_stock_data, get_stock_info
from modules.technical import compute_technical
from modules.fundamental import extract_fundamentals
from modules.scoring import technical_score
from modules.trade import trade_setup
from modules.ai import ai_decision

st.title("Split Wise Stock Analysis")

symbol = st.text_input("Enter Stock", "RELIANCE.NS")

if st.button("Analyze"):

    df = get_stock_data(symbol)
    info = get_stock_info(symbol)

    df = compute_technical(df)
    fundamentals = extract_fundamentals(info)

    score = technical_score(df)
    decision = ai_decision(score)

    entry, stop, target, qty = trade_setup(df, 100000, 1)

    st.write("Score:", score)
    st.write("Decision:", decision)
    st.write("Entry:", entry)
    st.write("Stop:", stop)
    st.write("Target:", target)
    st.write("Qty:", qty)

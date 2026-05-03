import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def get_history(symbol, period="6mo"):
    try:
        df = yf.download(symbol, period=period, auto_adjust=True, progress=False)
        return df.dropna()
    except:
        return pd.DataFrame()


@st.cache_data(ttl=86400)
def get_sector(symbol):
    try:
        info = yf.Ticker(symbol).info
        return info.get("sector", "Others")
    except:
        return "Others"

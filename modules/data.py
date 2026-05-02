import yfinance as yf
import pandas as pd

def get_stock_data(symbol, period="1y"):
    df = yf.download(symbol, period=period, auto_adjust=True)
    return df

def get_stock_info(symbol):
    return yf.Ticker(symbol).info

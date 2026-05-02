import yfinance as yf

def get_history(symbol, period="1y"):
    return yf.download(symbol, period=period, auto_adjust=True)

def get_info(symbol):
    return yf.Ticker(symbol).info

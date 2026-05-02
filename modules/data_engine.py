import yfinance as yf

def get_history(symbol, period="1y"):
    df = yf.download(symbol, period=period, auto_adjust=True)
    return df.dropna()

def get_info(symbol):
    return yf.Ticker(symbol).info

from modules.data_engine import get_history
from modules.technical_engine import compute_indicators
from modules.scoring_engine import score_stock

def analyze_universe(stock_list):

    results = []

    for s in stock_list:

        df = get_history(s, "6mo")

        if df.empty or len(df) < 50:
            continue

        df = compute_indicators(df)
        last = df.iloc[-1]

        m = {
            "close": last["Close"],
            "sma20": last["SMA20"],
            "sma50": last["SMA50"],
            "rsi": last["RSI"]
        }

        score = score_stock(m)

        trend = "Bullish" if last["SMA20"] > last["SMA50"] else "Bearish"

        results.append({
            "Stock": s,
            "Score": score,
            "RSI": round(m["rsi"], 2),
            "Trend": trend
        })

    return results

from modules.data_engine import get_history
from modules.technical_engine import compute_indicators
from modules.scoring_engine import score_stock

def run_scan(stock_list):

    results = []

    for s in stock_list:

        df = get_history(s)

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

        results.append({"Stock": s, "Score": score})

    return sorted(results, key=lambda x: x["Score"], reverse=True)

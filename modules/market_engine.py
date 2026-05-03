from modules.data_engine import get_history, get_sector
from modules.technical_engine import compute_indicators
from modules.scoring_engine import score_stock
import numpy as np


def analyze_universe(stocks):

    results = []

    for s in stocks:

        df = get_history(s)

        if df.empty or len(df) < 50:
            continue

        df = compute_indicators(df)
        last = df.iloc[-1]

        m = {
    "close": float(last["Close"]),
    "sma20": float(last["SMA20"]),
    "sma50": float(last["SMA50"]),
    "rsi": float(last["RSI"])
}

        score = score_stock(m)
        trend = "Bullish" if last["SMA20"] > last["SMA50"] else "Bearish"

        # 🔥 AUTO SECTOR
        sector = get_sector(s)

        results.append({
            "Stock": s,
            "Score": score,
            "RSI": round(m["rsi"], 2),
            "Trend": trend,
            "Sector": sector
        })

    return results


def market_breadth(results):

    if not results:
        return 0, 0, 0, 0

    adv = sum(1 for r in results if r["Score"] >= 60)
    dec = sum(1 for r in results if r["Score"] < 40)
    neutral = len(results) - adv - dec

    strength = (adv / len(results)) * 100

    return adv, dec, neutral, round(strength, 2)


def sector_distribution(results):

    sector_data = {}

    for r in results:
        sector = r["Sector"]
        sector_data.setdefault(sector, []).append(r["Score"])

    return {
        sec: round(np.mean(scores), 2)
        for sec, scores in sector_data.items()
    }

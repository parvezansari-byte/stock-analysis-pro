# modules/market_engine.py

from modules.data_engine import get_history
from modules.technical_engine import compute_indicators
from modules.scoring_engine import score_stock
import numpy as np


# -----------------------------------
# 🔹 MAIN UNIVERSE ANALYSIS
# -----------------------------------
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


# -----------------------------------
# 🔹 MARKET BREADTH ENGINE
# -----------------------------------
def market_breadth(results):

    if not results:
        return {
            "Advancers": 0,
            "Decliners": 0,
            "Neutral": 0,
            "Strength %": 0
        }

    adv = sum(1 for r in results if r["Score"] >= 60)
    dec = sum(1 for r in results if r["Score"] < 40)
    neutral = len(results) - adv - dec

    strength = (adv / len(results)) * 100

    return {
        "Advancers": adv,
        "Decliners": dec,
        "Neutral": neutral,
        "Strength %": round(strength, 2)
    }


# -----------------------------------
# 🔹 SECTOR DISTRIBUTION ENGINE
# -----------------------------------
SECTOR_MAP = {
    "RELIANCE.NS": "Energy",
    "ONGC.NS": "Energy",
    "TCS.NS": "IT",
    "INFY.NS": "IT",
    "HCLTECH.NS": "IT",
    "HDFCBANK.NS": "Banking",
    "ICICIBANK.NS": "Banking",
    "SBIN.NS": "Banking",
    "MARUTI.NS": "Auto",
    "TATAMOTORS.NS": "Auto",
}

def sector_distribution(results):

    sector_data = {}

    for r in results:

        stock = r["Stock"]
        score = r["Score"]

        sector = SECTOR_MAP.get(stock, "Others")

        sector_data.setdefault(sector, []).append(score)

    # Average score per sector
    sector_strength = {
        sec: round(np.mean(scores), 2)
        for sec, scores in sector_data.items()
    }

    return sector_strength

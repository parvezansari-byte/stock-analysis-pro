def score_stock(m):
    score = 0

    if m["close"] > m["sma20"]: score += 20
    if m["close"] > m["sma50"]: score += 20
    if 50 < m["rsi"] < 70: score += 20

    return score

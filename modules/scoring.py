def technical_score(df):

    last = df.iloc[-1]

    score = 0

    if last["Close"] > last["SMA20"]:
        score += 20

    if last["Close"] > last["SMA50"]:
        score += 20

    if 50 < last["RSI"] < 70:
        score += 20

    return score

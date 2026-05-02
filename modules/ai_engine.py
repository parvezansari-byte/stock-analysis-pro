def ai_decision(score):
    if score >= 60:
        return "BUY"
    elif score >= 40:
        return "HOLD"
    return "SELL"

def trade_setup(df, capital, risk_pct):

    last = df.iloc[-1]

    entry = last["High"]
    stop = last["Low"]

    risk = capital * (risk_pct / 100)
    risk_per_share = entry - stop

    qty = int(risk / risk_per_share) if risk_per_share > 0 else 0
    target = entry + (risk_per_share * 2)

    return entry, stop, target, qty

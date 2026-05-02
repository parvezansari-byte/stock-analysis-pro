def extract_fundamentals(info):

    return {
        "pe": info.get("trailingPE"),
        "roe": info.get("returnOnEquity"),
        "de": info.get("debtToEquity"),
        "growth": info.get("revenueGrowth"),
    }

# HKD to USD fixed exchange rate
HKD_USD_RATE = 1 / 7.8

# Portfolio holdings
# currency: "USD" (default) or "HKD" for HKEX-listed stocks
PORTFOLIO_HOLDINGS = [
    {"symbol": "BABA", "shares": 1000, "currency": "USD"},
    {"symbol": "9988.HK", "shares": 15200, "currency": "HKD"},
    {"symbol": "BRK-B", "shares": 300, "currency": "USD"},
    {"symbol": "KWEB", "shares": 1100, "currency": "USD"},
    {"symbol": "0823.HK", "shares": 160525, "currency": "HKD"},
]

# Companies to track for earnings
TRACKED_SYMBOLS = ["BABA", "BRK-B", "KWEB"]

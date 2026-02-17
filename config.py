# FX pairs to fetch via yfinance (XXX to USD)
FX_PAIRS = {
    "HKD": "HKDUSD=X",
    "SGD": "SGDUSD=X",
}

# Portfolio holdings
# currency: "USD" (default), "HKD", or "SGD"
PORTFOLIO_HOLDINGS = [
    {"symbol": "BABA", "shares": 1000, "currency": "USD"},
    {"symbol": "9988.HK", "shares": 15200, "currency": "HKD"},
    {"symbol": "BRK-B", "shares": 300, "currency": "USD"},
    {"symbol": "KWEB", "shares": 1100, "currency": "USD"},
    {"symbol": "0823.HK", "shares": 160525, "currency": "HKD"},
]

# Margin loans (amount in local currency)
MARGIN_LOANS = [
    {"currency": "SGD", "amount": 594000, "label": "SGD Margin Loan"},
]

# Companies to track for earnings
TRACKED_SYMBOLS = ["BABA", "BRK-B", "KWEB"]

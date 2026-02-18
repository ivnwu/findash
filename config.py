# FX pairs to fetch via yfinance (XXX to USD)
FX_PAIRS = {
    "HKD": "HKDUSD=X",
    "SGD": "SGDUSD=X",
}

# Companies to track for earnings
TRACKED_SYMBOLS = ["BABA", "BRK-B", "KWEB"]

# Benchmark indices stored alongside portfolio holdings in asset_prices
BENCHMARK_SYMBOLS = {
    "^HSI": "Hang Seng Index",
    "^GSPC": "S&P 500",
    "URTH": "MSCI World (ETF)",
}

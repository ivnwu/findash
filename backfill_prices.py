"""Backfill asset_prices with ~3 years of daily close prices.

Fetches history for all user holdings and benchmark indices, then
upserts one row per (symbol, date) into asset_prices.

Usage:
    python backfill_prices.py
"""

import yfinance as yf
from pathlib import Path
from dotenv import load_dotenv
from supabase_client import supabase
from config import BENCHMARK_SYMBOLS, FX_PAIRS

env_file = Path(__file__).parent / ".env.onadev"
if not env_file.exists():
    env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

HISTORY_PERIOD = "3y"
BATCH_SIZE = 500


def backfill():
    print(f"Backfilling {HISTORY_PERIOD} of price history...")

    # Collect symbols: user holdings + benchmarks + FX pairs
    response = supabase.table("user_holdings").select("symbol").execute()
    symbols = list({row["symbol"] for row in response.data})
    symbols.extend(BENCHMARK_SYMBOLS.keys())
    symbols.extend(FX_PAIRS.values())
    symbols = sorted(set(symbols))

    for symbol in symbols:
        try:
            hist = yf.Ticker(symbol).history(period=HISTORY_PERIOD)
            if hist.empty:
                print(f"No data for {symbol}")
                continue

            rows = []
            for date, row in hist.iterrows():
                rows.append({
                    "symbol": symbol,
                    "close_price": float(row["Close"]),
                    "updated_date": date.strftime("%Y-%m-%d"),
                })

            # Upsert in batches
            for i in range(0, len(rows), BATCH_SIZE):
                batch = rows[i : i + BATCH_SIZE]
                supabase.table("asset_prices").upsert(
                    batch, on_conflict="symbol,updated_date"
                ).execute()

            print(f"{symbol}: inserted {len(rows)} rows")
        except Exception as e:
            print(f"Error backfilling {symbol}: {e}")


if __name__ == "__main__":
    backfill()

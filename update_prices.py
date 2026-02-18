import yfinance as yf
from pathlib import Path
from dotenv import load_dotenv
from supabase_client import supabase
from config import BENCHMARK_SYMBOLS, FX_PAIRS
from datetime import datetime, timezone

# Load from .env.onadev or .env if present; in CI, env vars are injected directly
env_file = Path(__file__).parent / ".env.onadev"
if not env_file.exists():
    env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)


def _upsert_price(symbol: str, close_price: float, date_str: str):
    """Insert or update a single (symbol, date) price row."""
    supabase.table("asset_prices").upsert(
        {"symbol": symbol, "close_price": close_price, "updated_date": date_str},
        on_conflict="symbol,updated_date",
    ).execute()


def update_prices():
    print("Starting price update...")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Collect unique symbols across all users + benchmarks + FX pairs
    response = supabase.table("user_holdings").select("symbol").execute()
    symbols = list({row["symbol"] for row in response.data})
    symbols.extend(BENCHMARK_SYMBOLS.keys())
    symbols.extend(FX_PAIRS.values())
    symbols = list(set(symbols))

    for symbol in symbols:
        try:
            hist = yf.Ticker(symbol).history(period="1d")
            if hist.empty:
                print(f"No data for {symbol}")
                continue
            close_price = float(hist["Close"].iloc[-1])
            _upsert_price(symbol, close_price, today)
            print(f"Updated {symbol}: {close_price:.2f}")
        except Exception as e:
            print(f"Error updating {symbol}: {e}")


if __name__ == "__main__":
    update_prices()

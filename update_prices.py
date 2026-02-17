import yfinance as yf
from pathlib import Path
from dotenv import load_dotenv
from supabase_client import supabase
from config import PORTFOLIO_HOLDINGS
from datetime import datetime, timezone

# Load from .env.onadev or .env if present; in CI, env vars are injected directly
env_file = Path(__file__).parent / ".env.onadev"
if not env_file.exists():
    env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)


def update_prices():
    print("Starting price update...")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    symbols = list({h['symbol'] for h in PORTFOLIO_HOLDINGS})

    for symbol in symbols:
        try:
            hist = yf.Ticker(symbol).history(period="1d")
            if hist.empty:
                print(f"No data for {symbol}")
                continue
            close_price = float(hist['Close'].iloc[-1])

            existing = supabase.table('asset_prices') \
                .select("id") \
                .eq('symbol', symbol) \
                .execute()

            data = {
                'symbol': symbol,
                'close_price': close_price,
                'updated_date': today,
            }

            if existing.data:
                supabase.table('asset_prices') \
                    .update(data) \
                    .eq('symbol', symbol) \
                    .execute()
            else:
                supabase.table('asset_prices') \
                    .insert(data) \
                    .execute()

            print(f"Updated {symbol}: {close_price:.2f}")
        except Exception as e:
            print(f"Error updating {symbol}: {e}")


if __name__ == "__main__":
    update_prices()

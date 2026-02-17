import yfinance as yf
from pathlib import Path
from dotenv import load_dotenv
from supabase_client import supabase
from config import FX_PAIRS
from datetime import datetime, timezone

# Load from .env.onadev or .env if present; in CI, env vars are injected directly
env_file = Path(__file__).parent / ".env.onadev"
if not env_file.exists():
    env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)


def update_fx_rates():
    print("Starting FX rate update...")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for currency, pair in FX_PAIRS.items():
        try:
            hist = yf.Ticker(pair).history(period="1d")
            if hist.empty:
                print(f"No data for {pair}")
                continue
            rate = float(hist['Close'].iloc[-1])

            existing = supabase.table('fx_rates') \
                .select("id") \
                .eq('currency', currency) \
                .execute()

            data = {
                'currency': currency,
                'pair': pair,
                'rate_to_usd': rate,
                'updated_date': today,
            }

            if existing.data:
                supabase.table('fx_rates') \
                    .update(data) \
                    .eq('currency', currency) \
                    .execute()
            else:
                supabase.table('fx_rates') \
                    .insert(data) \
                    .execute()

            print(f"Updated {currency}/USD: {rate:.6f}")
        except Exception as e:
            print(f"Error updating {currency}: {e}")


if __name__ == "__main__":
    update_fx_rates()

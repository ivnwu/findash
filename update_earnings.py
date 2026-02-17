import yfinance as yf
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
from supabase_client import supabase
from config import TRACKED_SYMBOLS
import time
import os

# Load from .env.onadev or .env if present; in CI, env vars are injected directly
env_file = Path(__file__).parent / ".env.onadev"
if not env_file.exists():
    env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

def get_earnings_data(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    calendar = ticker.calendar

    if not calendar:
        return None

    return {
        'symbol': symbol,
        'company_name': info.get('longName', symbol),
        'earnings_date': str(calendar.get('Earnings Date', '')),
        'eps_estimate': calendar.get('EPS Estimate'),
        'revenue_estimate': calendar.get('Revenue Estimate') / 1e6 if calendar.get('Revenue Estimate') else None,
    }

def scrape_nasdaq_transcript(symbol):
    url = f"https://www.nasdaq.com/market-activity/stocks/{symbol.lower()}/earnings-call"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.content, 'html.parser')
        content = soup.find("div", class_="asset-stream-content")
        if content:
            text = content.get_text().strip()
            return text[:6000]
    except Exception as e:
        print(f"Scrape failed {symbol}: {e}")
    return None

def summarize_transcript(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a financial analyst. Summarize in 5 bullet points: revenue, earnings, guidance, risks, tone."},
                {"role": "user", "content": f"Summarize:\n\n{text}"}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "Summary failed."

def save_summary(data):
    existing = supabase.table('earnings_summaries') \
        .select("id") \
        .eq('symbol', data['symbol']) \
        .execute()

    if existing.data:
        supabase.table('earnings_summaries') \
            .update(data) \
            .eq('symbol', data['symbol']) \
            .execute()
    else:
        supabase.table('earnings_summaries') \
            .insert(data) \
            .execute()

def run_update():
    print("Starting earnings update...")
    for symbol in TRACKED_SYMBOLS:
        print(f"Processing {symbol}...")
        earnings = get_earnings_data(symbol)
        if not earnings:
            continue

        transcript = scrape_nasdaq_transcript(symbol)
        if not transcript:
            continue

        summary = summarize_transcript(transcript)
        data = {
            'symbol': symbol,
            'company_name': earnings['company_name'],
            'earnings_date': earnings['earnings_date'],
            'eps_estimate': earnings['eps_estimate'],
            'revenue_estimate': earnings['revenue_estimate'],
            'transcript_summary': summary
        }
        save_summary(data)
        print(f"✅ Updated {symbol}")
        time.sleep(15)

if __name__ == "__main__":
    run_update()

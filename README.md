# findash 💼

AI-powered financial dashboard. Tracks multi-currency portfolio value, margin loans, and earnings call summaries.

## Features

- Portfolio NAV with multi-currency support (USD, HKD, SGD)
- Live FX rates stored in Supabase, updated daily via GitHub Actions
- Margin loan tracking with FX conversion
- AI-generated earnings call summaries (GPT-4)
- Streamlit web dashboard

## Setup

### 1. Supabase

Create a project at [supabase.com](https://supabase.com) and run this SQL:

```sql
CREATE TABLE earnings_summaries (
  id SERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  company_name TEXT,
  earnings_date TEXT,
  eps_estimate NUMERIC,
  revenue_estimate NUMERIC,
  transcript_summary TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE fx_rates (
  id SERIAL PRIMARY KEY,
  currency TEXT NOT NULL UNIQUE,
  pair TEXT NOT NULL,
  rate_to_usd NUMERIC NOT NULL,
  updated_date TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. Clone & Configure

```bash
git clone https://github.com/ivnwu/findash.git
cd findash
cp .env.example .env
# Edit .env with your Supabase URL, Supabase anon key, and OpenAI API key
```

### 3. Install & Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

### 4. GitHub Actions

The workflow runs weekdays at 9am UTC and can be triggered manually. It:

1. Updates FX rates (HKD/USD, SGD/USD) from yfinance into Supabase
2. Fetches earnings data, scrapes transcripts, summarizes via GPT-4, and stores in Supabase

Add these as repository secrets (**Settings → Secrets → Actions**):

- `SUPABASE_URL`
- `SUPABASE_KEY` (anon public key, starts with `eyJ`)
- `OPENAI_API_KEY`

### 5. Portfolio Configuration

Edit `config.py` to set your holdings, margin loans, and tracked symbols. HKEX stocks use the `.HK` suffix (e.g., `9988.HK`). FX pairs are defined in `FX_PAIRS`.

## Project Structure

| File | Purpose |
|---|---|
| `app.py` | Streamlit dashboard |
| `portfolio.py` | Portfolio valuation, reads FX rates from Supabase |
| `config.py` | Holdings, margin loans, FX pairs, tracked symbols |
| `update_fx_rates.py` | Fetches FX rates from yfinance, stores in Supabase |
| `update_earnings.py` | Fetches earnings data, generates AI summaries |
| `supabase_client.py` | Supabase client initialization |

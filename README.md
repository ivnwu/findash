# findash 💼

**Your AI-powered financial dashboard.**  
Automatically tracks your portfolio value and summarizes earnings calls using AI.

---

## 🚀 Features

- ✅ **Net Asset Value (NAV)** of your portfolio
- ✅ **AI-generated summaries** of earnings call transcripts
- ✅ **Auto-updated daily** via GitHub Actions
- ✅ **Web-based dashboard** (runs on Render, Railway, or Streamlit)

---

## 🔧 Setup Guide

### 1. Create a Supabase Project
- Go to [https://supabase.com](https://supabase.com)
- Create a new project
- Get your **API URL** and **Anonymous Key**

#### Run This SQL:
\`\`\`sql
CREATE TABLE portfolio (
  id SERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  shares NUMERIC NOT NULL,
  purchase_price NUMERIC
);

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
\`\`\`

---

### 2. Clone & Configure
\`\`\`bash
git clone https://github.com/yourusername/findash.git
cd findash
cp .env.example .env
# Edit .env with your keys
\`\`\`

### 3. Install & Run
\`\`\`bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
\`\`\`

### 4. Deploy to Render
- Push to GitHub
- Deploy as Web Service
- Add secrets

### 5. Enable GitHub Actions
Add your API keys in GitHub Secrets.

---

**Made with ❤️ for busy tech professionals.**

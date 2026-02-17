import streamlit as st
from portfolio import get_portfolio_value
from supabase_client import supabase
import pandas as pd

st.set_page_config(page_title="💼 findash", layout="wide")
st.title("💼 findash")

st.markdown("**Your AI-powered financial dashboard**")

# --- Portfolio Section ---
st.header("📊 Portfolio Overview")
total_value, holdings = get_portfolio_value()

col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Net Asset Value", f"${total_value:,.2f}")

with col2:
    if holdings:
        df = pd.DataFrame(holdings)
        st.dataframe(df[['symbol', 'shares', 'current_price', 'value', 'gain_loss_pct']])

# --- Earnings Summaries ---
st.header("🎙️ Recent Earnings Summaries")
response = supabase.table('earnings_summaries') \
    .select("*") \
    .order('earnings_date', desc=True) \
    .limit(10) \
    .execute()

for row in response.data:
    with st.expander(f"**{row['symbol']}** – {row['company_name']} ({str(row['earnings_date'])[:10]})"):
        st.markdown(f"**EPS Estimate**: ${row['eps_estimate'] or 'N/A'}")
        rev = row['revenue_estimate']
        st.markdown(f"**Revenue Estimate**: \${rev:,.0f}M" if rev else "**Revenue Estimate**: N/A")
        st.markdown("---")
        st.markdown(row['transcript_summary'])

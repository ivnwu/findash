import streamlit as st
from portfolio import get_portfolio_value
from supabase_client import supabase
import pandas as pd

st.set_page_config(page_title="💼 findash", layout="wide")
st.title("💼 findash")

st.markdown("**Your AI-powered financial dashboard**")

# --- Portfolio Section ---
st.header("📊 Portfolio Overview")
nav, gross_value, holdings, loans, fx_rates, fx_updated, prices_updated = get_portfolio_value()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Net Asset Value", f"${nav:,.2f}")
with col2:
    st.metric("Gross Portfolio", f"${gross_value:,.2f}")
with col3:
    total_loans = sum(l['amount_usd'] for l in loans)
    st.metric("Margin Loans", f"${total_loans:,.2f}")

# Data freshness and FX rates
info_parts = []
if prices_updated:
    info_parts.append(f"Prices as of: {prices_updated}")
if fx_updated:
    rate_strs = [f"{k}/USD: {v:.4f}" for k, v in fx_rates.items() if k != "USD"]
    info_parts.append(f"FX rates as of: {fx_updated} ({' | '.join(rate_strs)})")
if info_parts:
    st.caption(" · ".join(info_parts))

# Holdings table
if holdings:
    df = pd.DataFrame(holdings)
    st.dataframe(df[['symbol', 'shares', 'currency', 'local_price', 'fx_rate', 'price_usd', 'value']])

# Margin loan details
if loans:
    st.subheader("Margin Loans")
    df_loans = pd.DataFrame(loans)
    st.dataframe(df_loans[['label', 'currency', 'amount_local', 'fx_rate', 'amount_usd']])

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

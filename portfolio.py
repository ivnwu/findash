import yfinance as yf
from supabase_client import supabase
from config import PORTFOLIO_HOLDINGS, MARGIN_LOANS


def get_fx_rates():
    """Read FX rates from Supabase (updated daily by CI)."""
    rates = {"USD": 1.0}
    try:
        response = supabase.table('fx_rates').select("currency, rate_to_usd").execute()
        for row in response.data:
            rates[row['currency']] = row['rate_to_usd']
    except Exception as e:
        print(f"Error reading FX rates from Supabase: {e}")
    return rates


def get_portfolio_value():
    fx_rates = get_fx_rates()
    total_value = 0
    detailed = []

    for h in PORTFOLIO_HOLDINGS:
        ticker = yf.Ticker(h['symbol'])
        try:
            hist = ticker.history(period="1d")
            if hist.empty:
                continue
            local_price = hist['Close'].iloc[-1]
            currency = h.get('currency', 'USD')
            fx_rate = fx_rates.get(currency, 1.0)
            price_usd = local_price * fx_rate
            value_usd = price_usd * h['shares']
            total_value += value_usd
            detailed.append({
                'symbol': h['symbol'],
                'shares': h['shares'],
                'currency': currency,
                'local_price': round(local_price, 2),
                'fx_rate': round(fx_rate, 6),
                'price_usd': round(price_usd, 2),
                'value': round(value_usd, 2),
            })
        except Exception as e:
            print(f"Error fetching {h['symbol']}: {e}")

    # Subtract margin loans
    total_loans_usd = 0
    loan_details = []
    for loan in MARGIN_LOANS:
        currency = loan['currency']
        fx_rate = fx_rates.get(currency, 1.0)
        amount_usd = loan['amount'] * fx_rate
        total_loans_usd += amount_usd
        loan_details.append({
            'label': loan['label'],
            'currency': currency,
            'amount_local': loan['amount'],
            'fx_rate': round(fx_rate, 6),
            'amount_usd': round(amount_usd, 2),
        })

    nav = round(total_value - total_loans_usd, 2)
    return nav, round(total_value, 2), detailed, loan_details, fx_rates

from supabase_client import supabase
from config import PORTFOLIO_HOLDINGS, MARGIN_LOANS


def get_fx_rates():
    """Read FX rates and their update date from Supabase."""
    rates = {"USD": 1.0}
    fx_updated = None
    try:
        response = supabase.table('fx_rates') \
            .select("currency, rate_to_usd, updated_date") \
            .execute()
        for row in response.data:
            rates[row['currency']] = row['rate_to_usd']
            if row.get('updated_date'):
                fx_updated = row['updated_date']
    except Exception as e:
        print(f"Error reading FX rates from Supabase: {e}")
    return rates, fx_updated


def get_asset_prices():
    """Read daily close prices and their update date from Supabase."""
    prices = {}
    prices_updated = None
    try:
        response = supabase.table('asset_prices') \
            .select("symbol, close_price, updated_date") \
            .execute()
        for row in response.data:
            prices[row['symbol']] = row['close_price']
            if row.get('updated_date'):
                prices_updated = row['updated_date']
    except Exception as e:
        print(f"Error reading asset prices from Supabase: {e}")
    return prices, prices_updated


def get_portfolio_value():
    fx_rates, fx_updated = get_fx_rates()
    prices, prices_updated = get_asset_prices()
    total_value = 0
    detailed = []

    for h in PORTFOLIO_HOLDINGS:
        symbol = h['symbol']
        local_price = prices.get(symbol)
        if local_price is None:
            print(f"No price data for {symbol}")
            continue
        currency = h.get('currency', 'USD')
        fx_rate = fx_rates.get(currency, 1.0)
        price_usd = local_price * fx_rate
        value_usd = price_usd * h['shares']
        total_value += value_usd
        detailed.append({
            'symbol': symbol,
            'shares': h['shares'],
            'currency': currency,
            'local_price': round(local_price, 2),
            'fx_rate': round(fx_rate, 6),
            'price_usd': round(price_usd, 2),
            'value': round(value_usd, 2),
        })

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
    return nav, round(total_value, 2), detailed, loan_details, fx_rates, fx_updated, prices_updated

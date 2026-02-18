from supabase_client import supabase


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
    """Read the latest close price per symbol from Supabase."""
    prices = {}
    prices_updated = None
    try:
        # Order by date desc so the first row per symbol is the latest
        response = supabase.table('asset_prices') \
            .select("symbol, close_price, updated_date") \
            .order("updated_date", desc=True) \
            .execute()
        for row in response.data:
            sym = row['symbol']
            if sym not in prices:
                prices[sym] = row['close_price']
                if row.get('updated_date'):
                    prices_updated = row['updated_date']
    except Exception as e:
        print(f"Error reading asset prices from Supabase: {e}")
    return prices, prices_updated


def get_user_holdings(user_id: int) -> list[dict]:
    """Fetch holdings for a given user from Supabase."""
    response = (
        supabase.table("user_holdings")
        .select("symbol, shares, currency")
        .eq("user_id", user_id)
        .execute()
    )
    return response.data


def get_user_margin_loans(user_id: int) -> list[dict]:
    """Fetch margin loans for a given user from Supabase."""
    response = (
        supabase.table("user_margin_loans")
        .select("label, currency, amount")
        .eq("user_id", user_id)
        .execute()
    )
    return response.data


def get_portfolio_value(user_id: int):
    fx_rates, fx_updated = get_fx_rates()
    prices, prices_updated = get_asset_prices()

    holdings_data = get_user_holdings(user_id)
    loans_data = get_user_margin_loans(user_id)

    total_value = 0
    detailed = []

    for h in holdings_data:
        symbol = h['symbol']
        local_price = prices.get(symbol)
        if local_price is None:
            print(f"No price data for {symbol}")
            continue
        currency = h.get('currency', 'USD')
        fx_rate = fx_rates.get(currency, 1.0)
        price_usd = local_price * fx_rate
        shares = float(h['shares'])
        value_usd = price_usd * shares
        total_value += value_usd
        detailed.append({
            'symbol': symbol,
            'shares': shares,
            'currency': currency,
            'local_price': round(local_price, 2),
            'fx_rate': round(fx_rate, 6),
            'price_usd': round(price_usd, 2),
            'value': round(value_usd, 2),
        })

    total_loans_usd = 0
    loan_details = []
    for loan in loans_data:
        currency = loan['currency']
        fx_rate = fx_rates.get(currency, 1.0)
        amount = float(loan['amount'])
        amount_usd = amount * fx_rate
        total_loans_usd += amount_usd
        loan_details.append({
            'label': loan['label'],
            'currency': currency,
            'amount_local': amount,
            'fx_rate': round(fx_rate, 6),
            'amount_usd': round(amount_usd, 2),
        })

    nav = round(total_value - total_loans_usd, 2)
    return nav, round(total_value, 2), detailed, loan_details, fx_rates, fx_updated, prices_updated

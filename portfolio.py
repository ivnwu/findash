import yfinance as yf
from supabase_client import supabase
from config import PORTFOLIO_HOLDINGS, HKD_USD_RATE

def get_portfolio_value():
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
            fx_rate = HKD_USD_RATE if currency == 'HKD' else 1.0
            price_usd = local_price * fx_rate
            value_usd = price_usd * h['shares']
            total_value += value_usd
            detailed.append({
                'symbol': h['symbol'],
                'shares': h['shares'],
                'currency': currency,
                'local_price': round(local_price, 2),
                'price_usd': round(price_usd, 2),
                'value': round(value_usd, 2),
            })
        except Exception as e:
            print(f"Error fetching {h['symbol']}: {e}")

    return round(total_value, 2), detailed

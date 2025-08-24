import yfinance as yf
from supabase_client import supabase
from config import PORTFOLIO_HOLDINGS

def get_portfolio_value():
    total_value = 0
    detailed = []

    for h in PORTFOLIO_HOLDINGS:
        ticker = yf.Ticker(h['symbol'])
        try:
            hist = ticker.history(period="1d")
            if hist.empty:
                continue
            current_price = hist['Close'].iloc[-1]
            value = current_price * h['shares']
            total_value += value
            gain_loss = value - (h['shares'] * h['purchase_price'])
            detailed.append({
                'symbol': h['symbol'],
                'shares': h['shares'],
                'purchase_price': round(h['purchase_price'], 2),
                'current_price': round(current_price, 2),
                'value': round(value, 2),
                'gain_loss': round(gain_loss, 2),
                'gain_loss_pct': round((gain_loss / (h['shares'] * h['purchase_price'])) * 100, 2)
            })
        except Exception as e:
            print(f"Error fetching {h['symbol']}: {e}")

    return round(total_value, 2), detailed

"""Portfolio performance vs benchmarks over selectable time periods."""

from datetime import date, timedelta
import pandas as pd
from supabase_client import supabase
from config import BENCHMARK_SYMBOLS


PERIOD_DAYS = {
    "1W": 7,
    "1M": 30,
    "YTD": None,  # computed dynamically
    "1Y": 365,
    "3Y": 3 * 365,
}


def _start_date_for_period(period: str) -> date:
    today = date.today()
    if period == "YTD":
        return date(today.year, 1, 1)
    return today - timedelta(days=PERIOD_DAYS[period])


def _fetch_prices(symbols: list[str], start: date) -> pd.DataFrame:
    """Fetch daily prices from asset_prices for given symbols from start date."""
    start_str = start.isoformat()
    rows = []
    # Supabase has a default 1000-row limit; paginate per symbol
    for symbol in symbols:
        response = (
            supabase.table("asset_prices")
            .select("symbol, close_price, updated_date")
            .eq("symbol", symbol)
            .gte("updated_date", start_str)
            .order("updated_date")
            .execute()
        )
        rows.extend(response.data)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["updated_date"] = pd.to_datetime(df["updated_date"])
    df = df.pivot(index="updated_date", columns="symbol", values="close_price")
    df.sort_index(inplace=True)
    return df


def _fetch_fx_history(start: date) -> pd.DataFrame:
    """Fetch historical FX rates from asset_prices.

    FX pairs are stored as yfinance tickers (e.g. HKDUSD=X).
    Returns a DataFrame indexed by date with columns = currency code,
    values = rate to USD.
    """
    from config import FX_PAIRS

    fx_tickers = list(FX_PAIRS.values())
    ticker_to_ccy = {v: k for k, v in FX_PAIRS.items()}

    df = _fetch_prices(fx_tickers, start)
    if df.empty:
        return df
    df.rename(columns=ticker_to_ccy, inplace=True)
    df["USD"] = 1.0
    return df


def get_performance(user_id: int, period: str) -> pd.DataFrame | None:
    """Return a DataFrame with indexed (base-100) daily returns.

    Columns: 'Portfolio', plus one per benchmark.
    Index: date.
    """
    start = _start_date_for_period(period)

    # User holdings
    response = (
        supabase.table("user_holdings")
        .select("symbol, shares, currency")
        .eq("user_id", user_id)
        .execute()
    )
    holdings = response.data
    if not holdings:
        return None

    holding_symbols = list({h["symbol"] for h in holdings})
    benchmark_symbols = list(BENCHMARK_SYMBOLS.keys())
    all_symbols = list(set(holding_symbols + benchmark_symbols))

    prices = _fetch_prices(all_symbols, start)
    if prices.empty or len(prices) < 2:
        return None

    # FX history for non-USD holdings
    currencies_needed = {h["currency"] for h in holdings if h["currency"] != "USD"}
    fx_df = pd.DataFrame(index=prices.index)
    fx_df["USD"] = 1.0
    if currencies_needed:
        fx_hist = _fetch_fx_history(start)
        if not fx_hist.empty:
            # Drop USD from fx_hist to avoid overlap
            fx_hist = fx_hist.drop(columns=["USD"], errors="ignore")
            fx_df = fx_df.join(fx_hist, how="left")
    fx_df.ffill(inplace=True)
    fx_df.bfill(inplace=True)

    # Compute daily portfolio value in USD
    portfolio_value = pd.Series(0.0, index=prices.index)
    for h in holdings:
        sym = h["symbol"]
        if sym not in prices.columns:
            continue
        ccy = h.get("currency", "USD")
        shares = float(h["shares"])
        fx_col = fx_df[ccy] if ccy in fx_df.columns else 1.0
        portfolio_value += prices[sym] * fx_col * shares

    # Drop rows where portfolio value is 0 (missing data at start)
    portfolio_value = portfolio_value[portfolio_value > 0]
    if len(portfolio_value) < 2:
        return None

    # Percentage change from period start
    result = pd.DataFrame(index=portfolio_value.index)
    result["Portfolio"] = (portfolio_value / portfolio_value.iloc[0] - 1) * 100

    for sym in benchmark_symbols:
        if sym in prices.columns:
            series = prices[sym].reindex(result.index).ffill().bfill()
            if series.iloc[0] > 0:
                result[BENCHMARK_SYMBOLS[sym]] = (series / series.iloc[0] - 1) * 100

    return result

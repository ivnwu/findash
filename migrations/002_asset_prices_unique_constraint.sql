-- Allow multiple dated rows per symbol instead of one row per symbol.
-- Add unique constraint so upsert on (symbol, updated_date) works.
CREATE UNIQUE INDEX IF NOT EXISTS asset_prices_symbol_date_idx
    ON asset_prices (symbol, updated_date);

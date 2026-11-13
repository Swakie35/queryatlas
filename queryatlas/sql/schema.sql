PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS dim_site (
  site_id INTEGER PRIMARY KEY,
  site_name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS dim_product (
  product_id INTEGER PRIMARY KEY,
  product_name TEXT NOT NULL UNIQUE,
  category TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS fact_sales_events (
  event_id TEXT PRIMARY KEY,
  event_day TEXT NOT NULL CHECK (event_day GLOB '????-??-??'),
  site_id INTEGER NOT NULL REFERENCES dim_site(site_id),
  product_id INTEGER NOT NULL REFERENCES dim_product(product_id),
  customer_key TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('SALE','REFUND')),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price_pence INTEGER NOT NULL CHECK (unit_price_pence >= 0),
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_event_site_day ON fact_sales_events(site_id,event_day);
CREATE INDEX IF NOT EXISTS idx_event_customer_day ON fact_sales_events(customer_key,event_day);
CREATE INDEX IF NOT EXISTS idx_event_product_day ON fact_sales_events(product_id,event_day);

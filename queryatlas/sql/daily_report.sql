-- Periodic site/day aggregates. All currency is stored as integer pence.
WITH daily AS (
  SELECT e.site_id, s.site_name, e.event_day,
         COUNT(*) AS events,
         SUM(CASE WHEN e.kind='SALE' THEN e.quantity*e.unit_price_pence ELSE -e.quantity*e.unit_price_pence END) AS net_revenue_pence,
         SUM(CASE WHEN e.kind='REFUND' THEN 1 ELSE 0 END) AS refund_events,
         COUNT(DISTINCT e.customer_key) AS distinct_customers
  FROM fact_sales_events e JOIN dim_site s USING(site_id)
  GROUP BY e.site_id, s.site_name, e.event_day
), enriched AS (
  SELECT d.*,
         SUM(net_revenue_pence) OVER (PARTITION BY site_id ORDER BY event_day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7_active_day_revenue_pence,
         DENSE_RANK() OVER (PARTITION BY event_day ORDER BY net_revenue_pence DESC) AS daily_revenue_rank
  FROM daily d
)
SELECT site_id, site_name,event_day,events,net_revenue_pence,refund_events,distinct_customers,
       rolling_7_active_day_revenue_pence,daily_revenue_rank
FROM enriched
ORDER BY event_day,site_id;

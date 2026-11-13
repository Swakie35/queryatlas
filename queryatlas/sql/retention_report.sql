-- A customer's cohort is their first observed SALE (refund-only keys excluded).
WITH first_sale AS (
 SELECT customer_key, MIN(event_day) AS cohort_day
 FROM fact_sales_events WHERE kind='SALE' GROUP BY customer_key
), activity AS (
 SELECT e.customer_key,f.cohort_day,e.event_day
 FROM fact_sales_events e JOIN first_sale f USING (customer_key)
 WHERE e.kind='SALE' AND e.event_day>f.cohort_day
 GROUP BY e.customer_key,f.cohort_day,e.event_day
)
SELECT f.cohort_day,COUNT(DISTINCT f.customer_key) AS cohort_size,
       COUNT(DISTINCT a.customer_key) AS returning_customers
FROM first_sale f LEFT JOIN activity a ON a.customer_key=f.customer_key
GROUP BY f.cohort_day ORDER BY f.cohort_day;

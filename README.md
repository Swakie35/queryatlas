# QueryAtlas

[![CI](https://github.com/Swakie35/queryatlas/actions/workflows/ci.yml/badge.svg)](https://github.com/Swakie35/queryatlas/actions/workflows/ci.yml)

**A small warehouse you can actually run, inspect and explain.**

I use this project to show the SQL decisions that matter between raw operational events and reporting: dimensional modelling, input contracts, idempotent loads, integer currency, refund netting, indexes and useful analytical window functions.

## Inside
- Site and product dimensions, transactional fact table, foreign keys and composite indexes
- Deterministic synthetic sales/refund stream; repeatable `UPSERT` ingestion using source `event_id`
- Daily revenue and refund metrics with `DENSE_RANK()` and 7-active-day window sums
- First-sale cohort and return-customer reporting via common table expressions
- CSV reports, CLI, tests; no paid warehouse or external database required

## Try it
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[test]'
python -m queryatlas --db warehouse.sqlite --out reports/generated/daily.csv
pytest -q
```
The CLI also writes `retention.csv`. Rerunning doesn't duplicate facts because event IDs are stable. Open `queryatlas/sql` to review the queries themselves.

## Trade-offs and next steps
SQLite is used for immediate execution, not to claim a production-scale warehouse. The rolling query is seven **active dates**, not guaranteed seven consecutive calendar days if some days are missing. Cohorts use first *observed* sale, not a verified lifetime customer history. A deployed build would move to PostgreSQL or an analytics warehouse, use batch audit tables and watermarks, support late-arriving dimensions and event deletion, add schema contracts, and benchmark query plans under real volumes. Customer keys and data here are invented for the demo.

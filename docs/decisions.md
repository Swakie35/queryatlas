# Design notes — queryatlas

**Why this exists.** A small, executable analytics warehouse with incremental upserts, star schema and window-function reports.

The default implementation is intentionally self-contained so reviewers can run it without private services, paid accounts or unpublished data. The README names its limitations; this project is an engineering reference, not a claim about production deployment.

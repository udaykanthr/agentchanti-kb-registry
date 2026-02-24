---
id: "beh-005"
title: "Performance Review Instructions"
category: "behavioral"
language: "all"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - performance
  - behavioral
  - n+1
  - database
  - profiling
  - caching
---

# Performance Review Instructions

When reviewing code for performance, follow these instructions exactly.

## Always Check

- **N+1 query patterns**: A loop that makes a database query inside each iteration is always N+1. Flag every ORM access inside a loop unless the loop body explicitly limits to a fixed, small N.
- **Missing database indexes on filtered/joined columns**: Any column used in a WHERE, JOIN ON, or ORDER BY clause without an index on a large table is a potential full-table scan. Flag with column name and estimated table size if visible.
- **Unbounded queries (no LIMIT)**: Any query that fetches all records from a large table without pagination. Flag as HIGH impact if the table could have thousands of rows.
- **Loading full objects when only fields are needed**: Using `SELECT *` (or ORM equivalent loading full models) when only 1-2 fields are needed. Suggest `.values()`, `values_list()`, or projection queries.
- **Synchronous I/O in async context**: A blocking call (requests.get, open(), time.sleep()) inside an async function blocks the event loop. Flag as [CRITICAL] — it defeats the purpose of async.

## Always Flag with Estimated Impact (HIGH/MEDIUM/LOW)

Format: `[PERF:HIGH|MEDIUM|LOW] description → suggested fix`

- **HIGH**: N+1 queries in a response handler, unbounded queries on tables with 10k+ rows, sync I/O in async code, missing index on a heavily queried column.
- **MEDIUM**: Repeated identical computation in a loop that could be memoized, loading 10-100 full objects when only IDs are needed, unindexed sort on a medium table.
- **LOW**: Minor: slightly inefficient algorithm that works fine at current scale, missing cache on a non-hot path, suboptimal string concatenation in a non-hot loop.

## Never

- **Never micro-optimize without profiling data.** Do not suggest changing `for i in range(len(x))` to `enumerate(x)` as a performance improvement — it makes zero practical difference. Reserve performance suggestions for measurable bottlenecks.
- **Never add caching without noting the invalidation strategy.** Every cache suggestion must include: when is this cache invalidated? What happens if stale data is served?
- **Never suggest an index on every column.** Indexes have write overhead. Suggest indexes only on: columns used in WHERE/JOIN/ORDER BY on large tables, columns with high cardinality, and foreign keys.

## Suggest Profiling First for HIGH Impact Items

Before implementing a fix for a HIGH impact item, suggest:
- Python: `cProfile`, `line_profiler`, `py-spy`, or Django Debug Toolbar (for DB queries)
- JavaScript/Node.js: `clinic.js`, `--prof` flag, browser DevTools Performance tab
- Database: `EXPLAIN ANALYZE` (PostgreSQL), `EXPLAIN` (MySQL/SQLite)

Format: `[PERF:HIGH] N+1 in UserListView: each user triggers a profile query → Confirm with Django Debug Toolbar, then add select_related('profile')`

## Performance Review Output Format

```
## Performance Review: `get_dashboard_data()`

[PERF:HIGH] N+1 query: `user.orders.all()` inside the users loop (line 34)
→ Confirm: run Django Debug Toolbar and count queries on this view
→ Fix: Use `users = User.objects.prefetch_related('orders').filter(...)`

[PERF:HIGH] Unbounded query: `Article.objects.filter(status='published')` with no LIMIT (line 12)
→ Fix: Add `.order_by('-created_at')[:50]` or implement pagination

[PERF:MEDIUM] Full User objects loaded when only user.id needed (line 45)
→ Fix: `User.objects.filter(...).values_list('id', flat=True)`

[PERF:LOW] `title.upper()` called twice per item in the loop (line 67)
→ Fix: Store result in a variable: `upper_title = title.upper()`
```

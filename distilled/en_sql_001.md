# SQL Query Optimization Examples

## Topic: Index Optimization

### Problem
A query filtering on a non-indexed column performs a full table scan, causing poor performance on large datasets.

```sql
-- Slow query (no index)
SELECT order_id, customer_id, order_date, total_amount
FROM orders
WHERE customer_id = 12345;
```

### Solution
```sql
-- Create a targeted index for frequently queried columns
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- For composite queries, use a composite index
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);

-- Optimized query now uses index scan instead of table scan
SELECT order_id, customer_id, order_date, total_amount
FROM orders
WHERE customer_id = 12345;
```

### Explanation
Without an index, the database must scan every row in the table to find matching records (O(n) complexity). With a B-tree index on `customer_id`, the database can locate matching rows in O(log n) time. Composite indexes further optimize queries that filter on multiple columns by allowing index-only scans. The index acts like a sorted lookup table, dramatically reducing I/O operations and improving query response time from seconds to milliseconds on large tables.

---

## Topic: JOIN vs Subquery

### Problem
Using a subquery in the WHERE clause with IN operator causes the database to execute the subquery for each row, leading to poor performance.

```sql
-- Slow query with correlated subquery
SELECT o.order_id, o.order_date, o.total_amount
FROM orders o
WHERE o.customer_id IN (
    SELECT c.customer_id
    FROM customers c
    WHERE c.status = 'active'
    AND c.registration_date > '2023-01-01'
);
```

### Solution
```sql
-- Optimized query using JOIN
SELECT o.order_id, o.order_date, o.total_amount
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
WHERE c.status = 'active'
AND c.registration_date > '2023-01-01';

-- Alternative using EXISTS (often faster than IN)
SELECT o.order_id, o.order_date, o.total_amount
FROM orders o
WHERE EXISTS (
    SELECT 1
    FROM customers c
    WHERE c.customer_id = o.customer_id
    AND c.status = 'active'
    AND c.registration_date > '2023-01-01'
);
```

### Explanation
JOIN operations allow the query optimizer to choose the most efficient join algorithm (nested loop, hash join, or merge join) based on table statistics and available indexes. The database can also better parallelize JOIN operations. Subqueries with IN often execute once per row (correlated subquery) or create temporary tables, adding overhead. EXISTS is often faster than IN because it can short-circuit evaluation once a match is found, and the query optimizer can transform it into a semi-join internally.

---

## Topic: Query Execution Plan Analysis

### Problem
A query appears simple but runs slowly due to implicit type conversion preventing index usage.

```sql
-- Slow query (type mismatch)
SELECT id, name, email, created_at
FROM users
WHERE phone_number = 5551234567;  -- phone_number is VARCHAR
```

### Solution
```sql
-- Step 1: Analyze the execution plan
EXPLAIN ANALYZE
SELECT id, name, email, created_at
FROM users
WHERE phone_number = 5551234567;

-- Step 2: Fix type mismatch
SELECT id, name, email, created_at
FROM users
WHERE phone_number = '5551234567';  -- Now matches VARCHAR type

-- Step 3: Verify index usage in execution plan
EXPLAIN ANALYZE
SELECT id, name, email, created_at
FROM users
WHERE phone_number = '5551234567';
```

### Explanation
The execution plan reveals that implicit type conversion forces the database to convert `phone_number` from VARCHAR to numeric for every row, preventing index usage and causing a full table scan. By using the correct type (string literal with quotes), the database can use the index on `phone_number`. Key execution plan indicators to watch for: "Seq Scan" (slow) vs "Index Scan" (fast), "Filter" conditions that reduce rows early, and "Nested Loop" vs "Hash Join" for multi-table queries. Always use EXPLAIN ANALYZE to understand actual execution costs, not just estimated plans.

---

## Topic: Pagination Optimization

### Problem
Traditional OFFSET-based pagination becomes exponentially slower as you navigate to later pages because the database must scan and discard all previous rows.

```sql
-- Slow pagination for deep pages
SELECT id, title, created_at, author_id
FROM articles
ORDER BY created_at DESC, id DESC
LIMIT 20 OFFSET 100000;  -- Scans 100,020 rows, discards 100,000
```

### Solution
```sql
-- Optimized pagination using cursor/seek method
-- First page
SELECT id, title, created_at, author_id
FROM articles
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Subsequent pages (using last seen values)
-- If last row had: created_at = '2024-01-15 10:30:00', id = 45678
SELECT id, title, created_at, author_id
FROM articles
WHERE created_at < '2024-01-15 10:30:00'
   OR (created_at = '2024-01-15 10:30:00' AND id < 45678)
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Create supporting index
CREATE INDEX idx_articles_pagination ON articles(created_at DESC, id DESC);
```

### Explanation
Cursor-based pagination (also called "seek method" or "keyset pagination") uses WHERE clauses to skip directly to the desired position, eliminating the need to scan and discard rows. This provides O(1) performance regardless of page depth, whereas OFFSET pagination is O(n). The composite condition handles ties in `created_at` by using the unique `id` as a tiebreaker. The supporting index allows the database to seek directly to the starting position. This technique is especially critical for infinite scroll implementations and APIs supporting deep pagination.

---

## Topic: Aggregation Performance

### Problem
Multiple aggregate functions on the same dataset cause repeated table scans and calculations, and aggregating before filtering creates unnecessary work.

```sql
-- Slow query: aggregates entire table, then filters
SELECT 
    DATE(created_at) as order_date,
    COUNT(*) as total_orders,
    SUM(total_amount) as revenue,
    AVG(total_amount) as avg_order_value
FROM orders
HAVING COUNT(*) > 100
ORDER BY order_date DESC;

-- Multiple separate aggregation queries
SELECT COUNT(*) FROM orders WHERE status = 'completed';
SELECT SUM(total_amount) FROM orders WHERE status = 'completed';
SELECT AVG(total_amount) FROM orders WHERE status = 'completed';
```

### Solution
```sql
-- Optimized: Filter before aggregation
SELECT 
    DATE(created_at) as order_date,
    COUNT(*) as total_orders,
    SUM(total_amount) as revenue,
    AVG(total_amount) as avg_order_value
FROM orders
WHERE created_at >= '2024-01-01'  -- Filter early
GROUP BY DATE(created_at)
HAVING COUNT(*) > 100
ORDER BY order_date DESC;

-- Single query for multiple aggregates
SELECT 
    COUNT(*) as total_orders,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
    SUM(CASE WHEN status = 'completed' THEN total_amount ELSE 0 END) as completed_revenue
FROM orders
WHERE created_at >= '2024-01-01';

-- Create supporting index
CREATE INDEX idx_orders_created_at ON orders(created_at);
```

### Explanation
Filtering early (WHERE clause) reduces the dataset before aggregation, minimizing the work the database must perform. The WHERE clause filters rows before grouping, while HAVING filters groups after aggregation—use WHERE whenever possible for better performance. Combining multiple aggregations into a single query using CASE expressions allows the database to compute all values in a single table scan instead of multiple scans. The index on `created_at` enables efficient filtering of recent data. For time-series aggregations, consider materialized views or summary tables that pre-aggregate data for common queries, updating them periodically instead of recalculating from raw data.

---

## Summary

These optimization techniques address common performance bottlenecks:

1. **Index Optimization**: Reduces O(n) scans to O(log n) lookups
2. **JOIN vs Subquery**: Enables better query planning and execution strategies
3. **Execution Plan Analysis**: Identifies hidden performance killers like type mismatches
4. **Cursor Pagination**: Eliminates OFFSET overhead for deep pagination
5. **Smart Aggregation**: Minimizes data scanned and calculations performed

Always measure performance before and after optimizations using EXPLAIN ANALYZE, and remember that the best optimization often comes from understanding your data distribution and query patterns.

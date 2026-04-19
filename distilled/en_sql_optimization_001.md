# SQL Query Optimization Techniques

## Problem

Demonstrate SQL query optimization strategies including index usage, query rewriting, execution plan analysis, and performance tuning.

## Implementation

```sql
-- Setup: Create sample database schema
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    total_amount DECIMAL(10, 2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer_id (customer_id),
    INDEX idx_created_at (created_at),
    INDEX idx_status (status)
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER,
    quantity INTEGER,
    unit_price DECIMAL(10, 2),
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id)
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    category VARCHAR(50),
    price DECIMAL(10, 2),
    stock INTEGER,
    INDEX idx_category (category)
);

-- ============================================
-- OPTIMIZATION TECHNIQUES
-- ============================================

-- 1. EXPLAIN ANALYZE for Query Analysis
EXPLAIN ANALYZE
SELECT c.name, COUNT(o.id) as order_count
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name
HAVING COUNT(o.id) > 5;

-- 2. Index-Friendly Queries
-- BAD: Function on indexed column prevents index usage
SELECT * FROM orders 
WHERE DATE(created_at) = '2024-01-15';

-- GOOD: Range query uses index
SELECT * FROM orders 
WHERE created_at >= '2024-01-15 00:00:00' 
  AND created_at < '2024-01-16 00:00:00';

-- 3. Covering Index (Include all columns in index)
-- Create composite index for common query
CREATE INDEX idx_orders_status_date_amount 
ON orders(status, created_at, total_amount);

-- Query can be satisfied entirely from index
SELECT status, created_at, total_amount
FROM orders
WHERE status = 'completed'
ORDER BY created_at DESC;

-- 4. Avoid SELECT *
-- BAD: Fetches all columns
SELECT * FROM customers WHERE id = 1;

-- GOOD: Fetch only needed columns
SELECT id, name, email FROM customers WHERE id = 1;

-- 5. EXISTS vs IN for Subqueries
-- Often EXISTS is more efficient for correlated subqueries
SELECT c.id, c.name
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.customer_id = c.id 
    AND o.total_amount > 1000
);

-- 6. JOIN Optimization
-- Put smallest table first, filter early
SELECT c.name, o.id, o.total_amount
FROM orders o
INNER JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'completed'
  AND o.created_at >= '2024-01-01'
ORDER BY o.total_amount DESC
LIMIT 100;

-- 7. Window Functions for Analytics
-- Avoid self-joins for running calculations
SELECT 
    id,
    customer_id,
    total_amount,
    SUM(total_amount) OVER (
        PARTITION BY customer_id 
        ORDER BY created_at
    ) as running_total,
    AVG(total_amount) OVER (
        PARTITION BY customer_id
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) as moving_avg
FROM orders;

-- 8. Common Table Expressions (CTE) for Readability
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', created_at) as month,
        SUM(total_amount) as total
    FROM orders
    WHERE status = 'completed'
    GROUP BY DATE_TRUNC('month', created_at)
),
avg_sales AS (
    SELECT AVG(total) as avg_monthly FROM monthly_sales
)
SELECT 
    m.month,
    m.total,
    a.avg_monthly,
    (m.total - a.avg_monthly) / a.avg_monthly * 100 as pct_diff
FROM monthly_sales m
CROSS JOIN avg_sales a
ORDER BY m.month;

-- 9. Pagination Optimization
-- BAD: OFFSET with large values
SELECT * FROM orders 
ORDER BY created_at DESC 
LIMIT 20 OFFSET 100000;

-- GOOD: Cursor-based pagination
SELECT * FROM orders 
WHERE created_at < '2024-01-01'
ORDER BY created_at DESC 
LIMIT 20;

-- 10. Batch Operations
-- Insert multiple rows at once
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
VALUES 
    (1, 101, 2, 29.99),
    (1, 102, 1, 49.99),
    (1, 103, 3, 9.99);

-- 11. Avoid N+1 Query Problem
-- Use JOIN or subquery instead of multiple queries
SELECT 
    c.id,
    c.name,
    COALESCE(order_summary.total_orders, 0) as total_orders,
    COALESCE(order_summary.total_spent, 0) as total_spent
FROM customers c
LEFT JOIN (
    SELECT 
        customer_id,
        COUNT(*) as total_orders,
        SUM(total_amount) as total_spent
    FROM orders
    GROUP BY customer_id
) order_summary ON order_summary.customer_id = c.id;

-- 12. Index on Expression
CREATE INDEX idx_orders_year ON orders (EXTRACT(YEAR FROM created_at));

-- 13. Partial Index for Specific Conditions
CREATE INDEX idx_orders_pending_high_value 
ON orders(total_amount) 
WHERE status = 'pending' AND total_amount > 1000;

-- 14. UNION ALL vs UNION
-- UNION ALL is faster when duplicates don't matter
SELECT id, name FROM products WHERE category = 'electronics'
UNION ALL
SELECT id, name FROM products WHERE stock < 10;

-- 15. ANALYZE Tables Regularly
ANALYZE customers;
ANALYZE orders;
ANALYZE order_items;
ANALYZE products;

-- ============================================
-- TESTS (Using assertions in queries)
-- ============================================

-- Test 1: Index usage verification
EXPLAIN (COSTS OFF) 
SELECT * FROM orders WHERE customer_id = 1;
-- Expected: "Index Scan" not "Seq Scan"

-- Test 2: Composite index order matters
CREATE INDEX idx_test ON orders (status, created_at);
-- Query uses full composite index
SELECT * FROM orders WHERE status = 'completed' AND created_at > '2024-01-01';
-- Query uses only first column of index
SELECT * FROM orders WHERE status = 'completed';

-- Test 3: Subquery optimization
-- Correlated subquery (slow)
SELECT c.name,
    (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id)
FROM customers c;

-- JOIN alternative (fast)
SELECT c.name, COALESCE(o.order_count, 0) as order_count
FROM customers c
LEFT JOIN (
    SELECT customer_id, COUNT(*) as order_count
    FROM orders
    GROUP BY customer_id
) o ON o.customer_id = c.id;
```

## Query Performance Checklist

| Technique | When to Use | Impact |
|-----------|-------------|--------|
| Index columns | WHERE, JOIN, ORDER BY | High |
| Covering index | Frequently accessed columns | High |
| Batch operations | Bulk inserts/updates | High |
| EXISTS vs IN | Correlated subqueries | Medium |
| Partial index | Subset of rows queried | Medium |
| CTE | Complex queries | Medium |
| Window functions | Running calculations | High |

## Index Design Principles

1. **Order matters**: Put equality columns first, range columns second
2. **Selectivity**: High cardinality columns benefit most from indexes
3. **Coverage**: Include columns in index to avoid table lookups
4. **Maintenance**: Indexes slow writes, create only necessary ones
5. **Monitor**: Use `EXPLAIN ANALYZE` to verify index usage

## Key Metrics

- **Seq Scan**: Sequential scan (slow for large tables)
- **Index Scan**: Index lookup (fast)
- **Bitmap Scan**: Combination of index + table scan
- **Hash Join**: Memory-based join (fast for small tables)
- **Merge Join**: Sorted join (fast for large sorted datasets)

# SQL Indexing Strategies

## Problem

Implement comprehensive indexing strategies for database performance optimization, including composite indexes, partial indexes, and index maintenance.

## Implementation

```sql
-- ============================================
-- INDEX TYPES AND STRATEGIES
-- ============================================

-- Sample Schema
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    country VARCHAR(2),
    subscription_tier VARCHAR(20)
);

CREATE TABLE user_activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    activity_type VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 1. B-Tree Index (Default)
-- Good for: equality, range, prefix queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- 2. Composite Index (Multi-column)
-- Order matters: equality → range → sort
CREATE INDEX idx_users_country_tier_active 
ON users(country, subscription_tier, is_active);

-- Query uses full index
SELECT * FROM users 
WHERE country = 'US' 
  AND subscription_tier = 'premium' 
  AND is_active = true;

-- Query uses first two columns
SELECT * FROM users 
WHERE country = 'US' 
  AND subscription_tier = 'premium';

-- Query uses only first column
SELECT * FROM users WHERE country = 'US';

-- 3. Partial Index
-- Index only subset of rows
CREATE INDEX idx_users_premium 
ON users(created_at DESC) 
WHERE subscription_tier = 'premium';

-- Only indexes premium users, saving space
SELECT * FROM users 
WHERE subscription_tier = 'premium' 
ORDER BY created_at DESC;

-- 4. Covering Index
-- Include all columns needed by query
CREATE INDEX idx_users_covering 
ON users(country, subscription_tier) 
INCLUDE (first_name, last_name, email);

-- Query satisfied entirely from index
SELECT first_name, last_name, email
FROM users
WHERE country = 'US' AND subscription_tier = 'premium';

-- 5. Unique Index
CREATE UNIQUE INDEX idx_users_username ON users(username);
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- 6. Expression Index
CREATE INDEX idx_users_lower_email ON users(LOWER(email));
CREATE INDEX idx_users_extract_year ON users(EXTRACT(YEAR FROM created_at));

-- Query uses expression index
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';

-- 7. GIN Index (Generalized Inverted Index)
-- Good for: JSONB, arrays, full-text search
CREATE INDEX idx_activities_metadata ON user_activities USING GIN (metadata);
CREATE INDEX idx_activities_metadata_path ON user_activities USING GIN (metadata jsonb_path_ops);

-- Query JSONB efficiently
SELECT * FROM user_activities 
WHERE metadata @> '{"action": "purchase"}';

-- 8. Full-Text Search Index
CREATE INDEX idx_users_name_search ON users 
USING GIN (to_tsvector('english', first_name || ' ' || last_name));

SELECT * FROM users 
WHERE to_tsvector('english', first_name || ' ' || last_name) 
      @@ to_tsquery('john & smith');

-- 9. BRIN Index (Block Range Index)
-- Good for: large tables with naturally ordered data
CREATE INDEX idx_activities_created_brin 
ON user_activities USING BRIN (created_at);

-- 10. Hash Index
-- Good for: equality comparisons only
CREATE INDEX idx_users_country_hash ON users USING HASH (country);

-- ============================================
-- INDEX MAINTENANCE
-- ============================================

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- Find unused indexes
SELECT 
    schemaname || '.' || relname AS table,
    indexrelname AS index,
    pg_size_pretty(pg_relation_size(i.indexrelid)) AS index_size,
    idx_scan as index_scans
FROM pg_stat_user_indexes ui
JOIN pg_index i ON ui.indexrelid = i.indexrelid
WHERE NOT indisunique 
  AND idx_scan < 50 
  AND pg_relation_size(relid) > 5 * 8192
ORDER BY pg_relation_size(i.indexrelid) DESC;

-- Index bloat check
SELECT 
    current_database(),
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
    idx_scan,
    idx_tup_read
FROM pg_stat_user_indexes
JOIN pg_index USING (indexrelid)
WHERE pg_relation_size(indexrelid) > 1024 * 1024
ORDER BY pg_relation_size(indexrelid) DESC;

-- Rebuild index (lock-free with CONCURRENTLY)
CREATE INDEX CONCURRENTLY idx_users_new_email ON users(email);
DROP INDEX CONCURRENTLY idx_users_email;
ALTER INDEX idx_users_new_email RENAME TO idx_users_email;

-- REINDEX for maintenance
REINDEX INDEX idx_users_email;
REINDEX TABLE users;

-- Update statistics
ANALYZE users;
ANALYZE user_activities;

-- ============================================
-- INDEX OPTIMIZATION EXAMPLES
-- ============================================

-- Scenario 1: Search by multiple optional filters
-- Create separate indexes for each filter
CREATE INDEX idx_users_country ON users(country);
CREATE INDEX idx_users_tier ON users(subscription_tier);
CREATE INDEX idx_users_active ON users(is_active);

-- Query planner can combine indexes with bitmap scan
SELECT * FROM users
WHERE country = 'US'
  AND subscription_tier = 'premium'
  AND is_active = true;

-- Scenario 2: Time-series queries
CREATE INDEX idx_activities_time_desc ON user_activities(created_at DESC);

-- Efficient pagination
SELECT * FROM user_activities
WHERE created_at < '2024-01-01'
ORDER BY created_at DESC
LIMIT 100;

-- Scenario 3: Multi-tenant queries
CREATE INDEX idx_activities_tenant_time 
ON user_activities(user_id, created_at DESC);

SELECT * FROM user_activities
WHERE user_id = 123
ORDER BY created_at DESC
LIMIT 50;

-- ============================================
-- TESTING INDEX USAGE
-- ============================================

-- Verify index is used
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM users 
WHERE email = 'user@example.com';

-- Check for sequential scans (bad sign)
SELECT 
    schemaname,
    relname,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan
ORDER BY seq_scan DESC;

-- Force index usage for testing
SET enable_seqscan = off;
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';
SET enable_seqscan = on;
```

## Index Type Comparison

| Type | Best For | Size | Write Cost |
|------|----------|------|------------|
| B-Tree | Equality, range, prefix | Medium | Medium |
| Hash | Equality only | Small | Low |
| GIN | JSONB, arrays, text search | Large | High |
| GiST | Geospatial, ranges | Medium | Medium |
| BRIN | Ordered, large tables | Tiny | Very Low |

## Index Design Rules

1. **Leftmost Prefix Rule**: Query must use leftmost columns of composite index
2. **Selectivity**: Index columns with high cardinality
3. **Coverage**: Include frequently selected columns
4. **Partial Indexes**: Filter common WHERE conditions
5. **Order**: Equality → Range → Sort in composite indexes

## Performance Metrics

- **idx_scan**: Number of index scans
- **idx_tup_read**: Tuples read from index
- **idx_tup_fetch**: Tuples fetched from heap
- **Index hit ratio**: Should be > 99% for OLTP

## Maintenance Schedule

| Task | Frequency |
|------|-----------|
| ANALYZE | After bulk changes |
| REINDEX | Monthly or after major changes |
| Check unused | Weekly |
| Monitor bloat | Daily |

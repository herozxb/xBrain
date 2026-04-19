# SQL Joins Mastery

## Problem

Demonstrate all SQL join types with practical examples, optimization techniques, and common patterns for data analysis.

## Implementation

```sql
-- ============================================
-- SAMPLE DATA SETUP
-- ============================================

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    budget DECIMAL(15, 2)
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    department_id INTEGER REFERENCES departments(id),
    manager_id INTEGER REFERENCES employees(id),
    salary DECIMAL(10, 2),
    hire_date DATE
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    department_id INTEGER REFERENCES departments(id),
    budget DECIMAL(15, 2),
    start_date DATE,
    end_date DATE
);

CREATE TABLE employee_projects (
    employee_id INTEGER REFERENCES employees(id),
    project_id INTEGER REFERENCES projects(id),
    role VARCHAR(50),
    hours_allocated INTEGER,
    PRIMARY KEY (employee_id, project_id)
);

-- Sample data
INSERT INTO departments (name, budget) VALUES
    ('Engineering', 1000000),
    ('Marketing', 500000),
    ('Sales', 600000),
    ('HR', 200000);

INSERT INTO employees (name, department_id, salary, hire_date) VALUES
    ('Alice', 1, 120000, '2020-01-15'),
    ('Bob', 1, 110000, '2020-03-20'),
    ('Charlie', 2, 90000, '2021-06-01'),
    ('Diana', 2, 85000, '2021-09-15'),
    ('Eve', 3, 95000, '2019-11-01'),
    ('Frank', NULL, 80000, '2022-01-01'); -- No department

-- ============================================
-- 1. INNER JOIN
-- Returns rows when match in BOTH tables
-- ============================================

SELECT e.name, e.salary, d.name as department
FROM employees e
INNER JOIN departments d ON e.department_id = d.id;

-- With additional conditions
SELECT e.name, d.name as department
FROM employees e
INNER JOIN departments d 
    ON e.department_id = d.id 
    AND d.budget > 400000;

-- ============================================
-- 2. LEFT JOIN (LEFT OUTER JOIN)
-- All rows from left, matching from right
-- ============================================

-- All employees, even without department
SELECT e.name, d.name as department
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;

-- Find employees WITHOUT department
SELECT e.name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id
WHERE d.id IS NULL;

-- ============================================
-- 3. RIGHT JOIN (RIGHT OUTER JOIN)
-- All rows from right, matching from left
-- ============================================

-- All departments, even without employees
SELECT e.name, d.name as department
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.id;

-- Find departments WITHOUT employees
SELECT d.name
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.id
WHERE e.id IS NULL;

-- ============================================
-- 4. FULL OUTER JOIN
-- All rows from both sides
-- ============================================

SELECT e.name as employee, d.name as department
FROM employees e
FULL OUTER JOIN departments d ON e.department_id = d.id;

-- Find unmatched rows in either table
SELECT e.name as employee, d.name as department
FROM employees e
FULL OUTER JOIN departments d ON e.department_id = d.id
WHERE e.id IS NULL OR d.id IS NULL;

-- ============================================
-- 5. CROSS JOIN (Cartesian Product)
-- Every row from left with every row from right
-- ============================================

-- All possible employee-department combinations
SELECT e.name as employee, d.name as department
FROM employees e
CROSS JOIN departments d;

-- Use case: Generate all date combinations
WITH dates AS (
    SELECT generate_series(
        '2024-01-01'::date,
        '2024-01-07'::date,
        '1 day'::interval
    )::date as date
),
employees_subset AS (
    SELECT id, name FROM employees WHERE department_id = 1
)
SELECT e.name, d.date
FROM employees_subset e
CROSS JOIN dates d;

-- ============================================
-- 6. SELF JOIN
-- Join table to itself
-- ============================================

-- Update with manager relationships
UPDATE employees SET manager_id = 1 WHERE id IN (2, 3);
UPDATE employees SET manager_id = 4 WHERE id = 5;

-- Find employees and their managers
SELECT 
    e.name as employee,
    m.name as manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;

-- Find employees who earn more than their manager
SELECT 
    e.name as employee,
    e.salary as employee_salary,
    m.name as manager,
    m.salary as manager_salary
FROM employees e
INNER JOIN employees m ON e.manager_id = m.id
WHERE e.salary > m.salary;

-- ============================================
-- 7. NATURAL JOIN
-- Automatically joins on same-named columns
-- ============================================

-- Joins on department_id automatically
SELECT e.name, d.name as department
FROM employees e
NATURAL JOIN departments d;

-- ============================================
-- 8. LATERAL JOIN
-- Reference previous tables in subquery
-- ============================================

-- Get top 2 highest-paid employees per department
SELECT d.name, e.name, e.salary
FROM departments d
CROSS JOIN LATERAL (
    SELECT name, salary
    FROM employees e
    WHERE e.department_id = d.id
    ORDER BY salary DESC
    LIMIT 2
) e;

-- ============================================
-- 9. MULTIPLE JOINS
-- ============================================

-- Three-way join
SELECT 
    e.name as employee,
    d.name as department,
    p.name as project
FROM employees e
INNER JOIN departments d ON e.department_id = d.id
INNER JOIN projects p ON p.department_id = d.id;

-- Join through junction table
SELECT 
    e.name as employee,
    p.name as project,
    ep.role,
    ep.hours_allocated
FROM employees e
INNER JOIN employee_projects ep ON e.id = ep.employee_id
INNER JOIN projects p ON ep.project_id = p.id;

-- ============================================
-- 10. JOIN WITH AGGREGATION
-- ============================================

-- Count employees per department
SELECT 
    d.name as department,
    COUNT(e.id) as employee_count,
    COALESCE(SUM(e.salary), 0) as total_salary
FROM departments d
LEFT JOIN employees e ON e.department_id = d.id
GROUP BY d.id, d.name
ORDER BY employee_count DESC;

-- Department stats with subquery
SELECT 
    d.name,
    stats.employee_count,
    stats.avg_salary,
    stats.max_salary
FROM departments d
LEFT JOIN (
    SELECT 
        department_id,
        COUNT(*) as employee_count,
        AVG(salary) as avg_salary,
        MAX(salary) as max_salary
    FROM employees
    GROUP BY department_id
) stats ON stats.department_id = d.id;

-- ============================================
-- 11. JOIN OPTIMIZATION TECHNIQUES
-- ============================================

-- Create indexes for join columns
CREATE INDEX idx_employees_dept ON employees(department_id);
CREATE INDEX idx_employees_manager ON employees(manager_id);
CREATE INDEX idx_employee_projects_emp ON employee_projects(employee_id);
CREATE INDEX idx_employee_projects_proj ON employee_projects(project_id);

-- Filter early (WHERE before JOIN)
-- Better
SELECT e.name, d.name as department
FROM employees e
INNER JOIN departments d ON e.department_id = d.id
WHERE e.salary > 90000;

-- Worse (filters after join)
SELECT e.name, d.name as department
FROM employees e
INNER JOIN departments d ON e.department_id = d.id
  AND e.salary > 90000;

-- Use CTEs for complex joins
WITH active_employees AS (
    SELECT * FROM employees 
    WHERE hire_date < CURRENT_DATE - INTERVAL '6 months'
),
large_departments AS (
    SELECT * FROM departments 
    WHERE budget > 400000
)
SELECT ae.name, ld.name as department
FROM active_employees ae
INNER JOIN large_departments ld ON ae.department_id = ld.id;

-- ============================================
-- 12. ANTI-JOIN PATTERNS
-- ============================================

-- Employees NOT in any project
SELECT e.name
FROM employees e
WHERE NOT EXISTS (
    SELECT 1 FROM employee_projects ep 
    WHERE ep.employee_id = e.id
);

-- Departments without projects
SELECT d.name
FROM departments d
LEFT JOIN projects p ON p.department_id = d.id
WHERE p.id IS NULL;

-- ============================================
-- TESTS
-- ============================================

-- Test 1: INNER JOIN returns only matching rows
-- Result: 5 employees (Frank has no department)
SELECT COUNT(*) = 5 FROM employees e
INNER JOIN departments d ON e.department_id = d.id;

-- Test 2: LEFT JOIN returns all employees
-- Result: 6 employees (Frank has NULL department)
SELECT COUNT(*) = 6 FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;

-- Test 3: SELF JOIN finds managers
-- Result: Employees with their managers
SELECT COUNT(*) > 0 FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id
WHERE m.name IS NOT NULL;

-- Test 4: Department with most employees
SELECT d.name, COUNT(e.id) as cnt
FROM departments d
LEFT JOIN employees e ON e.department_id = d.id
GROUP BY d.id, d.name
ORDER BY cnt DESC
LIMIT 1;
```

## Join Types Summary

| Join Type | Returns | Use Case |
|-----------|---------|----------|
| INNER | Matching rows only | Default for filtering |
| LEFT | All left + matching | Find missing relations |
| RIGHT | All right + matching | Rarely used (use LEFT) |
| FULL OUTER | All from both | Find all mismatches |
| CROSS | Cartesian product | Generate combinations |
| SELF | Table to itself | Hierarchies |
| LATERAL | Per-row subquery | Top-N per group |

## Performance Tips

1. **Index join columns** on both tables
2. **Filter early** with WHERE before JOIN
3. **Use appropriate join type** - don't use LEFT if INNER works
4. **Avoid CROSS JOIN** on large tables
5. **Consider denormalization** for frequently joined data

## Common Patterns

- **Find missing data**: LEFT JOIN + IS NULL
- **Hierarchical data**: SELF JOIN
- **Many-to-many**: Junction table with two JOINs
- **Top-N per group**: LATERAL JOIN
- **Aggregations**: JOIN with GROUP BY

-- ====================================================================
-- BANGLADESH E-COMMERCE CUSTOMER INTELLIGENCE PLATFORM
-- SQL Analytics: Retention & Cohort Analysis
-- Dialect: ANSI SQL / PostgreSQL / DuckDB
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. Monthly Customer Acquisition & First-Purchase Cohort Sizing
-- --------------------------------------------------------------------
WITH customer_first_purchase AS (
    SELECT 
        customer_id,
        MIN(order_date) AS first_order_date,
        DATE_TRUNC('month', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
)
SELECT 
    STRFTIME(cohort_month, '%Y-%m') AS cohort,
    COUNT(customer_id) AS new_customers_acquired
FROM customer_first_purchase
GROUP BY cohort_month
ORDER BY cohort_month;

-- --------------------------------------------------------------------
-- 2. Monthly Retention Cohort Matrix (Triangular Retention Grid)
-- --------------------------------------------------------------------
WITH customer_cohort AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
),
customer_activities AS (
    SELECT 
        o.customer_id,
        c.cohort_month,
        DATE_TRUNC('month', o.order_date) AS activity_month,
        -- Calculate month offset (M0, M1, M2...)
        (DATE_PART('year', o.order_date) - DATE_PART('year', c.cohort_month)) * 12 +
        (DATE_PART('month', o.order_date) - DATE_PART('month', c.cohort_month)) AS month_number
    FROM orders o
    JOIN customer_cohort c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'Delivered'
),
cohort_size AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS initial_cohort_size
    FROM customer_cohort
    GROUP BY cohort_month
),
retention_matrix AS (
    SELECT 
        ca.cohort_month,
        cs.initial_cohort_size,
        COUNT(DISTINCT CASE WHEN ca.month_number = 0 THEN ca.customer_id END) AS m0_active,
        COUNT(DISTINCT CASE WHEN ca.month_number = 1 THEN ca.customer_id END) AS m1_active,
        COUNT(DISTINCT CASE WHEN ca.month_number = 2 THEN ca.customer_id END) AS m2_active,
        COUNT(DISTINCT CASE WHEN ca.month_number = 3 THEN ca.customer_id END) AS m3_active,
        COUNT(DISTINCT CASE WHEN ca.month_number = 4 THEN ca.customer_id END) AS m4_active,
        COUNT(DISTINCT CASE WHEN ca.month_number = 5 THEN ca.customer_id END) AS m5_active,
        COUNT(DISTINCT CASE WHEN ca.month_number = 6 THEN ca.customer_id END) AS m6_active
    FROM customer_activities ca
    JOIN cohort_size cs ON ca.cohort_month = cs.cohort_month
    GROUP BY ca.cohort_month, cs.initial_cohort_size
)
SELECT 
    STRFTIME(cohort_month, '%Y-%m') AS cohort,
    initial_cohort_size,
    ROUND(m0_active::FLOAT / initial_cohort_size * 100, 1) AS m0_pct,
    ROUND(m1_active::FLOAT / initial_cohort_size * 100, 1) AS m1_pct,
    ROUND(m2_active::FLOAT / initial_cohort_size * 100, 1) AS m2_pct,
    ROUND(m3_active::FLOAT / initial_cohort_size * 100, 1) AS m3_pct,
    ROUND(m4_active::FLOAT / initial_cohort_size * 100, 1) AS m4_pct,
    ROUND(m5_active::FLOAT / initial_cohort_size * 100, 1) AS m5_pct,
    ROUND(m6_active::FLOAT / initial_cohort_size * 100, 1) AS m6_pct
FROM retention_matrix
ORDER BY cohort_month;

-- --------------------------------------------------------------------
-- 3. Cohort Cumulative Revenue LTV Trajectory
-- --------------------------------------------------------------------
WITH customer_cohort AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
),
cohort_revenue AS (
    SELECT 
        c.cohort_month,
        (DATE_PART('year', o.order_date) - DATE_PART('year', c.cohort_month)) * 12 +
        (DATE_PART('month', o.order_date) - DATE_PART('month', c.cohort_month)) AS month_number,
        SUM(o.total_amount) AS revenue_generated
    FROM orders o
    JOIN customer_cohort c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'Delivered'
    GROUP BY c.cohort_month, month_number
),
cohort_base AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_customers
    FROM customer_cohort
    GROUP BY cohort_month
)
SELECT 
    STRFTIME(cr.cohort_month, '%Y-%m') AS cohort,
    cb.cohort_customers,
    cr.month_number,
    ROUND(cr.revenue_generated, 2) AS monthly_cohort_revenue,
    ROUND(SUM(cr.revenue_generated) OVER (
        PARTITION BY cr.cohort_month 
        ORDER BY cr.month_number
    ), 2) AS cumulative_cohort_revenue,
    ROUND(SUM(cr.revenue_generated) OVER (
        PARTITION BY cr.cohort_month 
        ORDER BY cr.month_number
    ) / cb.cohort_customers, 2) AS cumulative_revenue_per_acquired_customer
FROM cohort_revenue cr
JOIN cohort_base cb ON cr.cohort_month = cb.cohort_month
WHERE cr.month_number <= 6
ORDER BY cr.cohort_month, cr.month_number;

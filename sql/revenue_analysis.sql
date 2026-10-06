-- ====================================================================
-- BANGLADESH E-COMMERCE CUSTOMER INTELLIGENCE PLATFORM
-- SQL Analytics: Revenue Analysis
-- Dialect: ANSI SQL / PostgreSQL / DuckDB
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. Total High-Level Revenue & Order Performance Metrics
-- --------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_purchasing_customers,
    ROUND(SUM(o.total_amount), 2) AS gross_sales_bdt,
    ROUND(SUM(oi.revenue), 2) AS net_product_revenue_bdt,
    ROUND(SUM(oi.cost), 2) AS total_cost_bdt,
    ROUND(SUM(oi.profit), 2) AS gross_profit_bdt,
    ROUND(SUM(oi.profit) / NULLIF(SUM(oi.revenue), 0) * 100, 2) AS overall_profit_margin_pct,
    ROUND(AVG(o.total_amount), 2) AS average_order_value_bdt
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Delivered';

-- --------------------------------------------------------------------
-- 2. Monthly Revenue Trend, Running Total, MoM Growth & Margin (Window Functions)
-- --------------------------------------------------------------------
WITH monthly_metrics AS (
    SELECT 
        DATE_TRUNC('month', o.order_date) AS order_month,
        COUNT(DISTINCT o.order_id) AS monthly_orders,
        ROUND(SUM(oi.revenue), 2) AS monthly_revenue,
        ROUND(SUM(oi.profit), 2) AS monthly_profit
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY DATE_TRUNC('month', o.order_date)
)
SELECT 
    STRFTIME(order_month, '%Y-%m') AS month,
    monthly_orders,
    monthly_revenue,
    monthly_profit,
    ROUND(monthly_profit / monthly_revenue * 100, 2) AS profit_margin_pct,
    -- Running Cumulative Revenue
    ROUND(SUM(monthly_revenue) OVER (ORDER BY order_month), 2) AS cumulative_revenue_bdt,
    -- Month-over-Month Growth Calculation via LAG
    ROUND(LAG(monthly_revenue, 1) OVER (ORDER BY order_month), 2) AS prev_month_revenue,
    ROUND(
        ((monthly_revenue - LAG(monthly_revenue, 1) OVER (ORDER BY order_month)) 
        / NULLIF(LAG(monthly_revenue, 1) OVER (ORDER BY order_month), 0)) * 100, 
        2
    ) AS mom_revenue_growth_pct,
    -- 3-Month Moving Average Revenue
    ROUND(AVG(monthly_revenue) OVER (
        ORDER BY order_month 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_3m_avg_revenue
FROM monthly_metrics
ORDER BY order_month;

-- --------------------------------------------------------------------
-- 3. Revenue by Product Category & Contribution Share
-- --------------------------------------------------------------------
WITH cat_summary AS (
    SELECT 
        p.category,
        COUNT(DISTINCT o.order_id) AS order_count,
        SUM(oi.quantity) AS total_units_sold,
        ROUND(SUM(oi.revenue), 2) AS total_revenue,
        ROUND(SUM(oi.cost), 2) AS total_cost,
        ROUND(SUM(oi.profit), 2) AS total_profit,
        ROUND(SUM(oi.profit) / NULLIF(SUM(oi.revenue), 0) * 100, 2) AS margin_pct
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY p.category
)
SELECT 
    category,
    order_count,
    total_units_sold,
    total_revenue,
    total_profit,
    margin_pct,
    ROUND(total_revenue / SUM(total_revenue) OVER () * 100, 2) AS revenue_share_pct,
    ROUND(total_profit / SUM(total_profit) OVER () * 100, 2) AS profit_share_pct,
    DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
FROM cat_summary
ORDER BY total_revenue DESC;

-- --------------------------------------------------------------------
-- 4. Revenue & Order Density by Administrative Division & City
-- --------------------------------------------------------------------
SELECT 
    c.division,
    c.city,
    COUNT(DISTINCT c.customer_id) AS customer_count,
    COUNT(DISTINCT o.order_id) AS order_count,
    ROUND(SUM(o.total_amount), 2) AS total_revenue_bdt,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value_bdt,
    ROUND(SUM(o.total_amount) / SUM(SUM(o.total_amount)) OVER () * 100, 2) AS national_revenue_share_pct,
    RANK() OVER (PARTITION BY c.division ORDER BY SUM(o.total_amount) DESC) AS city_rank_in_division
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_status = 'Delivered'
GROUP BY c.division, c.city
ORDER BY total_revenue_bdt DESC;

-- --------------------------------------------------------------------
-- 5. Revenue by Marketing Acquisition Channel & Payment Method
-- --------------------------------------------------------------------
SELECT 
    c.acquisition_channel,
    o.payment_method,
    COUNT(DISTINCT o.order_id) AS orders_count,
    ROUND(SUM(o.total_amount), 2) AS total_revenue_bdt,
    ROUND(AVG(o.total_amount), 2) AS aov_bdt,
    ROUND(SUM(o.discount_amount), 2) AS total_discount_given_bdt,
    ROUND(SUM(o.discount_amount) / NULLIF(SUM(o.total_amount), 0) * 100, 2) AS discount_to_revenue_pct
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_status = 'Delivered'
GROUP BY c.acquisition_channel, o.payment_method
ORDER BY c.acquisition_channel, total_revenue_bdt DESC;

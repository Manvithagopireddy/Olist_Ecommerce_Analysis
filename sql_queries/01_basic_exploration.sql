-- 01_basic_exploration.sql
-- Basic queries to understand revenue and product volume

-- 1. Total Revenue by Year and Month
SELECT 
    EXTRACT(YEAR FROM order_purchase_timestamp) AS year,
    EXTRACT(MONTH FROM order_purchase_timestamp) AS month,
    SUM(payment_value) AS total_revenue
FROM orders o
JOIN order_payments op ON o.order_id = op.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1, 2
ORDER BY 1, 2;

-- 2. Top 10 Product Categories by Total Sales Volume
SELECT 
    p.product_category_name, 
    COUNT(oi.order_id) AS total_items_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10;

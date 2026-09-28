-- 02_logistics_analysis.sql
-- Queries analyzing delivery times, freight costs, and customer satisfaction

-- 1. Average Delivery Time vs. Estimated Time by State
SELECT 
    c.customer_state,
    AVG(EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp))/86400) AS avg_actual_delivery_days,
    AVG(EXTRACT(EPOCH FROM (o.order_estimated_delivery_date - o.order_purchase_timestamp))/86400) AS avg_estimated_delivery_days
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY 2 DESC;

-- 2. Customer Satisfaction (Review Scores) by Product Category
SELECT 
    p.product_category_name,
    AVG(r.review_score) AS avg_review_score,
    COUNT(r.review_id) AS total_reviews
FROM order_reviews r
JOIN order_items oi ON r.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY 1
HAVING COUNT(r.review_id) > 50
ORDER BY 2 ASC -- Look at the worst performing categories
LIMIT 10;

-- 3. Impact of Freight Value (Shipping Cost) on Order Volume
SELECT 
    CASE 
        WHEN oi.freight_value < 10 THEN 'Under $10'
        WHEN oi.freight_value BETWEEN 10 AND 20 THEN '$10 - $20'
        WHEN oi.freight_value BETWEEN 20 AND 50 THEN '$20 - $50'
        ELSE 'Over $50' 
    END AS shipping_cost_tier,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    AVG(r.review_score) AS avg_review_score
FROM order_items oi
LEFT JOIN order_reviews r ON oi.order_id = r.order_id
GROUP BY 1
ORDER BY 2 DESC;

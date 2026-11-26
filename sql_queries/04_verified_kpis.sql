-- SQLite: separate monetary definitions; never join raw payments to raw items.
WITH payments AS (
    SELECT order_id, SUM(payment_value) AS paid
    FROM order_payments GROUP BY order_id
), items AS (
    SELECT order_id, SUM(price) AS merchandise, SUM(freight_value) AS freight
    FROM order_items GROUP BY order_id
)
SELECT o.order_status,
       COUNT(*) AS orders,
       ROUND(SUM(COALESCE(p.paid, 0)), 2) AS payment_total_brl,
       ROUND(SUM(COALESCE(i.merchandise, 0)), 2) AS merchandise_total_brl,
       ROUND(SUM(COALESCE(i.freight, 0)), 2) AS freight_total_brl,
       ROUND(AVG(p.paid), 2) AS average_paid_order_brl,
       SUM(CASE WHEN p.order_id IS NULL THEN 1 ELSE 0 END) AS orders_without_payment
FROM orders o
LEFT JOIN payments p ON o.order_id = p.order_id
LEFT JOIN items i ON o.order_id = i.order_id
GROUP BY o.order_status
ORDER BY o.order_status;

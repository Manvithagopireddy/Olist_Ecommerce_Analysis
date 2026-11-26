-- Run after ingestion. Indexes target status/time filtering and order-grain joins.
CREATE INDEX IF NOT EXISTS ix_orders_status_purchase ON orders(order_status, order_purchase_timestamp);
ANALYZE;
EXPLAIN QUERY PLAN
SELECT order_id FROM orders
WHERE order_status='delivered' AND order_purchase_timestamp >= '2018-01-01'
AND order_purchase_timestamp < '2018-02-01';

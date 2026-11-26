# Power BI reconciliation guide
Import the canonical ORDER_FACT query from analytics_core.py (one row per order), via SQLite ODBC or an exported CSV. Name the table OrdersFact. Do not join raw payment and item tables directly.
Measures:
```dax
Recorded payments = SUM(OrdersFact[payment_total])
Delivered payments = CALCULATE([Recorded payments], OrdersFact[order_status] = "delivered")
Delivered orders = CALCULATE(DISTINCTCOUNT(OrdersFact[order_id]), OrdersFact[order_status] = "delivered")
Average paid delivered order = CALCULATE(AVERAGE(OrdersFact[payment_total]), OrdersFact[order_status] = "delivered")
Late delivery rate = CALCULATE(AVERAGE(OrdersFact[late]), OrdersFact[order_status] = "delivered")
```
Set payment measures to BRL, late rate to percentage. Use a date dimension, state and status slicers, monthly payment trend, and a delivery performance matrix. Reconcile unfiltered payments to 16,008,872.12 and delivered payments to 15,422,461.77 for the supplied historical snapshot. The original PBIX is unchanged; apply and verify these measures in Power BI Desktop.

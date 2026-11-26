"""Create synthetic CSV input and build database for runtime smoke tests."""
import csv
from pathlib import Path
from python_eda.validated_etl import TABLES, build

def prepare(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    extra = {
        "orders": {"order_status": "delivered", "order_purchase_timestamp": "2018-01-01 12:00:00", "order_delivered_customer_date": "2018-01-05 12:00:00", "order_estimated_delivery_date": "2018-01-08 00:00:00"},
        "customers": {"customer_state": "SP"},
        "order_items": {"price": 10, "freight_value": 2, "order_item_id": 1},
        "order_payments": {"payment_value": 12, "payment_sequential": 1},
        "order_reviews": {"review_score": 5},
    }
    for table, (name, keys, required) in TABLES.items():
        values = dict.fromkeys(keys + required, "fixture")
        values.update(extra.get(table, {}))
        with (root / name).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(values))
            writer.writeheader()
            writer.writerow(values)
    build(root, root / "olist.db")

if __name__ == "__main__":
    prepare("data")

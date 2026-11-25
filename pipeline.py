"""Run python pipeline.py --download to retrieve and ingest Olist."""
import argparse
import csv
import sqlite3
from pathlib import Path
import tempfile
import os

TABLES = {f"olist_{n}_dataset.csv": n for n in (
    "orders", "customers", "order_items", "order_payments", "order_reviews",
    "products", "sellers", "geolocation")}
TABLES["product_category_name_translation.csv"] = "category_translation"

def ingest(source, destination):
    import pandas as pd
    source, destination = Path(source), Path(destination)
    for filename in TABLES:
        if not (source / filename).is_file():
            raise FileNotFoundError(source / filename)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=destination.parent)
    os.close(fd)
    try:
        with sqlite3.connect(tmp) as conn:
            for filename, table in TABLES.items():
                frame = pd.read_csv(source / filename)
                if frame.empty:
                    raise ValueError(f"Empty table: {table}")
                frame.to_sql(table, conn, index=False)
            for table, key in (("orders","order_id"),("customers","customer_id"),
                               ("products","product_id"),("sellers","seller_id")):
                if conn.execute(f"SELECT COUNT(*) FROM {table} WHERE {key} IS NULL").fetchone()[0]:
                    raise ValueError(f"Missing key: {table}")
                conn.execute(f"CREATE UNIQUE INDEX idx_{table}_pk ON {table}({key})")
            for table in ("order_items","order_payments","order_reviews"):
                conn.execute(f"CREATE INDEX idx_{table}_order ON {table}(order_id)")
            for table, key, parent in (("orders","customer_id","customers"),
                ("order_items","order_id","orders"),("order_payments","order_id","orders"),
                ("order_reviews","order_id","orders")):
                if conn.execute(f"SELECT COUNT(*) FROM {table} t LEFT JOIN {parent} p ON t.{key}=p.{key} WHERE p.{key} IS NULL").fetchone()[0]:
                    raise ValueError(f"Orphan records: {table}")
            from analytics_core import metrics
            print(metrics(conn))
        os.replace(tmp, destination)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--source", default="data")
    parser.add_argument("--database", default="data/olist.db")
    args = parser.parse_args()
    if args.download:
        import kagglehub
        args.source = kagglehub.dataset_download("olistbr/brazilian-ecommerce")
    ingest(args.source, args.database)

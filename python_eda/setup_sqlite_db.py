"""
setup_sqlite_db.py
------------------
Loads all Olist CSV files from the data/ folder into a local SQLite database.
This lets you run all SQL queries from sql_queries/ without needing PostgreSQL.

Run: .\venv\Scripts\python python_eda\setup_sqlite_db.py
"""

import pandas as pd
import sqlite3
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_PATH  = os.path.join(os.path.dirname(__file__), '..', 'data', 'olist.db')

# Map of CSV filenames → SQL table names
CSV_TABLE_MAP = {
    'olist_orders_dataset.csv':                'orders',
    'olist_order_items_dataset.csv':           'order_items',
    'olist_order_payments_dataset.csv':        'order_payments',
    'olist_order_reviews_dataset.csv':         'order_reviews',
    'olist_customers_dataset.csv':             'customers',
    'olist_products_dataset.csv':              'products',
    'olist_sellers_dataset.csv':               'sellers',
    'olist_geolocation_dataset.csv':           'geolocation',
    'product_category_name_translation.csv':   'category_translation',
}

def load_csvs_to_sqlite():
    print(f"Connecting to SQLite database at: {DB_PATH}\n")
    conn = sqlite3.connect(DB_PATH)

    for csv_file, table_name in CSV_TABLE_MAP.items():
        filepath = os.path.join(DATA_DIR, csv_file)
        if os.path.exists(filepath):
            print(f"  Loading {csv_file}  -->  table '{table_name}' ...", end=' ')
            df = pd.read_csv(filepath)
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"OK  ({len(df):,} rows)")
        else:
            print(f"  WARNING: {csv_file} not found - skipping.")

    conn.close()
    print("\nAll CSVs loaded into olist.db successfully!")
    print(f"Database path: {os.path.abspath(DB_PATH)}")
    print("\nYou can now open this .db file in DB Browser for SQLite to run your queries!")

if __name__ == '__main__':
    load_csvs_to_sqlite()

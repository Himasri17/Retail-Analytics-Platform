"""
load_data.py
------------
Loads data/superstore.csv into the configured database (SQLite by default,
PostgreSQL if DATABASE_URL is set accordingly). Run once before starting the API:

    python load_data.py
"""

import os

import pandas as pd
from dotenv import load_dotenv

from database import Base, engine

load_dotenv()
CSV_PATH = os.getenv("CSV_PATH", "../data/superstore.csv")

COLUMN_MAP = {
    "Row ID": "row_id",
    "Order ID": "order_id",
    "Order Date": "order_date",
    "Ship Date": "ship_date",
    "Ship Mode": "ship_mode",
    "Customer ID": "customer_id",
    "Customer Name": "customer_name",
    "Segment": "segment",
    "Country": "country",
    "City": "city",
    "State": "state",
    "Postal Code": "postal_code",
    "Region": "region",
    "Product ID": "product_id",
    "Category": "category",
    "Sub-Category": "sub_category",
    "Product Name": "product_name",
    "Sales": "sales",
    "Quantity": "quantity",
    "Discount": "discount",
    "Profit": "profit",
}


def main():
    print(f"📥 Reading {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH, encoding="latin1")
    df = df.rename(columns=COLUMN_MAP)
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.date
    df["ship_date"] = pd.to_datetime(df["ship_date"]).dt.date
    df["postal_code"] = df["postal_code"].astype(str)

    print("🧱 Creating tables ...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print(f"🚚 Writing {len(df):,} rows to the database ...")
    df.to_sql("orders", con=engine, if_exists="append", index=False, chunksize=1000)

    print(f"✅ Done. Loaded {len(df):,} rows into '{engine.url}'.")


if __name__ == "__main__":
    main()

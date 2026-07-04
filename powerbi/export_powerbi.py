"""
export_powerbi.py
------------------
Builds a small star schema (1 fact table + 4 dimension tables + the RFM
segmentation table) as CSVs ready to import into Power BI or Tableau.

Can be run two ways:
  1. Standalone, reading data/superstore.csv directly:
         python export_powerbi.py
  2. Imported and called from the FastAPI backend (POST /api/export/powerbi),
     which passes in a live, filtered DataFrame via run_export(df).
"""

import os

import pandas as pd

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "exports")


def run_export(df: pd.DataFrame) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["ship_date"] = pd.to_datetime(df["ship_date"])

    # ── Fact table ───────────────────────────────────────────────────────
    fact_cols = ["row_id", "order_id", "order_date", "ship_date", "ship_mode",
                 "customer_id", "product_id", "region", "sales", "quantity",
                 "discount", "profit"]
    fact = df[fact_cols].copy()
    fact["profit_margin_pct"] = (fact["profit"] / fact["sales"] * 100).round(2)
    fact.to_csv(os.path.join(OUTPUT_DIR, "fact_orders.csv"), index=False)

    # ── Dim: Customer ────────────────────────────────────────────────────
    dim_customer = df.groupby("customer_id").agg(
        customer_name=("customer_name", "first"),
        segment=("segment", "first"),
        state=("state", "first"),
        region=("region", "first"),
    ).reset_index()
    dim_customer.to_csv(os.path.join(OUTPUT_DIR, "dim_customer.csv"), index=False)

    # ── Dim: Product ─────────────────────────────────────────────────────
    dim_product = df.groupby("product_id").agg(
        product_name=("product_name", "first"),
        category=("category", "first"),
        sub_category=("sub_category", "first"),
    ).reset_index()
    dim_product.to_csv(os.path.join(OUTPUT_DIR, "dim_product.csv"), index=False)

    # ── Dim: Geography ───────────────────────────────────────────────────
    dim_geo = df.groupby(["state", "city", "region"]).size().reset_index(name="order_lines")
    dim_geo.to_csv(os.path.join(OUTPUT_DIR, "dim_geography.csv"), index=False)

    # ── Dim: Date ────────────────────────────────────────────────────────
    dmin, dmax = df["order_date"].min(), df["order_date"].max()
    dim_date = pd.DataFrame({"Date": pd.date_range(dmin, dmax, freq="D")})
    dim_date["Year"] = dim_date["Date"].dt.year
    dim_date["Quarter"] = dim_date["Date"].dt.quarter
    dim_date["Month"] = dim_date["Date"].dt.month
    dim_date["MonthName"] = dim_date["Date"].dt.strftime("%B")
    dim_date["Weekday"] = dim_date["Date"].dt.day_name()
    dim_date.to_csv(os.path.join(OUTPUT_DIR, "dim_date.csv"), index=False)

    # ── RFM segmentation table (reuses the backend's RFM engine) ─────────
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
    from rfm import compute_rfm  # noqa: E402

    rfm = compute_rfm(df)
    rfm.to_csv(os.path.join(OUTPUT_DIR, "customer_rfm.csv"), index=False)

    print(f"✅ Power BI exports written to {OUTPUT_DIR}/")
    for f in ["fact_orders.csv", "dim_customer.csv", "dim_product.csv",
              "dim_geography.csv", "dim_date.csv", "customer_rfm.csv"]:
        print(f"   • {f}")
    return OUTPUT_DIR


if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "superstore.csv")
    raw = pd.read_csv(csv_path, encoding="latin1")
    raw = raw.rename(columns={
        "Row ID": "row_id", "Order ID": "order_id", "Order Date": "order_date",
        "Ship Date": "ship_date", "Ship Mode": "ship_mode", "Customer ID": "customer_id",
        "Customer Name": "customer_name", "Segment": "segment", "Country": "country",
        "City": "city", "State": "state", "Postal Code": "postal_code", "Region": "region",
        "Product ID": "product_id", "Category": "category", "Sub-Category": "sub_category",
        "Product Name": "product_name", "Sales": "sales", "Quantity": "quantity",
        "Discount": "discount", "Profit": "profit",
    })
    run_export(raw)

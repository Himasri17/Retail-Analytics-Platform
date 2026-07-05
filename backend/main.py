"""
main.py — Retail Analytics Platform API
=========================================
FastAPI backend serving sales, profit, customer, product and RFM-segmentation
KPIs to the React/Recharts dashboard (and, via /api/export/powerbi, to Power BI).

Run:
    pip install -r requirements.txt
    python load_data.py        # one-time: load data/superstore.csv into the DB
    uvicorn main:app --reload

Docs: http://127.0.0.1:8000/docs
"""

import os
from datetime import date
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import OrderLine
from rfm import compute_rfm, rfm_summary

load_dotenv()

app = FastAPI(
    title="Retail Analytics Platform API",
    description="REST API for the Superstore Retail Analytics Platform — sales, profit, "
                 "customer & RFM segmentation KPIs.",
    version="1.0.0",
)

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "https://retail-analytics-platform-3rhphsdu8-himasris-projects-c419fd03.vercel.app")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "https://retail-analytics-platform-3rhphsdu8-himasris-projects-c419fd03.vercel.app", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


# ─────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────

def _orders_df(db: Session, start: Optional[date] = None, end: Optional[date] = None,
                region: Optional[str] = None, category: Optional[str] = None,
                segment: Optional[str] = None) -> pd.DataFrame:
    """Pull the orders table (optionally filtered) into a DataFrame for pandas-side analytics."""
    q = db.query(OrderLine)
    if start:
        q = q.filter(OrderLine.order_date >= start)
    if end:
        q = q.filter(OrderLine.order_date <= end)
    if region:
        q = q.filter(OrderLine.region == region)
    if category:
        q = q.filter(OrderLine.category == category)
    if segment:
        q = q.filter(OrderLine.segment == segment)

    rows = [r.__dict__ for r in q.all()]
    for r in rows:
        r.pop("_sa_instance_state", None)
    df = pd.DataFrame(rows)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data matches the given filters.")
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


CommonFilters = dict(
    start=Query(None, description="Filter: order date >= start (YYYY-MM-DD)"),
    end=Query(None, description="Filter: order date <= end (YYYY-MM-DD)"),
    region=Query(None, description="Filter by Region"),
    category=Query(None, description="Filter by Category"),
    segment=Query(None, description="Filter by Segment"),
)


# ─────────────────────────────────────────────────────────────────────────
# 0. Health & meta
# ─────────────────────────────────────────────────────────────────────────

@app.get("/api/health", tags=["Meta"])
def health():
    return {"status": "ok", "service": "Retail Analytics Platform API"}


@app.get("/api/meta/filters", tags=["Meta"])
def meta_filters(db: Session = Depends(get_db)):
    """Distinct filter values for the dashboard's filter bar."""
    def distinct(col):
        return [r[0] for r in db.query(col).distinct().order_by(col).all() if r[0]]

    years = sorted({d.year for (d,) in db.query(OrderLine.order_date).all()})
    return {
        "regions": distinct(OrderLine.region),
        "categories": distinct(OrderLine.category),
        "sub_categories": distinct(OrderLine.sub_category),
        "segments": distinct(OrderLine.segment),
        "ship_modes": distinct(OrderLine.ship_mode),
        "states": distinct(OrderLine.state),
        "years": years,
    }


# ─────────────────────────────────────────────────────────────────────────
# 1. KPIs / overview
# ─────────────────────────────────────────────────────────────────────────

@app.get("/api/kpis/summary", tags=["KPIs"])
def kpi_summary(start: Optional[date] = None, end: Optional[date] = None,
                 region: Optional[str] = None, category: Optional[str] = None,
                 segment: Optional[str] = None, db: Session = Depends(get_db)):
    df = _orders_df(db, start, end, region, category, segment)
    total_sales = float(df["sales"].sum())
    total_profit = float(df["profit"].sum())
    return {
        "total_sales": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "profit_margin_pct": round(total_profit / total_sales * 100, 2) if total_sales else 0,
        "total_orders": int(df["order_id"].nunique()),
        "total_customers": int(df["customer_id"].nunique()),
        "avg_order_value": round(df.groupby("order_id")["sales"].sum().mean(), 2),
        "total_quantity": int(df["quantity"].sum()),
        "avg_discount_pct": round(df["discount"].mean() * 100, 2),
    }


@app.get("/api/kpis/monthly-trend", tags=["KPIs"])
def kpi_monthly_trend(db: Session = Depends(get_db)):
    df = _orders_df(db)
    m = df.groupby(df["order_date"].dt.to_period("M")).agg(
        sales=("sales", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique")
    ).round(2)
    m.index = m.index.astype(str)
    return m.reset_index().rename(columns={"order_date": "month"}).to_dict(orient="records")


@app.get("/api/kpis/yearly-trend", tags=["KPIs"])
def kpi_yearly_trend(db: Session = Depends(get_db)):
    df = _orders_df(db)
    y = df.groupby(df["order_date"].dt.year).agg(
        sales=("sales", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique")
    ).round(2)
    return y.reset_index().rename(columns={"order_date": "year"}).to_dict(orient="records")


# ─────────────────────────────────────────────────────────────────────────
# 2. Sales
# ─────────────────────────────────────────────────────────────────────────

@app.get("/api/sales/by-category", tags=["Sales"])
def sales_by_category(db: Session = Depends(get_db)):
    df = _orders_df(db)
    g = df.groupby("category").agg(sales=("sales", "sum"), profit=("profit", "sum"),
                                     orders=("order_id", "nunique")).round(2)
    return g.reset_index().to_dict(orient="records")


@app.get("/api/sales/by-subcategory", tags=["Sales"])
def sales_by_subcategory(db: Session = Depends(get_db)):
    df = _orders_df(db)
    g = df.groupby(["category", "sub_category"]).agg(
        sales=("sales", "sum"), profit=("profit", "sum")
    ).round(2).reset_index()
    return g.to_dict(orient="records")


@app.get("/api/sales/by-region", tags=["Sales"])
def sales_by_region(db: Session = Depends(get_db)):
    df = _orders_df(db)
    g = df.groupby("region").agg(sales=("sales", "sum"), profit=("profit", "sum"),
                                   orders=("order_id", "nunique")).round(2)
    return g.reset_index().to_dict(orient="records")


@app.get("/api/sales/by-state", tags=["Sales"])
def sales_by_state(limit: int = Query(15, ge=1, le=60), db: Session = Depends(get_db)):
    df = _orders_df(db)
    g = df.groupby("state").agg(sales=("sales", "sum"), profit=("profit", "sum")).round(2)
    return g.sort_values("sales", ascending=False).head(limit).reset_index().to_dict(orient="records")


@app.get("/api/sales/by-segment", tags=["Sales"])
def sales_by_segment(db: Session = Depends(get_db)):
    df = _orders_df(db)
    g = df.groupby("segment").agg(sales=("sales", "sum"), profit=("profit", "sum"),
                                    customers=("customer_id", "nunique")).round(2)
    return g.reset_index().to_dict(orient="records")


@app.get("/api/sales/by-ship-mode", tags=["Sales"])
def sales_by_ship_mode(db: Session = Depends(get_db)):
    df = _orders_df(db)
    g = df.groupby("ship_mode").agg(sales=("sales", "sum"), orders=("order_id", "nunique")).round(2)
    return g.reset_index().to_dict(orient="records")


@app.get("/api/sales/top-products", tags=["Sales"])
def sales_top_products(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    df = _orders_df(db)
    g = df.groupby(["product_id", "product_name", "category"]).agg(
        sales=("sales", "sum"), profit=("profit", "sum"), quantity=("quantity", "sum")
    ).round(2)
    return g.sort_values("sales", ascending=False).head(limit).reset_index().to_dict(orient="records")


@app.get("/api/sales/discount-impact", tags=["Sales"])
def sales_discount_impact(db: Session = Depends(get_db)):
    df = _orders_df(db)
    bins = [-0.01, 0, 0.2, 0.4, 0.6, 0.8, 1.0]
    labels = ["0%", "1-20%", "21-40%", "41-60%", "61-80%", "81-100%"]
    df["discount_band"] = pd.cut(df["discount"], bins=bins, labels=labels)
    g = df.groupby("discount_band", observed=True).agg(
        avg_profit=("profit", "mean"), total_profit=("profit", "sum"), rows=("row_id", "count")
    ).round(2)
    return g.reset_index().to_dict(orient="records")


# ─────────────────────────────────────────────────────────────────────────
# 3. Profit
# ─────────────────────────────────────────────────────────────────────────

@app.get("/api/profit/by-category", tags=["Profit"])
def profit_by_category(db: Session = Depends(get_db)):
    df = _orders_df(db)
    g = df.groupby("category").agg(sales=("sales", "sum"), profit=("profit", "sum")).round(2)
    g["margin_pct"] = (g["profit"] / g["sales"] * 100).round(2)
    return g.reset_index().to_dict(orient="records")


@app.get("/api/profit/loss-making-subcategories", tags=["Profit"])
def profit_loss_subcats(db: Session = Depends(get_db)):
    df = _orders_df(db)
    g = df.groupby("sub_category")["profit"].sum().round(2)
    loss = g[g < 0].sort_values()
    return [{"sub_category": k, "total_profit": v} for k, v in loss.items()]


@app.get("/api/profit/heatmap", tags=["Profit"])
def profit_heatmap(db: Session = Depends(get_db)):
    df = _orders_df(db)
    pivot = df.pivot_table(values="profit", index="segment", columns="category", aggfunc="sum").round(2)
    return pivot.reset_index().to_dict(orient="records")


# ─────────────────────────────────────────────────────────────────────────
# 4. Customers & RFM
# ─────────────────────────────────────────────────────────────────────────

@app.get("/api/customers/summary", tags=["Customers"])
def customers_summary(db: Session = Depends(get_db)):
    df = _orders_df(db)
    ltv = df.groupby("customer_id")["sales"].sum()
    return {
        "total_customers": int(df["customer_id"].nunique()),
        "avg_ltv": round(ltv.mean(), 2),
        "median_ltv": round(ltv.median(), 2),
        "top_ltv": round(ltv.max(), 2),
    }


@app.get("/api/customers/top", tags=["Customers"])
def customers_top(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    df = _orders_df(db)
    g = df.groupby(["customer_id", "customer_name"]).agg(
        ltv=("sales", "sum"), orders=("order_id", "nunique"), avg_order=("sales", "mean")
    ).round(2)
    return g.sort_values("ltv", ascending=False).head(limit).reset_index().to_dict(orient="records")


@app.get("/api/customers/{customer_id}", tags=["Customers"])
def customer_detail(customer_id: str, db: Session = Depends(get_db)):
    df = _orders_df(db)
    cdf = df[df["customer_id"] == customer_id]
    if cdf.empty:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {
        "customer_id": customer_id,
        "customer_name": cdf["customer_name"].iloc[0],
        "segment": cdf["segment"].iloc[0],
        "total_orders": int(cdf["order_id"].nunique()),
        "total_spend": round(float(cdf["sales"].sum()), 2),
        "total_profit": round(float(cdf["profit"].sum()), 2),
        "favorite_category": cdf.groupby("category")["sales"].sum().idxmax(),
        "last_order_date": cdf["order_date"].max().strftime("%Y-%m-%d"),
    }


@app.get("/api/customers/rfm/table", tags=["RFM Segmentation"])
def rfm_table(segment: Optional[str] = Query(None, description="Filter by RFM segment tier"),
              limit: int = Query(200, ge=1, le=2000), db: Session = Depends(get_db)):
    df = _orders_df(db)
    rfm = compute_rfm(df)
    if segment:
        rfm = rfm[rfm["Segment"] == segment]
    return rfm.head(limit).to_dict(orient="records")


@app.get("/api/customers/rfm/summary", tags=["RFM Segmentation"])
def rfm_summary_endpoint(db: Session = Depends(get_db)):
    df = _orders_df(db)
    rfm = compute_rfm(df)
    return rfm_summary(rfm)


@app.get("/api/customers/rfm/{customer_id}", tags=["RFM Segmentation"])
def rfm_customer(customer_id: str, db: Session = Depends(get_db)):
    df = _orders_df(db)
    rfm = compute_rfm(df)
    row = rfm[rfm["customer_id"] == customer_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Customer not found")
    return row.iloc[0].to_dict()


# ─────────────────────────────────────────────────────────────────────────
# 5. Products
# ─────────────────────────────────────────────────────────────────────────

@app.get("/api/products/top", tags=["Products"])
def products_top(by: str = Query("sales", pattern="^(sales|profit|quantity)$"),
                  limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    df = _orders_df(db)
    g = df.groupby(["product_id", "product_name", "category", "sub_category"]).agg(
        sales=("sales", "sum"), profit=("profit", "sum"), quantity=("quantity", "sum")
    ).round(2)
    return g.sort_values(by, ascending=False).head(limit).reset_index().to_dict(orient="records")


@app.get("/api/products/{product_id}", tags=["Products"])
def product_detail(product_id: str, db: Session = Depends(get_db)):
    df = _orders_df(db)
    pdf = df[df["product_id"] == product_id]
    if pdf.empty:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "product_id": product_id,
        "product_name": pdf["product_name"].iloc[0],
        "category": pdf["category"].iloc[0],
        "sub_category": pdf["sub_category"].iloc[0],
        "total_sales": round(float(pdf["sales"].sum()), 2),
        "total_profit": round(float(pdf["profit"].sum()), 2),
        "total_quantity": int(pdf["quantity"].sum()),
        "avg_discount_pct": round(float(pdf["discount"].mean() * 100), 2),
    }


# ─────────────────────────────────────────────────────────────────────────
# 6. Orders
# ─────────────────────────────────────────────────────────────────────────

@app.get("/api/orders", tags=["Orders"])
def list_orders(page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=200),
                 region: Optional[str] = None, category: Optional[str] = None,
                 db: Session = Depends(get_db)):
    q = db.query(OrderLine)
    if region:
        q = q.filter(OrderLine.region == region)
    if category:
        q = q.filter(OrderLine.category == category)
    total = q.count()
    rows = q.order_by(OrderLine.order_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = []
    for r in rows:
        items.append({
            "order_id": r.order_id, "order_date": str(r.order_date), "customer_name": r.customer_name,
            "product_name": r.product_name, "category": r.category, "sub_category": r.sub_category,
            "sales": r.sales, "profit": r.profit, "quantity": r.quantity, "region": r.region,
        })
    return {"page": page, "page_size": page_size, "total": total, "items": items}


@app.get("/api/orders/{order_id}", tags=["Orders"])
def order_detail(order_id: str, db: Session = Depends(get_db)):
    rows = db.query(OrderLine).filter(OrderLine.order_id == order_id).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Order not found")
    line_items = [{
        "product_name": r.product_name, "category": r.category, "sub_category": r.sub_category,
        "sales": r.sales, "profit": r.profit, "quantity": r.quantity, "discount": r.discount,
    } for r in rows]
    first = rows[0]
    return {
        "order_id": order_id, "order_date": str(first.order_date), "ship_date": str(first.ship_date),
        "ship_mode": first.ship_mode, "customer_name": first.customer_name, "region": first.region,
        "state": first.state, "city": first.city,
        "total_sales": round(sum(r.sales for r in rows), 2),
        "total_profit": round(sum(r.profit for r in rows), 2),
        "line_items": line_items,
    }


# ─────────────────────────────────────────────────────────────────────────
# 7. Power BI export trigger
# ─────────────────────────────────────────────────────────────────────────

@app.post("/api/export/powerbi", tags=["Export"])
def export_powerbi(db: Session = Depends(get_db)):
    """Regenerates the Power BI-ready CSVs (fact + dimension tables) on disk."""
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "powerbi"))
    from export_powerbi import run_export  # local import to avoid circular deps

    df = _orders_df(db)
    out_dir = run_export(df)
    return {"status": "ok", "output_dir": out_dir}

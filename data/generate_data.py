"""
generate_data.py
-----------------
Generates a realistic Superstore-schema retail dataset (same 21 columns as the
classic "Sample Superstore" dataset used throughout this project).

Why this exists: the original Kaggle Superstore CSV is not redistributable /
fetchable from this environment. This script produces a statistically similar
synthetic dataset so the entire platform (notebook, FastAPI backend, RFM
engine, React dashboard, Power BI export) runs end-to-end out of the box.

>>> If you have the real Superstore CSV, just drop it in as
    data/superstore.csv with the same column names and skip this script.

Usage:
    python generate_data.py
"""

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

N_ROWS = 9994  # match the classic Superstore row count

# ── Reference dimensions ────────────────────────────────────────────────
REGIONS = {
    "West": ["California", "Washington", "Oregon", "Nevada", "Arizona", "Colorado", "Utah"],
    "East": ["New York", "Pennsylvania", "New Jersey", "Massachusetts", "Connecticut", "Maine"],
    "Central": ["Texas", "Illinois", "Ohio", "Michigan", "Indiana", "Wisconsin", "Minnesota"],
    "South": ["Florida", "Georgia", "North Carolina", "Virginia", "Tennessee", "Alabama"],
}

CITIES_BY_STATE = {
    "California": ["Los Angeles", "San Francisco", "San Diego", "Sacramento"],
    "Washington": ["Seattle", "Spokane", "Tacoma"],
    "Oregon": ["Portland", "Eugene"],
    "Nevada": ["Las Vegas", "Reno"],
    "Arizona": ["Phoenix", "Tucson"],
    "Colorado": ["Denver", "Boulder"],
    "Utah": ["Salt Lake City"],
    "New York": ["New York City", "Buffalo", "Albany"],
    "Pennsylvania": ["Philadelphia", "Pittsburgh"],
    "New Jersey": ["Newark", "Jersey City"],
    "Massachusetts": ["Boston", "Cambridge"],
    "Connecticut": ["Hartford"],
    "Maine": ["Portland"],
    "Texas": ["Houston", "Dallas", "Austin", "San Antonio"],
    "Illinois": ["Chicago", "Springfield"],
    "Ohio": ["Columbus", "Cleveland", "Cincinnati"],
    "Michigan": ["Detroit", "Grand Rapids"],
    "Indiana": ["Indianapolis"],
    "Wisconsin": ["Milwaukee", "Madison"],
    "Minnesota": ["Minneapolis", "Saint Paul"],
    "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville"],
    "Georgia": ["Atlanta", "Savannah"],
    "North Carolina": ["Charlotte", "Raleigh"],
    "Virginia": ["Richmond", "Virginia Beach"],
    "Tennessee": ["Nashville", "Memphis"],
    "Alabama": ["Birmingham", "Montgomery"],
}

CATEGORY_TREE = {
    "Furniture": {
        "Bookcases": (200, 700),
        "Chairs": (80, 500),
        "Tables": (150, 900),
        "Furnishings": (20, 150),
    },
    "Office Supplies": {
        "Storage": (30, 250),
        "Supplies": (5, 80),
        "Paper": (2, 40),
        "Binders": (3, 60),
        "Art": (2, 50),
        "Envelopes": (2, 30),
        "Fasteners": (1, 15),
        "Labels": (1, 20),
    },
    "Technology": {
        "Phones": (80, 900),
        "Copiers": (400, 3500),
        "Machines": (200, 2800),
        "Accessories": (15, 300),
    },
}

PRODUCT_ADJ = ["Premium", "Deluxe", "Standard", "Executive", "Compact", "Ergonomic",
               "Classic", "ProSeries", "EcoLine", "HeavyDuty"]

SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SHIP_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]
SHIP_MODE_LAG = {"Same Day": (0, 1), "First Class": (1, 3), "Second Class": (2, 5), "Standard Class": (4, 8)}

FIRST_NAMES = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
               "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
               "Thomas", "Sarah", "Charles", "Karen", "Ananya", "Ravi", "Priya", "Arjun", "Wei",
               "Mei", "Carlos", "Sofia", "Liam", "Olivia"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Rodriguez", "Martinez", "Wilson", "Anderson", "Taylor", "Thomas", "Moore",
              "Jackson", "Martin", "Lee", "Perez", "Thompson", "Rao", "Iyer", "Kapoor", "Chen",
              "Nguyen", "Kim", "Singh", "Patel", "Reddy", "Sharma"]

# ── Build a realistic customer base (customers make repeat purchases) ──
N_CUSTOMERS = 800
customers = []
for i in range(N_CUSTOMERS):
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    cust_id = f"CU-{10000 + i}"
    segment = random.choices(SEGMENTS, weights=[0.55, 0.30, 0.15])[0]
    customers.append((cust_id, name, segment))

# ── Build a product catalog ─────────────────────────────────────────────
products = []
pid_counter = 1
for category, subcats in CATEGORY_TREE.items():
    for subcat, price_range in subcats.items():
        n_products = random.randint(15, 30)
        for _ in range(n_products):
            name = f"{random.choice(PRODUCT_ADJ)} {subcat[:-1] if subcat.endswith('s') else subcat} {random.randint(100,999)}"
            pid = f"{category[:3].upper()}-{subcat[:2].upper()}-{pid_counter:05d}"
            pid_counter += 1
            products.append((pid, name, category, subcat, price_range))

# ── Date range: 4 full years ─────────────────────────────────────────────
START_DATE = datetime(2021, 1, 1)
END_DATE = datetime(2024, 12, 30)
DATE_SPAN = (END_DATE - START_DATE).days


def random_date():
    # Slight seasonality: bias toward Nov/Dec (holiday season) and back-to-school (Aug/Sep)
    d = START_DATE + timedelta(days=random.randint(0, DATE_SPAN))
    if random.random() < 0.15:
        year = random.choice(range(2021, 2025))
        d = datetime(year, 11, random.randint(1, 28)) if random.random() < 0.5 else datetime(year, 12, random.randint(1, 24))
    return d


rows = []
order_counter = 1
row_id = 1
n_orders = N_ROWS // 3  # ~3 line items per order on average

for _ in range(n_orders):
    cust_id, cust_name, segment = random.choice(customers)
    region = random.choice(list(REGIONS.keys()))
    state = random.choice(REGIONS[region])
    city = random.choice(CITIES_BY_STATE[state])
    order_date = random_date()
    ship_mode = random.choices(SHIP_MODES, weights=[0.55, 0.20, 0.18, 0.07])[0]
    lag_lo, lag_hi = SHIP_MODE_LAG[ship_mode]
    ship_date = order_date + timedelta(days=random.randint(lag_lo, lag_hi))
    order_id = f"US-{order_date.year}-{100000 + order_counter}"
    order_counter += 1

    n_items = random.choices([1, 2, 3, 4, 5], weights=[0.35, 0.30, 0.18, 0.12, 0.05])[0]
    for _ in range(n_items):
        pid, pname, category, subcat, (price_lo, price_hi) = random.choice(products)
        quantity = random.randint(1, 12)
        unit_price = round(random.uniform(price_lo, price_hi), 2)
        # discount distribution: mostly none/low, occasional deep discount
        discount = random.choices(
            [0.0, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
            weights=[0.42, 0.13, 0.10, 0.12, 0.08, 0.06, 0.04, 0.02, 0.02, 0.01],
        )[0]
        sales = round(unit_price * quantity * (1 - discount * 0.15), 2)  # discount lightly affects list->sales
        # base margin varies by category; deep discounts erode / flip profit negative
        base_margin = {"Technology": 0.22, "Office Supplies": 0.18, "Furniture": 0.12}[category]
        margin = base_margin - discount * 0.9 + np.random.normal(0, 0.05)
        profit = round(sales * margin, 2)

        rows.append({
            "Row ID": row_id,
            "Order ID": order_id,
            "Order Date": order_date.strftime("%Y-%m-%d"),
            "Ship Date": ship_date.strftime("%Y-%m-%d"),
            "Ship Mode": ship_mode,
            "Customer ID": cust_id,
            "Customer Name": cust_name,
            "Segment": segment,
            "Country": "United States",
            "City": city,
            "State": state,
            "Postal Code": f"{random.randint(10000, 99999)}",
            "Region": region,
            "Product ID": pid,
            "Category": category,
            "Sub-Category": subcat,
            "Product Name": pname,
            "Sales": sales,
            "Quantity": quantity,
            "Discount": discount,
            "Profit": profit,
        })
        row_id += 1
        if row_id > N_ROWS:
            break
    if row_id > N_ROWS:
        break

df = pd.DataFrame(rows)
df.to_csv("superstore.csv", index=False)
print(f"✅ Generated data/superstore.csv — {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"   Orders: {df['Order ID'].nunique():,}   Customers: {df['Customer ID'].nunique():,}   Products: {df['Product ID'].nunique():,}")
print(f"   Date range: {df['Order Date'].min()} → {df['Order Date'].max()}")

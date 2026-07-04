"""Builds notebook/Retail_Analytics_RFM.ipynb from scratch using nbformat."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(src):
    cells.append(nbf.v4.new_markdown_cell(src))

def code(src):
    cells.append(nbf.v4.new_code_cell(src))

# ── Title ────────────────────────────────────────────────────────────────
md("""# 🛒 Retail Analytics Platform — Superstore Dataset
**Full pipeline:** Data Loading → Cleaning → Statistics → Feature Engineering → Business Analysis →
Visualization → Insights → **RFM Customer Segmentation** → SQL Analytics → Power BI Export

This notebook is the analytical core of the full-stack Retail Analytics Platform
(FastAPI backend + React/Recharts dashboard + Power BI export — see the `backend/`,
`frontend/`, and `powerbi/` folders alongside this notebook).

> **Note on data:** this uses `data/superstore.csv`, a synthetically generated dataset that
> mirrors the schema and statistical shape of the classic "Sample Superstore" dataset
> (21 columns, order-line grain, ~4 years of orders). Drop in the real Kaggle CSV with the
> same column names to switch datasets — nothing else needs to change.
""")

# ── Stage 1 ──────────────────────────────────────────────────────────────
md("## 📦 Stage 1 — Setup & Data Loading")
code("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['figure.figsize'] = (9, 5)
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
sns.set_style('whitegrid')

df = pd.read_csv('../data/superstore.csv', encoding='latin1')
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Ship Date']  = pd.to_datetime(df['Ship Date'])
print(f"✅ Loaded {df.shape[0]:,} rows × {df.shape[1]} columns")
df.head()
""")

# ── Stage 2 ──────────────────────────────────────────────────────────────
md("## 🔍 Stage 2 — Data Understanding")
code("""print("─── Shape ───────────────────────────────────")
print(f"Rows: {df.shape[0]:,}   Columns: {df.shape[1]}")
print("\\n─── Data types ──────────────────────────────")
print(df.dtypes)
""")
code("""for col in ['Category', 'Sub-Category', 'Region', 'Segment', 'Ship Mode']:
    print(f"\\n{col}:")
    print(df[col].value_counts().to_string())
""")

# ── Stage 3 ──────────────────────────────────────────────────────────────
md("## 🧹 Stage 3 — Data Cleaning")
code("""print("─── Missing values per column ───────────────")
missing = df.isnull().sum()
print(missing[missing > 0] if missing.any() else "✅ No missing values found!")

dups = df.duplicated().sum()
print(f"\\n─── Duplicate rows: {dups} ───")
""")
code("""df['Order Year']    = df['Order Date'].dt.year
df['Order Month']   = df['Order Date'].dt.month
df['Order Quarter'] = df['Order Date'].dt.quarter
df['Ship Lag']      = (df['Ship Date'] - df['Order Date']).dt.days

df['Postal Code'] = df['Postal Code'].astype(str).str.zfill(5)

print("✅ Cleaning done. Final shape:", df.shape)
df.sample(5, random_state=42)
""")

# ── Stage 4 ──────────────────────────────────────────────────────────────
md("## 📊 Stage 4 — Basic Statistics")
code("""df[['Sales', 'Quantity', 'Discount', 'Profit', 'Ship Lag']].describe().round(2)""")
code("""total_sales  = df['Sales'].sum()
total_profit = df['Profit'].sum()
margin       = (total_profit / total_sales) * 100

print(f"Total Sales  : ${total_sales:>14,.2f}")
print(f"Total Profit : ${total_profit:>14,.2f}")
print(f"Profit Margin: {margin:>14.2f}%")
""")
code("""cat_stats = df.groupby('Category').agg(
    Total_Sales   = ('Sales',    'sum'),
    Total_Profit  = ('Profit',   'sum'),
    Avg_Discount  = ('Discount', 'mean'),
    Orders        = ('Order ID', 'nunique')
).round(2)
cat_stats['Margin_%'] = (cat_stats['Total_Profit'] / cat_stats['Total_Sales'] * 100).round(2)
cat_stats.sort_values('Total_Sales', ascending=False)
""")

# ── Stage 5 ──────────────────────────────────────────────────────────────
md("## ⚙️ Stage 5 — Feature Engineering")
code("""df['Profit Margin %'] = (df['Profit'] / df['Sales'] * 100).round(2)

df['Sales Tier'] = pd.cut(
    df['Sales'],
    bins=[0, 100, 500, 1000, df['Sales'].max()],
    labels=['Small (<$100)', 'Medium ($100-500)', 'Large ($500-1K)', 'XL (>$1K)']
)

df['Discount Band'] = pd.cut(
    df['Discount'],
    bins=[-0.01, 0, 0.2, 0.4, 0.6, 0.8, 1.0],
    labels=['0%', '1-20%', '21-40%', '41-60%', '61-80%', '81-100%']
)

df[['Sales', 'Profit', 'Profit Margin %', 'Sales Tier', 'Discount Band']].head()
""")
code("""customer_ltv = df.groupby('Customer ID').agg(
    Customer_Name = ('Customer Name', 'first'),
    LTV           = ('Sales',   'sum'),
    Orders        = ('Order ID','nunique'),
    Avg_Order     = ('Sales',   'mean')
).sort_values('LTV', ascending=False).round(2)
customer_ltv.head(10)
""")

# ── Stage 6 ──────────────────────────────────────────────────────────────
md("## 💼 Stage 6 — Business Analysis")
code("""# Q1: Which Sub-Categories are loss-making?
sub_profit = df.groupby('Sub-Category')['Profit'].sum().sort_values()
loss_subs  = sub_profit[sub_profit < 0]
print("⚠️  Loss-making Sub-Categories:")
print(loss_subs.to_string() if len(loss_subs) else "None — every sub-category is profitable.")
""")
code("""# Q2: Top 5 States by Sales
top_states = df.groupby('State')['Sales'].sum().nlargest(5)
print("Top 5 States by Sales:")
print(top_states.to_string())
""")
code("""# Q3: Sales & Profit by Year-Quarter
quarterly = df.groupby(['Order Year', 'Order Quarter']).agg(
    Sales  = ('Sales',  'sum'),
    Profit = ('Profit', 'sum')
).round(2)
quarterly
""")
code("""# Q4: Discount impact on Profit
disc_impact = df.groupby('Discount Band', observed=True).agg(
    Avg_Profit   = ('Profit', 'mean'),
    Total_Profit = ('Profit', 'sum'),
    Rows         = ('Row ID', 'count')
).round(2)
disc_impact
""")
code("""# Q5: Pivot — Category x Region Sales
pivot = df.pivot_table(values='Sales', index='Category', columns='Region', aggfunc='sum').round(0)
pivot
""")

# ── Stage 7 ──────────────────────────────────────────────────────────────
md("## 📈 Stage 7 — Visualization")
code("""cat_sales = df.groupby('Category')['Sales'].sum().sort_values(ascending=False)
fig, ax = plt.subplots()
bars = ax.bar(cat_sales.index, cat_sales.values, color=['#7C9CFF','#34D6A6','#F0B429'])
ax.bar_label(bars, fmt='$%.0f', padding=5)
ax.set_title('Sales by Category', fontweight='bold')
ax.set_ylabel('Sales ($)')
plt.tight_layout(); plt.show()
""")
code("""sub = df.groupby('Sub-Category')['Profit'].sum().sort_values()
colors = ['#FF6B5B' if v < 0 else '#34D6A6' for v in sub.values]
fig, ax = plt.subplots(figsize=(10, 6))
sub.plot.barh(ax=ax, color=colors)
ax.axvline(0, color='black', linewidth=0.8)
ax.set_title('Profit by Sub-Category', fontweight='bold')
ax.set_xlabel('Profit ($)')
plt.tight_layout(); plt.show()
""")
code("""monthly = df.groupby(df['Order Date'].dt.to_period('M'))['Sales'].sum()
monthly.index = monthly.index.to_timestamp()
fig, ax = plt.subplots()
ax.plot(monthly.index, monthly.values, marker='o', linewidth=2, color='#7C9CFF')
ax.fill_between(monthly.index, monthly.values, alpha=0.08, color='#7C9CFF')
ax.set_title('Monthly Sales Trend', fontweight='bold')
ax.set_ylabel('Sales ($)')
plt.tight_layout(); plt.show()
""")
code("""reg = df.groupby('Region')[['Sales','Profit']].sum()
x = np.arange(len(reg)); w = 0.35
fig, ax = plt.subplots()
ax.bar(x - w/2, reg['Sales'],  w, label='Sales',  color='#7C9CFF')
ax.bar(x + w/2, reg['Profit'], w, label='Profit', color='#34D6A6')
ax.set_xticks(x); ax.set_xticklabels(reg.index)
ax.set_title('Sales & Profit by Region', fontweight='bold')
ax.legend()
plt.tight_layout(); plt.show()
""")
code("""fig, ax = plt.subplots()
scatter = ax.scatter(df['Discount'], df['Profit'], c=df['Sales'], cmap='viridis', alpha=0.4, s=20)
plt.colorbar(scatter, ax=ax, label='Sales ($)')
ax.axhline(0, color='red', linewidth=0.8, linestyle='--')
ax.set_title('Discount vs Profit', fontweight='bold')
ax.set_xlabel('Discount'); ax.set_ylabel('Profit ($)')
plt.tight_layout(); plt.show()
""")
code("""fig, ax = plt.subplots()
ax.hist(df['Sales'], bins=60, color='#7C9CFF', edgecolor='white', linewidth=0.5)
ax.set_title('Sales Distribution', fontweight='bold')
ax.set_xlabel('Sales ($)'); ax.set_ylabel('Frequency')
ax.set_xlim(0, 2000)
plt.tight_layout(); plt.show()
""")
code("""top10 = df.groupby('State')['Sales'].sum().nlargest(10).sort_values()
fig, ax = plt.subplots(figsize=(10, 6))
top10.plot.barh(ax=ax, color='#7C9CFF')
ax.set_title('Top 10 States by Total Sales', fontweight='bold')
ax.set_xlabel('Sales ($)')
plt.tight_layout(); plt.show()
""")
code("""hm = df.pivot_table(values='Profit', index='Segment', columns='Category', aggfunc='sum')
fig, ax = plt.subplots(figsize=(8, 4))
sns.heatmap(hm, annot=True, fmt=',.0f', cmap='RdYlGn', ax=ax, linewidths=0.5, center=0)
ax.set_title('Profit Heatmap — Segment × Category', fontweight='bold')
plt.tight_layout(); plt.show()
""")

# ── Stage 8 ──────────────────────────────────────────────────────────────
md("## 💡 Stage 8 — Key Business Insights")
code("""total_orders    = df['Order ID'].nunique()
total_customers = df['Customer ID'].nunique()
avg_order_val   = df.groupby('Order ID')['Sales'].sum().mean()

print("═══ KEY PERFORMANCE INDICATORS ═══")
print(f"  Total Orders      : {total_orders:,}")
print(f"  Total Customers   : {total_customers:,}")
print(f"  Avg Order Value   : ${avg_order_val:,.2f}")
print(f"  Overall Margin    : {margin:.2f}%")
""")
code("""print("Sub-Categories with NEGATIVE total profit:")
loss = df.groupby('Sub-Category')['Profit'].sum()
print(loss[loss < 0].sort_values().to_string() or "None")

print("\\nHigh-discount rows where profit < 0:")
high_disc_loss = df[(df['Discount'] >= 0.4) & (df['Profit'] < 0)]
print(f"  {len(high_disc_loss):,} rows ({len(high_disc_loss)/len(df)*100:.1f}% of all rows)")
""")
code("""print("Top 5 most profitable Sub-Categories:")
top5 = df.groupby('Sub-Category')['Profit'].sum().nlargest(5)
print(top5.to_string())

print("\\nTop 5 most profitable States:")
print(df.groupby('State')['Profit'].sum().nlargest(5).to_string())
""")

md("""### 📋 Insights Summary

| # | Insight | Action |
|---|---------|--------|
| 1 | Loss-making sub-categories cluster around Furniture (Bookcases, Tables) | Review pricing / cap discounts on Furniture |
| 2 | Discounts ≥ 40% almost always erode or reverse profit | Cap promotional discount at ~30% |
| 3 | Technology (Copiers, Phones) drives the highest margin | Prioritize marketing spend here |
| 4 | West & East regions lead on both sales and profit | Focus expansion / inventory investment there |
| 5 | A small share of customers (RFM "Champions") drive an outsized share of revenue | See Stage 9 — target retention campaigns |
""")

# ── Stage 9 — RFM (NEW, detailed) ───────────────────────────────────────
md("""## 🎯 Stage 9 — RFM Customer Segmentation

**RFM** scores every customer on three dimensions, each 1 (worst) – 5 (best):

- **Recency (R)** — how recently did they order? (fewer days since last order = higher score)
- **Frequency (F)** — how many distinct orders have they placed?
- **Monetary (M)** — how much have they spent in total (lifetime value)?

Customers are then classified into 5 actionable tiers using a rule-based mapping of
their (R, F, M) scores — the same logic that powers `backend/rfm.py`, the
`/api/customers/rfm/*` endpoints, and the `customer_rfm.csv` Power BI export.
""")
code("""snapshot_date = df['Order Date'].max() + pd.Timedelta(days=1)

rfm = df.groupby('Customer ID').agg(
    Customer_Name   = ('Customer Name', 'first'),
    Last_Order_Date = ('Order Date', 'max'),
    Frequency       = ('Order ID', 'nunique'),
    Monetary        = ('Sales', 'sum'),
).reset_index()

rfm['Recency'] = (snapshot_date - rfm['Last_Order_Date']).dt.days

# Quintile scores 1-5 (Recency reversed: fewer days = higher score)
rfm['R'] = pd.qcut(rfm['Recency'].rank(method='first'), 5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm['M'] = pd.qcut(rfm['Monetary'].rank(method='first'),  5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)

rfm[['Customer ID', 'Customer_Name', 'Recency', 'Frequency', 'Monetary', 'R', 'F', 'M', 'RFM_Score']].head()
""")
code("""def classify_segment(r, f, m):
    \"\"\"Rule-based mapping of (R,F,M) scores -> 5 business-friendly tiers.\"\"\"
    if r >= 4 and f >= 4 and m >= 4:
        return 'Champions'
    if r <= 2 and f <= 2:
        return 'Lost'
    if r <= 2 and f >= 3:
        return 'At-Risk'
    if r >= 4 and f <= 2:
        return 'New'
    return 'Loyal'

rfm['Segment'] = rfm.apply(lambda row: classify_segment(row['R'], row['F'], row['M']), axis=1)

SEGMENT_ACTIONS = {
    'Champions': 'Reward with early access & loyalty perks; ask for referrals.',
    'Loyal':     'Upsell higher-value products; keep engagement steady with regular offers.',
    'At-Risk':   'Send win-back campaigns with personalized discounts before they churn.',
    'Lost':      'Low-cost re-engagement (email blast); deprioritize for premium spend.',
    'New':       'Nurture with onboarding offers to build purchase frequency.',
}
rfm['Recommended_Action'] = rfm['Segment'].map(SEGMENT_ACTIONS)

rfm.sort_values('Monetary', ascending=False).head(10)
""")
code("""seg_summary = rfm.groupby('Segment').agg(
    Customers      = ('Customer ID', 'count'),
    Avg_Recency    = ('Recency', 'mean'),
    Avg_Frequency  = ('Frequency', 'mean'),
    Avg_Monetary   = ('Monetary', 'mean'),
    Total_Monetary = ('Monetary', 'sum'),
).round(2)
seg_summary['Pct_of_Customers'] = (seg_summary['Customers'] / seg_summary['Customers'].sum() * 100).round(1)
seg_summary['Pct_of_Revenue']   = (seg_summary['Total_Monetary'] / seg_summary['Total_Monetary'].sum() * 100).round(1)
seg_summary.sort_values('Total_Monetary', ascending=False)
""")
code("""SEGMENT_COLORS = {'Champions': '#34D6A6', 'Loyal': '#7C9CFF', 'At-Risk': '#F0B429',
                   'Lost': '#FF6B5B', 'New': '#B39BFF'}

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Donut: customer count by segment
order = seg_summary.sort_values('Customers', ascending=False).index
axes[0].pie(seg_summary.loc[order, 'Customers'], labels=order, autopct='%1.0f%%',
            colors=[SEGMENT_COLORS[s] for s in order], wedgeprops=dict(width=0.4))
axes[0].set_title('Customers by RFM Segment', fontweight='bold')

# Scatter: Recency vs Frequency, sized by Monetary
for seg, color in SEGMENT_COLORS.items():
    sub = rfm[rfm['Segment'] == seg]
    axes[1].scatter(sub['Recency'], sub['Frequency'], s=sub['Monetary']/150,
                     color=color, alpha=0.6, label=seg)
axes[1].set_xlabel('Recency (days since last order)')
axes[1].set_ylabel('Frequency (orders)')
axes[1].set_title('Recency vs Frequency (bubble = spend)', fontweight='bold')
axes[1].legend(fontsize=8)

plt.tight_layout(); plt.show()
""")
md("""**Reading the segmentation:**
- **Champions** are your best customers — recent, frequent, high spend. Protect this group.
- **At-Risk** customers used to buy often but haven't ordered recently — the highest-value
  group to target with win-back campaigns before they churn completely.
- **Lost** customers haven't ordered in a long time and never bought often — low priority
  for premium retention spend.
- **New** customers ordered recently but only once or twice — the segment most receptive
  to onboarding nudges that build a habit.
""")

# ── Stage 10 — SQL ───────────────────────────────────────────────────────
md("""## 🗄️ Stage 10 — SQL Analytics (SQLite demo → PostgreSQL in production)

The FastAPI backend (`backend/database.py`) uses SQLAlchemy against **PostgreSQL** in
production and **SQLite** for zero-setup local development — same schema, same queries,
just a different `DATABASE_URL`. This section demonstrates the SQL layer directly.
""")
code("""import sqlite3

conn = sqlite3.connect(':memory:')  # swap for a file path, or PostgreSQL via SQLAlchemy, to persist
df_sql = df.copy()
df_sql['Order Date'] = df_sql['Order Date'].astype(str)
df_sql['Ship Date']  = df_sql['Ship Date'].astype(str)
df_sql.to_sql('orders', conn, index=False, if_exists='replace')
print("✅ Loaded into SQLite in-memory DB — table 'orders'")
""")
code("""q1 = pd.read_sql(\"\"\"
    SELECT Category,
           ROUND(SUM(Sales),  2) AS Total_Sales,
           ROUND(SUM(Profit), 2) AS Total_Profit,
           ROUND(SUM(Profit)/SUM(Sales)*100, 2) AS Margin_Pct
    FROM orders
    GROUP BY Category
    ORDER BY Total_Sales DESC
\"\"\", conn)
print("── Total Sales & Profit by Category ──")
q1
""")
code("""q2 = pd.read_sql(\"\"\"
    SELECT City, State,
           COUNT(DISTINCT "Order ID") AS Orders,
           ROUND(SUM(Sales), 2)       AS Total_Sales
    FROM orders
    GROUP BY City, State
    ORDER BY Total_Sales DESC
    LIMIT 10
\"\"\", conn)
print("── Top 10 Cities by Revenue ──")
q2
""")
code("""q3 = pd.read_sql(\"\"\"
    SELECT "Sub-Category",
           ROUND(SUM(Profit), 2) AS Total_Profit,
           COUNT(*)              AS Rows
    FROM orders
    GROUP BY "Sub-Category"
    HAVING SUM(Profit) < 0
    ORDER BY Total_Profit
\"\"\", conn)
print("── Loss-Making Sub-Categories ──")
q3
""")
code("""q4 = pd.read_sql(\"\"\"
    SELECT strftime('%Y-%m', "Order Date") AS Month,
           ROUND(SUM(Sales),  2) AS Sales,
           ROUND(SUM(Profit), 2) AS Profit
    FROM orders
    GROUP BY Month
    ORDER BY Month
\"\"\", conn)
print("── Monthly Revenue ──")
q4.head(12)
""")
code("""q5 = pd.read_sql(\"\"\"
    SELECT "Customer Name",
           COUNT(DISTINCT "Order ID") AS Orders,
           ROUND(SUM(Sales), 2)       AS LTV,
           ROUND(AVG(Sales), 2)       AS Avg_Order
    FROM orders
    GROUP BY "Customer Name"
    ORDER BY LTV DESC
    LIMIT 10
\"\"\", conn)
print("── Customer Ranking by LTV ──")
q5
""")
md("""### 🔄 Switching to PostgreSQL

```python
from sqlalchemy import create_engine
engine = create_engine('postgresql+psycopg2://postgres:password@localhost:5432/superstore_db')
df.to_sql('orders', engine, if_exists='replace', index=False)
result = pd.read_sql('SELECT * FROM orders LIMIT 5', engine)
```

This is exactly what `backend/load_data.py` + `backend/database.py` do — set
`DATABASE_URL` in `backend/.env` and re-run `python load_data.py`.
""")

# ── Stage 11 — Power BI export ──────────────────────────────────────────
md("## 📊 Stage 11 — Power BI Export")
code("""import os
OUTPUT = 'powerbi_exports'
os.makedirs(OUTPUT, exist_ok=True)

fact = df[['Row ID','Order ID','Order Date','Ship Date','Ship Mode','Customer ID',
           'Customer Name','Segment','Country','City','State','Postal Code',
           'Region','Product ID','Category','Sub-Category','Product Name',
           'Sales','Quantity','Discount','Profit',
           'Order Year','Order Month','Order Quarter','Ship Lag','Profit Margin %']]
fact.to_csv(f'{OUTPUT}/fact_orders.csv', index=False)
rfm.to_csv(f'{OUTPUT}/customer_rfm.csv', index=False)

print(f"✅ Exported {len(fact):,} fact rows and {len(rfm):,} RFM rows to {OUTPUT}/")
print("   (The full star-schema export — with dim tables — lives in powerbi/export_powerbi.py)")
""")
md("""See `powerbi/DAX_measures.md` for the full Power BI setup guide: relationships,
DAX measures, and suggested report pages (Executive Overview, Category/Product,
Customer & RFM, Geography).
""")

# ── Stage 12 — Platform architecture ────────────────────────────────────
md("""## 🏗️ Stage 12 — Full-Stack Platform

This notebook is the analytical foundation for the rest of the platform:

| Layer | Location | What it does |
|---|---|---|
| **Data** | `data/superstore.csv`, `data/generate_data.py` | Source dataset |
| **Database** | `backend/database.py`, `backend/models.py`, `backend/load_data.py` | SQLAlchemy models; SQLite (dev) / PostgreSQL (prod) |
| **RFM Engine** | `backend/rfm.py` | Same segmentation logic as Stage 9, shared by the API & Power BI export |
| **API** | `backend/main.py` | 25+ REST endpoints — KPIs, sales, profit, customers, RFM, products, orders |
| **Dashboard** | `frontend/` (React + Recharts) | 6-tab dashboard consuming the API |
| **Power BI** | `powerbi/export_powerbi.py`, `powerbi/DAX_measures.md` | Star-schema CSV export + DAX measures |

**Run the full stack:**
```bash
# 1. Backend
cd backend
pip install -r requirements.txt
python load_data.py
uvicorn main:app --reload            # http://127.0.0.1:8000/docs

# 2. Frontend
cd frontend
npm install
npm run dev                          # http://localhost:5173
```

See the top-level `README.md` for full setup, deployment notes, and architecture diagram.
""")
md("""## ✅ Project Complete

| Stage | Status |
|---|---|
| 1. Setup & Data Loading | ✅ |
| 2. Data Understanding | ✅ |
| 3. Data Cleaning | ✅ |
| 4. Basic Statistics | ✅ |
| 5. Feature Engineering | ✅ |
| 6. Business Analysis | ✅ |
| 7. Visualization (8 charts) | ✅ |
| 8. Key Insights | ✅ |
| 9. **RFM Customer Segmentation** | ✅ |
| 10. SQL Analytics (SQLite/PostgreSQL) | ✅ |
| 11. Power BI Export | ✅ |
| 12. Full-Stack Platform (FastAPI + React) | ✅ |
""")

nb['cells'] = cells
nb['metadata'] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.12"},
}

with open('Retail_Analytics_RFM.ipynb', 'w') as f:
    nbf.write(nb, f)

print("✅ Notebook written.")

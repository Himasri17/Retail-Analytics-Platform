# Retail Analytics Platform

A full-stack analytics platform built on the Superstore dataset — Python · FastAPI ·
PostgreSQL · React · Recharts · Power BI · Jupyter.

- **25+ REST API endpoints** serving sales, customer, product and RFM KPIs to a React
  dashboard with Recharts visualizations and a Power BI export pipeline.
- **RFM (Recency, Frequency, Monetary) customer segmentation** in Python/Pandas —
  classifying customers into 5 tiers (Champions, Loyal, At-Risk, Lost, New) to support
  targeted marketing decisions.

```
retail-analytics-platform/
├── data/               synthetic Superstore-schema dataset + generator
├── notebook/           full analysis notebook (cleaning → RFM → SQL → Power BI)
├── backend/             FastAPI + SQLAlchemy (PostgreSQL/SQLite) REST API
├── frontend/            React + Recharts dashboard ("Ledger")
├── powerbi/              star-schema CSV export + DAX measures guide
└── README.md            (this file)
```

## About the data

`data/superstore.csv` is the real, classic Kaggle **"Sample Superstore"** dataset (9,994
rows, 21 columns, orders from 2014–2017). All numbers in the notebook, API, and
dashboard are computed from it directly.

`data/generate_data.py` is also included as a fallback: it produces a synthetic dataset
with the exact same schema, in case you ever need to regenerate or replace the data (e.g.
for testing with a larger or different sample). Just run `python3 generate_data.py`
inside `data/` and it will overwrite `superstore.csv` — swap back to the real file by
re-copying it if needed.

## Quick start

### 1. Generate the data (already included, re-run if you want a different sample)

```bash
cd data
python3 generate_data.py
```

### 2. Backend — FastAPI + SQLAlchemy

```bash
cd backend
python -m venv venv &&  .\venv\Scripts\Activate.ps1   # optional but recommended
pip install -r requirements.txt

cp .env.example .env          # defaults to local SQLite — zero setup
python3 load_data.py          # loads data/superstore.csv into the DB
uvicorn main:app --reload     # http://127.0.0.1:8000/docs (Swagger UI)
```

To use **PostgreSQL** instead of SQLite, edit `backend/.env`:
```
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/superstore_db
```
then re-run `python3 load_data.py`.

### 3. Frontend — React + Recharts

```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173
```

The dashboard expects the API at `http://localhost:8000` (set `VITE_API_URL` in a
`.env` file inside `frontend/` to point elsewhere).

### 4. Notebook — full analysis + RFM

```bash
cd notebook
jupyter notebook Retail_Analytics_RFM.ipynb
```
Covers: data cleaning → statistics → feature engineering → business analysis → 8
visualizations → key insights → **RFM segmentation** → SQL analytics (SQLite/PostgreSQL)
→ Power BI export.

### 5. Power BI export

```bash
cd powerbi
python3 export_powerbi.py
```
Writes a 6-table star schema (`fact_orders`, 4 dimension tables, `customer_rfm`) to
`powerbi/exports/`. See `powerbi/DAX_measures.md` for the import steps, relationships,
and ready-to-paste DAX measures. You can also trigger a fresh export from the running
API: `POST http://localhost:8000/api/export/powerbi`.

## API overview

| Group | Example endpoints |
|---|---|
| Meta | `GET /api/health`, `GET /api/meta/filters` |
| KPIs | `GET /api/kpis/summary`, `GET /api/kpis/monthly-trend`, `GET /api/kpis/yearly-trend` |
| Sales | `GET /api/sales/by-category`, `by-region`, `by-state`, `by-segment`, `by-ship-mode`, `top-products`, `discount-impact` |
| Profit | `GET /api/profit/by-category`, `loss-making-subcategories`, `heatmap` |
| Customers | `GET /api/customers/summary`, `top`, `{customer_id}` |
| **RFM** | `GET /api/customers/rfm/table`, `/summary`, `/{customer_id}` |
| Products | `GET /api/products/top`, `{product_id}` |
| Orders | `GET /api/orders`, `{order_id}` |
| Export | `POST /api/export/powerbi` |

Full interactive docs at `http://127.0.0.1:8000/docs` once the backend is running.

## RFM segmentation logic

Every customer gets a 1–5 quintile score on Recency, Frequency, and Monetary value, then
a rule-based classifier (`backend/rfm.py`, mirrored in the notebook's Stage 9) assigns
one of 5 tiers:

| Segment | Rule | Suggested action |
|---|---|---|
| **Champions** | R≥4, F≥4, M≥4 | Reward with early access & loyalty perks; ask for referrals |
| **Loyal** | Everything not caught below | Upsell higher-value products; keep engagement steady |
| **At-Risk** | R≤2, F≥3 | Win-back campaigns before they churn |
| **Lost** | R≤2, F≤2 | Low-cost re-engagement; deprioritize premium spend |
| **New** | R≥4, F≤2 | Onboarding nudges to build purchase frequency |

The same logic runs in three places — the notebook, the API (`/api/customers/rfm/*`),
and the Power BI export — so all three stay consistent.

## Dashboard tabs

1. **Overview** — monthly sales/profit trend, sales by region & category, top states
2. **Sales** — segment & ship-mode breakdown, discount-impact analysis, top products
3. **Profit** — margin by category, loss-making sub-categories, segment×category heatmap
4. **Customers · RFM** — segment donut, recency/frequency scatter, segmentation table with playbook, top customers by LTV
5. **Products** — sortable top-products table (sales / profit / quantity)
6. **Orders** — paginated order-line detail

Filter by Region / Category / Segment from the top bar — filters apply to the KPI strip
across all tabs.

## Deployment notes

- **Backend**: containerize with the included `requirements.txt`; deploy to Railway,
  Render, Fly.io, or any container host. Point `DATABASE_URL` at a managed PostgreSQL
  instance (Railway/Render/Supabase/RDS all work).
- **Frontend**: `npm run build` outputs a static `dist/` folder — deploy to Vercel,
  Netlify, or serve it from the backend's container behind a reverse proxy. Set
  `VITE_API_URL` to the deployed backend's URL at build time.
- **CORS**: update `FRONTEND_ORIGIN` in `backend/.env` to your deployed frontend URL.

## Tech stack

Python · Pandas · NumPy · Matplotlib/Seaborn · FastAPI · SQLAlchemy · PostgreSQL/SQLite ·
React 18 · Vite · Recharts · Power BI (DAX) · Jupyter

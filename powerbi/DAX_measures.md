# Power BI Setup Guide

## 1. Generate the export files

```bash
cd powerbi
python export_powerbi.py
```

This writes six CSVs to `powerbi/exports/`:

| File | Grain | Purpose |
|---|---|---|
| `fact_orders.csv` | 1 row per order line | Core fact table (sales, profit, quantity, discount) |
| `dim_customer.csv` | 1 row per customer | Customer name, segment, state, region |
| `dim_product.csv` | 1 row per product | Product name, category, sub-category |
| `dim_geography.csv` | 1 row per state/city/region | Geographic hierarchy |
| `dim_date.csv` | 1 row per calendar day | Full date dimension for time intelligence |
| `customer_rfm.csv` | 1 row per customer | RFM scores + segment tier + recommended action |

## 2. Import into Power BI Desktop

1. **Get Data → Text/CSV** → import each of the 6 files above.
2. Open **Model view** and create these relationships:
   - `fact_orders[customer_id]` → `dim_customer[customer_id]` (many-to-one)
   - `fact_orders[product_id]` → `dim_product[product_id]` (many-to-one)
   - `fact_orders[order_date]` → `dim_date[Date]` (many-to-one)
   - `customer_rfm[customer_id]` → `dim_customer[customer_id]` (one-to-one)
3. Mark `dim_date` as a **Date Table** (Modeling → Mark as Date Table).

## 3. DAX Measures

```dax
Total Sales          = SUM(fact_orders[sales])
Total Profit         = SUM(fact_orders[profit])
Total Orders          = DISTINCTCOUNT(fact_orders[order_id])
Total Customers        = DISTINCTCOUNT(fact_orders[customer_id])

Profit Margin %       = DIVIDE([Total Profit], [Total Sales], 0)
Avg Order Value        = DIVIDE([Total Sales], [Total Orders], 0)
Avg Discount %          = AVERAGE(fact_orders[discount])

Sales YoY %            =
VAR CurrYear = [Total Sales]
VAR PrevYear = CALCULATE([Total Sales], SAMEPERIODLASTYEAR(dim_date[Date]))
RETURN DIVIDE(CurrYear - PrevYear, PrevYear, 0)

Sales MTD              = TOTALMTD([Total Sales], dim_date[Date])
Sales QTD              = TOTALQTD([Total Sales], dim_date[Date])
Sales YTD              = TOTALYTD([Total Sales], dim_date[Date])

Champions Revenue Share =
DIVIDE(
    CALCULATE([Total Sales], customer_rfm[Segment] = "Champions"),
    [Total Sales], 0
)

Loss-Making Line Items  = CALCULATE(COUNTROWS(fact_orders), fact_orders[profit] < 0)
```

## 4. Suggested pages

1. **Executive Overview** — KPI cards (Sales, Profit, Margin %, Orders) + monthly trend line + region map.
2. **Category / Product** — Sales & profit by category/sub-category, top 10 products table.
3. **Customer & RFM** — Segment donut chart (`customer_rfm[Segment]`), scatter of Recency vs Frequency sized by Monetary, top-customers table with `Recommended_Action`.
4. **Geography** — Filled map by state, top 10 states/cities bar chart.

## 5. Refreshing data

Re-run `python export_powerbi.py` any time the underlying data changes (or call
`POST /api/export/powerbi` on the running FastAPI backend), then click
**Refresh** in Power BI Desktop — the model and visuals rebuild automatically
since the relationships and measures are defined at the schema level.

import { fmtMoney, fmtNum, fmtPct } from "../format";

export default function KpiStrip({ data }) {
  if (!data) return null;

  const cells = [
    { label: "Total Sales", value: fmtMoney(data.total_sales) },
    {
      label: "Total Profit",
      value: fmtMoney(data.total_profit),
      cls: data.total_profit >= 0 ? "pos" : "neg",
    },
    { label: "Profit Margin", value: fmtPct(data.profit_margin_pct) },
    { label: "Orders", value: fmtNum(data.total_orders) },
    { label: "Customers", value: fmtNum(data.total_customers) },
    { label: "Avg Order Value", value: fmtMoney(data.avg_order_value) },
    { label: "Units Sold", value: fmtNum(data.total_quantity) },
    { label: "Avg Discount", value: fmtPct(data.avg_discount_pct) },
  ];

  return (
    <div className="kpi-strip">
      {cells.map((c) => (
        <div className="kpi-cell" key={c.label}>
          <div className="label">{c.label}</div>
          <div className={`value ${c.cls || ""}`}>{c.value}</div>
        </div>
      ))}
    </div>
  );
}

import { api } from "../api";
import { useFetch } from "../useFetch";
import Panel from "../components/Panel";
import BarChartPanel from "../components/BarChartPanel";
import { fmtMoney, fmtNum, fmtPct } from "../format";

export default function Sales() {
  const bySegment = useFetch(() => api.salesBySegment(), []);
  const byShip = useFetch(() => api.salesByShipMode(), []);
  const discount = useFetch(() => api.discountImpact(), []);
  const topProducts = useFetch(() => api.topProducts("sales", 10), []);

  return (
    <div className="grid" style={{ gap: 16 }}>
      <div className="grid cols-2">
        <Panel title="Sales by Customer Segment" loading={bySegment.loading} error={bySegment.error}>
          {bySegment.data && (
            <BarChartPanel
              data={bySegment.data}
              xKey="segment"
              bars={[
                { key: "sales", name: "Sales", color: "#7c9cff" },
                { key: "profit", name: "Profit", color: "#34d6a6" },
              ]}
            />
          )}
        </Panel>

        <Panel title="Sales by Ship Mode" loading={byShip.loading} error={byShip.error}>
          {byShip.data && (
            <BarChartPanel
              data={byShip.data}
              xKey="ship_mode"
              bars={[{ key: "sales", name: "Sales", color: "#7c9cff" }]}
            />
          )}
        </Panel>
      </div>

      <Panel
        title="Discount Impact on Profit"
        tag="avg & total profit by discount band"
        loading={discount.loading}
        error={discount.error}
      >
        {discount.data && (
          <>
            <BarChartPanel
              data={discount.data}
              xKey="discount_band"
              bars={[
                { key: "avg_profit", name: "Avg Profit / Order", color: "#34d6a6" },
              ]}
            />
            <p className="foot-note">
              Deep discounts (40%+) consistently erode or reverse profit — a strong signal to cap
              promotional discounting.
            </p>
          </>
        )}
      </Panel>

      <Panel title="Top 10 Products by Sales" loading={topProducts.loading} error={topProducts.error}>
        {topProducts.data && (
          <table className="ledger">
            <thead>
              <tr>
                <th>Product</th>
                <th>Category</th>
                <th className="num">Sales</th>
                <th className="num">Profit</th>
                <th className="num">Qty</th>
              </tr>
            </thead>
            <tbody>
              {topProducts.data.map((p) => (
                <tr key={p.product_id}>
                  <td>{p.product_name}</td>
                  <td>{p.category}</td>
                  <td className="num">{fmtMoney(p.sales)}</td>
                  <td className="num">{fmtMoney(p.profit)}</td>
                  <td className="num">{fmtNum(p.quantity)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Panel>
    </div>
  );
}

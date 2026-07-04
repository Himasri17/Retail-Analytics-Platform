import { useState } from "react";
import { api } from "../api";
import { useFetch } from "../useFetch";
import Panel from "../components/Panel";
import { fmtMoney, fmtNum, fmtPct } from "../format";

export default function Products() {
  const [sortBy, setSortBy] = useState("sales");
  const top = useFetch(() => api.topProducts(sortBy, 15), [sortBy]);

  return (
    <div className="grid" style={{ gap: 16 }}>
      <Panel
        title="Top Products"
        loading={top.loading}
        error={top.error}
      >
        <div className="filters" style={{ marginBottom: 12 }}>
          {[
            { id: "sales", label: "By Sales" },
            { id: "profit", label: "By Profit" },
            { id: "quantity", label: "By Quantity" },
          ].map((o) => (
            <button
              key={o.id}
              className="clear"
              style={{
                borderColor: sortBy === o.id ? "#7c9cff" : undefined,
                color: sortBy === o.id ? "#e9e7e1" : undefined,
              }}
              onClick={() => setSortBy(o.id)}
            >
              {o.label}
            </button>
          ))}
        </div>
        {top.data && (
          <table className="ledger">
            <thead>
              <tr>
                <th>Product</th>
                <th>Category</th>
                <th>Sub-Category</th>
                <th className="num">Sales</th>
                <th className="num">Profit</th>
                <th className="num">Qty</th>
              </tr>
            </thead>
            <tbody>
              {top.data.map((p) => (
                <tr key={p.product_id}>
                  <td>{p.product_name}</td>
                  <td>{p.category}</td>
                  <td>{p.sub_category}</td>
                  <td className="num">{fmtMoney(p.sales)}</td>
                  <td className="num" style={{ color: p.profit >= 0 ? "#34d6a6" : "#ff6b5b" }}>
                    {fmtMoney(p.profit)}
                  </td>
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

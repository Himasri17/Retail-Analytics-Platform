import { useState } from "react";
import { api } from "../api";
import { useFetch } from "../useFetch";
import Panel from "../components/Panel";
import { fmtMoney } from "../format";

export default function Orders() {
  const [page, setPage] = useState(1);
  const pageSize = 15;
  const orders = useFetch(() => api.orders(page, pageSize), [page]);

  const totalPages = orders.data ? Math.ceil(orders.data.total / pageSize) : 1;

  return (
    <Panel
      title="Recent Orders"
      tag={orders.data ? `${orders.data.total.toLocaleString()} total order lines` : undefined}
      loading={orders.loading}
      error={orders.error}
    >
      {orders.data && (
        <>
          <table className="ledger">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Date</th>
                <th>Customer</th>
                <th>Product</th>
                <th>Region</th>
                <th className="num">Sales</th>
                <th className="num">Profit</th>
              </tr>
            </thead>
            <tbody>
              {orders.data.items.map((o, i) => (
                <tr key={`${o.order_id}-${i}`}>
                  <td>{o.order_id}</td>
                  <td>{o.order_date}</td>
                  <td>{o.customer_name}</td>
                  <td>{o.product_name}</td>
                  <td>{o.region}</td>
                  <td className="num">{fmtMoney(o.sales)}</td>
                  <td className="num" style={{ color: o.profit >= 0 ? "#34d6a6" : "#ff6b5b" }}>
                    {fmtMoney(o.profit)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="filters" style={{ marginTop: 14, justifyContent: "space-between" }}>
            <button className="clear" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              ← Previous
            </button>
            <span className="foot-note">Page {page} of {totalPages}</span>
            <button className="clear" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
              Next →
            </button>
          </div>
        </>
      )}
    </Panel>
  );
}

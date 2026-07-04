import { useState } from "react";
import { api } from "../api";
import { useFetch } from "../useFetch";
import Panel from "../components/Panel";
import RfmDonut from "../components/RfmDonut";
import RfmScatter from "../components/RfmScatter";
import { SEGMENT_COLORS, fmtMoney, fmtNum } from "../format";

export default function Customers() {
  const [segmentFilter, setSegmentFilter] = useState("");
  const summary = useFetch(() => api.rfmSummary(), []);
  const table = useFetch(() => api.rfmTable(segmentFilter || undefined, 300), [segmentFilter]);
  const topCustomers = useFetch(() => api.topCustomers(8), []);

  return (
    <div className="grid" style={{ gap: 16 }}>
      <div className="grid cols-2">
        <Panel
          title="RFM Segments"
          tag="Recency · Frequency · Monetary"
          loading={summary.loading}
          error={summary.error}
        >
          {summary.data && <RfmDonut data={summary.data} />}
        </Panel>

        <Panel title="Segment Playbook" loading={summary.loading} error={summary.error}>
          {summary.data && (
            <div className="rfm-actions">
              {summary.data.map((s) => (
                <div className="rfm-action-row" key={s.Segment}>
                  <span className="swatch" style={{ background: SEGMENT_COLORS[s.Segment] }} />
                  <span>
                    <b>{s.Segment}</b> — {s.customers} customers ({s.pct_of_customers}%), avg spend{" "}
                    {fmtMoney(s.avg_monetary)}
                    <br />
                    <span className="txt">{s.action}</span>
                  </span>
                </div>
              ))}
            </div>
          )}
        </Panel>
      </div>

      <Panel
        title="Recency vs Frequency"
        tag="bubble size = lifetime spend"
        loading={table.loading}
        error={table.error}
      >
        {table.data && <RfmScatter rows={table.data} />}
      </Panel>

      <Panel
        title="Customer Segmentation Table"
        tag={`${table.data?.length ?? "…"} customers`}
        loading={table.loading}
        error={table.error}
      >
        <div className="filters" style={{ marginBottom: 12 }}>
          {["", "Champions", "Loyal", "At-Risk", "Lost", "New"].map((seg) => (
            <button
              key={seg || "all"}
              className="clear"
              style={{
                borderColor: segmentFilter === seg ? "#7c9cff" : undefined,
                color: segmentFilter === seg ? "#e9e7e1" : undefined,
              }}
              onClick={() => setSegmentFilter(seg)}
            >
              {seg || "All"}
            </button>
          ))}
        </div>
        {table.data && (
          <table className="ledger">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Segment</th>
                <th className="num">Recency (d)</th>
                <th className="num">Frequency</th>
                <th className="num">Monetary</th>
                <th className="num">RFM</th>
              </tr>
            </thead>
            <tbody>
              {table.data.slice(0, 40).map((r) => (
                <tr key={r.customer_id}>
                  <td>{r.customer_name}</td>
                  <td>
                    <span className="segment-pill">
                      <span className="dot" style={{ background: SEGMENT_COLORS[r.Segment] }} />
                      {r.Segment}
                    </span>
                  </td>
                  <td className="num">{fmtNum(r.recency)}</td>
                  <td className="num">{fmtNum(r.frequency)}</td>
                  <td className="num">{fmtMoney(r.monetary)}</td>
                  <td className="num">{r.RFM_Score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <p className="foot-note">Showing top 40 of {table.data?.length ?? 0} matching customers, sorted by lifetime spend.</p>
      </Panel>

      <Panel title="Top Customers by Lifetime Value" loading={topCustomers.loading} error={topCustomers.error}>
        {topCustomers.data && (
          <table className="ledger">
            <thead>
              <tr>
                <th>Customer</th>
                <th className="num">Orders</th>
                <th className="num">LTV</th>
                <th className="num">Avg Order</th>
              </tr>
            </thead>
            <tbody>
              {topCustomers.data.map((c) => (
                <tr key={c.customer_id}>
                  <td>{c.customer_name}</td>
                  <td className="num">{fmtNum(c.orders)}</td>
                  <td className="num">{fmtMoney(c.ltv)}</td>
                  <td className="num">{fmtMoney(c.avg_order)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Panel>
    </div>
  );
}

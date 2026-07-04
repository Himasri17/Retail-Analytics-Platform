import { api } from "../api";
import { useFetch } from "../useFetch";
import Panel from "../components/Panel";
import { fmtMoney, fmtPct } from "../format";

function heatColor(value, max) {
  if (value === null || value === undefined) return "transparent";
  const intensity = Math.min(Math.abs(value) / max, 1);
  return value >= 0
    ? `rgba(52, 214, 166, ${0.12 + intensity * 0.55})`
    : `rgba(255, 107, 91, ${0.12 + intensity * 0.55})`;
}

export default function Profit() {
  const byCategory = useFetch(() => api.profitByCategory(), []);
  const lossSubcats = useFetch(() => api.lossSubcats(), []);
  const heatmap = useFetch(() => api.profitHeatmap(), []);

  const categories = heatmap.data ? Object.keys(heatmap.data[0]).filter((k) => k !== "segment") : [];
  const maxAbs = heatmap.data
    ? Math.max(...heatmap.data.flatMap((row) => categories.map((c) => Math.abs(row[c] ?? 0))))
    : 1;

  return (
    <div className="grid" style={{ gap: 16 }}>
      <div className="grid cols-2">
        <Panel title="Profit Margin by Category" loading={byCategory.loading} error={byCategory.error}>
          {byCategory.data && (
            <table className="ledger">
              <thead>
                <tr>
                  <th>Category</th>
                  <th className="num">Sales</th>
                  <th className="num">Profit</th>
                  <th className="num">Margin</th>
                </tr>
              </thead>
              <tbody>
                {byCategory.data.map((c) => (
                  <tr key={c.category}>
                    <td>{c.category}</td>
                    <td className="num">{fmtMoney(c.sales)}</td>
                    <td className="num" style={{ color: c.profit >= 0 ? "#34d6a6" : "#ff6b5b" }}>
                      {fmtMoney(c.profit)}
                    </td>
                    <td className="num">{fmtPct(c.margin_pct)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Panel>

        <Panel
          title="Loss-Making Sub-Categories"
          tag="negative total profit"
          loading={lossSubcats.loading}
          error={lossSubcats.error}
        >
          {lossSubcats.data && (
            lossSubcats.data.length === 0 ? (
              <p className="foot-note">No sub-categories are currently loss-making. 🎉</p>
            ) : (
              <table className="ledger">
                <thead>
                  <tr>
                    <th>Sub-Category</th>
                    <th className="num">Total Profit</th>
                  </tr>
                </thead>
                <tbody>
                  {lossSubcats.data.map((s) => (
                    <tr key={s.sub_category}>
                      <td>{s.sub_category}</td>
                      <td className="num" style={{ color: "#ff6b5b" }}>{fmtMoney(s.total_profit)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          )}
        </Panel>
      </div>

      <Panel
        title="Profit Heatmap — Segment × Category"
        tag="darker = larger magnitude"
        loading={heatmap.loading}
        error={heatmap.error}
      >
        {heatmap.data && (
          <table className="ledger">
            <thead>
              <tr>
                <th>Segment</th>
                {categories.map((c) => (
                  <th className="num" key={c}>{c}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {heatmap.data.map((row) => (
                <tr key={row.segment}>
                  <td>{row.segment}</td>
                  {categories.map((c) => (
                    <td
                      className="num"
                      key={c}
                      style={{ background: heatColor(row[c], maxAbs), fontWeight: 500 }}
                    >
                      {fmtMoney(row[c])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Panel>
    </div>
  );
}

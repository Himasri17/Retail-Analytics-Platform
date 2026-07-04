import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import { SEGMENT_COLORS, fmtMoney } from "../format";

export default function RfmScatter({ rows }) {
  const bySegment = {};
  rows.forEach((r) => {
    bySegment[r.Segment] = bySegment[r.Segment] || [];
    bySegment[r.Segment].push(r);
  });

  return (
    <ResponsiveContainer width="100%" height={320}>
      <ScatterChart margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
        <CartesianGrid stroke="#2b2f3a" />
        <XAxis
          type="number"
          dataKey="recency"
          name="Recency (days)"
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 11 }}
          label={{ value: "Recency (days since last order) →", position: "insideBottom", offset: -6, fill: "#565b66", fontSize: 11 }}
        />
        <YAxis
          type="number"
          dataKey="frequency"
          name="Frequency (orders)"
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 11 }}
          label={{ value: "Frequency (orders) →", angle: -90, position: "insideLeft", fill: "#565b66", fontSize: 11 }}
        />
        <ZAxis type="number" dataKey="monetary" range={[30, 400]} name="Lifetime Spend" />
        <Tooltip
          cursor={{ strokeDasharray: "3 3" }}
          formatter={(v, n) => (n === "Lifetime Spend" ? fmtMoney(v) : v)}
          contentStyle={{
            background: "#21252e",
            border: "1px solid #2b2f3a",
            borderRadius: 6,
            fontFamily: "IBM Plex Mono, monospace",
            fontSize: 12,
          }}
        />
        {Object.entries(bySegment).map(([seg, pts]) => (
          <Scatter key={seg} name={seg} data={pts} fill={SEGMENT_COLORS[seg] || "#7c9cff"} fillOpacity={0.75} />
        ))}
      </ScatterChart>
    </ResponsiveContainer>
  );
}

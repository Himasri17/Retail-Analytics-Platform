import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fmtMoney } from "../format";

/**
 * Generic bar chart.
 * `bars`: [{ key: 'sales', name: 'Sales', color: '#7c9cff' }, ...]
 * `layout`: 'vertical' (bars go horizontal, category on Y) or 'horizontal' (default)
 */
export default function BarChartPanel({ data, xKey, bars, layout = "horizontal", height = 280, colorByIndex }) {
  const isVertical = layout === "vertical";
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={data}
        layout={isVertical ? "vertical" : "horizontal"}
        margin={{ top: 4, right: 16, left: isVertical ? 8 : 0, bottom: 0 }}
      >
        <CartesianGrid stroke="#2b2f3a" horizontal={!isVertical} vertical={isVertical} />
        {isVertical ? (
          <>
            <XAxis type="number" tickFormatter={fmtMoney} axisLine={false} tickLine={false} />
            <YAxis
              type="category"
              dataKey={xKey}
              width={110}
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 11 }}
            />
          </>
        ) : (
          <>
            <XAxis dataKey={xKey} axisLine={{ stroke: "#2b2f3a" }} tickLine={false} tick={{ fontSize: 11 }} />
            <YAxis tickFormatter={fmtMoney} axisLine={false} tickLine={false} width={54} />
          </>
        )}
        <Tooltip
          formatter={(v) => fmtMoney(v)}
          contentStyle={{
            background: "#21252e",
            border: "1px solid #2b2f3a",
            borderRadius: 6,
            fontFamily: "IBM Plex Mono, monospace",
            fontSize: 12,
          }}
        />
        {bars.length > 1 && <Legend wrapperStyle={{ fontSize: 12 }} />}
        {bars.map((b) => (
          <Bar key={b.key} dataKey={b.key} name={b.name} fill={b.color} radius={[3, 3, 3, 3]}>
            {colorByIndex &&
              data.map((entry, idx) => <Cell key={idx} fill={colorByIndex(entry, idx)} />)}
          </Bar>
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}

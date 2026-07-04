import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fmtMoney } from "../format";

export default function MonthlyTrendChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ top: 4, right: 12, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="#2b2f3a" vertical={false} />
        <XAxis dataKey="month" tickMargin={8} axisLine={{ stroke: "#2b2f3a" }} tickLine={false} />
        <YAxis
          tickFormatter={fmtMoney}
          axisLine={false}
          tickLine={false}
          width={56}
        />
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
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Line type="monotone" dataKey="sales" name="Sales" stroke="#7c9cff" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="profit" name="Profit" stroke="#34d6a6" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

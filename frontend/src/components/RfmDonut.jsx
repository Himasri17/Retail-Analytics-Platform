import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { SEGMENT_COLORS, fmtNum } from "../format";

export default function RfmDonut({ data }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie
          data={data}
          dataKey="customers"
          nameKey="Segment"
          innerRadius={62}
          outerRadius={92}
          paddingAngle={2}
        >
          {data.map((d) => (
            <Cell key={d.Segment} fill={SEGMENT_COLORS[d.Segment] || "#7c9cff"} stroke="#14161b" />
          ))}
        </Pie>
        <Tooltip
          formatter={(v, n, p) => [`${fmtNum(v)} customers (${p.payload.pct_of_customers}%)`, p.payload.Segment]}
          contentStyle={{
            background: "#21252e",
            border: "1px solid #2b2f3a",
            borderRadius: 6,
            fontFamily: "IBM Plex Mono, monospace",
            fontSize: 12,
          }}
        />
        <Legend
          layout="vertical"
          verticalAlign="middle"
          align="right"
          wrapperStyle={{ fontSize: 12, fontFamily: "IBM Plex Mono, monospace" }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}

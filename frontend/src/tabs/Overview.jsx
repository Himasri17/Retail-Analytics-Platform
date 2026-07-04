import { api } from "../api";
import { useFetch } from "../useFetch";
import Panel from "../components/Panel";
import MonthlyTrendChart from "../components/MonthlyTrendChart";
import BarChartPanel from "../components/BarChartPanel";
import { CATEGORY_COLORS } from "../format";

export default function Overview() {
  const trend = useFetch(() => api.monthlyTrend(), []);
  const byRegion = useFetch(() => api.salesByRegion(), []);
  const byCategory = useFetch(() => api.salesByCategory(), []);
  const topStates = useFetch(() => api.salesByState(8), []);

  return (
    <div className="grid" style={{ gap: 16 }}>
      <Panel title="Sales & Profit — Monthly Trend" tag="all years" loading={trend.loading} error={trend.error}>
        {trend.data && <MonthlyTrendChart data={trend.data} />}
      </Panel>

      <div className="grid cols-2">
        <Panel title="Sales & Profit by Region" loading={byRegion.loading} error={byRegion.error}>
          {byRegion.data && (
            <BarChartPanel
              data={byRegion.data}
              xKey="region"
              bars={[
                { key: "sales", name: "Sales", color: "#7c9cff" },
                { key: "profit", name: "Profit", color: "#34d6a6" },
              ]}
            />
          )}
        </Panel>

        <Panel title="Sales by Category" loading={byCategory.loading} error={byCategory.error}>
          {byCategory.data && (
            <BarChartPanel
              data={byCategory.data}
              xKey="category"
              bars={[{ key: "sales", name: "Sales", color: "#7c9cff" }]}
              colorByIndex={(_, i) => CATEGORY_COLORS[i % CATEGORY_COLORS.length]}
            />
          )}
        </Panel>
      </div>

      <Panel title="Top 8 States by Sales" loading={topStates.loading} error={topStates.error}>
        {topStates.data && (
          <BarChartPanel
            data={[...topStates.data].sort((a, b) => a.sales - b.sales)}
            xKey="state"
            layout="vertical"
            height={300}
            bars={[{ key: "sales", name: "Sales", color: "#7c9cff" }]}
          />
        )}
      </Panel>
    </div>
  );
}

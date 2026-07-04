import { useState } from "react";
import { api } from "./api";
import { useFetch } from "./useFetch";
import Sidebar from "./components/Sidebar";
import FilterBar from "./components/FilterBar";
import KpiStrip from "./components/KpiStrip";
import Overview from "./tabs/Overview";
import Sales from "./tabs/Sales";
import Profit from "./tabs/Profit";
import Customers from "./tabs/Customers";
import Products from "./tabs/Products";
import Orders from "./tabs/Orders";

const TAB_META = {
  overview: { title: "Overview", sub: "Sales & profit performance at a glance" },
  sales: { title: "Sales", sub: "Segment, ship-mode and discount analysis" },
  profit: { title: "Profit", sub: "Margins, losses and the segment × category heatmap" },
  customers: { title: "Customers · RFM", sub: "Recency-Frequency-Monetary segmentation & playbook" },
  products: { title: "Products", sub: "Best & worst performing SKUs" },
  orders: { title: "Orders", sub: "Order-line level detail" },
};

export default function App() {
  const [active, setActive] = useState("overview");
  const [filters, setFilters] = useState({});

  const meta = useFetch(() => api.metaFilters(), []);
  const kpis = useFetch(() => api.kpiSummary(filters), [filters.region, filters.category, filters.segment]);

  const tabProps = { filters };

  return (
    <div className="shell">
      <Sidebar active={active} setActive={setActive} />
      <main className="main">
        <div className="topbar">
          <div>
            <h1>{TAB_META[active].title}</h1>
            <div className="sub">{TAB_META[active].sub}</div>
          </div>
          <FilterBar meta={meta.data} filters={filters} setFilters={setFilters} />
        </div>

        <KpiStrip data={kpis.data} />

        {active === "overview" && <Overview {...tabProps} />}
        {active === "sales" && <Sales {...tabProps} />}
        {active === "profit" && <Profit {...tabProps} />}
        {active === "customers" && <Customers {...tabProps} />}
        {active === "products" && <Products {...tabProps} />}
        {active === "orders" && <Orders {...tabProps} />}
      </main>
    </div>
  );
}

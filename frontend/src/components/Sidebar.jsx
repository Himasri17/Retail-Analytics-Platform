const TABS = [
  { id: "overview", label: "Overview" },
  { id: "sales", label: "Sales" },
  { id: "profit", label: "Profit" },
  { id: "customers", label: "Customers · RFM" },
  { id: "products", label: "Products" },
  { id: "orders", label: "Orders" },
];

export default function Sidebar({ active, setActive }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">retail / analytics</div>
        <div className="brand-name">Ledger</div>
      </div>
      <nav className="nav">
        {TABS.map((t, i) => (
          <button
            key={t.id}
            className={`nav-item ${active === t.id ? "active" : ""}`}
            onClick={() => setActive(t.id)}
          >
            <span className="idx">{String(i + 1).padStart(2, "0")}</span>
            {t.label}
          </button>
        ))}
      </nav>
      <div className="sidebar-foot">
        Superstore dataset<br />
        FastAPI · PostgreSQL · React
      </div>
    </aside>
  );
}

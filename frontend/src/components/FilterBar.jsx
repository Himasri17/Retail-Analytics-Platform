export default function FilterBar({ meta, filters, setFilters }) {
  if (!meta) return null;

  const update = (key) => (e) => setFilters((f) => ({ ...f, [key]: e.target.value }));
  const hasFilters = filters.region || filters.category || filters.segment;

  return (
    <div className="filters">
      <select value={filters.region || ""} onChange={update("region")}>
        <option value="">All Regions</option>
        {meta.regions.map((r) => (
          <option key={r} value={r}>{r}</option>
        ))}
      </select>
      <select value={filters.category || ""} onChange={update("category")}>
        <option value="">All Categories</option>
        {meta.categories.map((c) => (
          <option key={c} value={c}>{c}</option>
        ))}
      </select>
      <select value={filters.segment || ""} onChange={update("segment")}>
        <option value="">All Segments</option>
        {meta.segments.map((s) => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>
      {hasFilters && (
        <button className="clear" onClick={() => setFilters({})}>
          Clear
        </button>
      )}
    </div>
  );
}

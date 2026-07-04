export default function Panel({ title, tag, loading, error, children, className = "" }) {
  const stateClass = loading ? "loading" : error ? "error" : "";
  return (
    <div className={`panel ${stateClass} ${className}`}>
      {title && !loading && !error && (
        <div className="panel-head">
          <h3>{title}</h3>
          {tag && <span className="tag">{tag}</span>}
        </div>
      )}
      {loading ? "fetching…" : error ? `⚠ ${String(error.message || error)}` : children}
    </div>
  );
}

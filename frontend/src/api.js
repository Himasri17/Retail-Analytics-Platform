const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Thin fetch wrapper. `params` is a plain object of query params;
 * empty/undefined values are dropped automatically so filter state
 * can be passed straight through.
 */
export async function apiGet(path, params = {}) {
  const query = Object.entries(params)
    .filter(([, v]) => v !== undefined && v !== null && v !== "")
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join("&");

  const url = `${BASE}${path}${query ? `?${query}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} — ${body}`);
  }
  return res.json();
}

export const api = {
  health: () => apiGet("/api/health"),
  metaFilters: () => apiGet("/api/meta/filters"),

  kpiSummary: (filters) => apiGet("/api/kpis/summary", filters),
  monthlyTrend: () => apiGet("/api/kpis/monthly-trend"),
  yearlyTrend: () => apiGet("/api/kpis/yearly-trend"),

  salesByCategory: () => apiGet("/api/sales/by-category"),
  salesByRegion: () => apiGet("/api/sales/by-region"),
  salesByState: (limit = 10) => apiGet("/api/sales/by-state", { limit }),
  salesBySegment: () => apiGet("/api/sales/by-segment"),
  salesByShipMode: () => apiGet("/api/sales/by-ship-mode"),
  topProducts: (by = "sales", limit = 8) => apiGet("/api/products/top", { by, limit }),
  discountImpact: () => apiGet("/api/sales/discount-impact"),

  profitByCategory: () => apiGet("/api/profit/by-category"),
  lossSubcats: () => apiGet("/api/profit/loss-making-subcategories"),
  profitHeatmap: () => apiGet("/api/profit/heatmap"),

  customersSummary: () => apiGet("/api/customers/summary"),
  topCustomers: (limit = 8) => apiGet("/api/customers/top", { limit }),
  rfmTable: (segment, limit = 500) => apiGet("/api/customers/rfm/table", { segment, limit }),
  rfmSummary: () => apiGet("/api/customers/rfm/summary"),

  orders: (page = 1, page_size = 10, filters = {}) =>
    apiGet("/api/orders", { page, page_size, ...filters }),
};

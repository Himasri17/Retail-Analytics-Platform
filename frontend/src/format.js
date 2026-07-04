export const fmtMoney = (n) => {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  const abs = Math.abs(n);
  const sign = n < 0 ? "-" : "";
  if (abs >= 1_000_000) return `${sign}$${(abs / 1_000_000).toFixed(2)}M`;
  if (abs >= 1_000) return `${sign}$${(abs / 1_000).toFixed(1)}K`;
  return `${sign}$${abs.toFixed(0)}`;
};

export const fmtNum = (n) => {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return new Intl.NumberFormat("en-US").format(n);
};

export const fmtPct = (n) => (n === null || n === undefined ? "—" : `${n.toFixed(1)}%`);

export const SEGMENT_COLORS = {
  Champions: "#34d6a6",
  Loyal: "#7c9cff",
  "At-Risk": "#f0b429",
  Lost: "#ff6b5b",
  New: "#b39bff",
};

export const CATEGORY_COLORS = ["#7c9cff", "#34d6a6", "#f0b429", "#ff6b5b", "#b39bff"];

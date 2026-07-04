"""
rfm.py
------
RFM (Recency, Frequency, Monetary) customer segmentation.

Classifies every customer into one of 5 tiers used across the dashboard and
Power BI export: Champions, Loyal, At-Risk, Lost, New.

Scoring method
--------------
1. Recency  = days since the customer's most recent order (relative to the
   day after the last order date in the whole dataset — so the most recent
   shopper scores best).
2. Frequency = number of distinct orders placed.
3. Monetary  = total sales (lifetime spend).

Each metric is bucketed into quintiles (1-5) with pandas.qcut. Recency is
scored in reverse (lower days-since = higher score). The three scores are
then combined with a rule-based classifier (rather than a fixed cutoff sum)
so that customers who are simultaneously frequent AND high-spend AND recent
are the only ones who land in "Champions", low-recency/low-frequency
customers are clearly "Lost", etc.
"""

from __future__ import annotations

import pandas as pd


def _safe_qcut_score(series: pd.Series, ascending: bool, labels_desc=(1, 2, 3, 4, 5)) -> pd.Series:
    """
    Quintile-score a series 1-5. Falls back to rank-based binning when there
    aren't enough distinct values for qcut (common with small/sparse data).
    """
    try:
        bins = pd.qcut(series.rank(method="first"), q=5, labels=labels_desc if ascending else labels_desc[::-1])
        return bins.astype(int)
    except ValueError:
        # Not enough unique values — degrade gracefully to a simple rank split
        ranked = series.rank(pct=True)
        edges = [0, 0.2, 0.4, 0.6, 0.8, 1.0001]
        score_labels = labels_desc if ascending else labels_desc[::-1]
        return pd.cut(ranked, bins=edges, labels=score_labels, include_lowest=True).astype(int)


def classify_segment(r: int, f: int, m: int) -> str:
    """Rule-based mapping of (R, F, M) scores -> one of 5 business-friendly tiers."""
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    if r <= 2 and f <= 2:
        return "Lost"
    if r <= 2 and f >= 3:
        return "At-Risk"
    if r >= 4 and f <= 2:
        return "New"
    return "Loyal"


SEGMENT_ACTIONS = {
    "Champions": "Reward with early access & loyalty perks; ask for referrals.",
    "Loyal": "Upsell higher-value products; keep engagement steady with regular offers.",
    "At-Risk": "Send win-back campaigns with personalized discounts before they churn.",
    "Lost": "Low-cost re-engagement (email blast); deprioritize for premium spend.",
    "New": "Nurture with onboarding offers to build purchase frequency.",
}


def compute_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    df must contain: customer_id, customer_name, order_id, order_date, sales

    Returns one row per customer with recency/frequency/monetary raw values,
    1-5 scores, combined RFM score string, and the assigned segment tier.
    """
    snapshot_date = df["order_date"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("customer_id").agg(
        customer_name=("customer_name", "first"),
        last_order_date=("order_date", "max"),
        frequency=("order_id", "nunique"),
        monetary=("sales", "sum"),
    ).reset_index()

    rfm["recency"] = (snapshot_date - rfm["last_order_date"]).dt.days

    rfm["R"] = _safe_qcut_score(rfm["recency"], ascending=False)   # fewer days = higher score
    rfm["F"] = _safe_qcut_score(rfm["frequency"], ascending=True)
    rfm["M"] = _safe_qcut_score(rfm["monetary"], ascending=True)

    rfm["RFM_Score"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)
    rfm["Segment"] = rfm.apply(lambda row: classify_segment(row["R"], row["F"], row["M"]), axis=1)
    rfm["Recommended_Action"] = rfm["Segment"].map(SEGMENT_ACTIONS)

    rfm["monetary"] = rfm["monetary"].round(2)
    rfm["last_order_date"] = rfm["last_order_date"].dt.strftime("%Y-%m-%d")

    return rfm.sort_values("monetary", ascending=False).reset_index(drop=True)


def rfm_summary(rfm_df: pd.DataFrame) -> list[dict]:
    """Aggregate tier-level stats used for the dashboard's segment donut / bar chart."""
    summary = rfm_df.groupby("Segment").agg(
        customers=("customer_id", "count"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        total_monetary=("monetary", "sum"),
    ).round(2).reset_index()
    summary["pct_of_customers"] = (summary["customers"] / summary["customers"].sum() * 100).round(1)
    summary["action"] = summary["Segment"].map(SEGMENT_ACTIONS)
    return summary.sort_values("total_monetary", ascending=False).to_dict(orient="records")

import pandas as pd
import numpy as np


# ── Overview ──────────────────────────────────────────────────────────────────

def overview_kpis(df):
    return {
        "total_revenue": df["order_total"].sum(),
        "total_orders": len(df),
        "aov": df["order_total"].mean(),
        "avg_delivery_minutes": df["delivery_time_minutes"].mean(),
        "delayed_pct": df["delivery_delay_flag"].mean() * 100,
        "avg_rating": df["rating"].mean(),
        "unique_customers": df["customer_id"].nunique(),
    }


def revenue_over_time(df, freq="M"):
    col = "order_month" if freq == "M" else "order_week"
    return (
        df.groupby(col)
        .agg(revenue=("order_total", "sum"), orders=("order_id", "count"))
        .reset_index()
        .rename(columns={col: "period"})
        .sort_values("period")
    )


def peak_hours(df):
    return (
        df.groupby("order_hour")
        .agg(orders=("order_id", "count"), revenue=("order_total", "sum"))
        .reset_index()
    )


# ── Products ──────────────────────────────────────────────────────────────────

def top_categories(df, n=10):
    return (
        df.groupby("category")
        .agg(revenue=("order_total", "sum"), orders=("order_id", "count"))
        .reset_index()
        .sort_values("revenue", ascending=False)
        .head(n)
    )


def top_products(df, n=20):
    return (
        df.groupby(["product_id", "product_name", "category"])
        .agg(revenue=("order_total", "sum"), orders=("order_id", "count"))
        .reset_index()
        .sort_values("revenue", ascending=False)
        .head(n)
    )


def inventory_vs_demand(master_df, inv_df):
    demand = (
        master_df.groupby("product_id")
        .agg(demand_orders=("order_id", "count"))
        .reset_index()
    )
    combined = inv_df.merge(demand, on="product_id", how="left").fillna({"demand_orders": 0})
    combined["demand_orders"] = combined["demand_orders"].astype(int)
    return combined.sort_values("low_stock_flag", ascending=False)


# ── Customers ─────────────────────────────────────────────────────────────────

def new_vs_repeat(df):
    counts = df.drop_duplicates("customer_id")["is_new_customer"].value_counts()
    return pd.DataFrame({
        "type": ["New", "Repeat"],
        "count": [counts.get(1, 0), counts.get(0, 0)],
    })


def clv_distribution(df):
    return df.drop_duplicates("customer_id")[["customer_id", "customer_segment", "customer_lifetime_value"]].dropna()


def purchase_frequency_dist(df):
    return df.drop_duplicates("customer_id")[["customer_id", "purchase_frequency"]].dropna()


def customer_segment_revenue(df):
    return (
        df.groupby("customer_segment")
        .agg(revenue=("order_total", "sum"), orders=("order_id", "count"), customers=("customer_id", "nunique"))
        .reset_index()
        .sort_values("revenue", ascending=False)
    )


def area_revenue(df):
    return (
        df.groupby("area")
        .agg(revenue=("order_total", "sum"), orders=("order_id", "count"))
        .reset_index()
        .sort_values("revenue", ascending=False)
    )


# ── Delivery ──────────────────────────────────────────────────────────────────

def delivery_status_split(df):
    return df["delivery_status"].value_counts().reset_index()


def delay_vs_rating(df):
    return (
        df.groupby("delivery_delay_flag")
        .agg(avg_rating=("rating", "mean"), orders=("order_id", "count"))
        .reset_index()
    )


def delay_reasons(df):
    delayed = df[df["delivery_delay_flag"] == 1]["reasons_if_delayed"].dropna()
    return delayed.value_counts().reset_index()


def delivery_time_by_area(df):
    return (
        df.groupby("area")
        .agg(avg_delivery_min=("delivery_time_minutes", "mean"), orders=("order_id", "count"))
        .reset_index()
        .sort_values("avg_delivery_min", ascending=False)
    )


# ── Marketing ─────────────────────────────────────────────────────────────────

def campaign_performance(mkt_df):
    return (
        mkt_df.groupby("campaign_name")
        .agg(
            spend=("spend", "sum"),
            revenue=("revenue_generated", "sum"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
            avg_roas=("roas", "mean"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )


def channel_performance(mkt_df):
    return (
        mkt_df.groupby("channel")
        .agg(spend=("spend", "sum"), revenue=("revenue_generated", "sum"), conversions=("conversions", "sum"))
        .reset_index()
        .assign(roi=lambda x: (x["revenue"] - x["spend"]) / x["spend"].replace(0, np.nan) * 100)
        .sort_values("roi", ascending=False)
    )


def marketing_over_time(mkt_df):
    mkt_df = mkt_df.copy()
    mkt_df["month"] = mkt_df["date"].dt.to_period("M").astype(str)
    return (
        mkt_df.groupby("month")
        .agg(spend=("spend", "sum"), revenue=("revenue_generated", "sum"), conversions=("conversions", "sum"))
        .reset_index()
        .sort_values("month")
    )


def conversion_funnel(mkt_df):
    return {
        "impressions": int(mkt_df["impressions"].sum()),
        "clicks": int(mkt_df["clicks"].sum()),
        "conversions": int(mkt_df["conversions"].sum()),
    }


# ── Feedback ──────────────────────────────────────────────────────────────────

def rating_distribution(df):
    return df["rating"].value_counts().sort_index().reset_index()


def sentiment_split(df):
    return df["sentiment"].value_counts().reset_index()


def feedback_category_counts(df):
    return df["feedback_category"].value_counts().reset_index()


def rating_over_time(df):
    return (
        df.groupby("order_month")
        .agg(avg_rating=("rating", "mean"), feedback_count=("rating", "count"))
        .reset_index()
        .rename(columns={"order_month": "period"})
        .sort_values("period")
    )

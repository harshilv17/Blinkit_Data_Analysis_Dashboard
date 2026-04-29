import pandas as pd
import numpy as np

EXCEL_PATH = "blinkit_dataset_raw_combined.xlsx"


def load_all_sheets():
    xl = pd.ExcelFile(EXCEL_PATH)
    return {sheet: pd.read_excel(xl, sheet_name=sheet) for sheet in xl.sheet_names}


def clean_orders(df):
    df = df.drop_duplicates(subset="order_id")
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["promised_delivery_time"] = pd.to_datetime(df["promised_delivery_time"])
    df["actual_delivery_time"] = pd.to_datetime(df["actual_delivery_time"])
    df["order_total"] = pd.to_numeric(df["order_total"], errors="coerce").fillna(0)
    df["delivery_status"] = df["delivery_status"].str.strip().str.lower()
    return df


def clean_order_items(df):
    df = df.dropna(subset=["order_id", "product_id"])
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1).astype(int)
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0)
    df["line_total"] = df["quantity"] * df["unit_price"]
    return df


def clean_products(df):
    df = df.drop_duplicates(subset="product_id")
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
    df["mrp"] = pd.to_numeric(df["mrp"], errors="coerce").fillna(0)
    df["margin_percentage"] = pd.to_numeric(df["margin_percentage"], errors="coerce").fillna(0)
    df["category"] = df["category"].str.strip()
    return df


def clean_customers(df):
    df = df.drop_duplicates(subset="customer_id")
    df["registration_date"] = pd.to_datetime(df["registration_date"])
    df["avg_order_value"] = pd.to_numeric(df["avg_order_value"], errors="coerce").fillna(0)
    df["total_orders"] = pd.to_numeric(df["total_orders"], errors="coerce").fillna(0).astype(int)
    df["customer_segment"] = df["customer_segment"].str.strip()
    df["area"] = df["area"].str.strip()
    return df


def clean_delivery(df):
    df = df.drop_duplicates(subset="order_id")
    df["delivery_time_minutes"] = pd.to_numeric(df["delivery_time_minutes"], errors="coerce").fillna(0)
    df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce").fillna(0)
    df["delivery_status"] = df["delivery_status"].str.strip().str.lower()
    return df


def clean_feedback(df):
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["feedback_date"] = pd.to_datetime(df["feedback_date"])
    df["sentiment"] = df["sentiment"].str.strip().str.lower()
    df["feedback_category"] = df["feedback_category"].str.strip()
    return df


def clean_marketing(df):
    df["date"] = pd.to_datetime(df["date"])
    df["spend"] = pd.to_numeric(df["spend"], errors="coerce").fillna(0)
    df["revenue_generated"] = pd.to_numeric(df["revenue_generated"], errors="coerce").fillna(0)
    df["roas"] = pd.to_numeric(df["roas"], errors="coerce").fillna(0)
    df["impressions"] = pd.to_numeric(df["impressions"], errors="coerce").fillna(0).astype(int)
    df["clicks"] = pd.to_numeric(df["clicks"], errors="coerce").fillna(0).astype(int)
    df["conversions"] = pd.to_numeric(df["conversions"], errors="coerce").fillna(0).astype(int)
    df["ctr"] = (df["clicks"] / df["impressions"].replace(0, np.nan)).fillna(0)
    df["conversion_rate"] = (df["conversions"] / df["clicks"].replace(0, np.nan)).fillna(0)
    return df


def clean_inventory(df_old, df_new):
    df = pd.concat([df_old, df_new], ignore_index=True)
    df["date"] = pd.to_datetime(df["date"])
    df["stock_received"] = pd.to_numeric(df["stock_received"], errors="coerce").fillna(0).astype(int)
    df["damaged_stock"] = pd.to_numeric(df["damaged_stock"], errors="coerce").fillna(0).astype(int)
    df["net_stock"] = df["stock_received"] - df["damaged_stock"]
    return df


def build_master(sheets):
    orders = clean_orders(sheets["blinkit_orders"])
    order_items = clean_order_items(sheets["blinkit_order_items"])
    products = clean_products(sheets["blinkit_products"])
    customers = clean_customers(sheets["blinkit_customers"])
    delivery = clean_delivery(sheets["blinkit_delivery_performance"])
    feedback = clean_feedback(sheets["blinkit_customer_feedback"])

    # Aggregate order_items to order level
    items_agg = (
        order_items.groupby("order_id")
        .agg(total_items=("quantity", "sum"), order_value=("line_total", "sum"))
        .reset_index()
    )

    # First product per order for category-level analysis
    first_item = (
        order_items.merge(products[["product_id", "category", "product_name", "brand", "margin_percentage"]], on="product_id", how="left")
        .drop_duplicates(subset="order_id")
        [["order_id", "product_id", "category", "product_name", "brand", "margin_percentage"]]
    )

    master = (
        orders
        .merge(items_agg, on="order_id", how="left")
        .merge(first_item, on="order_id", how="left")
        .merge(customers[["customer_id", "customer_name", "area", "customer_segment", "total_orders", "avg_order_value", "registration_date"]], on="customer_id", how="left")
        .merge(delivery[["order_id", "delivery_time_minutes", "distance_km", "reasons_if_delayed"]], on="order_id", how="left")
        .merge(feedback[["order_id", "rating", "sentiment", "feedback_category"]].drop_duplicates("order_id"), on="order_id", how="left")
    )

    # Feature engineering
    master["delivery_delay_flag"] = (master["delivery_status"] == "delayed").astype(int)
    master["customer_lifetime_value"] = master["total_orders"] * master["avg_order_value"]
    master["purchase_frequency"] = master["total_orders"]
    master["rating_category"] = pd.cut(
        master["rating"],
        bins=[0, 2, 3, 5],
        labels=["Low", "Medium", "High"],
        right=True,
    )
    master["order_month"] = master["order_date"].dt.to_period("M").astype(str)
    master["order_week"] = master["order_date"].dt.to_period("W").astype(str)
    master["order_hour"] = master["order_date"].dt.hour
    master["is_new_customer"] = (master["total_orders"] == 1).astype(int)

    return master


def build_inventory_summary(sheets):
    inv = clean_inventory(sheets["blinkit_inventory"], sheets["blinkit_inventoryNew"])
    products = clean_products(sheets["blinkit_products"])
    inv_summary = (
        inv.groupby("product_id")
        .agg(total_stock=("net_stock", "sum"), total_damaged=("damaged_stock", "sum"))
        .reset_index()
        .merge(products[["product_id", "product_name", "category", "min_stock_level", "max_stock_level"]], on="product_id", how="left")
    )
    inv_summary["stock_vs_min"] = inv_summary["total_stock"] - inv_summary["min_stock_level"]
    inv_summary["low_stock_flag"] = (inv_summary["stock_vs_min"] < 0).astype(int)
    return inv_summary


def build_marketing(sheets):
    return clean_marketing(sheets["blinkit_marketing_performance"])


def run_pipeline():
    print("Loading sheets...")
    sheets = load_all_sheets()

    print("Building master dataset...")
    master = build_master(sheets)
    master.to_csv("master_dataset.csv", index=False)
    print(f"master_dataset.csv saved — {master.shape[0]} rows x {master.shape[1]} cols")

    print("Building inventory summary...")
    inv = build_inventory_summary(sheets)
    inv.to_csv("inventory_summary.csv", index=False)
    print(f"inventory_summary.csv saved — {inv.shape[0]} rows")

    print("Building marketing dataset...")
    mkt = build_marketing(sheets)
    mkt.to_csv("marketing_data.csv", index=False)
    print(f"marketing_data.csv saved — {mkt.shape[0]} rows")

    return master, inv, mkt


if __name__ == "__main__":
    run_pipeline()

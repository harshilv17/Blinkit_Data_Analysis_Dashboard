import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_processing import load_all_sheets, build_master, build_inventory_summary, build_marketing
import eda

st.set_page_config(
    page_title="Blinkit Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand tokens ──────────────────────────────────────────────────────────────
Y1 = "#f7c325"   # Blinkit yellow
Y2 = "#ffe580"   # yellow light
Y3 = "#3d3200"   # yellow dark wash (dark-mode fill)
G1 = "#2d8a4e"   # Blinkit green
G2 = "#4caf50"   # green light
BK = "#f0f0f0"   # near-white text on dark bg
WH = "#1a1a2e"   # "white" = dark card bg
DARK_BG = "#0f0f1a"
CARD_BG = "#1e1e30"
RED = "#e74c3c"
SIDEBAR_BG = "#12121f"

PLOTLY_TEMPLATE = "plotly_dark"

CHART_SEQ = [Y1, G1, Y2, G2, "#FF9800", "#8BC34A", "#FFC107", "#66BB6A"]
RAMP_YG = ["#3d3200", Y1, G1]
RAMP_RYG = [RED, Y1, G1]

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* ── Main bg ── */
  .stApp {{
      background-color: {DARK_BG} !important;
  }}
  .block-container {{
      padding-top: 1.5rem !important;
  }}

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {{
      background-color: {SIDEBAR_BG} !important;
  }}
  [data-testid="stSidebar"] * {{
      color: #f0f0f0 !important;
  }}
  [data-testid="stSidebar"] .stSelectbox > div > div,
  [data-testid="stSidebar"] .stDateInput > div > div input {{
      background-color: #1e1e30 !important;
      color: #f0f0f0 !important;
      border-color: {Y1} !important;
  }}
  [data-testid="stSidebar"] .stSelectbox svg,
  [data-testid="stSidebar"] .stDateInput svg {{
      fill: {Y1} !important;
  }}

  /* ── Top header bar ── */
  .blinkit-header {{
      background: linear-gradient(135deg, {Y1} 0%, #c89a00 100%);
      padding: 18px 28px;
      border-radius: 14px;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 14px;
  }}
  .blinkit-header h1 {{
      color: #1a1a1a;
      margin: 0;
      font-size: 26px;
      font-weight: 800;
      letter-spacing: -0.5px;
  }}
  .blinkit-header p {{
      color: #1a1a1a;
      margin: 0;
      font-size: 13px;
      opacity: 0.7;
  }}

  /* ── KPI cards ── */
  .kpi-card {{
      background: #ffffff;
      border-radius: 14px;
      padding: 18px 20px;
      border-top: 4px solid {Y1};
      box-shadow: 0 4px 20px rgba(0,0,0,0.4);
      height: 100px;
      display: flex;
      flex-direction: column;
      justify-content: center;
  }}
  .kpi-val {{
      font-size: 26px;
      font-weight: 800;
      color: #1a1a1a;
      line-height: 1.1;
  }}
  .kpi-label {{
      font-size: 12px;
      color: #666;
      margin-top: 4px;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.4px;
  }}

  /* ── Section headers ── */
  .section-title {{
      font-size: 18px;
      font-weight: 700;
      color: #f0f0f0;
      border-left: 4px solid {Y1};
      padding-left: 10px;
      margin: 18px 0 12px 0;
  }}

  /* ── Tab styling ── */
  button[data-baseweb="tab"] {{
      font-weight: 600 !important;
      color: #aaa !important;
  }}
  button[data-baseweb="tab"][aria-selected="true"] {{
      color: {Y1} !important;
      border-bottom-color: {Y1} !important;
  }}

  /* ── Plotly chart cards ── */
  .stPlotlyChart {{
      background: {CARD_BG};
      border-radius: 14px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      padding: 4px;
  }}

  /* ── Dataframe ── */
  .stDataFrame {{
      border-radius: 10px;
      overflow: hidden;
  }}

  /* ── Divider ── */
  hr {{
      border-color: #2a2a40 !important;
      margin: 20px 0 !important;
  }}
</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading Blinkit data…")
def load_data():
    sheets = load_all_sheets()
    master = build_master(sheets)
    inv = build_inventory_summary(sheets)
    mkt = build_marketing(sheets)
    return master, inv, mkt


master_raw, inv_df, mkt_df = load_data()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding: 16px 0 8px 0;">
        <span style="font-size:48px;">🛒</span>
        <div style="font-size:20px; font-weight:800; color:{Y1}; margin-top:6px;">blinkit</div>
        <div style="font-size:11px; color:#aaa; margin-top:2px;">Analytics Dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"<hr style='border-color:{Y1}; opacity:0.3;'>", unsafe_allow_html=True)

    min_date = master_raw["order_date"].min().date()
    max_date = master_raw["order_date"].max().date()
    date_range = st.date_input("📅 Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    categories = ["All"] + sorted(master_raw["category"].dropna().unique().tolist())
    sel_category = st.selectbox("🏷 Product Category", categories)

    areas = ["All"] + sorted(master_raw["area"].dropna().unique().tolist())
    sel_area = st.selectbox("📍 Area / Region", areas)

    segments = ["All"] + sorted(master_raw["customer_segment"].dropna().unique().tolist())
    sel_segment = st.selectbox("👤 Customer Segment", segments)

    st.markdown(f"<hr style='border-color:{Y1}; opacity:0.3;'>", unsafe_allow_html=True)
    st.caption("Blinkit Ops Data · 2024–25")


# ── Filters ───────────────────────────────────────────────────────────────────
df = master_raw.copy()
if len(date_range) == 2:
    df = df[(df["order_date"].dt.date >= date_range[0]) & (df["order_date"].dt.date <= date_range[1])]
if sel_category != "All":
    df = df[df["category"] == sel_category]
if sel_area != "All":
    df = df[df["area"] == sel_area]
if sel_segment != "All":
    df = df[df["customer_segment"] == sel_segment]

mkt_filtered = mkt_df.copy()
if len(date_range) == 2:
    mkt_filtered = mkt_filtered[
        (mkt_filtered["date"].dt.date >= date_range[0]) &
        (mkt_filtered["date"].dt.date <= date_range[1])
    ]


# ── Helpers ───────────────────────────────────────────────────────────────────
def kpi(label, value, suffix=""):
    return f"""<div class="kpi-card">
        <div class="kpi-val">{value}{suffix}</div>
        <div class="kpi-label">{label}</div>
    </div>"""


def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def fmt_inr(val):
    if val >= 1e7:
        return f"₹{val/1e7:.1f}Cr"
    if val >= 1e5:
        return f"₹{val/1e5:.1f}L"
    return f"₹{val:,.0f}"


def chart_layout(fig, height=None):
    updates = dict(
        plot_bgcolor=CARD_BG,
        paper_bgcolor=CARD_BG,
        font_family="sans-serif",
        font_color="#d0d0d0",
        title_font_size=15,
        title_font_color="#f0f0f0",
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(bgcolor=CARD_BG, bordercolor="#333350"),
    )
    if height:
        updates["height"] = height
    fig.update_layout(**updates)
    fig.update_xaxes(showgrid=True, gridcolor="#252540", zeroline=False, color="#888")
    fig.update_yaxes(showgrid=True, gridcolor="#252540", zeroline=False, color="#888")
    return fig


# ── Page header ───────────────────────────────────────────────────────────────
kpis_global = eda.overview_kpis(df)
st.markdown(f"""
<div class="blinkit-header">
  <span style="font-size:40px;">🛒</span>
  <div>
    <h1>Blinkit Analytics Dashboard</h1>
    <p>{kpis_global['total_orders']:,} orders · {fmt_inr(kpis_global['total_revenue'])} revenue · {kpis_global['unique_customers']:,} customers</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview", "🛍 Products", "👤 Customers",
    "🚚 Delivery", "📢 Marketing", "⭐ Feedback"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    section("Key Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Total Revenue", fmt_inr(kpis_global["total_revenue"])), unsafe_allow_html=True)
    c2.markdown(kpi("Total Orders", f"{kpis_global['total_orders']:,}"), unsafe_allow_html=True)
    c3.markdown(kpi("Avg Order Value", fmt_inr(kpis_global["aov"])), unsafe_allow_html=True)
    c4.markdown(kpi("Unique Customers", f"{kpis_global['unique_customers']:,}"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    c5.markdown(kpi("Avg Delivery Time", f"{kpis_global['avg_delivery_minutes']:.0f}", " min"), unsafe_allow_html=True)
    c6.markdown(kpi("Delayed Orders", f"{kpis_global['delayed_pct']:.1f}", "%"), unsafe_allow_html=True)
    c7.markdown(kpi("Avg Rating", f"{kpis_global['avg_rating']:.2f}", " ★"), unsafe_allow_html=True)
    c8.markdown(kpi("On-Time Rate", f"{100 - kpis_global['delayed_pct']:.1f}", "%"), unsafe_allow_html=True)

    st.markdown("---")
    section("Revenue & Order Trends")

    col_left, col_right = st.columns([2, 1])
    with col_left:
        rev_time = eda.revenue_over_time(df, freq="M")
        fig = px.area(
            rev_time, x="period", y="revenue",
            title="Monthly Revenue",
            labels={"period": "Month", "revenue": "Revenue (₹)"},
            template=PLOTLY_TEMPLATE,
        )
        fig.update_traces(
            line_color=G1, fillcolor=Y3,
            line_width=2.5,
        )
        st.plotly_chart(chart_layout(fig), width="stretch")

    with col_right:
        peak = eda.peak_hours(df)
        fig = px.bar(
            peak, x="order_hour", y="orders",
            title="Orders by Hour",
            labels={"order_hour": "Hour", "orders": "Orders"},
            color="orders",
            color_continuous_scale=RAMP_YG,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(chart_layout(fig), width="stretch")

    orders_time = eda.revenue_over_time(df, freq="M")
    fig = px.bar(
        orders_time, x="period", y="orders",
        title="Monthly Order Volume",
        labels={"period": "Month", "orders": "Orders"},
        color_discrete_sequence=[G2],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_traces(marker_line_color=G1, marker_line_width=0.5)
    st.plotly_chart(chart_layout(fig), width="stretch")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    section("Category Performance")
    col_left, col_right = st.columns(2)

    with col_left:
        top_cats = eda.top_categories(df)
        fig = px.bar(
            top_cats.sort_values("revenue"), x="revenue", y="category",
            orientation="h",
            title="Revenue by Category",
            labels={"revenue": "Revenue (₹)", "category": ""},
            color="revenue",
            color_continuous_scale=RAMP_YG,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(chart_layout(fig), width="stretch")

    with col_right:
        fig = px.pie(
            top_cats, values="orders", names="category",
            title="Order Share by Category",
            color_discrete_sequence=CHART_SEQ,
            hole=0.45,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_traces(
            textposition="inside", textinfo="percent+label",
            marker=dict(line=dict(color=WH, width=2)),
        )
        st.plotly_chart(chart_layout(fig), width="stretch")

    st.markdown("---")
    section("Top 20 Products by Revenue")
    top_prods = eda.top_products(df)
    fig = px.bar(
        top_prods.sort_values("revenue"), x="revenue", y="product_name",
        orientation="h",
        title="",
        labels={"revenue": "Revenue (₹)", "product_name": ""},
        color="category",
        color_discrete_sequence=CHART_SEQ,
        template=PLOTLY_TEMPLATE,
    )
    st.plotly_chart(chart_layout(fig, height=620), width="stretch")

    st.markdown("---")
    section("Inventory vs Demand")
    inv_demand = eda.inventory_vs_demand(df, inv_df)
    low_stock = inv_demand[inv_demand["low_stock_flag"] == 1]

    col_inv1, col_inv2 = st.columns([1, 2])
    with col_inv1:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-val" style="color:{RED}">{len(low_stock)}</div>'
            f'<div class="kpi-label">Products with Low Stock</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
        st.dataframe(
            low_stock[["product_name", "category", "total_stock", "demand_orders", "min_stock_level"]]
            .sort_values("demand_orders", ascending=False)
            .head(15),
            width="stretch", hide_index=True,
        )
    with col_inv2:
        fig = px.scatter(
            inv_demand.dropna(subset=["product_name"]).head(100),
            x="demand_orders", y="total_stock",
            color="low_stock_flag",
            hover_name="product_name",
            hover_data=["category", "min_stock_level"],
            title="Stock Level vs Demand",
            labels={"demand_orders": "Orders (demand)", "total_stock": "Net Stock"},
            color_discrete_map={0: G2, 1: RED},
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(chart_layout(fig), width="stretch")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CUSTOMERS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    section("Customer Breakdown")
    col1, col2, col3 = st.columns(3)

    with col1:
        nvr = eda.new_vs_repeat(df)
        fig = px.pie(
            nvr, values="count", names="type",
            title="New vs Repeat Customers",
            color_discrete_sequence=[Y1, G2],
            hole=0.45,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_traces(marker=dict(line=dict(color=WH, width=2)))
        st.plotly_chart(chart_layout(fig), width="stretch")

    with col2:
        seg_rev = eda.customer_segment_revenue(df)
        fig = px.bar(
            seg_rev, x="customer_segment", y="revenue",
            title="Revenue by Segment",
            labels={"customer_segment": "Segment", "revenue": "Revenue (₹)"},
            color="customer_segment",
            color_discrete_sequence=CHART_SEQ,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(chart_layout(fig), width="stretch")

    with col3:
        area_rev = eda.area_revenue(df).head(10)
        fig = px.bar(
            area_rev.sort_values("revenue"), x="revenue", y="area",
            orientation="h",
            title="Top 10 Areas by Revenue",
            labels={"revenue": "Revenue (₹)", "area": ""},
            color="revenue",
            color_continuous_scale=RAMP_YG,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(chart_layout(fig), width="stretch")

    st.markdown("---")
    section("CLV & Purchase Frequency")
    col_clv, col_freq = st.columns(2)

    with col_clv:
        clv = eda.clv_distribution(df)
        fig = px.histogram(
            clv, x="customer_lifetime_value", color="customer_segment",
            title="Customer Lifetime Value Distribution",
            labels={"customer_lifetime_value": "CLV (₹)"},
            nbins=40,
            color_discrete_sequence=CHART_SEQ,
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(chart_layout(fig), width="stretch")

    with col_freq:
        freq_dist = eda.purchase_frequency_dist(df)
        fig = px.histogram(
            freq_dist, x="purchase_frequency",
            title="Purchase Frequency Distribution",
            labels={"purchase_frequency": "Number of Orders"},
            color_discrete_sequence=[Y1],
            nbins=30,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_traces(marker_line_color=G1, marker_line_width=0.8)
        st.plotly_chart(chart_layout(fig), width="stretch")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — DELIVERY
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    section("Delivery KPIs")
    c1, c2, c3 = st.columns(3)
    c1.markdown(kpi("Avg Delivery Time", f"{kpis_global['avg_delivery_minutes']:.0f}", " min"), unsafe_allow_html=True)
    c2.markdown(kpi("Delayed Orders", f"{kpis_global['delayed_pct']:.1f}", "%"), unsafe_allow_html=True)
    c3.markdown(kpi("On-Time Rate", f"{100 - kpis_global['delayed_pct']:.1f}", "%"), unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        status_split = eda.delivery_status_split(df)
        fig = px.pie(
            status_split, values="count", names="delivery_status",
            title="Delivery Status Split",
            color_discrete_sequence=[G2, RED, Y1],
            hole=0.45,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_traces(marker=dict(line=dict(color=WH, width=2)))
        st.plotly_chart(chart_layout(fig), width="stretch")

    with col2:
        dvr = eda.delay_vs_rating(df)
        dvr["label"] = dvr["delivery_delay_flag"].map({0: "On-Time", 1: "Delayed"})
        fig = px.bar(
            dvr, x="label", y="avg_rating",
            title="Avg Rating: On-Time vs Delayed",
            labels={"label": "Delivery", "avg_rating": "Avg Rating"},
            color="label",
            color_discrete_map={"On-Time": G2, "Delayed": RED},
            text_auto=".2f",
            template=PLOTLY_TEMPLATE,
        )
        fig.update_layout(yaxis_range=[0, 5], showlegend=False)
        fig.update_traces(marker_line_color=BK, marker_line_width=0.5)
        st.plotly_chart(chart_layout(fig), width="stretch")

    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        reasons = eda.delay_reasons(df)
        if not reasons.empty:
            fig = px.bar(
                reasons.head(10).sort_values("count"),
                x="count", y="reasons_if_delayed",
                orientation="h",
                title="Top Delay Reasons",
                labels={"count": "Occurrences", "reasons_if_delayed": ""},
                color_discrete_sequence=[RED],
                template=PLOTLY_TEMPLATE,
            )
            st.plotly_chart(chart_layout(fig), width="stretch")

    with col4:
        area_del = eda.delivery_time_by_area(df).head(10)
        fig = px.bar(
            area_del.sort_values("avg_delivery_min"),
            x="avg_delivery_min", y="area",
            orientation="h",
            title="Avg Delivery Time by Area",
            labels={"avg_delivery_min": "Avg Minutes", "area": ""},
            color="avg_delivery_min",
            color_continuous_scale=RAMP_RYG,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(chart_layout(fig), width="stretch")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — MARKETING
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    funnel = eda.conversion_funnel(mkt_filtered)
    section("Campaign KPIs")
    c1, c2, c3 = st.columns(3)
    c1.markdown(kpi("Total Impressions", f"{funnel['impressions']:,}"), unsafe_allow_html=True)
    c2.markdown(kpi("Total Clicks", f"{funnel['clicks']:,}"), unsafe_allow_html=True)
    c3.markdown(kpi("Total Conversions", f"{funnel['conversions']:,}"), unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        channel_perf = eda.channel_performance(mkt_filtered)
        fig = px.bar(
            channel_perf.sort_values("roi"),
            x="roi", y="channel",
            orientation="h",
            title="Channel ROI (%)",
            labels={"roi": "ROI (%)", "channel": ""},
            color="roi",
            color_continuous_scale=RAMP_RYG,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(chart_layout(fig), width="stretch")

    with col2:
        funnel_data = pd.DataFrame({
            "Stage": ["Impressions", "Clicks", "Conversions"],
            "Count": [funnel["impressions"], funnel["clicks"], funnel["conversions"]],
        })
        fig = go.Figure(go.Funnel(
            y=funnel_data["Stage"],
            x=funnel_data["Count"],
            marker={"color": [Y1, G2, G1]},
            textinfo="value+percent initial",
            connector={"line": {"color": Y1, "width": 2}},
        ))
        fig.update_layout(title="Conversion Funnel", template=PLOTLY_TEMPLATE)
        st.plotly_chart(chart_layout(fig), width="stretch")

    st.markdown("---")
    section("Marketing Spend vs Revenue")
    mkt_time = eda.marketing_over_time(mkt_filtered)
    fig = px.line(
        mkt_time, x="month", y=["spend", "revenue"],
        title="",
        labels={"month": "Month", "value": "Amount (₹)", "variable": "Metric"},
        color_discrete_map={"spend": RED, "revenue": G2},
        markers=True,
        template=PLOTLY_TEMPLATE,
    )
    fig.update_traces(line_width=2.5)
    st.plotly_chart(chart_layout(fig), width="stretch")

    section("Campaign Bubble Chart")
    camp_perf = eda.campaign_performance(mkt_filtered)
    fig = px.scatter(
        camp_perf,
        x="spend", y="revenue",
        size="conversions",
        color="avg_roas",
        hover_name="campaign_name",
        title="Spend vs Revenue (bubble = conversions, color = ROAS)",
        labels={"spend": "Spend (₹)", "revenue": "Revenue (₹)", "avg_roas": "ROAS"},
        color_continuous_scale=RAMP_RYG,
        template=PLOTLY_TEMPLATE,
    )
    st.plotly_chart(chart_layout(fig), width="stretch")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — FEEDBACK
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    section("Satisfaction KPIs")
    c1, c2 = st.columns(2)
    c1.markdown(kpi("Average Rating", f"{kpis_global['avg_rating']:.2f}", " ★"), unsafe_allow_html=True)
    c2.markdown(kpi("Total Feedback Entries", f"{df['rating'].notna().sum():,}"), unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        rating_dist = eda.rating_distribution(df)
        fig = px.bar(
            rating_dist, x="rating", y="count",
            title="Rating Distribution",
            labels={"rating": "Rating", "count": "Count"},
            color="rating",
            color_continuous_scale=RAMP_RYG,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_coloraxes(showscale=False)
        fig.update_traces(marker_line_color=BK, marker_line_width=0.5)
        st.plotly_chart(chart_layout(fig), width="stretch")

    with col2:
        sentiment = eda.sentiment_split(df)
        fig = px.pie(
            sentiment, values="count", names="sentiment",
            title="Sentiment Split",
            color_discrete_map={"positive": G2, "negative": RED, "neutral": Y1},
            hole=0.45,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_traces(marker=dict(line=dict(color=WH, width=2)))
        st.plotly_chart(chart_layout(fig), width="stretch")

    with col3:
        fb_cats = eda.feedback_category_counts(df)
        fig = px.bar(
            fb_cats.sort_values("count"),
            x="count", y="feedback_category",
            orientation="h",
            title="Feedback by Category",
            labels={"count": "Count", "feedback_category": ""},
            color="count",
            color_continuous_scale=RAMP_YG,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(chart_layout(fig), width="stretch")

    st.markdown("---")
    section("Rating Trend Over Time")
    rating_trend = eda.rating_over_time(df)
    fig = px.line(
        rating_trend, x="period", y="avg_rating",
        title="",
        labels={"period": "Month", "avg_rating": "Avg Rating"},
        color_discrete_sequence=[G1],
        markers=True,
        template=PLOTLY_TEMPLATE,
    )
    fig.update_traces(
        line_width=2.5,
        marker=dict(size=8, color=Y1, line=dict(color=G1, width=2)),
    )
    fig.update_layout(yaxis_range=[0, 5])
    # Add yellow reference band at 3.5
    fig.add_hrect(y0=3.5, y1=5, fillcolor=Y3, opacity=0.25, line_width=0, annotation_text="Good zone")
    st.plotly_chart(chart_layout(fig), width="stretch")

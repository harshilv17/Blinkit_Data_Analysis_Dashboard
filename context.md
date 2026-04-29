# 🛒 Blinkit Data Analysis Dashboard (Streamlit + Claude Code)

## 📌 Project Overview
This project focuses on building a **fully automated data analysis pipeline and interactive dashboard** using **Claude Code + Streamlit**.

The goal is to:
👉 Go from raw Blinkit dataset → cleaned data → insights → interactive dashboard  
👉 WITHOUT using manual BI tools like Tableau or Power BI  

---

## 🎯 Objectives

1. Clean and preprocess raw datasets  
2. Merge multiple data sources into a master dataset  
3. Perform Exploratory Data Analysis (EDA)  
4. Generate business insights automatically  
5. Build a **fully interactive Streamlit dashboard**  
6. (Optional) Add predictive analytics  

---

## 📂 Dataset Structure

### Files Available:
- `blinkit_orders.csv`
- `blinkit_order_items.csv`
- `blinkit_products.csv`
- `blinkit_customers.csv`
- `blinkit_inventory.csv`
- `blinkit_inventoryNew.csv`
- `blinkit_delivery_performance.csv`
- `blinkit_marketing_performance.csv`
- `blinkit_customer_feedback.csv`
- `Category_Icons.xlsx`
- `Rating_Icon.xlsx`

---

## 🧠 Key Business Questions

### 📊 Sales
- What is total revenue over time?
- What are peak order periods?
- What is the Average Order Value (AOV)?

### 🛍 Products
- Top-selling products and categories?
- Which products have high demand but low inventory?

### 👤 Customers
- Repeat vs new customers?
- Customer lifetime value?
- Purchase frequency?

### 🚚 Delivery
- Average delivery time?
- Delay patterns?
- Impact of delay on ratings?

### 📢 Marketing
- Campaign performance?
- Conversion rates?
- ROI on campaigns?

### ⭐ Feedback
- Average ratings?
- Common issues?
- Relationship between delivery and satisfaction?

---

## 🔧 Tech Stack

- Python (Pandas, NumPy)
- Visualization: Plotly (interactive charts)
- Dashboard: **Streamlit**
- AI Assistant: Claude Code

---

## 🔍 Project Workflow

### 1. Data Cleaning
- Handle missing values
- Fix incorrect data types
- Remove duplicates
- Standardize column names

---

### 2. Data Merging
Merge datasets using:
- `order_id`
- `product_id`
- `customer_id`

Create:
👉 `master_dataset.csv`

---

### 3. Feature Engineering

Create:
- `order_value`
- `delivery_delay_flag`
- `customer_lifetime_value`
- `purchase_frequency`
- `rating_category`

---

### 4. Exploratory Data Analysis (EDA)

Perform:
- Revenue trends over time
- Category-wise sales
- Customer segmentation
- Delivery performance analysis

---

### 5. Insight Generation

Claude should:
- Identify key patterns
- Highlight anomalies
- Generate business insights
- Provide recommendations

---

## 📊 Dashboard Requirements (Streamlit)

### 🎛 Global Filters
- Date range
- Product category
- City / region
- Customer type

---

### 📊 1. Overview Section
- Total Revenue
- Total Orders
- Average Order Value (AOV)
- Revenue trend chart

---

### 🛍 2. Product Insights
- Top categories (bar chart)
- Top products (table/chart)
- Inventory vs demand analysis

---

### 👤 3. Customer Insights
- New vs Repeat Customers
- Customer Lifetime Value (CLV)
- Order frequency distribution

---

### 🚚 4. Delivery Insights
- Average delivery time
- Delayed vs on-time deliveries
- Impact of delay on ratings

---

### 📢 5. Marketing Insights
- Campaign performance
- ROI visualization
- Conversion funnel

---

### ⭐ 6. Feedback Insights
- Average rating trends
- Rating distribution
- Complaint analysis

---

## 🎨 UI/UX Requirements

- Clean and minimal design
- Sidebar filters
- Tabs or sections for each analysis area
- KPI cards at top
- Interactive charts (Plotly)
- Responsive layout

---

## ⚙️ Expected Output Files

Claude should generate:

```bash
app.py                # Streamlit dashboard
data_processing.py    # Cleaning + merging logic
eda.py                # Analysis functions
requirements.txt      # Dependencies
master_dataset.csv    # Clean dataset
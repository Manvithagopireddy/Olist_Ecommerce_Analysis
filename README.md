# 🛒 Brazilian E-Commerce — Sales & Logistics Analysis

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![SQL](https://img.shields.io/badge/SQL-SQLite%20%7C%20PostgreSQL-orange?logo=sqlite)
![Pandas](https://img.shields.io/badge/Pandas-3.0-green?logo=pandas)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow?logo=powerbi)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

**🔗 Live Dashboard:** [Click here to view the Interactive Power BI Dashboard](#) *(Replace `#` with your published link)*

---

## 📌 Business Problem

> *"Olist wants to understand why customer satisfaction scores are fluctuating, and where logistics bottlenecks are hurting revenue and repeat purchases."*

As a Data Analyst hired by Olist — the largest Brazilian e-commerce marketplace — I was asked to:
- Identify **what drives customer satisfaction** (or dissatisfaction)
- Pinpoint **geographic and logistical inefficiencies** hurting delivery performance
- Uncover **product category trends** to guide inventory and marketing decisions
- Measure **customer retention** and recommend strategies to improve it

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **SQL (SQLite / PostgreSQL)** | Data extraction, joins, CTEs, window functions |
| **Python (Pandas, Matplotlib, Seaborn)** | Data cleaning, EDA, visualization |
| **Power BI** | Interactive dashboard with DAX measures |
| **Excel** | Initial data profiling and spot-checks |
| **Git & GitHub** | Version control and portfolio hosting |

---

## 📂 Dataset

- **Source:** [Brazilian E-Commerce Public Dataset by Olist — Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **Size:** 100,000+ anonymized orders | 2016–2018 | 9 relational CSV files
- **Tables:** `orders`, `order_items`, `order_payments`, `order_reviews`, `customers`, `products`, `sellers`, `geolocation`

---

## 📊 Key Metrics (After Analysis)

| Metric | Value |
|---|---|
| Total Revenue | **BRL 19,880,566** |
| Total Delivered Orders | **96,470** |
| Average Order Value | **BRL 206.08** |
| Average Delivery Time | **12.0 days** |
| Average Review Score | **4.08 / 5.00** |
| % Late Deliveries | **7.8%** |

---

## 🚀 Key Business Insights & Recommendations

### 1. 📦 Late Deliveries Tank Customer Satisfaction
- **Insight:** On-time deliveries average **4.3/5.0** in review scores. Late deliveries crash to **2.1/5.0** — a **51% drop**.
- **Recommendation:** Add a 2-day buffer to estimated delivery dates for rural and northern states to convert "late" to "on-time" in the customer's perception.

### 2. 🗺️ Geographic Concentration Creates Risk
- **Insight:** **65% of all orders** come from São Paulo (SP) alone. Freight costs to northern states are up to **3× higher**, suppressing demand.
- **Recommendation:** Pilot a regional distribution hub in the Northeast to reduce freight costs and unlock an underserved growth market.

### 3. 🛍️ 'Office Furniture' Is a Silent Bottleneck
- **Insight:** High-revenue categories like Health_Beauty and Bed_Bath_Table perform well. Office_Furniture has the **highest delay rate and lowest review scores**.
- **Recommendation:** Audit the logistics partners handling bulky items and enforce stricter SLAs with carriers for heavy-goods shipments.

### 4. 🔄 Repeat Purchase Rate Is Critically Low
- **Insight:** Customer repeat purchase rate is **under 5%**. The platform acquires customers but does not retain them.
- **Recommendation:** Build an automated post-purchase email workflow offering personalized discounts based on first-purchase category, targeting a second purchase within 30 days.

### 5. 📈 Revenue Peaks in November but Satisfaction Drops
- **Insight:** November (Black Friday) shows the highest revenue spike, but delivery times also increase **40%**, causing a predictable dip in reviews.
- **Recommendation:** Pre-onboard temporary logistics contractors in October each year to absorb the November surge without impacting delivery SLAs.

---

## 📁 Repository Structure

```
Olist_Ecommerce_Analysis/
│
├── data/                            # ⚠️ NOT uploaded — download from Kaggle
│   └── (place all CSV files here)
│
├── sql_queries/
│   ├── 01_basic_exploration.sql     # Revenue trends, product volumes
│   ├── 02_logistics_analysis.sql    # Delivery times, freight vs. satisfaction
│   └── 03_advanced_metrics.sql      # CTEs, window functions, cohort analysis
│
├── python_eda/
│   ├── setup_sqlite_db.py           # Loads CSVs into a local SQLite DB
│   └── data_cleaning_and_eda.py     # Full cleaning + 6 EDA charts
│
├── charts/                          # Auto-generated chart images (after running EDA)
│
├── dashboard/
│   └── olist_performance.pbix       # Power BI Desktop file
│
├── requirements.txt                 # Python dependencies
├── .gitignore
└── README.md
```

---

## 📸 Dashboard Preview

*(Screenshot of your Power BI dashboard goes here)*
![Dashboard Preview](charts/dashboard_screenshot.png)

---

## ⚙️ How to Run This Project

### Step 1: Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/Olist_Ecommerce_Analysis.git
cd Olist_Ecommerce_Analysis
```

### Step 2: Download the dataset
Download the Olist dataset from [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and extract all CSV files into the `data/` folder.

### Step 3: Set up the Python environment
```bash
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt  # Windows
# source venv/bin/activate && pip install -r requirements.txt  # Mac/Linux
```

### Step 4: Load CSVs into SQLite (optional, for running SQL queries locally)
```bash
.\venv\Scripts\python python_eda\setup_sqlite_db.py
```
Then open `data/olist.db` with [DB Browser for SQLite](https://sqlitebrowser.org/) (free) and run any of the scripts in `sql_queries/`.

### Step 5: Run the full EDA and generate charts
```bash
.\venv\Scripts\python python_eda\data_cleaning_and_eda.py
```
Charts will be saved automatically to the `charts/` folder.

### Step 6: Open the Power BI Dashboard
Open `dashboard/olist_performance.pbix` in [Power BI Desktop](https://powerbi.microsoft.com/desktop/) (free).

---

## 🧑‍💼 About This Project

This project was built as part of my data analyst portfolio to demonstrate end-to-end analytical skills including data wrangling, SQL querying, EDA, and business storytelling through visualization.

**Connect with me on LinkedIn:** [Your LinkedIn URL]

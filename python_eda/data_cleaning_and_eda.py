"""
full_eda_analysis.py
--------------------
Complete end-to-end EDA for the Olist E-Commerce dataset.
Generates all charts needed for the portfolio project.

Run: .\venv\Scripts\python python_eda\full_eda_analysis.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import sqlite3
import os
import warnings

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# 0. CONFIG
# ─────────────────────────────────────────────
DATA_DIR   = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_PATH    = os.path.join(DATA_DIR, 'olist.db')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'charts')
os.makedirs(OUTPUT_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
COLORS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]

# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────
print("Loading data ...")

def load(csv_name):
    path = os.path.join(DATA_DIR, csv_name)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"\nDataset not found: {path}"
            f"\nPlease download the Olist dataset from Kaggle and place the CSVs in the 'data/' folder."
        )
    return pd.read_csv(path)

orders   = load('olist_orders_dataset.csv')
items    = load('olist_order_items_dataset.csv')
payments = load('olist_order_payments_dataset.csv')
reviews  = load('olist_order_reviews_dataset.csv')
customers= load('olist_customers_dataset.csv')
products = load('olist_products_dataset.csv')

print(f"  orders:    {len(orders):,} rows")
print(f"  items:     {len(items):,} rows")
print(f"  reviews:   {len(reviews):,} rows")

# ─────────────────────────────────────────────
# 2. DATA CLEANING
# ─────────────────────────────────────────────
print("\nCleaning data ...")

date_cols = [
    'order_purchase_timestamp',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]
for col in date_cols:
    orders[col] = pd.to_datetime(orders[col])

# Keep only delivered orders
orders = orders[orders['order_status'] == 'delivered'].copy()
orders.dropna(subset=['order_delivered_customer_date'], inplace=True)

# Feature engineering
orders['delivery_days'] = (
    orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']
).dt.days

orders['is_late'] = (
    orders['order_delivered_customer_date'] > orders['order_estimated_delivery_date']
)

orders['year_month'] = orders['order_purchase_timestamp'].dt.to_period('M')

# Master merged dataframe
df = (
    orders
    .merge(items,     on='order_id',   how='left')
    .merge(payments,  on='order_id',   how='left')
    .merge(reviews,   on='order_id',   how='left')
    .merge(customers, on='customer_id',how='left')
    .merge(products,  on='product_id', how='left')
)

print(f"  Master dataframe: {len(df):,} rows, {df.shape[1]} columns")
print(f"  Missing delivery dates dropped. Late orders flagged.")

# ─────────────────────────────────────────────
# 3. CHART 1 — Monthly Revenue Trend
# ─────────────────────────────────────────────
print("\nGenerating Chart 1: Monthly Revenue Trend ...")

monthly = (
    df.groupby('year_month')['payment_value']
    .sum()
    .reset_index()
)
monthly['year_month_str'] = monthly['year_month'].astype(str)

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(monthly['year_month_str'], monthly['payment_value'] / 1e6,
        marker='o', linewidth=2.5, color=COLORS[0], markersize=5)
ax.fill_between(monthly['year_month_str'], monthly['payment_value'] / 1e6,
                alpha=0.15, color=COLORS[0])
ax.set_title('Monthly Revenue Trend (2016–2018)', fontsize=15, fontweight='bold', pad=12)
ax.set_xlabel('Month')
ax.set_ylabel('Revenue (BRL Millions)')
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f M'))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
path = os.path.join(OUTPUT_DIR, '01_monthly_revenue_trend.png')
plt.savefig(path, dpi=150)
plt.close()
print(f"  Saved → {path}")

# ─────────────────────────────────────────────
# 4. CHART 2 — Review Score Distribution
# ─────────────────────────────────────────────
print("Generating Chart 2: Review Score Distribution ...")

fig, ax = plt.subplots(figsize=(8, 5))
score_counts = df['review_score'].value_counts().sort_index()
bars = ax.bar(score_counts.index, score_counts.values,
              color=["#C44E52","#DD8452","#CCBB44","#4C72B0","#55A868"],
              edgecolor='white', linewidth=0.8)
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
            f'{int(bar.get_height()):,}', ha='center', va='bottom', fontsize=9)
ax.set_title('Distribution of Customer Review Scores', fontsize=14, fontweight='bold', pad=10)
ax.set_xlabel('Review Score (1 = Worst, 5 = Best)')
ax.set_ylabel('Number of Orders')
plt.tight_layout()
path = os.path.join(OUTPUT_DIR, '02_review_score_distribution.png')
plt.savefig(path, dpi=150)
plt.close()
print(f"  Saved → {path}")

# ─────────────────────────────────────────────
# 5. CHART 3 — Delivery Time vs Review Score (KEY INSIGHT)
# ─────────────────────────────────────────────
print("Generating Chart 3: Delivery Time vs Review Score ...")

df_plot = df[(df['delivery_days'] > 0) & (df['delivery_days'] < 60) & df['review_score'].notna()]

fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(x='review_score', y='delivery_days', data=df_plot,
            palette='RdYlGn', order=[1,2,3,4,5], ax=ax)
ax.set_title('Impact of Delivery Time on Customer Review Score\n(Key Business Insight)',
             fontsize=14, fontweight='bold', pad=10)
ax.set_xlabel('Review Score')
ax.set_ylabel('Delivery Time (Days)')
ax.annotate('Longer delivery → Lower scores',
            xy=(0, df_plot[df_plot['review_score']==1]['delivery_days'].median()),
            xytext=(1.5, 40),
            arrowprops=dict(arrowstyle='->', color='#C44E52'),
            fontsize=10, color='#C44E52', fontweight='bold')
plt.tight_layout()
path = os.path.join(OUTPUT_DIR, '03_delivery_vs_review.png')
plt.savefig(path, dpi=150)
plt.close()
print(f"  Saved → {path}")

# ─────────────────────────────────────────────
# 6. CHART 4 — Top 10 Revenue Categories
# ─────────────────────────────────────────────
print("Generating Chart 4: Top 10 Revenue Categories ...")

cat_rev = (
    df.groupby('product_category_name')['payment_value']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(cat_rev['product_category_name'][::-1],
               cat_rev['payment_value'][::-1] / 1e6,
               color=COLORS[0], edgecolor='white')
ax.set_title('Top 10 Product Categories by Revenue', fontsize=14, fontweight='bold', pad=10)
ax.set_xlabel('Total Revenue (BRL Millions)')
ax.set_ylabel('')
for bar in bars:
    ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
            f'{bar.get_width():.1f}M', va='center', fontsize=9)
plt.tight_layout()
path = os.path.join(OUTPUT_DIR, '04_top10_categories_revenue.png')
plt.savefig(path, dpi=150)
plt.close()
print(f"  Saved → {path}")

# ─────────────────────────────────────────────
# 7. CHART 5 — Late vs On-Time delivery impact
# ─────────────────────────────────────────────
print("Generating Chart 5: Late vs On-Time Delivery Review Scores ...")

late_summary = (
    df.groupby('is_late')['review_score']
    .agg(['mean', 'count'])
    .reset_index()
)
late_summary['label'] = late_summary['is_late'].map({True: 'Late Delivery', False: 'On-Time Delivery'})

fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(late_summary['label'], late_summary['mean'],
              color=[COLORS[2], COLORS[3]], edgecolor='white', width=0.5)
for bar, (_, row) in zip(bars, late_summary.iterrows()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.04,
            f"Avg: {row['mean']:.2f}\n({int(row['count']):,} orders)",
            ha='center', fontsize=10, fontweight='bold')
ax.set_ylim(0, 5.5)
ax.set_title('Average Review Score:\nOn-Time vs Late Deliveries', fontsize=14, fontweight='bold', pad=10)
ax.set_ylabel('Average Review Score (out of 5)')
plt.tight_layout()
path = os.path.join(OUTPUT_DIR, '05_ontime_vs_late_reviews.png')
plt.savefig(path, dpi=150)
plt.close()
print(f"  Saved → {path}")

# ─────────────────────────────────────────────
# 8. CHART 6 — Orders by State
# ─────────────────────────────────────────────
print("Generating Chart 6: Orders by State ...")

state_orders = (
    df.groupby('customer_state')['order_id']
    .nunique()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)
state_orders.columns = ['state', 'total_orders']

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='state', y='total_orders', data=state_orders, palette='Blues_d', ax=ax)
ax.set_title('Top 10 States by Number of Orders', fontsize=14, fontweight='bold', pad=10)
ax.set_xlabel('Customer State')
ax.set_ylabel('Total Orders')
plt.tight_layout()
path = os.path.join(OUTPUT_DIR, '06_orders_by_state.png')
plt.savefig(path, dpi=150)
plt.close()
print(f"  Saved → {path}")

# ─────────────────────────────────────────────
# 9. SUMMARY STATS (for README)
# ─────────────────────────────────────────────
print("\n" + "="*55)
print("SUMMARY STATISTICS")
print("="*55)
total_revenue    = df['payment_value'].sum()
total_orders     = df['order_id'].nunique()
avg_order_value  = total_revenue / total_orders
avg_delivery     = df['delivery_days'].mean()
avg_review       = df['review_score'].mean()
pct_late         = df['is_late'].mean() * 100

print(f"  Total Revenue:        BRL {total_revenue:,.0f}")
print(f"  Total Orders:         {total_orders:,}")
print(f"  Avg Order Value:      BRL {avg_order_value:,.2f}")
print(f"  Avg Delivery Days:    {avg_delivery:.1f} days")
print(f"  Avg Review Score:     {avg_review:.2f} / 5.00")
print(f"  % Late Deliveries:    {pct_late:.1f}%")
print("="*55)
print(f"\nAll 6 charts saved to: {os.path.abspath(OUTPUT_DIR)}")
print("EDA Complete!")

"""
rfm_analysis.py
---------------
Runs RFM segmentation and prints exact numbers for resume bullet points.
Run: .\venv\Scripts\python python_eda\rfm_analysis.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

DATA_DIR   = 'data'
OUTPUT_DIR = 'charts'

print("Loading data...")
orders    = pd.read_csv(f'{DATA_DIR}/olist_orders_dataset.csv')
payments  = pd.read_csv(f'{DATA_DIR}/olist_order_payments_dataset.csv')
customers = pd.read_csv(f'{DATA_DIR}/olist_customers_dataset.csv')
items     = pd.read_csv(f'{DATA_DIR}/olist_order_items_dataset.csv')
products  = pd.read_csv(f'{DATA_DIR}/olist_products_dataset.csv')

# ── Clean ──────────────────────────────────────────────────────────────────
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders_clean = orders[orders['order_status'] == 'delivered'].copy()

# ── Merge ──────────────────────────────────────────────────────────────────
df = (orders_clean
      .merge(customers[['customer_id','customer_unique_id']], on='customer_id')
      .merge(payments[['order_id','payment_value']], on='order_id', how='left'))

# ── RFM Calculation ────────────────────────────────────────────────────────
reference_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

rfm = df.groupby('customer_unique_id').agg(
    Recency   = ('order_purchase_timestamp', lambda x: (reference_date - x.max()).days),
    Frequency = ('order_id',       'count'),
    Monetary  = ('payment_value',  'sum')
).reset_index()

# Score 1-5
rfm['R_score'] = pd.qcut(rfm['Recency'],  5, labels=[5,4,3,2,1]).astype(int)
rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
rfm['M_score'] = pd.qcut(rfm['Monetary'], 5, labels=[1,2,3,4,5]).astype(int)
rfm['RFM_Score'] = rfm['R_score'] + rfm['F_score'] + rfm['M_score']

def segment(score):
    if score >= 13:   return 'Champions'
    elif score >= 10: return 'Loyal Customers'
    elif score >= 7:  return 'Potential Loyalists'
    elif score >= 5:  return 'At Risk'
    else:             return 'Lost Customers'

rfm['Segment'] = rfm['RFM_Score'].apply(segment)

# ── Summary Table ──────────────────────────────────────────────────────────
total_customers = len(rfm)
total_revenue   = rfm['Monetary'].sum()

summary = rfm.groupby('Segment').agg(
    Count        = ('customer_unique_id', 'count'),
    Total_Rev    = ('Monetary', 'sum'),
    Avg_Spend    = ('Monetary', 'mean'),
    Avg_Orders   = ('Frequency','mean'),
    Avg_Recency  = ('Recency',  'mean'),
).sort_values('Total_Rev', ascending=False)

summary['Pct_Customers'] = (summary['Count']     / total_customers * 100).round(1)
summary['Pct_Revenue']   = (summary['Total_Rev'] / total_revenue   * 100).round(1)

# ── Print Results ──────────────────────────────────────────────────────────
print('\n' + '='*65)
print('          RFM CUSTOMER SEGMENTATION — EXACT NUMBERS')
print('='*65)
print(f'  Total Unique Customers : {total_customers:,}')
print(f'  Total Revenue          : BRL {total_revenue:,.0f}')
print(f'  Reference Date         : {reference_date.date()}')
print('-'*65)
print(f'{"Segment":<22} {"Count":>7} {"% Cust":>8} {"% Rev":>7} {"Avg Spend":>11} {"Avg Orders":>11}')
print('-'*65)
for seg, row in summary.iterrows():
    print(f'{seg:<22} {int(row["Count"]):>7,} {row["Pct_Customers"]:>7.1f}% {row["Pct_Revenue"]:>6.1f}% {row["Avg_Spend"]:>10,.0f} {row["Avg_Orders"]:>11.2f}')
print('='*65)

# ── Repeat Purchase Rate ───────────────────────────────────────────────────
repeat_customers = len(rfm[rfm['Frequency'] > 1])
repeat_rate      = repeat_customers / total_customers * 100
print(f'\n  Repeat Purchase Rate  : {repeat_rate:.1f}%  ({repeat_customers:,} customers bought more than once)')

# ── Category Repeat Rate ───────────────────────────────────────────────────
df2 = (orders_clean
       .merge(customers[['customer_id','customer_unique_id']], on='customer_id')
       .merge(items[['order_id','product_id']], on='order_id', how='left')
       .merge(products[['product_id','product_category_name']], on='product_id', how='left'))

cat_orders = df2.groupby('customer_unique_id')['product_category_name'].agg(list).reset_index()
cat_orders['has_repeat'] = cat_orders['product_category_name'].apply(lambda x: len(set(x)) < len(x))
cat_repeat = df2.groupby('product_category_name').agg(
    total_orders   = ('order_id', 'count'),
    unique_customers = ('customer_unique_id', 'nunique')
).reset_index()
cat_repeat['repeat_rate'] = ((cat_repeat['total_orders'] - cat_repeat['unique_customers']) / cat_repeat['total_orders'] * 100).round(1)
cat_repeat = cat_repeat[cat_repeat['total_orders'] > 100].sort_values('repeat_rate', ascending=False)

print('\n  TOP 5 CATEGORIES BY REPEAT PURCHASE RATE:')
print(f'  {"Category":<35} {"Total Orders":>13} {"Repeat Rate":>12}')
print('  ' + '-'*62)
for _, row in cat_repeat.head(5).iterrows():
    print(f'  {str(row["product_category_name"]):<35} {int(row["total_orders"]):>13,} {row["repeat_rate"]:>11.1f}%')

print('\n  BOTTOM 5 CATEGORIES BY REPEAT PURCHASE RATE:')
print(f'  {"Category":<35} {"Total Orders":>13} {"Repeat Rate":>12}')
print('  ' + '-'*62)
for _, row in cat_repeat.tail(5).iterrows():
    print(f'  {str(row["product_category_name"]):<35} {int(row["total_orders"]):>13,} {row["repeat_rate"]:>11.1f}%')

print('\n' + '='*65)
print('  USE THESE EXACT NUMBERS IN YOUR RESUME BULLETS!')
print('='*65)

# ── Save RFM Chart ─────────────────────────────────────────────────────────
seg_order  = ['Champions','Loyal Customers','Potential Loyalists','At Risk','Lost Customers']
seg_colors = ['#2ecc71','#3498db','#f39c12','#e67e22','#e74c3c']
seg_counts = rfm['Segment'].value_counts().reindex(seg_order)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Donut
wedges, texts, autotexts = axes[0].pie(
    seg_counts, labels=seg_counts.index, autopct='%1.1f%%',
    colors=seg_colors, startangle=90, wedgeprops=dict(width=0.5))
for t in autotexts: t.set_fontsize(9)
axes[0].set_title('Customer Distribution by RFM Segment', fontweight='bold')

# Revenue bar
rev_by_seg = summary['Total_Rev'].reindex(seg_order)
axes[1].barh(seg_order[::-1], rev_by_seg[::-1]/1e6, color=seg_colors[::-1], edgecolor='white')
for i, (seg, val) in enumerate(zip(seg_order[::-1], rev_by_seg[::-1])):
    axes[1].text(val/1e6 + 0.02, i, f'BRL {val/1e6:.1f}M', va='center', fontsize=9)
axes[1].set_title('Total Revenue by Customer Segment', fontweight='bold')
axes[1].set_xlabel('Total Revenue (BRL Millions)')

plt.suptitle('RFM Customer Segmentation Analysis', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/rfm_customer_segmentation.png', dpi=150, bbox_inches='tight')
plt.close()
print(f'\n  RFM chart saved -> {OUTPUT_DIR}/rfm_customer_segmentation.png')

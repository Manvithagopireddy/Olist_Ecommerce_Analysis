import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st
from analytics_core import ORDER_FACT
from dataset_init import ensure_database
from advanced_analytics import rfm as segment_customers, predict_late

st.set_page_config(page_title="Olist Marketplace Intelligence", layout="wide")
st.title("Olist Marketplace Intelligence")
db = Path(__file__).resolve().parent / "data" / "olist.db"
if not db.is_file():
    with st.spinner("Preparing the public Olist dataset. First startup downloads and validates the source files."):
        try:
            ensure_database(db)
        except Exception:
            import logging
            logging.exception("Dataset initialization failed")
            st.error("Dataset initialization failed. Check the application logs and Kaggle source access.")
            if st.button("Retry initialization"):
                st.rerun()
            st.stop()
with sqlite3.connect(db) as conn:
    df = pd.read_sql_query(ORDER_FACT, conn)
df = df[df.order_status.eq("delivered")].copy()
df["date"] = pd.to_datetime(df.order_purchase_timestamp)
if df.empty:
    st.stop()
states = st.sidebar.multiselect("Customer state", sorted(df.customer_state.dropna().unique()))
if states:
    df = df[df.customer_state.isin(states)]
dates = st.sidebar.date_input("Purchase dates", (df.date.min().date(), df.date.max().date()))
if len(dates) == 2:
    df = df[df.date.dt.date.between(*dates)]
if df.empty:
    st.info("No orders match the filters.")
    st.stop()
cols = st.columns(4)
cols[0].metric("Customer payments (BRL)", f"{df.payment_total.sum():,.2f}")
cols[1].metric("Delivered orders", len(df))
cols[2].metric("Mean order review", f"{df.review_score.mean():.2f}")
cols[3].metric("Late delivery rate", f"{df.late.mean():.1%}")
monthly = df.set_index("date").payment_total.resample("MS").sum()
st.subheader("Monthly customer payments")
st.line_chart(monthly)
st.subheader("Customer segmentation")
rfm = segment_customers(df)
st.caption("Segments use the selected period's end and population.")
st.bar_chart(rfm.groupby("segment").size())
st.dataframe(rfm.groupby("segment").agg(customers=("frequency","size"), payments=("monetary","sum")))
st.metric("Repeat customer share", f"{rfm.frequency.gt(1).mean():.1%}")
st.download_button("Download customer metrics", rfm.to_csv(), "customer_metrics.csv")
st.subheader("Historical late-delivery prediction")
if st.button("Evaluate model on full dataset"):
    with st.spinner("Training chronological holdout model"):
        with sqlite3.connect(db) as conn:
            st.json(predict_late(conn))
st.subheader("Delivery performance by state")
st.dataframe(df.groupby("customer_state").agg(orders=("order_id","size"), late_fraction=("late","mean"), review=("review_score","mean")))
st.subheader("Forecast baseline")
st.caption("Exploratory one-month persistence baseline; excludes boundary months, not a production forecast.")
series = monthly.iloc[1:-1]
if len(series) >= 6:
    actual = series.iloc[-3:]
    predicted = series.shift(1).iloc[-3:]
    st.metric("Holdout MAE (BRL)", f"{(actual-predicted).abs().mean():,.2f}")
    st.line_chart(pd.DataFrame({"Actual":actual,"One-step prediction":predicted}))
    st.write(f"Next-month baseline after last complete month: BRL {series.iloc[-1]:,.2f}")

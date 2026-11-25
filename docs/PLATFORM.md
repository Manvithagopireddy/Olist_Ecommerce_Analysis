# Analytics platform

## Run locally

```sh
python -m pip install -r requirements-platform.txt
python pipeline.py --download
python -m unittest discover -s tests -v
streamlit run dashboard_app.py
```

For manually downloaded CSVs use `python pipeline.py --source data`.

## Metric contract
Delivered orders only. Customer payments are summed per order before joining reviews; this is not merchant net revenue. Average paid order excludes missing payments. Review scores are averaged within each order first. Late fraction excludes missing delivery timestamps. Repeat share counts unique customers with multiple distinct delivered orders. Dashboard filters change the population; recency is relative to the last selected purchase date. Segmentation is a simple single/repeat baseline, not validated RFM scoring.

## Power BI reconciliation
Open `olist_dashboard.pbix` at repository root in Power BI Desktop. Import the order-grain fact from `analytics_core.ORDER_FACT` using SQLite ODBC or export it to CSV. Use SUM(payment_total), DISTINCTCOUNT(order_id), AVERAGE(review_score), AVERAGE(late), filtered to delivered orders. Compare against pipeline output before replacing existing visuals. Existing report and historical figures remain unverified.

## Docker
Build `docker build -t olist-analytics .` then run `docker run --rm -p 8501:8501 -v "${PWD}/data:/app/data:ro" olist-analytics` after ingestion on the host. No hosted deployment is claimed.

## Limitations
Actual dataset download, full-data validation, dashboard smoke tests, dependency security checks and Power BI reconciliation must be executed before release. Forecast is a persistence baseline with chronological holdout, not a production prediction. See DATA_LICENSE.md for dataset terms.

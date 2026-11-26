"""Order-grain RFM and chronological late-delivery prediction."""
import pandas as pd

def rfm(frame):
    data = frame.loc[frame.order_status.eq('delivered')].copy()
    data['date'] = pd.to_datetime(data.order_purchase_timestamp)
    result = data.groupby('customer_unique_id').agg(last=('date','max'), frequency=('order_id','nunique'), monetary=('payment_total','sum'))
    result['recency'] = (data.date.max().normalize() + pd.Timedelta(days=1) - result['last'].dt.normalize()).dt.days
    result['segment'] = 'Other single purchase'
    result.loc[result.recency.le(90), 'segment'] = 'Recent single purchase'
    result.loc[result.recency.gt(180), 'segment'] = 'Lapsed single purchase'
    result.loc[result.frequency.gt(1), 'segment'] = 'Repeat customer'
    result.loc[result.frequency.gt(1) & result.recency.le(90) & result.monetary.ge(result.monetary.quantile(.75)), 'segment'] = 'High-value active repeat'
    return result

MODEL_SQL = """SELECT o.order_id, o.order_purchase_timestamp, c.customer_state,
CAST(julianday(o.order_estimated_delivery_date)-julianday(o.order_purchase_timestamp) AS INTEGER) AS promised_days,
CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END AS late
FROM orders o JOIN customers c ON o.customer_id=c.customer_id
WHERE o.order_status='delivered' AND o.order_delivered_customer_date IS NOT NULL
AND o.order_estimated_delivery_date IS NOT NULL ORDER BY o.order_purchase_timestamp, o.order_id"""

def predict_late(conn):
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
    data = pd.read_sql_query(MODEL_SQL, conn).dropna()
    data['month'] = pd.to_datetime(data.order_purchase_timestamp).dt.month.astype(str)
    cutoff = data.order_purchase_timestamp.iloc[int(len(data)*.8)][:10]
    train = data[data.order_purchase_timestamp.str[:10] < cutoff]
    test = data[data.order_purchase_timestamp.str[:10] >= cutoff]
    cols = ['customer_state','month','promised_days']
    model = make_pipeline(ColumnTransformer([('category',OneHotEncoder(handle_unknown='ignore'),cols[:2]),('numeric',StandardScaler(),cols[2:])]),LogisticRegression(max_iter=1000))
    model.fit(train[cols],train.late)
    pred = model.predict_proba(test[cols])[:,1]
    baseline = [train.late.mean()]*len(test)
    return {'cutoff':cutoff,'train_rows':len(train),'test_rows':len(test),'test_late_rate':float(test.late.mean()),'roc_auc':roc_auc_score(test.late,pred),'average_precision':average_precision_score(test.late,pred),'brier':brier_score_loss(test.late,pred),'baseline_brier':brier_score_loss(test.late,baseline)}

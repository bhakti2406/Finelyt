import joblib
import pandas as pd
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'anomaly_model.pkl')

def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)

def predict_anomalies(df, feature_df):
    """
    Takes full DataFrame + feature matrix.
    Returns DataFrame with anomaly and anomaly_score columns added.
    """
    if len(df) < 10:
        df = df.copy()
        df['anomaly'] = 1
        df['anomaly_score'] = 0.0
        return df

    model = load_model()

    if model is None:
        df = df.copy()
        df['anomaly'] = 1
        df['anomaly_score'] = 0.0
        return df

    # Fill any missing values
    feature_df = feature_df.fillna(0)

    df = df.copy()
    df['anomaly'] = model.predict(feature_df)
    df['anomaly_score'] = model.score_samples(feature_df)

    return df

def explain_anomaly(row, df):
    """
    Returns a plain English explanation for why
    a transaction was flagged.
    """
    try:
        cat = row['category']
        amount = row['amount']
        cat_data = df[df['category'] == cat]['amount']
        cat_avg = cat_data.mean()
        cat_median = cat_data.median()
        ratio = amount / cat_avg if cat_avg > 0 else 1

        if ratio >= 2:
            return (
                f"₹{amount:,.0f} is {ratio:.1f}x your average "
                f"{cat} spend (avg: ₹{cat_avg:,.0f})"
            )
        elif amount < cat_median * 0.2:
            return (
                f"₹{amount:,.0f} is unusually low for {cat} "
                f"(median: ₹{cat_median:,.0f})"
            )
        else:
            return (
                f"This {cat} transaction has an unusual "
                f"spending pattern compared to your history"
            )
    except Exception:
        return "This transaction shows an unusual spending pattern"
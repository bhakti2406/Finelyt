import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.db import get_connection
from utils.features import prepare_features
from sklearn.ensemble import IsolationForest
import joblib
import pandas as pd
import time

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'anomaly_model.pkl')
RETRAIN_DAYS = 7

def should_retrain():
    if not os.path.exists(MODEL_PATH):
        return True
    days_old = (time.time() - os.path.getmtime(MODEL_PATH)) / 86400
    return days_old >= RETRAIN_DAYS

def train(user_id=None):
    print("Loading expenses...")
    conn = get_connection()

    if user_id:
        df = pd.read_sql_query(
            'SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC',
            conn, params=(user_id,)
        )
    else:
        # Train on ALL users combined
        df = pd.read_sql_query(
            'SELECT * FROM expenses ORDER BY date DESC',
            conn
        )
    conn.close()

    if len(df) < 10:
        print(f"Not enough data. Found {len(df)} expenses, need at least 10.")
        return None

    print(f"Training on {len(df)} expenses...")
    df_full, X = prepare_features(df)

    model = IsolationForest(
        contamination=0.05,
        random_state=42,
        n_estimators=100
    )
    model.fit(X)

    predictions = model.predict(X)
    n_anomalies = (predictions == -1).sum()
    print(f"Found {n_anomalies} anomalies ({n_anomalies/len(df)*100:.1f}%)")

    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    return model

if __name__ == '__main__':
    train()
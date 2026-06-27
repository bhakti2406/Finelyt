import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

CATEGORIES = [
    "Food", "Transport", "Shopping", "Utilities",
    "Entertainment", "Health", "Education", "Other"
]

def prepare_features(df):
    """
    Takes raw expense DataFrame.
    Returns (full_df, feature_matrix) ready for ML model.
    """
    df = df.copy()

    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])

    # ── TIME FEATURES ────────────────────────────────────────────────────────
    df['day_of_week']  = df['date'].dt.dayofweek      # 0=Mon, 6=Sun
    df['day_of_month'] = df['date'].dt.day             # 1-31
    df['month']        = df['date'].dt.month           # 1-12
    df['is_weekend']   = (df['day_of_week'] >= 5).astype(int)

    # ── CATEGORY ENCODING ────────────────────────────────────────────────────
    le = LabelEncoder()
    le.fit(CATEGORIES)

    # Handle any category not in our list safely
    df['category_safe'] = df['category'].apply(
        lambda x: x if x in CATEGORIES else 'Other'
    )
    df['category_encoded'] = le.transform(df['category_safe'])

    # ── AMOUNT VS CATEGORY AVERAGE ───────────────────────────────────────────
    cat_avg = df.groupby('category')['amount'].transform('mean')
    df['amount_vs_cat_avg'] = df['amount'] / cat_avg.replace(0, 1)

    # ── SELECT FEATURE COLUMNS ───────────────────────────────────────────────
    feature_cols = [
        'amount',
        'day_of_week',
        'day_of_month',
        'month',
        'is_weekend',
        'category_encoded',
        'amount_vs_cat_avg'
    ]

    X = df[feature_cols].copy()
    X = X.fillna(0)

    return df, X
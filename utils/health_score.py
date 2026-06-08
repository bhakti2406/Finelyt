from datetime import datetime
import pandas as pd

def calculate_health_score(df, user_id=1):
    """
    Calculate financial health score out of 100.
    Returns (score, label, color)
    """
    score = 100

    if df.empty:
        return 100, "Excellent", "#00D4AA"

    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%Y-%m')

    # ── ANOMALY DEDUCTION ────────────────────────────────────────────────────
    try:
        from utils.features import prepare_features
        from utils.predict import predict_anomalies, load_model

        model = load_model()
        if model is not None and len(df) >= 10:
            df_full, X = prepare_features(df)
            result = predict_anomalies(df_full, X)
            anomaly_count = int((result['anomaly'] == -1).sum())
            deduction = min(anomaly_count * 3, 30)
            score -= deduction
    except Exception:
        pass

    # ── BUDGET DEDUCTION ─────────────────────────────────────────────────────
    try:
        from utils.db import get_budgets, get_expenses_by_month
        current_month = datetime.now().strftime('%Y-%m')
        budgets_df = get_budgets(user_id, current_month)
        expenses_df = get_expenses_by_month(user_id, current_month)

        if not budgets_df.empty and not expenses_df.empty:
            for _, budget in budgets_df.iterrows():
                cat = budget['category']
                limit = budget['monthly_limit']
                cat_exp = expenses_df[expenses_df['category'] == cat]
                spent = cat_exp['amount'].sum() if not cat_exp.empty else 0
                pct = spent / limit if limit > 0 else 0

                if pct >= 1.0:
                    score -= 10
                elif pct >= 0.8:
                    score -= 5
    except Exception:
        pass

    # ── TREND DEDUCTION ──────────────────────────────────────────────────────
    try:
        monthly = df.groupby('month')['amount'].sum()
        if len(monthly) >= 2:
            last = monthly.iloc[-1]
            prev = monthly.iloc[-2]
            if last > prev * 1.2:
                score -= 5
    except Exception:
        pass

    # ── FINAL SCORE ──────────────────────────────────────────────────────────
    score = max(0, min(100, score))

    if score >= 80:
        return score, "Excellent", "#10B981"
    elif score >= 60:
        return score, "Good", "#F59E0B"
    elif score >= 40:
        return score, "Fair", "#F97316"
    else:
        return score, "Poor", "#EF4444"
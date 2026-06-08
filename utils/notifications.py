import pandas as pd
from datetime import datetime

def generate_notifications(user_id, df_expenses, df_income=None):
    """
    Generate smart notifications based on user data.
    Saves them to DB and returns list for display.
    """
    from utils.db import add_notification, get_notifications_db

    notifications = []

    if df_expenses.empty:
        return notifications

    df = df_expenses.copy()
    df['date'] = pd.to_datetime(df['date'])
    current_month = datetime.now().strftime('%Y-%m')
    df['month'] = df['date'].dt.strftime('%Y-%m')
    df_this_month = df[df['month'] == current_month]

    # ── ANOMALY ALERT ─────────────────────────────────────────────────────────
    try:
        from utils.features import prepare_features
        from utils.predict import predict_anomalies, load_model
        model = load_model()
        if model is not None and len(df) >= 10:
            df_full, X = prepare_features(df)
            result = predict_anomalies(df_full, X)
            anomaly_count = int((result['anomaly'] == -1).sum())
            if anomaly_count > 0:
                worst = result[result['anomaly'] == -1].sort_values(
                    'anomaly_score'
                ).iloc[0]
                notifications.append({
                    "title": "Spending Anomaly Detected",
                    "message": f"{anomaly_count} unusual transaction"
                               f"{'s' if anomaly_count > 1 else ''} found. "
                               f"Largest: ₹{worst['amount']:,.0f} "
                               f"on {worst['category']}.",
                    "type": "danger",
                    "priority": "high",
                    "icon": ""
                })
    except Exception:
        pass

    # ── BUDGET ALERTS ─────────────────────────────────────────────────────────
    try:
        from utils.db import get_budgets
        budgets_df = get_budgets(user_id, current_month)
        if not budgets_df.empty and not df_this_month.empty:
            for _, budget in budgets_df.iterrows():
                cat = budget['category']
                limit = budget['monthly_limit']
                spent = df_this_month[
                    df_this_month['category'] == cat
                ]['amount'].sum()
                pct = (spent / limit * 100) if limit > 0 else 0

                if pct >= 100:
                    notifications.append({
                        "title": f"{cat} Budget Exceeded",
                        "message": f"You've spent ₹{spent:,.0f} of your "
                                   f"₹{limit:,.0f} {cat} budget "
                                   f"({pct:.0f}% used).",
                        "type": "danger",
                        "priority": "high",
                        "icon": ""
                    })
                elif pct >= 80:
                    notifications.append({
                        "title": f"{cat} Budget Warning",
                        "message": f"{pct:.0f}% of {cat} budget used. "
                                   f"Only ₹{limit - spent:,.0f} remaining.",
                        "type": "warning",
                        "priority": "medium",
                        "icon": ""
                    })
    except Exception:
        pass

    # ── HIGH SPENDING TODAY ───────────────────────────────────────────────────
    try:
        today = datetime.now().date()
        df_today = df[df['date'].dt.date == today]
        if not df_today.empty:
            daily_avg = df.groupby(
                df['date'].dt.date
            )['amount'].sum().mean()
            today_total = df_today['amount'].sum()
            if today_total > daily_avg * 2:
                notifications.append({
                    "title": "High Spending Day",
                    "message": f"Today's spending (₹{today_total:,.0f}) "
                               f"is {today_total/daily_avg:.1f}x your "
                               f"daily average (₹{daily_avg:,.0f}).",
                    "type": "warning",
                    "priority": "medium",
                    "icon": ""
                })
    except Exception:
        pass

    # ── SPENDING TREND ────────────────────────────────────────────────────────
    try:
        df['month_period'] = df['date'].dt.to_period('M')
        monthly = df.groupby('month_period')['amount'].sum()
        if len(monthly) >= 2:
            last = monthly.iloc[-1]
            prev = monthly.iloc[-2]
            pct_change = ((last - prev) / prev * 100) if prev > 0 else 0
            if pct_change > 20:
                notifications.append({
                    "title": "Spending Trend Alert",
                    "message": f"Monthly spending increased by "
                               f"{pct_change:.0f}% compared to last month.",
                    "type": "warning",
                    "priority": "medium",
                    "icon": ""
                })
    except Exception:
        pass

    # ── SAVINGS GOALS ─────────────────────────────────────────────────────────
    try:
        from utils.db import get_savings_goals
        goals = get_savings_goals(user_id)
        if not goals.empty:
            for _, goal in goals.iterrows():
                pct = (goal['current_amount'] /
                       goal['target_amount'] * 100) \
                    if goal['target_amount'] > 0 else 0
                if pct >= 100:
                    notifications.append({
                        "title": "Goal Achieved!",
                        "message": f"Congratulations! You reached your "
                                   f"'{goal['name']}' savings goal!",
                        "type": "success",
                        "priority": "high",
                        "icon": ""
                    })
                elif pct >= 75:
                    notifications.append({
                        "title": "Savings Goal Progress",
                        "message": f"'{goal['name']}' is {pct:.0f}% complete."
                                   f" Keep going!",
                        "type": "success",
                        "priority": "low",
                        "icon": ""
                    })
    except Exception:
        pass

    # ── ALL BUDGETS ON TRACK ──────────────────────────────────────────────────
    try:
        from utils.db import get_budgets
        budgets_df = get_budgets(user_id, current_month)
        if not budgets_df.empty and not df_this_month.empty:
            all_ok = all(
                (df_this_month[
                    df_this_month['category'] == b['category']
                ]['amount'].sum() / b['monthly_limit'] * 100) < 80
                for _, b in budgets_df.iterrows()
            )
            if all_ok:
                notifications.append({
                    "title": "Great Financial Discipline",
                    "message": "All budgets are on track this month. "
                               "Keep it up!",
                    "type": "success",
                    "priority": "low",
                    "icon": ""
                })
    except Exception:
        pass

    # ── NO INCOME RECORDED ────────────────────────────────────────────────────
    try:
        if df_income is not None and df_income.empty:
            notifications.append({
                "title": "Income Not Tracked",
                "message": "Add your income to see savings rate "
                           "and cash flow analysis.",
                "type": "info",
                "priority": "low",
                "icon": ""
            })
    except Exception:
        pass

    return notifications
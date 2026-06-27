from datetime import datetime
import pandas as pd
import sqlite3
import os
import json

DB_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'data', 'finance.db'
)

def get_connection():
    return sqlite3.connect(DB_PATH)

def save_health_score_history(user_id, month, score, breakdown):
    """
    Saves a monthly health score snapshot to the database.
    """
    conn = get_connection()
    try:
        conn.execute('''
            INSERT INTO health_score_history (
                user_id, month, score, savings_rate, expense_stability,
                emergency_fund, debt_to_income, budget_adherence, investment_readiness
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, month) DO UPDATE SET
                score = excluded.score,
                savings_rate = excluded.savings_rate,
                expense_stability = excluded.expense_stability,
                emergency_fund = excluded.emergency_fund,
                debt_to_income = excluded.debt_to_income,
                budget_adherence = excluded.budget_adherence,
                investment_readiness = excluded.investment_readiness
        ''', (
            user_id, month, float(score),
            float(breakdown['savings_rate']),
            float(breakdown['expense_stability']),
            float(breakdown['emergency_fund']),
            float(breakdown['debt_to_income']),
            float(breakdown['budget_adherence']),
            float(breakdown['investment_readiness'])
        ))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

def get_health_score_history(user_id):
    """
    Fetches the historical health score snapshots for a user.
    """
    conn = get_connection()
    df = pd.read_sql_query('''
        SELECT month, score, savings_rate, expense_stability,
               emergency_fund, debt_to_income, budget_adherence, investment_readiness
        FROM health_score_history
        WHERE user_id = ?
        ORDER BY month ASC
    ''', conn, params=(user_id,))
    conn.close()
    return df

def calculate_health_score(user_id=1):
    """
    Calculate financial health score (0-100) based on 6 core factors.
    Returns: (overall_score, label, color, breakdown_dict, strengths, improvements)
    """
    from utils.db import (
        get_all_expenses, get_all_income, get_budgets,
        get_expenses_by_month, get_income_by_month
    )
    from pages.networth import get_assets, get_liabilities

    current_month = datetime.now().strftime('%Y-%m')

    # Load Data
    expenses_df = get_all_expenses(user_id)
    income_df = get_all_income(user_id)
    assets_df = get_assets(user_id)
    liabilities_df = get_liabilities(user_id)

    # 1. Monthly totals
    this_month_expenses = expenses_df[expenses_df['date'].str.startswith(current_month)] if not expenses_df.empty else pd.DataFrame()
    this_month_income = income_df[income_df['date'].str.startswith(current_month)] if not income_df.empty else pd.DataFrame()

    total_exp = this_month_expenses['amount'].sum() if not this_month_expenses.empty else 0
    total_inc = this_month_income['amount'].sum() if not this_month_income.empty else 0

    # Fallback to general averages if current month is empty
    if total_inc == 0 and not income_df.empty:
        total_inc = income_df['amount'].mean()
    if total_exp == 0 and not expenses_df.empty:
        total_exp = expenses_df['amount'].mean()

    # ── FACTOR 1: Savings Rate (25%) ──
    # Target: >= 20% of income saved
    savings = max(0, total_inc - total_exp)
    savings_rate_val = (savings / total_inc) if total_inc > 0 else 0
    savings_rate_score = min(25.0, (savings_rate_val / 0.20) * 25.0) if savings_rate_val > 0 else 0.0

    # ── FACTOR 2: Expense Stability (15%) ──
    # Check volatility of monthly expenses
    expense_stability_score = 15.0
    if not expenses_df.empty:
        expenses_df = expenses_df.copy()
        expenses_df['date'] = pd.to_datetime(expenses_df['date'])
        expenses_df['month'] = expenses_df['date'].dt.strftime('%Y-%m')
        monthly_exp = expenses_df.groupby('month')['amount'].sum()
        if len(monthly_exp) >= 2:
            std_dev = monthly_exp.std()
            mean_exp = monthly_exp.mean()
            volatility = (std_dev / mean_exp) if mean_exp > 0 else 0
            if volatility < 0.15:
                expense_stability_score = 15.0
            elif volatility < 0.30:
                expense_stability_score = 10.0
            elif volatility < 0.50:
                expense_stability_score = 5.0
            else:
                expense_stability_score = 2.0

    # ── FACTOR 3: Emergency Fund Adequacy (20%) ──
    # Target: 6 months of expenses covered by cash/savings assets
    cash_assets = 0.0
    if not assets_df.empty:
        cash_df = assets_df[assets_df['category'] == 'Cash & Savings']
        if not cash_df.empty:
            cash_assets = pd.to_numeric(cash_df['value'], errors='coerce').sum()
    
    avg_exp = total_exp if total_exp > 0 else 30000.0  # default baseline
    if not expenses_df.empty:
        expenses_df = expenses_df.copy()
        expenses_df['date'] = pd.to_datetime(expenses_df['date'])
        expenses_df['month'] = expenses_df['date'].dt.strftime('%Y-%m')
        avg_exp = expenses_df.groupby('month')['amount'].sum().mean()
        if pd.isna(avg_exp) or avg_exp == 0:
            avg_exp = 30000.0

    months_covered = cash_assets / avg_exp if avg_exp > 0 else 0
    emergency_fund_score = min(20.0, (months_covered / 6.0) * 20.0)

    # ── FACTOR 4: Debt-to-Income Ratio (20%) ──
    # Target: Monthly debt repayments (estimated at 5% of total liabilities) <= 30% of income
    total_liab = 0.0
    if not liabilities_df.empty:
        total_liab = pd.to_numeric(liabilities_df['value'], errors='coerce').sum()
    
    est_monthly_debt = total_liab * 0.05
    dti = est_monthly_debt / total_inc if total_inc > 0 else (0.5 if total_liab > 0 else 0.0)
    
    if total_liab == 0:
        debt_to_income_score = 20.0
    elif dti <= 0.10:
        debt_to_income_score = 20.0
    elif dti <= 0.30:
        debt_to_income_score = 15.0
    elif dti <= 0.50:
        debt_to_income_score = 10.0
    elif dti <= 0.70:
        debt_to_income_score = 5.0
    else:
        debt_to_income_score = 0.0

    # ── FACTOR 5: Budget Adherence (10%) ──
    # Percentage of categories that remained under budget
    budgets_df = get_budgets(user_id, current_month)
    budget_adherence_score = 10.0
    if not budgets_df.empty:
        total_budgets = len(budgets_df)
        adhered = 0
        for _, budget in budgets_df.iterrows():
            cat = budget['category']
            limit = budget['monthly_limit']
            spent_df = this_month_expenses[this_month_expenses['category'] == cat] if not this_month_expenses.empty else pd.DataFrame()
            spent = spent_df['amount'].sum() if not spent_df.empty else 0
            if spent <= limit:
                adhered += 1
        budget_adherence_score = (adhered / total_budgets) * 10.0

    # ── FACTOR 6: Investment Readiness (10%) ──
    # Ready if Emergency Fund >= 3 months and Debt-to-Income < 30%
    investment_readiness_score = 0.0
    if months_covered >= 3.0:
        investment_readiness_score += 5.0
    if dti <= 0.30 or total_liab == 0:
        investment_readiness_score += 5.0

    # Sum Score
    overall_score = round(
        savings_rate_score + expense_stability_score +
        emergency_fund_score + debt_to_income_score +
        budget_adherence_score + investment_readiness_score
    )
    overall_score = max(0, min(100, overall_score))

    breakdown = {
        'savings_rate': round(savings_rate_score, 1),
        'expense_stability': round(expense_stability_score, 1),
        'emergency_fund': round(emergency_fund_score, 1),
        'debt_to_income': round(debt_to_income_score, 1),
        'budget_adherence': round(budget_adherence_score, 1),
        'investment_readiness': round(investment_readiness_score, 1)
    }

    # Strengths and Improvements
    strengths = []
    improvements = []

    if savings_rate_score >= 20:
        strengths.append("Strong savings rate (saving >= 16% of income)")
    elif savings_rate_score < 12:
        improvements.append("Savings rate is low; aim to save at least 20% of your income")

    if expense_stability_score >= 12:
        strengths.append("Stable and predictable month-over-month expenses")
    elif expense_stability_score < 8:
        improvements.append("High volatility in monthly spending; try to stabilize expenses")

    if emergency_fund_score >= 16:
        strengths.append("Excellent emergency fund buffer (>= 5 months of expenses covered)")
    elif emergency_fund_score < 10:
        improvements.append("Emergency fund is below target; aim for 3-6 months of expenses")

    if debt_to_income_score >= 16:
        strengths.append("Low debt burden relative to income")
    elif debt_to_income_score < 10:
        improvements.append("High debt burden; prioritize paying off credit cards or high-interest loans")

    if budget_adherence_score >= 8:
        strengths.append("High budget compliance across categories")
    elif budget_adherence_score < 6:
        improvements.append("Frequent budget overruns; review and adjust monthly category limits")

    if investment_readiness_score >= 8:
        strengths.append("Ready to invest (adequate buffer and manageable debt)")
    elif investment_readiness_score < 5:
        improvements.append("Build emergency buffer and reduce debt before starting investments")

    # Labels and Colors
    if overall_score >= 80:
        label = "Excellent"
        color = "#10B981"
    elif overall_score >= 60:
        label = "Good"
        color = "#3B82F6"
    elif overall_score >= 40:
        label = "Fair"
        color = "#F59E0B"
    else:
        label = "Poor"
        color = "#EF4444"

    # Save to history automatically
    save_health_score_history(user_id, current_month, overall_score, breakdown)

    return overall_score, label, color, breakdown, strengths, improvements
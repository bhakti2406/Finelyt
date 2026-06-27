from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def linear_fit(x, y):
    n = len(x)
    if n == 0:
        return 0, 0
    if n == 1:
        return 0, y[0]
    
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xx = sum(val * val for val in x)
    sum_xy = sum(x[i] * y[i] for i in range(n))
    
    denominator = (n * sum_xx - sum_x * sum_x)
    if denominator == 0:
        return 0, sum_y / n
    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n
    return slope, intercept

def forecast_cash_flow(user_id=1):
    """
    Predicts next 1, 3, and 6 months of income, expenses, and savings.
    Returns: (history_df, forecast_df)
    """
    from utils.db import get_all_expenses, get_all_income
    
    expenses_df = get_all_expenses(user_id)
    income_df = get_all_income(user_id)
    
    # Process history
    if expenses_df.empty:
        expenses_df = pd.DataFrame(columns=['date', 'amount'])
    else:
        expenses_df = expenses_df.copy()
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
        
    if income_df.empty:
        income_df = pd.DataFrame(columns=['date', 'amount'])
    else:
        income_df = income_df.copy()
    income_df['date'] = pd.to_datetime(income_df['date'])
        
    # Group by month
    expenses_df['month'] = expenses_df['date'].dt.to_period('M')
    income_df['month'] = income_df['date'].dt.to_period('M')
    
    monthly_exp = expenses_df.groupby('month')['amount'].sum().reset_index()
    monthly_inc = income_df.groupby('month')['amount'].sum().reset_index()
    
    # Merge history
    history = pd.merge(monthly_inc, monthly_exp, on='month', how='outer', suffixes=('_inc', '_exp')).fillna(0)
    history['month_str'] = history['month'].astype(str)
    history = history.sort_values('month_str').reset_index(drop=True)
    history['savings'] = history['amount_inc'] - history['amount_exp']
    
    # Projections
    n_history = len(history)
    forecast_months = [1, 3, 6]
    forecast_records = []
    
    # Current month/date
    now = datetime.now()
    
    if n_history < 2:
        # Fallback to simple average or default values
        avg_inc = history['amount_inc'].mean() if n_history > 0 else 50000.0
        avg_exp = history['amount_exp'].mean() if n_history > 0 else 30000.0
        
        for m in [1, 2, 3, 4, 5, 6]:
            target_date = now + timedelta(days=30 * m)
            month_str = target_date.strftime('%Y-%m')
            
            # Add minor seasonal noise
            seasonal_noise_inc = 1.0 + (0.05 if target_date.month in [10, 12, 3] else 0.0)
            seasonal_noise_exp = 1.0 + (0.1 if target_date.month in [10, 12, 5] else -0.05)
            
            p_inc = avg_inc * seasonal_noise_inc
            p_exp = avg_exp * seasonal_noise_exp
            
            forecast_records.append({
                'month_str': month_str,
                'predicted_income': round(p_inc, 2),
                'predicted_expenses': round(p_exp, 2),
                'predicted_savings': round(p_inc - p_exp, 2)
            })
    else:
        # Use linear regression trends
        x_vals = list(range(n_history))
        inc_y = history['amount_inc'].tolist()
        exp_y = history['amount_exp'].tolist()
        
        slope_inc, int_inc = linear_fit(x_vals, inc_y)
        slope_exp, int_exp = linear_fit(x_vals, exp_y)
        
        for m in [1, 2, 3, 4, 5, 6]:
            target_date = now + timedelta(days=30 * m)
            month_str = target_date.strftime('%Y-%m')
            
            # Predict
            pred_idx = n_history + m - 1
            p_inc = max(0.0, slope_inc * pred_idx + int_inc)
            p_exp = max(0.0, slope_exp * pred_idx + int_exp)
            
            # Add minor seasonal noise (festival months, vacation seasons)
            if target_date.month in [10, 12]:  # Oct, Dec
                p_inc *= 1.05
                p_exp *= 1.15
            elif target_date.month in [5, 6]:  # Summer
                p_exp *= 1.08
                
            forecast_records.append({
                'month_str': month_str,
                'predicted_income': round(p_inc, 2),
                'predicted_expenses': round(p_exp, 2),
                'predicted_savings': round(p_inc - p_exp, 2)
            })
            
    forecast_df = pd.DataFrame(forecast_records)
    return history, forecast_df

def analyze_goal_feasibility(goal_id, user_id=1):
    """
    Evaluates the probability and time requirements to achieve a savings goal.
    """
    from utils.db import get_savings_goals, get_all_expenses, get_all_income
    
    goals = get_savings_goals(user_id)
    if goals.empty:
        return None
        
    goal_row = goals[goals['id'] == goal_id]
    if goal_row.empty:
        return None
        
    goal = goal_row.iloc[0]
    target_amount = float(goal['target_amount'])
    current_amount = float(goal['current_amount'])
    remaining = max(0.0, target_amount - current_amount)
    
    target_date_str = goal['target_date']
    if not target_date_str:
        target_date = datetime.now() + timedelta(days=365)
    else:
        try:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
        except ValueError:
            target_date = datetime.now() + timedelta(days=365)
            
    now = datetime.now()
    days_left = (target_date - now).days
    months_left = max(0.1, days_left / 30.4)
    
    # Calculate historical monthly savings velocity (last 6 months)
    expenses = get_all_expenses(user_id)
    income = get_all_income(user_id)
    
    avg_monthly_savings = 5000.0  # default baseline velocity
    if not expenses.empty or not income.empty:
        exp_amt = expenses['amount'].sum() if not expenses.empty else 0
        inc_amt = income['amount'].sum() if not income.empty else 0
        
        # calculate history spans
        all_dates = []
        if not expenses.empty:
            all_dates += pd.to_datetime(expenses['date']).tolist()
        if not income.empty:
            all_dates += pd.to_datetime(income['date']).tolist()
            
        if all_dates:
            min_date = min(all_dates)
            span_days = max(30, (now - min_date).days)
            span_months = span_days / 30.4
            net_savings = max(0.0, inc_amt - exp_amt)
            avg_monthly_savings = max(1000.0, net_savings / span_months)
            
    if remaining == 0:
        return {
            'probability': 100.0,
            'completion_date': now.strftime('%d %b %Y'),
            'required_monthly_savings': 0.0,
            'current_velocity': avg_monthly_savings,
            'remaining_amount': 0.0,
            'months_needed': 0.0
        }
        
    required_monthly = remaining / months_left
    velocity_ratio = avg_monthly_savings / required_monthly if required_monthly > 0 else 1.0
    probability = max(0.0, min(100.0, velocity_ratio * 100.0))
    
    months_needed = remaining / avg_monthly_savings if avg_monthly_savings > 0 else 999.0
    completion_date = now + timedelta(days=int(months_needed * 30.4))
    
    return {
        'probability': round(probability, 1),
        'completion_date': completion_date.strftime('%d %b %Y'),
        'required_monthly_savings': round(required_monthly, 2),
        'current_velocity': round(avg_monthly_savings, 2),
        'remaining_amount': round(remaining, 2),
        'months_needed': round(months_needed, 1)
    }

def model_retirement_planning(current_age, retirement_age, current_savings,
                              expected_return, expected_inflation, post_retirement_expense):
    """
    Retirement calculator with inflation-adjusted targets.
    - expected_return, expected_inflation: as percentages (e.g. 10.0 for 10%)
    - post_retirement_expense: today's monthly expense target during retirement
    """
    years_to_retire = max(0, retirement_age - current_age)
    if years_to_retire == 0:
        return {
            'target_corpus': 0.0,
            'future_value_savings': current_savings,
            'shortfall': 0.0,
            'required_monthly_contribution': 0.0,
            'corpus_at_retirement': current_savings
        }
        
    # 1. Calculate inflation adjusted retirement expenses
    inf_rate = expected_inflation / 100.0
    inflation_multiplier = (1.0 + inf_rate) ** years_to_retire
    future_monthly_expense = post_retirement_expense * inflation_multiplier
    
    # 2. Calculate corpus required at retirement
    # Target post-retirement life span: 30 years
    # Real rate of return post retirement (assuming conservative returns e.g. return - inflation)
    real_rate_post = ((1.0 + expected_return/100.0) / (1.0 + inf_rate)) - 1.0
    if real_rate_post == 0:
        real_rate_post = 0.02  # fallback baseline
        
    # Present Value of 30-year annuity of future_monthly_expense
    r_monthly = real_rate_post / 12.0
    n_months_post = 30 * 12
    # PV = PMT * [1 - (1+r)^-n] / r
    target_corpus = (future_monthly_expense * 12) * (1 - (1 + real_rate_post) ** -30) / real_rate_post
    
    # 3. Calculate future value of current savings
    r_rate = expected_return / 100.0
    future_value_savings = current_savings * ((1.0 + r_rate) ** years_to_retire)
    
    # 4. Shortfall and monthly contribution required
    shortfall = max(0.0, target_corpus - future_value_savings)
    
    # PMT = FV * r / [(1+r)^n - 1]
    r_monthly_pre = r_rate / 12.0
    n_months_pre = years_to_retire * 12
    
    if shortfall > 0 and r_monthly_pre > 0:
        required_monthly = shortfall * r_monthly_pre / (((1.0 + r_monthly_pre) ** n_months_pre) - 1)
    else:
        required_monthly = 0.0
        
    return {
        'target_corpus': round(target_corpus, 2),
        'future_value_savings': round(future_value_savings, 2),
        'shortfall': round(shortfall, 2),
        'required_monthly_contribution': round(required_monthly, 2),
        'corpus_at_retirement': round(future_value_savings, 2)
    }

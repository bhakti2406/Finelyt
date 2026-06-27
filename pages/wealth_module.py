import streamlit as st
import pandas as pd
import plotly.express as px
from utils.currency import format_amount, get_symbol
from utils.health_score import calculate_health_score
from utils.db import get_all_expenses, get_all_income
from pages.networth import get_assets, get_liabilities

def show(user_id=1):
    currency = st.session_state.get('currency', 'INR')
    sym = get_symbol(currency)
    
    st.markdown("""
    <style>
    .page-title { font-size: 2rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0; }
    .page-sub { font-size: 1rem; color: var(--text-secondary); margin-bottom: 1.5rem; }
    .wealth-val { font-size: 3.5rem; font-weight: 900; line-height: 1; margin: 0.5rem 0; }
    .wealth-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-surface) 100%);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .milestone-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; border-bottom: 1px solid var(--border); }
    .milestone-achieved { color: #10B981; font-weight: 700; }
    .milestone-pending { color: var(--text-muted); }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="page-title">Wealth Building Module</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Evaluate your investment readiness, review personalized asset allocation suggestions, and track your long-term wealth milestones.</p>', unsafe_allow_html=True)
    st.divider()
    
    # Investment Readiness calculations
    assets_df = get_assets(user_id)
    liabilities_df = get_liabilities(user_id)
    expenses_df = get_all_expenses(user_id)
    income_df = get_all_income(user_id)
    
    cash_assets = 0.0
    if not assets_df.empty:
        cash_df = assets_df[assets_df['category'] == 'Cash & Savings']
        if not cash_df.empty:
            cash_assets = pd.to_numeric(cash_df['value'], errors='coerce').sum()
            
    total_assets = pd.to_numeric(assets_df['value'], errors='coerce').sum() if not assets_df.empty else 0.0
    total_liab = pd.to_numeric(liabilities_df['value'], errors='coerce').sum() if not liabilities_df.empty else 0.0
    net_worth = max(0.0, total_assets - total_liab)
    
    avg_exp = 30000.0
    if not expenses_df.empty:
        expenses_df = expenses_df.copy()
        expenses_df['date'] = pd.to_datetime(expenses_df['date'])
        expenses_df['month'] = expenses_df['date'].dt.strftime('%Y-%m')
        avg_exp = expenses_df.groupby('month')['amount'].sum().mean()
        if pd.isna(avg_exp) or avg_exp == 0:
            avg_exp = 30000.0
            
    months_covered = cash_assets / avg_exp if avg_exp > 0 else 0.0
    
    # Calculate Readiness Score (0-100)
    # 1. Emergency Buffer status (up to 40 points): full points if >= 3 months
    buffer_points = min(40.0, (months_covered / 3.0) * 40.0)
    # 2. Debt status (up to 40 points): full points if total liabilities == 0
    debt_points = 40.0 if total_liab == 0 else max(0.0, 40.0 - (total_liab / max(1.0, total_assets)) * 40.0)
    # 3. Monthly savings velocity (up to 20 points): full points if saving > 10,000 / month
    avg_inc = income_df['amount'].mean() if not income_df.empty else 0.0
    surplus = max(0.0, avg_inc - avg_exp)
    surplus_points = min(20.0, (surplus / 10000.0) * 20.0)
    
    readiness_score = round(buffer_points + debt_points + surplus_points)
    
    col_score, col_details = st.columns([1.2, 1.8])
    
    with col_score:
        if readiness_score >= 80:
            status_lbl = "INVESTMENT READY"
            status_color = "#10B981"
            status_desc = "Excellent position. You have healthy cash buffers and manageable debt."
        elif readiness_score >= 50:
            status_lbl = "PARTIALLY READY"
            status_color = "#F59E0B"
            status_desc = "Good start, but build a stronger cash buffer or pay down debt before aggressive investing."
        else:
            status_lbl = "NOT READY"
            status_color = "#EF4444"
            status_desc = "Prioritize building an emergency fund of 3-6 months and paying down outstanding liabilities."
            
        st.markdown(f"""
        <div class="wealth-card">
            <div style="color:var(--text-muted); font-size:.9rem; text-transform:uppercase; letter-spacing:.1em">
                Investment Readiness Score
            </div>
            <div class="wealth-val" style="color:{status_color}">
                {readiness_score}/100
            </div>
            <div style="color:{status_color}; font-weight:700; font-size:1.15rem; margin-top:0.4rem;">
                {status_lbl}
            </div>
            <p style="color:var(--text-secondary); font-size:0.83rem; margin-top:0.8rem; line-height:1.4;">
                {status_desc}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_details:
        st.markdown("<p style='font-weight:700; font-size:1.1rem; color:var(--text-primary); margin-bottom:1rem;'>Asset Allocation Suggestions</p>", unsafe_allow_html=True)
        
        risk_profile = st.selectbox("Select Your Risk Appetite Profile:", ["Conservative", "Moderate", "Aggressive"])
        
        # Educational Allocation Suggestion mapping
        if risk_profile == "Aggressive":
            alloc_data = pd.DataFrame({
                'Asset Class': ['Equity / Stock Mutual Funds', 'Fixed Income / Debt Funds', 'Gold & Jewelry / Precious Metals', 'Cash & Liquid Savings'],
                'Allocation %': [60, 20, 10, 10]
            })
        elif risk_profile == "Moderate":
            alloc_data = pd.DataFrame({
                'Asset Class': ['Equity / Stock Mutual Funds', 'Fixed Income / Debt Funds', 'Gold & Jewelry / Precious Metals', 'Cash & Liquid Savings'],
                'Allocation %': [40, 40, 10, 10]
            })
        else:
            alloc_data = pd.DataFrame({
                'Asset Class': ['Equity / Stock Mutual Funds', 'Fixed Income / Debt Funds', 'Gold & Jewelry / Precious Metals', 'Cash & Liquid Savings'],
                'Allocation %': [20, 60, 10, 10]
            })
            
        fig_alloc = px.pie(
            alloc_data, values='Allocation %', names='Asset Class',
            color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#06B6D4'],
            hole=0.4
        )
        fig_alloc.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#F8FAFC', showlegend=True,
            legend=dict(font=dict(color='#94A3B8'), bgcolor='rgba(0,0,0,0)'),
            margin=dict(t=10, b=10, l=10, r=10),
            height=250
        )
        st.plotly_chart(fig_alloc, use_container_width=True)
        
    st.divider()
    
    # Wealth milestones
    st.markdown("<p style='font-weight:700; font-size:1.1rem; color:var(--text-primary); margin-bottom:1rem;'>Wealth Milestone Roadmap Tracker</p>", unsafe_allow_html=True)
    
    milestones = [
        ("Base Level (First positive Net Worth)", 0),
        ("Kickstarter Milestone", 10000),
        ("Emergency Buffer Complete (10k)", 50000),
        ("Six Figure Wealth Goal", 100000),
        ("Quarter Million Milestone", 250000),
        ("Half Million Milestone", 500000),
        ("One Million Financial Freedom Goal", 1000000)
    ]
    
    for label, val in milestones:
        is_achieved = net_worth >= val
        achieved_txt = "ACHIEVED" if is_achieved else f"PENDING ({format_amount(val - net_worth, currency)} left)"
        achieved_class = "milestone-achieved" if is_achieved else "milestone-pending"
        check_icon = "✓" if is_achieved else "✕"
        check_color = "#10B981" if is_achieved else "#EF4444"
        
        st.markdown(f"""
        <div class="milestone-row">
            <div>
                <span style="color:{check_color}; font-weight:700; margin-right:8px;">{check_icon}</span>
                <span style="color:var(--text-primary); font-weight:600;">{label}</span>
            </div>
            <div class="{achieved_class}">
                {achieved_txt}
            </div>
        </div>
        """, unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.currency import format_amount, get_symbol
from utils.health_score import calculate_health_score
from utils.db import get_all_expenses, get_all_income, get_budgets
from pages.networth import get_assets, get_liabilities
from datetime import datetime

def show(user_id=1):
    currency = st.session_state.get('currency', 'INR')
    sym = get_symbol(currency)
    
    st.markdown("""
    <style>
    .page-title { font-size: 2rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0; }
    .page-sub { font-size: 1rem; color: var(--text-secondary); margin-bottom: 1.5rem; }
    .risk-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .risk-badge {
        font-weight: 700;
        font-size: 0.8rem;
        padding: 3px 10px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
    }
    .risk-low { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #10B981; }
    .risk-med { background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); color: #F59E0B; }
    .risk-high { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: #EF4444; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="page-title">Financial Risk Engine</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Understand your vulnerability across liquidity, debt, budget breaches, and saving habits.</p>', unsafe_allow_html=True)
    st.divider()
    
    # Gather database details
    expenses_df = get_all_expenses(user_id)
    income_df = get_all_income(user_id)
    assets_df = get_assets(user_id)
    liabilities_df = get_liabilities(user_id)
    current_month = datetime.now().strftime('%Y-%m')
    
    # Calculate statistics
    total_inc = income_df['amount'].sum() if not income_df.empty else 0
    total_exp = expenses_df['amount'].sum() if not expenses_df.empty else 0
    
    # averages
    avg_exp = 30000.0
    if not expenses_df.empty:
        expenses_df = expenses_df.copy()
        expenses_df['date'] = pd.to_datetime(expenses_df['date'])
        expenses_df['month'] = expenses_df['date'].dt.strftime('%Y-%m')
        avg_exp = expenses_df.groupby('month')['amount'].sum().mean()
        if pd.isna(avg_exp) or avg_exp == 0:
            avg_exp = 30000.0
            
    avg_inc = 50000.0
    if not income_df.empty:
        income_df = income_df.copy()
        income_df['date'] = pd.to_datetime(income_df['date'])
        income_df['month'] = income_df['date'].dt.strftime('%Y-%m')
        avg_inc = income_df.groupby('month')['amount'].sum().mean()
        if pd.isna(avg_inc) or avg_inc == 0:
            avg_inc = 50000.0
            
    # Assets and liabilities
    cash_assets = 0.0
    if not assets_df.empty:
        cash_df = assets_df[assets_df['category'] == 'Cash & Savings']
        if not cash_df.empty:
            cash_assets = pd.to_numeric(cash_df['value'], errors='coerce').sum()
            
    total_liab = 0.0
    if not liabilities_df.empty:
        total_liab = pd.to_numeric(liabilities_df['value'], errors='coerce').sum()
        
    # ── 1. LIQUIDITY RISK ──
    months_covered = cash_assets / avg_exp if avg_exp > 0 else 0
    if months_covered >= 6.0:
        liq_risk = "LOW"
        liq_class = "risk-low"
        liq_desc = "Excellent liquidity buffer. You can comfortably survive over 6 months without income."
        liq_rec = "Keep maintaining this reserve. Any excess cash can be directed to long-term wealth investments."
    elif months_covered >= 3.0:
        liq_risk = "MEDIUM"
        liq_class = "risk-med"
        liq_desc = f"Moderate liquidity buffer. You have {months_covered:.1f} months of expenses covered."
        liq_rec = "Aim to set aside a portion of monthly savings to build this buffer up to a full 6 months."
    else:
        liq_risk = "HIGH"
        liq_class = "risk-high"
        liq_desc = f"Vulnerable liquidity buffer. You only have {months_covered:.1f} months of expenses covered."
        liq_rec = "Prioritize building an emergency fund. Pause aggressive debt prepayments or investments temporarily."
        
    # ── 2. DEBT RISK ──
    est_monthly_debt = total_liab * 0.05
    dti = est_monthly_debt / avg_inc if avg_inc > 0 else (0.5 if total_liab > 0 else 0.0)
    
    if total_liab == 0:
        debt_risk = "LOW"
        debt_class = "risk-low"
        debt_desc = "Zero debt outstanding. You have absolute freedom from debt repayment stress."
        debt_rec = "Maintain this status. Avoid taking unnecessary high-interest consumer debt."
    elif dti < 0.30:
        debt_risk = "LOW"
        debt_class = "risk-low"
        debt_desc = f"Comfortable debt levels. Estimated monthly payments take {dti*100:.1f}% of average income."
        debt_rec = "Prepay any high-interest debt first. Keep credit card utilization below 30%."
    elif dti <= 0.50:
        debt_risk = "MEDIUM"
        debt_class = "risk-med"
        debt_desc = f"Moderate debt burden. Estimated monthly repayments consume {dti*100:.1f}% of income."
        debt_rec = "Avoid taking on any new loans. Build a plan to consolidate or accelerate debt payoff."
    else:
        debt_risk = "HIGH"
        debt_class = "risk-high"
        debt_desc = f"High debt burden. Estimated monthly repayments consume {dti*100:.1f}% of income."
        debt_rec = "Take active steps to restructure or pay down high-interest liabilities. Avoid further credit use."
        
    # ── 3. OVERSPENDING RISK ──
    budgets_df = get_budgets(user_id, current_month)
    overspending_risk = "LOW"
    overspending_desc = "No categories are currently near budget limits."
    overspending_rec = "Keep tracking and log every expense to ensure you stay inside your targets."
    
    if not budgets_df.empty:
        breached_or_near = 0
        total_b = len(budgets_df)
        for _, budget in budgets_df.iterrows():
            cat = budget['category']
            limit = budget['monthly_limit']
            this_month_spent = expenses_df[(expenses_df['month'] == current_month) & (expenses_df['category'] == cat)]['amount'].sum() if not expenses_df.empty else 0
            if limit > 0 and (this_month_spent / limit) >= 0.8:
                breached_or_near += 1
                
        ratio = breached_or_near / total_b
        if ratio >= 0.5:
            overspending_risk = "HIGH"
            overspending_desc = f"High risk of overspending. {breached_or_near} out of {total_b} budget categories are above 80% limit."
            overspending_rec = "Lock down discretionary wants spending for the remainder of the month. Review limits."
        elif ratio > 0.0:
            overspending_risk = "MEDIUM"
            overspending_desc = f"Moderate risk. {breached_or_near} out of {total_b} budget categories are approaching limits."
            overspending_rec = "Slow down shopping/dining spending. Switch to essentials-only for a few days."
            
    overspending_class = "risk-high" if overspending_risk == "HIGH" else "risk-med" if overspending_risk == "MEDIUM" else "risk-low"
    
    # ── 4. SAVINGS RISK ──
    savings_rate = (avg_inc - avg_exp) / avg_inc if avg_inc > 0 else 0.0
    if savings_rate >= 0.20:
        savings_risk = "LOW"
        savings_class = "risk-low"
        savings_desc = f"Healthy savings rate. You save {savings_rate*100:.1f}% of your monthly income."
        savings_rec = "Automate your investment contributions so this surplus is put to work immediately."
    elif savings_rate >= 0.10:
        savings_risk = "MEDIUM"
        savings_class = "risk-med"
        savings_desc = f"Moderate savings rate. You save {savings_rate*100:.1f}% of your monthly income."
        savings_rec = "Audit your discretionary categories (dining, wants) to find extra margin to reach 20%."
    else:
        savings_risk = "HIGH"
        savings_class = "risk-high"
        savings_desc = f"Vulnerable savings behavior. You save {savings_rate*100:.1f}% of your monthly income."
        savings_rec = "Audit expenses immediately. Track every single transaction and establish a firm savings goal."

    # Render UI
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown(f"""
        <div class="risk-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <span style="font-weight:700; color:var(--text-primary); font-size:1.1rem;">Liquidity Risk</span>
                <span class="risk-badge {liq_class}">{liq_risk} RISK</span>
            </div>
            <p style="font-size:0.9rem; color:var(--text-secondary); line-height:1.5; margin-bottom:1rem;">{liq_desc}</p>
            <div style="background:var(--bg-elevated); border-radius:8px; padding:0.6rem 0.8rem; font-size:0.82rem; border-left:3px solid var(--accent);">
                <strong style="color:var(--text-primary);">Actionable Tip:</strong><br>
                <span style="color:var(--text-muted);">{liq_rec}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="risk-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <span style="font-weight:700; color:var(--text-primary); font-size:1.1rem;">Overspending Risk</span>
                <span class="risk-badge {overspending_class}">{overspending_risk} RISK</span>
            </div>
            <p style="font-size:0.9rem; color:var(--text-secondary); line-height:1.5; margin-bottom:1rem;">{overspending_desc}</p>
            <div style="background:var(--bg-elevated); border-radius:8px; padding:0.6rem 0.8rem; font-size:0.82rem; border-left:3px solid var(--accent);">
                <strong style="color:var(--text-primary);">Actionable Tip:</strong><br>
                <span style="color:var(--text-muted);">{overspending_rec}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="risk-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <span style="font-weight:700; color:var(--text-primary); font-size:1.1rem;">Debt Burden Risk</span>
                <span class="risk-badge {debt_class}">{debt_risk} RISK</span>
            </div>
            <p style="font-size:0.9rem; color:var(--text-secondary); line-height:1.5; margin-bottom:1rem;">{debt_desc}</p>
            <div style="background:var(--bg-elevated); border-radius:8px; padding:0.6rem 0.8rem; font-size:0.82rem; border-left:3px solid var(--accent);">
                <strong style="color:var(--text-primary);">Actionable Tip:</strong><br>
                <span style="color:var(--text-muted);">{debt_rec}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="risk-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <span style="font-weight:700; color:var(--text-primary); font-size:1.1rem;">Savings Risk</span>
                <span class="risk-badge {savings_class}">{savings_risk} RISK</span>
            </div>
            <p style="font-size:0.9rem; color:var(--text-secondary); line-height:1.5; margin-bottom:1rem;">{savings_desc}</p>
            <div style="background:var(--bg-elevated); border-radius:8px; padding:0.6rem 0.8rem; font-size:0.82rem; border-left:3px solid var(--accent);">
                <strong style="color:var(--text-primary);">Actionable Tip:</strong><br>
                <span style="color:var(--text-muted);">{savings_rec}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Aggregate Risk Chart
    st.divider()
    st.markdown("<p style='font-weight:700; font-size:1.1rem; color:var(--text-primary); margin-bottom:1rem;'>Risk Factor Distribution Map</p>", unsafe_allow_html=True)
    
    # Pie chart showing risk levels
    risk_summary = pd.DataFrame({
        'Risk Category': ['Liquidity Risk', 'Debt Risk', 'Overspending Risk', 'Savings Risk'],
        'Level': [liq_risk, debt_risk, overspending_risk, savings_risk]
    })
    
    fig = px.bar(
        risk_summary, x='Risk Category', y='Level',
        color='Level',
        color_discrete_map={'LOW': '#10B981', 'MEDIUM': '#F59E0B', 'HIGH': '#EF4444'},
        title="Active Risk Vectors Matrix"
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#F8FAFC',
        xaxis=dict(gridcolor='#1E293B', color='#94A3B8', title=""),
        yaxis=dict(gridcolor='#1E293B', color='#94A3B8', title="Risk Exposure Level", categoryarray=['LOW', 'MEDIUM', 'HIGH'], type='category'),
        margin=dict(t=40, b=20, l=20, r=20),
        legend=dict(font=dict(color='#94A3B8'), bgcolor='rgba(0,0,0,0)')
    )
    st.plotly_chart(fig, use_container_width=True)

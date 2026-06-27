import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import importlib
import utils.health_score
importlib.reload(utils.health_score)
from utils.health_score import calculate_health_score, get_health_score_history
from utils.currency import format_amount, get_symbol
from datetime import datetime

def show(user_id=1):
    currency = st.session_state.get('currency', 'INR')
    sym = get_symbol(currency)
    
    st.markdown("""
    <style>
    .page-title { font-size: 2rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0; }
    .page-sub { font-size: 1rem; color: var(--text-secondary); margin-bottom: 1.5rem; }
    .health-val { font-size: 4rem; font-weight: 900; line-height: 1; margin: 0.5rem 0; }
    .health-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-surface) 100%);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .check-item { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 0.92rem; }
    .check-icon { font-weight: bold; font-size: 1.1rem; }
    .factor-bar-container { margin-bottom: 1rem; }
    .factor-label-row { display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 4px; }
    .framework-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="page-title">Financial Health & Frameworks</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Understand your scoring, historical trends, and alignment with globally recognized frameworks.</p>', unsafe_allow_html=True)
    st.divider()
    
    # Calculate Score
    score, label, color, breakdown, strengths, improvements = calculate_health_score(user_id)
    
    col_score, col_details = st.columns([1.2, 1.8])
    
    with col_score:
        st.markdown(f"""
        <div class="health-card">
            <div style="color:var(--text-muted); font-size:.9rem; text-transform:uppercase; letter-spacing:.1em">
                Financial Health Score
            </div>
            <div class="health-val" style="color:{color}">
                {score}/100
            </div>
            <div style="color:{color}; font-weight:700; font-size:1.2rem">
                {label}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display Strengths
        if strengths:
            st.markdown("<p style='font-weight:700; color:var(--text-primary); margin-bottom:0.5rem;'>Strengths</p>", unsafe_allow_html=True)
            for strength in strengths:
                st.markdown(f"""
                <div class="check-item">
                    <span class="check-icon" style="color:#10B981">✓</span>
                    <span style="color:var(--text-secondary)">{strength}</span>
                </div>
                """, unsafe_allow_html=True)
                
        # Display Improvements
        if improvements:
            st.markdown("<p style='font-weight:700; color:var(--text-primary); margin-top:1rem; margin-bottom:0.5rem;'>Areas to Improve</p>", unsafe_allow_html=True)
            for imp in improvements:
                st.markdown(f"""
                <div class="check-item">
                    <span class="check-icon" style="color:#F59E0B">⚠</span>
                    <span style="color:var(--text-secondary)">{imp}</span>
                </div>
                """, unsafe_allow_html=True)
                
    with col_details:
        st.markdown("<p style='font-weight:700; font-size:1.1rem; color:var(--text-primary); margin-bottom:1rem;'>Score Breakdown</p>", unsafe_allow_html=True)
        
        factors = [
            ("Savings Rate", breakdown['savings_rate'], 25.0, "var(--accent)"),
            ("Expense Stability", breakdown['expense_stability'], 15.0, "#3B82F6"),
            ("Emergency Fund Adequacy", breakdown['emergency_fund'], 20.0, "#8B5CF6"),
            ("Debt-to-Income Ratio", breakdown['debt_to_income'], 20.0, "#06B6D4"),
            ("Budget Adherence", breakdown['budget_adherence'], 10.0, "#F59E0B"),
            ("Investment Readiness", breakdown['investment_readiness'], 10.0, "#10B981")
        ]
        
        for name, current, max_val, bar_color in factors:
            pct = (current / max_val)
            st.markdown(f"""
            <div class="factor-bar-container">
                <div class="factor-label-row">
                    <span style="font-weight:600; color:var(--text-primary);">{name}</span>
                    <span>{current:.1f} / {max_val:.1f} points</span>
                </div>
                <div style="background:var(--bg-elevated); border-radius:999px; height:8px;">
                    <div style="background:{bar_color}; width:{pct*100:.1f}%; height:8px; border-radius:999px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    st.divider()
    
    # ── TABBED DETAILS: HISTORICAL TREND & FRAMEWORKS ─────────────────────────
    tab_trend, tab_503020, tab_emergency, tab_fire = st.tabs([
        "Score Trend History", "50-30-20 Rule", "Emergency Fund Tracker", "FIRE Framework"
    ])
    
    # 1. SCORE TREND HISTORY
    with tab_trend:
        st.markdown("<p style='font-weight:700; font-size:1.1rem; color:var(--text-primary); margin-bottom:0.5rem;'>Health Score over Time</p>", unsafe_allow_html=True)
        history_df = get_health_score_history(user_id)
        
        if history_df.empty:
            st.info("No historical logs recorded yet. Scores will be recorded monthly.")
        else:
            fig = px.line(
                history_df, x='month', y='score',
                markers=True, text='score',
                title="Historical Score Progression"
            )
            fig.update_traces(line_color="#00D4AA", textposition="top center")
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#F8FAFC',
                title_font_color='#F8FAFC',
                xaxis=dict(gridcolor='#1E293B', color='#94A3B8', title="Month"),
                yaxis=dict(gridcolor='#1E293B', color='#94A3B8', title="Score", range=[0, 105]),
                margin=dict(t=40, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)
            
    # 2. 50-30-20 RULE
    with tab_503020:
        st.markdown("<p style='font-weight:700; font-size:1.1rem; color:var(--text-primary); margin-bottom:0.5rem;'>50-30-20 Framework Integration</p>", unsafe_allow_html=True)
        
        from utils.db import get_all_expenses, get_all_income
        expenses_df = get_all_expenses(user_id)
        income_df = get_all_income(user_id)
        
        needs_cats = ["Bills", "Rent", "Utilities", "Insurance", "Healthcare", "Groceries"]
        wants_cats = ["Dining", "Shopping", "Entertainment", "Travel", "Subscriptions"]
        
        total_inc = income_df['amount'].sum() if not income_df.empty else 0
        
        if total_inc == 0:
            total_inc = 50000.0  # baseline default
            
        needs_spent = expenses_df[expenses_df['category'].isin(needs_cats)]['amount'].sum() if not expenses_df.empty else 0
        wants_spent = expenses_df[expenses_df['category'].isin(wants_cats)]['amount'].sum() if not expenses_df.empty else 0
        
        other_spent = expenses_df[~expenses_df['category'].isin(needs_cats + wants_cats)]['amount'].sum() if not expenses_df.empty else 0
        savings_invest = max(0, total_inc - (needs_spent + wants_spent + other_spent))
        
        # Percentages
        total_pie = needs_spent + wants_spent + savings_invest
        if total_pie > 0:
            needs_pct = (needs_spent / total_inc) * 100
            wants_pct = (wants_spent / total_inc) * 100
            savings_pct = (savings_invest / total_inc) * 100
        else:
            needs_pct, wants_pct, savings_pct = 0, 0, 0
            
        c1, c2 = st.columns(2)
        with c1:
            # Gauge compliance
            st.markdown(f"""
            <div class="framework-card">
                <p style="font-weight:700; color:var(--text-primary); font-size:1.05rem; margin:0 0 0.8rem 0;">Framework Compliance</p>
                <p style="color:var(--text-secondary); font-size:0.88rem; line-height:1.5;">
                    The 50-30-20 rule allocates 50% of monthly income to <strong>Needs</strong>, 30% to <strong>Wants</strong>, and 20% to <strong>Savings/Investments</strong>.
                </p>
                <div style="margin-top:1rem;">
                    <strong>Needs (Target 50%):</strong> {needs_pct:.1f}% ({format_amount(needs_spent, currency)})<br>
                    <strong>Wants (Target 30%):</strong> {wants_pct:.1f}% ({format_amount(wants_spent, currency)})<br>
                    <strong>Savings (Target 20%):</strong> {savings_pct:.1f}% ({format_amount(savings_invest, currency)})
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            pie_data = pd.DataFrame({
                'Allocation': ['Needs (Needs & Groceries)', 'Wants (Lifestyle)', 'Savings & Surplus'],
                'Percentage': [needs_pct, wants_pct, savings_pct]
            })
            fig_pie = px.pie(
                pie_data, values='Percentage', names='Allocation',
                color_discrete_sequence=['#3B82F6', '#FF8C42', '#10B981'],
                hole=0.4
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#F8FAFC', showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
    # 3. EMERGENCY FUND TRACKER
    with tab_emergency:
        st.markdown("<p style='font-weight:700; font-size:1.1rem; color:var(--text-primary); margin-bottom:0.5rem;'>Emergency Fund Tracker</p>", unsafe_allow_html=True)
        from pages.networth import get_assets
        assets_df = get_assets(user_id)
        
        cash_assets = 0.0
        if not assets_df.empty:
            cash_df = assets_df[assets_df['category'] == 'Cash & Savings']
            if not cash_df.empty:
                cash_assets = pd.to_numeric(cash_df['value'], errors='coerce').sum()
                
        # average monthly expenses
        avg_exp = 30000.0
        if not expenses_df.empty:
            expenses_df = expenses_df.copy()
            expenses_df['date'] = pd.to_datetime(expenses_df['date'])
            expenses_df['month'] = expenses_df['date'].dt.strftime('%Y-%m')
            avg_exp = expenses_df.groupby('month')['amount'].sum().mean()
            if pd.isna(avg_exp) or avg_exp == 0:
                avg_exp = 30000.0
                
        target_3m = avg_exp * 3
        target_6m = avg_exp * 6
        
        pct_3m = min(100.0, (cash_assets / target_3m) * 100.0) if target_3m > 0 else 100.0
        pct_6m = min(100.0, (cash_assets / target_6m) * 100.0) if target_6m > 0 else 100.0
        
        st.markdown(f"""
        <div class="framework-card">
            <p style="font-weight:700; color:var(--text-primary); font-size:1.05rem; margin:0 0 0.8rem 0;">Emergency Preparedness</p>
            <div style="font-size:0.95rem; margin-bottom:1rem;">
                <strong>Current Cash Reserve:</strong> <span style="color:#00D4AA; font-weight:700;">{format_amount(cash_assets, currency)}</span>
            </div>
            <div style="margin-bottom:1rem;">
                <strong>3-Month Target (Minimum): {format_amount(target_3m, currency)}</strong>
                <div style="background:var(--bg-elevated); border-radius:999px; height:12px; margin-top:4px;">
                    <div style="background:#3B82F6; width:{pct_3m}%; height:12px; border-radius:999px;"></div>
                </div>
                <span style="font-size:0.75rem; color:var(--text-muted);">{pct_3m:.1f}% Complete</span>
            </div>
            <div>
                <strong>6-Month Target (Secure): {format_amount(target_6m, currency)}</strong>
                <div style="background:var(--bg-elevated); border-radius:999px; height:12px; margin-top:4px;">
                    <div style="background:#10B981; width:{pct_6m}%; height:12px; border-radius:999px;"></div>
                </div>
                <span style="font-size:0.75rem; color:var(--text-muted);">{pct_6m:.1f}% Complete</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # 4. FIRE FRAMEWORK
    with tab_fire:
        st.markdown("<p style='font-weight:700; font-size:1.1rem; color:var(--text-primary); margin-bottom:0.5rem;'>FIRE Calculator (Financial Independence Retire Early)</p>", unsafe_allow_html=True)
        
        # Calculate annual expenses
        avg_exp = 30000.0
        if not expenses_df.empty:
            expenses_df = expenses_df.copy()
            expenses_df['date'] = pd.to_datetime(expenses_df['date'])
            expenses_df['month'] = expenses_df['date'].dt.strftime('%Y-%m')
            avg_exp = expenses_df.groupby('month')['amount'].sum().mean()
            if pd.isna(avg_exp) or avg_exp == 0:
                avg_exp = 30000.0
                
        annual_exp = avg_exp * 12
        fire_number = annual_exp * 25 # 4% safe withdrawal rule
        
        # Current net worth (Assets - Liabilities)
        total_assets = 0.0
        total_liab = 0.0
        if not assets_df.empty:
            total_assets = pd.to_numeric(assets_df['value'], errors='coerce').sum()
        from pages.networth import get_liabilities
        liabilities_df = get_liabilities(user_id)
        if not liabilities_df.empty:
            total_liab = pd.to_numeric(liabilities_df['value'], errors='coerce').sum()
            
        net_worth = max(0.0, total_assets - total_liab)
        fire_progress = (net_worth / fire_number) * 100 if fire_number > 0 else 0.0
        
        # Calculate monthly savings velocity
        avg_inc = 50000.0
        if not income_df.empty:
            income_df = income_df.copy()
            income_df['date'] = pd.to_datetime(income_df['date'])
            income_df['month'] = income_df['date'].dt.strftime('%Y-%m')
            avg_inc = income_df.groupby('month')['amount'].sum().mean()
            if pd.isna(avg_inc) or avg_inc == 0:
                avg_inc = 50000.0
                
        monthly_saving = max(1000.0, avg_inc - avg_exp)
        annual_saving = monthly_saving * 12
        
        years_to_fire = (fire_number - net_worth) / annual_saving if annual_saving > 0 else 99.0
        years_to_fire = max(0.0, years_to_fire)
        
        st.markdown(f"""
        <div class="framework-card">
            <p style="font-weight:700; color:var(--text-primary); font-size:1.05rem; margin:0 0 0.8rem 0;">FIRE Parameters</p>
            <table style="width:100%; border-collapse:collapse; font-size:0.92rem;">
                <tr style="border-bottom:1px solid var(--border); height:32px;">
                    <td style="color:var(--text-secondary);">FIRE Target (25x Annual Spend)</td>
                    <td style="text-align:right; font-weight:700; color:var(--accent);">{format_amount(fire_number, currency)}</td>
                </tr>
                <tr style="border-bottom:1px solid var(--border); height:32px;">
                    <td style="color:var(--text-secondary);">Current Net Worth</td>
                    <td style="text-align:right; font-weight:700; color:#3B82F6;">{format_amount(net_worth, currency)}</td>
                </tr>
                <tr style="border-bottom:1px solid var(--border); height:32px;">
                    <td style="color:var(--text-secondary);">Current Progress %</td>
                    <td style="text-align:right; font-weight:700; color:#10B981;">{fire_progress:.1f}%</td>
                </tr>
                <tr style="height:32px;">
                    <td style="color:var(--text-secondary);">Estimated Years Remaining</td>
                    <td style="text-align:right; font-weight:700; color:#F59E0B;">{years_to_fire:.1f} years</td>
                </tr>
            </table>
            <div style="margin-top:1rem;">
                <div style="background:var(--bg-elevated); border-radius:999px; height:12px;">
                    <div style="background:linear-gradient(90deg, #3B82F6, #10B981); width:{min(100.0, fire_progress)}%; height:12px; border-radius:999px;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

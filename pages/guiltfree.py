import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.db import get_all_expenses, get_all_income, get_budgets
from utils.currency import format_amount, get_symbol
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'data', 'finance.db'
)

def D(v):
    try:
        return Decimal(str(v)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP)
    except Exception:
        return Decimal('0.00')

def get_recurring_bills(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT * FROM recurring_bills WHERE user_id=?",
            conn, params=(user_id,)
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

def get_savings_goals(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT * FROM saving_goals WHERE user_id=?",
            conn, params=(user_id,)
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

def show(user_id=1):
    currency = st.session_state.get('currency', 'INR')
    symbol   = get_symbol(currency)
    today    = date.today()
    cur_month = today.strftime('%Y-%m')

    st.markdown("""
    <style>
    .slbl     { font-size:.75rem; font-weight:700;
                color:var(--accent); text-transform:uppercase;
                letter-spacing:.1em; margin-bottom:.6rem; }
    .big-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-surface) 100%);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        padding: 2rem;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-md);
    }
    .gf-amount {
        font-size: 3.5rem;
        font-weight: 900;
        line-height: 1;
        margin: 0.5rem 0;
    }
    .item-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1rem 1.2rem;
        margin-bottom: .5rem;
    }
    .kpi-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .kpi-lbl { font-size:.75rem; color:var(--text-muted);
               text-transform:uppercase; letter-spacing:.06em; }
    .kpi-val { font-size:1.4rem; font-weight:800;
               color:var(--text-primary); margin-top:4px; }
    .row-div { border-bottom:1px solid var(--border); margin:.3rem 0; }
    .tip-box {
        background: var(--accent-dim);
        border-left: 3px solid var(--accent);
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
        padding: .6rem .9rem;
        color: var(--text-secondary); font-size: .85rem;
        margin-bottom: .8rem;
    }
    .warning-box {
        background: var(--danger-dim);
        border-left: 3px solid var(--danger);
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
        padding: .6rem .9rem;
        color: var(--danger); font-size: .85rem;
        margin-bottom: .8rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="fc-page-title">Guilt-Free Spending</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="fc-page-sub">Know exactly how much you can spend '
        'freely — after bills, savings, and essentials.</p>',
        unsafe_allow_html=True)
    st.divider()

    # ── LOAD DATA ─────────────────────────────────────────────────────────────
    df_income  = get_all_income(user_id)
    df_expense = get_all_expenses(user_id)
    df_bills   = get_recurring_bills(user_id)
    df_goals   = get_savings_goals(user_id)
    df_budgets = get_budgets(user_id, cur_month)

    # Filter this month expenses
    if not df_expense.empty:
        df_expense['date'] = pd.to_datetime(df_expense['date'])
        df_this_month = df_expense[
            df_expense['date'].dt.strftime('%Y-%m') == cur_month
        ]
    else:
        df_this_month = pd.DataFrame()

    # This month income
    if not df_income.empty:
        df_income['date'] = pd.to_datetime(df_income['date'])
        df_income_month = df_income[
            df_income['date'].dt.strftime('%Y-%m') == cur_month
        ]
        monthly_income = float(
            df_income_month['amount'].sum()
            if not df_income_month.empty else 0
        )
    else:
        monthly_income = 0.0

    # If no income this month use average from history
    if monthly_income == 0 and not df_income.empty:
        months = df_income['date'].dt.to_period('M').nunique()
        monthly_income = float(
            df_income['amount'].sum() / max(months, 1)
        )

    # ── MANUAL INCOME OVERRIDE ────────────────────────────────────────────────
    st.markdown('<p class="slbl">Your Monthly Income</p>',
                unsafe_allow_html=True)

    income_input = st.number_input(
        f"Monthly Income ({symbol})",
        min_value=0.0,
        value=float(monthly_income),
        step=1000.0,
        format="%.2f",
        help="Auto-filled from your income records. Edit if needed."
    )
    monthly_income = income_input

    st.divider()

    # ── DEDUCTIONS ────────────────────────────────────────────────────────────
    st.markdown('<p class="slbl">Monthly Deductions</p>',
                unsafe_allow_html=True)
    st.markdown(
        "<div class='tip-box'>"
        "Set each deduction. The remainder is your "
        "guilt-free spending money.</div>",
        unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(
            "<p style='color:#FFF;font-weight:600;"
            "margin-bottom:.5rem'>Fixed Bills</p>",
            unsafe_allow_html=True)

        # Auto-fill from recurring bills
        if not df_bills.empty:
            bills_total = float(df_bills['amount'].sum())
            st.markdown(
                f"<p style='color:#8B8FA8;font-size:.82rem;"
                f"margin-bottom:.3rem'>"
                f"Auto-detected from Recurring Bills: "
                f"<strong style='color:var(--warning)'>"
                f"{format_amount(bills_total, currency)}"
                f"</strong></p>",
                unsafe_allow_html=True)
        else:
            bills_total = 0.0

        fixed_bills = st.number_input(
            f"Fixed Bills ({symbol})",
            min_value=0.0,
            value=bills_total,
            step=100.0,
            format="%.2f",
            help="Rent, electricity, subscriptions etc."
        )

        st.markdown(
            "<p style='color:#FFF;font-weight:600;"
            "margin:.8rem 0 .5rem'>EMIs / Loans</p>",
            unsafe_allow_html=True)
        emis = st.number_input(
            f"EMIs / Loan Payments ({symbol})",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.2f"
        )

    with col_right:
        st.markdown(
            "<p style='color:#FFF;font-weight:600;"
            "margin-bottom:.5rem'>Savings Target</p>",
            unsafe_allow_html=True)

        # Auto-fill from savings goals
        if not df_goals.empty:
            # Sum monthly needed for all active goals
            goals_monthly = 0.0
            for _, g in df_goals.iterrows():
                target = float(D(g['target']))
                saved  = float(D(g['saved']))
                dl     = g.get('deadline','') or ''
                if saved < target and dl:
                    try:
                        dd = datetime.strptime(
                            dl, '%Y-%m-%d').date()
                        months = max(
                            (dd.year - today.year) * 12
                            + dd.month - today.month, 1)
                        goals_monthly += (
                            target - saved) / months
                    except Exception:
                        pass
        else:
            goals_monthly = 0.0

        if goals_monthly > 0:
            st.markdown(
                f"<p style='color:#8B8FA8;font-size:.82rem;"
                f"margin-bottom:.3rem'>"
                f"Auto from Savings Goals: "
                f"<strong style='color:var(--accent)'>"
                f"{format_amount(goals_monthly, currency)}"
                f"/month</strong></p>",
                unsafe_allow_html=True)

        savings_target = st.number_input(
            f"Monthly Savings ({symbol})",
            min_value=0.0,
            value=float(goals_monthly),
            step=100.0,
            format="%.2f",
            help="How much you want to save each month"
        )

        st.markdown(
            "<p style='color:#FFF;font-weight:600;"
            "margin:.8rem 0 .5rem'>Essential Expenses</p>",
            unsafe_allow_html=True)

        # Auto-fill essentials from budget categories
        essential_cats = [
            'Food', 'Groceries', 'Transport',
            'Health', 'Utilities', 'Education'
        ]
        if not df_this_month.empty:
            ess_spent = float(
                df_this_month[
                    df_this_month['category'].isin(
                        essential_cats)
                ]['amount'].sum()
            )
        else:
            ess_spent = 0.0

        essentials = st.number_input(
            f"Essential Expenses ({symbol})",
            min_value=0.0,
            value=ess_spent,
            step=100.0,
            format="%.2f",
            help="Food, transport, health, utilities"
        )

    st.divider()

    # ── CALCULATE ─────────────────────────────────────────────────────────────
    total_deductions = (
        fixed_bills + emis + savings_target + essentials
    )
    guilt_free = max(monthly_income - total_deductions, 0)
    already_spent_disc = 0.0

    # How much already spent on discretionary this month
    if not df_this_month.empty:
        disc_cats = [
            'Entertainment', 'Shopping',
            'Other', 'Dining'
        ]
        already_spent_disc = float(
            df_this_month[
                df_this_month['category'].isin(disc_cats)
            ]['amount'].sum()
        )

    guilt_free_remaining = max(
        guilt_free - already_spent_disc, 0
    )
    spent_pct = (
        (already_spent_disc / guilt_free * 100)
        if guilt_free > 0 else 0
    )

    # ── BIG RESULT CARD ───────────────────────────────────────────────────────
    st.markdown('<p class="slbl">Your Guilt-Free Budget</p>',
                unsafe_allow_html=True)

    if monthly_income == 0:
        st.markdown(
            "<div class='warning-box'>"
            "Add your income first — go to the Income page "
            "or enter your monthly income above.</div>",
            unsafe_allow_html=True)
    else:
        # Color based on remaining
        if guilt_free_remaining <= 0:
            gf_color = "var(--danger)"
            gf_msg   = "You've used all your discretionary budget"
        elif spent_pct >= 80:
            gf_color = "var(--warning)"
            gf_msg   = "Running low — spend carefully"
        else:
            gf_color = "var(--accent)"
            gf_msg   = "You can spend this freely!"

        # Main card
        st.markdown(f"""
        <div class="big-card">
            <div style="color:var(--text-muted);font-size:.9rem;
                        text-transform:uppercase;
                        letter-spacing:.1em">
                Guilt-Free Spending Remaining
            </div>
            <div class="gf-amount" style="color:{gf_color}">
                {format_amount(guilt_free_remaining, currency)}
            </div>
            <div style="color:var(--text-secondary);font-size:.95rem;
                        margin-top:.5rem">
                {gf_msg}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Sub KPIs
        k1, k2, k3, k4 = st.columns(4)
        k1.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-lbl">Monthly Income</div>
            <div class="kpi-val" style="font-size:1.1rem">
                {format_amount(monthly_income, currency)}
            </div>
        </div>""", unsafe_allow_html=True)

        k2.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-lbl">Total Deductions</div>
            <div class="kpi-val" style="font-size:1.1rem;
                                         color:var(--danger)">
                {format_amount(total_deductions, currency)}
            </div>
        </div>""", unsafe_allow_html=True)

        k3.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-lbl">Full Budget</div>
            <div class="kpi-val" style="font-size:1.1rem;
                                         color:var(--accent)">
                {format_amount(guilt_free, currency)}
            </div>
        </div>""", unsafe_allow_html=True)

        k4.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-lbl">Already Spent</div>
            <div class="kpi-val" style="font-size:1.1rem;
                                         color:var(--warning)">
                {format_amount(already_spent_disc, currency)}
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Spending progress bar
        st.markdown(
            f"<p style='color:var(--text-secondary);font-size:.85rem;"
            f"margin-bottom:4px'>"
            f"Discretionary Budget Used — "
            f"{min(spent_pct,100):.1f}%</p>",
            unsafe_allow_html=True)
        bar_color = (
            "var(--danger)" if spent_pct >= 100 else
            "var(--warning)" if spent_pct >= 80 else
            "var(--accent)"
        )
        st.markdown(f"""
        <div style="background:#0F1117;border-radius:999px;
                    height:12px;margin-bottom:1.5rem">
            <div style="background:{bar_color};
                        width:{min(spent_pct,100):.1f}%;
                        height:12px;border-radius:999px">
            </div>
        </div>""", unsafe_allow_html=True)

        st.divider()

        # ── BREAKDOWN CHART ───────────────────────────────────────────────────
        st.markdown('<p class="slbl">Income Breakdown</p>',
                    unsafe_allow_html=True)

        labels = [
            'Fixed Bills', 'EMIs / Loans',
            'Savings', 'Essentials', 'Guilt-Free Budget'
        ]
        values = [
            fixed_bills, emis,
            savings_target, essentials, guilt_free
        ]
        colors = [
            '#EF4444', '#F59E0B',
            '#10B981', '#3B82F6', '#8B5CF6'
        ]

        # Remove zero items
        filtered = [
            (l, v, c) for l, v, c
            in zip(labels, values, colors)
            if v > 0
        ]
        if filtered:
            fl, fv, fc = zip(*filtered)
            fig = go.Figure(go.Pie(
                labels=fl,
                values=fv,
                marker=dict(colors=fc),
                hole=0.45,
                texttemplate='%{label}<br>%{percent}',
                textfont_color='#FFFFFF'
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF',
                legend=dict(
                    font=dict(color='#FFFFFF'),
                    bgcolor='rgba(0,0,0,0)'
                ),
                margin=dict(t=20,b=20,l=20,r=20),
                height=320
            )
            fig.update_traces(
                marker=dict(
                    line=dict(color='#0F1117', width=2))
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # ── DEDUCTION BREAKDOWN ───────────────────────────────────────────────
        st.markdown('<p class="slbl">Deduction Details</p>',
                    unsafe_allow_html=True)

        items = [
            ("Fixed Bills",      fixed_bills,      "var(--danger)"),
            ("EMIs / Loans",     emis,             "var(--warning)"),
            ("Monthly Savings",  savings_target,   "var(--accent)"),
            ("Essentials",       essentials,       "var(--info)"),
        ]

        for label, amount, color in items:
            if amount > 0:
                pct_of_income = (
                    amount / monthly_income * 100
                    if monthly_income > 0 else 0
                )
                ic1, ic2, ic3 = st.columns([4, 2, 2])
                ic1.markdown(
                    f"<span style='color:#FFF;"
                    f"font-weight:500'>{label}</span>",
                    unsafe_allow_html=True)
                ic2.markdown(
                    f"<span style='color:{color};"
                    f"font-weight:700'>"
                    f"{format_amount(amount, currency)}"
                    f"</span>",
                    unsafe_allow_html=True)
                ic3.markdown(
                    f"<span style='color:var(--text-muted);"
                    f"font-size:.85rem'>"
                    f"{pct_of_income:.1f}% of income"
                    f"</span>",
                    unsafe_allow_html=True)
                st.markdown(
                    "<div class='row-div'></div>",
                    unsafe_allow_html=True)

        # Total row
        ic1, ic2, ic3 = st.columns([4, 2, 2])
        ic1.markdown(
            "<span style='color:#FFF;font-weight:700'>"
            "Total Deductions</span>",
            unsafe_allow_html=True)
        ic2.markdown(
            f"<span style='color:var(--danger);font-weight:700'>"
            f"{format_amount(total_deductions, currency)}"
            f"</span>",
            unsafe_allow_html=True)
        pct_total = (
            total_deductions / monthly_income * 100
            if monthly_income > 0 else 0
        )
        ic3.markdown(
            f"<span style='color:var(--text-muted);font-size:.85rem'>"
            f"{pct_total:.1f}% of income</span>",
            unsafe_allow_html=True)

        st.divider()

        # ── SMART TIPS ────────────────────────────────────────────────────────
        st.markdown('<p class="slbl">Smart Insights</p>',
                    unsafe_allow_html=True)

        tips = []
        savings_pct = (
            savings_target / monthly_income * 100
            if monthly_income > 0 else 0
        )
        if savings_pct < 20:
            tips.append(
                f"You're saving {savings_pct:.1f}% of income. "
                f"Financial experts recommend saving at least 20%.")
        else:
            tips.append(
                f"Great! You're saving {savings_pct:.1f}% of income. "
                f"That's above the recommended 20%.")

        if pct_total > 80:
            tips.append(
                f"Your deductions are {pct_total:.1f}% of income — "
                f"very high. Try reducing fixed costs or EMIs.")
        elif pct_total > 60:
            tips.append(
                f"Deductions at {pct_total:.1f}% of income. "
                f"Try to keep this below 60%.")
        else:
            tips.append(
                f"Deductions at {pct_total:.1f}% — "
                f"healthy ratio. You have good spending room.")

        if guilt_free > 0 and already_spent_disc > guilt_free:
            overspend = already_spent_disc - guilt_free
            tips.append(
                f"You've overspent your discretionary budget by "
                f"{format_amount(overspend, currency)} this month.")

        if guilt_free_remaining > 0:
            daily_budget = guilt_free_remaining / max(
                (date(today.year, today.month + 1
                      if today.month < 12 else 1,
                      1) - today).days, 1
            )
            tips.append(
                f"You have {format_amount(guilt_free_remaining, currency)} "
                f"left for this month — roughly "
                f"{format_amount(daily_budget, currency)}/day.")

        for tip in tips:
            # Check if warning, error or normal info to style accordingly
            if "overspent" in tip or "high" in tip:
                st.markdown(
                    f"<div class='warning-box'>{tip}</div>",
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    f"<div class='tip-box'>{tip}</div>",
                    unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
import os
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from utils.db import get_all_expenses, get_all_income, get_budgets
from utils.currency import format_amount, get_symbol
from decimal import Decimal, ROUND_HALF_UP

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
            conn, params=(user_id,))
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

def get_savings_goals(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT * FROM saving_goals WHERE user_id=?",
            conn, params=(user_id,))
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

def show(user_id=1):
    currency = st.session_state.get('currency', 'INR')
    symbol   = get_symbol(currency)
    today    = date.today()

    st.markdown("""
    <style>
    .slbl     { font-size:.75rem; font-weight:700;
                color:var(--accent); text-transform:uppercase;
                letter-spacing:.1em; margin-bottom:.6rem; }
    .kpi-card { background:var(--bg-card); border:1px solid var(--border);
                border-radius:14px; padding:1.2rem 1.4rem; }
    .kpi-lbl  { font-size:.75rem; color:var(--text-muted);
                text-transform:uppercase; letter-spacing:.06em; }
    .kpi-val  { font-size:1.5rem; font-weight:800;
                color:var(--text-primary); margin-top:4px; }
    .kpi-sub  { font-size:.78rem; color:var(--text-muted); margin-top:4px; }
    .tip-box  { background:var(--accent-dim);
                border-left:3px solid var(--accent);
                border-radius:0 var(--radius-sm) var(--radius-sm) 0;
                padding:.6rem .9rem; color:var(--text-secondary);
                font-size:.85rem; margin-bottom:.6rem; }
    .warn-box { background:var(--warning-dim);
                border-left:3px solid var(--warning);
                border-radius:0 var(--radius-sm) var(--radius-sm) 0;
                padding:.6rem .9rem; color:var(--warning);
                font-size:.85rem; margin-bottom:.6rem; }
    .bad-box  { background:var(--danger-dim);
                border-left:3px solid var(--danger);
                border-radius:0 var(--radius-sm) var(--radius-sm) 0;
                padding:.6rem .9rem; color:var(--danger);
                font-size:.85rem; margin-bottom:.6rem; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="fc-page-title">Monthly Summary</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="fc-page-sub">Your complete financial picture for any month — income, spending, savings, and more.</p>',
        unsafe_allow_html=True)
    st.divider()

    # ── MONTH SELECTOR ────────────────────────────────────────────────────────
    df_all = get_all_expenses(user_id)
    if not df_all.empty:
        df_all['date'] = pd.to_datetime(df_all['date'])
        available_months = sorted(
            df_all['date'].dt.to_period('M').unique().tolist(),
            reverse=True)
        month_labels = [
            pd.Period(str(m)).strftime('%B %Y')
            for m in available_months]
    else:
        available_months = []
        month_labels     = []

    if not month_labels:
        st.markdown("""
        <div class="fc-empty">
            <h3 class="fc-empty-title">No data yet</h3>
            <p class="fc-empty-sub">
                Add some expenses to generate your monthly summary.
            </p>
        </div>""", unsafe_allow_html=True)
        return

    ms1, ms2 = st.columns([2, 3])
    with ms1:
        sel_label  = st.selectbox("Select Month", month_labels)
        sel_idx    = month_labels.index(sel_label)
        sel_period = available_months[sel_idx]
        sel_month  = str(sel_period)

    with ms2:
        prev_period = sel_period - 1
        prev_label  = pd.Period(str(prev_period)).strftime('%B %Y')
        st.markdown(
            f"<p style='color:var(--text-secondary);font-size:.85rem;"
            f"margin-top:1.8rem'>Comparing with: "
            f"<strong style='color:#FFF'>{prev_label}</strong></p>",
            unsafe_allow_html=True)

    st.divider()

    # ── LOAD DATA ─────────────────────────────────────────────────────────────
    df_month    = df_all[
        df_all['date'].dt.strftime('%Y-%m') == sel_month
    ].copy()
    df_prev_all = df_all[
        df_all['date'].dt.strftime('%Y-%m') == str(prev_period)
    ].copy()

    df_income_all = get_all_income(user_id)
    if not df_income_all.empty:
        df_income_all['date'] = pd.to_datetime(
            df_income_all['date'])
        df_income_month = df_income_all[
            df_income_all['date'].dt.strftime('%Y-%m') == sel_month]
        df_income_prev  = df_income_all[
            df_income_all['date'].dt.strftime('%Y-%m')
            == str(prev_period)]
        income_total      = float(df_income_month['amount'].sum())
        income_prev_total = float(df_income_prev['amount'].sum())
    else:
        df_income_month   = pd.DataFrame()
        df_income_prev    = pd.DataFrame()
        income_total      = 0.0
        income_prev_total = 0.0

    expense_total      = float(df_month['amount'].sum())
    expense_prev_total = float(df_prev_all['amount'].sum())
    net_savings        = income_total - expense_total
    savings_rate       = (
        net_savings / income_total * 100
        if income_total > 0 else 0)

    df_budgets = get_budgets(user_id, sel_month)

    # ── TOP KPI ROW ───────────────────────────────────────────────────────────
    st.markdown(
        f'<p class="slbl">{sel_label} — At a Glance</p>',
        unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)

    inc_diff = income_total - income_prev_total
    inc_pct  = (inc_diff / income_prev_total * 100
                if income_prev_total > 0 else 0)
    inc_sign = '+' if inc_pct >= 0 else '-'
    k1.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">Total Income</div>
        <div class="kpi-val" style="color:var(--accent)">
            {format_amount(income_total, currency)}
        </div>
        <div class="kpi-sub">
            {inc_sign}{abs(inc_pct):.1f}% vs {prev_label}
        </div>
    </div>""", unsafe_allow_html=True)

    exp_diff  = expense_total - expense_prev_total
    exp_pct   = (exp_diff / expense_prev_total * 100
                 if expense_prev_total > 0 else 0)
    exp_color = "var(--danger)" if exp_pct > 0 else "var(--accent)"
    exp_sign  = '+' if exp_pct >= 0 else '-'
    k2.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">Total Spent</div>
        <div class="kpi-val" style="color:var(--danger)">
            {format_amount(expense_total, currency)}
        </div>
        <div class="kpi-sub" style="color:{exp_color}">
            {exp_sign}{abs(exp_pct):.1f}% vs {prev_label}
        </div>
    </div>""", unsafe_allow_html=True)

    net_color = "var(--accent)" if net_savings >= 0 else "var(--danger)"
    k3.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">Net Savings</div>
        <div class="kpi-val" style="color:{net_color}">
            {format_amount(net_savings, currency)}
        </div>
        <div class="kpi-sub">
            {savings_rate:.1f}% savings rate
        </div>
    </div>""", unsafe_allow_html=True)

    tx_count      = len(df_month)
    tx_prev_count = len(df_prev_all)
    tx_diff       = tx_count - tx_prev_count
    k4.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">Transactions</div>
        <div class="kpi-val">{tx_count}</div>
        <div class="kpi-sub">
            {'+' if tx_diff >= 0 else ''}{tx_diff}
            vs {prev_label}
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── CHARTS ────────────────────────────────────────────────────────────────
    st.markdown('<p class="slbl">Income vs Expenses</p>',
                unsafe_allow_html=True)

    chart_l, chart_r = st.columns(2)

    with chart_l:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name=f'Income ({prev_label})',
            x=[prev_label],
            y=[income_prev_total],
            marker_color='#065F46',
        ))
        fig_bar.add_trace(go.Bar(
            name=f'Income ({sel_label})',
            x=[sel_label],
            y=[income_total],
            marker_color='#10B981',
        ))
        fig_bar.add_trace(go.Bar(
            name=f'Expenses ({prev_label})',
            x=[prev_label],
            y=[expense_prev_total],
            marker_color='#991B1B',
        ))
        fig_bar.add_trace(go.Bar(
            name=f'Expenses ({sel_label})',
            x=[sel_label],
            y=[expense_total],
            marker_color='#EF4444',
        ))
        fig_bar.update_layout(
            height=350,
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#FFFFFF',
            title='Month Comparison',
            title_font_color='#FFFFFF',
            xaxis=dict(gridcolor='#1E293B', color='#94A3B8'),
            yaxis=dict(gridcolor='#1E293B', color='#94A3B8',
                       rangemode='tozero'),
            legend=dict(font=dict(color='#FFFFFF'),
                        bgcolor='rgba(0,0,0,0)',
                        orientation='h',
                        yanchor='bottom', y=-0.4),
            margin=dict(t=40, b=80, l=20, r=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with chart_r:
        if not df_month.empty:
            cat_data = df_month.groupby(
                'category')['amount'].sum().reset_index()
            fig_pie = px.pie(
                cat_data, values='amount', names='category',
                color_discrete_sequence=[
                    '#10B981', '#3B82F6', '#F59E0B', '#EF4444',
                    '#8B5CF6', '#06B6D4', '#6366F1'],
                hole=0.4
            )
            fig_pie.update_layout(
                height=350,
                title=dict(
                    text='Spending by Category',
                    x=0.5,
                    y=0.95,
                    xanchor='center',
                    yanchor='top',
                    font=dict(size=16, color='#FFFFFF')
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF',
                legend=dict(font=dict(color='#FFFFFF'),
                            bgcolor='rgba(0,0,0,0)'),
                margin=dict(t=80, b=20, l=20, r=20)
            )
            fig_pie.update_traces(
                textposition='inside',
                texttemplate='%{label}<br>%{percent}',
                textfont_color='#FFFFFF',
                marker=dict(
                    line=dict(color='#0A0F1D', width=2))
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.markdown(
                "<div class='fc-empty'>"
                "<p style='color:var(--text-muted);margin:0'>"
                "No expenses this month.</p></div>",
                unsafe_allow_html=True)

    st.divider()

    # ── SPENDING + BUDGET ─────────────────────────────────────────────────────
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown('<p class="slbl">Spending Breakdown</p>',
                    unsafe_allow_html=True)

        if df_month.empty:
            st.markdown(
                "<p style='color:var(--text-muted)'>No expenses this month.</p>",
                unsafe_allow_html=True)
        else:
            cat_summary = df_month.groupby(
                'category')['amount'].agg(
                ['sum','count','mean']).reset_index()
            cat_summary = cat_summary.sort_values(
                'sum', ascending=False)

            for _, row in cat_summary.iterrows():
                pct   = (row['sum'] / expense_total * 100
                         if expense_total > 0 else 0)
                bar_w = min(pct, 100)

                prev_cat = float(
                    df_prev_all[
                        df_prev_all['category'] == row['category']
                    ]['amount'].sum())
                diff     = row['sum'] - prev_cat
                if diff > 0:
                    diff_str   = f"+ {format_amount(diff, currency)}"
                    diff_color = "var(--danger)"
                elif diff < 0:
                    diff_str   = f"- {format_amount(abs(diff), currency)}"
                    diff_color = "var(--accent)"
                else:
                    diff_str   = "same"
                    diff_color = "var(--text-muted)"

                st.markdown(
                    f"<div style='margin-bottom:.8rem'>"
                    f"<div style='display:flex;"
                    f"justify-content:space-between;"
                    f"margin-bottom:3px'>"
                    f"<span style='color:#FFF;font-weight:500'>"
                    f"{row['category']}</span>"
                    f"<span style='color:#FFF;font-weight:700'>"
                    f"{format_amount(row['sum'], currency)}"
                    f"</span></div>"
                    f"<div style='background:#0F1117;"
                    f"border-radius:999px;height:5px;"
                    f"margin-bottom:3px'>"
                    f"<div style='background:var(--info);"
                    f"width:{bar_w:.1f}%;height:5px;"
                    f"border-radius:999px'></div></div>"
                    f"<div style='display:flex;"
                    f"justify-content:space-between'>"
                    f"<span style='color:var(--text-muted);font-size:.75rem'>"
                    f"{pct:.1f}% · {int(row['count'])} txns"
                    f"</span>"
                    f"<span style='color:{diff_color};"
                    f"font-size:.75rem'>{diff_str}</span>"
                    f"</div></div>",
                    unsafe_allow_html=True)

    with right_col:
        st.markdown('<p class="slbl">Budget Status</p>',
                    unsafe_allow_html=True)

        if df_budgets.empty:
            st.markdown(
                "<div class='fc-empty'>"
                "<p style='color:var(--text-muted);margin:0'>"
                "No budgets set for this month.</p></div>",
                unsafe_allow_html=True)
        else:
            for _, bud in df_budgets.iterrows():
                cat   = bud['category']
                limit = float(bud['monthly_limit'])
                spent = float(
                    df_month[df_month['category'] == cat
                             ]['amount'].sum()
                    if not df_month.empty else 0)
                pct    = min(spent / limit, 1.0) \
                    if limit > 0 else 0
                remain = max(limit - spent, 0)

                if pct >= 1.0:
                    bc     = "var(--danger)"
                    status = "Over Budget"
                elif pct >= 0.8:
                    bc     = "var(--warning)"
                    status = "Almost Full"
                else:
                    bc     = "var(--accent)"
                    status = "On Track"

                st.markdown(
                    f"<div style='margin-bottom:.8rem'>"
                    f"<div style='display:flex;"
                    f"justify-content:space-between;"
                    f"margin-bottom:3px'>"
                    f"<span style='color:#FFF;font-weight:500'>"
                    f"{cat}</span>"
                    f"<span style='color:{bc};font-size:.78rem;"
                    f"font-weight:600'>{status}</span></div>"
                    f"<div style='background:#0F1117;"
                    f"border-radius:999px;height:8px;"
                    f"margin-bottom:3px'>"
                    f"<div style='background:{bc};"
                    f"width:{pct*100:.1f}%;height:8px;"
                    f"border-radius:999px'></div></div>"
                    f"<div style='display:flex;"
                    f"justify-content:space-between'>"
                    f"<span style='color:var(--text-muted);font-size:.75rem'>"
                    f"{format_amount(spent, currency)} spent</span>"
                    f"<span style='color:var(--text-muted);font-size:.75rem'>"
                    f"{format_amount(limit, currency)} limit"
                    f"</span></div></div>",
                    unsafe_allow_html=True)

    st.divider()

    # ── INCOME BREAKDOWN ──────────────────────────────────────────────────────
    if not df_income_month.empty:
        st.markdown('<p class="slbl">Income Sources</p>',
                    unsafe_allow_html=True)
        ig1, ig2 = st.columns(2)
        with ig1:
            for _, inc in df_income_month.iterrows():
                st.markdown(
                    f"<div style='display:flex;"
                    f"justify-content:space-between;"
                    f"padding:.4rem 0;"
                    f"border-bottom:1px solid var(--border)'>"
                    f"<span style='color:#FFF'>"
                    f"{inc['source']}</span>"
                    f"<span style='color:var(--accent);"
                    f"font-weight:700'>"
                    f"{format_amount(inc['amount'], currency)}"
                    f"</span></div>",
                    unsafe_allow_html=True)
        with ig2:
            src_data = df_income_month.groupby(
                'source')['amount'].sum().reset_index()
            fig_inc = px.pie(
                src_data, values='amount', names='source',
                hole=0.5,
                color_discrete_sequence=[
                    '#10B981', '#3B82F6', '#F59E0B', '#8B5CF6', '#EF4444']
            )
            fig_inc.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF',
                showlegend=True,
                legend=dict(font=dict(color='#FFFFFF'),
                            bgcolor='rgba(0,0,0,0)'),
                margin=dict(t=10,b=10,l=10,r=10),
                height=200
            )
            fig_inc.update_traces(
                texttemplate='%{percent}',
                textfont_color='#FFFFFF'
            )
            st.plotly_chart(fig_inc, use_container_width=True)
        st.divider()

    # ── TOP 5 EXPENSES ────────────────────────────────────────────────────────
    st.markdown('<p class="slbl">Top 5 Expenses This Month</p>',
                unsafe_allow_html=True)

    if not df_month.empty:
        top5 = df_month.nlargest(5, 'amount').copy()
        top5['date_str'] = top5['date'].dt.strftime('%d %b')

        th1,th2,th3,th4 = st.columns([2,2,2,2])
        for col, lbl in zip(
            [th1,th2,th3,th4],
            ['Date','Category','Amount','Notes']
        ):
            col.markdown(
                f"<span style='color:var(--text-muted);font-size:.75rem;"
                f"font-weight:700;text-transform:uppercase'>"
                f"{lbl}</span>",
                unsafe_allow_html=True)

        st.markdown(
            "<div style='border-bottom:1px solid var(--border);"
            "margin-bottom:.4rem'></div>",
            unsafe_allow_html=True)

        for _, row in top5.iterrows():
            c1,c2,c3,c4 = st.columns([2,2,2,2])
            c1.markdown(
                f"<span style='color:var(--text-muted);font-size:.88rem'>"
                f"{row['date_str']}</span>",
                unsafe_allow_html=True)
            c2.markdown(
                f"<span style='color:#FFF'>"
                f"{row['category']}</span>",
                unsafe_allow_html=True)
            c3.markdown(
                f"<span style='color:var(--danger);font-weight:700'>"
                f"{format_amount(row['amount'], currency)}"
                f"</span>",
                unsafe_allow_html=True)
            c4.markdown(
                f"<span style='color:var(--text-muted);font-size:.85rem'>"
                f"{row['notes'] or '—'}</span>",
                unsafe_allow_html=True)
            st.markdown(
                "<div style='border-bottom:1px solid var(--border);"
                "margin:.2rem 0'></div>",
                unsafe_allow_html=True)

    st.divider()

    # ── SMART INSIGHTS ────────────────────────────────────────────────────────
    st.markdown('<p class="slbl">Smart Insights</p>',
                unsafe_allow_html=True)

    insights = []

    if savings_rate >= 30:
        insights.append(("tip",
            f"Excellent! You saved {savings_rate:.1f}% of your income this month. Above the recommended 20%."))
    elif savings_rate >= 20:
        insights.append(("tip",
            f"Good job! You saved {savings_rate:.1f}% of your income. Keep it up!"))
    elif savings_rate >= 0:
        insights.append(("warn",
            f"You saved {savings_rate:.1f}% of income. Try to reach 20% next month."))
    else:
        insights.append(("bad",
            f"You spent more than you earned by {format_amount(abs(net_savings), currency)}. Review your expenses."))

    if expense_prev_total > 0:
        if exp_pct > 20:
            top_cat_name = (
                df_month.groupby('category')['amount']
                .sum().idxmax()
                if not df_month.empty else 'N/A')
            insights.append(("bad",
                f"Spending increased by {exp_pct:.1f}% vs last month. Highest category: {top_cat_name}."))
        elif exp_pct < -10:
            insights.append(("tip",
                f"Great! You reduced spending by {abs(exp_pct):.1f}% vs last month."))

    if not df_budgets.empty and not df_month.empty:
        over_budget = []
        for _, bud in df_budgets.iterrows():
            cat   = bud['category']
            limit = float(bud['monthly_limit'])
            spent = float(
                df_month[df_month['category'] == cat
                         ]['amount'].sum())
            if spent > limit:
                over_budget.append(cat)
        if over_budget:
            insights.append(("bad",
                f"Over budget in: {', '.join(over_budget)}."))

    if not df_month.empty:
        top_cat  = df_month.groupby(
            'category')['amount'].sum().idxmax()
        top_amt  = df_month.groupby(
            'category')['amount'].sum().max()
        pct_top  = (top_amt / expense_total * 100
                    if expense_total > 0 else 0)
        if pct_top > 50:
            insights.append(("warn",
                f"{top_cat} is {pct_top:.0f}% of your spending ({format_amount(top_amt, currency)})."))

    box_map = {"tip":"tip-box","warn":"warn-box","bad":"bad-box"}

    for kind, msg in insights:
        st.markdown(
            f"<div class='{box_map[kind]}'>"
            f"{msg}</div>",
            unsafe_allow_html=True)

    st.divider()

    # ── EXPORT ────────────────────────────────────────────────────────────────
    st.markdown('<p class="slbl">Export</p>',
                unsafe_allow_html=True)

    ex1, ex2 = st.columns(2)
    with ex1:
        if not df_month.empty:
            csv = df_month[
                ['date','category','amount','notes']
            ].copy()
            csv['date'] = csv['date'].dt.strftime('%Y-%m-%d')
            st.download_button(
                "Download Transactions CSV",
                csv.to_csv(index=False),
                file_name=f"summary_{sel_month}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
    with ex2:
        if not df_month.empty:
            cat_csv = df_month.groupby('category').agg(
                Total=('amount','sum'),
                Count=('amount','count'),
                Average=('amount','mean')
            ).reset_index()
            st.download_button(
                "Download Category Summary CSV",
                cat_csv.to_csv(index=False),
                file_name=f"categories_{sel_month}.csv",
                mime="text/csv",
                use_container_width=True
            )
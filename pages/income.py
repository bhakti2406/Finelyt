import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.db import (
    add_income, get_all_income, delete_income,
    get_expenses_by_month, get_all_expenses
)
from utils.currency import format_amount, get_symbol
import datetime

INCOME_SOURCES = [
    "Salary", "Freelance", "Business",
    "Investment", "Gift", "Other"
]

def show(user_id=1):
    currency = st.session_state.get('currency', 'INR')
    symbol   = get_symbol(currency)

    st.markdown("""
    <style>
    .kpi-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
        transition: var(--transition);
        box-shadow: var(--shadow-sm);
    }
    .kpi-card:hover {
        border-color: var(--border-light);
        background: var(--bg-card-hover);
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    .kpi-label {
        font-size: 0.72rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: var(--text-primary);
        margin-top: 4px;
        font-family: var(--font-mono);
        letter-spacing: -0.02em;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: var(--text-secondary);
        margin-top: 4px;
    }
    .empty-state {
        background: var(--bg-card);
        border: 1px dashed var(--border);
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="page-title">Income</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">Track your income sources '
        'and understand your cash flow.</p>',
        unsafe_allow_html=True)
    st.divider()

    df_income   = get_all_income(user_id)
    today        = datetime.date.today()
    current_month = today.strftime('%Y-%m')

    # ── ADD INCOME FORM ───────────────────────────────────────────────────────
    st.markdown(
        '<p class="section-title">Add Income</p>',
        unsafe_allow_html=True)

    with st.form("income_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            source = st.selectbox("Source", INCOME_SOURCES)
        with col2:
            amount = st.number_input(
                f"Amount ({symbol})",
                min_value=0.01, step=100.0, format="%.2f"
            )
        with col3:
            inc_date = st.date_input("Date", value=today)
        notes = st.text_input(
            "Notes (optional)",
            placeholder="e.g. Monthly salary, Project payment"
        )
        submitted = st.form_submit_button(
            "Save Income",
            use_container_width=True, type="primary"
        )

    if submitted:
        if amount <= 0:
            st.error("Amount must be greater than 0.")
        else:
            add_income(inc_date, source, amount,
                       notes, user_id)
            st.success(
                f"{format_amount(amount, currency)} from "
                f"{source} added on {inc_date}"
            )
            st.rerun()

    st.divider()

    # ── INCOME HISTORY ────────────────────────────────────────────────────────
    st.markdown(
        '<p class="section-title">Income History</p>',
        unsafe_allow_html=True)

    df_fresh = get_all_income(user_id)

    if df_fresh.empty:
        st.markdown("""
        <div class="empty-state">
            <h3 style="color:var(--text-primary);margin-bottom:0.5rem;">
                No income recorded yet
            </h3>
            <p style="color:var(--text-secondary);margin:0;">
                Add your first income entry above.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    if 'confirm_delete_income_id' not in st.session_state:
        st.session_state.confirm_delete_income_id = None

    # Column headers
    h1, h2, h3, h4 = st.columns([3.5, 2, 2, 0.7])
    for col, lbl in zip([h1,h2,h3,h4],
                        ['Source','Amount','Date','Del']):
        col.markdown(
            f"<span style='color:var(--text-muted);font-size:0.7rem;"
            f"font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.08em;'>{lbl}</span>",
            unsafe_allow_html=True)

    st.markdown(
        "<div style='border-bottom:1px solid var(--border);"
        "margin-bottom:0.5rem;'></div>",
        unsafe_allow_html=True)

    for _, row in df_fresh.iterrows():
        income_id = row['id']
        date_str  = str(row['date'])[:10]

        c1, c2, c3, c4 = st.columns([3.5, 2, 2, 0.7])

        with c1:
            st.markdown(
                f"<span style='color:var(--text-primary);"
                f"font-weight:600;'>{row['source']}</span>"
                f"<br><span style='color:var(--text-secondary);"
                f"font-size:0.78rem;'>"
                f"{row['notes'] or '—'}</span>",
                unsafe_allow_html=True)

        with c2:
            st.markdown(
                f"<span style='font-weight:700;"
                f"color:#10B981;font-size:1rem;"
                f"font-family:var(--font-mono);'>"
                f"{format_amount(row['amount'], currency)}"
                f"</span>",
                unsafe_allow_html=True)

        with c3:
            st.markdown(
                f"<span style='color:var(--text-secondary);"
                f"font-size:0.88rem;'>{date_str}</span>",
                unsafe_allow_html=True)

        with c4:
            if st.button("Del",
                          key=f"del_inc_{income_id}",
                          use_container_width=True):
                if st.session_state\
                        .confirm_delete_income_id == income_id:
                    st.session_state\
                        .confirm_delete_income_id = None
                else:
                    st.session_state\
                        .confirm_delete_income_id = income_id
                st.rerun()

        if st.session_state\
                .confirm_delete_income_id == income_id:
            st.markdown(f"""
            <div style='background:var(--danger-dim);
                        border:1px solid var(--danger);
                        border-radius:10px;
                        padding:0.7rem 1rem;
                        margin:0.2rem 0;'>
                <span style='color:var(--danger);font-weight:600;
                             font-size:0.88rem;'>
                    Delete {row['source']} —
                    {format_amount(row['amount'], currency)}?
                    This cannot be undone.
                </span>
            </div>
            """, unsafe_allow_html=True)
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button(
                    "Yes, Delete",
                    key=f"confirm_inc_{income_id}",
                    type="secondary",
                    use_container_width=True
                ):
                    delete_income(income_id, user_id)
                    st.session_state\
                        .confirm_delete_income_id = None
                    st.success(
                        f"{row['source']} — "
                        f"{format_amount(row['amount'], currency)}"
                        f" deleted."
                    )
                    st.rerun()
            with cc2:
                if st.button(
                    "Cancel",
                    key=f"cancel_inc_{income_id}",
                    use_container_width=True
                ):
                    st.session_state\
                        .confirm_delete_income_id = None
                    st.rerun()

        st.markdown(
            "<div style='border-bottom:1px solid var(--border);"
            "margin:0.3rem 0;'></div>",
            unsafe_allow_html=True)
    # ── KPI + CHARTS ──────────────────────────────────────────────────────────
    if not df_income.empty:
        df_income['date'] = pd.to_datetime(df_income['date'])
        df_this_month     = df_income[
            df_income['date'].dt.strftime('%Y-%m')
            == current_month
        ]

        total_income      = df_income['amount'].sum()
        income_this_month = (df_this_month['amount'].sum()
                             if not df_this_month.empty else 0)
        expenses_month    = get_expenses_by_month(
            user_id, current_month)
        total_expenses    = (expenses_month['amount'].sum()
                             if not expenses_month.empty else 0)
        cash_flow         = income_this_month - total_expenses
        savings_rate      = (
            cash_flow / income_this_month * 100
            if income_this_month > 0 else 0
        )
        months_count = (
            df_income['date'].dt.to_period('M').nunique()
        )
        avg_monthly  = (
            total_income / months_count
            if months_count > 0 else 0
        )
        top_source   = df_income.groupby(
            'source')['amount'].sum().idxmax()

        st.markdown(
            '<p class="section-title">Analytics</p>',
            unsafe_allow_html=True)

        chart_col, kpi_col = st.columns([1.6, 1])

        with chart_col:
            source_data = df_income.groupby(
                'source')['amount'].sum().reset_index()
            fig_pie = px.pie(
                source_data,
                values='amount', names='source',
                color_discrete_sequence=[
                    '#10B981','#3B82F6','#F59E0B',
                    '#8B5CF6','#EF4444','#059669'
                ],
                hole=0.4
            )
            fig_pie.update_layout(
                title=dict(
                    text='Income by Source',
                    x=0.5,
                    y=0.95,
                    xanchor='center',
                    yanchor='top',
                    font=dict(size=18, color='#F8FAFC')
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#F8FAFC',
                legend=dict(
                    font=dict(color='#94A3B8'),
                    bgcolor='rgba(0,0,0,0)'),
                margin=dict(t=100, b=40, l=40, r=40),
                height=340
            )
            fig_pie.update_traces(
                texttemplate='%{label}<br>%{percent}',
                textfont_color='#FFFFFF',
                marker=dict(
                    line=dict(color='#0A0F1D', width=2))
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            df_income['month_str']   = (
                df_income['date'].dt.strftime('%b %Y'))
            df_income['month_order'] = (
                df_income['date'].dt.to_period('M'))
            monthly = df_income.groupby(
                ['month_order','month_str']
            )['amount'].sum().reset_index()
            monthly = monthly.sort_values('month_order')
            monthly.columns = ['Order','Month','Amount']

            fig_bar = px.bar(
                monthly, x='Month', y='Amount',
                title='Monthly Income Trend',
                color='Amount',
                color_continuous_scale=[
                    '#3B82F6','#10B981'],
                text='Amount'
            )
            fig_bar.update_traces(
                texttemplate='%{text:,.0f}',
                textposition='outside',
                textfont_color='#F8FAFC'
            )
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#F8FAFC',
                title_font_color='#F8FAFC',
                xaxis=dict(
                    gridcolor='#1E293B', color='#94A3B8',
                    title='Month', type='category'),
                yaxis=dict(
                    gridcolor='#1E293B', color='#94A3B8',
                    title=f'Amount ({currency})',
                    rangemode='tozero'),
                coloraxis_showscale=False,
                margin=dict(t=40,b=20,l=10,r=10),
                height=260
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with kpi_col:
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Income</div>
                <div class="kpi-value">
                    {format_amount(total_income, currency)}
                </div>
                <div class="kpi-sub">all time</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">This Month</div>
                <div class="kpi-value">
                    {format_amount(income_this_month, currency)}
                </div>
                <div class="kpi-sub">
                    {today.strftime('%B %Y')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            cf_color = (
                "#10B981" if cash_flow >= 0 else "#EF4444"
            )
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Cash Flow</div>
                <div class="kpi-value"
                     style="color:{cf_color};">
                    {format_amount(cash_flow, currency)}
                </div>
                <div class="kpi-sub">
                    {savings_rate:.1f}% savings rate
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Avg Monthly</div>
                <div class="kpi-value">
                    {format_amount(avg_monthly, currency)}
                </div>
                <div class="kpi-sub">
                    top source: {top_source}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Income vs Expenses
        st.markdown(
            '<p class="section-title">Income vs Expenses</p>',
            unsafe_allow_html=True)

        df_exp = get_all_expenses(user_id)
        if not df_exp.empty:
            df_exp['date']       = pd.to_datetime(
                df_exp['date'])
            df_exp['month_str']  = (
                df_exp['date'].dt.strftime('%b %Y'))
            df_exp['month_order'] = (
                df_exp['date'].dt.to_period('M'))
            exp_monthly = df_exp.groupby(
                ['month_order','month_str']
            )['amount'].sum().reset_index()
            exp_monthly.columns = ['Order','Month','Expenses']

            df_income['month_str2']   = (
                df_income['date'].dt.strftime('%b %Y'))
            df_income['month_order2'] = (
                df_income['date'].dt.to_period('M'))
            inc_monthly = df_income.groupby(
                ['month_order2','month_str2']
            )['amount'].sum().reset_index()
            inc_monthly.columns = ['Order','Month','Income']

            merged = pd.merge(
                inc_monthly, exp_monthly,
                on='Month', how='outer'
            ).fillna(0)

            fig_compare = go.Figure()
            fig_compare.add_trace(go.Bar(
                name='Income',
                x=merged['Month'],
                y=merged['Income'],
                marker_color='#10B981'
            ))
            fig_compare.add_trace(go.Bar(
                name='Expenses',
                x=merged['Month'],
                y=merged['Expenses'],
                marker_color='#EF4444'
            ))
            fig_compare.update_layout(
                barmode='group',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#F8FAFC',
                xaxis=dict(
                    gridcolor='#1E293B', color='#94A3B8',
                    type='category'),
                yaxis=dict(
                    gridcolor='#1E293B', color='#94A3B8',
                    title=f'Amount ({currency})',
                    rangemode='tozero'),
                legend=dict(
                    font=dict(color='#94A3B8'),
                    bgcolor='rgba(0,0,0,0)'),
                margin=dict(t=20,b=20,l=10,r=10)
            )
            st.plotly_chart(
                fig_compare, use_container_width=True)

        st.divider()
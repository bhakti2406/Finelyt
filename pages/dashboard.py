import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.db import get_all_expenses, get_budgets
from utils.currency import format_amount
from datetime import datetime
from dateutil.relativedelta import relativedelta

def show(user_id=1):
    currency = st.session_state.get('currency', 'INR')

    st.markdown("""
    <style>
    .health-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-surface) 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-sm);
    }
    .onboarding-card {
        background: linear-gradient(135deg, var(--bg-card), var(--bg-surface));
        border: 1px solid var(--accent);
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        box-shadow: var(--shadow-md);
    }
    .compare-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.5rem;
        transition: var(--transition);
        box-shadow: var(--shadow-sm);
    }
    .compare-card:hover {
        border-color: var(--border-light);
        background: var(--bg-card-hover);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    </style>
    """, unsafe_allow_html=True)

    # Page header
    st.markdown('<p class="page-title">Dashboard</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">Your complete financial overview.</p>',
        unsafe_allow_html=True)
    st.divider()

    df = get_all_expenses(user_id)

    if df.empty:
        st.markdown("""
        <div class="onboarding-card">
            <div style="width:56px;height:56px;
                        background:var(--accent-dim);
                        border:1px solid rgba(16,185,129,0.3);
                        border-radius:16px;
                        display:flex;align-items:center;
                        justify-content:center;
                        margin:0 auto 1.2rem;">
                <svg width="26" height="26" viewBox="0 0 24 24"
                     fill="none" stroke="#10B981" stroke-width="2"
                     stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="1" x2="12" y2="23"/>
                    <path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5
                             3.5 0 010 7H6"/>
                </svg>
            </div>
            <h2 style="color:var(--text-primary);margin-bottom:0.5rem;
                        font-size:1.5rem;font-weight:800;
                        letter-spacing:-0.02em;">
                Welcome to Finelyt
            </h2>
            <p style="color:var(--text-secondary);font-size:1rem;
                       margin-bottom:1.5rem;line-height:1.6;">
                Your dashboard will come alive once you add
                your first expense.
            </p>
            <p style="color:var(--accent);font-weight:600;
                       font-size:0.9rem;">
                Click "Add Expense" in the sidebar to get started
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    df['date']       = pd.to_datetime(df['date'])
    df['month']      = df['date'].dt.strftime('%Y-%m')
    current_month    = datetime.now().strftime('%Y-%m')
    prev_month       = (
        datetime.now() - relativedelta(months=1)
    ).strftime('%Y-%m')
    df_this_month = df[df['month'] == current_month]
    df_prev_month = df[df['month'] == prev_month]

    try:
        from utils.health_score import calculate_health_score
        score, label, color = calculate_health_score(df, user_id)
    except Exception:
        score, label, color = 100, "Excellent", "#10B981"

    anomaly_count = 0
    try:
        if len(df) >= 10:
            from utils.features import prepare_features
            from utils.predict import predict_anomalies
            df_full, X = prepare_features(df)
            result     = predict_anomalies(df_full, X)
            anomaly_count = int((result['anomaly'] == -1).sum())
    except Exception:
        anomaly_count = 0

    # ── KPI CARDS ─────────────────────────────────────────────────────────────
    st.markdown(
        '<p class="section-title">Financial Overview</p>',
        unsafe_allow_html=True)

    col_health, col1, col2, col3, col4 = st.columns(
        [1.2, 1, 1, 1, 1])

    with col_health:
        st.markdown(f"""
        <div class="health-card">
            <div style="font-size:0.72rem;color:var(--text-muted);
                        text-transform:uppercase;
                        letter-spacing:0.12em;
                        font-weight:600;margin-bottom:8px;">
                Health Score
            </div>
            <div style="font-size:3.5rem;font-weight:900;
                        color:{color};line-height:1;
                        font-family:var(--font-mono);
                        text-shadow: 0 0 15px {color}40, 0 0 30px {color}15;">
                {score}
            </div>
            <div style="font-size:0.9rem;font-weight:600;
                        color:{color};margin-top:0.4rem;">
                {label}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col1:
        total = (df_this_month['amount'].sum()
                 if not df_this_month.empty
                 else df['amount'].sum())
        prev_total = (df_prev_month['amount'].sum()
                      if not df_prev_month.empty else 0)
        delta_total = total - prev_total
        st.metric(
            "Total Spent",
            format_amount(total, currency),
            delta=(
                f"{format_amount(abs(delta_total), currency)} "
                f"{'more' if delta_total > 0 else 'less'} "
                f"than last month"
            ) if prev_total > 0 else None,
            delta_color="inverse"
        )

    with col2:
        if not df_this_month.empty:
            daily = df_this_month.groupby(
                'date')['amount'].sum().mean()
        else:
            daily = df.groupby('date')['amount'].sum().mean()
        st.metric("Daily Average",
                  format_amount(daily, currency))

    with col3:
        count      = (len(df_this_month)
                      if not df_this_month.empty else len(df))
        prev_count = (len(df_prev_month)
                      if not df_prev_month.empty else 0)
        st.metric(
            "Transactions",
            count,
            delta=count - prev_count if prev_count > 0 else None
        )

    with col4:
        delta = (f"{anomaly_count} flagged"
                 if anomaly_count > 0 else None)
        st.metric("Anomalies", anomaly_count,
                  delta=delta, delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CHARTS ────────────────────────────────────────────────────────────────
    st.markdown(
        '<p class="section-title">Spending Breakdown</p>',
        unsafe_allow_html=True)

    col_pie, col_bar = st.columns(2)

    with col_pie:
        cat_data = df.groupby(
            'category')['amount'].sum().reset_index()
        cat_data['display'] = cat_data['amount'].apply(
            lambda x: format_amount(x, currency)
        )
        fig_pie = px.pie(
            cat_data,
            values='amount',
            names='category',
            color_discrete_sequence=[
                '#10B981','#3B82F6','#F59E0B','#EF4444',
                '#8B5CF6','#059669','#F97316','#6366F1'
            ],
            hole=0.4,
            hover_data={'display': True, 'amount': False}
        )
        fig_pie.update_layout(
            height=350,
            title=dict(
                text='Spending by Category',
                x=0.5,
                y=0.95,
                xanchor='center',
                yanchor='top',
                font=dict(size=16, color='#F8FAFC')
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#F8FAFC',
            legend=dict(
                font=dict(color='#94A3B8'),
                bgcolor='rgba(0,0,0,0)'
            ),
            margin=dict(t=80, b=20, l=20, r=20)
        )
        fig_pie.update_traces(
            textposition='inside',
            texttemplate='%{label}<br>%{percent}',
            textfont_color='#FFFFFF',
            marker=dict(line=dict(color='#0A0F1D', width=2))
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_bar:
        df['month_str']   = df['date'].dt.strftime('%b %Y')
        df['month_order'] = df['date'].dt.to_period('M')
        monthly = df.groupby(
            ['month_order', 'month_str']
        )['amount'].sum().reset_index()
        monthly = monthly.sort_values('month_order')
        monthly.columns = ['Order', 'Month', 'Amount']

        fig_bar = px.bar(
            monthly,
            x='Month',
            y='Amount',
            title='Monthly Spending Trend',
            color='Amount',
            color_continuous_scale=[
                '#10B981', '#3B82F6', '#EF4444'],
            text='Amount'
        )
        fig_bar.update_traces(
            texttemplate='%{text:,.0f}',
            textposition='outside',
            textfont_color='#F8FAFC'
        )
        fig_bar.update_layout(
            height=350,
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
            margin=dict(t=40, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── MONTH COMPARISON ──────────────────────────────────────────────────────
    st.markdown(
        '<p class="section-title">Month vs Last Month</p>',
        unsafe_allow_html=True)

    current_label = datetime.now().strftime('%B %Y')
    prev_label    = (
        datetime.now() - relativedelta(months=1)
    ).strftime('%B %Y')

    if df_prev_month.empty:
        st.markdown(f"""
        <div style="background:var(--bg-card);
                    border:1px dashed var(--border);
                    border-radius:12px;padding:1.5rem;
                    text-align:center;">
            <p style="color:var(--text-secondary);margin:0;font-size:0.88rem;">
                No data for {prev_label} yet.
                Comparison will appear once you have
                two months of data.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        categories = sorted(set(
            df_this_month['category'].unique().tolist() +
            df_prev_month['category'].unique().tolist()
        ))

        comparison_data = []
        for cat in categories:
            curr = df_this_month[
                df_this_month['category'] == cat
            ]['amount'].sum()
            prev = df_prev_month[
                df_prev_month['category'] == cat
            ]['amount'].sum()
            diff       = curr - prev
            pct_change = (
                (curr - prev) / prev * 100
                if prev > 0 else 0
            )
            comparison_data.append({
                'Category':     cat,
                current_label:  curr,
                prev_label:     prev,
                'Change':       diff,
                'Change %':     pct_change
            })

        comp_df = pd.DataFrame(comparison_data)

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            name=prev_label,
            x=comp_df['Category'],
            y=comp_df[prev_label],
            marker_color='#3B82F6',
            text=comp_df[prev_label].apply(
                lambda x: format_amount(x, currency)),
            textposition='outside',
            textfont_color='#F8FAFC'
        ))
        fig_comp.add_trace(go.Bar(
            name=current_label,
            x=comp_df['Category'],
            y=comp_df[current_label],
            marker_color='#10B981',
            text=comp_df[current_label].apply(
                lambda x: format_amount(x, currency)),
            textposition='outside',
            textfont_color='#F8FAFC'
        ))
        fig_comp.update_layout(
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#F8FAFC',
            title=(
                f'{prev_label} vs {current_label}'
                f' — Category Comparison'
            ),
            title_font_color='#F8FAFC',
            xaxis=dict(
                gridcolor='#1E293B', color='#94A3B8'),
            yaxis=dict(
                gridcolor='#1E293B', color='#94A3B8'),
            legend=dict(
                font=dict(color='#94A3B8'),
                bgcolor='rgba(0,0,0,0)'
            ),
            margin=dict(t=60, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        for _, row in comp_df.iterrows():
            curr_amt = row[current_label]
            prev_amt = row[prev_label]
            diff     = row['Change']
            pct      = row['Change %']

            if diff > 0:
                arrow      = "↑"
                diff_color = "#EF4444"
            elif diff < 0:
                arrow      = "↓"
                diff_color = "#10B981"
            else:
                arrow      = "→"
                diff_color = "#94A3B8"

            st.markdown(f"""
            <div class="compare-card">
                <div style="display:flex;
                            justify-content:space-between;
                            align-items:center;">
                    <div style="font-weight:600;
                                color:var(--text-primary);font-size:0.95rem;">
                        {row['Category']}
                    </div>
                    <div style="display:flex;gap:2rem;
                                align-items:center;">
                        <div style="text-align:center;">
                            <div style="font-size:0.7rem;
                                        color:var(--text-muted);
                                        text-transform:uppercase;
                                        letter-spacing:0.06em;">
                                {prev_label}
                            </div>
                            <div style="color:#3B82F6;
                                        font-weight:600;
                                        font-size:0.9rem;">
                                {format_amount(prev_amt, currency)}
                            </div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:0.7rem;
                                        color:var(--text-muted);
                                        text-transform:uppercase;
                                        letter-spacing:0.06em;">
                                {current_label}
                            </div>
                            <div style="color:#10B981;
                                        font-weight:600;
                                        font-size:0.9rem;">
                                {format_amount(curr_amt, currency)}
                            </div>
                        </div>
                        <div style="text-align:right;
                                    min-width:80px;">
                            <div style="color:{diff_color};
                                        font-weight:700;
                                        font-size:1.05rem;">
                                {arrow} {abs(pct):.1f}%
                            </div>
                            <div style="color:{diff_color};
                                        font-size:0.78rem;">
                                {format_amount(abs(diff), currency)}
                                {'more' if diff > 0 else 'less'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── BUDGET STATUS ─────────────────────────────────────────────────────────
    st.markdown(
        '<p class="section-title">Budget Status</p>',
        unsafe_allow_html=True)

    budgets_df = get_budgets(user_id, current_month)

    if budgets_df.empty:
        st.markdown("""
        <div style="background:var(--bg-card);
                    border:1px dashed var(--border);
                    border-radius:12px;padding:1.5rem;
                    text-align:center;">
            <p style="color:var(--text-secondary);margin:0;font-size:0.88rem;">
                No budgets set for this month.
                <span style="color:var(--accent);">
                    Go to Budgets to set category limits.
                </span>
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for _, budget in budgets_df.iterrows():
            cat        = budget['category']
            limit      = budget['monthly_limit']
            spent_data = df_this_month[
                df_this_month['category'] == cat]
            spent = (spent_data['amount'].sum()
                     if not spent_data.empty else 0)
            pct   = min(spent / limit, 1.0) if limit > 0 else 0

            if pct >= 1.0:
                bar_color    = "#EF4444"
                status       = "Over Budget"
                status_color = "#EF4444"
            elif pct >= 0.8:
                bar_color    = "#F59E0B"
                status       = "Approaching"
                status_color = "#F59E0B"
            else:
                bar_color    = "#10B981"
                status       = "On Track"
                status_color = "#10B981"

            col_label, col_bar_col, col_status = \
                st.columns([2, 5, 2])

            with col_label:
                st.markdown(
                    f"<p style='color:var(--text-primary);"
                    f"font-weight:600;margin-top:8px;"
                    f"font-size:0.9rem;'>{cat}</p>",
                    unsafe_allow_html=True
                )
            with col_bar_col:
                st.markdown(f"""
                <div style="background:var(--bg-elevated);
                            border-radius:999px;height:8px;
                            margin-top:16px;">
                    <div style="background:{bar_color};
                                width:{pct*100:.1f}%;
                                height:8px;
                                border-radius:999px;">
                    </div>
                </div>
                <div style="display:flex;
                            justify-content:space-between;
                            margin-top:4px;">
                    <span style="color:var(--text-secondary);
                                 font-size:0.75rem;">
                        {format_amount(spent, currency)} spent
                    </span>
                    <span style="color:var(--text-secondary);
                                 font-size:0.75rem;">
                        {format_amount(limit, currency)} limit
                    </span>
                </div>
                """, unsafe_allow_html=True)

            with col_status:
                st.markdown(
                    f"<p style='color:{status_color};"
                    f"font-size:0.82rem;font-weight:600;"
                    f"margin-top:8px;text-align:right;'>"
                    f"{status}</p>",
                    unsafe_allow_html=True
                )

            if pct >= 1.0:
                st.warning(
                    f"{cat} is "
                    f"{format_amount(spent - limit, currency)}"
                    f" over budget!"
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── RECENT TRANSACTIONS ───────────────────────────────────────────────────
    st.markdown(
        '<p class="section-title">Recent Transactions</p>',
        unsafe_allow_html=True)

    recent = df.head(10).copy()
    
    # Column headers
    h1, h2, h3, h4 = st.columns([2.5, 2.5, 2.5, 4.5])
    h1.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;'>Date</span>", unsafe_allow_html=True)
    h2.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;'>Category</span>", unsafe_allow_html=True)
    h3.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;text-align:right;display:block;'>Amount</span>", unsafe_allow_html=True)
    h4.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;'>Notes</span>", unsafe_allow_html=True)
    st.markdown(
        "<div style='border-bottom:1px solid var(--border); margin-bottom:0.5rem;'></div>",
        unsafe_allow_html=True
    )

    for _, row in recent.iterrows():
        date_str = row['date'].strftime('%d %b %Y')
        amt_str = format_amount(row['amount'], currency)
        notes_str = row['notes'] if row['notes'] else '—'
        
        c1, c2, c3, c4 = st.columns([2.5, 2.5, 2.5, 4.5])
        with c1:
            st.markdown(f"<span style='color:var(--text-secondary);font-size:0.88rem;'>{date_str}</span>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<span class='feature-badge' style='margin:0;padding:2px 8px;font-size:0.75rem;'>{row['category']}</span>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<span style='color:var(--danger);font-weight:700;font-family:var(--font-mono);font-size:0.95rem;text-align:right;display:block;'>{amt_str}</span>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<span style='color:var(--text-muted);font-size:0.85rem;'>{notes_str}</span>", unsafe_allow_html=True)
            
        st.markdown(
            "<div style='border-bottom:1px solid rgba(255,255,255,0.03); margin:0.3rem 0;'></div>",
            unsafe_allow_html=True
        )

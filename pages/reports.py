import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_all_expenses
from utils.currency import format_amount, get_symbol
from datetime import datetime, date

def show(user_id=1):
    currency = st.session_state.get('currency', 'INR')
    symbol = get_symbol(currency)

    st.markdown("""
    <style>
    .active-filter {
        background: var(--accent-dim);
        border: 1px solid var(--accent);
        border-radius: var(--radius-sm);
        padding: 0.4rem 0.8rem;
        color: var(--accent);
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="fc-page-title">Reports</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="fc-page-sub">Filter, analyse, and download your expense history.</p>',
        unsafe_allow_html=True
    )
    st.divider()

    all_df = get_all_expenses(user_id)

    if all_df.empty:
        st.markdown("""
        <div class="fc-empty">
            <h3 class="fc-empty-title">No expenses to report</h3>
            <p class="fc-empty-sub">Add some expenses first to generate reports.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    all_df['date'] = pd.to_datetime(all_df['date'])
    min_date = all_df['date'].min().date()
    max_date = all_df['date'].max().date()
    today = date.today()

    # ── FILTERS ───────────────────────────────────────────────────────────────
    st.markdown('<p class="fc-section-label">Filters</p>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)

    with f1:
        view_by = st.selectbox(
            "View By",
            ["All Time", "Month", "Year", "Day", "Custom Range"]
        )

    with f2:
        all_cats = sorted(all_df['category'].unique().tolist())
        # Auto select all by default
        selected_cats = st.multiselect(
            "Categories",
            options=all_cats,
            default=all_cats,
            placeholder="All categories selected"
        )
        if not selected_cats:
            selected_cats = all_cats

    with f3:
        sort_by = st.selectbox(
            "Sort By",
            ["Date (Newest First)", "Date (Oldest First)",
             "Amount (Highest First)", "Amount (Lowest First)",
             "Category (A-Z)"]
        )

    # ── TIME PERIOD SELECTOR ──────────────────────────────────────────────────
    start_date = min_date
    end_date = max_date
    filter_label = "All Time"

    if view_by == "Month":
        all_df['month_period'] = all_df['date'].dt.to_period('M')
        available_months = sorted(
            all_df['month_period'].unique().tolist(), reverse=True
        )
        month_display = [
            pd.Period(str(m)).strftime('%B %Y') for m in available_months
        ]
        selected_month_display = st.selectbox("Select Month", month_display)
        selected_idx = month_display.index(selected_month_display)
        selected_period = available_months[selected_idx]
        start_date = selected_period.start_time.date()
        end_date = selected_period.end_time.date()
        if end_date > max_date:
            end_date = max_date
        filter_label = f"Month: {selected_month_display}"

    elif view_by == "Year":
        available_years = sorted(
            all_df['date'].dt.year.unique().tolist(), reverse=True
        )
        selected_year = st.selectbox("Select Year", available_years)
        start_date = date(selected_year, 1, 1)
        end_date = date(selected_year, 12, 31)
        if end_date > max_date:
            end_date = max_date
        filter_label = f"Year: {selected_year}"

    elif view_by == "Day":
        # Use max_date as default so it's always valid
        selected_day = st.date_input(
            "Select Day",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )
        start_date = selected_day
        end_date = selected_day
        filter_label = f"Day: {selected_day.strftime('%d %b %Y')}"

    elif view_by == "Custom Range":
        cr1, cr2 = st.columns(2)
        with cr1:
            start_date = st.date_input(
                "From", value=min_date,
                min_value=min_date, max_value=max_date
            )
        with cr2:
            end_date = st.date_input(
                "To", value=max_date,
                min_value=min_date, max_value=max_date
            )
        filter_label = (f"Custom: {start_date.strftime('%d %b %Y')} "
                        f"to {end_date.strftime('%d %b %Y')}")

    else:
        start_date = min_date
        end_date = max_date
        filter_label = "All Time"

    st.markdown(
        f"<div class='active-filter'>Showing: {filter_label}</div>",
        unsafe_allow_html=True
    )

    # ── APPLY FILTERS ─────────────────────────────────────────────────────────
    filtered = all_df[
        (all_df['date'].dt.date >= start_date) &
        (all_df['date'].dt.date <= end_date)
    ].copy()

    filtered = filtered[filtered['category'].isin(selected_cats)]

    # ── APPLY SORTING ─────────────────────────────────────────────────────────
    if sort_by == "Date (Newest First)":
        filtered = filtered.sort_values('date', ascending=False)
    elif sort_by == "Date (Oldest First)":
        filtered = filtered.sort_values('date', ascending=True)
    elif sort_by == "Amount (Highest First)":
        filtered = filtered.sort_values('amount', ascending=False)
    elif sort_by == "Amount (Lowest First)":
        filtered = filtered.sort_values('amount', ascending=True)
    elif sort_by == "Category (A-Z)":
        filtered = filtered.sort_values('category', ascending=True)

    st.divider()

    if filtered.empty:
        st.markdown("""
        <div class="fc-empty">
            <h3 class="fc-empty-title">No results</h3>
            <p class="fc-empty-sub">No expenses match your filters.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── SUMMARY KPIs ──────────────────────────────────────────────────────────
    st.markdown('<p class="fc-section-label">Summary</p>', unsafe_allow_html=True)

    total = filtered['amount'].sum()
    avg_tx = filtered['amount'].mean()
    num_tx = len(filtered)
    num_days = max((end_date - start_date).days + 1, 1)
    daily_avg = total / num_days
    top_cat = filtered.groupby('category')['amount'].sum().idxmax()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.markdown(f"""
    <div class="fc-metric">
        <div class="fc-metric-label">Total Spent</div>
        <div class="fc-metric-value">{format_amount(total, currency)}</div>
    </div>
    """, unsafe_allow_html=True)
    k2.markdown(f"""
    <div class="fc-metric">
        <div class="fc-metric-label">Transactions</div>
        <div class="fc-metric-value">{num_tx}</div>
    </div>
    """, unsafe_allow_html=True)
    k3.markdown(f"""
    <div class="fc-metric">
        <div class="fc-metric-label">Daily Average</div>
        <div class="fc-metric-value">{format_amount(daily_avg, currency)}</div>
    </div>
    """, unsafe_allow_html=True)
    k4.markdown(f"""
    <div class="fc-metric">
        <div class="fc-metric-label">Avg Transaction</div>
        <div class="fc-metric-value">{format_amount(avg_tx, currency)}</div>
    </div>
    """, unsafe_allow_html=True)
    k5.markdown(f"""
    <div class="fc-metric">
        <div class="fc-metric-label">Top Category</div>
        <div class="fc-metric-value" style="font-size:1.1rem;">{top_cat}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CHARTS ────────────────────────────────────────────────────────────────
    st.markdown('<p class="fc-section-label">Visual Breakdown</p>',
                unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        cat_summary = filtered.groupby('category')['amount'].sum().reset_index()
        cat_summary.columns = ['Category', 'Amount']
        cat_summary = cat_summary.sort_values('Amount', ascending=False)
        fig_bar = px.bar(
            cat_summary, x='Amount', y='Category',
            orientation='h', title='Spending by Category',
            color='Amount',
            color_continuous_scale=['#1E293B', '#10B981']
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#FFFFFF', title_font_color='#FFFFFF',
            xaxis=dict(gridcolor='#1E293B', color='#94A3B8',
                       title=f'Amount ({currency})'),
            yaxis=dict(gridcolor='#1E293B', color='#94A3B8'),
            coloraxis_showscale=False,
            margin=dict(t=40, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        if view_by == "Year":
            filtered['period'] = filtered['date'].dt.strftime('%b %Y')
            filtered['period_sort'] = filtered['date'].dt.strftime('%Y-%m')
        else:
            filtered['period'] = filtered['date'].dt.strftime('%d %b %Y')
            filtered['period_sort'] = filtered['date'].dt.strftime('%Y-%m-%d')

        trend = filtered.groupby(
            ['period_sort', 'period']
        )['amount'].sum().reset_index()
        trend = trend.sort_values('period_sort')
        trend.columns = ['Sort', 'Period', 'Amount']

        fig_line = px.line(
            trend, x='Period', y='Amount',
            title='Spending Trend', markers=True
        )
        fig_line.update_traces(line_color='#10B981', marker_color='#10B981')
        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#FFFFFF', title_font_color='#FFFFFF',
            xaxis=dict(gridcolor='#1E293B', color='#94A3B8',
                       type='category', tickangle=-45),
            yaxis=dict(gridcolor='#1E293B', color='#94A3B8',
                       title=f'Amount ({currency})', rangemode='tozero'),
            margin=dict(t=40, b=60, l=20, r=20)
        )
        st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    # ── CATEGORY BREAKDOWN ────────────────────────────────────────────────────
    st.markdown('<p class="fc-section-label">Category Breakdown</p>',
                unsafe_allow_html=True)

    cat_table = filtered.groupby('category').agg(
        Total=('amount', 'sum'),
        Transactions=('amount', 'count'),
        Average=('amount', 'mean'),
        Highest=('amount', 'max'),
        Lowest=('amount', 'min')
    ).reset_index()
    cat_table = cat_table.sort_values('Total', ascending=False)
    for col in ['Total', 'Average', 'Highest', 'Lowest']:
        cat_table[col] = cat_table[col].apply(
            lambda x: format_amount(x, currency)
        )
    cat_table.columns = ['Category', 'Total', 'Transactions',
                         'Average', 'Highest', 'Lowest']
    # Column headers
    rh1, rh2, rh3, rh4, rh5, rh6 = st.columns([2.5, 2, 1.2, 2.1, 2.1, 2.1])
    rh1.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;'>Category</span>", unsafe_allow_html=True)
    rh2.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;text-align:right;display:block;'>Total</span>", unsafe_allow_html=True)
    rh3.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;text-align:center;display:block;'>Txns</span>", unsafe_allow_html=True)
    rh4.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;text-align:right;display:block;'>Average</span>", unsafe_allow_html=True)
    rh5.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;text-align:right;display:block;'>Highest</span>", unsafe_allow_html=True)
    rh6.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;text-align:right;display:block;'>Lowest</span>", unsafe_allow_html=True)
    st.markdown(
        "<div style='border-bottom:1px solid var(--border); margin-bottom:0.5rem;'></div>",
        unsafe_allow_html=True
    )

    for _, row in cat_table.iterrows():
        rc1, rc2, rc3, rc4, rc5, rc6 = st.columns([2.5, 2, 1.2, 2.1, 2.1, 2.1])
        with rc1:
            st.markdown(f"<span class='feature-badge' style='margin:0;padding:2px 8px;font-size:0.75rem;'>{row['Category']}</span>", unsafe_allow_html=True)
        with rc2:
            st.markdown(f"<span style='color:var(--danger);font-weight:700;font-family:var(--font-mono);font-size:0.88rem;text-align:right;display:block;'>{row['Total']}</span>", unsafe_allow_html=True)
        with rc3:
            st.markdown(f"<span style='color:var(--text-primary);font-size:0.88rem;text-align:center;display:block;'>{row['Transactions']}</span>", unsafe_allow_html=True)
        with rc4:
            st.markdown(f"<span style='color:var(--text-secondary);font-family:var(--font-mono);font-size:0.88rem;text-align:right;display:block;'>{row['Average']}</span>", unsafe_allow_html=True)
        with rc5:
            st.markdown(f"<span style='color:var(--text-secondary);font-family:var(--font-mono);font-size:0.88rem;text-align:right;display:block;'>{row['Highest']}</span>", unsafe_allow_html=True)
        with rc6:
            st.markdown(f"<span style='color:var(--text-secondary);font-family:var(--font-mono);font-size:0.88rem;text-align:right;display:block;'>{row['Lowest']}</span>", unsafe_allow_html=True)
        st.markdown(
            "<div style='border-bottom:1px solid rgba(255,255,255,0.03); margin:0.3rem 0;'></div>",
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TRANSACTIONS TABLE ────────────────────────────────────────────────────
    st.markdown(
        f'<p class="section-title">Transactions ({len(filtered)})</p>',
        unsafe_allow_html=True
    )

    display = filtered.copy()
    display['date_display'] = display['date'].dt.strftime('%d %b %Y')
    display['amount_display'] = display['amount'].apply(
        lambda x: format_amount(x, currency)
    )

    has_payment = 'payment_method' in display.columns
    if has_payment:
        th1, th2, th3, th4, th5 = st.columns([2.5, 2.5, 2.5, 2.5, 4.5])
        th1.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;'>Date</span>", unsafe_allow_html=True)
        th2.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;'>Category</span>", unsafe_allow_html=True)
        th3.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;text-align:right;display:block;'>Amount</span>", unsafe_allow_html=True)
        th4.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;'>Payment</span>", unsafe_allow_html=True)
        th5.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;'>Notes</span>", unsafe_allow_html=True)
        st.markdown("<div style='border-bottom:1px solid var(--border); margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)

        for _, row in display.iterrows():
            c1, c2, c3, c4, c5 = st.columns([2.5, 2.5, 2.5, 2.5, 4.5])
            with c1:
                st.markdown(f"<span style='color:var(--text-secondary);font-size:0.88rem;'>{row['date_display']}</span>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<span class='feature-badge' style='margin:0;padding:2px 8px;font-size:0.75rem;'>{row['category']}</span>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<span style='color:var(--danger);font-weight:700;font-family:var(--font-mono);font-size:0.95rem;text-align:right;display:block;'>{row['amount_display']}</span>", unsafe_allow_html=True)
            with c4:
                st.markdown(f"<span style='color:var(--text-primary);font-size:0.88rem;'>{row['payment_method']}</span>", unsafe_allow_html=True)
            with c5:
                notes_val = row['notes'] if row['notes'] else '—'
                st.markdown(f"<span style='color:var(--text-muted);font-size:0.85rem;'>{notes_val}</span>", unsafe_allow_html=True)
            st.markdown("<div style='border-bottom:1px solid rgba(255,255,255,0.03); margin:0.3rem 0;'></div>", unsafe_allow_html=True)
    else:
        th1, th2, th3, th4 = st.columns([2.5, 2.5, 2.5, 4.5])
        th1.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;'>Date</span>", unsafe_allow_html=True)
        th2.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;'>Category</span>", unsafe_allow_html=True)
        th3.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;text-align:right;display:block;'>Amount</span>", unsafe_allow_html=True)
        th4.markdown("<span style='color:var(--text-secondary);font-size:0.75rem;text-transform:uppercase;font-weight:700;'>Notes</span>", unsafe_allow_html=True)
        st.markdown("<div style='border-bottom:1px solid var(--border); margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)

        for _, row in display.iterrows():
            c1, c2, c3, c4 = st.columns([2.5, 2.5, 2.5, 4.5])
            with c1:
                st.markdown(f"<span style='color:var(--text-secondary);font-size:0.88rem;'>{row['date_display']}</span>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<span class='feature-badge' style='margin:0;padding:2px 8px;font-size:0.75rem;'>{row['category']}</span>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<span style='color:var(--danger);font-weight:700;font-family:var(--font-mono);font-size:0.95rem;text-align:right;display:block;'>{row['amount_display']}</span>", unsafe_allow_html=True)
            with c4:
                notes_val = row['notes'] if row['notes'] else '—'
                st.markdown(f"<span style='color:var(--text-muted);font-size:0.85rem;'>{notes_val}</span>", unsafe_allow_html=True)
            st.markdown("<div style='border-bottom:1px solid rgba(255,255,255,0.03); margin:0.3rem 0;'></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── DOWNLOAD ──────────────────────────────────────────────────────────────
    st.markdown('<p class="section-title">Download</p>',
                unsafe_allow_html=True)

    dl1, dl2 = st.columns(2)
    with dl1:
        csv_data = filtered[['date', 'category', 'amount', 'notes']].copy()
        csv_data['date'] = csv_data['date'].dt.strftime('%Y-%m-%d')
        st.download_button(
            label="Download Transactions CSV",
            data=csv_data.to_csv(index=False),
            file_name=f"transactions_{start_date}_to_{end_date}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
    with dl2:
        summary_csv = filtered.groupby('category').agg(
            Total=('amount', 'sum'),
            Transactions=('amount', 'count'),
            Average=('amount', 'mean')
        ).reset_index().to_csv(index=False)
        st.download_button(
            label="Download Summary CSV",
            data=summary_csv,
            file_name=f"summary_{start_date}_to_{end_date}.csv",
            mime="text/csv",
            use_container_width=True
        )
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.db import get_all_expenses
from utils.features import prepare_features
from utils.predict import predict_anomalies, explain_anomaly
from utils.currency import format_amount
import subprocess
import sys
import os

def show(user_id=1):
    currency = st.session_state.get('currency', 'INR')

    st.markdown("""
    <style>
    .stat-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        transition: var(--transition);
        box-shadow: var(--shadow-sm);
    }
    .stat-card:hover {
        border-color: var(--border-light);
        background: var(--bg-card-hover);
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    .stat-label {
        font-size: 0.72rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
    }
    .stat-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--text-primary);
        margin-top: 4px;
        font-family: var(--font-mono);
        letter-spacing: -0.02em;
    }
    .anomaly-card {
        background: linear-gradient(
            135deg, var(--danger-dim) 0%, var(--bg-card) 100%);
        border: 1px solid var(--danger);
        border-left: 4px solid var(--danger);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
        box-shadow: var(--shadow-sm);
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

    st.markdown('<p class="page-title">Anomaly Detection</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">Machine learning flags transactions '
        "that don't fit your normal spending pattern.</p>",
        unsafe_allow_html=True)
    st.divider()

    df = get_all_expenses(user_id)

    if df.empty:
        st.markdown("""
        <div class="empty-state">
            <div style="width:48px;height:48px;
                        background:var(--bg-elevated);
                        border-radius:12px;
                        display:flex;align-items:center;
                        justify-content:center;
                        margin:0 auto 1rem;">
                <svg width="22" height="22" viewBox="0 0 24 24"
                     fill="none" stroke="var(--text-secondary)" stroke-width="2"
                     stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="11" cy="11" r="8"/>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                </svg>
            </div>
            <h3 style="color:var(--text-primary);margin-bottom:0.5rem;">
                No data to analyse
            </h3>
            <p style="color:var(--text-secondary);margin:0;">
                Add at least 10 expenses to enable
                anomaly detection.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    if len(df) < 10:
        st.markdown(f"""
        <div class="empty-state">
            <div style="width:48px;height:48px;
                        background:var(--bg-elevated);
                        border-radius:12px;
                        display:flex;align-items:center;
                        justify-content:center;
                        margin:0 auto 1rem;">
                <svg width="22" height="22" viewBox="0 0 24 24"
                     fill="none" stroke="var(--text-secondary)" stroke-width="2"
                     stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="20" x2="18" y2="10"/>
                    <line x1="12" y1="20" x2="12" y2="4"/>
                    <line x1="6" y1="20" x2="6" y2="14"/>
                </svg>
            </div>
            <h3 style="color:var(--text-primary);margin-bottom:0.5rem;">
                Need more data
            </h3>
            <p style="color:var(--text-secondary);margin:0;">
                You have
                <strong style="color:var(--text-primary);">{len(df)}</strong>
                expenses. Need at least
                <strong style="color:var(--accent);">10</strong>
                to run the model.
                Add {10 - len(df)} more to unlock this feature.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    df['date'] = pd.to_datetime(df['date'])
    df_full, X = prepare_features(df)
    MODEL_PATH  = os.path.join('models', 'anomaly_model.pkl')

    if not os.path.exists(MODEL_PATH):
        st.markdown("""
        <div class="empty-state">
            <div style="width:48px;height:48px;
                        background:var(--accent-dim);
                        border:1px solid rgba(16,185,129,0.3);
                        border-radius:12px;
                        display:flex;align-items:center;
                        justify-content:center;
                        margin:0 auto 1rem;">
                <svg width="22" height="22" viewBox="0 0 24 24"
                     fill="none" stroke="#10B981" stroke-width="2"
                     stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2a4 4 0 014 4v1h1a3 3 0 013
                             3v6a3 3 0 01-3 3H7a3 3 0 01-3-3V10
                             a3 3 0 013-3h1V6a4 4 0 014-4z"/>
                </svg>
            </div>
            <h3 style="color:var(--text-primary);margin-bottom:0.5rem;">
                Model Not Trained Yet
            </h3>
            <p style="color:var(--text-secondary);margin:0 0 1.5rem;">
                Train the ML model on your expense data
                to detect anomalies.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Train Model Now", type="primary",
                     use_container_width=True):
            with st.spinner("Training model on your data..."):
                try:
                    subprocess.run(
                        [sys.executable,
                         'models/train_model.py'],
                        check=True
                    )
                    st.success("Model trained. Refreshing...")
                    st.rerun()
                except Exception as e:
                    st.error(f"Training failed: {e}")
        return

    result    = predict_anomalies(df_full, X)
    anomalies = result[result['anomaly'] == -1].copy()
    normal    = result[result['anomaly'] == 1].copy()
    anomalies = anomalies.sort_values('anomaly_score')

    def get_severity(score):
        s = abs(float(score))
        if s > 0.1:    return "HIGH",   "#EF4444"
        elif s > 0.05: return "MEDIUM", "#F59E0B"
        else:          return "LOW",    "#F59E0B"

    anomaly_total = (anomalies['amount'].sum()
                     if not anomalies.empty else 0)
    anomaly_pct   = (len(anomalies) / len(result) * 100
                     if len(result) > 0 else 0)

    # ── KPI CARDS ─────────────────────────────────────────────────────────────
    st.markdown(
        '<p class="section-title">Detection Summary</p>',
        unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Total Transactions</div>
        <div class="stat-value">{len(result)}</div>
    </div>""", unsafe_allow_html=True)

    k2.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Anomalies Found</div>
        <div class="stat-value" style="color:#EF4444;">
            {len(anomalies)}
        </div>
        <div style="font-size:0.75rem;color:var(--text-secondary);
                    margin-top:4px;">
            {anomaly_pct:.1f}% of all transactions
        </div>
    </div>""", unsafe_allow_html=True)

    k3.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Normal Transactions</div>
        <div class="stat-value" style="color:#10B981;">
            {len(normal)}
        </div>
    </div>""", unsafe_allow_html=True)

    k4.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Flagged Amount</div>
        <div class="stat-value" style="color:#F59E0B;">
            {format_amount(anomaly_total, currency)}
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CHARTS ────────────────────────────────────────────────────────────────
    st.markdown(
        '<p class="section-title">Spending Timeline</p>',
        unsafe_allow_html=True)

    chart_left, chart_right = st.columns([1.6, 1])

    with chart_left:
        result['date_str']  = (
            result['date'].dt.strftime('%d %b %Y'))
        result['date_sort'] = (
            result['date'].dt.strftime('%Y-%m-%d'))
        result['Status']    = result['anomaly'].map(
            {1: 'Normal', -1: 'Anomaly'})
        result_sorted = result.sort_values('date_sort')

        fig_scatter = px.scatter(
            result_sorted,
            x='date_str', y='amount',
            color='Status',
            color_discrete_map={
                'Normal': '#10B981', 'Anomaly': '#EF4444'},
            title='All Transactions — Anomalies Highlighted',
            hover_data={
                'date_str': True, 'category': True,
                'amount': ':,.0f', 'Status': True,
                'date_sort': False
            },
            size='amount', size_max=30
        )
        fig_scatter.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#F8FAFC',
            title_font_color='#F8FAFC',
            xaxis=dict(
                gridcolor='#1E293B', color='#94A3B8',
                title='Date', type='category',
                tickangle=-45),
            yaxis=dict(
                gridcolor='#1E293B', color='#94A3B8',
                title=f'Amount ({currency})',
                rangemode='tozero'),
            legend=dict(
                font=dict(color='#94A3B8'),
                bgcolor='rgba(0,0,0,0)'),
            margin=dict(t=50, b=60, l=20, r=20)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with chart_right:
        cat_counts = result.groupby(
            ['category','Status']
        ).size().reset_index(name='Count')
        fig_cat = px.bar(
            cat_counts, x='Count', y='category',
            color='Status', orientation='h',
            color_discrete_map={
                'Normal': '#10B981', 'Anomaly': '#EF4444'},
            title='Anomalies by Category',
            barmode='stack'
        )
        fig_cat.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#F8FAFC',
            title_font_color='#F8FAFC',
            xaxis=dict(
                gridcolor='#1E293B', color='#94A3B8',
                title='Count'),
            yaxis=dict(
                gridcolor='#1E293B', color='#94A3B8',
                title=''),
            legend=dict(
                font=dict(color='#94A3B8'),
                bgcolor='rgba(0,0,0,0)'),
            margin=dict(t=50, b=20, l=10, r=10)
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    st.divider()

    # ── FLAGGED TRANSACTIONS ──────────────────────────────────────────────────
    if not anomalies.empty:
        st.markdown(
            '<p class="section-title">Flagged Transactions</p>',
            unsafe_allow_html=True)

        f1, f2 = st.columns(2)
        with f1:
            all_cats = ["All Categories"] + sorted(
                anomalies['category'].unique().tolist()
            )
            sel_cat = st.selectbox(
                "Filter by Category", all_cats)
        with f2:
            sel_sev = st.selectbox(
                "Filter by Severity",
                ["All", "HIGH", "MEDIUM", "LOW"]
            )

        filtered_anomalies = anomalies.copy()
        if sel_cat != "All Categories":
            filtered_anomalies = filtered_anomalies[
                filtered_anomalies['category'] == sel_cat
            ]
        if sel_sev != "All":
            filtered_anomalies = filtered_anomalies[
                filtered_anomalies['anomaly_score'].apply(
                    lambda s: get_severity(s)[0] == sel_sev
                )
            ]

        st.markdown(
            f"<p style='color:var(--text-secondary);font-size:0.85rem;'>"
            f"Showing {len(filtered_anomalies)} of "
            f"{len(anomalies)} flagged transactions</p>",
            unsafe_allow_html=True)

        if filtered_anomalies.empty:
            st.info("No anomalies match your current filters.")
        else:
            for _, row in filtered_anomalies.iterrows():
                explanation = explain_anomaly(row, result)
                date_str    = (
                    row['date'].strftime('%d %b %Y')
                    if hasattr(row['date'], 'strftime')
                    else str(row['date'])[:10]
                )
                sev, sev_color = get_severity(
                    row['anomaly_score'])
                cat_avg   = result[
                    result['category'] == row['category']
                ]['amount'].mean()
                times_avg = (row['amount'] / cat_avg
                             if cat_avg > 0 else 1)

                badge_html = (
                    f"<span style='background:{sev_color}22;"
                    f"border:1px solid {sev_color};"
                    f"color:{sev_color};"
                    f"border-radius:999px;"
                    f"padding:3px 12px;"
                    f"font-size:0.72rem;"
                    f"font-weight:700;'>"
                    f"{sev}</span>"
                )

                st.markdown(f"""
                <div class="anomaly-card">
                    <div style="display:flex;
                                justify-content:space-between;
                                align-items:flex-start;
                                margin-bottom:0.8rem;">
                        <div>
                            <span style="font-size:1.05rem;
                                         font-weight:700;
                                         color:var(--text-primary);
                                         font-family:var(--font-mono);">
                                {format_amount(row['amount'],
                                               currency)}
                            </span>
                            <span style="color:var(--text-secondary);
                                         font-size:0.88rem;
                                         margin-left:0.8rem;">
                                {row['category']} · {date_str}
                            </span>
                        </div>
                        {badge_html}
                    </div>
                    <div style="background:var(--danger-dim);
                                border-radius:8px;
                                padding:0.6rem 0.8rem;
                                margin-bottom:0.8rem;">
                        <span style="color:var(--danger);
                                     font-size:0.83rem;
                                     font-weight:600;">
                            Why flagged:
                        </span>
                        <span style="color:var(--text-primary);
                                     font-size:0.83rem;
                                     margin-left:0.4rem;">
                            {explanation}
                        </span>
                    </div>
                    <div style="display:grid;
                                grid-template-columns:
                                1fr 1fr 1fr 1fr;
                                gap:0.8rem;">
                        <div>
                            <div style="color:var(--text-muted);
                                        font-size:0.72rem;
                                        text-transform:uppercase;
                                        letter-spacing:0.06em;">
                                Amount
                            </div>
                            <div style="color:var(--danger);
                                        font-weight:700;
                                        font-size:0.92rem;
                                        font-family:var(--font-mono);">
                                {format_amount(row['amount'],
                                               currency)}
                            </div>
                        </div>
                        <div>
                            <div style="color:var(--text-muted);
                                        font-size:0.72rem;
                                        text-transform:uppercase;
                                        letter-spacing:0.06em;">
                                Category Avg
                            </div>
                            <div style="color:var(--text-primary);
                                        font-size:0.92rem;
                                        font-family:var(--font-mono);">
                                {format_amount(cat_avg,
                                               currency)}
                            </div>
                        </div>
                        <div>
                            <div style="color:var(--text-muted);
                                        font-size:0.72rem;
                                        text-transform:uppercase;
                                        letter-spacing:0.06em;">
                                Times Avg
                            </div>
                            <div style="color:#F59E0B;
                                        font-weight:700;
                                        font-size:0.92rem;">
                                {times_avg:.1f}x
                            </div>
                        </div>
                        <div>
                            <div style="color:var(--text-muted);
                                        font-size:0.72rem;
                                        text-transform:uppercase;
                                        letter-spacing:0.06em;">
                                Notes
                            </div>
                            <div style="color:var(--text-primary);
                                        font-size:0.92rem;">
                                {row['notes']
                                 if row['notes'] else '—'}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="background:var(--accent-dim);
                    border:1px solid var(--accent);
                    border-radius:12px;padding:2rem;
                    text-align:center;">
            <div style="width:44px;height:44px;
                        background:var(--accent-dim);
                        border:1px solid rgba(16,185,129,0.3);
                        border-radius:12px;
                        display:flex;align-items:center;
                        justify-content:center;
                        margin:0 auto 1rem;">
                <svg width="20" height="20" viewBox="0 0 24 24"
                     fill="none" stroke="#10B981" stroke-width="2.5"
                     stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"/>
                </svg>
            </div>
            <h3 style="color:#10B981;margin:0 0 0.4rem;">
                No anomalies detected
            </h3>
            <p style="color:var(--text-secondary);margin:0;font-size:0.88rem;">
                Your spending patterns look healthy and consistent.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── MODEL CONTROLS ────────────────────────────────────────────────────────
    st.markdown(
        '<p class="section-title">Model Controls</p>',
        unsafe_allow_html=True)

    ctrl1, ctrl2 = st.columns([3, 1])
    with ctrl1:
        st.markdown(f"""
        <div style="background:var(--bg-card);
                    border:1px solid var(--border);
                    border-radius:12px;
                    padding:1rem 1.2rem;">
            <p style="color:var(--text-secondary);font-size:0.85rem;margin:0;">
                Model trained on
                <strong style="color:var(--text-primary);">
                    {len(result)}
                </strong>
                transactions with
                <strong style="color:var(--danger);">
                    {len(anomalies)}
                </strong>
                anomalies detected.
                Retrain after adding more expenses
                for better accuracy.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with ctrl2:
        if st.button("Retrain Model",
                     use_container_width=True,
                     type="primary"):
            with st.spinner("Retraining..."):
                try:
                    subprocess.run(
                        [sys.executable,
                         'models/train_model.py'],
                        check=True
                    )
                    st.success("Model retrained.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")

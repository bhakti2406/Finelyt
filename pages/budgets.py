import streamlit as st
import pandas as pd
import sqlite3
import os
from utils.db import set_budget, get_budgets, delete_budget, get_expenses_by_month
from utils.currency import format_amount, get_symbol
from datetime import datetime, date

CATEGORIES = [
    "Food", "Transport", "Shopping", "Utilities",
    "Entertainment", "Health", "Education", "Other"
]

BILL_CATEGORIES = [
    "Utilities", "Entertainment", "Health", "Education",
    "Transport", "Food", "Shopping", "Other"
]

def get_db_path():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', 'data', 'finance.db'
    )

def ensure_bills_table():
    conn = sqlite3.connect(get_db_path())
    conn.execute('''
        CREATE TABLE IF NOT EXISTS recurring_bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            due_day INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    conn.commit()
    conn.close()

def add_bill(user_id, name, amount, category, due_day):
    conn = sqlite3.connect(get_db_path())
    conn.execute(
        '''INSERT INTO recurring_bills
           (user_id, name, amount, category, due_day)
           VALUES (?, ?, ?, ?, ?)''',
        (user_id, name, float(amount), category, int(due_day))
    )
    conn.commit()
    conn.close()

def get_bills(user_id):
    conn = sqlite3.connect(get_db_path())
    df = pd.read_sql_query(
        'SELECT * FROM recurring_bills WHERE user_id=? ORDER BY due_day',
        conn, params=(user_id,)
    )
    conn.close()
    return df

def delete_bill(bill_id, user_id):
    conn = sqlite3.connect(get_db_path())
    conn.execute(
        'DELETE FROM recurring_bills WHERE id=? AND user_id=?',
        (bill_id, user_id)
    )
    conn.commit()
    conn.close()

def show(user_id=1):
    ensure_bills_table()
    currency = st.session_state.get('currency', 'INR')
    symbol = get_symbol(currency)

    st.markdown("""
    <style>
    .page-title { font-size:2rem; font-weight:700; color:var(--text-primary); margin-bottom:0; }
    .page-sub { font-size:1rem; color:var(--text-secondary); margin-bottom:1.5rem; }
    .section-title { font-size:1rem; font-weight:600; color:var(--accent);
                     text-transform:uppercase; letter-spacing:0.08em; margin-bottom:1rem; }
    .budget-card { background:var(--bg-card); border:1px solid var(--border);
                   border-radius:14px; padding:1.2rem 1.5rem; margin-bottom:0.8rem;
                   box-shadow:var(--shadow-sm); }
    .empty-state { background:var(--bg-card); border:1px dashed var(--border);
                   border-radius:16px; padding:3rem; text-align:center; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="page-title">Budgets & Bills</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">Set monthly spending limits and track recurring bills.</p>',
        unsafe_allow_html=True
    )
    st.divider()

    tab_budgets, tab_bills = st.tabs(["Monthly Budgets", "Recurring Bills"])

    # ── TAB 1: BUDGETS ────────────────────────────────────────────────────────
    with tab_budgets:
        current_month = datetime.now().strftime('%Y-%m')
        current_month_display = datetime.now().strftime('%B %Y')

        st.markdown('<p class="section-title">Set Monthly Budget</p>',
                    unsafe_allow_html=True)

        with st.form("budget_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox("Category", CATEGORIES)
            with col2:
                monthly_limit = st.number_input(
                    f"Monthly Limit ({symbol})",
                    min_value=1.0, step=100.0, format="%.0f"
                )
            submitted = st.form_submit_button(
                "Save Budget", use_container_width=True, type="primary"
            )

        if submitted:
            if monthly_limit <= 0:
                st.error("Budget limit must be greater than 0.")
            else:
                set_budget(user_id, category, monthly_limit, current_month)
                st.success(
                    f"Budget set: {format_amount(monthly_limit, currency)} "
                    f"for {category} in {current_month_display}"
                )
                st.rerun()

        st.divider()

        st.markdown(
            f'<p class="section-title">Your Budgets — {current_month_display}</p>',
            unsafe_allow_html=True
        )

        budgets_df = get_budgets(user_id, current_month)
        expenses_df = get_expenses_by_month(user_id, current_month)

        if budgets_df.empty:
            st.markdown("""
            <div class="empty-state">
                <h3 style="color:var(--text-primary);">No budgets set yet</h3>
                <p style="color:var(--text-secondary);">
                    Set a monthly limit for each spending category above.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            total_budget = budgets_df['monthly_limit'].sum()
            total_spent = 0
            if not expenses_df.empty:
                cats = budgets_df['category'].tolist()
                total_spent = expenses_df[
                    expenses_df['category'].isin(cats)
                ]['amount'].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Budgeted",
                        format_amount(total_budget, currency))
            col2.metric("Total Spent",
                        format_amount(total_spent, currency))
            remaining = total_budget - total_spent
            col3.metric(
                "Remaining",
                format_amount(max(remaining, 0), currency),
                delta=f"{format_amount(remaining, currency)}",
                delta_color="normal" if remaining >= 0 else "inverse"
            )

            st.markdown("<br>", unsafe_allow_html=True)

            if 'confirm_delete_budget_id' not in st.session_state:
                st.session_state.confirm_delete_budget_id = None

            for _, budget in budgets_df.iterrows():
                cat = budget['category']
                limit = budget['monthly_limit']
                budget_id = budget['id']

                spent = expenses_df[
                    expenses_df['category'] == cat
                ]['amount'].sum() if not expenses_df.empty else 0

                pct = min(spent / limit, 1.0) if limit > 0 else 0
                remaining_cat = limit - spent

                if pct >= 1.0:
                    bar_color = "#EF4444"
                    status = "OVER BUDGET"
                    status_color = "#EF4444"
                elif pct >= 0.8:
                    bar_color = "#F59E0B"
                    status = "APPROACHING"
                    status_color = "#F59E0B"
                else:
                    bar_color = "#10B981"
                    status = "ON TRACK"
                    status_color = "#10B981"

                # Row: budget card + delete button side by side
                card_col, del_col = st.columns([11, 1])

                with card_col:
                    st.markdown(f"""
                    <div class="budget-card">
                        <div style="display:flex; justify-content:space-between;
                                    align-items:center; margin-bottom:0.8rem;">
                            <span style="font-size:1.1rem; font-weight:700;
                                         color:var(--text-primary);">{cat}</span>
                            <span style="color:{status_color}; font-size:0.8rem;
                                         font-weight:600;">{status}</span>
                        </div>
                        <div style="background:var(--bg-elevated); border-radius:999px;
                                    height:10px;">
                            <div style="background:{bar_color};
                                        width:{pct*100:.1f}%; height:10px;
                                        border-radius:999px;"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between;
                                    margin-top:0.5rem;">
                            <span style="color:var(--text-secondary); font-size:0.82rem;">
                                Spent: <strong style="color:var(--text-primary);">
                                {format_amount(spent, currency)}</strong>
                            </span>
                            <span style="color:var(--text-secondary); font-size:0.82rem;">
                                {pct*100:.0f}% used
                            </span>
                            <span style="color:var(--text-secondary); font-size:0.82rem;">
                                Limit: <strong style="color:var(--text-primary);">
                                {format_amount(limit, currency)}</strong>
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with del_col:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    if st.button("Del", key=f"del_budget_{budget_id}",
                                 help=f"Remove {cat} budget"):
                        if st.session_state.confirm_delete_budget_id == budget_id:
                            st.session_state.confirm_delete_budget_id = None
                        else:
                            st.session_state.confirm_delete_budget_id = budget_id
                        st.rerun()

                # Delete confirmation inline
                if st.session_state.confirm_delete_budget_id == budget_id:
                    st.markdown(f"""
                    <div style='background:var(--danger-dim); border:1px solid var(--danger);
                                border-radius:10px; padding:0.7rem 1rem;
                                margin:0.2rem 0;'>
                        <span style='color:var(--danger); font-weight:600;
                                     font-size:0.85rem;'>
                            Remove {cat} budget
                            ({format_amount(limit, currency)})?
                            This cannot be undone.
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        if st.button(
                            "Yes, Remove",
                            key=f"confirm_budget_{budget_id}",
                            type="secondary",
                            use_container_width=True
                        ):
                            delete_budget(budget_id, user_id)
                            st.session_state.confirm_delete_budget_id = None
                            st.success("Budget removed.")
                            st.rerun()
                    with cc2:
                        if st.button(
                            "Cancel",
                            key=f"cancel_budget_{budget_id}",
                            use_container_width=True
                        ):
                            st.session_state.confirm_delete_budget_id = None
                            st.rerun()

                if pct >= 1.0:
                    st.error(
                        f"You're {format_amount(abs(remaining_cat), currency)} "
                        f"over your {cat} budget!"
                    )
                elif pct >= 0.8:
                    st.warning(
                        f"{cat} budget is {pct*100:.0f}% used. "
                        f"Only {format_amount(remaining_cat, currency)} remaining."
                    )

    # ── TAB 2: RECURRING BILLS ────────────────────────────────────────────────
    with tab_bills:
        today = date.today()

        st.markdown('<p class="section-title">Add Recurring Bill</p>',
                    unsafe_allow_html=True)

        with st.form("bill_form", clear_on_submit=True):
            bc1, bc2, bc3, bc4 = st.columns(4)
            with bc1:
                bill_name = st.text_input(
                    "Bill Name",
                    placeholder="e.g. Netflix, Rent"
                )
            with bc2:
                bill_amount = st.number_input(
                    f"Amount ({symbol})", min_value=0.01,
                    step=100.0, format="%.2f"
                )
            with bc3:
                bill_category = st.selectbox("Category", BILL_CATEGORIES)
            with bc4:
                bill_due_day = st.number_input(
                    "Due Day of Month",
                    min_value=1, max_value=28, value=1, step=1
                )
            bill_submitted = st.form_submit_button(
                "Add Bill", use_container_width=True, type="primary"
            )

        if bill_submitted:
            if not bill_name:
                st.error("Please enter a bill name.")
            elif bill_amount <= 0:
                st.error("Amount must be greater than 0.")
            else:
                add_bill(user_id, bill_name, bill_amount,
                         bill_category, bill_due_day)
                st.success(f"Added: {bill_name}")
                st.rerun()

        st.divider()

        bills_df = get_bills(user_id)

        if bills_df.empty:
            st.markdown("""
            <div class="empty-state">
                <h3 style="color:var(--text-primary);">No recurring bills yet</h3>
                <p style="color:var(--text-secondary);">
                    Add your monthly bills above to track due dates.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            total_bills = bills_df['amount'].sum()

            st.markdown('<p class="section-title">Your Bills</p>',
                        unsafe_allow_html=True)

            sm1, sm2, sm3 = st.columns(3)
            sm1.metric("Total Bills", len(bills_df))
            sm2.metric("Monthly Total",
                       format_amount(total_bills, currency))
            sm3.metric("Annual Total",
                       format_amount(total_bills * 12, currency))

            st.markdown("<br>", unsafe_allow_html=True)

            if 'confirm_delete_bill_id' not in st.session_state:
                st.session_state.confirm_delete_bill_id = None

            # Column headers
            h1, h2, h3, h4, h5 = st.columns([2.5, 1.5, 1.5, 1.5, 0.7])
            h1.markdown("<span style='color:var(--text-secondary);font-size:0.78rem;text-transform:uppercase;'>Bill</span>", unsafe_allow_html=True)
            h2.markdown("<span style='color:var(--text-secondary);font-size:0.78rem;text-transform:uppercase;'>Amount</span>", unsafe_allow_html=True)
            h3.markdown("<span style='color:var(--text-secondary);font-size:0.78rem;text-transform:uppercase;'>Category</span>", unsafe_allow_html=True)
            h4.markdown("<span style='color:var(--text-secondary);font-size:0.78rem;text-transform:uppercase;'>Due</span>", unsafe_allow_html=True)
            h5.markdown("<span style='color:var(--text-secondary);font-size:0.78rem;text-transform:uppercase;'>Del</span>", unsafe_allow_html=True)
            st.markdown(
                "<div style='border-bottom:1px solid var(--border);"
                "margin-bottom:0.5rem;'></div>",
                unsafe_allow_html=True
            )

            for _, bill in bills_df.iterrows():
                bill_id = bill['id']
                due_day = int(bill['due_day'])
                days_until = due_day - today.day
                if days_until < 0:
                    days_until += 30

                if days_until == 0:
                    due_text = "Due TODAY"
                    due_color = "#EF4444"
                elif days_until <= 3:
                    due_text = f"Due in {days_until} day{'s' if days_until > 1 else ''}"
                    due_color = "#EF4444"
                elif days_until <= 7:
                    due_text = f"Due in {days_until} days"
                    due_color = "#F59E0B"
                else:
                    due_text = f"Day {due_day} of month"
                    due_color = "#10B981"

                c1, c2, c3, c4, c5 = st.columns([2.5, 1.5, 1.5, 1.5, 0.7])

                with c1:
                    st.markdown(
                        f"**{bill['name']}**",
                        unsafe_allow_html=True
                    )
                with c2:
                    st.markdown(
                        f"<span style='color:var(--text-primary);font-weight:700;'>"
                        f"{format_amount(bill['amount'], currency)}</span>",
                        unsafe_allow_html=True
                    )
                with c3:
                    st.markdown(
                        f"<span style='color:var(--text-secondary);font-size:0.88rem;'>"
                        f"{bill['category']}</span>",
                        unsafe_allow_html=True
                    )
                with c4:
                    st.markdown(
                        f"<span style='color:{due_color};font-size:0.88rem;"
                        f"font-weight:600;'>{due_text}</span>",
                        unsafe_allow_html=True
                    )
                with c5:
                    if st.button("Del", key=f"del_bill_{bill_id}",
                                 help="Delete bill"):
                        if st.session_state.confirm_delete_bill_id == bill_id:
                            st.session_state.confirm_delete_bill_id = None
                        else:
                            st.session_state.confirm_delete_bill_id = bill_id
                        st.rerun()

                if st.session_state.confirm_delete_bill_id == bill_id:
                    st.markdown(f"""
                    <div style='background:var(--danger-dim); border:1px solid var(--danger);
                                border-radius:10px; padding:0.6rem 1rem;
                                margin:0.2rem 0;'>
                        <span style='color:var(--danger); font-weight:600;
                                     font-size:0.85rem;'>
                            Delete "{bill['name']}"? Cannot be undone.
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        if st.button(
                            "Yes, Delete",
                            key=f"confirm_bill_{bill_id}",
                            type="secondary",
                            use_container_width=True
                        ):
                            delete_bill(bill_id, user_id)
                            st.session_state.confirm_delete_bill_id = None
                            st.success("Bill deleted.")
                            st.rerun()
                    with dc2:
                        if st.button(
                            "Cancel",
                            key=f"cancel_bill_{bill_id}",
                            use_container_width=True
                        ):
                            st.session_state.confirm_delete_bill_id = None
                            st.rerun()

                st.markdown(
                    "<div style='border-bottom:1px solid var(--border);"
                    "margin:0.3rem 0;'></div>",
                    unsafe_allow_html=True
                )
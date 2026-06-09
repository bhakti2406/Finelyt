import streamlit as st
from utils.db import get_all_expenses, delete_expense
from utils.currency import format_amount, get_symbol
import datetime
import pandas as pd
import sqlite3
import os

CATEGORIES = [
    "Food", "Transport", "Shopping", "Utilities",
    "Entertainment", "Health", "Education", "Other"
]

PAYMENT_METHODS = [
    "UPI", "Cash", "Debit Card", "Credit Card",
    "Wallet", "Bank Transfer", "Other"
]

# Text labels replacing emoji icons
PAYMENT_LABELS = {
    "UPI":           "UPI",
    "Cash":          "Cash",
    "Debit Card":    "Debit Card",
    "Credit Card":   "Credit Card",
    "Wallet":        "Wallet",
    "Bank Transfer": "Bank Transfer",
    "Other":         "Other"
}

DB_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'data', 'finance.db'
)

def get_db_path():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', 'data', 'finance.db'
    )

def ensure_payment_method_column():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(expenses)")
    cols = [row[1] for row in cursor.fetchall()]
    if 'payment_method' not in cols:
        cursor.execute(
            "ALTER TABLE expenses ADD COLUMN "
            "payment_method TEXT DEFAULT 'UPI'"
        )
        conn.commit()
    conn.close()

def add_expense_full(date, category, amount, notes,
                     payment_method, user_id):
    conn = sqlite3.connect(get_db_path())
    conn.execute(
        '''INSERT INTO expenses
           (date, category, amount, notes,
            payment_method, user_id)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (str(date), category, float(amount),
         notes, payment_method, user_id)
    )
    conn.commit()
    conn.close()

def update_expense(expense_id, category, amount,
                   notes, payment_method, user_id):
    conn = sqlite3.connect(get_db_path())
    conn.execute(
        '''UPDATE expenses
           SET category=?, amount=?, notes=?,
               payment_method=?
           WHERE id=? AND user_id=?''',
        (category, float(amount), notes,
         payment_method, expense_id, user_id)
    )
    conn.commit()
    conn.close()

def show(user_id=1):
    ensure_payment_method_column()
    currency = st.session_state.get('currency', 'INR')
    symbol   = get_symbol(currency)

    st.markdown("""
    <style>
    .insight-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        transition: var(--transition);
        box-shadow: var(--shadow-sm);
    }
    .insight-card:hover {
        border-color: var(--border-light);
        background: var(--bg-card-hover);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    .insight-label {
        font-size: 0.72rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .insight-value {
        font-size: 1.4rem;
        font-weight: 800;
        color: var(--text-primary);
        font-family: var(--font-mono);
        letter-spacing: -0.02em;
    }
    .insight-sub {
        font-size: 0.78rem;
        color: var(--text-secondary);
        margin-top: 2px;
    }
    .pm-badge {
        display: inline-flex;
        align-items: center;
        background: var(--bg-elevated);
        border: 1px solid var(--border-light);
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.78rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="page-title">Add Expense</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">Record your spending '
        'and track every transaction.</p>',
        unsafe_allow_html=True)
    st.divider()

    df    = get_all_expenses(user_id)
    today = datetime.date.today()

    if not df.empty:
        df['date']          = pd.to_datetime(df['date'])
        df_today            = df[df['date'].dt.date == today]
        spent_today         = df_today['amount'].sum()
        transactions_today  = len(df_today)
    else:
        spent_today        = 0
        transactions_today = 0
        df_today           = pd.DataFrame()

    # ── TODAY SUMMARY ─────────────────────────────────────────────────────────
    st.markdown(
        "<p class='section-title'>Today's Summary</p>",
        unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">Spent Today</div>
            <div class="insight-value">
                {format_amount(spent_today, currency)}
            </div>
            <div class="insight-sub">
                {today.strftime('%d %B %Y')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">Transactions Today</div>
            <div class="insight-value">{transactions_today}</div>
            <div class="insight-sub">entries recorded</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        if not df.empty:
            daily_avg  = df.groupby(
                df['date'].dt.date)['amount'].sum().mean()
            diff       = spent_today - daily_avg
            diff_text  = (
                f"{format_amount(abs(diff), currency)} "
                f"{'above' if diff > 0 else 'below'} average"
            )
            diff_color = (
                "#EF4444" if diff > 0 else "#10B981"
            )
        else:
            daily_avg  = 0
            diff_text  = "No history yet"
            diff_color = "#94A3B8"

        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">Daily Average</div>
            <div class="insight-value">
                {format_amount(daily_avg, currency)}
            </div>
            <div class="insight-sub"
                 style="color:{diff_color};">
                {diff_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── NEW EXPENSE FORM ──────────────────────────────────────────────────────
    st.markdown(
        "<p class='section-title'>New Expense</p>",
        unsafe_allow_html=True)

    col_cat, col_pm = st.columns(2)
    with col_cat:
        category = st.selectbox("Category", CATEGORIES)
    with col_pm:
        payment_method = st.selectbox(
            "Payment Method", PAYMENT_METHODS)

    # Category insights
    if not df.empty and category:
        cat_data = df[df['category'] == category]
        if not cat_data.empty:
            cat_avg   = cat_data['amount'].mean()
            cat_total = cat_data['amount'].sum()
            cat_count = len(cat_data)
            cat_today = (
                df_today[
                    df_today['category'] == category
                ]['amount'].sum()
                if not df_today.empty else 0
            )

            col_a, col_b, col_c = st.columns(3)
            col_a.markdown(f"""
            <div class="insight-card">
                <div class="insight-label">
                    Avg per transaction
                </div>
                <div class="insight-value"
                     style="font-size:1.1rem;">
                    {format_amount(cat_avg, currency)}
                </div>
                <div class="insight-sub">for {category}</div>
            </div>
            """, unsafe_allow_html=True)

            col_b.markdown(f"""
            <div class="insight-card">
                <div class="insight-label">
                    {category} today
                </div>
                <div class="insight-value"
                     style="font-size:1.1rem;
                      color:{'#EF4444' if cat_today > cat_avg
                            else '#10B981'};">
                    {format_amount(cat_today, currency)}
                </div>
                <div class="insight-sub">
                    {cat_count} past transactions
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_c.markdown(f"""
            <div class="insight-card">
                <div class="insight-label">
                    All-time {category}
                </div>
                <div class="insight-value"
                     style="font-size:1.1rem;">
                    {format_amount(cat_total, currency)}
                </div>
                <div class="insight-sub">total spent</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input(
                f"Amount ({symbol})",
                min_value=0.01, step=10.0, format="%.2f"
            )
        with col2:
            exp_date = st.date_input("Date", value=today)
        notes = st.text_input(
            "Notes (optional)",
            placeholder="e.g. Lunch with friends"
        )
        submitted = st.form_submit_button(
            "Save Expense",
            use_container_width=True, type="primary"
        )

    if submitted:
        if amount <= 0:
            st.error("Amount must be greater than 0.")
        else:
            add_expense_full(
                exp_date, category, amount,
                notes, payment_method, user_id
            )
            from utils.db import clear_cache
            clear_cache()
            st.success(
                f"Saved {format_amount(amount, currency)} "
                f"for {category} via {payment_method} "
                f"on {exp_date}"
            )
            st.rerun()

    st.divider()

    # ── RECENT EXPENSES ───────────────────────────────────────────────────────
    st.markdown(
        "<p class='section-title'>Recent Expenses</p>",
        unsafe_allow_html=True)

    df_fresh = get_all_expenses(user_id)

    # Show edit success notification if set by the edit form
    if st.session_state.get('_edit_success'):
        st.success(st.session_state.pop('_edit_success'))

    if df_fresh.empty:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;
                    background:var(--bg-card);
                    border:1px dashed var(--border);
                    border-radius:16px;">
            <p style="color:var(--text-secondary);font-size:0.95rem;margin:0;">
                No expenses yet. Add your first expense above.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    if 'editing_expense_id' not in st.session_state:
        st.session_state.editing_expense_id = None
    if 'confirm_delete_id' not in st.session_state:
        st.session_state.confirm_delete_id = None

    # Column headers
    h1,h2,h3,h4,h5,h6 = st.columns(
        [2.5, 1.5, 1.5, 1.5, 0.7, 0.7])
    for col, lbl in zip(
        [h1,h2,h3,h4,h5,h6],
        ['Transaction','Amount','Payment','Notes','','']
    ):
        col.markdown(
            f"<span style='color:var(--text-muted);font-size:0.7rem;"
            f"font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.08em;'>{lbl}</span>",
            unsafe_allow_html=True)

    st.markdown(
        "<div style='border-bottom:1px solid var(--border);"
        "margin-bottom:0.5rem;'></div>",
        unsafe_allow_html=True)

    for _, row in df_fresh.head(25).iterrows():
        expense_id = row['id']
        pm         = row.get('payment_method', 'UPI') or 'UPI'
        date_str   = str(row['date'])[:10]

        c1,c2,c3,c4,c5,c6 = st.columns(
            [2.5, 1.5, 1.5, 1.5, 0.7, 0.7])

        with c1:
            st.markdown(
                f"<span style='color:#F0F4FF;"
                f"font-weight:600;'>{row['category']}</span>"
                f"<br><span style='color:#8892AA;"
                f"font-size:0.78rem;'>{date_str}</span>",
                unsafe_allow_html=True)

        with c2:
            st.markdown(
                f"<span style='font-weight:700;"
                f"color:#F0F4FF;font-family:\"DM Mono\","
                f"monospace;'>"
                f"{format_amount(row['amount'], currency)}"
                f"</span>",
                unsafe_allow_html=True)

        with c3:
            st.markdown(
                f"<span class='pm-badge'>{pm}</span>",
                unsafe_allow_html=True)

        with c4:
            st.markdown(
                f"<span style='color:#8892AA;"
                f"font-size:0.85rem;'>"
                f"{row['notes'] or '—'}</span>",
                unsafe_allow_html=True)

        with c5:
            if st.button("Edit",
                         key=f"edit_{expense_id}",
                         use_container_width=True):
                if st.session_state.editing_expense_id \
                        == expense_id:
                    st.session_state.editing_expense_id \
                        = None
                else:
                    st.session_state.editing_expense_id \
                        = expense_id
                    st.session_state.confirm_delete_id \
                        = None
                st.rerun()

        with c6:
            if st.button("Del",
                         key=f"del_{expense_id}",
                         use_container_width=True):
                if st.session_state.confirm_delete_id \
                        == expense_id:
                    st.session_state.confirm_delete_id \
                        = None
                else:
                    st.session_state.confirm_delete_id \
                        = expense_id
                    st.session_state.editing_expense_id \
                        = None
                st.rerun()

        # Inline edit form
        if st.session_state.editing_expense_id == expense_id:
            with st.form(f"edit_form_{expense_id}"):
                st.markdown(
                    "<p style='color:#00C896;font-weight:600;"
                    "font-size:0.85rem;margin-bottom:0.5rem;'>"
                    "Edit Expense</p>",
                    unsafe_allow_html=True)
                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    new_cat = st.selectbox(
                        "Category", CATEGORIES,
                        index=CATEGORIES.index(row['category'])
                        if row['category'] in CATEGORIES
                        else 0,
                        key=f"ecat_{expense_id}"
                    )
                with ec2:
                    new_amt = st.number_input(
                        f"Amount ({symbol})",
                        value=float(row['amount']),
                        min_value=0.01, step=10.0,
                        format="%.2f",
                        key=f"eamt_{expense_id}"
                    )
                with ec3:
                    curr_pm = (
                        row.get('payment_method', 'UPI')
                        or 'UPI'
                    )
                    pm_idx = (
                        PAYMENT_METHODS.index(curr_pm)
                        if curr_pm in PAYMENT_METHODS else 0
                    )
                    new_pm = st.selectbox(
                        "Payment Method",
                        PAYMENT_METHODS,
                        index=pm_idx,
                        key=f"epm_{expense_id}"
                    )
                new_notes = st.text_input(
                    "Notes",
                    value=row['notes'] or '',
                    key=f"enotes_{expense_id}"
                )
                sv, ca = st.columns(2)
                with sv:
                    save_btn = st.form_submit_button(
                        "Save Changes",
                        use_container_width=True,
                        type="primary"
                    )
                with ca:
                    cancel_btn = st.form_submit_button(
                        "Cancel",
                        use_container_width=True
                    )

                # ── Must be inside the form block so Streamlit
                #    can correctly read form_submit_button values
                if save_btn:
                    update_expense(
                        expense_id, new_cat, new_amt,
                        new_notes, new_pm, user_id
                    )
                    from utils.db import clear_cache
                    clear_cache()
                    st.session_state.editing_expense_id = None
                    st.session_state['_edit_success'] = (
                        f"✓ {new_cat} updated to "
                        f"{format_amount(new_amt, currency)}"
                    )
                    st.rerun()
                if cancel_btn:
                    st.session_state.editing_expense_id = None
                    st.rerun()

        # Delete confirmation
        if st.session_state.confirm_delete_id == expense_id:
            st.markdown(f"""
            <div style='background:var(--danger-dim);
                        border:1px solid var(--danger);
                        border-radius:10px;
                        padding:0.7rem 1rem;
                        margin:0.2rem 0;'>
                <span style='color:var(--danger);
                             font-weight:600;
                             font-size:0.88rem;'>
                    Delete {row['category']} —
                    {format_amount(row['amount'], currency)}?
                    This cannot be undone.
                </span>
            </div>
            """, unsafe_allow_html=True)
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button(
                    "Yes, Delete",
                    key=f"confirm_{expense_id}",
                    type="secondary",
                    use_container_width=True
                ):
                    delete_expense(expense_id, user_id)
                    st.session_state.confirm_delete_id = None
                    st.success("Deleted.")
                    st.rerun()
            with cc2:
                if st.button(
                    "Cancel",
                    key=f"cancel_del_{expense_id}",
                    use_container_width=True
                ):
                    st.session_state.confirm_delete_id = None
                    st.rerun()

        st.markdown(
            "<div style='border-bottom:1px solid var(--border);"
            "margin:0.3rem 0;'></div>",
            unsafe_allow_html=True)

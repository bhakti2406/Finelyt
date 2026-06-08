import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import date, datetime, timedelta
from utils.currency import format_amount, get_symbol
import calendar

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'data', 'finance.db'
)

# ── DB HELPERS ────────────────────────────────────────────────────────────────

def init_bill_payments_table():
    """
    Ensures bill_payments table exists and that recurring_bills
    has the status / paid_on columns (safe to run every startup).
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Payment history table
    c.execute("""
        CREATE TABLE IF NOT EXISTS bill_payments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            bill_id     INTEGER NOT NULL,
            bill_name   TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            paid_on     TEXT    NOT NULL,
            month_key   TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


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


def get_bill_payments(user_id, month_key):
    """Returns all payments for a given user + month (format: YYYY-MM)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT * FROM bill_payments WHERE user_id=? AND month_key=?",
            conn, params=(user_id, month_key)
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


def mark_bill_paid(user_id, bill_id, bill_name, amount, month_key):
    """Records a payment. Idempotent — silently ignores duplicate for same month."""
    conn = sqlite3.connect(DB_PATH)
    # Check if already paid this month
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM bill_payments WHERE user_id=? AND bill_id=? AND month_key=?",
        (user_id, bill_id, month_key)
    )
    if cur.fetchone() is None:
        paid_on = date.today().strftime('%Y-%m-%d')
        conn.execute(
            "INSERT INTO bill_payments (user_id,bill_id,bill_name,amount,paid_on,month_key) "
            "VALUES (?,?,?,?,?,?)",
            (user_id, bill_id, bill_name, float(amount), paid_on, month_key)
        )
        conn.commit()
    conn.close()


def unmark_bill_paid(user_id, bill_id, month_key):
    """Removes a payment record (undo mark as paid)."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "DELETE FROM bill_payments WHERE user_id=? AND bill_id=? AND month_key=?",
        (user_id, bill_id, month_key)
    )
    conn.commit()
    conn.close()


def get_all_expenses(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT * FROM expenses WHERE user_id=? ORDER BY date DESC",
            conn, params=(user_id,)
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


# ── PAGE ──────────────────────────────────────────────────────────────────────

def show(user_id=1):
    init_bill_payments_table()

    currency = st.session_state.get('currency', 'INR')
    symbol   = get_symbol(currency)
    today    = date.today()

    st.markdown("""
    <style>
    .slbl     { font-size:.75rem; font-weight:700;
                color:var(--accent); text-transform:uppercase;
                letter-spacing:.1em; margin-bottom:.6rem; }
    .kpi-card { background:var(--bg-card); border:1px solid var(--border);
                border-radius:12px; padding:1rem 1.2rem;
                text-align:center; }
    .kpi-lbl  { font-size:.75rem; color:var(--text-muted);
                text-transform:uppercase; letter-spacing:.06em; }
    .kpi-val  { font-size:1.5rem; font-weight:800;
                color:var(--text-primary); margin-top:4px; }
    .bill-row { background:var(--bg-card); border:1px solid var(--border);
                border-radius:10px; padding:.8rem 1rem;
                margin-bottom:.4rem; }
    .day-cell {
        border-radius:10px;
        padding:6px 4px;
        min-height:80px;
        border:1px solid var(--border);
        background:var(--bg-card);
        font-size:.75rem;
    }
    .day-today { border:2px solid var(--info) !important;
                 background:var(--info-dim) !important; }
    .day-has-bill { border-color:rgba(239, 68, 68, 0.3) !important;
                    background:rgba(239, 68, 68, 0.05) !important; }
    .day-due-soon { border-color:var(--warning) !important;
                    background:var(--warning-dim) !important; }
    .day-past     { opacity:.5; }
    .badge-overdue {
        background:var(--danger-dim); border:1px solid var(--danger);
        color:var(--danger); border-radius:999px;
        padding:2px 10px; font-size:.7rem; font-weight:700;
    }
    .badge-soon {
        background:var(--warning-dim); border:1px solid var(--warning);
        color:var(--warning); border-radius:999px;
        padding:2px 10px; font-size:.7rem; font-weight:700;
    }
    .badge-ok {
        background:var(--accent-dim); border:1px solid var(--accent);
        color:var(--accent); border-radius:999px;
        padding:2px 10px; font-size:.7rem; font-weight:700;
    }
    .badge-paid {
        background:rgba(16,185,129,0.15); border:1px solid #10B981;
        color:#10B981; border-radius:999px;
        padding:2px 10px; font-size:.7rem; font-weight:700;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="fc-page-title">Bill Payment Calendar</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="fc-page-sub">Track, manage and mark your recurring bills as paid.</p>',
        unsafe_allow_html=True)
    st.divider()

    bills_df = get_recurring_bills(user_id)

    if bills_df.empty:
        st.markdown("""
        <div class="fc-empty">
            <h3 class="fc-empty-title">No recurring bills yet</h3>
            <p class="fc-empty-sub">
                Go to <strong>Budgets &rarr; Recurring Bills</strong> to add your monthly bills first.
            </p>
        </div>""", unsafe_allow_html=True)
        return

    # ── MONTH NAVIGATION ──────────────────────────────────────────────────────
    if 'cal_year'  not in st.session_state:
        st.session_state.cal_year  = today.year
    if 'cal_month' not in st.session_state:
        st.session_state.cal_month = today.month

    nav1, nav2, nav3 = st.columns([1, 3, 1])
    with nav1:
        if st.button("← Prev", use_container_width=True):
            if st.session_state.cal_month == 1:
                st.session_state.cal_month = 12
                st.session_state.cal_year -= 1
            else:
                st.session_state.cal_month -= 1
            st.rerun()
    with nav2:
        cur_year  = st.session_state.cal_year
        cur_month = st.session_state.cal_month
        month_label = date(cur_year, cur_month, 1).strftime('%B %Y')
        st.markdown(
            f"<h3 style='text-align:center;color:#FFF;margin:0'>{month_label}</h3>",
            unsafe_allow_html=True)
    with nav3:
        if st.button("Next →", use_container_width=True):
            if st.session_state.cal_month == 12:
                st.session_state.cal_month = 1
                st.session_state.cal_year += 1
            else:
                st.session_state.cal_month += 1
            st.rerun()

    if st.button("Today", use_container_width=False):
        st.session_state.cal_year  = today.year
        st.session_state.cal_month = today.month
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Current month key for payment tracking (YYYY-MM)
    month_key = f"{cur_year}-{cur_month:02d}"

    # Load payments for this month
    payments_df = get_bill_payments(user_id, month_key)
    paid_bill_ids = set(payments_df['bill_id'].tolist()) if not payments_df.empty else set()

    # Build bill schedule for calendar grid
    bill_by_day = {}
    for _, bill in bills_df.iterrows():
        due_day    = int(bill['due_day'])
        max_day    = calendar.monthrange(cur_year, cur_month)[1]
        actual_day = min(due_day, max_day)
        if actual_day not in bill_by_day:
            bill_by_day[actual_day] = []
        bill_by_day[actual_day].append(bill)

    # ── SUMMARY KPIs ──────────────────────────────────────────────────────────
    st.markdown('<p class="slbl">This Month Summary</p>', unsafe_allow_html=True)

    total_bills  = float(bills_df['amount'].sum())
    bills_count  = len(bills_df)
    paid_count   = len(paid_bill_ids)
    paid_amount  = float(payments_df['amount'].sum()) if not payments_df.empty else 0.0
    unpaid_amount = total_bills - paid_amount

    due_soon = []
    overdue  = []
    upcoming = []
    if cur_year == today.year and cur_month == today.month:
        for day, day_bills in bill_by_day.items():
            bill_date = date(cur_year, cur_month, day)
            days_diff = (bill_date - today).days
            for b in day_bills:
                if int(b['id']) in paid_bill_ids:
                    continue  # already paid — skip from alerts
                if days_diff < 0:
                    overdue.append((day, b, abs(days_diff)))
                elif days_diff <= 7:
                    due_soon.append((day, b, days_diff))
                else:
                    upcoming.append((day, b, days_diff))

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">Total Bills</div>
        <div class="kpi-val">{bills_count}</div>
    </div>""", unsafe_allow_html=True)

    k2.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">Monthly Total</div>
        <div class="kpi-val" style="font-size:1.1rem;color:var(--danger)">
            {format_amount(total_bills, currency)}
        </div>
    </div>""", unsafe_allow_html=True)

    k3.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">Paid</div>
        <div class="kpi-val" style="color:#10B981">
            {paid_count}
        </div>
    </div>""", unsafe_allow_html=True)

    k4.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">Due Soon</div>
        <div class="kpi-val" style="color:var(--warning)">
            {len(due_soon)}
        </div>
    </div>""", unsafe_allow_html=True)

    k5.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">Overdue</div>
        <div class="kpi-val" style="color:var(--danger)">
            {len(overdue)}
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ALERTS (unpaid only) ───────────────────────────────────────────────────
    for day, bill, days_ago in overdue:
        st.error(
            f"⚠ {bill['name']} — "
            f"{format_amount(bill['amount'], currency)} "
            f"was due {days_ago} day{'s' if days_ago>1 else ''} ago (Day {day})"
        )
    for day, bill, days_left in due_soon:
        label = "Due TODAY" if days_left == 0 else (
            "Due TOMORROW" if days_left == 1 else f"Due in {days_left} days")
        st.warning(
            f"🔔 {bill['name']} — "
            f"{format_amount(bill['amount'], currency)} · {label} (Day {day})"
        )

    st.divider()

    # ── CALENDAR GRID ─────────────────────────────────────────────────────────
    st.markdown('<p class="slbl">Calendar</p>', unsafe_allow_html=True)

    cal_grid  = calendar.monthcalendar(cur_year, cur_month)
    day_names = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

    hcols = st.columns(7)
    for col, dn in zip(hcols, day_names):
        col.markdown(
            f"<div style='text-align:center;color:var(--text-muted);"
            f"font-size:.78rem;font-weight:700;"
            f"padding:6px 0;border-bottom:1px solid var(--border)'>"
            f"{dn}</div>",
            unsafe_allow_html=True)

    for week in cal_grid:
        week_cols = st.columns(7)
        for col, day_num in zip(week_cols, week):
            if day_num == 0:
                col.markdown("<div style='min-height:80px'></div>",
                             unsafe_allow_html=True)
                continue

            day_bills = bill_by_day.get(day_num, [])
            this_date = date(cur_year, cur_month, day_num)
            is_today  = this_date == today
            is_past   = this_date < today

            if is_today:
                border, bg = "var(--info)", "var(--info-dim)"
                num_color  = "var(--info)"
            elif day_bills and not is_past:
                days_away = (this_date - today).days
                if days_away <= 3:
                    border, bg = "var(--danger)", "rgba(239,68,68,0.05)"
                    num_color  = "var(--danger)"
                elif days_away <= 7:
                    border, bg = "var(--warning)", "var(--warning-dim)"
                    num_color  = "var(--warning)"
                else:
                    border, bg = "var(--border)", "var(--bg-card)"
                    num_color  = "var(--text-primary)"
            elif day_bills and is_past:
                border, bg = "var(--border)", "var(--bg-base)"
                num_color  = "var(--text-muted)"
            else:
                border, bg = "var(--border)", "var(--bg-card)"
                num_color  = "var(--text-muted)" if is_past else "var(--text-primary)"

            bill_html = ""
            for b in day_bills[:2]:
                amt      = format_amount(b['amount'], currency)
                name     = b['name'][:10] + ('…' if len(b['name']) > 10 else '')
                is_paid  = int(b['id']) in paid_bill_ids
                if is_paid:
                    bill_color = "#10B981"
                elif is_past:
                    bill_color = "var(--text-muted)"
                elif (this_date - today).days <= 3:
                    bill_color = "var(--danger)"
                elif (this_date - today).days <= 7:
                    bill_color = "var(--warning)"
                else:
                    bill_color = "var(--accent)"

                paid_tick = " ✓" if is_paid else ""
                bill_html += (
                    f"<div style='background:{bill_color}22;"
                    f"border-radius:4px;padding:1px 4px;"
                    f"margin-top:2px;white-space:nowrap;"
                    f"overflow:hidden;text-overflow:ellipsis;"
                    f"color:{bill_color};font-size:.65rem;"
                    f"font-weight:600'>"
                    f"{name}{paid_tick} {amt}"
                    f"</div>"
                )
            if len(day_bills) > 2:
                bill_html += (
                    f"<div style='color:var(--text-muted);"
                    f"font-size:.62rem;margin-top:1px'>"
                    f"+{len(day_bills)-2} more</div>"
                )

            today_dot = (
                "<div style='width:6px;height:6px;"
                "background:var(--info);border-radius:50%;"
                "margin:0 auto 2px'></div>"
                if is_today else ""
            )

            col.markdown(
                f"<div style='border:1px solid {border};"
                f"border-radius:10px;padding:6px 4px;"
                f"min-height:80px;background:{bg}'>"
                f"{today_dot}"
                f"<div style='text-align:right;"
                f"color:{num_color};"
                f"font-weight:{'700' if is_today else '500'};"
                f"font-size:.82rem;margin-bottom:2px'>"
                f"{day_num}</div>"
                f"{bill_html}"
                f"</div>",
                unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── BILL LIST WITH MARK AS PAID ───────────────────────────────────────────
    st.markdown('<p class="slbl">All Bills This Month</p>',
                unsafe_allow_html=True)

    # Filter tabs
    filter_tab_all, filter_tab_pending, filter_tab_paid, filter_tab_overdue = st.tabs([
        "All", "Pending", "Paid", "Overdue"
    ])

    def render_bill_list(bills_iter, tab_name):
        """Renders a filtered list of bills with Mark as Paid / Undo buttons."""
        rendered = 0
        for _, bill in bills_iter:
            bill_id    = int(bill['id'])
            due_day    = int(bill['due_day'])
            max_day    = calendar.monthrange(cur_year, cur_month)[1]
            actual_day = min(due_day, max_day)
            bill_date  = date(cur_year, cur_month, actual_day)
            days_diff  = (bill_date - today).days
            is_paid    = bill_id in paid_bill_ids

            paid_on_str = ""
            if is_paid and not payments_df.empty:
                pay_row = payments_df[payments_df['bill_id'] == bill_id]
                if not pay_row.empty:
                    paid_on_str = pay_row.iloc[0]['paid_on']

            if is_paid:
                status      = "Paid"
                badge_class = "badge-paid"
            elif cur_year == today.year and cur_month == today.month:
                if days_diff < 0:
                    status      = "Overdue"
                    badge_class = "badge-overdue"
                elif days_diff == 0:
                    status      = "Due Today"
                    badge_class = "badge-overdue"
                elif days_diff <= 7:
                    status      = f"Due in {days_diff}d"
                    badge_class = "badge-soon"
                else:
                    status      = f"Day {actual_day}"
                    badge_class = "badge-ok"
            else:
                status      = f"Day {actual_day}"
                badge_class = "badge-ok"

            bc1, bc2, bc3, bc4, bc5 = st.columns([2.5, 1.8, 1.5, 1.2, 1.5])

            bc1.markdown(
                f"<span style='color:#FFF;font-weight:600'>{bill['name']}</span>"
                f"<br><span style='color:var(--text-muted);font-size:.8rem'>"
                f"{bill['category']}</span>",
                unsafe_allow_html=True)

            bc2.markdown(
                f"<span style='color:var(--danger);font-weight:700;font-size:1rem'>"
                f"{format_amount(bill['amount'], currency)}</span>",
                unsafe_allow_html=True)

            bc3.markdown(
                f"<span style='color:var(--text-muted);font-size:.85rem'>"
                f"Due day {actual_day}</span>"
                + (f"<br><span style='color:#10B981;font-size:.75rem'>Paid: {paid_on_str}</span>"
                   if paid_on_str else ""),
                unsafe_allow_html=True)

            bc4.markdown(
                f"<span class='{badge_class}'>{status}</span>",
                unsafe_allow_html=True)

            with bc5:
                if is_paid:
                    if st.button("↩ Undo",
                                 key=f"undo_{tab_name}_{bill_id}_{month_key}",
                                 use_container_width=True):
                        unmark_bill_paid(user_id, bill_id, month_key)
                        st.rerun()
                else:
                    if st.button("✓ Mark Paid",
                                 key=f"pay_{tab_name}_{bill_id}_{month_key}",
                                 use_container_width=True, type="primary"):
                        mark_bill_paid(user_id, bill_id, bill['name'],
                                       bill['amount'], month_key)
                        st.rerun()

            st.markdown(
                "<div style='border-bottom:1px solid var(--border);margin:.3rem 0'></div>",
                unsafe_allow_html=True)
            rendered += 1

        if rendered == 0:
            st.markdown(
                "<p style='color:var(--text-muted);font-size:.9rem;"
                "text-align:center;padding:1rem 0'>No bills in this category.</p>",
                unsafe_allow_html=True)

    sorted_bills = bills_df.sort_values('due_day')

    with filter_tab_all:
        render_bill_list(sorted_bills.iterrows(), "all")

    with filter_tab_pending:
        pending = sorted_bills[~sorted_bills['id'].astype(int).isin(paid_bill_ids)]
        render_bill_list(pending.iterrows(), "pending")

    with filter_tab_paid:
        paid_bills = sorted_bills[sorted_bills['id'].astype(int).isin(paid_bill_ids)]
        render_bill_list(paid_bills.iterrows(), "paid")

    with filter_tab_overdue:
        overdue_ids = {int(b['id']) for _, b in sorted_bills.iterrows()
                       if int(b['id']) not in paid_bill_ids
                       and cur_year == today.year
                       and cur_month == today.month
                       and (date(cur_year, cur_month,
                                 min(int(b['due_day']),
                                     calendar.monthrange(cur_year, cur_month)[1]))
                            - today).days < 0}
        overdue_df = sorted_bills[sorted_bills['id'].astype(int).isin(overdue_ids)]
        render_bill_list(overdue_df.iterrows(), "overdue")

    st.divider()

    # ── PAYMENT HISTORY ───────────────────────────────────────────────────────
    st.markdown('<p class="slbl">Payment History</p>',
                unsafe_allow_html=True)

    # Show last 3 months of payment history
    history_rows = []
    for offset in range(0, 3):
        m = today.month - offset
        y = today.year
        if m <= 0:
            m += 12
            y -= 1
        mk  = f"{y}-{m:02d}"
        p_df = get_bill_payments(user_id, mk)
        if not p_df.empty:
            for _, pr in p_df.iterrows():
                history_rows.append({
                    'Month':    date(y, m, 1).strftime('%B %Y'),
                    'Bill':     pr['bill_name'],
                    'Amount':   format_amount(pr['amount'], currency),
                    'Paid On':  pr['paid_on'],
                })

    if history_rows:
        st.dataframe(
            pd.DataFrame(history_rows),
            use_container_width=True,
            hide_index=True)
    else:
        st.markdown(
            "<p style='color:var(--text-muted);font-size:.9rem'>No payment history yet.</p>",
            unsafe_allow_html=True)

    st.divider()

    # ── UPCOMING 3 MONTHS ─────────────────────────────────────────────────────
    st.markdown('<p class="slbl">Next 3 Months Outlook</p>',
                unsafe_allow_html=True)

    rows = []
    for offset in range(1, 4):
        m = today.month + offset
        y = today.year
        if m > 12:
            m -= 12
            y += 1
        rows.append({
            'Month':     date(y, m, 1).strftime('%B %Y'),
            'Bills':     len(bills_df),
            'Total Due': format_amount(float(bills_df['amount'].sum()), currency),
        })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True)
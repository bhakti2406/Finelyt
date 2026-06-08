import streamlit as st
import sqlite3
import os
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from datetime import date, datetime
import plotly.graph_objects as go

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

def money(v, cur='INR'):
    sym = {'INR':'₹','USD':'$','EUR':'€',
           'GBP':'£','OMR':'OMR ','AED':'AED '}
    return f"{sym.get(cur, cur+' ')}{D(v)}"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS saving_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        target TEXT NOT NULL,
        saved TEXT NOT NULL DEFAULT '0.00',
        currency TEXT NOT NULL DEFAULT 'INR',
        deadline TEXT DEFAULT '',
        category TEXT DEFAULT 'General',
        icon TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now'))
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS saving_deposits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        amount TEXT NOT NULL,
        note TEXT DEFAULT '',
        dep_date TEXT NOT NULL DEFAULT '',
        created_at TEXT DEFAULT (datetime('now'))
    )""")
    conn.commit()
    conn.close()

def add_goal(user_id, name, target, currency, deadline, category, icon):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO saving_goals (user_id,name,target,saved,currency,deadline,category,icon) VALUES (?,?,?,?,?,?,?,?)",
        (user_id, name, str(target), '0.00', currency, str(deadline), category, icon)
    )
    conn.commit()
    conn.close()

def get_goals(user_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM saving_goals WHERE user_id=? ORDER BY created_at DESC",
        conn, params=(user_id,)
    )
    conn.close()
    return df

def add_deposit(goal_id, user_id, amount, note, dep_date):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO saving_deposits (goal_id,user_id,amount,note,dep_date) VALUES (?,?,?,?,?)",
        (goal_id, user_id, str(amount), note, str(dep_date))
    )
    conn.execute(
        "UPDATE saving_goals SET saved = CAST(ROUND(CAST(saved AS REAL) + ?, 2) AS TEXT) WHERE id=? AND user_id=?",
        (float(amount), goal_id, user_id)
    )
    conn.commit()
    conn.close()

def get_deposits(goal_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM saving_deposits WHERE goal_id=? ORDER BY created_at DESC",
        conn, params=(goal_id,)
    )
    conn.close()
    return df

def delete_goal(goal_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM saving_deposits WHERE goal_id=?", (goal_id,))
    conn.execute("DELETE FROM saving_goals WHERE id=? AND user_id=?", (goal_id, user_id))
    conn.commit()
    conn.close()

def delete_deposit(dep_id, goal_id, user_id, amount):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM saving_deposits WHERE id=?", (dep_id,))
    conn.execute(
        "UPDATE saving_goals SET saved = CAST(ROUND(MAX(CAST(saved AS REAL) - ?, 0), 2) AS TEXT) WHERE id=? AND user_id=?",
        (float(amount), goal_id, user_id)
    )
    conn.commit()
    conn.close()

CATEGORIES = [
    "Emergency Fund", "Vacation", "Home", "Car",
    "Education", "Wedding", "Gadget",
    "Investment", "Retirement", "Other"
]
ICONS = {
    "Emergency Fund": "", "Vacation": "",
    "Home": "", "Car": "", "Education": "",
    "Wedding": "", "Gadget": "",
    "Investment": "", "Retirement": "", "Other": "",
}

def show(user_id=1):
    init_db()
    currency   = st.session_state.get('currency', 'INR')
    CURRENCIES = ['INR','OMR','USD','EUR','GBP','AED']

    st.markdown("""
    <style>
    .slbl{font-size:.75rem;font-weight:700;color:var(--accent);
          text-transform:uppercase;letter-spacing:.1em;margin-bottom:.6rem}
    .kpi-card{background:var(--bg-card);border:1px solid var(--border);
              border-radius:12px;padding:1rem 1.2rem;text-align:center}
    .kpi-lbl{font-size:.75rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.06em}
    .kpi-val{font-size:1.5rem;font-weight:800;color:var(--text-primary);margin-top:4px}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="fc-page-title">Savings Goals</p>', unsafe_allow_html=True)
    st.markdown('<p class="fc-page-sub">Set goals, add deposits, track progress.</p>', unsafe_allow_html=True)
    st.divider()

    goals_df = get_goals(user_id)

    # ── OVERVIEW ──────────────────────────────────────────────────────────────
    if not goals_df.empty:
        total_target = sum(D(r['target']) for _, r in goals_df.iterrows())
        total_saved  = sum(D(r['saved'])  for _, r in goals_df.iterrows())
        completed    = sum(1 for _, r in goals_df.iterrows() if D(r['saved']) >= D(r['target']))
        overall_pct  = float(total_saved / total_target * 100) if total_target > 0 else 0

        st.markdown('<p class="slbl">Overview</p>', unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        k1.markdown(f'<div class="kpi-card"><div class="kpi-lbl">Goals</div><div class="kpi-val">{len(goals_df)}</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="kpi-card"><div class="kpi-lbl">Total Target</div><div class="kpi-val" style="font-size:1.1rem">{money(total_target,currency)}</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="kpi-card"><div class="kpi-lbl">Total Saved</div><div class="kpi-val" style="color:var(--accent);font-size:1.1rem">{money(total_saved,currency)}</div></div>', unsafe_allow_html=True)
        k4.markdown(f'<div class="kpi-card"><div class="kpi-lbl">Completed</div><div class="kpi-val" style="color:var(--warning)">{completed}/{len(goals_df)}</div></div>', unsafe_allow_html=True)

        bar_color = "var(--accent)" if overall_pct >= 100 else "var(--info)"
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:var(--text-secondary);font-size:.85rem;margin-bottom:4px'>Overall Progress — {overall_pct:.1f}%</p>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#0F1117;border-radius:999px;height:10px;margin-bottom:1.5rem">
          <div style="background:{bar_color};width:{min(overall_pct,100):.1f}%;height:10px;border-radius:999px"></div>
        </div>""", unsafe_allow_html=True)
        st.divider()

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["My Goals", "New Goal"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — MY GOALS
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        goals_df = get_goals(user_id)

        if goals_df.empty:
            st.markdown("""
            <div class="fc-empty">
              <h3 class="fc-empty-title">No goals yet</h3>
              <p class="fc-empty-sub">Create your first savings goal in the New Goal tab.</p>
            </div>""", unsafe_allow_html=True)
        else:
            if 'del_goal' not in st.session_state:
                st.session_state.del_goal = None
            if 'dep_goal' not in st.session_state:
                st.session_state.dep_goal = None
            if 'del_dep' not in st.session_state:
                st.session_state.del_dep = None

            for _, g in goals_df.iterrows():
                gid    = g['id']
                target = D(g['target'])
                saved  = D(g['saved'])
                cur    = g.get('currency', currency) or currency
                pct    = float(saved / target * 100) if target > 0 else 0.0
                remain = max(target - saved, D(0))
                dl     = g.get('deadline','') or ''

                # Status badge — use st components not HTML badges
                if saved >= target:
                    status_color = "var(--accent)"
                    status_text  = "Complete"
                    bar_c        = "var(--accent)"
                elif dl and dl < str(date.today()):
                    status_color = "var(--danger)"
                    status_text  = "Overdue"
                    bar_c        = "var(--danger)"
                else:
                    status_color = "var(--info)"
                    status_text  = "In Progress"
                    bar_c        = "var(--info)"

                # Days left
                days_info = ""
                if dl and saved < target:
                    try:
                        dd = datetime.strptime(dl, '%Y-%m-%d').date()
                        days = (dd - date.today()).days
                        if days > 0:
                            days_info = f"{days} days left"
                        elif days == 0:
                            days_info = "Due today"
                        else:
                            days_info = f"{abs(days)} days overdue"
                    except Exception:
                        pass

                # Monthly needed
                monthly_tip = ""
                if dl and saved < target:
                    try:
                        dd = datetime.strptime(dl, '%Y-%m-%d').date()
                        months = max(
                            (dd.year - date.today().year) * 12
                            + dd.month - date.today().month, 1)
                        needed = (remain / months).quantize(
                            Decimal('0.01'), rounding=ROUND_HALF_UP)
                        monthly_tip = (
                            f"Save {money(needed,cur)}/month "
                            f"to reach goal on time")
                    except Exception:
                        pass

                # ── Goal header row ───────────────────────────────────────────
                hc1, hc2 = st.columns([11, 1])

                with hc1:
                    # Title row
                    title_col, status_col = st.columns([7, 3])
                    with title_col:
                        st.markdown(
                            f"<span style='color:#FFF;font-weight:700;"
                            f"font-size:1.05rem'>{g['name']}</span>"
                            f"&nbsp;&nbsp;"
                            f"<span style='color:#8B8FA8;font-size:.8rem'>"
                            f"{g.get('category','')} "
                            f"{'· ' + dl if dl else ''} "
                            f"{'· ' + days_info if days_info else ''}"
                            f"</span>",
                            unsafe_allow_html=True
                        )
                    with status_col:
                        st.markdown(
                            f"<div style='text-align:right'>"
                            f"<span style='background:{status_color}22;"
                            f"border:1px solid {status_color};"
                            f"color:{status_color};"
                            f"border-radius:999px;"
                            f"padding:3px 12px;"
                            f"font-size:.72rem;"
                            f"font-weight:700'>"
                            f"{status_text}"
                            f"</span></div>",
                            unsafe_allow_html=True
                        )

                    # Amounts
                    st.markdown(
                        f"<div style='display:flex;"
                        f"justify-content:space-between;"
                        f"margin:8px 0 6px'>"
                        f"<span style='color:var(--accent);"
                        f"font-weight:700;font-size:1.1rem'>"
                        f"{money(saved,cur)}</span>"
                        f"<span style='color:#8B8FA8;font-size:.85rem'>"
                        f"of {money(target,cur)} target</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    # Progress bar
                    st.markdown(
                        f"<div style='background:#0F1117;"
                        f"border-radius:999px;height:10px;"
                        f"margin-bottom:6px'>"
                        f"<div style='background:{bar_c};"
                        f"width:{min(pct,100):.1f}%;"
                        f"height:10px;border-radius:999px'>"
                        f"</div></div>",
                        unsafe_allow_html=True
                    )

                    # Stats row
                    st.markdown(
                        f"<div style='display:flex;"
                        f"justify-content:space-between;"
                        f"margin-bottom:4px'>"
                        f"<span style='color:#8B8FA8;font-size:.78rem'>"
                        f"{pct:.1f}% saved</span>"
                        f"<span style='color:#8B8FA8;font-size:.78rem'>"
                        f"{money(remain,cur)} remaining</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    if monthly_tip:
                        st.markdown(
                            f"<p style='color:var(--warning);font-size:.78rem;"
                            f"margin:2px 0 0'>{monthly_tip}</p>",
                            unsafe_allow_html=True
                        )

                with hc2:
                    if st.button("Del", key=f"dg_{gid}",
                                 help="Delete goal"):
                        st.session_state.del_goal = (
                            None if st.session_state.del_goal == gid
                            else gid)
                        st.rerun()

                # Delete confirmation
                if st.session_state.del_goal == gid:
                    st.markdown(
                        f"<div style='background:#1A0D0D;"
                        f"border:1px solid #FF4B4B;"
                        f"border-radius:10px;"
                        f"padding:.7rem 1rem;margin:.3rem 0'>"
                        f"<span style='color:#FF4B4B;font-weight:600'>"
                        f"Delete \"{g['name']}\" and all deposits? "
                        f"Cannot be undone.</span></div>",
                        unsafe_allow_html=True
                    )
                    da, db = st.columns(2)
                    with da:
                        if st.button("Yes, Delete",
                                     key=f"dgok_{gid}",
                                     type="secondary",
                                     use_container_width=True):
                            delete_goal(gid, user_id)
                            st.session_state.del_goal = None
                            st.rerun()
                    with db:
                        if st.button("Cancel",
                                     key=f"dgno_{gid}",
                                     use_container_width=True):
                            st.session_state.del_goal = None
                            st.rerun()

                # Add money button
                dep_open = st.session_state.dep_goal == gid
                if st.button(
                    "Close" if dep_open else "Add Money",
                    key=f"adddep_{gid}"
                ):
                    st.session_state.dep_goal = (
                        None if dep_open else gid)
                    st.rerun()

                # Deposit form
                if st.session_state.dep_goal == gid:
                    with st.form(f"dep_{gid}",
                                 clear_on_submit=True):
                        fa, fb, fc = st.columns(3)
                        with fa:
                            dep_amt = st.text_input(
                                "Amount *",
                                placeholder="e.g. 500")
                        with fb:
                            dep_date = st.date_input(
                                "Date", value=date.today(),
                                key=f"dd_{gid}")
                        with fc:
                            dep_note = st.text_input(
                                "Note (optional)",
                                placeholder="e.g. Salary")
                        dep_sub = st.form_submit_button(
                            "Add Deposit",
                            use_container_width=True,
                            type="primary")

                    if dep_sub:
                        try:
                            amt = D(dep_amt.strip())
                            if amt <= 0:
                                st.error("Amount must be > 0.")
                            else:
                                add_deposit(
                                    gid, user_id, amt,
                                    dep_note, dep_date)
                                new_saved = saved + amt
                                if new_saved >= target:
                                    st.success(
                                        f"Goal complete! "
                                        f"{g['name']} reached!")
                                else:
                                    st.success(
                                        f"Added {money(amt,cur)} "
                                        f"to {g['name']}!")
                                st.session_state.dep_goal = None
                                st.rerun()
                        except Exception:
                            st.error("Invalid amount.")

                # Deposit history
                deposits = get_deposits(gid)
                if not deposits.empty:
                    with st.expander(
                        f"Deposit History "
                        f"({len(deposits)} entries)"
                    ):
                        for _, dep in deposits.iterrows():
                            did = dep['id']
                            dc1, dc2, dc3, dc4 = st.columns(
                                [2, 2, 3, 0.7])
                            dc1.markdown(
                                f"<span style='color:#FFF;"
                                f"font-weight:600'>"
                                f"{money(D(dep['amount']),cur)}"
                                f"</span>",
                                unsafe_allow_html=True)
                            dc2.markdown(
                                f"<span style='color:#8B8FA8;"
                                f"font-size:.85rem'>"
                                f"{dep.get('dep_date','')}"
                                f"</span>",
                                unsafe_allow_html=True)
                            dc3.markdown(
                                f"<span style='color:#8B8FA8;"
                                f"font-size:.85rem'>"
                                f"{dep.get('note','') or '—'}"
                                f"</span>",
                                unsafe_allow_html=True)
                            with dc4:
                                if st.button(
                                    "Del", key=f"dd_{did}"):
                                    st.session_state.del_dep = (
                                        None if
                                        st.session_state.del_dep
                                        == did else did)
                                    st.rerun()

                            if st.session_state.del_dep == did:
                                if st.button(
                                    "Confirm Remove",
                                    key=f"ddok_{did}",
                                    type="secondary",
                                    use_container_width=True):
                                    delete_deposit(
                                        did, gid, user_id,
                                        D(dep['amount']))
                                    st.session_state.del_dep\
                                        = None
                                    st.rerun()

                            st.markdown(
                                "<div style='border-bottom:"
                                "1px solid #1A1D27;"
                                "margin:.2rem 0'></div>",
                                unsafe_allow_html=True)

                # Progress chart
                deposits_all = get_deposits(gid)
                if len(deposits_all) >= 2:
                    with st.expander("Progress Chart"):
                        dep_sorted = deposits_all\
                            .sort_values('dep_date')
                        cumulative = []
                        running = D(0)
                        for _, d in dep_sorted.iterrows():
                            running += D(d['amount'])
                            cumulative.append(float(running))

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=dep_sorted['dep_date'].tolist(),
                            y=cumulative,
                            mode='lines+markers',
                            line=dict(color='#10B981', width=2),
                            marker=dict(color='#10B981', size=6),
                            fill='tozeroy',
                            fillcolor='rgba(16,185,129,0.1)',
                        ))
                        fig.add_hline(
                            y=float(target),
                            line_dash="dash",
                            line_color="#F59E0B",
                            annotation_text="Target",
                            annotation_font_color="#F59E0B"
                        )
                        fig.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#FFF',
                            height=250,
                            margin=dict(t=20,b=20,l=20,r=20),
                            xaxis=dict(
                                gridcolor='#1E293B',
                                color='#94A3B8',
                                type='category'),
                            yaxis=dict(
                                gridcolor='#1E293B',
                                color='#94A3B8'),
                            showlegend=False
                        )
                        st.plotly_chart(
                            fig, use_container_width=True)

                st.divider()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — NEW GOAL
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown(
            '<p class="slbl">Create a New Savings Goal</p>',
            unsafe_allow_html=True)

        ng1, ng2, ng3 = st.columns(3)
        with ng1:
            g_name = st.text_input(
                "Goal Name *",
                placeholder="e.g. Emergency Fund, Goa Trip")
        with ng2:
            g_target = st.text_input(
                "Target Amount *",
                placeholder="e.g. 50000")
        with ng3:
            g_cur = st.selectbox(
                "Currency", CURRENCIES,
                index=CURRENCIES.index(currency)
                if currency in CURRENCIES else 0)

        ng4, ng5 = st.columns(2)
        with ng4:
            g_cat = st.selectbox("Category", CATEGORIES)
        with ng5:
            g_deadline = st.date_input(
                "Target Date (optional)",
                value=None,
                help="Leave empty for no deadline")

        g_icon = ICONS.get(g_cat, '')
        st.markdown(
            f"<p style='color:#8B8FA8;font-size:.85rem;"
            f"margin-top:.5rem'>"
            f"Goal category: "
            f"<span style='color:var(--accent)'>{g_cat}</span></p>",
            unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Create Goal", type="primary",
                     use_container_width=True):
            errors = []
            if not g_name.strip():
                errors.append("Goal name is required.")
            target = D(0)
            try:
                target = D(g_target.strip())
                if target <= 0:
                    errors.append(
                        "Target must be greater than 0.")
            except Exception:
                errors.append(
                    "Invalid amount.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                dl_str = str(g_deadline) if g_deadline else ''
                add_goal(user_id, g_name.strip(), target,
                         g_cur, dl_str, g_cat, g_icon)
                st.success(
                    f"Goal created: "
                    f"**{g_name.strip()}** — "
                    f"{money(target, g_cur)}")
                st.info(
                    "Go to My Goals tab to add deposits "
                    "and track progress.")
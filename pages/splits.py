import streamlit as st
import sqlite3
import os
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from datetime import date

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

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
    s = {'INR':'₹','USD':'$','EUR':'€','GBP':'£',
         'OMR':'OMR ','AED':'AED '}.get(cur, cur+' ')
    return f"{s}{D(v)}"

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE  – completely fresh schema, no migration needed
# ─────────────────────────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ── splits ────────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS sp_splits (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            title      TEXT    NOT NULL,
            total      TEXT    NOT NULL,
            currency   TEXT    NOT NULL DEFAULT 'INR',
            bdate      TEXT    NOT NULL DEFAULT '',
            notes      TEXT             DEFAULT '',
            method     TEXT    NOT NULL DEFAULT 'equal',
            created_at TEXT             DEFAULT (datetime('now'))
        )""")

    # ── members ───────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS sp_members (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            split_id INTEGER NOT NULL,
            name     TEXT    NOT NULL,
            share    TEXT    NOT NULL,
            paid     INTEGER NOT NULL DEFAULT 0
        )""")

    # ── payments ──────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS sp_payments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            payer      TEXT    NOT NULL,
            receiver   TEXT    NOT NULL,
            amount     TEXT    NOT NULL,
            currency   TEXT    NOT NULL DEFAULT 'INR',
            method     TEXT    NOT NULL DEFAULT 'Cash',
            pdate      TEXT    NOT NULL DEFAULT '',
            notes      TEXT             DEFAULT '',
            created_at TEXT             DEFAULT (datetime('now'))
        )""")

    conn.commit()
    conn.close()

def db_add_split(user_id, title, total, cur, bdate,
                 notes, method, members):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO sp_splits "
        "(user_id,title,total,currency,bdate,notes,method) "
        "VALUES (?,?,?,?,?,?,?)",
        (user_id, title, str(total), cur,
         str(bdate), notes, method))
    sid = c.lastrowid
    for name, share in members:
        c.execute(
            "INSERT INTO sp_members "
            "(split_id,name,share,paid) VALUES (?,?,?,?)",
            (sid, name, str(share), 1 if name == 'You' else 0))
    conn.commit()
    conn.close()

def db_splits(user_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM sp_splits WHERE user_id=? "
        "ORDER BY created_at DESC",
        conn, params=(user_id,))
    conn.close()
    return df

def db_members(split_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM sp_members WHERE split_id=?",
        conn, params=(split_id,))
    conn.close()
    return df

def db_toggle(mid, cur_paid):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE sp_members SET paid=? WHERE id=?",
                 (0 if cur_paid else 1, mid))
    conn.commit()
    conn.close()

def db_del_split(sid, user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM sp_members WHERE split_id=?", (sid,))
    conn.execute(
        "DELETE FROM sp_splits WHERE id=? AND user_id=?",
        (sid, user_id))
    conn.commit()
    conn.close()

def db_add_payment(user_id, payer, receiver, amount,
                   cur, method, pdate, notes):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO sp_payments "
        "(user_id,payer,receiver,amount,currency,method,pdate,notes) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (user_id, payer, receiver, str(amount),
         cur, method, str(pdate), notes))
    conn.commit()
    conn.close()

def db_payments(user_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM sp_payments WHERE user_id=? "
        "ORDER BY created_at DESC",
        conn, params=(user_id,))
    conn.close()
    return df

def db_del_payment(pid, user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "DELETE FROM sp_payments WHERE id=? AND user_id=?",
        (pid, user_id))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# SPLIT CALCULATORS
# ─────────────────────────────────────────────────────────────────────────────

def parse_lines(text):
    """Parse 'Name: Value' lines → list of (name, Decimal)."""
    result = []
    for i, raw in enumerate(text.strip().splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if ':' not in line:
            raise ValueError(
                f"Line {i}: use format  Name: Value  "
                f"(got '{line}')")
        name, val_str = line.split(':', 1)
        name    = name.strip()
        val_str = val_str.strip().rstrip('%')
        if not name:
            raise ValueError(f"Line {i}: name is empty")
        if not val_str:
            raise ValueError(
                f"Line {i}: value missing for '{name}'")
        try:
            val = D(val_str)
        except Exception:
            raise ValueError(
                f"Line {i}: '{val_str}' is not a number")
        result.append((name, val))
    return result

def calc_equal(total, people):
    if not people:
        return None, "Add at least one person."
    n     = len(people)
    share = (total / n).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP)
    # give rounding remainder to first person
    diff  = total - share * n
    out   = []
    for i, p in enumerate(people):
        out.append((p, share + diff if i == 0 else share))
    return out, None

def calc_exact(total, text):
    try:
        pairs = parse_lines(text)
    except ValueError as e:
        return None, str(e)
    if not pairs:
        return None, "Enter at least one person and amount."
    got  = sum(p[1] for p in pairs)
    diff = abs(got - total)
    if diff > Decimal('0.10'):
        return None, (
            f"Your amounts add up to {money(got)} "
            f"but the bill is {money(total)}. "
            f"Difference: {money(diff)}. "
            f"They must match (within ±0.10).")
    return pairs, None

def calc_pct(total, text):
    try:
        pairs = parse_lines(text)
    except ValueError as e:
        return None, str(e)
    if not pairs:
        return None, "Enter at least one person and percentage."
    total_pct = sum(p[1] for p in pairs)
    if abs(total_pct - Decimal('100')) > Decimal('0.5'):
        return None, (
            f"Percentages add up to {total_pct}% "
            f"— they must equal 100%.")
    out = [(n, (total * pct / 100).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP))
           for n, pct in pairs]
    # fix rounding
    diff = total - sum(o[1] for o in out)
    if diff and out:
        out[0] = (out[0][0], out[0][1] + diff)
    return out, None

def calc_shares(total, text):
    try:
        pairs = parse_lines(text)
    except ValueError as e:
        return None, str(e)
    if not pairs:
        return None, "Enter at least one person and shares."
    ts = sum(p[1] for p in pairs)
    if ts <= 0:
        return None, "Shares must be greater than 0."
    out = [(n, (total * sh / ts).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP))
           for n, sh in pairs]
    diff = total - sum(o[1] for o in out)
    if diff and out:
        out[0] = (out[0][0], out[0][1] + diff)
    return out, None

# ─────────────────────────────────────────────────────────────────────────────
# BALANCE ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def balances(splits_df, payments_df):
    bal = {}
    for _, sp in splits_df.iterrows():
        cur = sp.get('currency', 'INR') or 'INR'
        for _, m in db_members(sp['id']).iterrows():
            if m['name'] == 'You':
                continue
            n = m['name']
            if n not in bal:
                bal[n] = {'owed': D(0), 'paid': D(0),
                          'currency': cur}
            bal[n]['owed'] += D(m['share'])
            if bool(m['paid']):
                bal[n]['paid'] += D(m['share'])

    if not payments_df.empty:
        for _, p in payments_df.iterrows():
            a = D(p['amount'])
            if p['receiver'] == 'You' and p['payer'] in bal:
                bal[p['payer']]['paid'] += a
            elif p['payer'] == 'You' and p['receiver'] in bal:
                bal[p['receiver']]['owed'] -= a

    for n in bal:
        bal[n]['net'] = bal[n]['owed'] - bal[n]['paid']
    return bal

# ─────────────────────────────────────────────────────────────────────────────
# PAGE
# ─────────────────────────────────────────────────────────────────────────────

def show(user_id=1):
    init_db()

    cur_sym    = st.session_state.get('currency', 'INR')
    CURRENCIES = ['INR', 'OMR', 'USD', 'EUR', 'GBP', 'AED']

    st.markdown("""<style>
    .slbl{font-size:.75rem;font-weight:700;color:var(--accent);
          text-transform:uppercase;letter-spacing:.1em;margin-bottom:.5rem}
    .hint{background:var(--accent-dim);border-left:3px solid var(--accent);
          border-radius:0 var(--radius-sm) var(--radius-sm) 0;padding:.5rem .8rem;
          color:var(--text-secondary);font-size:.82rem;margin:.4rem 0 .9rem}
    .steplbl{color:var(--text-primary);font-weight:600;font-size:.95rem;
             margin:1rem 0 .4rem}
    .tblh{color:var(--text-muted);font-size:.72rem;font-weight:700;
          text-transform:uppercase;letter-spacing:.07em}
    .bp{background:var(--accent-dim);border:1px solid var(--accent);color:var(--accent);
        border-radius:var(--radius-full);padding:2px 12px;font-size:.72rem;
        font-weight:700}
    .bu{background:var(--danger-dim);border:1px solid var(--danger);color:var(--danger);
        border-radius:var(--radius-full);padding:2px 12px;font-size:.72rem;
        font-weight:700}
    .bm{background:var(--info-dim);border:1px solid var(--info);color:var(--info);
        border-radius:var(--radius-full);padding:2px 10px;font-size:.72rem;
        font-weight:600}
    .delbox{background:var(--danger-dim);border:1px solid var(--danger);
            border-radius:var(--radius-md);padding:.7rem 1rem;margin:.3rem 0}
    .rowdiv{border-bottom:1px solid var(--border);margin:.25rem 0}
    </style>""", unsafe_allow_html=True)

    st.markdown('<p class="fc-page-title">Expense Sharing</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="fc-page-sub">Split bills · Track balances · '
        'Record payments</p>',
        unsafe_allow_html=True)
    st.divider()

    sdf  = db_splits(user_id)
    pdf  = db_payments(user_id)
    bal  = balances(sdf, pdf)

    # ── BALANCE OVERVIEW ──────────────────────────────────────────────────────
    if bal:
        st.markdown('<p class="slbl">Cumulative Balances</p>',
                    unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#8B8FA8;font-size:.82rem;"
            "margin:-.3rem 0 .8rem'>"
            "Total each person owes you across all splits.</p>",
            unsafe_allow_html=True)

        outstanding = sum(max(d['net'], D(0)) for d in bal.values())
        settled     = sum(min(d['paid'], d['owed'])
                          for d in bal.values())
        k1, k2, k3 = st.columns(3)
        k1.metric("People",      len(bal))
        k2.metric("Outstanding", money(outstanding, cur_sym))
        k3.metric("Settled",     money(settled, cur_sym))
        st.markdown("<br>", unsafe_allow_html=True)

        h1, h2, h3, h4 = st.columns([3, 2, 2, 2])
        for c, l in zip([h1,h2,h3,h4],
                        ['Person','Total Owed',
                         'Paid Back','Still Owes']):
            c.markdown(f"<span class='tblh'>{l}</span>",
                       unsafe_allow_html=True)
        st.markdown(
            "<div style='border-bottom:1px solid var(--border);"
            "margin-bottom:.4rem'></div>",
            unsafe_allow_html=True)

        for name, d in sorted(bal.items()):
            c = d.get('currency', cur_sym) or cur_sym
            c1,c2,c3,c4 = st.columns([3,2,2,2])
            c1.markdown(
                f"<span style='color:#FFF;font-weight:600'>"
                f"{name}</span>",
                unsafe_allow_html=True)
            c2.markdown(
                f"<span style='color:#FFF'>"
                f"{money(d['owed'],c)}</span>",
                unsafe_allow_html=True)
            c3.markdown(
                f"<span style='color:var(--accent)'>"
                f"{money(d['paid'],c)}</span>",
                unsafe_allow_html=True)
            if d['net'] <= 0:
                c4.markdown(
                    "<span style='color:var(--accent);"
                    "font-weight:700'>Settled</span>",
                    unsafe_allow_html=True)
            else:
                c4.markdown(
                    f"<span style='color:var(--danger);"
                    f"font-weight:700'>"
                    f"{money(d['net'],c)}</span>",
                    unsafe_allow_html=True)
            st.markdown("<div class='rowdiv'></div>",
                        unsafe_allow_html=True)
        st.divider()

    # ── TABS ──────────────────────────────────────────────────────────────────
    t1, t2, t3, t4 = st.tabs([
        "New Split", "All Splits",
        "Record Payment", "Payment History"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 – NEW SPLIT
    # ══════════════════════════════════════════════════════════════════════════
    with t1:
        st.markdown('<p class="slbl">Create a New Split</p>',
                    unsafe_allow_html=True)

        # Step 1 – Bill details
        st.markdown('<p class="steplbl">Step 1 — Bill Details</p>',
                    unsafe_allow_html=True)
        ca, cb, cc = st.columns(3)
        with ca:
            s_title = st.text_input(
                "Bill Title *",
                placeholder="Dinner, Goa Trip, Rent…")
        with cb:
            s_total = st.text_input(
                "Total Amount *",
                placeholder="e.g. 1200.00")
        with cc:
            s_cur = st.selectbox(
                "Currency", CURRENCIES,
                index=CURRENCIES.index(cur_sym)
                if cur_sym in CURRENCIES else 0)

        cd, ce = st.columns(2)
        with cd:
            s_date = st.date_input("Date", value=date.today())
        with ce:
            s_notes = st.text_input(
                "Notes (optional)",
                placeholder="e.g. Team lunch")

        # Step 2 – Method
        st.markdown('<p class="steplbl">Step 2 — Split Method</p>',
                    unsafe_allow_html=True)
        method = st.radio(
            "m", ["Equal Split", "Exact Amount",
                  "Percentage", "Share-Based"],
            horizontal=True, label_visibility="collapsed")

        hints = {
            "Equal Split": (
                "Splits the total equally among everyone. "
                "Example: ₹1200 ÷ 3 = ₹400 each. "
                "Just enter names below."),
            "Exact Amount": (
                "Enter the exact amount each person pays. "
                "They must add up to the total. "
                "Format → Name: Amount"),
            "Percentage": (
                "Enter each person's percentage. "
                "Must total exactly 100%. "
                "Format → Name: Percentage"),
            "Share-Based": (
                "Enter share weights (any positive number). "
                "Example — You:2, Alice:1 means You pays ⅔ "
                "and Alice pays ⅓. "
                "Format → Name: Shares"),
        }
        st.markdown(
            f"<div class='hint'>{hints[method]}</div>",
            unsafe_allow_html=True)

        # Step 3 – People / values
        st.markdown(
            '<p class="steplbl">Step 3 — People & Amounts</p>',
            unsafe_allow_html=True)

        s_people = s_extra = ""

        if method == "Equal Split":
            st.markdown(
                "<p style='color:#8B8FA8;font-size:.85rem;"
                "margin-bottom:4px'>One name per line "
                "(You added automatically):</p>",
                unsafe_allow_html=True)
            s_people = st.text_area(
                "names",
                placeholder="Alice\nBob\nCharlie",
                height=110, label_visibility="collapsed")
        else:
            ph = {
                "Exact Amount":
                    "You: 400.00\nAlice: 400.00\nBob: 400.00",
                "Percentage":
                    "You: 33.34\nAlice: 33.33\nBob: 33.33",
                "Share-Based":
                    "You: 2\nAlice: 1\nBob: 1",
            }
            lb = {
                "Exact Amount":
                    "Name: Amount for each person",
                "Percentage":
                    "Name: Percentage (must total 100%)",
                "Share-Based":
                    "Name: Number of shares",
            }
            st.markdown(
                f"<p style='color:#8B8FA8;font-size:.85rem;"
                f"margin-bottom:4px'>{lb[method]}:</p>",
                unsafe_allow_html=True)
            s_extra = st.text_area(
                "vals", placeholder=ph[method],
                height=130, label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Create Split", type="primary",
                     use_container_width=True,
                     key="btn_create"):

            # ── Validate ──────────────────────────────────────────────────────
            errors = []
            if not s_title.strip():
                errors.append("Bill title is required.")

            total = D(0)
            try:
                total = D(s_total.strip())
                if total <= 0:
                    errors.append(
                        "Total amount must be greater than 0.")
            except Exception:
                errors.append(
                    "Invalid amount — use numbers like "
                    "1200 or 1200.50")

            if errors:
                for e in errors:
                    st.error(e)
                st.stop()

            # ── Calculate members ─────────────────────────────────────────────
            members = None
            errmsg  = None

            if method == "Equal Split":
                names = [
                    n.strip()
                    for n in s_people.replace(
                        ',', '\n').splitlines()
                    if n.strip()]
                if not names:
                    errmsg = (
                        "Add at least one person to "
                        "split with.")
                else:
                    if 'You' not in names:
                        names = ['You'] + names
                    members, errmsg = calc_equal(total, names)

            elif method == "Exact Amount":
                if not s_extra.strip():
                    errmsg = (
                        "Enter amounts. "
                        "Format: Name: Amount")
                else:
                    members, errmsg = calc_exact(
                        total, s_extra)

            elif method == "Percentage":
                if not s_extra.strip():
                    errmsg = (
                        "Enter percentages. "
                        "Format: Name: Percentage")
                else:
                    members, errmsg = calc_pct(
                        total, s_extra)

            elif method == "Share-Based":
                if not s_extra.strip():
                    errmsg = (
                        "Enter shares. "
                        "Format: Name: Shares")
                else:
                    members, errmsg = calc_shares(
                        total, s_extra)

            if errmsg:
                st.error(errmsg)
                st.stop()

            if not members:
                st.error(
                    "Could not calculate amounts. "
                    "Check inputs and try again.")
                st.stop()

            # ── Save ──────────────────────────────────────────────────────────
            db_add_split(
                user_id, s_title.strip(), total, s_cur,
                s_date, s_notes.strip(), method, members)

            st.success(
                f"Split created: **{s_title.strip()}**")

            # Preview table
            st.dataframe(
                pd.DataFrame({
                    'Person': [m[0] for m in members],
                    'Amount': [money(m[1], s_cur)
                               for m in members],
                    'Status': [
                        'PAID (you paid the bill)'
                        if m[0] == 'You' else 'UNPAID'
                        for m in members],
                }),
                use_container_width=True, hide_index=True)
            st.info(
                "Go to All Splits to manage payments.")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 – ALL SPLITS
    # ══════════════════════════════════════════════════════════════════════════
    with t2:
        sdf2 = db_splits(user_id)

        if sdf2.empty:
            st.markdown("""
            <div class="fc-empty">
              <h3 class="fc-empty-title">No splits yet</h3>
              <p class="fc-empty-sub">
                Create your first split in the New Split tab.
              </p>
            </div>""", unsafe_allow_html=True)
        else:
            tv = sum(D(r['total']) for _, r in sdf2.iterrows())
            x1, x2 = st.columns(2)
            x1.metric("Total Splits", len(sdf2))
            x2.metric("Total Value", money(tv, cur_sym))
            st.markdown("<br>", unsafe_allow_html=True)

            if 'del_sp' not in st.session_state:
                st.session_state.del_sp = None

            for _, sp in sdf2.iterrows():
                sid   = sp['id']
                spc   = sp.get('currency', cur_sym) or cur_sym
                spm   = sp.get('method', 'equal') or 'equal'
                spd   = sp.get('bdate', '') or ''
                spn   = sp.get('notes', '') or ''
                spt   = D(sp['total'])
                mems  = db_members(sid)

                paid_t = (
                    sum(D(m['share'])
                        for _, m in mems.iterrows()
                        if bool(m['paid']))
                    if not mems.empty else D(0))
                unp_t = spt - paid_t
                pct   = (float(paid_t / spt * 100)
                         if spt > 0 else 0.0)
                bc    = "var(--accent)" if pct >= 100 else "var(--warning)"

                hh1, hh2 = st.columns([11, 1])
                with hh1:
                    ml = spm.replace('-', ' ').title()
                    np_ = f" · {spn}" if spn else ""
                    st.markdown(f"""
                    <div style='display:flex;
                        justify-content:space-between;
                        align-items:center;margin-bottom:5px'>
                      <div>
                        <span style='color:#FFF;font-weight:700;
                            font-size:1rem'>{sp['title']}</span>
                        <span style='color:#8B8FA8;font-size:.8rem;
                            margin-left:8px'>{spd}</span>
                        <span class='bm'
                            style='margin-left:8px'>{ml}</span>
                        <span style='color:#8B8FA8;font-size:.78rem;
                            margin-left:6px'>{np_}</span>
                      </div>
                      <span style='color:#FFF;font-weight:700'>
                        {money(spt, spc)}</span>
                    </div>
                    <div style='background:#0F1117;
                        border-radius:999px;height:5px;
                        margin-bottom:4px'>
                      <div style='background:{bc};
                           width:{min(pct,100):.1f}%;
                           height:5px;border-radius:999px'>
                      </div>
                    </div>
                    <div style='display:flex;
                        justify-content:space-between;
                        margin-bottom:8px'>
                      <span style='color:#8B8FA8;font-size:.74rem'>
                        Paid:
                        <strong style='color:var(--accent)'>
                          {money(paid_t,spc)}</strong>
                      </span>
                      <span style='color:#8B8FA8;font-size:.74rem'>
                        {pct:.0f}% settled</span>
                      <span style='color:#8B8FA8;font-size:.74rem'>
                        Outstanding:
                        <strong style='color:var(--warning)'>
                          {money(unp_t,spc)}</strong>
                      </span>
                    </div>
                    """, unsafe_allow_html=True)

                with hh2:
                    if st.button("Del", key=f"db_{sid}"):
                        st.session_state.del_sp = (
                            None if st.session_state.del_sp == sid
                            else sid)
                        st.rerun()

                if st.session_state.del_sp == sid:
                    st.markdown(
                        f"<div class='delbox'>"
                        f"<span style='color:var(--danger);"
                        f"font-weight:600'>"
                        f"Delete \"{sp['title']}\"? "
                        f"Cannot be undone.</span></div>",
                        unsafe_allow_html=True)
                    da, db_ = st.columns(2)
                    with da:
                        if st.button("Yes, Delete",
                                     key=f"dok_{sid}",
                                     type="secondary",
                                     use_container_width=True):
                            db_del_split(sid, user_id)
                            st.session_state.del_sp = None
                            st.rerun()
                    with db_:
                        if st.button("Cancel",
                                     key=f"dno_{sid}",
                                     use_container_width=True):
                            st.session_state.del_sp = None
                            st.rerun()

                # Members
                if not mems.empty:
                    mh1,mh2,mh3,mh4 = st.columns([3,2,1.8,1.8])
                    for col, l in zip(
                        [mh1,mh2,mh3,mh4],
                        ['Person','Share','Status','Action']):
                        col.markdown(
                            f"<span class='tblh'>{l}</span>",
                            unsafe_allow_html=True)

                    for _, m in mems.iterrows():
                        mid    = m['id']
                        ipaid  = bool(m['paid'])
                        iyou   = m['name'] == 'You'
                        share  = D(m['share'])

                        mc1,mc2,mc3,mc4 = st.columns(
                            [3,2,1.8,1.8])
                        clr = "var(--accent)" if iyou else "#FFF"
                        mc1.markdown(
                            f"<span style='color:{clr};"
                            f"font-weight:500'>"
                            f"{m['name']}"
                            f"{' (You)' if iyou else ''}"
                            f"</span>",
                            unsafe_allow_html=True)
                        mc2.markdown(
                            f"<span style='color:#FFF;"
                            f"font-weight:700'>"
                            f"{money(share,spc)}</span>",
                            unsafe_allow_html=True)
                        bdg = ("<span class='bp'>PAID</span>"
                               if ipaid else
                               "<span class='bu'>UNPAID</span>")
                        mc3.markdown(bdg,
                                     unsafe_allow_html=True)
                        with mc4:
                            if not iyou:
                                 bl = ("Unmark"
                                       if ipaid else "Mark Paid")
                                 if st.button(
                                     bl, key=f"mp_{mid}",
                                     use_container_width=True):
                                    db_toggle(mid, ipaid)
                                    st.rerun()

                with st.expander("Export CSV"):
                    rows = [
                        {'Person': m['name'],
                         'Amount': str(D(m['share'])),
                         'Currency': spc,
                         'Status': ('Paid' if m['paid']
                                    else 'Unpaid')}
                        for _, m in mems.iterrows()]
                    st.download_button(
                        "Download",
                        pd.DataFrame(rows).to_csv(index=False),
                        file_name=f"{sp['title']}_split.csv",
                        mime="text/csv",
                        key=f"ex_{sid}")

                st.divider()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 – RECORD PAYMENT
    # ══════════════════════════════════════════════════════════════════════════
    with t3:
        st.markdown('<p class="slbl">Record a Payment</p>',
                    unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#8B8FA8;font-size:.85rem;"
            "margin:-.3rem 0 1rem'>Record when someone pays "
            "you back. Balance updates immediately.</p>",
            unsafe_allow_html=True)

        people = sorted(bal.keys()) if bal else []

        if not people:
            st.markdown("""
            <div class="fc-empty">
              <h3 class="fc-empty-title">No people yet</h3>
              <p class="fc-empty-sub">Create a split first.</p>
            </div>""", unsafe_allow_html=True)
        else:
            with st.form("pf", clear_on_submit=True):
                fa, fb = st.columns(2)
                with fa:
                    p_payer = st.selectbox(
                        "Who paid?", people)
                    p_amt   = st.text_input(
                        "Amount *",
                        placeholder="e.g. 400.00")
                with fb:
                    p_recv = st.selectbox(
                        "Paid to",
                        ["You"] + [
                            x for x in people
                            if x != p_payer])
                    p_cur = st.selectbox(
                        "Currency", CURRENCIES,
                        index=CURRENCIES.index(cur_sym)
                        if cur_sym in CURRENCIES else 0,
                        key="pc")

                fc, fd = st.columns(2)
                with fc:
                    p_meth = st.selectbox(
                        "Method",
                        ["Cash", "UPI", "Bank Transfer",
                         "Card", "Other"])
                with fd:
                    p_date = st.date_input(
                        "Date", value=date.today(),
                        key="pd")

                p_notes = st.text_input(
                    "Notes (optional)",
                    placeholder="e.g. Paid via GPay")
                p_sub = st.form_submit_button(
                    "Record Payment",
                    use_container_width=True, type="primary")

            if p_sub:
                try:
                    a = D(p_amt.strip())
                    if a <= 0:
                        st.error("Amount must be > 0.")
                    else:
                        db_add_payment(
                            user_id, p_payer, p_recv,
                            a, p_cur, p_meth,
                            p_date, p_notes)
                        st.success(
                            f"{p_payer} paid "
                            f"{money(a, p_cur)} "
                            f"to {p_recv}.")
                        st.rerun()
                except Exception:
                    st.error(
                        "Invalid amount — use numbers "
                        "like 500 or 500.50")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 – PAYMENT HISTORY
    # ══════════════════════════════════════════════════════════════════════════
    with t4:
        st.markdown('<p class="slbl">Payment History</p>',
                    unsafe_allow_html=True)
        pdf2 = db_payments(user_id)

        if pdf2.empty:
            st.markdown("""
            <div class="fc-empty">
              <h3 class="fc-empty-title">No payments yet</h3>
              <p class="fc-empty-sub">
                Record a payment when someone pays you back.
              </p>
            </div>""", unsafe_allow_html=True)
        else:
            st.download_button(
                "Export All CSV",
                pdf2.to_csv(index=False),
                file_name="payments.csv",
                mime="text/csv")
            st.markdown("<br>", unsafe_allow_html=True)

            if 'del_pay' not in st.session_state:
                st.session_state.del_pay = None

            g1,g2,g3,g4,g5,g6 = st.columns(
                [2,2,2,1.5,1.5,.6])
            for col, l in zip(
                [g1,g2,g3,g4,g5,g6],
                ['From','To','Amount',
                 'Method','Date','']):
                col.markdown(
                    f"<span class='tblh'>{l}</span>",
                    unsafe_allow_html=True)
            st.markdown(
                "<div style='border-bottom:1px solid var(--border);"
                "margin-bottom:.4rem'></div>",
                unsafe_allow_html=True)

            for _, p in pdf2.iterrows():
                pid  = p['id']
                pc   = p.get('currency', cur_sym) or cur_sym
                pm   = p.get('method', 'Cash') or 'Cash'
                pd_  = p.get('pdate', '') or ''

                r1,r2,r3,r4,r5,r6 = st.columns(
                    [2,2,2,1.5,1.5,.6])
                r1.markdown(
                    f"<span style='color:#FFF;"
                    f"font-weight:500'>"
                    f"{p['payer']}</span>",
                    unsafe_allow_html=True)
                r2.markdown(
                    f"<span style='color:#FFF'>"
                    f"{p['receiver']}</span>",
                    unsafe_allow_html=True)
                r3.markdown(
                    f"<span style='color:var(--accent);"
                    f"font-weight:700'>"
                    f"{money(D(p['amount']),pc)}</span>",
                    unsafe_allow_html=True)
                r4.markdown(
                    f"<span class='bm'>{pm}</span>",
                    unsafe_allow_html=True)
                r5.markdown(
                    f"<span style='color:#8B8FA8;"
                    f"font-size:.83rem'>{pd_}</span>",
                    unsafe_allow_html=True)
                with r6:
                    if st.button("Del", key=f"dp_{pid}"):
                        st.session_state.del_pay = (
                            None
                            if st.session_state.del_pay == pid
                            else pid)
                        st.rerun()

                if st.session_state.del_pay == pid:
                    ya, yb = st.columns(2)
                    with ya:
                        if st.button(
                            "Yes, Delete",
                            key=f"pok_{pid}",
                            type="secondary",
                            use_container_width=True):
                            db_del_payment(pid, user_id)
                            st.session_state.del_pay = None
                            st.rerun()
                    with yb:
                        if st.button(
                            "Cancel", key=f"pno_{pid}",
                            use_container_width=True):
                            st.session_state.del_pay = None
                            st.rerun()

                if p.get('notes'):
                    st.markdown(
                        f"<span style='color:#8B8FA8;"
                        f"font-size:.77rem'>"
                        f"Note: {p['notes']}</span>",
                        unsafe_allow_html=True)

                st.markdown("<div class='rowdiv'></div>",
                            unsafe_allow_html=True)
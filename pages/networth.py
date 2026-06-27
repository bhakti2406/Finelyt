import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
from decimal import Decimal, ROUND_HALF_UP
from utils.currency import format_amount, get_symbol

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

def F(v):
    try:
        return float(v)
    except Exception:
        return 0.0

def fmt(v, cur):
    return format_amount(F(v), cur)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS nw_assets (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            name       TEXT    NOT NULL,
            category   TEXT    NOT NULL DEFAULT 'Other',
            value      TEXT    NOT NULL,
            note       TEXT             DEFAULT '',
            updated_at TEXT             DEFAULT (datetime('now'))
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS nw_liabilities (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            name       TEXT    NOT NULL,
            category   TEXT    NOT NULL DEFAULT 'Other',
            value      TEXT    NOT NULL,
            note       TEXT             DEFAULT '',
            updated_at TEXT             DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()

def save_net_worth_history(user_id, total_assets, total_liabilities):
    from datetime import datetime
    month = datetime.now().strftime('%Y-%m')
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute('''
            INSERT INTO nw_history (user_id, month, total_assets, total_liabilities)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, month) DO UPDATE SET
                total_assets = excluded.total_assets,
                total_liabilities = excluded.total_liabilities
        ''', (user_id, month, float(total_assets), float(total_liabilities)))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

def get_net_worth_history(user_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT month, total_assets, total_liabilities FROM nw_history WHERE user_id=? "
        "ORDER BY month ASC",
        conn, params=(user_id,))
    conn.close()
    df['net_worth'] = df['total_assets'] - df['total_liabilities']
    return df

def add_asset(user_id, name, category, value, note):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO nw_assets "
        "(user_id,name,category,value,note) VALUES (?,?,?,?,?)",
        (user_id, name, category, str(value), note))
    conn.commit()
    conn.close()

def get_assets(user_id):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM nw_assets WHERE user_id=? "
        "ORDER BY category, name",
        conn, params=(user_id,))
    conn.close()
    return df

def update_asset(aid, value, note):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE nw_assets SET value=?, note=?, "
        "updated_at=datetime('now') WHERE id=?",
        (str(value), note, aid))
    conn.commit()
    conn.close()

def delete_asset(aid, user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "DELETE FROM nw_assets WHERE id=? AND user_id=?",
        (aid, user_id))
    conn.commit()
    conn.close()

def add_liability(user_id, name, category, value, note):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO nw_liabilities "
        "(user_id,name,category,value,note) VALUES (?,?,?,?,?)",
        (user_id, name, category, str(value), note))
    conn.commit()
    conn.close()

def get_liabilities(user_id):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM nw_liabilities WHERE user_id=? "
        "ORDER BY category, name",
        conn, params=(user_id,))
    conn.close()
    return df

def update_liability(lid, value, note):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE nw_liabilities SET value=?, note=?, "
        "updated_at=datetime('now') WHERE id=?",
        (str(value), note, lid))
    conn.commit()
    conn.close()

def delete_liability(lid, user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "DELETE FROM nw_liabilities WHERE id=? AND user_id=?",
        (lid, user_id))
    conn.commit()
    conn.close()

ASSET_CATS = [
    "Cash & Savings", "Investments", "Real Estate",
    "Vehicle", "Gold & Jewelry", "Business", "Other"
]
ASSET_ICONS = {
    "Cash & Savings": "", "Investments": "",
    "Real Estate": "", "Vehicle": "",
    "Gold & Jewelry": "", "Business": "", "Other": "",
}
LIAB_CATS = [
    "Home Loan", "Car Loan", "Personal Loan",
    "Credit Card", "Education Loan", "Other"
]
LIAB_ICONS = {
    "Home Loan": "", "Car Loan": "",
    "Personal Loan": "", "Credit Card": "",
    "Education Loan": "", "Other": "",
}

def show(user_id=1):
    init_db()
    currency = st.session_state.get('currency', 'INR')
    sym = get_symbol(currency)

    st.markdown("""
    <style>
    .slbl     { font-size:.75rem; font-weight:700;
                color:var(--accent); text-transform:uppercase;
                letter-spacing:.1em; margin-bottom:.6rem; }
    .kpi-card { background:var(--bg-card); border:1px solid var(--border);
                border-radius:14px; padding:1.2rem 1.4rem;
                text-align:center; }
    .kpi-lbl  { font-size:.75rem; color:var(--text-muted);
                text-transform:uppercase;
                letter-spacing:.06em; }
    .kpi-val  { font-size:1.6rem; font-weight:800;
                color:var(--text-primary); margin-top:4px; }
    .hero-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-surface) 100%);
        border: 1px solid var(--border);
        border-radius:20px;
        padding:2rem; text-align:center;
        margin-bottom:1rem;
        box-shadow: var(--shadow-md);
    }
    .nw-num { font-size:3.5rem; font-weight:900;
              line-height:1; }
    .del-box { background:var(--danger-dim);
               border:1px solid var(--danger);
               border-radius:10px;
               padding:.6rem 1rem; margin:.3rem 0; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="fc-page-title">Net Worth Tracker</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="fc-page-sub">Track your assets and liabilities to know your true financial position.</p>',
        unsafe_allow_html=True)
    st.divider()

    assets_df = get_assets(user_id)
    liab_df   = get_liabilities(user_id)

    total_assets = sum(
        D(r['value']) for _, r in assets_df.iterrows()
    ) if not assets_df.empty else D(0)

    total_liab = sum(
        D(r['value']) for _, r in liab_df.iterrows()
    ) if not liab_df.empty else D(0)

    net_worth = total_assets - total_liab
    nw_f = F(net_worth)
    ta_f = F(total_assets)
    tl_f = F(total_liab)

    save_net_worth_history(user_id, ta_f, tl_f)

    # ── HERO CARD ─────────────────────────────────────────────────────────────
    nw_color = "var(--accent)" if nw_f >= 0 else "var(--danger)"
    nw_label = "Positive Net Worth" if nw_f >= 0 else "Negative Net Worth"

    st.markdown(f"""
    <div class="hero-card">
        <div style="color:var(--text-muted);font-size:.9rem;
                    text-transform:uppercase;
                    letter-spacing:.1em">
            Your Net Worth
        </div>
        <div class="nw-num"
             style="color:{nw_color};margin:.5rem 0">
            {fmt(nw_f, currency)}
        </div>
        <div style="color:var(--text-secondary);font-size:.95rem">
            {nw_label}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    k1, k2, k3 = st.columns(3)
    k1.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">Total Assets</div>
        <div class="kpi-val" style="color:var(--accent)">
            {fmt(ta_f, currency)}
        </div>
    </div>""", unsafe_allow_html=True)

    k2.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">Total Liabilities</div>
        <div class="kpi-val" style="color:var(--danger)">
            {fmt(tl_f, currency)}
        </div>
    </div>""", unsafe_allow_html=True)

    debt_ratio = (tl_f / ta_f * 100) if ta_f > 0 else 0.0
    dr_color = (
        "var(--accent)" if debt_ratio < 30 else
        "var(--warning)" if debt_ratio < 60 else "var(--danger)"
    )
    dr_label = (
        "Healthy" if debt_ratio < 30 else
        "Moderate" if debt_ratio < 60 else "High"
    )
    k3.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">Debt Ratio</div>
        <div class="kpi-val" style="color:{dr_color}">
            {debt_ratio:.1f}%
        </div>
        <div style="font-size:.72rem;color:var(--text-muted);
                    margin-top:4px">
            {dr_label}
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── TABS ──────────────────────────────────────────────────────────────────
    t1, t2, t3, t4 = st.tabs([
        "Add Asset", "Add Liability",
        "Assets", "Liabilities"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — ADD ASSET
    # ══════════════════════════════════════════════════════════════════════════
    with t1:
        st.markdown('<p class="slbl">Add a New Asset</p>',
                    unsafe_allow_html=True)

        with st.form("add_asset_form",
                     clear_on_submit=True):
            aa1, aa2 = st.columns(2)
            with aa1:
                a_name = st.text_input(
                    "Asset Name *",
                    placeholder="e.g. SBI Savings Account")
                a_val = st.text_input(
                    "Current Value *",
                    placeholder="e.g. 50000")
            with aa2:
                a_cat = st.selectbox(
                    "Category", ASSET_CATS)
                a_note = st.text_input(
                    "Note (optional)",
                    placeholder="e.g. Emergency fund")
            a_sub = st.form_submit_button(
                "Add Asset",
                use_container_width=True,
                type="primary")

        if a_sub:
            if not a_name.strip():
                st.error("Asset name is required.")
            else:
                try:
                    val = D(a_val.strip())
                    if val < 0:
                        st.error("Value cannot be negative.")
                    else:
                        add_asset(
                            user_id, a_name.strip(),
                            a_cat, val, a_note.strip())
                        st.success(
                            f"Added: {a_name.strip()} — "
                            f"{fmt(F(val), currency)}")
                        st.rerun()
                except Exception:
                    st.error("Invalid value — use numbers like 50000")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — ADD LIABILITY
    # ══════════════════════════════════════════════════════════════════════════
    with t2:
        st.markdown('<p class="slbl">Add a New Liability</p>',
                    unsafe_allow_html=True)

        with st.form("add_liab_form",
                     clear_on_submit=True):
            la1, la2 = st.columns(2)
            with la1:
                l_name = st.text_input(
                    "Liability Name *",
                    placeholder="e.g. Home Loan, Car EMI")
                l_val = st.text_input(
                    "Outstanding Amount *",
                    placeholder="e.g. 500000")
            with la2:
                l_cat = st.selectbox(
                    "Category", LIAB_CATS)
                l_note = st.text_input(
                    "Note (optional)",
                    placeholder="e.g. 8.5% interest rate")
            l_sub = st.form_submit_button(
                "Add Liability",
                use_container_width=True,
                type="primary")

        if l_sub:
            if not l_name.strip():
                st.error("Liability name is required.")
            else:
                try:
                    val = D(l_val.strip())
                    if val < 0:
                        st.error("Value cannot be negative.")
                    else:
                        add_liability(
                            user_id, l_name.strip(),
                            l_cat, val, l_note.strip())
                        st.success(
                            f"Added: {l_name.strip()} — "
                            f"{fmt(F(val), currency)}")
                        st.rerun()
                except Exception:
                    st.error("Invalid value — use numbers like 500000")    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — ASSETS
    # ══════════════════════════════════════════════════════════════════════════
    with t3:
        st.markdown('<p class="slbl">Your Assets</p>',
                    unsafe_allow_html=True)

        if assets_df.empty:
            st.markdown("""
            <div class="fc-empty">
                <h3 class="fc-empty-title">No assets yet</h3>
                <p class="fc-empty-sub">
                    Add assets in the Add Asset tab.
                </p>
            </div>""", unsafe_allow_html=True)
        else:
            if 'del_asset' not in st.session_state:
                st.session_state.del_asset = None
            if 'edit_asset' not in st.session_state:
                st.session_state.edit_asset = None

            for cat in assets_df['category'].unique():
                cat_df = assets_df[
                    assets_df['category'] == cat]
                cat_tot = F(sum(
                    D(r['value'])
                    for _, r in cat_df.iterrows()))

                st.markdown(
                    f"<p style='color:var(--accent);"
                    f"font-weight:600;"
                    f"margin:.8rem 0 .3rem'>"
                    f"{cat} — "
                    f"{fmt(cat_tot, currency)}</p>",
                    unsafe_allow_html=True)

                for _, row in cat_df.iterrows():
                    aid = row['id']
                    ac1, ac2, ac3, ac4 = st.columns(
                        [3, 2, 0.7, 0.7])

                    ac1.markdown(
                        f"<span style='color:#FFF;"
                        f"font-weight:500'>"
                        f"{row['name']}</span>"
                        f"<br><span style='color:var(--text-muted);"
                        f"font-size:.78rem'>"
                        f"{row.get('note','') or '—'}"
                        f"</span>",
                        unsafe_allow_html=True)
                    ac2.markdown(
                        f"<span style='color:var(--accent);"
                        f"font-weight:700;font-size:1rem'>"
                        f"{fmt(F(D(row['value'])), currency)}"
                        f"</span>",
                        unsafe_allow_html=True)

                    with ac3:
                        if st.button("Edit",
                                     key=f"ea_{aid}"):
                            st.session_state.edit_asset = (
                                None if
                                st.session_state.edit_asset
                                == aid else aid)
                            st.rerun()
                    with ac4:
                        if st.button("Del",
                                     key=f"da_{aid}"):
                            st.session_state.del_asset = (
                                None if
                                st.session_state.del_asset
                                == aid else aid)
                            st.rerun()

                    if st.session_state.edit_asset == aid:
                        with st.form(f"eaf_{aid}",
                                     clear_on_submit=True):
                            ev1, ev2 = st.columns(2)
                            with ev1:
                                new_val = st.text_input(
                                    "New Value",
                                    value=str(D(row['value'])))
                            with ev2:
                                new_note = st.text_input(
                                    "Note",
                                    value=row.get(
                                        'note', '') or '')
                            es1, es2 = st.columns(2)
                            with es1:
                                esave = st.form_submit_button(
                                    "Save",
                                    use_container_width=True,
                                    type="primary")
                            with es2:
                                ecanc = st.form_submit_button(
                                    "Cancel",
                                    use_container_width=True)
                        if esave:
                            update_asset(
                                  aid, D(new_val), new_note)
                            st.session_state.edit_asset = None
                            st.rerun()
                        if ecanc:
                            st.session_state.edit_asset = None
                            st.rerun()

                    if st.session_state.del_asset == aid:
                        st.markdown(
                            f"<div class='del-box'>"
                            f"<span style='color:var(--danger);"
                            f"font-weight:600'>"
                            f"Delete \"{row['name']}\"? "
                            f"Cannot be undone."
                            f"</span></div>",
                            unsafe_allow_html=True)
                        dx1, dx2 = st.columns(2)
                        with dx1:
                            if st.button(
                                "Yes, Delete",
                                key=f"daok_{aid}",
                                type="secondary",
                                use_container_width=True):
                                delete_asset(aid, user_id)
                                st.session_state.del_asset = None
                                st.rerun()
                        with dx2:
                            if st.button(
                                "Cancel",
                                key=f"dano_{aid}",
                                use_container_width=True):
                                st.session_state.del_asset = None
                                st.rerun()

                    st.markdown(
                        "<div style='border-bottom:"
                        "1px solid var(--border);"
                        "margin:.2rem 0'></div>",
                        unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — LIABILITIES
    # ══════════════════════════════════════════════════════════════════════════
    with t4:
        st.markdown('<p class="slbl">Your Liabilities</p>',
                    unsafe_allow_html=True)

        if liab_df.empty:
            st.markdown("""
            <div class="fc-empty">
                <h3 class="fc-empty-title">No liabilities</h3>
                <p class="fc-empty-sub">
                    Add liabilities in the Add Liability tab.
                </p>
            </div>""", unsafe_allow_html=True)
        else:
            if 'del_liab' not in st.session_state:
                st.session_state.del_liab = None
            if 'edit_liab' not in st.session_state:
                st.session_state.edit_liab = None

            for cat in liab_df['category'].unique():
                cat_df = liab_df[
                    liab_df['category'] == cat]
                cat_tot = F(sum(
                    D(r['value'])
                    for _, r in cat_df.iterrows()))

                st.markdown(
                    f"<p style='color:var(--danger);"
                    f"font-weight:600;"
                    f"margin:.8rem 0 .3rem'>"
                    f"{cat} — "
                    f"{fmt(cat_tot, currency)}</p>",
                    unsafe_allow_html=True)

                for _, row in cat_df.iterrows():
                    lid = row['id']
                    lc1, lc2, lc3, lc4 = st.columns(
                        [3, 2, 0.7, 0.7])

                    lc1.markdown(
                        f"<span style='color:#FFF;"
                        f"font-weight:500'>"
                        f"{row['name']}</span>"
                        f"<br><span style='color:var(--text-muted);"
                        f"font-size:.78rem'>"
                        f"{row.get('note','') or '—'}"
                        f"</span>",
                        unsafe_allow_html=True)
                    lc2.markdown(
                        f"<span style='color:var(--danger);"
                        f"font-weight:700;font-size:1rem'>"
                        f"{fmt(F(D(row['value'])), currency)}"
                        f"</span>",
                        unsafe_allow_html=True)

                    with lc3:
                        if st.button("Edit",
                                     key=f"el_{lid}"):
                            st.session_state.edit_liab = (
                                None if
                                st.session_state.edit_liab
                                == lid else lid)
                            st.rerun()
                    with lc4:
                        if st.button("Del",
                                     key=f"dl_{lid}"):
                            st.session_state.del_liab = (
                                None if
                                st.session_state.del_liab
                                == lid else lid)
                            st.rerun()

                    if st.session_state.edit_liab == lid:
                        with st.form(f"elf_{lid}",
                                     clear_on_submit=True):
                            lv1, lv2 = st.columns(2)
                            with lv1:
                                lnew_val = st.text_input(
                                    "New Value",
                                    value=str(D(row['value'])))
                            with lv2:
                                lnew_note = st.text_input(
                                    "Note",
                                    value=row.get(
                                        'note', '') or '')
                            ls1, ls2 = st.columns(2)
                            with ls1:
                                lsave = st.form_submit_button(
                                    "Save",
                                    use_container_width=True,
                                    type="primary")
                            with ls2:
                                lcanc = st.form_submit_button(
                                    "Cancel",
                                    use_container_width=True)
                        if lsave:
                            update_liability(
                                lid, D(lnew_val), lnew_note)
                            st.session_state.edit_liab = None
                            st.rerun()
                        if lcanc:
                            st.session_state.edit_liab = None
                            st.rerun()

                    if st.session_state.del_liab == lid:
                        st.markdown(
                            f"<div class='del-box'>"
                            f"<span style='color:var(--danger);"
                            f"font-weight:600'>"
                            f"Delete \"{row['name']}\"? "
                            f"Cannot be undone."
                            f"</span></div>",
                            unsafe_allow_html=True)
                        lx1, lx2 = st.columns(2)
                        with lx1:
                            if st.button(
                                "Yes, Delete",
                                key=f"dlok_{lid}",
                                type="secondary",
                                use_container_width=True):
                                delete_liability(lid, user_id)
                                st.session_state.del_liab = None
                                st.rerun()
                        with lx2:
                            if st.button(
                                "Cancel",
                                key=f"dlno_{lid}",
                                use_container_width=True):
                                st.session_state.del_liab = None
                                st.rerun()

                    st.markdown(
                        "<div style='border-bottom:"
                        "1px solid var(--border);"
                        "margin:.2rem 0'></div>",
                        unsafe_allow_html=True)

    # ── CHARTS ────────────────────────────────────────────────────────────────
    if not assets_df.empty or not liab_df.empty:
        st.markdown('<p class="slbl">Breakdown</p>',
                    unsafe_allow_html=True)
        ch1, ch2 = st.columns(2)

        with ch1:
            if not assets_df.empty:
                a_grouped = assets_df.groupby(
                    'category'
                ).apply(
                    lambda x: F(sum(D(v) for v in x['value']))
                ).reset_index()
                a_grouped.columns = ['Category', 'Value']
                a_grouped = a_grouped[a_grouped['Value'] > 0]

                fig_a = px.pie(
                    a_grouped,
                    values='Value', names='Category',
                    title='Assets by Category',
                    color_discrete_sequence=[
                        '#10B981','#3B82F6','#F59E0B',
                        '#8B5CF6','#06B6D4',
                        '#F59E0B','#6366F1'],
                    hole=0.45)
                fig_a.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF',
                    title_font_color='#FFFFFF',
                    legend=dict(
                        font=dict(color='#FFFFFF'),
                        bgcolor='rgba(0,0,0,0)'),
                    margin=dict(t=40,b=20,l=10,r=10))
                fig_a.update_traces(
                    texttemplate='%{label}<br>%{percent}',
                    textfont_color='#FFFFFF',
                    marker=dict(
                        line=dict(color='#0A0F1D', width=2)))
                st.plotly_chart(
                    fig_a, use_container_width=True)

        with ch2:
            if not liab_df.empty:
                l_grouped = liab_df.groupby(
                    'category'
                ).apply(
                    lambda x: F(sum(D(v) for v in x['value']))
                ).reset_index()
                l_grouped.columns = ['Category', 'Value']
                l_grouped = l_grouped[l_grouped['Value'] > 0]

                fig_l = px.pie(
                    l_grouped,
                    values='Value', names='Category',
                    title='Liabilities by Category',
                    color_discrete_sequence=[
                        '#EF4444','#FF8C42','#F59E0B',
                        '#FF6B6B','#E53E3E','#C53030'],
                    hole=0.45)
                fig_l.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF',
                    title_font_color='#FFFFFF',
                    legend=dict(
                        font=dict(color='#FFFFFF'),
                        bgcolor='rgba(0,0,0,0)'),
                    margin=dict(t=40,b=20,l=10,r=10))
                fig_l.update_traces(
                    texttemplate='%{label}<br>%{percent}',
                    textfont_color='#FFFFFF',
                    marker=dict(
                        line=dict(color='#0A0F1D', width=2)))
                st.plotly_chart(
                    fig_l, use_container_width=True)

        st.divider()

        # Monthly Net Worth Trend Chart
        st.markdown('<p class="slbl">Net Worth Trend over Time</p>', unsafe_allow_html=True)
        nw_history_df = get_net_worth_history(user_id)
        if nw_history_df.empty:
            st.info("No historical logs recorded yet. Trends will accumulate as you update assets and liabilities monthly.")
        else:
            fig_trend = px.line(
                nw_history_df, x='month', y='net_worth',
                markers=True, text='net_worth',
                title="Historical Net Worth Progression"
            )
            fig_trend.update_traces(line_color="#10B981", textposition="top center")
            fig_trend.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF',
                title_font_color='#FFFFFF',
                xaxis=dict(gridcolor='#1E293B', color='#94A3B8', title="Month"),
                yaxis=dict(gridcolor='#1E293B', color='#94A3B8', title=f"Net Worth ({sym})"),
                margin=dict(t=40, b=20, l=10, r=10)
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        st.divider()
        
        # Financial Freedom progress
        st.markdown('<p class="slbl">Financial Freedom Target Planner</p>', unsafe_allow_html=True)
        col_input, col_prog = st.columns([1, 1.2])
        
        with col_input:
            target_nw = st.number_input("Target Net Worth for Financial Freedom", min_value=10000, value=1000000, step=50000)
            
            # calculate monthly savings velocity
            from utils.db import get_all_income, get_all_expenses
            from datetime import datetime
            expenses_df = get_all_expenses(user_id)
            income_df = get_all_income(user_id)
            
            avg_exp = 30000.0
            if not expenses_df.empty:
                expenses_df = expenses_df.copy()
                expenses_df['date'] = pd.to_datetime(expenses_df['date'])
                expenses_df['month'] = expenses_df['date'].dt.strftime('%Y-%m')
                avg_exp = expenses_df.groupby('month')['amount'].sum().mean()
                if pd.isna(avg_exp) or avg_exp == 0:
                    avg_exp = 30000.0
                    
            avg_inc = 50000.0
            if not income_df.empty:
                income_df = income_df.copy()
                income_df['date'] = pd.to_datetime(income_df['date'])
                income_df['month'] = income_df['date'].dt.strftime('%Y-%m')
                avg_inc = income_df.groupby('month')['amount'].sum().mean()
                if pd.isna(avg_inc) or avg_inc == 0:
                    avg_inc = 50000.0
                    
            monthly_saving_velocity = max(1000.0, avg_inc - avg_exp)
            st.markdown(f"""
            <div style='background:var(--bg-elevated); padding:10px 14px; border-radius:8px; border-left:3px solid var(--accent); margin-top:10px; font-size:0.85rem;'>
                <strong>Savings velocity:</strong> {format_amount(monthly_saving_velocity, currency)} / month
            </div>
            """, unsafe_allow_html=True)
            
        with col_prog:
            progress_pct = (nw_f / target_nw) * 100 if target_nw > 0 else 0.0
            progress_pct = min(100.0, max(0.0, progress_pct))
            
            shortfall = max(0.0, target_nw - nw_f)
            years_needed = shortfall / (monthly_saving_velocity * 12) if monthly_saving_velocity > 0 else 99.0
            
            st.markdown(f"""
            <div style='background:var(--bg-card); border:1px solid var(--border); padding:1.2rem; border-radius:12px; margin-top:6px;'>
                <div style='display:flex; justify-content:space-between; margin-bottom:8px;'>
                    <span style='color:var(--text-secondary); font-size:0.88rem;'>Target Progress</span>
                    <span style='color:#10B981; font-weight:700;'>{progress_pct:.1f}%</span>
                </div>
                <div style='background:var(--bg-elevated); border-radius:999px; height:12px;'>
                    <div style='background:linear-gradient(90deg, #3B82F6, #10B981); width:{progress_pct}%; height:12px; border-radius:999px;'></div>
                </div>
                <div style='margin-top:12px; font-size:0.88rem; line-height:1.5; color:var(--text-secondary);'>
                    Target: <strong>{format_amount(target_nw, currency)}</strong><br>
                    Current Net Worth: <strong>{format_amount(nw_f, currency)}</strong><br>
                    Years to Financial Freedom: <strong style='color:var(--accent);'>{years_needed:.1f} years</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
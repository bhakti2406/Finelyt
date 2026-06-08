import streamlit as st
import sqlite3
import os
from utils.currency import CURRENCY_SYMBOLS
from utils.auth import hash_password, verify_password, validate_password_strength, generate_session_token

def get_db_path():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', 'data', 'finance.db'
    )

def get_user_details(user_id):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def update_username(user_id, new_username):
    conn = sqlite3.connect(get_db_path())
    try:
        conn.execute(
            'UPDATE users SET username=? WHERE id=?',
            (new_username, user_id)
        )
        conn.commit()
        conn.close()
        return True, "Username updated successfully."
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already taken."

def update_password(user_id, current_pwd, new_pwd):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        'SELECT password_hash FROM users WHERE id=?', (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False, "User not found."
    if not verify_password(current_pwd, row[0]):
        return False, "Current password is incorrect."
    
    is_strong, strength_msg = validate_password_strength(new_pwd)
    if not is_strong:
        return False, strength_msg

    conn = sqlite3.connect(get_db_path())
    conn.execute(
        'UPDATE users SET password_hash=? WHERE id=?',
        (hash_password(new_pwd), user_id)
    )
    conn.commit()
    conn.close()
    return True, "Password updated successfully."

def get_expense_stats(user_id):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        'SELECT COUNT(*), SUM(amount) FROM expenses WHERE user_id=?',
        (user_id,)
    )
    row = cursor.fetchone()
    cursor.execute(
        'SELECT COUNT(*) FROM income WHERE user_id=?', (user_id,)
    )
    income_count = cursor.fetchone()[0]
    cursor.execute(
        'SELECT created_at FROM users WHERE id=?', (user_id,)
    )
    created = cursor.fetchone()
    conn.close()
    return {
        'expenses': row[0] or 0,
        'total_spent': row[1] or 0,
        'income_entries': income_count,
        'member_since': created[0][:10] if created and created[0] else 'N/A'
    }

def delete_all_data(user_id):
    conn = sqlite3.connect(get_db_path())
    conn.execute('DELETE FROM expenses WHERE user_id=?', (user_id,))
    conn.execute('DELETE FROM income WHERE user_id=?', (user_id,))
    conn.execute('DELETE FROM budgets WHERE user_id=?', (user_id,))
    conn.execute('DELETE FROM savings_goals WHERE user_id=?', (user_id,))
    conn.execute('DELETE FROM notifications WHERE user_id=?', (user_id,))
    conn.execute('DELETE FROM user_settings WHERE user_id=?', (user_id,))
    try:
        conn.execute(
            'DELETE FROM recurring_bills WHERE user_id=?', (user_id,)
        )
    except Exception:
        pass
    conn.commit()
    conn.close()

def show(user_id=1):
    currency = st.session_state.get('currency', 'INR')
    username = st.session_state.get('username', '')

    st.markdown("""
    <style>
    .section-title { font-size:1rem; font-weight:600; color:var(--accent);
                     text-transform:uppercase; letter-spacing:0.08em;
                     margin-bottom:1rem; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="fc-page-title">Settings</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="fc-page-sub">Manage your profile, security, and account data.</p>',
        unsafe_allow_html=True
    )
    st.divider()

    stats = get_expense_stats(user_id)

    # ── ACCOUNT OVERVIEW ──────────────────────────────────────────────────────
    st.markdown('<p class="section-title">Account Overview</p>',
                unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Username", f"@{username}")
    c2.metric("Expenses Logged", stats['expenses'])
    c3.metric("Income Entries", stats['income_entries'])
    c4.metric("Member Since", stats['member_since'])

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "Profile", "Security", "Preferences", "Data & Account"
    ])

    # ── TAB 1: PROFILE ────────────────────────────────────────────────────────
    with tab1:
        st.markdown('<p class="section-title">Change Username</p>',
                    unsafe_allow_html=True)

        with st.form("username_form"):
            st.markdown(
                f"<p style='color:#8B8FA8;font-size:0.88rem;"
                f"margin-bottom:0.5rem;'>Current username: "
                f"<strong style='color:var(--accent);'>@{username}</strong></p>",
                unsafe_allow_html=True
            )
            new_username = st.text_input(
                "New Username",
                placeholder="Min 3 characters, no spaces"
            )
            save_username = st.form_submit_button(
                "Update Username",
                use_container_width=True,
                type="primary"
            )

        if save_username:
            if not new_username:
                st.error("Please enter a new username.")
            elif len(new_username) < 3:
                st.error("Username must be at least 3 characters.")
            elif ' ' in new_username:
                st.error("Username cannot contain spaces.")
            elif new_username == username:
                st.warning("New username is the same as current.")
            else:
                success, msg = update_username(user_id, new_username)
                if success:
                    st.session_state.username = new_username
                    st.query_params['session_token'] = generate_session_token(user_id, new_username)
                    st.success(f"Username changed to @{new_username}")
                    st.rerun()
                else:
                    st.error(msg)

    # ── TAB 2: SECURITY ───────────────────────────────────────────────────────
    with tab2:
        st.markdown('<p class="section-title">Change Password</p>',
                    unsafe_allow_html=True)

        with st.form("password_form"):
            current_pwd = st.text_input(
                "Current Password", type="password",
                placeholder="Enter your current password"
            )
            new_pwd = st.text_input(
                "New Password", type="password",
                placeholder="Min 8 characters, uppercase, lowercase, digit, special"
            )
            confirm_pwd = st.text_input(
                "Confirm New Password", type="password",
                placeholder="Repeat new password"
            )

            # Live match indicator
            if confirm_pwd and new_pwd:
                if new_pwd != confirm_pwd:
                    st.markdown(
                        "<p style='color:var(--danger); font-size:0.82rem;'>"
                        "Passwords do not match</p>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        "<p style='color:var(--accent); font-size:0.82rem;'>"
                        "Passwords match</p>",
                        unsafe_allow_html=True
                    )

            # Unified Password strength check for settings
            if new_pwd:
                has_length = len(new_pwd) >= 8
                has_upper = any(c.isupper() for c in new_pwd)
                has_lower = any(c.islower() for c in new_pwd)
                has_number = any(c.isdigit() for c in new_pwd)
                has_special = any(c in "@#$^&*!?" for c in new_pwd)
                
                score = 0
                if has_length: score += 1
                if has_upper and has_lower: score += 1
                if has_number: score += 1
                if has_special: score += 1
                if len(new_pwd) >= 12: score += 1

                colors = {
                    0: "var(--danger)", 1: "var(--danger)", 2: "var(--danger)",
                    3: "var(--warning)", 4: "var(--accent)", 5: "#00F2A8"
                }
                labels = {
                    0: "Weak", 1: "Weak", 2: "Weak",
                    3: "Medium", 4: "Strong", 5: "Very Strong"
                }
                color = colors.get(score, "var(--danger)")
                label = labels.get(score, "Weak")
                pct = min(100, score * 20)

                st.markdown(f"""
                <div style="margin-bottom:0.5rem;">
                    <div style="display:flex; justify-content:space-between;
                                margin-bottom:4px;">
                        <span style="color:#8B8FA8;font-size:0.78rem;">
                            Password strength
                        </span>
                        <span style="color:{color};font-size:0.78rem;
                                     font-weight:600;">{label}</span>
                    </div>
                    <div style="background:#2A2D3E; border-radius:999px;
                                height:4px;">
                        <div style="background:{color};
                                    width:{pct}%;
                                    height:4px; border-radius:999px; transition: width 0.3s ease;">
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            save_pwd = st.form_submit_button(
                "Update Password",
                use_container_width=True,
                type="primary"
            )

        if save_pwd:
            if not current_pwd or not new_pwd or not confirm_pwd:
                st.error("Please fill in all fields.")
            elif new_pwd != confirm_pwd:
                st.error("Passwords do not match.")
            else:
                success, msg = update_password(
                    user_id, current_pwd, new_pwd
                )
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

        st.divider()

        st.markdown('<p class="section-title">Session Security</p>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div style="
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
">
    <p style="
        color: var(--text-secondary);
        font-size: 0.88rem;
        margin: 0;
        line-height: 1.5;
    ">
        Logged in as
        <strong style="color: var(--accent);">@{username}</strong>.
        Your account is protected with secure authentication, encrypted credentials, and verified email security.
    </p>
</div>
        """, unsafe_allow_html=True)


        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            from utils.auth import logout
            logout()
            st.query_params.clear()
            st.rerun()

    # ── TAB 3: PREFERENCES ────────────────────────────────────────────────────
    with tab3:
        st.markdown('<p class="section-title">Display Currency</p>',
                    unsafe_allow_html=True)

        currencies = ["INR", "OMR", "USD", "EUR", "GBP"]
        currency_labels = {
            "INR": "Indian Rupee",
            "OMR": "Omani Rial",
            "USD": "US Dollar",
            "EUR": "Euro",
            "GBP": "British Pound"
        }

        current_idx = currencies.index(currency) \
            if currency in currencies else 0

        selected_currency = st.selectbox(
            "Select Currency",
            options=currencies,
            format_func=lambda x: currency_labels.get(x, x),
            index=current_idx
        )

        if st.button(
            "Save Currency Preference",
            use_container_width=True,
            type="primary"
        ):
            st.session_state.currency = selected_currency
            st.success(
                f"Currency set to "
                f"{currency_labels.get(selected_currency)}"
            )
            st.rerun()

        st.divider()

        st.markdown('<p class="section-title">Notifications</p>',
                    unsafe_allow_html=True)
        st.markdown("""
        <div style="background:var(--bg-card); border:1px solid var(--border);
                    border-radius:12px; padding:1rem 1.2rem;">
            <p style="color:var(--text-secondary); font-size:0.88rem; margin:0;">
                Notifications are generated automatically from your
                spending data. Budget alerts, anomaly warnings, and
                savings progress appear via the bell icon at the top
                of every page. Click
                <strong style="color:var(--accent);">Clear All</strong>
                in the notification panel to dismiss them for 24 hours.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ── TAB 4: DATA & ACCOUNT ─────────────────────────────────────────────────
    with tab4:
        st.markdown('<p class="section-title">Your Data</p>',
                    unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:var(--bg-card); border:1px solid var(--border);
                    border-radius:12px; padding:1.2rem 1.5rem;
                    margin-bottom:1rem;">
            <div style="display:grid; grid-template-columns:1fr 1fr;
                        gap:0.8rem;">
                <div>
                    <div style="color:var(--text-muted);font-size:0.78rem;">
                        Total Expenses
                    </div>
                    <div style="color:#FFFFFF;font-weight:700;
                                font-size:1.1rem;">
                        {stats['expenses']} transactions
                    </div>
                </div>
                <div>
                    <div style="color:var(--text-muted);font-size:0.78rem;">
                        Income Entries
                    </div>
                    <div style="color:#FFFFFF;font-weight:700;
                                font-size:1.1rem;">
                        {stats['income_entries']} entries
                    </div>
                </div>
                <div>
                    <div style="color:var(--text-muted);font-size:0.78rem;">
                        Member Since
                    </div>
                    <div style="color:#FFFFFF;font-weight:700;
                                font-size:1.1rem;">
                        {stats['member_since']}
                    </div>
                </div>
                <div>
                    <div style="color:var(--text-muted);font-size:0.78rem;">
                        Account ID
                    </div>
                    <div style="color:#FFFFFF;font-weight:700;
                                font-size:1.1rem;">
                        #{user_id}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        st.markdown(
            '<p class="section-title" style="color:var(--danger);">'
            'Danger Zone</p>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div style="background:var(--danger-dim); border:1px solid var(--danger);
                    border-radius:12px; padding:1rem 1.2rem;
                    margin-bottom:1rem;">
            <p style="color:var(--danger); font-weight:600;
                       margin:0 0 4px 0;">
                Delete All My Data
            </p>
            <p style="color:var(--text-secondary); font-size:0.85rem; margin:0;">
                Permanently deletes all expenses, income, budgets,
                goals, and bills. Your account stays but all data
                will be cleared. This cannot be undone.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if 'confirm_delete_data' not in st.session_state:
            st.session_state.confirm_delete_data = False

        if not st.session_state.confirm_delete_data:
            if st.button(
                "Delete All My Data",
                use_container_width=True
            ):
                st.session_state.confirm_delete_data = True
                st.rerun()
        else:
            st.markdown("""
            <div style="background:#2E0D0D; border:1px solid var(--danger);
                        border-radius:10px; padding:1rem;
                        margin-bottom:0.5rem;">
                <p style="color:var(--danger); font-weight:700; margin:0;">
                    Are you absolutely sure? This cannot be undone.
                </p>
            </div>
            """, unsafe_allow_html=True)

            confirm_text = st.text_input(
                'Type DELETE to confirm',
                placeholder="DELETE"
            )
            cd1, cd2 = st.columns(2)
            with cd1:
                if st.button(
                    "Yes, Delete Everything",
                    type="secondary",
                    use_container_width=True
                ):
                    if confirm_text == "DELETE":
                        delete_all_data(user_id)
                        st.session_state.confirm_delete_data = False
                        st.success(
                            "All data deleted. Your account is now empty."
                        )
                        st.rerun()
                    else:
                        st.error('Type "DELETE" to confirm.')
            with cd2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.confirm_delete_data = False
                    st.rerun()
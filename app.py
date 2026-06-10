import streamlit as st

st.set_page_config(
    page_title="Finelyt | AI Finance Coach",
     page_icon="📈",
    layout="wide"
)

from app_styles import GLOBAL_CSS, LOGO_FULL_SVG, LOGO_ICON_SVG
from app_icons import ICONS, icon, icon_text
import re
# Strip comments and all blank lines to prevent Streamlit's markdown parser from splitting HTML block
clean_css = re.sub(r'/\*.*?\*/', '', GLOBAL_CSS, flags=re.DOTALL)
clean_css = "\n".join([line for line in clean_css.splitlines() if line.strip()])
st.markdown(clean_css, unsafe_allow_html=True)
from utils.db import create_tables
from utils.auth import (
    login_user, register_user,
    is_logged_in, logout,
    generate_otp, send_otp_email,
    generate_session_token
)

create_tables()

st.markdown("""
<style>
.stApp { background-color: transparent !important; color: #FFFFFF; }
section[data-testid="stSidebar"] {
    background-color: rgba(13, 18, 36, 0.7) !important;
    border-right: 1px solid var(--border) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}
div[data-testid="stSidebarNav"] { display: none; }
h1, h2, h3, h4, h5 { color: #FFFFFF !important; }
.stTextInput > div > div > input {
    background: #1A1D27 !important;
    border: 1px solid #2A2D3E !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00D4AA !important;
    box-shadow: 0 0 0 2px rgba(0,212,170,0.2) !important;
}
.stNumberInput > div > div > input {
    background: #1A1D27 !important;
    border: 1px solid #2A2D3E !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
}
.stSelectbox > div > div {
    background: #1A1D27 !important;
    border: 1px solid #2A2D3E !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
}
.stDateInput > div > div > input {
    background: #1A1D27 !important;
    border: 1px solid #2A2D3E !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00D4AA, #00B894) !important;
    color: #0F1117 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(0,212,170,0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #FF4B4B !important;
    border: 1px solid #FF4B4B !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #FF4B4B !important;
    color: #FFFFFF !important;
}
div[data-testid="metric-container"] {
    background: #1A1D27 !important;
    border: 1px solid #2A2D3E !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
div[data-testid="stForm"] {
    background: #1A1D27 !important;
    border: 1px solid #2A2D3E !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
}
.stSuccess > div {
    background: #0D2E1F !important;
    border: 1px solid #00D4AA !important;
    border-radius: 10px !important;
    color: #00D4AA !important;
}
.stError > div {
    background: #2E0D0D !important;
    border: 1px solid #FF4B4B !important;
    border-radius: 10px !important;
}
.stWarning > div {
    background: #2E1F0D !important;
    border: 1px solid #FFB347 !important;
    border-radius: 10px !important;
}
.stInfo > div {
    background: #0D1A2E !important;
    border: 1px solid #4A90D9 !important;
    border-radius: 10px !important;
}
.stExpander {
    background: #1A1D27 !important;
    border: 1px solid #2A2D3E !important;
    border-radius: 12px !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #1A1D27 !important;
    border-radius: 12px !important;
    padding: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #8B8FA8 !important;
    border-radius: 8px !important;
}
.stTabs [aria-selected="true"] {
    background: #00D4AA !important;
    color: #0F1117 !important;
    font-weight: 700 !important;
}
.stDataFrame {
    border: 1px solid #2A2D3E !important;
    border-radius: 12px !important;
}
hr { border-color: #2A2D3E !important; }
.feature-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0,212,170,0.1);
    border: 1px solid rgba(0,212,170,0.2);
    border-radius: 999px;
    padding: 6px 14px;
    margin: 4px;
    font-size: 0.82rem;
    color: #00D4AA;
}
.stat-pill {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    margin-bottom: 0.5rem;
}
.trust-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 0.75rem;
    color: #8B8FA8;
    margin: 3px;
}
@keyframes fadeIn {
    from { opacity:0; transform:translateY(-8px); }
    to   { opacity:1; transform:translateY(0); }
}
.notif-item-danger {
    background: rgba(255,75,75,0.08);
    border: 1px solid rgba(255,75,75,0.4);
    border-left: 3px solid #FF4B4B;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
    animation: fadeIn 0.3s ease;
}
.notif-item-warning {
    background: rgba(255,179,71,0.08);
    border: 1px solid rgba(255,179,71,0.4);
    border-left: 3px solid #FFB347;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
    animation: fadeIn 0.3s ease;
}
.notif-item-success {
    background: rgba(0,212,170,0.08);
    border: 1px solid rgba(0,212,170,0.4);
    border-left: 3px solid #00D4AA;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
    animation: fadeIn 0.3s ease;
}
.notif-item-info {
    background: rgba(74,144,217,0.08);
    border: 1px solid rgba(74,144,217,0.4);
    border-left: 3px solid #4A90D9;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
    animation: fadeIn 0.3s ease;
}
.notif-title {
    font-weight: 700;
    font-size: 0.88rem;
    color: #FFFFFF;
    margin-bottom: 2px;
}
.notif-msg {
    font-size: 0.8rem;
    color: #8B8FA8;
    line-height: 1.4;
}
</style>
""", unsafe_allow_html=True)

import datetime

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'currency' not in st.session_state:
    st.session_state.currency = 'INR'
if 'show_notif_center' not in st.session_state:
    st.session_state.show_notif_center = False
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0
if 'lockout_until' not in st.session_state:
    st.session_state.lockout_until = None
if 'auth_step' not in st.session_state:
    st.session_state.auth_step = "AUTH"
if 'auth_username' not in st.session_state:
    st.session_state.auth_username = ""
if 'auth_user_id' not in st.session_state:
    st.session_state.auth_user_id = None
if 'auth_otp_code' not in st.session_state:
    st.session_state.auth_otp_code = ""
if 'auth_remember_me' not in st.session_state:
    st.session_state.auth_remember_me = False
# Fields used only during the signup → OTP verification flow
if 'signup_pending_user_id' not in st.session_state:
    st.session_state.signup_pending_user_id = None
if 'signup_pending_username' not in st.session_state:
    st.session_state.signup_pending_username = ""
if 'signup_pending_email' not in st.session_state:
    st.session_state.signup_pending_email = ""
if 'signup_otp_code' not in st.session_state:
    st.session_state.signup_otp_code = ""
# Fields used only during forgot password flow
if 'reset_otp_code' not in st.session_state:
    st.session_state.reset_otp_code = ""
if 'reset_email' not in st.session_state:
    st.session_state.reset_email = ""
if 'reset_user_id' not in st.session_state:
    st.session_state.reset_user_id = None

# ── SESSION RESTORE ───────────────────────────────────────────────────────────
# MUST run before the timeout check so the token is read before last_active
# is evaluated. On a fresh page load session_state is empty — restore first.
params = st.query_params
if not st.session_state.logged_in:
    if 'session_token' in params:
        from utils.auth import verify_session_token
        res = verify_session_token(params['session_token'])
        if res:
            uid, u_name = res
            st.session_state.logged_in  = True
            st.session_state.username   = u_name
            st.session_state.user_id    = uid
            # Reset last_active so the timeout doesn't fire immediately
            st.session_state.last_active = datetime.datetime.now()

# Restore active page from URL
if st.session_state.logged_in and 'page' in params:
    _page_from_url = params['page']
    _nav_items_check = [
        "Dashboard", "Add Expense", "Income", "Anomalies", "AI Coach",
        "Budgets", "Reports", "Splits", "Savings", "Guilt-Free", "Streaks",
        "Bill Calendar", "Net Worth", "Summary", "Settings"
    ]
    if _page_from_url in _nav_items_check:
        st.session_state.current_page = _page_from_url

# ── INACTIVITY TIMEOUT ────────────────────────────────────────────────────────
# Only runs when logged in AND last_active is already set (not on fresh load).
# Does NOT clear query_params — session_token stays so refresh still works.
TIMEOUT_MINUTES = 30
if ('last_active' in st.session_state
        and st.session_state.logged_in
        and st.session_state.last_active is not None):
    elapsed = (datetime.datetime.now() - st.session_state.last_active).total_seconds()
    if elapsed > TIMEOUT_MINUTES * 60:
        st.session_state.logged_in   = False
        st.session_state.user_id     = None
        st.session_state.username    = ''
        st.session_state.messages    = []
        st.session_state.last_active = None
        # Clear token on genuine timeout — user must log in again
        st.query_params.clear()
        st.warning("Session timed out due to inactivity. Please log in again.")
        st.rerun()

st.session_state.last_active = datetime.datetime.now()

# ── AUTH PAGE ─────────────────────────────────────────────────────────────────
if not is_logged_in():
    # Lockout check (Rate limiting brute force protection)
    if st.session_state.lockout_until:
        lockout_diff = (st.session_state.lockout_until - datetime.datetime.now()).total_seconds()
        if lockout_diff > 0:
            st.session_state.auth_step = "LOCKED"
        else:
            st.session_state.lockout_until = None
            st.session_state.auth_step = "AUTH"

    left, right = st.columns([1.2, 0.8])

    with left:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="margin-bottom: 2.5rem; max-width: 280px; filter: drop-shadow(0 0 15px rgba(0, 242, 168, 0.2));">
            {LOGO_FULL_SVG}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <h1 style='font-size:3.5rem; font-weight:900; color:#FFFFFF; line-height:1.1; margin:0 0 1rem 0; letter-spacing: -0.04em;'>
            AI Personal<br>
            <span style='background:linear-gradient(135deg,#00F2A8,#00D4FF,#6366F1); -webkit-background-clip:text; -webkit-text-fill-color:transparent; display: inline-block;'>
                Finance Hub
            </span>
        </h1>
        <p style='color:#94A3B8; font-size:1.15rem; margin:0 0 2.5rem 0; line-height:1.6; font-weight: 400;'>
            Understand your money. Detect unusual spending.<br>
            Build smarter financial habits with AI.
        </p>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="login-feature-grid">
            <div class="login-feature-card">
                <span class="feature-icon dashboard-icon"></span>
                <span class="feature-label">Smart Dashboard</span>
            </div>
            <div class="login-feature-card">
                <span class="feature-icon anomaly-icon"></span>
                <span class="feature-label">Anomaly Detection</span>
            </div>
            <div class="login-feature-card">
                <span class="feature-icon budget-icon"></span>
                <span class="feature-label">Budget Tracking</span>
            </div>
            <div class="login-feature-card">
                <span class="feature-icon coach-icon"></span>
                <span class="feature-label">AI Coach</span>
            </div>
            <div class="login-feature-card">
                <span class="feature-icon health-icon"></span>
                <span class="feature-label">Health Score</span>
            </div>
            <div class="login-feature-card">
                <span class="feature-icon reports-icon"></span>
                <span class="feature-label">CSV Reports</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="login-trust-container">
            <div class="login-trust-badge">
                <span class="trust-icon shield-icon"></span>
                <span>Bank-grade security</span>
            </div>
            <div class="login-trust-badge">
                <span class="trust-icon lock-icon"></span>
                <span>Private data</span>
            </div>
            <div class="login-trust-badge">
                <span class="trust-icon sparkles-icon"></span>
                <span>Powered by AI</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        with st.container(key="login_panel"):
            if st.session_state.auth_step == "LOCKED":
                lockout_diff = 0
                if st.session_state.lockout_until:
                    lockout_diff = int((st.session_state.lockout_until - datetime.datetime.now()).total_seconds())
                
                if lockout_diff <= 0:
                    st.session_state.auth_step = "AUTH"
                    st.session_state.lockout_until = None
                    st.rerun()
                
                st.markdown(f"""
                <div class="lockout-panel">
                    <div class="lockout-shield-icon"></div>
                    <h2 style="color:#FFFFFF; font-size:1.4rem; font-weight:800; margin:0 0 0.5rem 0;">Account Locked</h2>
                    <p style="color:#94A3B8; font-size:0.88rem; margin:0 0 1rem 0;">Too many failed login attempts. For your security, access has been restricted temporarily.</p>
                    <div class="lockout-timer" id="lockout-countdown">{lockout_diff}s</div>
                    <p style="color:#FFB347; font-size:0.8rem; font-weight:600; margin-top:0.5rem;">Please wait before trying again.</p>
                </div>
                """, unsafe_allow_html=True)
                
                import streamlit.components.v1 as components
                components.html(f"""
                <script>
                    let timeLeft = {lockout_diff};
                    let doc = document;
                    try {{
                        if (window.parent && window.parent.document) {{
                            doc = window.parent.document;
                        }}
                    }} catch(e) {{
                        doc = document;
                    }}
                    const timerEl = doc.getElementById('lockout-countdown');
                    if (timerEl) {{
                        const interval = setInterval(() => {{
                            timeLeft--;
                            if (timeLeft <= 0) {{
                                clearInterval(interval);
                                timerEl.textContent = "Ready";
                            }} else {{
                                timerEl.textContent = timeLeft + "s";
                            }}
                        }}, 1000);
                    }}
                </script>
                """, height=0)
                
                if st.button("Check Lockout Status", use_container_width=True):
                    st.rerun()

            elif st.session_state.auth_step == "FORGOT_PASSWORD":
                # ── STEP 1: Enter registered email ───────────────────────────
                st.markdown("""
                <div style='text-align:center; margin-bottom: 1.5rem;'>
                    <h2 style='color:#FFFFFF; margin:0; font-size:1.6rem; font-weight:800;'>
                        Reset Password
                    </h2>
                    <p style='color:#94A3B8; font-size:0.88rem; margin:6px 0 1rem 0;'>
                        Enter your registered email address.<br>
                        We'll send a 6-digit reset code to it.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                with st.form("forgot_form"):
                    reset_email_input = st.text_input(
                        "Registered Email Address",
                        placeholder="you@example.com"
                    )
                    send_btn = st.form_submit_button(
                        "Send Reset Code",
                        use_container_width=True,
                        type="primary"
                    )

                if send_btn:
                    if not reset_email_input.strip():
                        st.error("Please enter your email address.")
                    else:
                        from utils.db import get_user_by_email
                        from utils.auth import generate_otp, send_otp_email
                        user_row = get_user_by_email(reset_email_input.strip().lower())
                        if user_row is None:
                            st.error("No account found with that email address.")
                        else:
                            otp = generate_otp()
                            ok, detail = send_otp_email(
                                reset_email_input.strip().lower(),
                                otp,
                                user_row[1]  # username
                            )
                            if not ok:
                                st.error(f"Could not send reset email: {detail}")
                            else:
                                import sqlite3
                                st.session_state.reset_otp_code = otp
                                st.session_state.reset_email    = reset_email_input.strip().lower()
                                st.session_state.reset_user_id  = user_row[0]
                                st.session_state.auth_step      = "RESET_PASSWORD"
                                st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Back to Sign In", key="forgot_back_btn",
                             use_container_width=True):
                    st.session_state.auth_step = "AUTH"
                    st.rerun()

            elif st.session_state.auth_step == "RESET_PASSWORD":
                # ── STEP 2: Verify OTP + set new password ────────────────────
                st.markdown(f"""
                <div style='text-align:center; margin-bottom: 1.5rem;'>
                    <h2 style='color:#FFFFFF; margin:0; font-size:1.6rem; font-weight:800;'>
                        Enter Reset Code
                    </h2>
                    <p style='color:#94A3B8; font-size:0.88rem; margin:6px 0 1rem 0;'>
                        A 6-digit reset code was sent to<br>
                        <strong style='color:#00D4AA;'>{st.session_state.reset_email}</strong>
                    </p>
                </div>
                """, unsafe_allow_html=True)

                with st.form("reset_form"):
                    otp_entered = st.text_input(
                        "Reset Code",
                        placeholder="Enter the 6-digit code",
                        max_chars=6
                    )
                    new_pwd = st.text_input(
                        "New Password", type="password",
                        placeholder="Min 8 characters"
                    )
                    confirm_pwd = st.text_input(
                        "Confirm New Password", type="password",
                        placeholder="Repeat new password"
                    )
                    reset_btn = st.form_submit_button(
                        "Reset Password",
                        use_container_width=True,
                        type="primary"
                    )

                    if reset_btn:
                        from utils.auth import validate_password_strength, hash_password
                        if not otp_entered.strip():
                            st.error("Please enter the reset code.")
                        elif otp_entered.strip() != st.session_state.reset_otp_code:
                            st.error("Incorrect reset code. Please check your email.")
                        elif not new_pwd or not confirm_pwd:
                            st.error("Please fill in both password fields.")
                        elif new_pwd != confirm_pwd:
                            st.error("Passwords do not match.")
                        else:
                            is_strong, strength_msg = validate_password_strength(new_pwd)
                            if not is_strong:
                                st.error(strength_msg)
                            else:
                                import sqlite3 as _sq
                                from utils.db import get_connection
                                conn = get_connection()
                                conn.execute(
                                    'UPDATE users SET password_hash=? WHERE id=?',
                                    (hash_password(new_pwd),
                                     st.session_state.reset_user_id)
                                )
                                conn.commit()
                                conn.close()
                                # Clear reset state
                                st.session_state.reset_otp_code = ""
                                st.session_state.reset_email    = ""
                                st.session_state.reset_user_id  = None
                                st.session_state.auth_step      = "AUTH"
                                st.success("Password reset successfully! You can now sign in.")
                                st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Back to Sign In", key="reset_back_btn",
                             use_container_width=True):
                    st.session_state.reset_otp_code = ""
                    st.session_state.reset_email    = ""
                    st.session_state.reset_user_id  = None
                    st.session_state.auth_step      = "AUTH"
                    st.rerun()

            elif st.session_state.auth_step == "OTP":
                # ── SIGNUP EMAIL VERIFICATION STEP ───────────────────────────
                # This step is reached ONLY from the Create Account flow.
                # Login never enters this branch — login goes directly to the
                # dashboard on success.
                pending_email    = st.session_state.signup_pending_email
                pending_username = st.session_state.signup_pending_username

                st.markdown(f"""
                <div style='text-align:center; margin-bottom: 1.5rem;'>
                    <h2 style='color:#FFFFFF; margin:0; font-size:1.6rem; font-weight:800; letter-spacing: -0.02em;'>
                        Verify Your Email
                    </h2>
                    <p style='color:#94A3B8; font-size:0.88rem; margin:6px 0 1rem 0;'>
                        A 6-digit verification code has been sent to<br>
                        <strong style='color:#00D4AA;'>{pending_email}</strong>
                    </p>
                    <div class="otp-badge">Account Verification</div>
                </div>
                """, unsafe_allow_html=True)

                # Console-fallback notice removed — SMTP is now required.

                with st.form("otp_form"):
                    otp_input = st.text_input(
                        "Verification Code",
                        placeholder="Enter the 6-digit code from your email",
                        max_chars=6
                    )
                    st.markdown("<br>", unsafe_allow_html=True)
                    verify_btn = st.form_submit_button(
                        "Verify & Activate Account",
                        use_container_width=True,
                        type="primary"
                    )

                if verify_btn:
                    if not otp_input.strip():
                        st.error("Please enter the verification code.")
                    elif otp_input.strip() == st.session_state.signup_otp_code:
                        # ── Mark account as verified in DB ───────────────────
                        from utils.db import mark_user_verified, log_login_activity
                        mark_user_verified(st.session_state.signup_pending_user_id)

                        # ── Auto-login: set session immediately ───────────────
                        st.session_state.logged_in  = True
                        st.session_state.user_id    = st.session_state.signup_pending_user_id
                        st.session_state.username   = st.session_state.signup_pending_username

                        # Persist session so page refresh keeps user logged in
                        st.query_params['session_token'] = generate_session_token(
                            st.session_state.signup_pending_user_id,
                            st.session_state.signup_pending_username
                        )

                        log_login_activity(
                            st.session_state.signup_pending_user_id,
                            "Signup Verified",
                            "0.0.0.0"
                        )

                        # ── Clear all signup temp state ───────────────────────
                        st.session_state.auth_step                = "AUTH"
                        st.session_state.signup_otp_code          = ""
                        st.session_state.signup_pending_user_id   = None
                        st.session_state.signup_pending_username  = ""
                        st.session_state.signup_pending_email     = ""

                        st.success(f"Welcome to Finelyt, {st.session_state.username}! 🎉")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Incorrect verification code. Please check your email and try again.")

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Cancel & Return to Sign In", use_container_width=True):
                    st.session_state.auth_step                = "AUTH"
                    st.session_state.signup_otp_code          = ""
                    st.session_state.signup_pending_user_id   = None
                    st.session_state.signup_pending_username  = ""
                    st.session_state.signup_pending_email     = ""
                    st.rerun()

            else: # AUTH Step
                st.markdown("""
                <div style='text-align:center; margin-bottom: 1.5rem;'>
                    <h2 style='color:#FFFFFF; margin:0; font-size:1.6rem; font-weight:800; letter-spacing: -0.02em;'>
                        Welcome Back
                    </h2>
                    <p style='color:#94A3B8; font-size:0.88rem; margin:6px 0 0 0;'>
                        Log in to manage your account
                    </p>
                </div>
                """, unsafe_allow_html=True)

                tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

                with tab_login:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown('<div id="login-username-warning" class="field-error-msg" style="display:none;"></div>', unsafe_allow_html=True)

                    with st.form("login_form"):
                        username = st.text_input(
                            "Username / Email", placeholder="Enter your username or email", key="login_username_input"
                        )
                        password = st.text_input(
                            "Password", type="password",
                            placeholder="Enter your password", key="login_password_input"
                        )
                        remember_me = st.checkbox(
                            "Remember me on this device",
                            key="remember_me_check",
                            help="Keep me logged in for 30 days even after closing the browser"
                        )
                        st.markdown("<br>", unsafe_allow_html=True)
                        login_btn = st.form_submit_button(
                            "Sign In",
                            use_container_width=True,
                            type="primary"
                        )

                    # Forgot Password link — outside the form
                    st.markdown(
                        "<p style='text-align:center;margin-top:0.5rem;'>"
                        "<span style='color:#94A3B8;font-size:0.85rem;'>Forgot your password? </span>"
                        "</p>",
                        unsafe_allow_html=True
                    )
                    if st.button("Reset Password", key="forgot_pwd_btn",
                                 use_container_width=False):
                        st.session_state.auth_step = "FORGOT_PASSWORD"
                        st.rerun()

                    if login_btn:
                        if not username or not password:
                            st.error("Please enter both fields.")
                        else:
                            with st.spinner("Authenticating..."):
                                success, user_id, message = login_user(
                                    username, password
                                )
                            if success:
                                st.session_state.logged_in   = True
                                st.session_state.user_id     = user_id
                                st.session_state.username    = username
                                st.session_state.last_active = datetime.datetime.now()

                                # Always write session_token so page refresh
                                # keeps the user logged in.
                                token = generate_session_token(user_id, username)
                                st.query_params['session_token'] = token
                                if remember_me:
                                    st.query_params['remember'] = '1'

                                from utils.db import log_login_activity
                                log_login_activity(user_id, "Web Login", "0.0.0.0")
                                st.session_state.login_attempts = 0
                                st.rerun()
                            elif message.startswith("LOCKED_OUT:"):
                                sec = int(message.split(":")[1])
                                st.session_state.lockout_until = (
                                    datetime.datetime.now()
                                    + datetime.timedelta(seconds=sec)
                                )
                                st.session_state.auth_step = "LOCKED"
                                st.rerun()
                            elif message.startswith("EMAIL_NOT_VERIFIED:"):
                                st.error(
                                    "Your email address has not been verified. "
                                    "Please sign up again and complete the verification step."
                                )
                            else:
                                st.error(message)

                with tab_register:
                    st.markdown("<br>", unsafe_allow_html=True)

                    new_username = st.text_input(
                        "Username",
                        placeholder="Min 3 characters, no spaces",
                        key="reg_username"
                    )
                    new_email = st.text_input(
                        "Email Address",
                        placeholder="you@example.com",
                        key="reg_email"
                    )
                    new_password = st.text_input(
                        "Password", type="password",
                        placeholder="Min 8 characters",
                        key="reg_password"
                    )

                    # Live strength — updates on every keystroke
                    pw = st.session_state.get("reg_password", "")
                    if pw:
                        import re as _re
                        checks = {
                            "min8":    len(pw) >= 8,
                            "upper":   bool(_re.search(r'[A-Z]', pw)),
                            "lower":   bool(_re.search(r'[a-z]', pw)),
                            "number":  bool(_re.search(r'\d', pw)),
                            "special": bool(_re.search(r'[@#$^&*!?%]', pw)),
                        }
                        score = sum(checks.values())
                        strength_map = {
                            0: ("Very Weak",  "#F05252", "10%"),
                            1: ("Very Weak",  "#F05252", "15%"),
                            2: ("Weak",       "#F59E0B", "30%"),
                            3: ("Fair",       "#FBBF24", "55%"),
                            4: ("Strong",     "#3B82F6", "75%"),
                            5: ("Very Strong","#00C896", "100%"),
                        }
                        strength, color, width = strength_map[score]

                        st.markdown(f"""
                        <div style='margin:4px 0 10px;'>
                            <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
                                <span style='font-size:0.75rem;color:#8892AA;'>Password strength</span>
                                <span style='font-size:0.75rem;font-weight:700;color:{color};'>{strength}</span>
                            </div>
                            <div style='background:#1E2640;border-radius:999px;height:5px;overflow:hidden;'>
                                <div style='width:{width};height:5px;border-radius:999px;
                                            background:{color};transition:width 0.3s ease;'></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        rules = [
                            ("min8",    "Minimum 8 characters"),
                            ("upper",   "At least 1 uppercase letter (A-Z)"),
                            ("lower",   "At least 1 lowercase letter (a-z)"),
                            ("number",  "At least 1 number (0-9)"),
                            ("special", "At least 1 special character (@#$^&*!?%)"),
                        ]
                        html = ""
                        for _k, _lbl in rules:
                            _c  = "#00C896" if checks[_k] else "#F05252"
                            _ic = "✓" if checks[_k] else "✕"
                            html += (f"<div style='display:flex;align-items:center;"
                                    f"gap:8px;margin-bottom:3px;'>"
                                    f"<span style='color:{_c};font-weight:700;"
                                    f"font-size:0.8rem;'>{_ic}</span>"
                                    f"<span style='color:{_c};font-size:0.8rem;'>"
                                    f"{_lbl}</span></div>")
                        st.markdown(f"<div style='margin-bottom:10px;'>{html}</div>",
                                    unsafe_allow_html=True)

                    confirm_password = st.text_input(
                        "Confirm Password", type="password",
                        placeholder="Repeat your password",
                        key="reg_confirm"
                    )

                    conf = st.session_state.get("reg_confirm", "")
                    if conf and pw:
                        if pw == conf:
                            st.markdown("<p style='color:#00C896;font-size:0.8rem;"
                                        "margin:2px 0 8px;'>Passwords match</p>",
                                        unsafe_allow_html=True)
                        else:
                            st.markdown("<p style='color:#F05252;font-size:0.8rem;"
                                        "margin:2px 0 8px;'>Passwords do not match</p>",
                                        unsafe_allow_html=True)

                    terms = st.checkbox(
                        "I agree my data stays private and secure",
                        key="reg_terms"
                    )
                    st.markdown("<br>", unsafe_allow_html=True)
                    register_btn = st.button(
                        "Create Account",
                        use_container_width=True,
                        type="primary", key="reg_submit"
                    )

                    if register_btn:
                        nu = st.session_state.get("reg_username", "").strip()
                        ne = st.session_state.get("reg_email", "").strip()
                        np = st.session_state.get("reg_password", "")
                        nc = st.session_state.get("reg_confirm", "")
                        nt = st.session_state.get("reg_terms", False)

                        # ── Client-side pre-validation ─────────────────────
                        if not nu or not ne or not np or not nc:
                            st.error("Please fill in all fields.")
                        elif not nt:
                            st.error("Please agree to the terms.")
                        elif np != nc:
                            st.error("Passwords do not match.")
                        else:
                            with st.spinner("Creating your account..."):
                                success, result = register_user(nu, ne, np)

                            if not success:
                                # result is an error message string
                                st.error(result)
                            else:
                                # result is the new user_id (int)
                                new_user_id = result
                                otp = generate_otp()
                                ok, send_detail = send_otp_email(ne, otp, nu)

                                if not ok:
                                    # Email delivery failed entirely — surface the error
                                    st.error(
                                        f"Account created but verification email could not be sent. "
                                        f"Error: {send_detail}. "
                                        f"Please contact support or check your SMTP configuration."
                                    )
                                else:
                                    # Store OTP + pending signup info in session
                                    st.session_state.signup_otp_code         = otp
                                    st.session_state.signup_pending_user_id  = new_user_id
                                    st.session_state.signup_pending_username = nu
                                    st.session_state.signup_pending_email    = ne
                                    st.session_state.auth_step = "OTP"
                                    st.rerun()

        import streamlit.components.v1 as components
        components.html(r"""
        <script>
        const setupPasswordValidation = () => {
            let doc = document;
            try {
                if (window.parent && window.parent.document) {
                    doc = window.parent.document;
                }
            } catch(e) {
                doc = document;
            }
            
            const validateUsernameInput = (val, errorEl) => {
                if (!errorEl) return;
                val = val.trim();
                if (val.length === 0) {
                    errorEl.style.display = 'none';
                    return;
                }
                if (val.includes('@')) {
                    const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
                    if (!emailRegex.test(val)) {
                        errorEl.innerHTML = '<span style="margin-right:4px;">⚠</span> Invalid email address format';
                        errorEl.style.display = 'flex';
                    } else {
                        errorEl.style.display = 'none';
                    }
                } else {
                    if (val.length < 3) {
                        errorEl.innerHTML = '<span style="margin-right:4px;">⚠</span> Username must be at least 3 characters';
                        errorEl.style.display = 'flex';
                    } else if (/\s/.test(val)) {
                        errorEl.innerHTML = '<span style="margin-right:4px;">⚠</span> Username cannot contain spaces';
                        errorEl.style.display = 'flex';
                    } else {
                        errorEl.style.display = 'none';
                    }
                }
            };

            const forms = doc.querySelectorAll('div[data-testid="stForm"]');
            forms.forEach(form => {
                const button = form.querySelector('button');
                if (!button) return;
                const buttonText = button.textContent || '';
                
                if (buttonText.includes('Create Account')) {
                    const regUser = form.querySelector('input[type="text"]');
                    const allPassFields = form.querySelectorAll('input[type="password"]');
                    const regPass = allPassFields.length > 0 ? allPassFields[0] : null;
                    const regWarning = doc.getElementById('register-username-warning');

                    if (regUser && regWarning && !regUser.dataset.hasListener) {
                        regUser.dataset.hasListener = "true";
                        regUser.addEventListener('input', (e) => {
                            validateUsernameInput(e.target.value, regWarning);
                        });
                    }

                    if (regPass && !regPass.dataset.hasListener) {
                        regPass.dataset.hasListener = "true";
                        regPass.addEventListener('input', (e) => {
                            const val = e.target.value;
                            
                            const hasLength = val.length >= 8;
                            const hasUpper = /[A-Z]/.test(val);
                            const hasLower = /[a-z]/.test(val);
                            const hasNumber = /[0-9]/.test(val);
                            const hasSpecial = /[@#$%^&*!?]/.test(val);
                            
                            updateReq(doc, 'req-length', hasLength);
                            updateReq(doc, 'req-upper', hasUpper);
                            updateReq(doc, 'req-lower', hasLower);
                            updateReq(doc, 'req-number', hasNumber);
                            updateReq(doc, 'req-special', hasSpecial);
                            
                            let score = 0;
                            if (val.length >= 8) score++;
                            if (hasUpper && hasLower) score++;
                            if (hasNumber) score++;
                            if (hasSpecial) score++;
                            if (val.length >= 12) score++;
                            
                            const bar = doc.getElementById('strength-bar');
                            const label = doc.getElementById('strength-label');
                            if (!bar || !label) return;
                            
                            if (val.length === 0) {
                                bar.style.width = '0%';
                                bar.style.backgroundColor = '#EF4444';
                                label.textContent = 'Weak';
                                label.style.color = '#EF4444';
                            } else if (score <= 2) {
                                bar.style.width = '25%';
                                bar.style.backgroundColor = '#EF4444';
                                label.textContent = 'Weak';
                                label.style.color = '#EF4444';
                            } else if (score === 3) {
                                bar.style.width = '50%';
                                bar.style.backgroundColor = '#F59E0B';
                                label.textContent = 'Medium';
                                label.style.color = '#F59E0B';
                            } else if (score === 4) {
                                bar.style.width = '75%';
                                bar.style.backgroundColor = '#00D4FF';
                                label.textContent = 'Strong';
                                label.style.color = '#00D4FF';
                            } else {
                                bar.style.width = '100%';
                                bar.style.backgroundColor = '#00F2A8';
                                label.textContent = 'Very Strong';
                                label.style.color = '#00F2A8';
                            }
                        });
                    }
                } else if (buttonText.includes('Sign In')) {
                    const loginUser = form.querySelector('input[type="text"]');
                    const loginWarning = doc.getElementById('login-username-warning');

                    if (loginUser && loginWarning && !loginUser.dataset.hasListener) {
                        loginUser.dataset.hasListener = "true";
                        loginUser.addEventListener('input', (e) => {
                            validateUsernameInput(e.target.value, loginWarning);
                        });
                    }
                }
            });
        };

        const updateReq = (doc, id, isValid) => {
            const el = doc.getElementById(id);
            if (!el) return;
            if (isValid) {
                el.className = 'validation-check valid';
            } else {
                el.className = 'validation-check invalid';
            }
        };

        setInterval(() => {
            setupPasswordValidation();
        }, 800);
        </script>
        """, height=0)

    st.stop()

# ── MAIN APP ──────────────────────────────────────────────────────────────────
user_id  = st.session_state.user_id
username = st.session_state.username

# ── SMART NOTIFICATIONS ───────────────────────────────────────────────────────
_live_notifs = []
_unread = 0

try:
    from utils.notifications import generate_notifications
    from utils.db import (
        get_all_expenses, get_all_income,
        set_notifs_cleared, get_notifs_cleared_at
    )
    from datetime import datetime, timedelta

    _df_exp = get_all_expenses(user_id)
    _df_inc = get_all_income(user_id)

    # Check DB for cleared timestamp
    cleared_at_str = get_notifs_cleared_at(user_id)
    show_notifs = True

    if cleared_at_str:
        try:
            cleared_at = None
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                try:
                    cleared_at = datetime.strptime(cleared_at_str, fmt)
                    break
                except ValueError:
                    continue
            if cleared_at:
                elapsed = datetime.utcnow() - cleared_at
                if elapsed < timedelta(hours=24):
                    show_notifs = False
        except Exception:
            show_notifs = True

    if show_notifs:
        _live_notifs = generate_notifications(user_id, _df_exp, _df_inc)
    else:
        _live_notifs = []

    _unread = len(_live_notifs)
except Exception:
    pass

# ── TOP NAVBAR & NAVIGATION ───────────────────────────────────────────────────
_nav_items = [
    "Dashboard", "Add Expense", "Income", "Anomalies", "AI Coach",
    "Budgets", "Reports", "Splits", "Savings", "Guilt-Free", "Streaks",
    "Bill Calendar", "Net Worth", "Summary"
]
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

with st.container(key="global_header"):
    col_left, col_center, col_right = st.columns([1.6, 9.0, 1.4])

    with col_left:
        st.markdown(f"""
        <div class="fc-logo-container" style="display: flex; align-items: center; gap: 12px; height: 38px;">
            <div style="width: 155px; height: 38px;">
                {LOGO_FULL_SVG}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_center:
        _nav_index = (
            _nav_items.index(st.session_state.current_page)
            if st.session_state.current_page in _nav_items
            else 0
        )
        selected_page = st.radio(
            "Navigation",
            options=_nav_items,
            index=_nav_index,
            horizontal=True,
            key="top_navigation",
            label_visibility="collapsed"
        )
        # Track the last nav item the user explicitly clicked using a
        # separate session state key. Only navigate when that key changes —
        # this prevents the radio's default index from auto-navigating.
        if 'last_nav_click' not in st.session_state:
            st.session_state.last_nav_click = selected_page

        if selected_page != st.session_state.last_nav_click:
            # User explicitly clicked a different nav item
            st.session_state.last_nav_click = selected_page
            st.session_state.current_page = selected_page
            st.query_params['page'] = selected_page
            st.rerun()

    with col_right:
        right_col1, right_col2, right_col3 = st.columns([1.0, 1.0, 1.0])
        with right_col1:
            bell_label = f"({_unread})" if _unread > 0 else ""
            btn_key = "alerts_button_unread" if _unread > 0 else "alerts_button"
            if st.button(
                ":material/notifications:",
                key=btn_key,
                use_container_width=True,
                help="View notifications"
            ):
                st.session_state.show_notif_center = \
                    not st.session_state.get('show_notif_center', False)

        with right_col2:
            if st.button(
                ":material/person:",
                key="profile_button",
                use_container_width=True,
                help="View profile settings"
            ):
                st.session_state.current_page = "Settings"
                st.query_params['page'] = "Settings"
                # Sync last_nav_click so the radio doesn't fire on next rerun
                st.session_state.last_nav_click = st.session_state.get(
                    'last_nav_click', _nav_items[0]
                )
                st.rerun()

        with right_col3:
            if st.button(
                ":material/logout:",
                key="logout_button",
                use_container_width=True,
                help="Logout"
            ):
                logout()
                st.query_params.clear()
                st.rerun()

# Always keep the URL in sync with the current page
if st.session_state.get('logged_in'):
    st.query_params['page'] = st.session_state.current_page

page = st.session_state.current_page

# ── NOTIFICATION CENTER PANEL ─────────────────────────────────────────────────
if st.session_state.get('show_notif_center', False):
    with st.container():
        st.markdown("<div class='fc-card'>", unsafe_allow_html=True)
        header_col, close_col = st.columns([5, 1])
        with header_col:
            st.markdown(
                f"**Notifications** "
                f"<span style='color:#94A3B8; font-size:0.8rem;'>"
                f"({_unread} active)</span>",
                unsafe_allow_html=True
            )
        with close_col:
            if st.button("Close", key="close_notif", use_container_width=True):
                st.session_state.show_notif_center = False
                st.rerun()

        if not _live_notifs:
            st.markdown("""
            <div style='text-align:center; padding:1.5rem;
                        background:var(--bg-card); border:1px solid var(--border);
                        border-radius:12px; color:var(--text-secondary);
                        margin-bottom:1rem;'>
                <p style='margin:0;'>All clear — no alerts right now.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            sorted_notifs = sorted(
                _live_notifs,
                key=lambda x: {
                    'high': 0, 'medium': 1, 'low': 2
                }.get(x.get('priority', 'medium'), 1)
            )
            for notif in sorted_notifs:
                css = f"notif-item-{notif['type']}"
                st.markdown(f"""
                <div class="{css}">
                    <div class="notif-title">
                        {notif['title']}
                    </div>
                    <div class="notif-msg">{notif['message']}</div>
                </div>
                """, unsafe_allow_html=True)

        if st.button(
            "Clear All",
            use_container_width=True,
            type="secondary",
            key="clear_notifs"
        ):
            try:
                from utils.db import set_notifs_cleared
                set_notifs_cleared(user_id)
            except Exception:
                pass
            st.session_state.show_notif_center = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.divider()

# ── ROUTING ───────────────────────────────────────────────────────────────────
if page == "Dashboard":
    from pages import dashboard
    dashboard.show(user_id=user_id)
elif page == "Add Expense":
    from pages import add_expense
    add_expense.show(user_id=user_id)
elif page == "Income":
    from pages import income
    income.show(user_id=user_id)
elif page == "Anomalies":
    from pages import anomalies
    anomalies.show(user_id=user_id)
elif page == "AI Coach":
    from pages import ai_coach
    ai_coach.show(user_id=user_id)
elif page == "Budgets":
    from pages import budgets
    budgets.show(user_id=user_id)
elif page == "Reports":
    from pages import reports
    reports.show(user_id=user_id)
elif page == "Splits":
    from pages import splits
    splits.show(user_id=user_id)
elif page == "Savings":
    from pages import savings
    savings.show(user_id=user_id)
elif page == "Guilt-Free":
    from pages import guiltfree
    guiltfree.show(user_id=user_id)
elif page == "Streaks":
    from pages import streaks
    streaks.show(user_id=user_id)
elif page == "Bill Calendar":
    from pages import bill_calendar
    bill_calendar.show(user_id=user_id)
elif page == "Summary":
    from pages import summary
    summary.show(user_id=user_id)
elif page == "Net Worth":
    from pages import networth
    networth.show(user_id=user_id)
elif page == "Settings":
    from pages import settings
    settings.show(user_id=user_id)

st.divider()
st.markdown("""
<div style='text-align:center; padding:1rem 0; margin-top:2rem;'>
    <div style='font-size:0.8rem; color:#94A3B8;'>
        Built with Python + Streamlit &nbsp;|&nbsp; Powered by Google Gemini
    </div>
</div>
""", unsafe_allow_html=True)

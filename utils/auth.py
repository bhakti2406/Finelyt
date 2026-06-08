import hashlib
import secrets
import hmac
import os
import re
import smtplib
import ssl
import datetime
import streamlit as st
from utils.db import (
    add_user, get_user, get_user_by_username_or_email,
    mark_user_verified,
    get_login_attempts, update_login_attempts, reset_login_attempts
)

# ── SECRETS ───────────────────────────────────────────────────────────────────

# Load .env so SMTP vars and SECRET_KEY are available when running via
# `streamlit run app.py` without a shell that pre-exports them.
try:
    from dotenv import load_dotenv
    # Use an explicit path so .env is found regardless of what directory
    # Streamlit is launched from. __file__ is utils/auth.py, so we go
    # one level up to reach the project root where .env lives.
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
    load_dotenv(dotenv_path=_env_path, override=False)
except ImportError:
    pass

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "finance_coach_production_secure_key_987654321"
)

# ── SMTP CONFIGURATION ────────────────────────────────────────────────────────
# Add these five variables to your .env file to enable real email delivery:
#
#   SMTP_HOST=smtp.gmail.com
#   SMTP_PORT=587
#   SMTP_USER=you@gmail.com
#   SMTP_PASSWORD=your_app_password_here
#   SMTP_FROM=Finelyt <you@gmail.com>
#
# If any variable is missing, email sending returns an error.
# The app will show the error to the user during signup.

SMTP_HOST     = os.getenv("SMTP_HOST", "")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM     = os.getenv("SMTP_FROM", SMTP_USER)

def _smtp_configured() -> bool:
    """Returns True only when all four required SMTP env vars are set."""
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)

# ── PASSWORD UTILITIES ────────────────────────────────────────────────────────

def hash_password(password, salt=None):
    """Secure PBKDF2 hashing with SHA-256, 100,000 iterations and a random salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    iterations = 100000
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${dk.hex()}"

def verify_password(password, stored_hash):
    """Verifies a password against a stored hash, supporting both PBKDF2 and legacy SHA-256."""
    if not stored_hash.startswith("pbkdf2_sha256$"):
        return stored_hash == hashlib.sha256(password.encode()).hexdigest()
    try:
        parts = stored_hash.split("$")
        if len(parts) != 4:
            return False
        _, iterations, salt, hash_hex = parts
        dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), int(iterations))
        return dk.hex() == hash_hex
    except Exception:
        return False

def validate_password_strength(password):
    """Checks password complexity and blacklists common weak values."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least 1 uppercase letter (A-Z)."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least 1 lowercase letter (a-z)."
    if not re.search(r"\d", password):
        return False, "Password must contain at least 1 number (0-9)."
    if not re.search(r"[@#$%\^&*!?]", password):
        return False, "Password must contain at least 1 special character (@#$%^&*!?)."
    weak_passwords = ["password", "123456", "12345678", "qwerty",
                      "admin", "finance", "coach", "welcome"]
    if password.lower() in weak_passwords:
        return False, "Password is too common or weak."
    return True, ""

# ── SESSION TOKENS ────────────────────────────────────────────────────────────

def generate_session_token(user_id, username):
    """Generates a secure cryptographically signed HMAC token for session recovery."""
    message = f"{user_id}:{username}".encode()
    signature = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).hexdigest()
    return f"{user_id}:{username}:{signature}"

def verify_session_token(token):
    """Verifies the integrity and authenticity of a session token."""
    if not token:
        return None
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return None
        user_id_str, username, signature = parts
        message = f"{user_id_str}:{username}".encode()
        expected_signature = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).hexdigest()
        if hmac.compare_digest(signature, expected_signature):
            return int(user_id_str), username
    except Exception:
        pass
    return None

# ── OTP EMAIL DELIVERY ────────────────────────────────────────────────────────

def generate_otp() -> str:
    """Returns a cryptographically random 6-digit OTP string."""
    return str(secrets.randbelow(900000) + 100000)

def send_otp_email(recipient_email: str, otp_code: str, username: str) -> tuple[bool, str]:
    """
    Sends the OTP to recipient_email via SMTP.

    Returns (True, "")  on success.
    Returns (False, error_message) on failure.

    If SMTP is not configured, returns (False, error_message).
    """
    if not _smtp_configured():
        return False, (
            "SMTP is not configured. Please add SMTP_HOST, SMTP_USER, "
            "and SMTP_PASSWORD to your .env file and restart the app."
        )

    subject = "Your Finelyt Verification Code"

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verify your Finelyt account</title>
</head>
<body style="margin:0;padding:0;background-color:#0A0F1D;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0A0F1D;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0" style="background-color:#111827;border-radius:16px;overflow:hidden;border:1px solid #1E2D3D;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#0D1F2D 0%,#0A2540 100%);padding:32px 40px;text-align:center;border-bottom:1px solid #1E2D3D;">
              <div style="display:inline-block;">
                <span style="font-size:26px;font-weight:900;letter-spacing:-0.5px;">
                  <span style="color:#00D4AA;">Fin</span><span style="color:#FFFFFF;">elyt</span>
                </span>
              </div>
              <p style="color:#64748B;font-size:13px;margin:6px 0 0 0;letter-spacing:0.5px;">
                AI FINANCE COACH
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px 40px 32px 40px;">
              <p style="color:#94A3B8;font-size:14px;margin:0 0 8px 0;">
                Hi <strong style="color:#E2E8F0;">{username}</strong>,
              </p>
              <h1 style="color:#FFFFFF;font-size:22px;font-weight:700;margin:0 0 16px 0;line-height:1.3;">
                Verify your email address
              </h1>
              <p style="color:#94A3B8;font-size:15px;line-height:1.6;margin:0 0 28px 0;">
                Use the verification code below to complete your Finelyt account setup.
                This code is valid for <strong style="color:#E2E8F0;">10 minutes</strong>.
              </p>

              <!-- OTP Box -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                <tr>
                  <td align="center" style="background-color:#0D1F2D;border:1px solid #00D4AA;border-radius:12px;padding:28px 20px;">
                    <p style="color:#64748B;font-size:12px;text-transform:uppercase;letter-spacing:2px;margin:0 0 12px 0;">
                      Verification Code
                    </p>
                    <p style="color:#00D4AA;font-size:42px;font-weight:900;letter-spacing:14px;margin:0;font-family:'Courier New',monospace;">
                      {otp_code}
                    </p>
                  </td>
                </tr>
              </table>

              <!-- Warning -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                <tr>
                  <td style="background-color:#1A1F35;border-left:3px solid #F59E0B;border-radius:0 8px 8px 0;padding:14px 16px;">
                    <p style="color:#F59E0B;font-size:13px;margin:0;line-height:1.5;">
                      <strong>Never share this code.</strong>
                      Finelyt will never ask for your verification code via phone or chat.
                    </p>
                  </td>
                </tr>
              </table>

              <p style="color:#64748B;font-size:13px;line-height:1.6;margin:0;">
                If you didn't create a Finelyt account, you can safely ignore this email.
                Someone may have entered your email address by mistake.
              </p>
            </td>
          </tr>

          <!-- Divider -->
          <tr>
            <td style="padding:0 40px;">
              <div style="border-top:1px solid #1E2D3D;"></div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:24px 40px;text-align:center;">
              <p style="color:#334155;font-size:12px;margin:0 0 6px 0;">
                This email was sent to <span style="color:#475569;">{recipient_email}</span>
              </p>
              <p style="color:#334155;font-size:12px;margin:0;">
                &copy; 2026 Finelyt &nbsp;·&nbsp; AI Finance Coach
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    # Plain text fallback for email clients that don't render HTML
    plain_fallback = f"""\
Hi {username},

Your Finelyt verification code is: {otp_code}

This code expires in 10 minutes. Do not share it with anyone.

If you did not create a Finelyt account, please ignore this email.

— The Finelyt Team
"""

    # Build a proper MIME multipart message so HTML renders in all clients
    import email.mime.multipart
    import email.mime.text
    import email.utils

    msg = email.mime.multipart.MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SMTP_FROM
    msg["To"]      = recipient_email
    msg["Date"]    = email.utils.formatdate(localtime=True)
    msg["Message-ID"] = email.utils.make_msgid(domain=SMTP_USER.split("@")[-1])

    msg.attach(email.mime.text.MIMEText(plain_fallback, "plain", "utf-8"))
    msg.attach(email.mime.text.MIMEText(html_body,      "html",  "utf-8"))

    message = msg

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, recipient_email, message.as_string())
        return True, ""
    except smtplib.SMTPAuthenticationError:
        return False, "SMTP authentication failed. Check SMTP_USER and SMTP_PASSWORD in .env."
    except smtplib.SMTPConnectError:
        return False, f"Could not connect to SMTP server {SMTP_HOST}:{SMTP_PORT}."
    except Exception as exc:
        return False, f"Email delivery error: {exc}"

# ── AUTHENTICATION ────────────────────────────────────────────────────────────

def login_user(identifier, password):
    """
    Authenticates a user by username OR email + password.

    Flow:
    1. Check for active account lockout.
    2. Look up user by username or email.
    3. Verify the password hash.
    4. Check that the account has been email-verified (is_verified = 1).
       Legacy accounts (created before this update) are grandfathered as
       verified so existing users are not locked out.
    5. On success clear login attempts and return (True, user_id, message).
    6. On failure increment attempt counter and return (False, None, message).
    """
    import sqlite3
    from utils.db import get_connection

    # 1. Lockout check
    attempts_info = get_login_attempts(identifier)
    if attempts_info:
        attempts, locked_until_str = attempts_info
        if locked_until_str:
            locked_until = datetime.datetime.fromisoformat(locked_until_str)
            diff = (locked_until - datetime.datetime.now()).total_seconds()
            if diff > 0:
                return False, None, f"LOCKED_OUT:{int(diff)}"
            else:
                reset_login_attempts(identifier)

    # 2. Fetch user — use sqlite3.Row so we access columns by name, not
    #    position.  This is safe regardless of ALTER TABLE column order.
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        'SELECT * FROM users WHERE username = ?', (identifier,)
    )
    user = cur.fetchone()
    if user is None and '@' in identifier:
        cur.execute(
            'SELECT * FROM users WHERE lower(email) = lower(?)', (identifier,)
        )
        user = cur.fetchone()
    conn.close()

    if user is None:
        _register_failed_attempt(identifier)
        return False, None, "Invalid username/email or password."

    user_id       = user['id']
    stored_hash   = user['password_hash']
    # is_verified may not exist in very old DB snapshots; treat as verified
    try:
        is_verified = user['is_verified']
    except IndexError:
        is_verified = 1

    # 3. Password check
    if not verify_password(password, stored_hash):
        _register_failed_attempt(identifier)
        attempts_info = get_login_attempts(identifier)
        attempts = attempts_info[0] if attempts_info else 1
        if attempts >= 5:
            return False, None, "LOCKED_OUT:30"
        return False, None, f"Invalid username/email or password. ({5 - attempts} attempts remaining)"

    # 4. Verified check
    if not is_verified:
        try:
            email_val = user['email'] or ''
        except Exception:
            email_val = ''
        return False, None, f"EMAIL_NOT_VERIFIED:{email_val}"

    # 5. Success
    reset_login_attempts(identifier)
    return True, user_id, "Login successful!"

def _register_failed_attempt(identifier):
    """Records a failed login attempt and locks the account after 5 failures."""
    attempts_info = get_login_attempts(identifier)
    attempts = (attempts_info[0] + 1) if attempts_info else 1
    locked_until = None
    if attempts >= 5:
        locked_until = (
            datetime.datetime.now() + datetime.timedelta(seconds=30)
        ).isoformat()
    update_login_attempts(identifier, attempts, locked_until)

def register_user(username, email, password):
    """
    Creates a new unverified user account.

    Parameters
    ----------
    username : str   — display name, min 3 chars, no spaces
    email    : str   — required, must be a valid email address
    password : str   — must pass strength validation

    Returns
    -------
    (True,  user_id)       — account row created; OTP must still be verified
    (False, error_message) — validation or DB error
    """
    # ── Validate username
    username = username.strip()
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if " " in username:
        return False, "Username cannot contain spaces."

    # ── Validate email
    email = email.strip().lower()
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_regex, email):
        return False, "Please enter a valid email address."

    # ── Validate password strength
    is_strong, strength_msg = validate_password_strength(password)
    if not is_strong:
        return False, strength_msg

    # ── Write to DB (is_verified = 0)
    password_hash = hash_password(password)
    success, result = add_user(username, password_hash, email=email)
    # result is user_id (int) on success or error string on failure
    return success, result

# ── SESSION STATE HELPERS ─────────────────────────────────────────────────────

def is_logged_in():
    return st.session_state.get('logged_in', False)

def get_current_user_id():
    return st.session_state.get('user_id', 1)

def get_current_username():
    return st.session_state.get('username', '')

def logout():
    st.session_state.logged_in = False
    st.session_state.user_id   = None
    st.session_state.username  = ''
    st.session_state.messages  = []
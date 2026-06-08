import sqlite3
import pandas as pd
import os
import streamlit as st

DB_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'data', 'finance.db'
)

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE,
            is_verified INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')

    # ── MIGRATE existing users table: add email and is_verified if absent ──
    # This runs on every startup but ALTER TABLE is a no-op if the column
    # already exists in SQLite — so it is safe to call repeatedly.
    existing_cols = [row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()]
    if 'email' not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if 'is_verified' not in existing_cols:
        # Existing users are grandfathered in as verified so they can still log in
        cursor.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 1")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            notes TEXT DEFAULT '',
            user_id INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            monthly_limit REAL NOT NULL,
            month TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, category, month)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            source TEXT NOT NULL,
            amount REAL NOT NULL,
            notes TEXT DEFAULT '',
            user_id INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            target_date TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            notifs_cleared_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_attempts (
            username TEXT PRIMARY KEY,
            attempts INTEGER DEFAULT 0,
            locked_until TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            device TEXT NOT NULL,
            ip TEXT NOT NULL,
            timestamp TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

# ── CACHE INVALIDATION ────────────────────────────────────────────────────────

def clear_cache():
    """Call this after any write operation to invalidate caches."""
    st.cache_data.clear()

# ── EXPENSE FUNCTIONS ─────────────────────────────────────────────────────────

def add_expense(date, category, amount, notes='', user_id=1):
    conn = get_connection()
    conn.execute(
        '''INSERT INTO expenses
           (date, category, amount, notes, user_id)
           VALUES (?, ?, ?, ?, ?)''',
        (str(date), category, float(amount), notes, user_id)
    )
    conn.commit()
    conn.close()
    clear_cache()

@st.cache_data(ttl=30, show_spinner=False)
def get_all_expenses(user_id=1):
    conn = get_connection()
    df = pd.read_sql_query(
        '''SELECT * FROM expenses
           WHERE user_id = ?
           ORDER BY date DESC, created_at DESC''',
        conn, params=(user_id,)
    )
    conn.close()
    return df

@st.cache_data(ttl=30, show_spinner=False)
def get_expenses_by_month(user_id=1, month=None):
    conn = get_connection()
    if month:
        df = pd.read_sql_query(
            '''SELECT * FROM expenses
               WHERE user_id = ?
               AND strftime('%Y-%m', date) = ?
               ORDER BY date DESC''',
            conn, params=(user_id, month)
        )
    else:
        from datetime import datetime
        current_month = datetime.now().strftime('%Y-%m')
        df = pd.read_sql_query(
            '''SELECT * FROM expenses
               WHERE user_id = ?
               AND strftime('%Y-%m', date) = ?
               ORDER BY date DESC''',
            conn, params=(user_id, current_month)
        )
    conn.close()
    return df

def delete_expense(expense_id, user_id=1):
    conn = get_connection()
    conn.execute(
        'DELETE FROM expenses WHERE id = ? AND user_id = ?',
        (expense_id, user_id)
    )
    conn.commit()
    conn.close()
    clear_cache()

@st.cache_data(ttl=30, show_spinner=False)
def get_expenses_by_date_range(start_date, end_date, user_id=1):
    conn = get_connection()
    df = pd.read_sql_query(
        '''SELECT * FROM expenses
           WHERE user_id = ? AND date BETWEEN ? AND ?
           ORDER BY date DESC''',
        conn, params=(user_id, str(start_date), str(end_date))
    )
    conn.close()
    return df

# ── BUDGET FUNCTIONS ──────────────────────────────────────────────────────────

def set_budget(user_id, category, monthly_limit, month):
    conn = get_connection()
    conn.execute(
        '''INSERT INTO budgets
           (user_id, category, monthly_limit, month)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(user_id, category, month)
           DO UPDATE SET monthly_limit = excluded.monthly_limit''',
        (user_id, category, float(monthly_limit), month)
    )
    conn.commit()
    conn.close()
    clear_cache()

@st.cache_data(ttl=30, show_spinner=False)
def get_budgets(user_id, month):
    conn = get_connection()
    df = pd.read_sql_query(
        '''SELECT * FROM budgets
           WHERE user_id = ? AND month = ?''',
        conn, params=(user_id, month)
    )
    conn.close()
    return df

def delete_budget(budget_id, user_id):
    conn = get_connection()
    conn.execute(
        'DELETE FROM budgets WHERE id = ? AND user_id = ?',
        (budget_id, user_id)
    )
    conn.commit()
    conn.close()
    clear_cache()

# ── INCOME FUNCTIONS ──────────────────────────────────────────────────────────

def add_income(date, source, amount, notes='', user_id=1):
    conn = get_connection()
    conn.execute(
        '''INSERT INTO income
           (date, source, amount, notes, user_id)
           VALUES (?, ?, ?, ?, ?)''',
        (str(date), source, float(amount), notes, user_id)
    )
    conn.commit()
    conn.close()
    clear_cache()

@st.cache_data(ttl=30, show_spinner=False)
def get_all_income(user_id=1):
    conn = get_connection()
    df = pd.read_sql_query(
        '''SELECT * FROM income
           WHERE user_id = ?
           ORDER BY date DESC''',
        conn, params=(user_id,)
    )
    conn.close()
    return df

@st.cache_data(ttl=30, show_spinner=False)
def get_income_by_month(user_id=1, month=None):
    conn = get_connection()
    if month:
        df = pd.read_sql_query(
            '''SELECT * FROM income
               WHERE user_id = ?
               AND strftime('%Y-%m', date) = ?
               ORDER BY date DESC''',
            conn, params=(user_id, month)
        )
    else:
        from datetime import datetime
        current_month = datetime.now().strftime('%Y-%m')
        df = pd.read_sql_query(
            '''SELECT * FROM income
               WHERE user_id = ?
               AND strftime('%Y-%m', date) = ?
               ORDER BY date DESC''',
            conn, params=(user_id, current_month)
        )
    conn.close()
    return df

def delete_income(income_id, user_id=1):
    conn = get_connection()
    conn.execute(
        'DELETE FROM income WHERE id = ? AND user_id = ?',
        (income_id, user_id)
    )
    conn.commit()
    conn.close()
    clear_cache()

# ── NOTIFICATION FUNCTIONS ────────────────────────────────────────────────────

def add_notification(user_id, title, message,
                     notif_type, priority='medium'):
    conn = get_connection()
    conn.execute(
        '''INSERT INTO notifications
           (user_id, title, message, type, priority)
           VALUES (?, ?, ?, ?, ?)''',
        (user_id, title, message, notif_type, priority)
    )
    conn.commit()
    conn.close()

def get_notifications_db(user_id, limit=20):
    conn = get_connection()
    df = pd.read_sql_query(
        '''SELECT * FROM notifications
           WHERE user_id = ?
           ORDER BY created_at DESC
           LIMIT ?''',
        conn, params=(user_id, limit)
    )
    conn.close()
    return df

def get_unread_count(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT COUNT(*) FROM notifications
           WHERE user_id=? AND is_read=0''',
        (user_id,)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count

def mark_all_read(user_id):
    conn = get_connection()
    conn.execute(
        'UPDATE notifications SET is_read=1 WHERE user_id=?',
        (user_id,)
    )
    conn.commit()
    conn.close()

def clear_notifications(user_id):
    conn = get_connection()
    conn.execute(
        'DELETE FROM notifications WHERE user_id=?',
        (user_id,)
    )
    conn.commit()
    conn.close()

def set_notifs_cleared(user_id):
    conn = get_connection()
    conn.execute(
        '''INSERT INTO user_settings
           (user_id, notifs_cleared_at)
           VALUES (?, datetime('now'))
           ON CONFLICT(user_id)
           DO UPDATE SET notifs_cleared_at = datetime('now')''',
        (user_id,)
    )
    conn.commit()
    conn.close()

def get_notifs_cleared_at(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT notifs_cleared_at FROM user_settings
           WHERE user_id = ?''',
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# ── SAVINGS GOAL FUNCTIONS ────────────────────────────────────────────────────

def add_savings_goal(user_id, name, target_amount,
                     target_date=None):
    conn = get_connection()
    conn.execute(
        '''INSERT INTO savings_goals
           (user_id, name, target_amount, target_date)
           VALUES (?, ?, ?, ?)''',
        (user_id, name, float(target_amount), target_date)
    )
    conn.commit()
    conn.close()
    clear_cache()

@st.cache_data(ttl=30, show_spinner=False)
def get_savings_goals(user_id):
    conn = get_connection()
    df = pd.read_sql_query(
        'SELECT * FROM savings_goals WHERE user_id=?',
        conn, params=(user_id,)
    )
    conn.close()
    return df

def update_savings_goal(goal_id, amount, user_id):
    conn = get_connection()
    conn.execute(
        '''UPDATE savings_goals
           SET current_amount = current_amount + ?
           WHERE id = ? AND user_id = ?''',
        (float(amount), goal_id, user_id)
    )
    conn.commit()
    conn.close()
    clear_cache()

def delete_savings_goal(goal_id, user_id):
    conn = get_connection()
    conn.execute(
        'DELETE FROM savings_goals WHERE id=? AND user_id=?',
        (goal_id, user_id)
    )
    conn.commit()
    conn.close()
    clear_cache()

# ── USER FUNCTIONS ────────────────────────────────────────────────────────────

def add_user(username, password_hash, email=None):
    """
    Creates a new user row.
    - email is stored as-is (may be NULL for legacy rows).
    - is_verified starts at 0; set to 1 after OTP confirmation.
    Returns (True, user_id) on success or (False, error_message).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO users
               (username, password_hash, email, is_verified)
               VALUES (?, ?, ?, 0)''',
            (username, password_hash, email)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return True, user_id
    except sqlite3.IntegrityError as e:
        conn.close()
        err = str(e).lower()
        if 'email' in err:
            return False, 'An account with that email already exists.'
        return False, 'Username already exists.'

def get_user(username):
    """
    Looks up a user by exact username match.
    Returns the full row tuple or None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM users WHERE username = ?',
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    return row

def get_user_by_email(email):
    """
    Looks up a user by email address (case-insensitive).
    Returns the full row tuple or None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM users WHERE lower(email) = lower(?)',
        (email,)
    )
    row = cursor.fetchone()
    conn.close()
    return row

def get_user_by_username_or_email(identifier):
    """
    Used during login: accepts either a username or an email address.
    Tries username first; falls back to email lookup.
    Returns the full row tuple or None.
    """
    row = get_user(identifier)
    if row is None and '@' in identifier:
        row = get_user_by_email(identifier)
    return row

def mark_user_verified(user_id):
    """
    Sets is_verified = 1 for the given user_id.
    Called immediately after successful OTP confirmation at signup.
    """
    conn = get_connection()
    conn.execute(
        'UPDATE users SET is_verified = 1 WHERE id = ?',
        (user_id,)
    )
    conn.commit()
    conn.close()

# ── LOGIN ATTEMPTS & ACTIVITY ──────────────────────────────────────────────────

def get_login_attempts(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT attempts, locked_until FROM login_attempts WHERE username = ?',
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    return row

def update_login_attempts(username, attempts, locked_until=None):
    conn = get_connection()
    conn.execute(
        '''INSERT INTO login_attempts (username, attempts, locked_until)
           VALUES (?, ?, ?)
           ON CONFLICT(username)
           DO UPDATE SET attempts = excluded.attempts, locked_until = excluded.locked_until''',
        (username, attempts, locked_until)
    )
    conn.commit()
    conn.close()

def reset_login_attempts(username):
    conn = get_connection()
    conn.execute('DELETE FROM login_attempts WHERE username = ?', (username,))
    conn.commit()
    conn.close()

def log_login_activity(user_id, device, ip):
    conn = get_connection()
    conn.execute(
        '''INSERT INTO login_activity (user_id, device, ip)
           VALUES (?, ?, ?)''',
        (user_id, device, ip)
    )
    conn.commit()
    conn.close()

def get_login_activity(user_id, limit=5):
    conn = get_connection()
    df = pd.read_sql_query(
        '''SELECT device, ip, timestamp FROM login_activity
           WHERE user_id = ?
           ORDER BY timestamp DESC LIMIT ?''',
        conn, params=(user_id, limit)
    )
    conn.close()
    return df
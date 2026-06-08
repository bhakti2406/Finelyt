import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.db import get_all_expenses, get_budgets
from utils.currency import format_amount, get_symbol
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import calendar

def D(v):
    try:
        return Decimal(str(v)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP)
    except Exception:
        return Decimal('0.00')

def get_daily_totals(df):
    """Returns dict: date_str -> total spent"""
    if df.empty:
        return {}
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    daily = df.groupby(df['date'].dt.date)['amount'].sum()
    return {str(k): float(v) for k, v in daily.items()}

def get_current_streak(daily_totals, daily_limit):
    """
    Days in a row where spending <= daily_limit.
    Counts backwards from yesterday.
    """
    streak = 0
    check_date = date.today() - timedelta(days=1)
    for _ in range(365):
        ds = str(check_date)
        spent = daily_totals.get(ds, 0)
        # A day with no expenses counts as under budget
        if spent <= daily_limit:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak

def get_best_streak(daily_totals, daily_limit):
    """Longest streak ever."""
    if not daily_totals:
        return 0
    all_dates = sorted(daily_totals.keys())
    if not all_dates:
        return 0
    start = datetime.strptime(all_dates[0], '%Y-%m-%d').date()
    end   = date.today()
    best  = 0
    curr  = 0
    d     = start
    while d <= end:
        ds    = str(d)
        spent = daily_totals.get(ds, 0)
        if spent <= daily_limit:
            curr += 1
            best = max(best, curr)
        else:
            curr = 0
        d += timedelta(days=1)
    return best

def get_under_budget_days(daily_totals, daily_limit, month_str):
    """Count days under budget in a given month."""
    count = 0
    for ds, spent in daily_totals.items():
        if ds.startswith(month_str) and spent <= daily_limit:
            count += 1
    return count

def streak_badge(streak):
    if streak >= 30:
        return "Legendary", "var(--warning)"
    elif streak >= 14:
        return "On Fire", "var(--danger)"
    elif streak >= 7:
        return "Strong", "var(--accent)"
    elif streak >= 3:
        return "Building", "var(--info)"
    elif streak >= 1:
        return "Starting", "var(--purple)"
    else:
        return "Start Today", "var(--text-muted)"

def show(user_id=1):
    currency = st.session_state.get('currency', 'INR')
    symbol   = get_symbol(currency)
    today    = date.today()
    cur_month = today.strftime('%Y-%m')

    st.markdown("""
    <style>
    .slbl     { font-size:.75rem; font-weight:700;
                color:var(--accent); text-transform:uppercase;
                letter-spacing:.1em; margin-bottom:.6rem; }
    .streak-hero {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-surface) 100%);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        padding: 2rem;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-md);
    }
    .streak-num {
        font-size: 5rem;
        font-weight: 900;
        line-height: 1;
        margin: .5rem 0;
    }
    .kpi-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1rem 1.2rem;
        text-align: center;
        margin-bottom: .5rem;
    }
    .kpi-lbl { font-size:.75rem; color:var(--text-muted);
               text-transform:uppercase; letter-spacing:.06em; }
    .kpi-val { font-size:1.5rem; font-weight:800;
               color:var(--text-primary); margin-top:4px; }
    .cal-day-good {
        background: var(--accent-dim);
        border: 1px solid var(--accent);
        border-radius: 6px;
        padding: 4px;
        text-align: center;
        font-size: .75rem;
        color: var(--accent);
        font-weight: 600;
    }
    .cal-day-bad {
        background: var(--danger-dim);
        border: 1px solid var(--danger);
        border-radius: 6px;
        padding: 4px;
        text-align: center;
        font-size: .75rem;
        color: var(--danger);
        font-weight: 600;
    }
    .cal-day-none {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 4px;
        text-align: center;
        font-size: .75rem;
        color: var(--text-secondary);
    }
    .cal-day-today {
        background: var(--info-dim);
        border: 2px solid var(--info);
        border-radius: 6px;
        padding: 4px;
        text-align: center;
        font-size: .75rem;
        color: var(--info);
        font-weight: 700;
    }
    .achievement {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: .9rem 1.2rem;
        margin-bottom: .5rem;
        display: flex;
        align-items: center;
    }
    .tip-box {
        background: var(--accent-dim);
        border-left: 3px solid var(--accent);
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
        padding: .6rem .9rem;
        color: var(--text-secondary); font-size: .85rem;
        margin-bottom: .8rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="fc-page-title">Money Streaks</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="fc-page-sub">Track your daily spending habits '
        'and build consistent financial streaks.</p>',
        unsafe_allow_html=True)
    st.divider()

    df = get_all_expenses(user_id)

    if df.empty:
        st.markdown("""
        <div class="fc-empty">
            <h3 class="fc-empty-title">No expenses yet</h3>
            <p class="fc-empty-sub">
                Add expenses to start tracking your streaks.
            </p>
        </div>""", unsafe_allow_html=True)
        return

    df['date'] = pd.to_datetime(df['date'])

    # ── DAILY LIMIT SETTING ───────────────────────────────────────────────────
    st.markdown('<p class="slbl">Daily Spending Limit</p>',
                unsafe_allow_html=True)

    # Auto-suggest based on average
    avg_daily = float(
        df.groupby(df['date'].dt.date)['amount'].sum().mean()
    )

    col_lim, col_info = st.columns([2, 3])
    with col_lim:
        daily_limit = st.number_input(
            f"Set your daily limit ({symbol})",
            min_value=1.0,
            value=float(round(avg_daily, -2))
            if avg_daily > 0 else 500.0,
            step=100.0,
            format="%.0f",
            help="Days where you spend below this count toward your streak"
        )
    with col_info:
        st.markdown(
            f"<div class='tip-box' style='margin-top:1.8rem'>"
            f"Your average daily spending is "
            f"<strong style='color:#FFF'>"
            f"{format_amount(avg_daily, currency)}</strong>. "
            f"Set your limit to something achievable — "
            f"you want to build a habit, not set yourself up to fail."
            f"</div>",
            unsafe_allow_html=True)

    st.divider()

    # ── COMPUTE STREAKS ───────────────────────────────────────────────────────
    daily_totals  = get_daily_totals(df)
    cur_streak    = get_current_streak(daily_totals, daily_limit)
    best_streak   = get_best_streak(daily_totals, daily_limit)
    under_days    = get_under_budget_days(
        daily_totals, daily_limit, cur_month)
    days_in_month = today.day  # days elapsed so far
    consistency   = (under_days / days_in_month * 100
                     if days_in_month > 0 else 0)

    # Today's spending
    today_spent = daily_totals.get(str(today), 0)
    today_remaining = max(daily_limit - today_spent, 0)
    today_over = max(today_spent - daily_limit, 0)

    # Streak badge
    badge_label, badge_color = streak_badge(cur_streak)

    # ── HERO STREAK CARD ──────────────────────────────────────────────────────
    st.markdown('<p class="slbl">Current Streak</p>',
                unsafe_allow_html=True)

    st.markdown(f"""
    <div class="streak-hero">
        <div class="streak-num" style="color:{badge_color}">
            {cur_streak}
        </div>
        <div style="color:var(--text-secondary);font-size:1rem">
            day{'s' if cur_streak != 1 else ''} in a row
            under {format_amount(daily_limit, currency)}/day
        </div>
        <div style="margin-top:.8rem">
            <span style="background:{badge_color}22;
                         border:1px solid {badge_color};
                         color:{badge_color};
                         border-radius:999px;
                         padding:4px 16px;
                         font-size:.82rem;
                         font-weight:700">
                {badge_label}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI ROW ───────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">Best Streak</div>
        <div class="kpi-val" style="color:var(--warning)">
            {best_streak} days
        </div>
    </div>""", unsafe_allow_html=True)

    k2.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">This Month</div>
        <div class="kpi-val" style="color:var(--accent)">
            {under_days}/{days_in_month} days
        </div>
    </div>""", unsafe_allow_html=True)

    k3.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">Consistency</div>
        <div class="kpi-val" style="color:var(--info)">
            {consistency:.0f}%
        </div>
    </div>""", unsafe_allow_html=True)

    if today_over > 0:
        k4.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-lbl">Over Today</div>
            <div class="kpi-val" style="color:var(--danger)">
                +{format_amount(today_over, currency)}
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        k4.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-lbl">Left Today</div>
            <div class="kpi-val" style="color:var(--accent)">
                {format_amount(today_remaining, currency)}
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── CALENDAR HEATMAP ──────────────────────────────────────────────────────
    st.markdown('<p class="slbl">This Month — Daily View</p>',
                unsafe_allow_html=True)

    year  = today.year
    month = today.month
    cal   = calendar.monthcalendar(year, month)
    month_name = today.strftime('%B %Y')

    st.markdown(
        f"<p style='color:var(--text-secondary);font-size:.85rem;"
        f"margin-bottom:.8rem'>{month_name} — "
        f"Green = under limit, Red = over limit, "
        f"Grey = no data</p>",
        unsafe_allow_html=True)

    # Day headers
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    header_cols = st.columns(7)
    for col, dn in zip(header_cols, day_names):
        col.markdown(
            f"<div style='text-align:center;color:var(--text-muted);"
            f"font-size:.75rem;font-weight:700;"
            f"padding:4px 0'>{dn}</div>",
            unsafe_allow_html=True)

    for week in cal:
        week_cols = st.columns(7)
        for col, day_num in zip(week_cols, week):
            if day_num == 0:
                col.markdown(
                    "<div style='padding:4px'></div>",
                    unsafe_allow_html=True)
                continue
            day_date = date(year, month, day_num)
            ds       = str(day_date)
            spent    = daily_totals.get(ds, None)

            if day_date == today:
                label = (
                    f"<b>{day_num}</b><br>"
                    f"<span style='font-size:.65rem'>"
                    f"{format_amount(today_spent,currency)}"
                    f"</span>"
                )
                col.markdown(
                    f"<div class='cal-day-today'>"
                    f"{label}</div>",
                    unsafe_allow_html=True)
            elif day_date > today:
                col.markdown(
                    f"<div class='cal-day-none'>"
                    f"{day_num}</div>",
                    unsafe_allow_html=True)
            elif spent is None:
                col.markdown(
                    f"<div class='cal-day-none'>"
                    f"{day_num}<br>"
                    f"<span style='font-size:.65rem'>—</span>"
                    f"</div>",
                    unsafe_allow_html=True)
            elif spent <= daily_limit:
                col.markdown(
                    f"<div class='cal-day-good'>"
                    f"{day_num}<br>"
                    f"<span style='font-size:.65rem'>"
                    f"{format_amount(spent,currency)}</span>"
                    f"</div>",
                    unsafe_allow_html=True)
            else:
                col.markdown(
                    f"<div class='cal-day-bad'>"
                    f"{day_num}<br>"
                    f"<span style='font-size:.65rem'>"
                    f"{format_amount(spent,currency)}</span>"
                    f"</div>",
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── SPENDING TREND CHART ──────────────────────────────────────────────────
    st.markdown('<p class="slbl">Last 30 Days</p>',
                unsafe_allow_html=True)

    dates_30  = [today - timedelta(days=i) for i in range(29, -1, -1)]
    spent_30  = [daily_totals.get(str(d), 0) for d in dates_30]
    labels_30 = [d.strftime('%d %b') for d in dates_30]
    colors_30 = [
        '#10B981' if s <= daily_limit else '#EF4444'
        for s in spent_30
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels_30,
        y=spent_30,
        marker_color=colors_30,
        name='Daily Spending'
    ))
    fig.add_hline(
        y=daily_limit,
        line_dash='dash',
        line_color='#F59E0B',
        annotation_text=f"Limit: {format_amount(daily_limit, currency)}",
        annotation_font_color='#F59E0B',
        annotation_position='top right'
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#FFFFFF',
        xaxis=dict(
            gridcolor='#1E293B', color='#94A3B8',
            type='category', tickangle=-45),
        yaxis=dict(
            gridcolor='#1E293B', color='#94A3B8',
            rangemode='tozero',
            title=f'Amount ({currency})'),
        margin=dict(t=30, b=60, l=20, r=20),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── ACHIEVEMENTS ──────────────────────────────────────────────────────────
    st.markdown('<p class="slbl">Achievements</p>',
                unsafe_allow_html=True)

    achievements = [
        {
            "title": "First Step",
            "desc":  "1 day under budget",
            "req":   best_streak >= 1,
            "color": "var(--purple)"
        },
        {
            "title": "Hat Trick",
            "desc":  "3 days in a row",
            "req":   best_streak >= 3,
            "color": "var(--info)"
        },
        {
            "title": "Week Warrior",
            "desc":  "7 days in a row",
            "req":   best_streak >= 7,
            "color": "var(--accent)"
        },
        {
            "title": "On Fire",
            "desc":  "14 days in a row",
            "req":   best_streak >= 14,
            "color": "var(--danger)"
        },
        {
            "title": "Monthly Master",
            "desc":  "30 days in a row",
            "req":   best_streak >= 30,
            "color": "var(--warning)"
        },
        {
            "title": "Consistency King",
            "desc":  "80%+ days under budget this month",
            "req":   consistency >= 80,
            "color": "var(--accent)"
        },
        {
            "title": "Perfect Month",
            "desc":  "Every day under budget this month",
            "req":   under_days == days_in_month
                     and days_in_month > 0,
            "color": "var(--warning)"
        },
    ]

    ach_cols = st.columns(2)
    for i, ach in enumerate(achievements):
        col = ach_cols[i % 2]
        if ach['req']:
            col.markdown(f"""
            <div style="background:var(--bg-card);
                        border:1px solid {ach['color']}44;
                        border-left:4px solid {ach['color']};
                        border-radius:12px;
                        padding:.9rem 1.2rem;
                        margin-bottom:.5rem;
                        display:flex;align-items:center;gap:12px">
                <div>
                    <div style="color:{ach['color']};
                                font-weight:700;
                                font-size:.95rem">
                        {ach['title']}
                    </div>
                    <div style="color:var(--text-secondary);font-size:.78rem">
                        {ach['desc']}
                    </div>
                </div>
                <span style="margin-left:auto;
                             background:{ach['color']}22;
                             border:1px solid {ach['color']};
                             color:{ach['color']};
                             border-radius:999px;
                             padding:2px 10px;
                             font-size:.7rem;
                             font-weight:700">
                    UNLOCKED
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            col.markdown(f"""
            <div style="background:var(--bg-card);
                        border:1px solid var(--border);
                        border-radius:12px;
                        padding:.9rem 1.2rem;
                        margin-bottom:.5rem;
                        display:flex;align-items:center;
                        gap:12px;opacity:.5">
                <div>
                    <div style="color:var(--text-muted);font-weight:700;
                                font-size:.95rem">
                        {ach['title']}
                    </div>
                    <div style="color:var(--text-muted);font-size:.78rem">
                        {ach['desc']}
                    </div>
                </div>
                <span style="margin-left:auto;color:var(--text-muted);
                             font-size:.7rem">LOCKED</span>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ── MOTIVATIONAL MESSAGE ──────────────────────────────────────────────────
    st.markdown('<p class="slbl">Today\'s Message</p>',
                unsafe_allow_html=True)

    if cur_streak == 0:
        msg = ("Every expert was once a beginner. "
               "Start your streak today — spend under "
               f"{format_amount(daily_limit, currency)} "
               "and it begins!")
        msg_color = "var(--info)"
    elif cur_streak < 3:
        msg = (f"{cur_streak} day streak! Keep going — "
               "3 days builds a habit. You're almost there!")
        msg_color = "var(--purple)"
    elif cur_streak < 7:
        msg = (f"{cur_streak} days strong! One more week "
               "and you unlock Week Warrior. Don't break it!")
        msg_color = "var(--accent)"
    elif cur_streak < 14:
        msg = (f"{cur_streak} days — impressive! "
               "You're building real financial discipline. "
               "Keep the momentum!")
        msg_color = "var(--danger)"
    elif cur_streak < 30:
        msg = (f"{cur_streak} days — you're unstoppable! "
               "Monthly Master is within reach. "
               "Don't stop now!")
        msg_color = "var(--warning)"
    else:
        msg = (f"{cur_streak} days — LEGENDARY! "
               "You've mastered your finances. "
               "You are an inspiration!")
        msg_color = "var(--warning)"

    st.markdown(f"""
    <div style="background:linear-gradient(135deg, var(--bg-card) 0%, var(--bg-surface) 100%);
                border:1px solid {msg_color}44;
                border-left:4px solid {msg_color};
                border-radius:12px;
                padding:1.2rem 1.5rem;
                margin-bottom:1rem">
        <p style="color:#FFF;font-size:1rem;
                  margin:0;line-height:1.6">
            {msg}
        </p>
    </div>
    """, unsafe_allow_html=True)
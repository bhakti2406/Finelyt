import streamlit as st
from google import genai
from utils.db import get_all_expenses, get_budgets, get_expenses_by_month, get_all_income
from utils.health_score import calculate_health_score
import pandas as pd
from datetime import datetime
import os
import re
import html
import logging
from dotenv import load_dotenv

load_dotenv()


def _sanitize_llm_input(text: str, max_length: int = 500) -> str:
    """Sanitize user input before sending to LLM: strip control chars and truncate."""
    # Remove control characters except newlines/tabs
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()[:max_length]


def _sanitize_llm_output(text: str) -> str:
    """Escape HTML entities in LLM output to prevent XSS when rendered."""
    return html.escape(text)

def build_context(df, user_id):
    if df.empty:
        return "The user has no expense data yet.", {}

    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    current_month = datetime.now().strftime('%Y-%m')
    df['month'] = df['date'].dt.strftime('%Y-%m')
    df_this_month = df[df['month'] == current_month]

    total_all = df['amount'].sum()
    total_month = df_this_month['amount'].sum() if not df_this_month.empty else 0
    avg_daily = df.groupby(df['date'].dt.date)['amount'].sum().mean()
    total_transactions = len(df)
    top_cat = df.groupby('category')['amount'].sum().idxmax()
    top_cat_amount = df.groupby('category')['amount'].sum().max()

    if not df_this_month.empty:
        cat_breakdown = df_this_month.groupby('category')['amount'].sum()
    else:
        cat_breakdown = df.groupby('category')['amount'].sum()

    cat_text = "\n".join([
        f"  - {cat}: ₹{amt:,.0f}"
        for cat, amt in cat_breakdown.items()
    ])

    budgets_df = get_budgets(user_id, current_month)
    budget_text = "No budgets set."
    if not budgets_df.empty:
        lines = []
        expenses_month = get_expenses_by_month(user_id, current_month)
        for _, b in budgets_df.iterrows():
            cat = b['category']
            limit = b['monthly_limit']
            spent = 0
            if not expenses_month.empty:
                cat_exp = expenses_month[expenses_month['category'] == cat]
                spent = cat_exp['amount'].sum()
            pct = (spent / limit * 100) if limit > 0 else 0
            status = "OVER" if pct >= 100 else \
                     "NEAR LIMIT" if pct >= 80 else "OK"
            lines.append(
                f"  - {cat}: ₹{spent:,.0f} / ₹{limit:,.0f} "
                f"({pct:.0f}%) [{status}]"
            )
        budget_text = "\n".join(lines)

    anomaly_count = 0
    try:
        from utils.features import prepare_features
        from utils.predict import predict_anomalies, load_model
        model = load_model()
        if model is not None and len(df) >= 10:
            df_full, X = prepare_features(df)
            result = predict_anomalies(df_full, X)
            anomaly_count = int((result['anomaly'] == -1).sum())
    except Exception:
        pass

    try:
        score, label, _, _, _, _ = calculate_health_score(user_id)
        health_text = f"{score}/100 ({label})"
    except Exception:
        health_text = "Not calculated"

    # ── AI COACH 2.0 ADVANCED BEHAVIORAL CHECKS ──
    insights = {}
    
    # 1. Impulse Spending Check
    dining_shopping = df_this_month[df_this_month['category'].isin(['Dining', 'Shopping'])] if not df_this_month.empty else pd.DataFrame()
    if not dining_shopping.empty:
        freq = dining_shopping.groupby(dining_shopping['date'].dt.date).size()
        frequent_days = int((freq >= 2).sum())
        if frequent_days >= 2:
            insights['impulse'] = f"Frequent spending spikes detected: you made multiple dining/shopping purchases on {frequent_days} separate days this month."
            
    # 2. Lifestyle Inflation Check
    income_df = get_all_income(user_id)
    if not income_df.empty:
        income_df = income_df.copy()
        income_df['date'] = pd.to_datetime(income_df['date'])
        income_df['month'] = income_df['date'].dt.strftime('%Y-%m')
        
        monthly_exp = df.groupby('month')['amount'].sum()
        monthly_inc = income_df.groupby('month')['amount'].sum()
        
        if len(monthly_exp) >= 2 and len(monthly_inc) >= 2:
            exp_growth = (monthly_exp.iloc[-1] - monthly_exp.iloc[0]) / monthly_exp.iloc[0] if monthly_exp.iloc[0] > 0 else 0
            inc_growth = (monthly_inc.iloc[-1] - monthly_inc.iloc[0]) / monthly_inc.iloc[0] if monthly_inc.iloc[0] > 0 else 0
            if exp_growth > inc_growth and exp_growth > 0.10:
                insights['inflation'] = f"Alert: Your monthly expenses are growing faster than your income ({exp_growth*100:.1f}% vs {inc_growth*100:.1f}%). Watch out for lifestyle inflation."

    # 3. Subscription Leakage Check
    subs_df = df_this_month[df_this_month['category'] == 'Subscriptions'] if not df_this_month.empty else pd.DataFrame()
    if not subs_df.empty:
        counts = subs_df.groupby('amount').size()
        duplicates = counts[counts >= 2].index.tolist()
        if duplicates:
            insights['leakage'] = f"Possible duplicate subscription: detected multiple active charges for the identical amount of ₹{duplicates[0]:,.0f} under subscriptions."

    # 4. Behavioral Spike (Spent within 5 days of salary credit)
    if not income_df.empty and not df_this_month.empty:
        salary_days = income_df[income_df['month'] == current_month]['date'].dt.day.tolist()
        if salary_days:
            sal_day = salary_days[0]
            spike_exp = df_this_month[(df_this_month['date'].dt.day >= sal_day) & (df_this_month['date'].dt.day <= sal_day + 5)]
            spike_total = spike_exp['amount'].sum()
            month_total = df_this_month['amount'].sum()
            pct = (spike_total / month_total * 100) if month_total > 0 else 0
            if pct >= 35:
                insights['spike'] = f"Post-salary spike: {pct:.1f}% of your monthly expenses occurred within 5 days of receiving your income credits."

    behavioral_text = "\n".join([f"  - {k.upper()}: {v}" for k, v in insights.items()])

    context = f"""
USER FINANCIAL DATA SUMMARY:

Overall:
  - Total spent (all time): ₹{total_all:,.0f}
  - Total spent (this month): ₹{total_month:,.0f}
  - Average daily spend: ₹{avg_daily:,.0f}
  - Total transactions: {total_transactions}
  - Top spending category: {top_cat} (₹{top_cat_amount:,.0f})
  - Financial Health Score: {health_text}
  - Anomalies detected: {anomaly_count}

Spending by Category (this month):
{cat_text}

Budget Status (this month):
{budget_text}

Detected Behavioral Insights:
{behavioral_text}
"""
    return context, insights


def show(user_id=1):

    st.markdown("""
    <style>
    .page-title {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0;
    }
    .page-sub {
        font-size: 1rem;
        color: var(--text-secondary);
        margin-bottom: 1.5rem;
    }
    .insight-card {
        background: rgba(255, 179, 71, 0.05);
        border: 1px solid rgba(255, 179, 71, 0.25);
        border-left: 4px solid #FFB347;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 0.88rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="page-title">AI Financial Coach 2.0</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">Upgrade your financial behavior, identify spending leakages, and chat with your intelligent personal coach.</p>',
        unsafe_allow_html=True
    )
    st.divider()

    # ── API KEY CHECK ─────────────────────────────────────────────────────────
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.markdown("""
        <div style="background:var(--warning-dim); border:1px solid var(--warning);
                    border-radius:12px; padding:1.5rem; text-align:center;">
            <h3 style="color:var(--warning);">Gemini API Key Required</h3>
            <p style="color:var(--text-secondary); margin-bottom: 1rem;">
                Add your Gemini API key to the .env file:
            </p>
            <code style="background:var(--bg-base); padding:0.5rem 1rem;
                          border-radius:8px; color:var(--accent);">
                GEMINI_API_KEY=your-key-here
            </code>
            <p style="color:var(--text-secondary); margin-top:1rem; font-size:0.85rem;">
                Get a free key at aistudio.google.com
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── LOAD DATA ─────────────────────────────────────────────────────────────
    df = get_all_expenses(user_id)
    context, insights = build_context(df, user_id)

    # ── DISPLAY BEHAVIORAL COACHING CARDS ──
    if insights:
        st.markdown("<p style='font-weight:700; color:var(--text-primary); margin-bottom:0.5rem;'>Coach's Behavioral Alerts</p>", unsafe_allow_html=True)
        for _, val in insights.items():
            st.markdown(f"""
            <div class="insight-card">
                <span style="color:#FFB347; font-weight:700; margin-right:6px;">💡 Alert:</span>
                <span style="color:var(--text-primary);">{val}</span>
            </div>
            """, unsafe_allow_html=True)
        st.divider()

    # ── CONFIGURE GEMINI (new package) ────────────────────────────────────────
    client = genai.Client(api_key=api_key)
    MODEL = 'gemini-2.5-flash'

    # ── CONTEXT CARD ──────────────────────────────────────────────────────────
    with st.expander("Data being shared with AI", expanded=False):
        st.code(context, language=None)

    # ── QUICK PROMPTS ─────────────────────────────────────────────────────────
    st.markdown("**Quick Questions:**")
    quick_prompts = [
        "Am I at risk of lifestyle inflation?",
        "Do I show any impulse spending patterns?",
        "Explain my post-salary spending spikes",
        "Am I overspending anywhere?",
        "Check for subscription leakages",
        "How can I improve my investment readiness?",
    ]

    cols = st.columns(3)
    for i, prompt in enumerate(quick_prompts):
        with cols[i % 3]:
            if st.button(prompt, use_container_width=True, key=f"quick_{i}"):
                st.session_state.quick_input = prompt

    st.divider()

    # ── CHAT HISTORY ──────────────────────────────────────────────────────────
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "Hi! I'm your Finelyt AI Coach 2.0 powered by Google Gemini. "
                "I have audited your transaction patterns for impulse shopping, subscription leakages, and post-salary spikes. "
                "Ask me any coaching question or savings strategy suggestion!"
            )
        })

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # ── HANDLE QUICK PROMPT ───────────────────────────────────────────────────
    if 'quick_input' in st.session_state and st.session_state.quick_input:
        user_input = st.session_state.quick_input
        st.session_state.quick_input = None

        # Rate limit: 10 requests per minute per session
        from utils.auth import check_rate_limit
        allowed, rate_msg = check_rate_limit("ai_chat", 10, 60)
        if not allowed:
            st.error(rate_msg)
        else:
            safe_input = _sanitize_llm_input(user_input)

            st.session_state.messages.append({
                "role": "user", "content": safe_input
            })

            with st.chat_message("user"):
                st.write(safe_input)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        prompt = f"""You are a professional behavioral personal finance coach.
You have access to the user's real spending statistics and pre-computed behavioral alerts below.
Explain these specific insights using their actual numbers.
Keep responses concise (2-4 sentences) and highly actionable.
Do not output any HTML tags or markdown links.

{context}

User question: {safe_input}"""

                        response = client.models.generate_content(
                            model=MODEL,
                            contents=prompt,
                            config={"max_output_tokens": 1024}
                        )
                        reply = _sanitize_llm_output(response.text)
                        st.write(reply)
                        st.session_state.messages.append({
                            "role": "assistant", "content": reply
                        })
                    except Exception as e:
                        logging.error("AI Coach error: %s", e)
                        st.error("AI Coach is temporarily unavailable. Please try again.")
            st.rerun()

    # ── CHAT INPUT ────────────────────────────────────────────────────────────
    user_input = st.chat_input("Ask me about your finances...")

    if user_input:
        # Rate limit: 10 requests per minute per session
        from utils.auth import check_rate_limit
        allowed, rate_msg = check_rate_limit("ai_chat", 10, 60)
        if not allowed:
            st.error(rate_msg)
        else:
            safe_input = _sanitize_llm_input(user_input)

            st.session_state.messages.append({
                "role": "user", "content": safe_input
            })

            with st.chat_message("user"):
                st.write(safe_input)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        prompt = f"""You are a professional behavioral personal finance coach.
You have access to the user's real spending statistics and pre-computed behavioral alerts below.
Explain these specific insights using their actual numbers.
Keep responses concise (2-4 sentences) and highly actionable.
Do not output any HTML tags or markdown links.

{context}

User question: {safe_input}"""

                        response = client.models.generate_content(
                            model=MODEL,
                            contents=prompt,
                            config={"max_output_tokens": 1024}
                        )
                        reply = _sanitize_llm_output(response.text)
                        st.write(reply)
                        st.session_state.messages.append({
                            "role": "assistant", "content": reply
                        })
                    except Exception as e:
                        logging.error("AI Coach error: %s", e)
                        st.error("AI Coach is temporarily unavailable. Please try again.")

    # ── CLEAR CHAT ────────────────────────────────────────────────────────────
    st.divider()
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
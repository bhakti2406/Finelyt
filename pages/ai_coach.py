import streamlit as st
from google import genai
from utils.db import get_all_expenses, get_budgets, get_expenses_by_month
from utils.health_score import calculate_health_score
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def build_context(df, user_id):
    if df.empty:
        return "The user has no expense data yet."

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
        score, label, _ = calculate_health_score(df, user_id)
        health_text = f"{score}/100 ({label})"
    except Exception:
        health_text = "Not calculated"

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
"""
    return context


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
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="page-title">AI Financial Coach</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">Powered by Google Gemini — '
        'knows your real spending data.</p>',
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
    context = build_context(df, user_id)

    # ── CONFIGURE GEMINI (new package) ────────────────────────────────────────
    client = genai.Client(api_key=api_key)
    MODEL = 'gemini-2.5-flash'

    # ── CONTEXT CARD ──────────────────────────────────────────────────────────
    with st.expander("Data being shared with AI", expanded=False):
        st.code(context, language=None)

    # ── QUICK PROMPTS ─────────────────────────────────────────────────────────
    st.markdown("**Quick Questions:**")
    quick_prompts = [
        "How is my spending this month?",
        "What's my biggest expense category?",
        "Give me 3 ways to save money",
        "Am I overspending anywhere?",
        "How can I improve my health score?",
        "Is my spending trend healthy?",
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
                "Hi! I'm your Finelyt AI Coach powered by Google Gemini. "
                "I have access to your real spending data and can help you with "
                "budgeting advice, spending analysis, and savings tips. "
                "What would you like to know?"
            )
        })

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # ── HANDLE QUICK PROMPT ───────────────────────────────────────────────────
    if 'quick_input' in st.session_state and st.session_state.quick_input:
        user_input = st.session_state.quick_input
        st.session_state.quick_input = None

        st.session_state.messages.append({
            "role": "user", "content": user_input
        })

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    prompt = f"""You are a professional personal finance coach.
You have access to the user's real spending data below.
Give specific, personalised advice using actual numbers from their data.
Keep responses concise (2-4 sentences).

{context}

User question: {user_input}"""

                    response = client.models.generate_content(
                        model=MODEL,
                        contents=prompt
                    )
                    reply = response.text
                    st.write(reply)
                    st.session_state.messages.append({
                        "role": "assistant", "content": reply
                    })
                except Exception as e:
                    err = f"AI unavailable: {str(e)}"
                    st.error(err)
        st.rerun()

    # ── CHAT INPUT ────────────────────────────────────────────────────────────
    user_input = st.chat_input("Ask me about your finances...")

    if user_input:
        st.session_state.messages.append({
            "role": "user", "content": user_input
        })

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    prompt = f"""You are a professional personal finance coach.
You have access to the user's real spending data below.
Give specific, personalised advice using actual numbers from their data.
Keep responses concise (2-4 sentences).
Do not make up numbers — only use what is in the data below.

{context}

User question: {user_input}"""

                    response = client.models.generate_content(
                        model=MODEL,
                        contents=prompt
                    )
                    reply = response.text
                    st.write(reply)
                    st.session_state.messages.append({
                        "role": "assistant", "content": reply
                    })
                except Exception as e:
                    err = f"AI unavailable right now: {str(e)}"
                    st.error(err)

    # ── CLEAR CHAT ────────────────────────────────────────────────────────────
    st.divider()
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
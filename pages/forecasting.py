import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import importlib
import utils.forecasting
importlib.reload(utils.forecasting)
from utils.forecasting import forecast_cash_flow, analyze_goal_feasibility, model_retirement_planning
from utils.currency import format_amount, get_symbol
from utils.db import get_savings_goals
from datetime import datetime, timedelta

def show(user_id=1):
    currency = st.session_state.get('currency', 'INR')
    sym = get_symbol(currency)
    
    st.markdown("""
    <style>
    .page-title { font-size: 2rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0; }
    .page-sub { font-size: 1rem; color: var(--text-secondary); margin-bottom: 1.5rem; }
    .metric-value { font-size: 1.6rem; font-weight: 800; color: var(--text-primary); margin-top: 4px; }
    .forecast-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .badge-high { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #10B981; border-radius: 6px; padding: 2px 8px; font-size: 0.8rem; font-weight: 600; }
    .badge-med { background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); color: #F59E0B; border-radius: 6px; padding: 2px 8px; font-size: 0.8rem; font-weight: 600; }
    .badge-low { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: #EF4444; border-radius: 6px; padding: 2px 8px; font-size: 0.8rem; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="page-title">Predictive Financial Planning</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Use advanced machine learning and statistical models to forecast your future financial cash flow, goal timelines, and retirement readiness.</p>', unsafe_allow_html=True)
    st.divider()
    
    tab_cashflow, tab_goals, tab_retirement = st.tabs([
        "Cash Flow Forecasting", "Goal Feasibility Analysis", "Retirement Planning"
    ])
    
    # 1. CASH FLOW FORECASTING
    with tab_cashflow:
        st.markdown("<p style='font-weight:700; font-size:1.1rem; color:var(--text-primary); margin-bottom:1rem;'>Future Cash Flow Projections</p>", unsafe_allow_html=True)
        
        history, forecast = forecast_cash_flow(user_id)
        
        # Display next 1, 3, 6 month highlights
        h1, h2, h3 = st.columns(3)
        
        m1 = forecast.iloc[0]
        m3 = forecast.iloc[2]
        m6 = forecast.iloc[5]
        
        h1.markdown(f"""
        <div class="forecast-card" style="text-align:center;">
            <span style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em;">Next Month (1M)</span>
            <div class="metric-value" style="color:var(--accent);">{format_amount(m1['predicted_savings'], currency)}</div>
            <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:4px;">Savings expected</div>
        </div>
        """, unsafe_allow_html=True)
        
        h2.markdown(f"""
        <div class="forecast-card" style="text-align:center;">
            <span style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em;">3 Months Cumulative</span>
            <div class="metric-value" style="color:#3B82F6;">{format_amount(forecast.iloc[:3]['predicted_savings'].sum(), currency)}</div>
            <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:4px;">Savings expected</div>
        </div>
        """, unsafe_allow_html=True)
        
        h3.markdown(f"""
        <div class="forecast-card" style="text-align:center;">
            <span style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em;">6 Months Cumulative</span>
            <div class="metric-value" style="color:#8B5CF6;">{format_amount(forecast['predicted_savings'].sum(), currency)}</div>
            <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:4px;">Savings expected</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Plotly chart: combine history + forecast
        hist_records = []
        for _, r in history.iterrows():
            hist_records.append({'Month': r['month_str'], 'Type': 'Historical', 'Income': r['amount_inc'], 'Expenses': r['amount_exp']})
        for _, r in forecast.iterrows():
            hist_records.append({'Month': r['month_str'], 'Type': 'Forecasted', 'Income': r['predicted_income'], 'Expenses': r['predicted_expenses']})
            
        combined_df = pd.DataFrame(hist_records)
        
        fig = go.Figure()
        # History
        hist_df = combined_df[combined_df['Type'] == 'Historical']
        fig.add_trace(go.Scatter(x=hist_df['Month'], y=hist_df['Income'], name='Income (Historical)', line=dict(color='#10B981', width=3)))
        fig.add_trace(go.Scatter(x=hist_df['Month'], y=hist_df['Expenses'], name='Expenses (Historical)', line=dict(color='#EF4444', width=3)))
        
        # Forecast
        fore_df = combined_df[combined_df['Type'] == 'Forecasted']
        # Conjoin the last element of history to make the line continuous
        if not hist_df.empty:
            fore_df = pd.concat([hist_df.tail(1), fore_df])
        fig.add_trace(go.Scatter(x=fore_df['Month'], y=fore_df['Income'], name='Income (Forecast)', line=dict(color='#10B981', width=3, dash='dash')))
        fig.add_trace(go.Scatter(x=fore_df['Month'], y=fore_df['Expenses'], name='Expenses (Forecast)', line=dict(color='#EF4444', width=3, dash='dash')))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#F8FAFC',
            title_font_color='#F8FAFC',
            title="Income vs Expenses Trend & Forecast",
            xaxis=dict(gridcolor='#1E293B', color='#94A3B8'),
            yaxis=dict(gridcolor='#1E293B', color='#94A3B8'),
            margin=dict(t=50, b=40, l=20, r=20),
            legend=dict(font=dict(color='#94A3B8'), bgcolor='rgba(0,0,0,0)')
        )
        st.plotly_chart(fig, use_container_width=True)
        
    # 2. GOAL FEASIBILITY ANALYSIS
    with tab_goals:
        st.markdown("<p style='font-weight:700; font-size:1.1rem; color:var(--text-primary); margin-bottom:1rem;'>Savings Goals Feasibility Analysis</p>", unsafe_allow_html=True)
        
        goals = get_savings_goals(user_id)
        if goals.empty:
            st.info("You don't have any savings goals set yet. Go to the Savings dashboard to add goals.")
            
            # Offer a simulation mock goal
            st.markdown("##### Simulate a Goal:")
            sim_name = st.selectbox("Mock Goal", ["Laptop Purchase", "Car Downpayment", "Vacation", "House Downpayment"])
            sim_target = st.slider("Target Amount", 10000, 500000, 100000, 10000)
            sim_current = st.slider("Current Savings", 0, sim_target, 20000, 5000)
            sim_months = st.slider("Target Timeline (Months)", 1, 36, 12)
            
            remaining = sim_target - sim_current
            monthly_contrib = remaining / sim_months
            
            # mock velocity
            sim_velocity = st.slider("Your Average Monthly Savings Velocity", 1000, 50000, 8000, 1000)
            
            # calculate
            ratio = sim_velocity / monthly_contrib if monthly_contrib > 0 else 1.0
            prob = max(0.0, min(100.0, ratio * 100.0))
            
            months_needed = remaining / sim_velocity if sim_velocity > 0 else 99
            est_comp_date = (datetime.now() + timedelta(days=int(months_needed * 30.4))).strftime('%d %b %Y')
            
            badge_class = "badge-high" if prob >= 80 else "badge-med" if prob >= 50 else "badge-low"
            badge_label = "High Probability" if prob >= 80 else "Moderate Probability" if prob >= 50 else "Low Probability"
            
            st.markdown(f"""
            <div class="forecast-card">
                <h4>{sim_name} Simulation Result:</h4>
                <p><strong>Goal Target:</strong> {format_amount(sim_target, currency)} | <strong>Current:</strong> {format_amount(sim_current, currency)}</p>
                <p><strong>Required Monthly Contribution:</strong> {format_amount(monthly_contrib, currency)}</p>
                <p><strong>Your Savings Velocity:</strong> {format_amount(sim_velocity, currency)}</p>
                <hr style="border-color:var(--border);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong>Achievability Probability:</strong> <span class="{badge_class}">{prob:.1f}% ({badge_label})</span>
                    </div>
                    <div>
                        <strong>Estimated Completion:</strong> <span style="color:#00D4AA; font-weight:700;">{est_comp_date}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            selected_goal = st.selectbox("Select Goal to Analyze", goals['name'].tolist())
            goal_id = goals[goals['name'] == selected_goal].iloc[0]['id']
            
            # Run analysis
            analysis = analyze_goal_feasibility(goal_id, user_id)
            
            if analysis:
                prob = analysis['probability']
                badge_class = "badge-high" if prob >= 80 else "badge-med" if prob >= 50 else "badge-low"
                badge_label = "High Probability" if prob >= 80 else "Moderate Probability" if prob >= 50 else "Low Probability"
                
                st.markdown(f"""
                <div class="forecast-card">
                    <h4>Goal: {selected_goal}</h4>
                    <p><strong>Remaining Balance Needed:</strong> {format_amount(analysis['remaining_amount'], currency)}</p>
                    <p><strong>Average Monthly Savings Velocity:</strong> {format_amount(analysis['current_velocity'], currency)}</p>
                    <p><strong>Required Monthly Savings to hit target date:</strong> {format_amount(analysis['required_monthly_savings'], currency)}</p>
                    <hr style="border-color:var(--border);">
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1.5rem;">
                        <div>
                            <strong>Probability of hitting target date:</strong><br>
                            <span class="{badge_class}" style="font-size:1rem; display:inline-block; margin-top:8px;">{prob}% ({badge_label})</span>
                        </div>
                        <div>
                            <strong>Estimated Completion Date:</strong><br>
                            <span style="color:#00D4AA; font-weight:700; font-size:1.1rem; display:inline-block; margin-top:8px;">{analysis['completion_date']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Interactive slider to simulate adjustments
                st.markdown("##### Simulate Contribution Adjustments:")
                sim_boost = st.slider("Boost Monthly Savings By", 0, 50000, 5000, 1000)
                new_velocity = analysis['current_velocity'] + sim_boost
                
                new_ratio = new_velocity / analysis['required_monthly_savings'] if analysis['required_monthly_savings'] > 0 else 1.0
                new_prob = max(0.0, min(100.0, new_ratio * 100.0))
                new_months = analysis['remaining_amount'] / new_velocity if new_velocity > 0 else 999.0
                new_date = (datetime.now() + timedelta(days=int(new_months * 30.4))).strftime('%d %b %Y')
                
                new_badge_class = "badge-high" if new_prob >= 80 else "badge-med" if new_prob >= 50 else "badge-low"
                
                st.markdown(f"""
                <div class="forecast-card" style="border-color:#10B981; background:rgba(16,185,129,0.02);">
                    <h5 style="color:#10B981; margin:0 0 0.5rem 0;">Simulated Results:</h5>
                    <p>New Savings Velocity: <strong>{format_amount(new_velocity, currency)} / month</strong></p>
                    <p>New Probability: <span class="{new_badge_class}">{new_prob:.1f}%</span></p>
                    <p>New Expected Completion Date: <span style="color:#10B981; font-weight:700;">{new_date}</span> (takes {new_months:.1f} months)</p>
                </div>
                """, unsafe_allow_html=True)
                
    # 3. RETIREMENT PLANNING
    with tab_retirement:
        st.markdown("<p style='font-weight:700; font-size:1.1rem; color:var(--text-primary); margin-bottom:1rem;'>Inflation-Adjusted Retirement Modeler</p>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 1.2])
        
        with c1:
            st.markdown("##### Simulation Parameters")
            current_age = st.slider("Current Age", 18, 70, 30)
            retirement_age = st.slider("Desired Retirement Age", current_age + 1, 80, 60)
            current_savings = st.number_input("Current Savings / Assets", min_value=0, value=500000, step=50000)
            expected_return = st.slider("Expected Annual Return (%)", 2.0, 20.0, 10.0, 0.5)
            expected_inflation = st.slider("Expected Annual Inflation (%)", 1.0, 12.0, 6.0, 0.5)
            post_retirement_expense = st.number_input("Target Monthly Expense (in today's values)", min_value=1000, value=40000, step=5000)
            
        with c2:
            st.markdown("##### Projection Dashboard")
            res = model_retirement_planning(
                current_age, retirement_age, current_savings,
                expected_return, expected_inflation, post_retirement_expense
            )
            
            st.markdown(f"""
            <div class="forecast-card">
                <table style="width:100%; border-collapse:collapse; font-size:0.95rem;">
                    <tr style="border-bottom:1px solid var(--border); height:36px;">
                        <td style="color:var(--text-secondary);">Target Corpus Required (Inflation-adjusted)</td>
                        <td style="text-align:right; font-weight:700; color:var(--accent); font-size:1rem;">{format_amount(res['target_corpus'], currency)}</td>
                    </tr>
                    <tr style="border-bottom:1px solid var(--border); height:36px;">
                        <td style="color:var(--text-secondary);">Future Value of Current Savings</td>
                        <td style="text-align:right; font-weight:700; color:#3B82F6;">{format_amount(res['future_value_savings'], currency)}</td>
                    </tr>
                    <tr style="border-bottom:1px solid var(--border); height:36px;">
                        <td style="color:var(--text-secondary);">Shortfall</td>
                        <td style="text-align:right; font-weight:700; color:#EF4444;">{format_amount(res['shortfall'], currency)}</td>
                    </tr>
                    <tr style="height:36px;">
                        <td style="color:var(--text-secondary); font-weight:700;">Required Monthly Contribution</td>
                        <td style="text-align:right; font-weight:900; color:#10B981; font-size:1.15rem;">{format_amount(res['required_monthly_contribution'], currency)} / mo</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            # Visualize wealth growth compounding line chart
            years = list(range(retirement_age - current_age + 1))
            corpus_trend = []
            contrib = res['required_monthly_contribution']
            current = current_savings
            r = expected_return / 100.0
            
            for y in years:
                if y == 0:
                    corpus_trend.append(current)
                else:
                    # compound current savings + add yearly contributions compounded monthly
                    current = current * (1.0 + r) + (contrib * 12) * (1.0 + r/2)
                    corpus_trend.append(current)
                    
            fig_compound = px.line(
                x=[current_age + y for y in years], y=corpus_trend,
                labels={'x': 'Age', 'y': f'Estimated Wealth ({sym})'},
                title="Corpus Growth Accumulation Projection"
            )
            fig_compound.update_traces(line_color="#10B981", line_width=3)
            fig_compound.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#F8FAFC',
                xaxis=dict(gridcolor='#1E293B', color='#94A3B8'),
                yaxis=dict(gridcolor='#1E293B', color='#94A3B8'),
                margin=dict(t=40, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_compound, use_container_width=True)

import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="Retirement Flow Simulator", page_icon="🏦", layout="wide")

# 2. Modern Styling
st.markdown("""
    <style>
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; }
    [data-testid="stSidebar"] { background-color: #f1f3f6; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Inputs
with st.sidebar:
    st.header("⚙️ Simulation Parameters")
    
    st.subheader("Current Status")
    opening_balance = st.number_input("Open Balance ($)", value=100000, step=10000)
    current_age = st.slider("Current Age", 18, 70, 35)
    retirement_age = st.slider("Retirement Age", 50, 80, 65)
    life_expectancy = st.slider("Life Expectancy", 70, 100, 95)
    
    st.divider()
    st.subheader("Financial Variables")
    inflation_rate = st.slider("Inflation Rate (%)", 0.0, 10.0, 3.0) / 100
    avg_yield = st.slider("Avg. Investment Yield (%)", 0.0, 15.0, 7.0) / 100
    
    st.divider()
    st.subheader("Monthly Cash Flow")
    monthly_income = st.number_input("Monthly Income (Pre-Retirement)", value=8000)
    monthly_savings = st.number_input("Monthly Savings (Ends at Retirement)", value=1500)
    monthly_withdrawal_post = st.number_input("Monthly Withdrawal (Post-Retirement)", value=6000)

# 4. Calculation Engine
total_horizon = life_expectancy - current_age
ages = np.arange(current_age, life_expectancy + 1)
balances = []
annual_flows = []
current_bal = opening_balance

# Real Rate of Return calculation (Fisher Equation)
real_yield = (1 + avg_yield) / (1 + inflation_rate) - 1

for year_idx, age in enumerate(ages):
    balances.append(max(0, current_bal))
    
    if age < retirement_age:
        # ACCUMULATION PHASE: Savings are active
        net_annual_flow = monthly_savings * 12
        current_bal = (current_bal * (1 + real_yield)) + net_annual_flow
    elif age < life_expectancy:
        # DISTRIBUTION PHASE: Savings are ZERO, Withdrawals are active
        net_annual_flow = -(monthly_withdrawal_post * 12)
        current_bal = (current_bal * (1 + real_yield)) + net_annual_flow
    else:
        net_annual_flow = 0
    
    annual_flows.append(net_annual_flow)

# 5. UI Dashboard
st.title("🏦 Retirement Capital Flow Simulator")
st.caption("Strategic wealth modeling based on inflation-adjusted purchasing power.")

# Metrics Row
col1, col2, col3,

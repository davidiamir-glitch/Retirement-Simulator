import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="Retirement Flow Simulator", page_icon="🏦", layout="wide")

# 2. Modern Styling
st.markdown("""
    <style>
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; }
    .main { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Inputs
with st.sidebar:
    st.header("⚙️ Simulation Parameters")
    
    st.subheader("Current Status")
    opening_balance = st.number_input("Open Balance ($)", value=100000, step=10000)
    current_age = st.slider("Current Age", 18, 70, 35)
    retirement_age = st.slider("Retirement Age", 50, 80, 65)
    life_expectancy = st.slider("Life Expectancy", 70, 100, 90)
    
    st.divider()
    st.subheader("Financial Variables")
    inflation_rate = st.slider("Inflation Rate (%)", 0.0, 10.0, 3.0) / 100
    avg_yield = st.slider("Avg. Investment Yield (%)", 0.0, 15.0, 7.0) / 100
    
    st.divider()
    st.subheader("Monthly Cash Flow")
    monthly_income = st.number_input("Monthly Income (Pre-Retirement)", value=8000)
    monthly_savings = st.number_input("Monthly Savings/Contribution", value=1500)
    monthly_withdrawal_post = st.number_input("Monthly Withdrawal (Post-Retirement)", value=5000)

# 4. Calculation Engine
years_to_retire = retirement_age - current_age
years_in_retire = life_expectancy - retirement_age
total_horizon = life_expectancy - current_age

# Setup data tracking
ages = np.arange(current_age, life_expectancy + 1)
balances = []
current_bal = opening_balance

for year in range(total_horizon + 1):
    balances.append(max(0, current_bal))
    
    # Calculate real yield (Nominal Yield - Inflation)
    real_yield = (1 + avg_yield) / (1 + inflation_rate) - 1
    
    if ages[year] < retirement_age:
        # Accumulation Phase
        annual_contribution = monthly_savings * 12
        current_bal = current_bal * (1 + real_yield) + annual_contribution
    else:
        # Distribution Phase
        annual_withdrawal = monthly_withdrawal_post * 12
        current_bal = current_bal * (1 + real_yield) - annual_withdrawal

# 5. UI Dashboard
st.title("🏦 Retirement Capital Flow Simulator")
st.write(f"Simulation for **{current_age} to {life_expectancy}** years old.")

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
peak_capital = max(balances)
final_balance = balances[-1]
status = "✅ Funded" if final_balance > 0 else "🚨 Shortfall"

col1.metric("Peak Capital", f"${peak_capital:,.0f}")
col2.metric("Final Balance", f"${final_balance:,.0f}")
col3.metric("Years to Retire", f"{years_to_retire}")
col4.metric("Plan Status", status)

# Charting
df = pd.DataFrame({"Age": ages, "Balance": balances})
st.subheader("📈 Wealth Progression (Adjusted for Inflation)")
st.area_chart(df.set_index("Age"), color="#29b5e8")



# Detailed Table
with st.expander("📂 View Year-by-Year Breakdown"):
    st.dataframe(df.style.format({"Balance": "${:,.2f}"}), use_container_width=True)

st.info("**Systems Note:** This model uses the 'Real Rate of Return' method. All values are shown in 'Today's Dollars' to maintain a consistent baseline for purchasing power.")

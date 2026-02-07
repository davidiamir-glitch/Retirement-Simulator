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
    monthly_savings = st.number_input("Monthly Savings (Ends at Retirement)", value=1500)
    monthly_withdrawal_post = st.number_input("Monthly Withdrawal (Starts at Retirement)", value=6000)

# 4. Calculation Engine
ages = np.arange(current_age, life_expectancy + 1)
balances = []
annual_flows = []
current_bal = opening_balance

# Real Rate of Return (Fisher Equation)
real_yield = (1 + avg_yield) / (1 + inflation_rate) - 1

for age in ages:
    balances.append(max(0, current_bal))
    
    # SYSTEM LOGIC: Determine if we are in the Inflow or Outflow phase
    if age < retirement_age:
        # Savings Phase
        net_annual_flow = monthly_savings * 12
    else:
        # Withdrawal Phase (Savings = 0)
        net_annual_flow = -(monthly_withdrawal_post * 12)
    
    annual_flows.append(net_annual_flow)
    
    # Growth applied to current balance, then add/subtract flow
    if age < life_expectancy:
        current_bal = (current_bal * (1 + real_yield)) + net_annual_flow

# 5. UI Dashboard
st.title("🏦 Retirement Capital Flow Simulator")
st.caption("Strategic wealth modeling based on inflation-adjusted purchasing power.")

# Metrics Row (Fixed Variable Assignment)
col1, col2, col3, col4 = st.columns(4)

peak_val = max(balances)
final_val = balances[-1]
# Find the first age where balance hits zero
shortfall_indices = [i for i, b in enumerate(balances) if b <= 0]
shortfall_age = ages[shortfall_indices[0]] if shortfall_indices else None

col1.metric("Peak Capital", f"${peak_val:,.0f}")
col2.metric("Final Balance", f"${final_val:,.0f}")
col3.metric("Real Yield", f"{real_yield*100:.2f}%")
col4.metric("Status", "✅ Sustainable" if final_val > 0 else f"🚨 Shortfall @ Age {shortfall_age}")

# Charting
df = pd.DataFrame({
    "Age": ages, 
    "Balance": balances,
    "Annual Flow": annual_flows
})

st.subheader("📈 Wealth Progression")
st.area_chart(df.set_index("Age")["Balance"], color="#2ecc71")



# 6. Detailed Analysis
st.divider()
c_logic1, c_logic2 = st.columns(2)

with c_logic1:
    st.subheader("📑 Cash Flow Logic")
    st.info(f"""
    **Accumulation Stage ({current_age} to {retirement_age - 1}):** You are saving **${monthly_savings*12:,.0f}** per year.
    
    **Distribution Stage ({retirement_age} to {life_expectancy}):** You are withdrawing **${monthly_withdrawal_post*12:,.0f}** per year and saving **$0**.
    """)

with c_logic2:
    st.subheader("📂 Annual Breakdown")
    st.dataframe(df.style.format({
        "Balance": "${:,.0f}", 
        "Annual Flow": "${:,.0f}"
    }), use_container_width=True)

st.warning("All values are adjusted for inflation to represent current purchasing power.")

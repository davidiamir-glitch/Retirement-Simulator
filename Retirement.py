from __future__ import annotations

import math
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


def annual_to_monthly(rate_annual: float) -> float:
    # Convert nominal annual rate to effective monthly
    return (1.0 + rate_annual) ** (1.0 / 12.0) - 1.0


def simulate_retirement(
    opening_balance: float,
    years_till_retirement: int,
    years_in_retirement: int,
    monthly_income: float,
    monthly_contribution: float,
    monthly_withdraw_pre: float,
    monthly_withdraw_post: float,
    inflation_annual: float,
    yield_annual: float,
    fee_annual: float,
    inflate_withdrawals_post: bool,
    one_time_contribution: float,
    one_time_contribution_month: int,
    one_time_withdrawal: float,
    one_time_withdrawal_month: int,
) -> pd.DataFrame:
    months_pre = years_till_retirement * 12
    months_post = years_in_retirement * 12
    total_months = months_pre + months_post

    r_m = annual_to_monthly(yield_annual - fee_annual)
    inf_m = annual_to_monthly(inflation_annual)

    rows = []
    bal = opening_balance

    for m in range(1, total_months + 1):
        phase = "Pre-retirement" if m <= months_pre else "Retirement"

        # Inflation index (for real vs nominal tracking)
        # Define month 1 as base (index=1.0)
        infl_index = (1.0 + inf_m) ** (m - 1)

        # Cashflows
        income = monthly_income if m <= months_pre else 0.0
        contrib = monthly_contribution if m <= months_pre else 0.0

        withdraw = monthly_withdraw_pre if m <= months_pre else monthly_withdraw_post
        if phase == "Retirement" and inflate_withdrawals_post:
            # Withdrawal grows with inflation after retirement
            # Base at first retirement month
            months_into_ret = m - months_pre
            withdraw = monthly_withdraw_post * ((1.0 + inf_m) ** (months_into_ret - 1))

        # One-time events
        ot_contrib = one_time_contribution if m == one_time_contribution_month else 0.0
        ot_withdraw = one_time_withdrawal if m == one_time_withdrawal_month else 0.0

        # Apply return then net cashflows (order choice)
        # You can swap order; this is a common convention for monthly modeling.
        bal_before = bal
        bal = bal * (1.0 + r_m)

        net_in = income + contrib + ot_contrib
        net_out = withdraw + ot_withdraw
        bal = bal + net_in - net_out

        # If balance goes below zero, cap at zero but keep tracking for "failure month"
        went_negative = bal < 0
        if went_negative:
            bal = 0.0

        rows.append(
            {
                "Month": m,
                "Year": (m - 1) // 12 + 1,
                "Phase": phase,
                "Balance_Nominal": bal,
                "Balance_Real_Today": bal / infl_index,  # in today's money
                "Return_Monthly": r_m,
                "Inflation_Monthly": inf_m,
                "Income": income,
                "Contribution": contrib,
                "Withdrawal": withdraw,
                "OneTime_Contribution": ot_contrib,
                "OneTime_Withdrawal": ot_withdraw,
                "Net_Cashflow": (net_in - net_out),
                "Balance_Before": bal_before,
                "Went_Negative": went_negative,
            }
        )

    return pd.DataFrame(rows)


def money(x: float) -> str:
    return f"${x:,.0f}"


st.set_page_config(page_title="Retirement Simulator", layout="wide")
st.title("Retirement Savings Simulator")
st.caption("Simulate balances month-by-month, with inflation and investment returns.")

with st.sidebar:
    st.header("Inputs")

    opening_balance = st.number_input("Opening balance", min_value=0.0, value=250_000.0, step=10_000.0)

    years_till = st.slider("Years till retirement", min_value=0, max_value=50, value=15, step=1)
    years_ret = st.slider("Years in retirement", min_value=1, max_value=50, value=25, step=1)

    st.divider()
    monthly_income = st.number_input("Monthly income till retirement", min_value=0.0, value=12_000.0, step=500.0)
    monthly_contrib = st.number_input("Monthly contribution (savings/investing) till retirement", min_value=0.0, value=2_500.0, step=100.0)

    monthly_withdraw_pre = st.number_input("Monthly withdrawal till retirement", min_value=0.0, value=0.0, step=100.0)
    monthly_withdraw_post = st.number_input("Monthly withdrawal after retirement", min_value=0.0, value=6_000.0, step=250.0)

    st.divider()
    inflation_pct = st.slider("Inflation rate (annual %)", min_value=0.0, max_value=15.0, value=2.5, step=0.1)
    yield_pct = st.slider("Avg. yield on investment (annual %)", min_value=0.0, max_value=20.0, value=6.0, step=0.1)

    fee_pct = st.slider("Fees / tax drag (annual %)", min_value=0.0, max_value=5.0, value=0.8, step=0.1)
    inflate_post = st.toggle("Increase retirement withdrawals with inflation", value=True)

    st.divider()
    st.subheader("Optional one-time events")
    one_time_contribution = st.number_input("One-time contribution", min_value=0.0, value=0.0, step=1_000.0)
    one_time_contribution_month = st.number_input(
        "Month of one-time contribution (1 = first month)", min_value=1, max_value=(years_till + years_ret) * 12, value=1, step=1
    )

    one_time_withdrawal = st.number_input("One-time withdrawal", min_value=0.0, value=0.0, step=1_000.0)
    one_time_withdrawal_month = st.number_input(
        "Month of one-time withdrawal (1 = first month)", min_value=1, max_value=(years_till + years_ret) * 12, value=1, step=1
    )

    run = st.button("Run simulation", type="primary", use_container_width=True)

if not run:
    st.info("Set your assumptions on the left and click **Run simulation**.")
    st.stop()

df = simulate_retirement(
    opening_balance=opening_balance,
    years_till_retirement=years_till,
    years_in_retirement=years_ret,
    monthly_income=monthly_income,
    monthly_contribution=monthly_contrib,
    monthly_withdraw_pre=monthly_withdraw_pre,
    monthly_withdraw_post=monthly_withdraw_post,
    inflation_annual=inflation_pct / 100.0,
    yield_annual=yield_pct / 100.0,
    fee_annual=fee_pct / 100.0,
    inflate_withdrawals_post=inflate_post,
    one_time_contribution=one_time_contribution,
    one_time_contribution_month=int(one_time_contribution_month),
    one_time_withdrawal=one_time_withdrawal,
    one_time_withdrawal_month=int(one_time_withdrawal_month),
)

end_nom = float(df["Balance_Nominal"].iloc[-1])
end_real = float(df["Balance_Real_Today"].iloc[-1])

# Detect failure month (first time it went negative)
failure_rows = df[df["Went_Negative"]]
failure_month = int(failure_rows["Month"].iloc[0]) if not failure_rows.empty else None

# KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("Ending balance (nominal)", money(end_nom))
k2.metric("Ending balance (today's $)", money(end_real))
k3.metric("Horizon", f"{years_till + years_ret} years ({(years_till + years_ret) * 12} months)")
k4.metric("Depletion month", "Never" if failure_month is None else f"Month {failure_month}")

st.divider()

# Charts
c1, c2 = st.columns(2)

with c1:
    st.subheader("Balance over time (nominal)")
    fig = plt.figure()
    plt.plot(df["Month"], df["Balance_Nominal"])
    plt.xlabel("Month")
    plt.ylabel("Balance")
    st.pyplot(fig, clear_figure=True)

with c2:
    st.subheader("Balance over time (inflation-adjusted)")
    fig = plt.figure()
    plt.plot(df["Month"], df["Balance_Real_Today"])
    plt.xlabel("Month")
    plt.ylabel("Balance (today's $)")
    st.pyplot(fig, clear_figure=True)

st.subheader("Cashflow components (selected)")
show_yearly = st.toggle("Show yearly table (instead of monthly)", value=True)

if show_yearly:
    yearly = df.groupby(["Year", "Phase"], as_index=False).agg(
        Income=("Income", "sum"),
        Contribution=("Contribution", "sum"),
        Withdrawal=("Withdrawal", "sum"),
        OneTime_Contribution=("OneTime_Contribution", "sum"),
        OneTime_Withdrawal=("OneTime_Withdrawal", "sum"),
        Ending_Balance_Nominal=("Balance_Nominal", "last"),
        Ending_Balance_Real=("Balance_Real_Today", "last"),
    )
    st.dataframe(yearly, use_container_width=True, hide_index=True)
else:
    st.dataframe(df[["Month","Phase","Income","Contribution","Withdrawal","Balance_Nominal","Balance_Real_Today"]], use_container_width=True, hide_index=True)

# Download
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download monthly results (CSV)", data=csv, file_name="retirement_simulation.csv", mime="text/csv")
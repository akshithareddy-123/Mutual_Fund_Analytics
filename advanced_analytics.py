import os
import pandas as pd
import numpy as np

print("STARTING ADVANCED ANALYTICS")

os.makedirs("outputs", exist_ok=True)

# Load datasets
fund_master = pd.read_csv("data/raw/01_fund_master.csv")
nav = pd.read_csv("data/raw/02_nav_history.csv")

# Convert date
nav["date"] = pd.to_datetime(nav["date"])

# Sort data
nav = nav.sort_values(["amfi_code", "date"])

# Compute daily returns
nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()

print("Daily Returns Ready")
# ======================================================
# ======================================================
# Historical VaR (95%) & CVaR
# ======================================================

print("\nComputing Historical VaR & CVaR...")

var_results = []

for code, group in nav.groupby("amfi_code"):

    returns = group["daily_return"].dropna()

    if len(returns) == 0:
        continue

    # Historical VaR (95%)
    var95 = np.percentile(returns, 5)

    # Conditional VaR
    cvar95 = returns[returns <= var95].mean()

    scheme = fund_master.loc[
        fund_master["amfi_code"] == code,
        "scheme_name"
    ]

    if len(scheme) > 0:
        scheme = scheme.values[0]
    else:
        scheme = "Unknown"

    var_results.append([
        code,
        scheme,
        round(var95, 5),
        round(cvar95, 5)
    ])

var_df = pd.DataFrame(
    var_results,
    columns=[
        "amfi_code",
        "scheme_name",
        "VaR_95",
        "CVaR_95"
    ]
)

var_df = var_df.sort_values(
    "VaR_95"
)

var_df.to_csv(
    "outputs/var_cvar_report.csv",
    index=False
)

print(var_df.head())

print("VaR & CVaR Report Saved")

# ======================================================
# Rolling 90-Day Sharpe Ratio
# ======================================================

import matplotlib.pyplot as plt

print("\nComputing Rolling 90-Day Sharpe Ratio...")

plt.figure(figsize=(14,7))

top5 = fund_master["amfi_code"].unique()[:5]

for code in top5:

    temp = nav[nav["amfi_code"] == code].copy()

    temp["rolling_sharpe"] = (
        temp["daily_return"].rolling(90).mean()
        /
        temp["daily_return"].rolling(90).std()
    ) * np.sqrt(252)

    scheme = fund_master.loc[
        fund_master["amfi_code"] == code,
        "scheme_name"
    ].values[0]

    plt.plot(
        temp["date"],
        temp["rolling_sharpe"],
        label=scheme
    )

plt.title("Rolling 90-Day Sharpe Ratio")
plt.xlabel("Date")
plt.ylabel("Sharpe Ratio")
plt.legend(fontsize=8)

plt.tight_layout()

plt.savefig(
    "outputs/rolling_sharpe_chart.png"
)

plt.close()

print("Rolling Sharpe Chart Saved")

# ======================================================
# Investor Cohort Analysis
# ======================================================

print("\nComputing Investor Cohort Analysis...")

transactions = pd.read_csv("data/raw/08_investor_transactions.csv")

transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"]
)

transactions["cohort_year"] = (
    transactions.groupby("investor_id")["transaction_date"]
    .transform("min")
    .dt.year
)

cohort = (
    transactions.groupby("cohort_year")
    .agg(
        avg_investment=("amount_inr","mean"),
        total_investment=("amount_inr","sum"),
        investors=("investor_id","nunique")
    )
    .reset_index()
)

print(cohort)

cohort.to_csv(
    "outputs/investor_cohort_analysis.csv",
    index=False
)

print("Investor Cohort Analysis Saved")
# ======================================================
# SIP Continuity Analysis
# ======================================================
# ======================================================
# SIP Continuity Analysis
# ======================================================

print("\nComputing SIP Continuity Analysis...")

# Filter only SIP transactions
sip = transactions[
    transactions["transaction_type"] == "SIP"
].copy()

# Sort by investor and date
sip = sip.sort_values(
    ["investor_id", "transaction_date"]
)

# Calculate gap between consecutive SIPs
sip["gap_days"] = (
    sip.groupby("investor_id")["transaction_date"]
    .diff()
    .dt.days
)

# Investors having at least 6 SIP transactions
sip_summary = (
    sip.groupby("investor_id")
    .agg(
        sip_count=("transaction_type", "count"),
        avg_gap=("gap_days", "mean")
    )
    .reset_index()
)

sip_summary = sip_summary[
    sip_summary["sip_count"] >= 6
]

# Flag investors
sip_summary["status"] = np.where(
    sip_summary["avg_gap"] > 35,
    "At Risk",
    "Active"
)

print(sip_summary.head())

sip_summary.to_csv(
    "outputs/sip_continuity_analysis.csv",
    index=False
)

print("SIP Continuity Analysis Saved")


# ======================================================
# Sector HHI Concentration
# ======================================================

print("\nComputing Sector HHI Concentration...")

holdings = pd.read_csv("data/raw/09_portfolio_holdings.csv")

# Calculate HHI for each fund
hhi_results = (
    holdings.groupby("amfi_code")["weight_pct"]
    .apply(lambda x: ((x / 100) ** 2).sum())
    .reset_index(name="HHI")
)

# Merge with scheme names
hhi_results = hhi_results.merge(
    fund_master[["amfi_code", "scheme_name"]],
    on="amfi_code",
    how="left"
)

# Sort by highest concentration
hhi_results = hhi_results.sort_values(
    "HHI",
    ascending=False
)

print(hhi_results.head())

# Save report
hhi_results.to_csv(
    "outputs/sector_hhi.csv",
    index=False
)

print("Sector HHI Report Saved")

# recommedned code
import pandas as pd

print("=== Mutual Fund Recommender ===")

performance = pd.read_csv("data/raw/07_scheme_performance.csv")

risk = input("Enter Risk Appetite (Low/Moderate/High): ").strip().title()

recommend = performance[
    performance["risk_grade"] == risk
]

if recommend.empty:
    print("No funds found for this risk level.")
    exit()

recommend = recommend.sort_values(
    by="sharpe_ratio",
    ascending=False
)

print("\nTop 3 Recommended Funds\n")

print(
    recommend[
        [
            "scheme_name",
            "fund_house",
            "risk_grade",
            "sharpe_ratio",
            "return_3yr_pct"
        ]
    ].head(3)
)
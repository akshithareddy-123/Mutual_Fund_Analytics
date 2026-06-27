import os
import pandas as pd
import numpy as np

print("STARTING PERFORMANCE ANALYTICS")

os.makedirs("outputs", exist_ok=True)

# -------------------------
# Load datasets
# -------------------------

fund_master = pd.read_csv("data/raw/01_fund_master.csv")
nav = pd.read_csv("data/raw/02_nav_history.csv")
benchmark = pd.read_csv("data/raw/10_benchmark_indices.csv")
performance = pd.read_csv("data/raw/07_scheme_performance.csv")

print("Datasets Loaded Successfully")

# -------------------------
# Convert dates
# -------------------------

nav["date"] = pd.to_datetime(nav["date"])
benchmark["date"] = pd.to_datetime(benchmark["date"])

# -------------------------
# Sort NAV
# -------------------------

nav = nav.sort_values(
    ["amfi_code", "date"]
)

# -------------------------
# Daily Returns
# -------------------------

print("\nComputing Daily Returns...")

nav["daily_return"] = (
    nav.groupby("amfi_code")["nav"]
    .pct_change()
)

print(nav.head())

nav.to_csv(
    "outputs/daily_returns.csv",
    index=False
)

print("Daily Returns Saved")
# ======================================================
# CAGR CALCULATION
# ======================================================

print("\nComputing CAGR...")

cagr_results = []

for code, group in nav.groupby("amfi_code"):

    group = group.sort_values("date")

    start_nav = group.iloc[0]["nav"]
    end_nav = group.iloc[-1]["nav"]

    total_years = (
        (group.iloc[-1]["date"] - group.iloc[0]["date"]).days
        / 365.25
    )

    if total_years <= 0:
        continue

    cagr = ((end_nav / start_nav) ** (1 / total_years) - 1) * 100

    scheme = fund_master.loc[
        fund_master["amfi_code"] == code,
        "scheme_name"
    ]

    if len(scheme) > 0:
        scheme = scheme.values[0]
    else:
        scheme = "Unknown"

    cagr_results.append([
        code,
        scheme,
        round(cagr, 2)
    ])

cagr_df = pd.DataFrame(
    cagr_results,
    columns=[
        "amfi_code",
        "scheme_name",
        "CAGR (%)"
    ]
)

cagr_df = cagr_df.sort_values(
    "CAGR (%)",
    ascending=False
)

cagr_df.to_csv(
    "outputs/cagr_table.csv",
    index=False
)

print(cagr_df.head())

print("CAGR Table Saved")
# ======================================================
# SHARPE RATIO
# ======================================================

print("\nComputing Sharpe Ratio...")

RISK_FREE_RATE = 0.065

sharpe_results = []

for code, group in nav.groupby("amfi_code"):

    returns = group["daily_return"].dropna()

    if len(returns) < 2:
        continue

    annual_return = returns.mean() * 252
    annual_std = returns.std() * np.sqrt(252)

    if annual_std == 0:
        sharpe = np.nan
    else:
        sharpe = (annual_return - RISK_FREE_RATE) / annual_std

    scheme = fund_master.loc[
        fund_master["amfi_code"] == code,
        "scheme_name"
    ]

    if len(scheme) > 0:
        scheme = scheme.values[0]
    else:
        scheme = "Unknown"

    sharpe_results.append([
        code,
        scheme,
        round(sharpe, 4)
    ])

sharpe_df = pd.DataFrame(
    sharpe_results,
    columns=[
        "amfi_code",
        "scheme_name",
        "Sharpe Ratio"
    ]
)

sharpe_df = sharpe_df.sort_values(
    "Sharpe Ratio",
    ascending=False
)

sharpe_df.to_csv(
    "outputs/sharpe_ratio.csv",
    index=False
)

print(sharpe_df.head())

print("Sharpe Ratio Saved")
# ======================================================
# SORTINO RATIO
# ======================================================

print("\nComputing Sortino Ratio...")

RISK_FREE_RATE = 0.065

sortino_results = []

for code, group in nav.groupby("amfi_code"):

    returns = group["daily_return"].dropna()

    if len(returns) < 2:
        continue

    downside_returns = returns[returns < 0]

    if len(downside_returns) == 0:
        continue

    annual_return = returns.mean() * 252
    downside_std = downside_returns.std() * np.sqrt(252)

    if downside_std == 0:
        sortino = np.nan
    else:
        sortino = (annual_return - RISK_FREE_RATE) / downside_std

    scheme = fund_master.loc[
        fund_master["amfi_code"] == code,
        "scheme_name"
    ]

    if len(scheme) > 0:
        scheme = scheme.values[0]
    else:
        scheme = "Unknown"

    sortino_results.append([
        code,
        scheme,
        round(sortino, 4)
    ])

sortino_df = pd.DataFrame(
    sortino_results,
    columns=[
        "amfi_code",
        "scheme_name",
        "Sortino Ratio"
    ]
)

sortino_df = sortino_df.sort_values(
    "Sortino Ratio",
    ascending=False
)

sortino_df.to_csv(
    "outputs/sortino_ratio.csv",
    index=False
)

print(sortino_df.head())

print("Sortino Ratio Saved")
from scipy.stats import linregress

# ======================================================
# ALPHA & BETA
# ======================================================

print("\nComputing Alpha & Beta...")

benchmark = benchmark.sort_values("date")

benchmark["benchmark_return"] = benchmark["close_value"].pct_change()

alpha_beta = []

for code, group in nav.groupby("amfi_code"):

    temp = group[["date", "daily_return"]].copy()

    merged = pd.merge(
        temp,
        benchmark[["date", "benchmark_return"]],
        on="date",
        how="inner"
    ).dropna()

    if len(merged) < 30:
        continue

    slope, intercept, r, p, stderr = linregress(
        merged["benchmark_return"],
        merged["daily_return"]
    )

    alpha = intercept * 252
    beta = slope

    scheme = fund_master.loc[
        fund_master["amfi_code"] == code,
        "scheme_name"
    ]

    if len(scheme) > 0:
        scheme = scheme.values[0]
    else:
        scheme = "Unknown"

    alpha_beta.append([
        code,
        scheme,
        round(alpha, 4),
        round(beta, 4)
    ])

alpha_beta_df = pd.DataFrame(
    alpha_beta,
    columns=[
        "amfi_code",
        "scheme_name",
        "Alpha",
        "Beta"
    ]
)

alpha_beta_df.to_csv(
    "outputs/alpha_beta.csv",
    index=False
)

print(alpha_beta_df.head())

print("Alpha & Beta Saved")
# ======================================================
# MAXIMUM DRAWDOWN
# ======================================================

print("\nComputing Maximum Drawdown...")

drawdown_results = []

for code, group in nav.groupby("amfi_code"):

    group = group.sort_values("date").copy()

    group["running_max"] = group["nav"].cummax()
    group["drawdown"] = (group["nav"] / group["running_max"]) - 1

    max_dd = group["drawdown"].min()

    dd_date = group.loc[group["drawdown"].idxmin(), "date"]

    scheme = fund_master.loc[
        fund_master["amfi_code"] == code,
        "scheme_name"
    ]

    if len(scheme) > 0:
        scheme = scheme.values[0]
    else:
        scheme = "Unknown"

    drawdown_results.append([
        code,
        scheme,
        round(max_dd * 100, 2),
        dd_date
    ])

drawdown_df = pd.DataFrame(
    drawdown_results,
    columns=[
        "amfi_code",
        "scheme_name",
        "Maximum Drawdown (%)",
        "Worst Date"
    ]
)

drawdown_df = drawdown_df.sort_values(
    "Maximum Drawdown (%)"
)

drawdown_df.to_csv(
    "outputs/max_drawdown.csv",
    index=False
)

print(drawdown_df.head())

print("Maximum Drawdown Saved")
# ======================================================
# FUND SCORECARD
# ======================================================

print("\nComputing Fund Scorecard...")

# Merge all metrics
score_df = cagr_df.merge(
    sharpe_df[["amfi_code", "Sharpe Ratio"]],
    on="amfi_code"
)

score_df = score_df.merge(
    alpha_beta_df[["amfi_code", "Alpha"]],
    on="amfi_code"
)

score_df = score_df.merge(
    drawdown_df[["amfi_code", "Maximum Drawdown (%)"]],
    on="amfi_code"
)

score_df = score_df.merge(
    performance[["amfi_code", "expense_ratio_pct"]],
    on="amfi_code"
)

# Rankings
score_df["return_rank"] = score_df["CAGR (%)"].rank(ascending=False)
score_df["sharpe_rank"] = score_df["Sharpe Ratio"].rank(ascending=False)
score_df["alpha_rank"] = score_df["Alpha"].rank(ascending=False)
score_df["expense_rank"] = score_df["expense_ratio_pct"].rank(ascending=True)
score_df["drawdown_rank"] = score_df["Maximum Drawdown (%)"].rank(ascending=False)

# Composite Score
score_df["Fund Score"] = (
      score_df["return_rank"] * 0.30
    + score_df["sharpe_rank"] * 0.25
    + score_df["alpha_rank"] * 0.20
    + score_df["expense_rank"] * 0.15
    + score_df["drawdown_rank"] * 0.10
)

score_df = score_df.sort_values("Fund Score")

score_df.to_csv(
    "outputs/fund_scorecard.csv",
    index=False
)

print(score_df.head())

print("Fund Scorecard Saved")
import matplotlib.pyplot as plt

# ======================================================
# BENCHMARK COMPARISON
# ======================================================

print("\nCreating Benchmark Comparison Chart...")

top5 = score_df.head(5)["amfi_code"].tolist()

plt.figure(figsize=(12,6))

for code in top5:

    temp = nav[
        nav["amfi_code"] == code
    ].sort_values("date")

    scheme = fund_master.loc[
        fund_master["amfi_code"] == code,
        "scheme_name"
    ].values[0]

    plt.plot(
        temp["date"],
        temp["nav"],
        label=scheme
    )

plt.plot(
    benchmark["date"],
    benchmark["close_value"],
    linewidth=3,
    label="Benchmark"
)

plt.legend()

plt.title("Top 5 Funds vs Benchmark")

plt.tight_layout()

plt.savefig(
    "outputs/benchmark_comparison.png"
)

plt.close()

print("Benchmark Comparison Saved")

print("\n======================================")
print("DAY 4 COMPLETED SUCCESSFULLY")
print("======================================")
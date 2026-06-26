import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

print("STARTING EDA")

# Create charts folder
os.makedirs("charts", exist_ok=True)

print("Loading datasets...")

fund_master = pd.read_csv("data/raw/01_fund_master.csv")
nav = pd.read_csv("data/raw/02_nav_history.csv")
aum = pd.read_csv("data/raw/03_aum_by_fund_house.csv")
sip = pd.read_csv("data/raw/04_monthly_sip_inflows.csv")
category = pd.read_csv("data/raw/05_category_inflows.csv")
folios = pd.read_csv("data/raw/06_industry_folio_count.csv")
performance = pd.read_csv("data/raw/07_scheme_performance.csv")
transactions = pd.read_csv("data/raw/08_investor_transactions.csv")
holdings = pd.read_csv("data/raw/09_portfolio_holdings.csv")
benchmark = pd.read_csv("data/raw/10_benchmark_indices.csv")

print("===================================")
print("Datasets Loaded Successfully")
print("===================================")

print("Fund Master:", fund_master.shape)
print("NAV History:", nav.shape)
print("AUM:", aum.shape)
print("SIP:", sip.shape)
print("Category:", category.shape)
print("Folios:", folios.shape)
print("Performance:", performance.shape)
print("Transactions:", transactions.shape)
print("Holdings:", holdings.shape)
print("Benchmark:", benchmark.shape)

print("EDA SETUP COMPLETE")
# ===========================================
# 1. NAV TREND ANALYSIS
# ===========================================

print("\nCreating NAV Trend Chart...")

# Convert date column
nav["date"] = pd.to_datetime(nav["date"])

# Merge with fund names
nav_plot = nav.merge(
    fund_master[["amfi_code", "scheme_name"]],
    on="amfi_code",
    how="left"
)

# Create interactive chart
fig = px.line(
    nav_plot,
    x="date",
    y="nav",
    color="scheme_name",
    title="Daily NAV Trend of Mutual Fund Schemes (2022–2026)"
)

# Highlight important periods
fig.add_vrect(
    x0="2023-01-01",
    x1="2023-12-31",
    fillcolor="green",
    opacity=0.10,
    annotation_text="2023 Bull Run",
    line_width=0
)

fig.add_vrect(
    x0="2024-01-01",
    x1="2024-12-31",
    fillcolor="red",
    opacity=0.08,
    annotation_text="2024 Market Correction",
    line_width=0
)

# Save chart
fig.write_image("charts/nav_trend.png")

print("NAV Trend Chart Saved")
# ===========================================
# ===========================================
# 2. AUM GROWTH BAR CHART
# ===========================================

print("\nCreating AUM Growth Chart...")

aum["date"] = pd.to_datetime(aum["date"])
aum["year"] = aum["date"].dt.year

plt.figure(figsize=(14,7))

sns.barplot(
    data=aum,
    x="year",
    y="aum_crore",
    hue="fund_house"
)

plt.title("AUM Growth by Fund House (2022-2025)")
plt.xlabel("Year")
plt.ylabel("AUM (Crore)")
plt.xticks(rotation=0)

plt.tight_layout()
plt.savefig("charts/aum_growth.png")
plt.close()

print("AUM Growth Chart Saved")
print("\nSIP Columns:")
print(sip.columns.tolist())

print("\nCategory Columns:")
print(category.columns.tolist())

print("\nFolios Columns:")
print(folios.columns.tolist())

print("\nHoldings Columns:")
print(holdings.columns.tolist())
# ===========================================
# 3. SIP INFLOW TIME SERIES
# ===========================================

print("\nCreating SIP Trend Chart...")

sip["month"] = pd.to_datetime(sip["month"])

fig = px.line(
    sip,
    x="month",
    y="sip_inflow_crore",
    title="Monthly SIP Inflow Trend (2022-2025)",
    markers=True
)

max_row = sip.loc[sip["sip_inflow_crore"].idxmax()]

fig.add_annotation(
    x=max_row["month"],
    y=max_row["sip_inflow_crore"],
    text=f"Highest: {max_row['sip_inflow_crore']:.0f} Cr",
    showarrow=True
)

fig.write_html("charts/sip_trend.html")

print("SIP Trend Saved")


# ===========================================
# 4. CATEGORY INFLOW HEATMAP
# ===========================================

print("\nCreating Category Heatmap...")

pivot = category.pivot(
    index="category",
    columns="month",
    values="net_inflow_crore"
)

plt.figure(figsize=(14,6))

sns.heatmap(
    pivot,
    cmap="YlGnBu",
    annot=False
)

plt.title("Category Inflow Heatmap")

plt.tight_layout()

plt.savefig("charts/category_heatmap.png")

plt.close()

print("Category Heatmap Saved")


# ===========================================
# 5. AGE GROUP PIE CHART
# ===========================================

print("\nCreating Age Group Chart...")

plt.figure(figsize=(7,7))

transactions["age_group"].value_counts().plot(
    kind="pie",
    autopct="%1.1f%%"
)

plt.ylabel("")
plt.title("Investor Age Groups")

plt.savefig("charts/age_group_pie.png")

plt.close()

print("Age Group Chart Saved")


# ===========================================
# 6. GENDER DISTRIBUTION
# ===========================================

print("\nCreating Gender Chart...")

plt.figure(figsize=(6,6))

transactions["gender"].value_counts().plot(
    kind="pie",
    autopct="%1.1f%%"
)

plt.ylabel("")
plt.title("Gender Distribution")

plt.savefig("charts/gender_pie.png")

plt.close()

print("Gender Chart Saved")


# ===========================================
# 7. SIP AMOUNT BY STATE
# ===========================================

print("\nCreating State Distribution...")

state_data = (
    transactions.groupby("state")["amount_inr"]
    .sum()
    .sort_values(ascending=False)
)

plt.figure(figsize=(12,8))

state_data.plot(kind="barh")

plt.title("Investment Amount by State")

plt.tight_layout()

plt.savefig("charts/state_distribution.png")

plt.close()

print("State Distribution Saved")


# ===========================================
# 8. CITY TIER
# ===========================================

print("\nCreating City Tier Chart...")

plt.figure(figsize=(6,6))

transactions["city_tier"].value_counts().plot(
    kind="pie",
    autopct="%1.1f%%"
)

plt.ylabel("")
plt.title("T30 vs B30")

plt.savefig("charts/city_tier.png")

plt.close()

print("City Tier Saved")


# ===========================================
# 9. FOLIO GROWTH
# ===========================================

print("\nCreating Folio Growth Chart...")

folios["month"] = pd.to_datetime(folios["month"])

plt.figure(figsize=(12,5))

plt.plot(
    folios["month"],
    folios["total_folios_crore"],
    marker="o"
)

plt.title("Industry Folio Growth")

plt.xlabel("Month")

plt.ylabel("Folios (Crore)")

plt.grid(True)

plt.tight_layout()

plt.savefig("charts/folio_growth.png")

plt.close()

print("Folio Growth Saved")
# ===========================================
# 10. NAV RETURN CORRELATION
# ===========================================

print("\nCreating Correlation Matrix...")

top10 = nav_plot["scheme_name"].dropna().unique()[:10]

corr_df = nav_plot[
    nav_plot["scheme_name"].isin(top10)
]

pivot = corr_df.pivot_table(
    index="date",
    columns="scheme_name",
    values="nav"
)

returns = pivot.pct_change().dropna()

plt.figure(figsize=(10,8))

sns.heatmap(
    returns.corr(),
    cmap="coolwarm",
    annot=False
)

plt.title("NAV Return Correlation")

plt.tight_layout()

plt.savefig("charts/nav_correlation.png")

plt.close()

print("Correlation Matrix Saved")


# ===========================================
# 11. SECTOR ALLOCATION
# ===========================================

print("\nCreating Sector Allocation...")

sector = (
    holdings.groupby("sector")["weight_pct"]
    .sum()
    .sort_values(ascending=False)
)

plt.figure(figsize=(8,8))

plt.pie(
    sector,
    labels=sector.index,
    autopct="%1.1f%%"
)

centre_circle = plt.Circle((0,0),0.55,color="white")
fig = plt.gcf()
fig.gca().add_artist(centre_circle)

plt.title("Sector Allocation")

plt.savefig("charts/sector_allocation.png")

plt.close()

print("Sector Allocation Saved")


print("\n=================================")
print("DAY 3 EDA COMPLETED SUCCESSFULLY")
print("Charts saved inside charts folder.")
print("=================================")
import pandas as pd
import os

# Create processed folder
os.makedirs("data/processed", exist_ok=True)

print("STARTING DATA CLEANING")

# =====================================================
# 1. NAV HISTORY CLEANING
# =====================================================

nav = pd.read_csv("data/raw/02_nav_history.csv")

nav["date"] = pd.to_datetime(nav["date"])

nav = nav.sort_values(
    by=["amfi_code", "date"]
)

nav["nav"] = nav.groupby(
    "amfi_code"
)["nav"].ffill()

nav = nav.drop_duplicates()

nav = nav[
    nav["nav"] > 0
]

nav.to_csv(
    "data/processed/nav_history_cleaned.csv",
    index=False
)

print("✅ NAV History cleaned")

# =====================================================
# 2. INVESTOR TRANSACTIONS CLEANING
# =====================================================

txn = pd.read_csv(
    "data/raw/08_investor_transactions.csv"
)

print("\nTransaction Columns:")
print(txn.columns.tolist())

# Standardize transaction type
txn["transaction_type"] = (
    txn["transaction_type"]
    .astype(str)
    .str.strip()
    .str.title()
)

# Correct column name
txn = txn[
    txn["amount_inr"] > 0
]

# Fix date format
txn["transaction_date"] = pd.to_datetime(
    txn["transaction_date"]
)

# Validate KYC values
valid_kyc = [
    "Verified",
    "Pending"
]

txn = txn[
    txn["kyc_status"].isin(valid_kyc)
]

txn.to_csv(
    "data/processed/investor_transactions_cleaned.csv",
    index=False
)

print("✅ Investor Transactions cleaned")

# =====================================================
# 3. SCHEME PERFORMANCE CLEANING
# =====================================================

perf = pd.read_csv(
    "data/raw/07_scheme_performance.csv"
)

print("\nScheme Performance Columns:")
print(perf.columns.tolist())

# Convert all return columns to numeric
for col in perf.columns:
    if "return" in col.lower():
        perf[col] = pd.to_numeric(
            perf[col],
            errors="coerce"
        )

# Validate expense ratio
if "expense_ratio_pct" in perf.columns:

    perf = perf[
        (perf["expense_ratio_pct"] >= 0.1)
        &
        (perf["expense_ratio_pct"] <= 2.5)
    ]

perf.to_csv(
    "data/processed/scheme_performance_cleaned.csv",
    index=False
)

print("✅ Scheme Performance cleaned")

print("\nFINISHED DATA CLEANING")
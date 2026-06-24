import pandas as pd
from sqlalchemy import create_engine

print("STARTING DATABASE LOAD")

engine = create_engine(
    "sqlite:///bluestock_mf.db"
)

files = {
    "fund_master": "data/raw/01_fund_master.csv",
    "nav_history": "data/processed/nav_history_cleaned.csv",
    "aum": "data/raw/03_aum_by_fund_house.csv",
    "sip": "data/raw/04_monthly_sip_inflows.csv",
    "category_inflows": "data/raw/05_category_inflows.csv",
    "folios": "data/raw/06_industry_folio_count.csv",
    "scheme_performance": "data/processed/scheme_performance_cleaned.csv",
    "transactions": "data/processed/investor_transactions_cleaned.csv",
    "holdings": "data/raw/09_portfolio_holdings.csv",
    "benchmark": "data/raw/10_benchmark_indices.csv"
}

for table, path in files.items():

    print(f"\nLoading {table}...")

    df = pd.read_csv(path)

    df.to_sql(
        table,
        engine,
        if_exists="replace",
        index=False
    )

    print(f"{table}: {len(df)} rows loaded")

print("\nDATABASE CREATED SUCCESSFULLY")
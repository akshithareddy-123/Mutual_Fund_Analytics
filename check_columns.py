import pandas as pd

txn = pd.read_csv("data/raw/08_investor_transactions.csv")

print(txn.columns.tolist())
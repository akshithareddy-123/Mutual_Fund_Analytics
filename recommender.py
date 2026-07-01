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
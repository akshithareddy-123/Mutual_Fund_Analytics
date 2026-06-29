import pandas as pd
import os

print("Program Started")

folder = "data/raw"

print("Files found:", os.listdir(folder))

for file in os.listdir(folder):
    if file.endswith(".csv"):
        path = os.path.join(folder, file)

        print("\n" + "="*50)
        print("File:", file)

        df = pd.read_csv(path)

        print("Shape:", df.shape)

        print("\nData Types:")
        print(df.dtypes)

        print("\nFirst 5 Rows:")
        print(df.head())
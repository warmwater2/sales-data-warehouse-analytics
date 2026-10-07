import pandas as pd

file_path = "data/raw/superstore.csv"

df = pd.read_csv(file_path)

print("Number of rows:", len(df))

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nData types:")
print(df.dtypes)

print("\nFirst 5 records:")
print(df.head())
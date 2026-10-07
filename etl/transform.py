import pandas as pd

input_file = "data/raw/superstore.csv"
output_file = "data/processed/cleaned_sales.csv"

df = pd.read_csv(input_file)

print("Original rows:", len(df))

df = df.drop_duplicates()

df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

numeric_columns = ["Sales", "Quantity", "Discount", "Profit"]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

text_columns = [
    "Customer Name",
    "Segment",
    "Product Name",
    "Category",
    "Sub-Category",
    "City",
    "State",
    "Region"
]

for column in text_columns:
    df[column] = df[column].fillna("Unknown")
    df[column] = df[column].astype(str).str.strip()

df["Profit Margin"] = (df["Profit"] / df["Sales"]) * 100

df["Profit Margin"] = df["Profit Margin"].replace(
    [float("inf"), -float("inf")], 0
)

df.to_csv(output_file, index=False)

print("Cleaned rows:", len(df))
print("Duplicates removed:", len(pd.read_csv(input_file)) - len(df))
print("Cleaned dataset saved to:", output_file)

print("\nRemaining missing values:")
print(df.isnull().sum())
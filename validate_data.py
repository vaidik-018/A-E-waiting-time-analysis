import pandas as pd

# Load numerical dataset
df = pd.read_csv("dataset/aed_waiting_time_numeric.csv")

print("========== DATASET VALIDATION ==========\n")

# 1. Dataset shape
print("Dataset shape:")
print(df.shape)

# 2. Column names
print("\nColumn names:")
print(df.columns.tolist())

# 3. Data types
print("\nData types:")
print(df.dtypes)

# 4. Missing values
print("\nMissing values:")
print(df.isnull().sum())

# 5. Duplicate rows
print("\nDuplicate rows:")
print(df.duplicated().sum())

# 6. Hospital count
print("\nNumber of hospitals:")
print(df["hospName"].nunique())

# 7. Check negative waiting times
numeric_columns = [
    "t1wt_minutes",
    "t2wt_minutes",
    "t2wt_upper_bound_minutes",
    "t3p50_minutes",
    "t3p95_minutes",
    "t45p50_minutes",
    "t45p95_minutes"
]

print("\nNegative waiting-time values:")

for col in numeric_columns:
    if col in df.columns:
        negative_count = (df[col] < 0).sum()
        print(f"{col}: {negative_count}")

# 8. Basic statistics
print("\nBasic statistics:")
print(df[numeric_columns].describe())

print("\n========== VALIDATION COMPLETE ==========")
import pandas as pd

# Step 1: Load dataset
df = pd.read_csv("dataset/aed_waiting_time.csv")

print("Original dataset shape:", df.shape)

# Step 2: Remove extra spaces from text columns
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].str.strip()

# Step 3: Standardize missing-value markers
df = df.replace(r"^\s*$", pd.NA, regex=True)
df = df.replace(["N/A", "NA"], pd.NA)

# Step 4: Check missing values
print("\nMissing values before cleaning:")
print(df.isnull().sum())

# Step 5: Check duplicate records
print("\nDuplicate rows:", df.duplicated().sum())

# Step 6: Check hospital names
print("\nNumber of hospitals:", df["hospName"].nunique())

# Step 7: Check missing values after standardization
print("\nMissing values after standardization:")
print(df.isnull().sum())

# Step 8: Save cleaned dataset
df.to_csv(
    "dataset/aed_waiting_time_cleaned.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nCleaned dataset saved successfully!")
print("Final dataset shape:", df.shape)
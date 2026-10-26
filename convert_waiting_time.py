import pandas as pd
import re

# Load cleaned dataset
df = pd.read_csv("dataset/aed_waiting_time_cleaned.csv")


def convert_to_minutes(value):
    """Convert exact waiting times to minutes."""

    if pd.isna(value):
        return None

    value = str(value).strip().lower()

    # Values without an exact numerical waiting time
    if value in ["", "n/a", "na"]:
        return None

    if "less than" in value:
        return None

    if "managing multiple" in value:
        return None

    # Extract numerical value
    match = re.search(r"(\d+(?:\.\d+)?)\s*(minutes?|mins?|hours?|hrs?)", value)

    if not match:
        return None

    number = float(match.group(1))
    unit = match.group(2)

    if unit.startswith(("hour", "hr")):
        return number * 60

    return number


# Create new numerical columns
time_columns = ["t1wt", "t2wt", "t3p50", "t3p95", "t45p50", "t45p95"]
# Create an upper-bound column for T2 waiting time
def convert_t2_upper_bound(value):
    if pd.isna(value):
        return None

    value = str(value).strip().lower()

    if "less than 15 minutes" in value:
        return 15

    return convert_to_minutes(value)


df["t2wt_upper_bound_minutes"] = df["t2wt"].apply(convert_t2_upper_bound)
for col in time_columns:
    df[col + "_minutes"] = df[col].apply(convert_to_minutes)

# Show converted values
print("Converted waiting-time columns:")
print(df[[
    "hospName",
    "t3p50",
    "t3p50_minutes",
    "t3p95",
    "t3p95_minutes",
    "t45p50",
    "t45p50_minutes",
    "t45p95",
    "t45p95_minutes"
]].head(10))

# Save new dataset
df.to_csv(
    "dataset/aed_waiting_time_numeric.csv",
    index=False,
    encoding="utf-8-sig"
) 

print("\nNumerical dataset saved successfully!")
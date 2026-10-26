import pandas as pd

# Load numerical dataset
df = pd.read_csv("dataset/aed_waiting_time_numeric.csv")

print("========== EXPLORATORY DATA ANALYSIS ==========\n")

# ------------------------------------------------
# 1. Dataset Information
# ------------------------------------------------

print("Number of hospitals:", df["hospName"].nunique())
print("Number of records:", len(df))

# ------------------------------------------------
# 2. Waiting Time Columns
# ------------------------------------------------

waiting_columns = [
    "t3p50_minutes",
    "t3p95_minutes",
    "t45p50_minutes",
    "t45p95_minutes"
]

# ------------------------------------------------
# 3. Overall Statistics
# ------------------------------------------------

print("\n========== OVERALL WAITING TIME STATISTICS ==========\n")

statistics = df[waiting_columns].describe().T

print(statistics[[
    "mean",
    "50%",
    "min",
    "max",
    "std"
]])

# ------------------------------------------------
# 4. Average Waiting Time
# ------------------------------------------------

print("\n========== AVERAGE WAITING TIME ==========\n")

for column in waiting_columns:
    print(f"{column}: {df[column].mean():.2f} minutes")

# ------------------------------------------------
# 5. Fastest and Slowest Hospitals
# ------------------------------------------------

print("\n========== TRIAGE 3 (MEDIAN) ==========\n")

fastest_t3 = df.loc[df["t3p50_minutes"].idxmin()]
slowest_t3 = df.loc[df["t3p50_minutes"].idxmax()]

print("Fastest hospital:")
print(f"{fastest_t3['hospName']} - {fastest_t3['t3p50_minutes']} minutes")

print("\nSlowest hospital:")
print(f"{slowest_t3['hospName']} - {slowest_t3['t3p50_minutes']} minutes")

# ------------------------------------------------
# 6. Triage 4 & 5 Analysis
# ------------------------------------------------

print("\n========== TRIAGE 4 & 5 (MEDIAN) ==========\n")

fastest_t45 = df.loc[df["t45p50_minutes"].idxmin()]
slowest_t45 = df.loc[df["t45p50_minutes"].idxmax()]

print("Fastest hospital:")
print(f"{fastest_t45['hospName']} - {fastest_t45['t45p50_minutes']} minutes")

print("\nSlowest hospital:")
print(f"{slowest_t45['hospName']} - {slowest_t45['t45p50_minutes']} minutes")

# ------------------------------------------------
# 7. Hospital-wise Waiting Time
# ------------------------------------------------

print("\n========== HOSPITAL-WISE WAITING TIME ==========\n")

hospital_analysis = df[
    [
        "hospName",
        "t3p50_minutes",
        "t3p95_minutes",
        "t45p50_minutes",
        "t45p95_minutes"
    ]
].copy()

print(hospital_analysis.to_string(index=False))

print("\n========== EDA COMPLETE ==========")
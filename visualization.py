import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("dataset/aed_waiting_time_numeric.csv")

# Create output folder
import os
os.makedirs("visualizations", exist_ok=True)


# ============================================================
# 1. Hospital-wise Triage 3 Waiting Time
# ============================================================

df_t3 = df.sort_values("t3p50_minutes")

plt.figure(figsize=(12, 7))

plt.barh(
    df_t3["hospName"],
    df_t3["t3p50_minutes"]
)

plt.xlabel("Waiting Time (Minutes)")
plt.ylabel("Hospital")
plt.title("Hospital-wise Triage 3 Median Waiting Time")

plt.tight_layout()

plt.savefig(
    "visualizations/triage3_waiting_time.png",
    dpi=300
)

plt.show()


# ============================================================
# 2. Hospital-wise Triage 4 & 5 Waiting Time
# ============================================================

df_t45 = df.sort_values("t45p50_minutes")

plt.figure(figsize=(12, 7))

plt.barh(
    df_t45["hospName"],
    df_t45["t45p50_minutes"]
)

plt.xlabel("Waiting Time (Minutes)")
plt.ylabel("Hospital")
plt.title("Hospital-wise Triage 4 & 5 Median Waiting Time")

plt.tight_layout()

plt.savefig(
    "visualizations/triage45_waiting_time.png",
    dpi=300
)

plt.show()


# ============================================================
# 3. Average Waiting Time Comparison
# ============================================================

categories = [
    "Triage 3\nMedian",
    "Triage 3\n95th Percentile",
    "Triage 4/5\nMedian",
    "Triage 4/5\n95th Percentile"
]

average_values = [
    df["t3p50_minutes"].mean(),
    df["t3p95_minutes"].mean(),
    df["t45p50_minutes"].mean(),
    df["t45p95_minutes"].mean()
]

plt.figure(figsize=(10, 6))

plt.bar(categories, average_values)

plt.ylabel("Average Waiting Time (Minutes)")
plt.title("Average Waiting Time by Triage Category")

plt.tight_layout()

plt.savefig(
    "visualizations/triage_comparison.png",
    dpi=300
)

plt.show()


# ============================================================
# 4. Waiting Time Distribution
# ============================================================

plt.figure(figsize=(10, 6))

plt.hist(
    df["t45p50_minutes"],
    bins=8
)

plt.xlabel("Waiting Time (Minutes)")
plt.ylabel("Number of Hospitals")
plt.title("Distribution of Triage 4 & 5 Median Waiting Time")

plt.tight_layout()

plt.savefig(
    "visualizations/waiting_time_distribution.png",
    dpi=300
)

plt.show()


print("\nVisualization completed successfully!")
print("Graphs saved in the 'visualizations' folder.")
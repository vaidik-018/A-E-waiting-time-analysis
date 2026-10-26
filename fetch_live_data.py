import requests
import pandas as pd
import re
import os
from datetime import datetime

# Official Hong Kong Hospital Authority API
URL = "https://www.ha.org.hk/opendata/aed/aedwtdata2-en.json"


def convert_to_minutes(value):

    if pd.isna(value):
        return None

    value = str(value).strip().lower()

    if value in ["", "n/a", "na"]:
        return None

    if "less than" in value:
        return None

    if "managing multiple" in value:
        return None

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(minutes?|mins?|hours?|hrs?)",
        value
    )

    if not match:
        return None

    number = float(match.group(1))
    unit = match.group(2)

    if unit.startswith(("hour", "hr")):
        return number * 60

    return number


def fetch_live_data():

    print("Fetching live A&E data...")

    response = requests.get(URL, timeout=20)

    response.raise_for_status()

    data = response.json()

    records = data["waitTime"]
    update_time = data["updateTime"]

    df = pd.json_normalize(records)

    # Add source update time
    df["source_update_time"] = update_time

    # Convert waiting times
    time_columns = [
        "t1wt",
        "t2wt",
        "t3p50",
        "t3p95",
        "t45p50",
        "t45p95"
    ]

    for column in time_columns:
        df[column + "_minutes"] = df[column].apply(
            convert_to_minutes
        )

    # T2 special handling
    def convert_t2_upper_bound(value):

        if pd.isna(value):
            return None

        value = str(value).strip().lower()

        if "less than 15 minutes" in value:
            return 15

        return convert_to_minutes(value)

    df["t2wt_upper_bound_minutes"] = df["t2wt"].apply(
        convert_t2_upper_bound
    )

    return df


def save_historical_data(df):

    os.makedirs("dataset", exist_ok=True)

    file_path = "dataset/historical_waiting_time.csv"

    # Add collection timestamp
    df["collection_time"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    if os.path.exists(file_path):

        old_df = pd.read_csv(file_path)

        # Prevent duplicate snapshots
        if "source_update_time" in old_df.columns:

            if df["source_update_time"].iloc[0] in old_df[
                "source_update_time"
            ].astype(str).values:

                print("This snapshot already exists.")
                return

        combined_df = pd.concat(
            [old_df, df],
            ignore_index=True
        )

    else:

        combined_df = df

    combined_df.to_csv(
        file_path,
        index=False,
        encoding="utf-8-sig"
    )

    print("Historical data saved successfully.")


if __name__ == "__main__":

    df = fetch_live_data()

    print("\nOfficial data update time:")
    print(df["source_update_time"].iloc[0])

    print("\nHospitals:")
    print(len(df))

    save_historical_data(df)

    print("\nLive data fetch completed!")
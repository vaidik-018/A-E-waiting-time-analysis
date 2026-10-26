import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import subprocess
import sys
import os
from datetime import datetime

# ==============================
# PAGE CONFIGURATION
# ==============================

st.set_page_config(
    page_title="Hong Kong A&E Waiting Time Dashboard",
    page_icon="🏥",
    layout="wide"
)

# Dashboard automatically reruns every 1 minute
st_autorefresh(
    interval=60 * 1000,
    key="data_refresh"
)

# ==============================
# FILE PATHS
# ==============================

DATA_FILE = "dataset/historical_waiting_time.csv"
FETCH_SCRIPT = "fetch_live_data.py"

# Fetch new data every 5 minutes
FETCH_INTERVAL = 5 * 60


# ==============================
# AUTOMATIC LIVE DATA FETCH
# ==============================

def get_last_fetch_time():

    if not os.path.exists(DATA_FILE):
        return None

    try:
        df = pd.read_csv(DATA_FILE)

        if "collection_time" not in df.columns:
            return None

        collection_time = pd.to_datetime(
            df["collection_time"],
            errors="coerce"
        )

        return collection_time.max()

    except Exception:
        return None


def fetch_live_data_if_needed():

    last_fetch = get_last_fetch_time()

    current_time = datetime.now()

    # If no previous data exists, fetch immediately
    if last_fetch is None:

        should_fetch = True

    else:

        elapsed_seconds = (
            current_time - last_fetch.to_pydatetime()
        ).total_seconds()

        should_fetch = elapsed_seconds >= FETCH_INTERVAL

    if should_fetch:

        try:

            result = subprocess.run(
                [sys.executable, FETCH_SCRIPT],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:

                return True, result.stdout

            else:

                return False, result.stderr

        except Exception as e:

            return False, str(e)

    return False, None


# ==============================
# FETCH LATEST DATA
# ==============================

fetch_performed, fetch_message = fetch_live_data_if_needed()


# ==============================
# LOAD DATA
# ==============================

def load_data():

    df = pd.read_csv(DATA_FILE)

    # Convert official Hospital Authority update time
    df["source_update_datetime"] = pd.to_datetime(
        df["source_update_time"],
        format="%d/%m/%Y %I:%M%p",
        errors="coerce"
    )

    # Convert our collection/fetch time
    df["collection_datetime"] = pd.to_datetime(
        df["collection_time"],
        errors="coerce"
    )

    # Latest official snapshot
    latest_time = df["source_update_datetime"].max()

    latest_df = df[
        df["source_update_datetime"] == latest_time
    ].copy()

    # Latest time when our script fetched data
    last_fetched = df["collection_datetime"].max()

    return latest_df, latest_time, last_fetched


df, latest_time, last_fetched = load_data()


# ==============================
# TITLE
# ==============================

st.title("🏥 Hong Kong A&E Waiting Time Analysis")


# ==============================
# LIVE STATUS
# ==============================

if pd.notna(latest_time):

    st.success(
        f"🟢 LIVE DATA | Hospital Authority Update: "
        f"{latest_time.strftime('%d %b %Y, %I:%M %p')}"
    )

else:

    st.warning(
        "⚠️ Unable to determine latest Hospital Authority update time."
    )


# ==============================
# LAST FETCHED
# ==============================

if pd.notna(last_fetched):

    st.info(
        f"🔄 Last Fetched: "
        f"{last_fetched.strftime('%d %b %Y, %I:%M:%S')}"
    )


# ==============================
# FETCH STATUS
# ==============================

if fetch_performed:

    st.caption(
        "✅ New live data fetched automatically."
    )

elif fetch_message:

    st.warning(
        "⚠️ Automatic data fetch failed. "
        "Showing the latest available data."
    )


st.markdown(
    "This dashboard provides an analysis of waiting times across "
    "Accident & Emergency departments in Hong Kong hospitals."
)

st.divider()


# ==============================
# SIDEBAR
# ==============================

st.sidebar.header("🔎 Filters")

hospital_list = [
    "All Hospitals"
] + sorted(
    df["hospName"].unique().tolist()
)

selected_hospital = st.sidebar.selectbox(
    "Select Hospital",
    hospital_list
)


# ==============================
# FILTER DATA
# ==============================

if selected_hospital == "All Hospitals":

    filtered_df = df.copy()

else:

    filtered_df = df[
        df["hospName"] == selected_hospital
    ]


# ==============================
# KPI SECTION
# ==============================

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "🏥 Total Hospitals",
        df["hospName"].nunique()
    )


with col2:

    st.metric(
        "⏱️ Avg Triage 3",
        f"{df['t3p50_minutes'].mean():.1f} min"
    )


with col3:

    st.metric(
        "⏱️ Avg Triage 4/5",
        f"{df['t45p50_minutes'].mean():.1f} min"
    )


with col4:

    st.metric(
        "🚨 Maximum T4/5",
        f"{df['t45p50_minutes'].max():.0f} min"
    )


st.divider()


# ==============================
# HOSPITAL INFORMATION
# ==============================

if selected_hospital != "All Hospitals":

    st.subheader(
        f"🏥 {selected_hospital}"
    )

    hospital = filtered_df.iloc[0]

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Triage 3 Median",
            f"{hospital['t3p50_minutes']:.0f} min"
        )


    with col2:

        st.metric(
            "Triage 3 95th Percentile",
            f"{hospital['t3p95_minutes']:.0f} min"
        )


    with col3:

        st.metric(
            "Triage 4/5 Median",
            f"{hospital['t45p50_minutes']:.0f} min"
        )


    with col4:

        st.metric(
            "Triage 4/5 95th Percentile",
            f"{hospital['t45p95_minutes']:.0f} min"
        )


    st.divider()


# ==============================
# TRIAGE 3 CHART
# ==============================

st.subheader(
    "📈 Hospital-wise Triage 3 Waiting Time"
)

chart_data = filtered_df[
    [
        "hospName",
        "t3p50_minutes"
    ]
].copy()

chart_data = chart_data.sort_values(
    "t3p50_minutes"
)

chart_data = chart_data.set_index(
    "hospName"
)

st.bar_chart(
    chart_data,
    x_label="Hospital",
    y_label="Waiting Time (Minutes)"
)


# ==============================
# TRIAGE 4 & 5 CHART
# ==============================

st.subheader(
    "📈 Hospital-wise Triage 4 & 5 Waiting Time"
)

chart_data_45 = filtered_df[
    [
        "hospName",
        "t45p50_minutes"
    ]
].copy()

chart_data_45 = chart_data_45.sort_values(
    "t45p50_minutes"
)

chart_data_45 = chart_data_45.set_index(
    "hospName"
)

st.bar_chart(
    chart_data_45,
    x_label="Hospital",
    y_label="Waiting Time (Minutes)"
)


# ==============================
# HIGH WAITING TIME HOSPITALS
# ==============================

st.subheader(
    "🚨 High Waiting Time Hospitals"
)

threshold = 360

high_waiting = df[
    df["t45p50_minutes"] >= threshold
][
    [
        "hospName",
        "t3p50_minutes",
        "t45p50_minutes",
        "t45p95_minutes"
    ]
].sort_values(
    "t45p50_minutes",
    ascending=False
)


if len(high_waiting) > 0:

    st.warning(
        f"{len(high_waiting)} hospitals have a "
        f"Triage 4/5 median waiting time of "
        f"{threshold} minutes or more."
    )

    st.dataframe(
        high_waiting,
        width="stretch"
    )

else:

    st.success(
        "No hospitals exceed the selected "
        "waiting-time threshold."
    )


# ==============================
# COMPLETE DATA TABLE
# ==============================

st.subheader(
    "📋 Hospital Waiting Time Data"
)

display_columns = [
    "hospName",
    "t3p50_minutes",
    "t3p95_minutes",
    "t45p50_minutes",
    "t45p95_minutes"
]

display_df = filtered_df[
    display_columns
].copy()

display_df.columns = [
    "Hospital",
    "Triage 3 Median (min)",
    "Triage 3 95th Percentile (min)",
    "Triage 4/5 Median (min)",
    "Triage 4/5 95th Percentile (min)"
]

st.dataframe(
    display_df,
    width="stretch"
)


# ==============================
# DOWNLOAD DATA
# ==============================

st.subheader(
    "📥 Download Data"
)

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="Download Filtered Data as CSV",
    data=csv_data,
    file_name="hong_kong_ae_waiting_time.csv",
    mime="text/csv"
)


# ==============================
# FOOTER
# ==============================

st.divider()

st.caption(
    "Hong Kong A&E Waiting Time Analysis | "
    "Data Science Project | "
    "Live data automatically refreshed"
)
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import subprocess
import sys
import os
from datetime import datetime


# ==========================================
# PAGE SETTINGS
# ==========================================

st.set_page_config(
    page_title="Hong Kong A&E Waiting Time Dashboard",
    page_icon="🏥",
    layout="wide"
)

# Dashboard refreshes every 1 minute
st_autorefresh(
    interval=60 * 1000,
    key="data_refresh"
)


# ==========================================
# FILE SETTINGS
# ==========================================

DATA_FILE = "dataset/historical_waiting_time.csv"
FETCH_SCRIPT = "fetch_live_data.py"

# New data will be fetched every 5 minutes
FETCH_INTERVAL = 5 * 60


# ==========================================
# FIND LAST FETCH TIME
# ==========================================

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


# ==========================================
# AUTOMATICALLY FETCH NEW DATA
# ==========================================

def fetch_live_data_if_needed():

    last_fetch = get_last_fetch_time()

    current_time = datetime.now()

    # Fetch immediately if there is no previous data
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


# ==========================================
# FETCH DATA
# ==========================================

fetch_performed, fetch_message = fetch_live_data_if_needed()


# ==========================================
# LOAD DATA
# ==========================================

def load_data():

    df = pd.read_csv(DATA_FILE)

    # Official Hospital Authority update time
    df["source_update_datetime"] = pd.to_datetime(
        df["source_update_time"],
        format="%d/%m/%Y %I:%M%p",
        errors="coerce"
    )

    # Our data collection time
    df["collection_datetime"] = pd.to_datetime(
        df["collection_time"],
        errors="coerce"
    )

    # Find latest official update
    latest_time = df["source_update_datetime"].max()

    latest_df = df[
        df["source_update_datetime"] == latest_time
    ].copy()

    # Find latest time our system fetched data
    last_fetched = df["collection_datetime"].max()

    return latest_df, latest_time, last_fetched


df, latest_time, last_fetched = load_data()


# ==========================================
# TITLE
# ==========================================

st.title("🏥 Hong Kong Accident & Emergency Waiting Time")

st.markdown(
    "This dashboard shows the latest waiting times "
    "for Accident & Emergency departments across "
    "Hong Kong hospitals."
)


# ==========================================
# LIVE STATUS
# ==========================================

if pd.notna(latest_time):

    st.success(
        f"🟢 LIVE DATA | Official Update: "
        f"{latest_time.strftime('%d %b %Y, %I:%M %p')}"
    )

else:

    st.warning(
        "⚠️ Latest update time is not available."
    )


# ==========================================
# LAST FETCHED TIME
# ==========================================

if pd.notna(last_fetched):

    st.info(
        f"🔄 Last Data Fetched: "
        f"{last_fetched.strftime('%d %b %Y, %I:%M:%S')}"
    )


# ==========================================
# FETCH STATUS
# ==========================================

if fetch_performed:

    st.caption(
        "✅ New data was fetched automatically."
    )

elif fetch_message:

    st.warning(
        "⚠️ Automatic data update failed. "
        "Showing the latest available data."
    )


st.divider()


# ==========================================
# SIDEBAR FILTER
# ==========================================

st.sidebar.header("🔎 Search Hospital")

hospital_list = [
    "All Hospitals"
] + sorted(
    df["hospName"].unique().tolist()
)

selected_hospital = st.sidebar.selectbox(
    "Select Hospital",
    hospital_list
)


# ==========================================
# FILTER DATA
# ==========================================

if selected_hospital == "All Hospitals":

    filtered_df = df.copy()

else:

    filtered_df = df[
        df["hospName"] == selected_hospital
    ]


# ==========================================
# KEY INFORMATION
# ==========================================

st.subheader("📊 Overall Waiting Time")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "🏥 Total Hospitals",
        df["hospName"].nunique()
    )


with col2:

    st.metric(
        "⏱️ Average Waiting Time",
        f"{df['t3p50_minutes'].mean():.1f} min"
    )


with col3:

    st.metric(
        "⏱️ Average Non-Urgent Waiting",
        f"{df['t45p50_minutes'].mean():.1f} min"
    )


with col4:

    st.metric(
        "🚨 Highest Waiting Time",
        f"{df['t45p50_minutes'].max():.0f} min"
    )


st.divider()


# ==========================================
# SELECTED HOSPITAL INFORMATION
# ==========================================

if selected_hospital != "All Hospitals":

    st.subheader(
        f"🏥 {selected_hospital}"
    )

    hospital = filtered_df.iloc[0]

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Regular Emergency Waiting",
            f"{hospital['t3p50_minutes']:.0f} min"
        )


    with col2:

        st.metric(
            "Longest Regular Waiting",
            f"{hospital['t3p95_minutes']:.0f} min"
        )


    with col3:

        st.metric(
            "Non-Urgent Waiting",
            f"{hospital['t45p50_minutes']:.0f} min"
        )


    with col4:

        st.metric(
            "Longest Non-Urgent Waiting",
            f"{hospital['t45p95_minutes']:.0f} min"
        )


    st.divider()


# ==========================================
# REGULAR EMERGENCY WAITING CHART
# ==========================================

st.subheader(
    "📈 Emergency Waiting Time by Hospital"
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

chart_data.columns = [
    "Average Emergency Waiting Time"
]

st.bar_chart(
    chart_data,
    x_label="Hospital",
    y_label="Waiting Time (Minutes)"
)


# ==========================================
# NON-URGENT WAITING CHART
# ==========================================

st.subheader(
    "📈 Non-Urgent Patient Waiting Time"
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

chart_data_45.columns = [
    "Non-Urgent Waiting Time"
]

st.bar_chart(
    chart_data_45,
    x_label="Hospital",
    y_label="Waiting Time (Minutes)"
)


# ==========================================
# HIGH WAITING TIME HOSPITALS
# ==========================================

st.subheader(
    "🚨 Hospitals with High Waiting Time"
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
        f"{len(high_waiting)} hospitals currently have "
        f"a non-urgent waiting time of {threshold} minutes "
        f"or more."
    )

    high_waiting.columns = [
        "Hospital",
        "Emergency Waiting Time",
        "Non-Urgent Waiting Time",
        "Longest Non-Urgent Waiting"
    ]

    st.dataframe(
        high_waiting,
        width="stretch"
    )

else:

    st.success(
        "✅ No hospitals currently have very high "
        "waiting times."
    )


# ==========================================
# COMPLETE DATA TABLE
# ==========================================

st.subheader(
    "📋 Hospital Waiting Time Details"
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


# Simple names for users
display_df.columns = [
    "Hospital",
    "Emergency Waiting Time",
    "Longest Emergency Waiting",
    "Non-Urgent Waiting Time",
    "Longest Non-Urgent Waiting"
]


st.dataframe(
    display_df,
    width="stretch"
) 


# ==========================================
# DOWNLOAD DATA
# ==========================================

st.subheader(
    "📥 Download Data"
)

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="Download Hospital Data as CSV",
    data=csv_data,
    file_name="hong_kong_ae_waiting_time.csv",
    mime="text/csv"
)


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Hong Kong A&E Waiting Time Analysis | "
    "Data Science Project | "
    "Live data automatically updated"
)
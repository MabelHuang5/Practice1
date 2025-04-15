import streamlit as st
import pandas as pd
import plotly.express as px

# Title and intro
st.title("🚌 CityBus Dashboard")
st.markdown("Upload monthly CSV data to visualize route efficiency, revenue, and transit trends.")

# Session state to store all uploaded data
if "all_data" not in st.session_state:
    st.session_state["all_data"] = pd.DataFrame()

# File uploader and month input
st.sidebar.header("📁 Upload Monthly Data")
uploaded_files = st.sidebar.file_uploader("Upload one or more CSV files", type=["csv"], accept_multiple_files=True)
month_input = st.sidebar.text_input("Enter Month (e.g., February 2023)")

# Data processing function
def process_uploaded_file(file, entered_month):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    # Clean numeric fields
    for col in ["Passengers", "Revenue", "Total Miles", "Total Hours"]:
        if col in df.columns:
            df[col] = df[col].replace({',': ''}, regex=True)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Entered_Month"] = entered_month
    return df

# Add data button
if st.sidebar.button("Add Data"):
    if uploaded_files and month_input:
        for file in uploaded_files:
            new_df = process_uploaded_file(file, month_input)
            st.session_state["all_data"] = pd.concat([st.session_state["all_data"], new_df], ignore_index=True)
        st.sidebar.success("✅ Data added!")
    else:
        st.sidebar.warning("⚠️ Please upload a CSV file and enter a month.")

# Clear all data button
if st.sidebar.button("Clear All Data"):
    st.session_state["all_data"] = pd.DataFrame()
    st.sidebar.success("🗑️ All data cleared.")

# MAIN DASHBOARD SECTION
df_all = st.session_state["all_data"]

if df_all.empty:
    st.info("Upload your first dataset using the sidebar.")
else:
    st.subheader("📋 Data Preview")
    st.write(df_all.head())

    # --- Visualization 1: Total Passengers per Route ---
    fig1 = px.bar(
        df_all.groupby("RouteName")["Passengers"].sum().reset_index(),
        x="Passengers",
        y="RouteName",
        orientation="h",
        title="Total Passengers per Route",
        labels={"Passengers": "Passengers", "RouteName": "Route"}
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- Visualization 2: Revenue per Route ---
    fig2 = px.bar(
        df_all.groupby("RouteName")["Revenue"].sum().reset_index(),
        x="Revenue",
        y="RouteName",
        orientation="h",
        title="Total Revenue per Route",
        labels={"Revenue": "Revenue ($)", "RouteName": "Route"},
        color="Revenue"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # --- Visualization 3: Monthly Total Miles by Route ---
    if "Total Miles" in df_all.columns:
        fig3 = px.bar(
            df_all.groupby(["Entered_Month", "RouteName"])["Total Miles"].sum().reset_index(),
            x="Entered_Month",
            y="Total Miles",
            color="RouteName",
            barmode="group",
            title="Monthly Total Miles by Route"
        )
        st.plotly_chart(fig3, use_container_width=True)

    # --- Visualization 4: Monthly Total Hours by Route ---
    if "Total Hours" in df_all.columns:
        fig4 = px.bar(
            df_all.groupby(["Entered_Month", "RouteName"])["Total Hours"].sum().reset_index(),
            x="Entered_Month",
            y="Total Hours",
            color="RouteName",
            barmode="group",
            title="Monthly Total Hours by Route"
        )
        st.plotly_chart(fig4, use_container_width=True)

    # --- Visualization 5: Efficiency (Miles per Hour) by Route ---
    if "Total Miles" in df_all.columns and "Total Hours" in df_all.columns:
        grouped = df_all.groupby(["Entered_Month", "RouteName"])[["Total Miles", "Total Hours"]].sum().reset_index()
        grouped["Miles per Hour"] = grouped.apply(
            lambda row: row["Total Miles"] / row["Total Hours"] if row["Total Hours"] > 0 else 0,
            axis=1
        )
        fig5 = px.line(
            grouped,
            x="Entered_Month",
            y="Miles per Hour",
            color="RouteName",
            title="Efficiency: Miles per Hour by Route",
            markers=True
        )
        st.plotly_chart(fig5, use_container_width=True)

    st.success("✅ Dashboard updated!")

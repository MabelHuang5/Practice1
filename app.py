import streamlit as st
import pandas as pd
import plotly.express as px

# Title
st.title("🚌 CityBus Dashboard - Route Trends")
st.markdown("Upload monthly city bus data and visualize route performance over time.")

# Session state for data
if "all_data" not in st.session_state:
    st.session_state["all_data"] = pd.DataFrame()

# Sidebar: File upload
st.sidebar.header("📁 Upload Monthly Data")
uploaded_files = st.sidebar.file_uploader("Upload CSV(s)", type=["csv"], accept_multiple_files=True)
month_input = st.sidebar.text_input("Enter Month (e.g., February 2023)")

# Helper to clean and prepare CSVs
def process_file(file, entered_month):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    # Clean numeric fields
    for col in ["Passengers", "Revenue", "Total Miles", "Total Hours"]:
        if col in df.columns:
            df[col] = df[col].replace({',': ''}, regex=True)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Entered_Month"] = entered_month
    return df

# Add data
if st.sidebar.button("Add Data"):
    if uploaded_files and month_input:
        for file in uploaded_files:
            new_df = process_file(file, month_input)
            st.session_state["all_data"] = pd.concat([st.session_state["all_data"], new_df], ignore_index=True)
        st.sidebar.success("✅ Data added!")
    else:
        st.sidebar.warning("⚠️ Upload a file and enter a month.")

# Clear data
if st.sidebar.button("Clear All Data"):
    st.session_state["all_data"] = pd.DataFrame()
    st.sidebar.success("🗑️ Data cleared.")

df_all = st.session_state["all_data"]

if df_all.empty:
    st.info("No data yet. Upload a file to begin.")
else:
    st.subheader("📊 Data Preview")
    st.write(df_all.head())

    # --- Visualization 1: Total Passengers per Route (Scatter) ---
    fig1 = px.scatter(
        df_all.groupby("Route")["Passengers"].sum().reset_index(),
        x="Route",
        y="Passengers",
        title="Total Passengers per Route",
        labels={"Passengers": "Total Passengers", "Route": "Route #"},
        size="Passengers",
        color="Route"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- Visualization 2: Total Revenue per Route (Scatter) ---
    fig2 = px.scatter(
        df_all.groupby("Route")["Revenue"].sum().reset_index(),
        x="Route",
        y="Revenue",
        title="Total Revenue per Route",
        labels={"Revenue": "Total Revenue ($)", "Route": "Route #"},
        size="Revenue",
        color="Route"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # --- Visualization 3: Monthly Total Miles by Route (Line) ---
    if "Total Miles" in df_all.columns:
        miles_df = df_all.groupby(["Entered_Month", "Route"])["Total Miles"].sum().reset_index()
        fig3 = px.line(
            miles_df,
            x="Entered_Month",
            y="Total Miles",
            color="Route",
            title="Monthly Total Miles by Route",
            markers=True
        )
        st.plotly_chart(fig3, use_container_width=True)

    # --- Visualization 4: Monthly Total Hours by Route (Line) ---
    if "Total Hours" in df_all.columns:
        hours_df = df_all.groupby(["Entered_Month", "Route"])["Total Hours"].sum().reset_index()
        fig4 = px.line(
            hours_df,
            x="Entered_Month",
            y="Total Hours",
            color="Route",
            title="Monthly Total Hours by Route",
            markers=True
        )
        st.plotly_chart(fig4, use_container_width=True)

    # --- Visualization 5: Efficiency - Miles per Hour by Route (Line) ---
    if "Total Miles" in df_all.columns and "Total Hours" in df_all.columns:
        eff_df = df_all.groupby(["Entered_Month", "Route"])[["Total Miles", "Total Hours"]].sum().reset_index()
        eff_df["Miles per Hour"] = eff_df.apply(
            lambda row: row["Total Miles"] / row["Total Hours"] if row["Total Hours"] > 0 else 0,
            axis=1
        )
        fig5 = px.line(
            eff_df,
            x="Entered_Month",
            y="Miles per Hour",
            color="Route",
            title="Efficiency: Miles per Hour by Route",
            markers=True
        )
        st.plotly_chart(fig5, use_container_width=True)

    st.success("✅ Dashboard updated with route-based trend analysis!")


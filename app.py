import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

# =============================================================================
# Session State: Initialize an empty DataFrame to store aggregated monthly data
# =============================================================================
if "all_data" not in st.session_state:
    st.session_state["all_data"] = pd.DataFrame()

# =============================================================================
# Helper Function: Process an Uploaded CSV File
# - Reads CSV, cleans key numeric columns and appends a column for the entered month.
# =============================================================================
def process_uploaded_file(uploaded_file, month_input):
    # Read CSV into a DataFrame
    df = pd.read_csv(uploaded_file)
    # Clean column names (remove accidental spaces)
    df.columns = df.columns.str.strip()
    
    # List of columns to clean (customize if needed)
    numeric_cols = ["Passengers", "Revenue", "Total Miles", "Total Hours"]
    for col in numeric_cols:
        if col in df.columns:
            # Remove commas and replace ambiguous strings with NaN
            df[col] = df[col].replace(',', '', regex=True)
            df[col] = df[col].replace(['-', ' - ', ' '], pd.NA)
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Add a column to indicate which month the data represents (user-input)
    df["Entered_Month"] = month_input
    return df

# =============================================================================
# Sidebar: File Upload and Data Management Panel
# =============================================================================
st.sidebar.header("Upload Monthly CityBus Data")

# Allow for multiple file uploads
uploaded_files = st.sidebar.file_uploader("Upload one or more CSV files", type=["csv"], accept_multiple_files=True)
month_input = st.sidebar.text_input("Enter Month (e.g., January 2023)")

# Button to process and add the uploaded data to session state
if st.sidebar.button("Add Data"):
    if uploaded_files and month_input:
        for file in uploaded_files:
            df_new = process_uploaded_file(file, month_input)
            # Append new data to our aggregated session state DataFrame
            st.session_state["all_data"] = pd.concat([st.session_state["all_data"], df_new], ignore_index=True)
        st.sidebar.success("Data added successfully!")
    else:
        st.sidebar.warning("Please upload at least one CSV file and enter the corresponding month.")

# Option to clear all data from session state
if st.sidebar.button("Clear All Data"):
    st.session_state["all_data"] = pd.DataFrame()
    st.sidebar.success("All data cleared!")

# =============================================================================
# Main Dashboard Layout
# =============================================================================
st.title("CityBus Dashboard")
st.markdown("Upload monthly datasets to generate dynamic visual reports.")

if st.session_state["all_data"].empty:
    st.info("No data available. Please upload your monthly CSV files from the sidebar.")
else:
    # Use the aggregated DataFrame
    df_all = st.session_state["all_data"].copy()

    # Drop rows that are missing critical information
    df_all = df_all.dropna(subset=["RouteName", "Passengers", "Revenue"])
    
    st.subheader("Aggregated Data Preview")
    st.write(df_all.head())

    # ----------------------------------------------------------
    # Visualization 1: Total Passengers per Route (Bar Chart)
    # ----------------------------------------------------------
    passengers_by_route = df_all.groupby("RouteName")["Passengers"].sum().reset_index()
    fig1 = px.bar(passengers_by_route, 
                  x="Passengers", 
                  y="RouteName", 
                  orientation="h",
                  title="Total Passengers per Route",
                  labels={"Passengers": "Number of Passengers", "RouteName": "Route"})
    st.plotly_chart(fig1, use_container_width=True)

    # ----------------------------------------------------------
    # Visualization 2: Total Revenue per Route (Bar Chart)
    # ----------------------------------------------------------
    revenue_by_route = df_all.groupby("RouteName")["Revenue"].sum().reset_index()
    fig2 = px.bar(revenue_by_route, 
                  x="Revenue", 
                  y="RouteName", 
                  orientation="h", 
                  title="Total Revenue per Route",
                  labels={"Revenue": "Revenue ($)", "RouteName": "Route"},
                  color="Revenue",
                  color_continuous_scale="Viridis")
    st.plotly_chart(fig2, use_container_width=True)

    # ----------------------------------------------------------
    # Visualization 3: Efficiency – Passengers per Mile
    # (Requires "Total Miles" to be present)
    # ----------------------------------------------------------
    if "Total Miles" in df_all.columns:
        # Calculate passengers per mile (ensure division safety)
        efficiency_mile = df_all.groupby("RouteName").apply(
            lambda x: x["Passengers"].sum() / x["Total Miles"].sum() if x["Total Miles"].sum() > 0 else 0
        ).reset_index(name="Passengers per Mile")
        fig3 = px.bar(efficiency_mile,
                      x="Passengers per Mile",
                      y="RouteName",
                      orientation="h",
                      title="Efficiency: Passengers per Mile",
                      labels={"Passengers per Mile": "Passengers per Mile", "RouteName": "Route"})
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("Column 'Total Miles' not available for Passengers per Mile calculation.")

    # ----------------------------------------------------------
    # Visualization 4: Efficiency – Passengers per Hour
    # (Requires "Total Hours" to be present)
    # ----------------------------------------------------------
    if "Total Hours" in df_all.columns:
        efficiency_hour = df_all.groupby("RouteName").apply(
            lambda x: x["Passengers"].sum() / x["Total Hours"].sum() if x["Total Hours"].sum() > 0 else 0
        ).reset_index(name="Passengers per Hour")
        fig4 = px.bar(efficiency_hour,
                      x="Passengers per Hour",
                      y="RouteName",
                      orientation="h",
                      title="Efficiency: Passengers per Hour",
                      labels={"Passengers per Hour": "Passengers per Hour", "RouteName": "Route"})
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("Column 'Total Hours' not available for Passengers per Hour calculation.")

    # ----------------------------------------------------------
    # Visualization 5: Monthly Passenger Trend (Line Chart)
    # ----------------------------------------------------------
    if "Entered_Month" in df_all.columns:
        # Aggregate total passengers by the user-entered month
        monthly_trend = df_all.groupby("Entered_Month")["Passengers"].sum().reset_index()
        fig5 = px.line(monthly_trend,
                       x="Entered_Month",
                       y="Passengers",
                       title="Monthly Passenger Trend",
                       markers=True,
                       labels={"Entered_Month": "Month", "Passengers": "Total Passengers"})
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.warning("No month information available for trend analysis.")

    # ----------------------------------------------------------
    # Visualization 6: Revenue vs. Passengers (Scatter Plot)
    # ----------------------------------------------------------
    fig6 = px.scatter(df_all,
                      x="Passengers",
                      y="Revenue",
                      color="RouteName",
                      title="Revenue vs. Passengers",
                      labels={"Passengers": "Passengers", "Revenue": "Revenue ($)"})
    st.plotly_chart(fig6, use_container_width=True)

    st.success("Dashboard updated with all visualizations!")
    # ===========================================================
# EXTRA: Monthly Route Trends & Efficiency Lollipop Charts
# ===========================================================
st.markdown("---")
st.header("📊 Monthly Route Trends and Efficiency Insights")

try:
    df_all["Entered_Month"] = pd.to_datetime(df_all["Entered_Month"], format="%B %Y")
except:
    st.warning("Some 'Entered_Month' values couldn't be parsed (e.g., not in 'March 2023' format).")

df_all = df_all.sort_values("Entered_Month")
available_years = sorted(df_all["Entered_Month"].dt.year.dropna().unique())

if available_years:
    selected_year = st.selectbox("📅 Select Year to View", available_years)

    df_year = df_all[df_all["Entered_Month"].dt.year == selected_year].copy()

    route_col = None
    for col in ["Route", "RouteCode", "RouteName"]:
        if col in df_year.columns:
            route_col = col
            break

    if route_col:
        df_year = df_year.sort_values(["Entered_Month", route_col])
        df_year["Monthly Miles"] = df_year.groupby(route_col)["Total Miles"].diff().fillna(df_year["Total Miles"])
        df_year["Monthly Hours"] = df_year.groupby(route_col)["Total Hours"].diff().fillna(df_year["Total Hours"])

        # Monthly Miles Line Chart
        miles_trend = df_year.groupby(["Entered_Month", route_col])["Monthly Miles"].sum().reset_index()
        fig_miles = px.line(
            miles_trend, x="Entered_Month", y="Monthly Miles", color=route_col,
            title=f"📈 Monthly Total Miles by Route ({selected_year})", markers=True
        )
        fig_miles.update_layout(xaxis=dict(type="date"))
        st.plotly_chart(fig_miles, use_container_width=True)

        # Monthly Hours Line Chart
        hours_trend = df_year.groupby(["Entered_Month", route_col])["Monthly Hours"].sum().reset_index()
        fig_hours = px.line(
            hours_trend, x="Entered_Month", y="Monthly Hours", color=route_col,
            title=f"📉 Monthly Total Hours by Route ({selected_year})", markers=True
        )
        fig_hours.update_layout(xaxis=dict(type="date"))
        st.plotly_chart(fig_hours, use_container_width=True)

        # Route Efficiency Lollipop Charts
        st.subheader(f"Route Efficiency (Miles per Hour) - {selected_year}")
        efficiency_df = df_year.groupby(route_col).agg({
            "Monthly Miles": "sum",
            "Monthly Hours": "sum"
        }).reset_index()

        efficiency_df = efficiency_df[
            (efficiency_df["Monthly Hours"] > 0) &
            (efficiency_df["Monthly Miles"] > 0)
        ]
        efficiency_df["Efficiency"] = efficiency_df["Monthly Miles"] / efficiency_df["Monthly Hours"]
        efficiency_df = efficiency_df.replace([float("inf"), -float("inf")], pd.NA).dropna(subset=["Efficiency"])

        top5_eff = efficiency_df.sort_values(by="Efficiency", ascending=False).head(5)
        bottom5_eff = efficiency_df.sort_values(by="Efficiency", ascending=True).head(5)

        fig_top = go.Figure()
        for _, row in top5_eff.iterrows():
            fig_top.add_trace(go.Scatter(
                x=[0, row["Efficiency"]],
                y=[row[route_col]] * 2,
                mode="lines+markers",
                marker=dict(size=[0, 12], color="green"),
                line=dict(color="lightgray", width=2),
                showlegend=False
            ))
        fig_top.update_layout(
            title="🏎 Top 5 Most Efficient Routes (Lollipop)",
            xaxis_title="Efficiency (Miles per Hour)",
            yaxis_title="Route",
            yaxis=dict(categoryorder="total ascending"),
            height=400
        )
        st.plotly_chart(fig_top, use_container_width=True)

        fig_bottom = go.Figure()
        for _, row in bottom5_eff.iterrows():
            fig_bottom.add_trace(go.Scatter(
                x=[0, row["Efficiency"]],
                y=[row[route_col]] * 2,
                mode="lines+markers",
                marker=dict(size=[0, 12], color="red"),
                line=dict(color="lightgray", width=2),
                showlegend=False
            ))
        fig_bottom.update_layout(
            title="🐢 Bottom 5 Least Efficient Routes (Lollipop)",
            xaxis_title="Efficiency (Miles per Hour)",
            yaxis_title="Route",
            yaxis=dict(categoryorder="total ascending"),
            height=400
        )
        st.plotly_chart(fig_bottom, use_container_width=True)

        st.success(f"Extra insights shown for {selected_year}")
    else:
        st.warning("No valid route column found (Route, RouteName, or RouteCode).")

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =============================================================================
# Session State: Initialize an empty DataFrame to store aggregated monthly data
# =============================================================================
if "all_data" not in st.session_state:
    st.session_state["all_data"] = pd.DataFrame()

# =============================================================================
# Helper Function: Process an Uploaded CSV File
# =============================================================================
def process_uploaded_file(uploaded_file, month_input):
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    numeric_cols = ["Passengers", "Revenue", "Total Miles", "Total Hours"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].replace(',', '', regex=True)
            df[col] = df[col].replace(['-', ' - ', ' '], pd.NA)
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Entered_Month"] = month_input
    return df

# =============================================================================
# Sidebar: File Upload and Data Management Panel
# =============================================================================
st.sidebar.header("Upload Monthly CityBus Data")
uploaded_files = st.sidebar.file_uploader("Upload one or more CSV files", type=["csv"], accept_multiple_files=True)
month_input = st.sidebar.text_input("Enter Month (e.g., January 2023)")

if st.sidebar.button("Add Data"):
    if uploaded_files and month_input:
        for file in uploaded_files:
            df_new = process_uploaded_file(file, month_input)
            st.session_state["all_data"] = pd.concat([st.session_state["all_data"], df_new], ignore_index=True)
        st.sidebar.success("Data added successfully!")
    else:
        st.sidebar.warning("Please upload at least one CSV file and enter the corresponding month.")

if st.sidebar.button("Clear All Data"):
    st.session_state["all_data"] = pd.DataFrame()
    st.sidebar.success("All data cleared!")

# =============================================================================
# Main Dashboard Layout
# =============================================================================
st.title("\U0001F68C CityBus Dashboard - Yearly & Monthly Route Trends")
st.markdown("Upload monthly datasets to generate dynamic visual reports.")

df_all = st.session_state["all_data"]

if df_all.empty:
    st.info("No data available. Please upload your monthly CSV files from the sidebar.")
else:
    try:
        df_all["Entered_Month"] = pd.to_datetime(df_all["Entered_Month"], format="%B %Y")
    except:
        st.warning("Check date format (e.g., 'March 2023')")

    df_all = df_all.sort_values("Entered_Month")

    available_years = sorted(df_all["Entered_Month"].dt.year.dropna().unique())
    selected_year = st.sidebar.selectbox("\ud83d\uddd5 Select Year to View", available_years)

    df_year = df_all[df_all["Entered_Month"].dt.year == selected_year].copy()

    route_col = None
    for col in ["Route", "RouteCode", "RouteName"]:
        if col in df_year.columns:
            route_col = col
            break

    st.subheader(f"\ud83d\udccb Preview: {selected_year}")
    st.write(df_year[["Entered_Month", route_col, "Total Miles", "Total Hours"]].head())

    if not route_col:
        st.error("No route column found ('Route', 'RouteCode', or 'RouteName').")
    else:
        df_year = df_year.sort_values(["Entered_Month", route_col])
        df_year["Monthly Miles"] = df_year.groupby(route_col)["Total Miles"].diff().fillna(df_year["Total Miles"])
        df_year["Monthly Hours"] = df_year.groupby(route_col)["Total Hours"].diff().fillna(df_year["Total Hours"])

        miles_trend = df_year.groupby(["Entered_Month", route_col])["Monthly Miles"].sum().reset_index()
        fig1 = px.line(miles_trend, x="Entered_Month", y="Monthly Miles", color=route_col, title=f"\ud83d\udcc8 Monthly Total Miles by Route ({selected_year})", markers=True)
        fig1.update_layout(xaxis=dict(type="date"))
        st.plotly_chart(fig1, use_container_width=True)

        hours_trend = df_year.groupby(["Entered_Month", route_col])["Monthly Hours"].sum().reset_index()
        fig2 = px.line(hours_trend, x="Entered_Month", y="Monthly Hours", color=route_col, title=f"\ud83d\udcc9 Monthly Total Hours by Route ({selected_year})", markers=True)
        fig2.update_layout(xaxis=dict(type="date"))
        st.plotly_chart(fig2, use_container_width=True)

        efficiency_df = df_year.groupby(route_col).agg({"Monthly Miles": "sum", "Monthly Hours": "sum"}).reset_index()
        efficiency_df = efficiency_df[(efficiency_df["Monthly Hours"] > 0) & (efficiency_df["Monthly Miles"] > 0)]
        efficiency_df["Efficiency"] = efficiency_df["Monthly Miles"] / efficiency_df["Monthly Hours"]
        efficiency_df = efficiency_df.replace([float("inf"), -float("inf")], pd.NA).dropna(subset=["Efficiency"])

        st.write(" Cleaned Efficiency Data (Top 10):")
        st.dataframe(efficiency_df.sort_values(by="Efficiency", ascending=False).head(10))

        top5_eff = efficiency_df.sort_values(by="Efficiency", ascending=False).head(5)
        bottom5_eff = efficiency_df.sort_values(by="Efficiency", ascending=True).head(5)

        fig_top = go.Figure()
        for _, row in top5_eff.iterrows():
            fig_top.add_trace(go.Scatter(x=[0, row["Efficiency"]], y=[row[route_col]] * 2, mode="lines+markers", marker=dict(size=[0, 12], color="green"), line=dict(color="lightgray", width=2), showlegend=False))
        fig_top.update_layout(title="\ud83c\udfce Top 5 Most Efficient Routes (Lollipop)", xaxis_title="Efficiency (Miles per Hour)", yaxis_title="Route", yaxis=dict(categoryorder="total ascending"), height=400)
        st.plotly_chart(fig_top, use_container_width=True)

        fig_bottom = go.Figure()
        for _, row in bottom5_eff.iterrows():
            fig_bottom.add_trace(go.Scatter(x=[0, row["Efficiency"]], y=[row[route_col]] * 2, mode="lines+markers", marker=dict(size=[0, 12], color="red"), line=dict(color="lightgray", width=2), showlegend=False))
        fig_bottom.update_layout(title="\ud83d\udc22 Bottom 5 Least Efficient Routes (Lollipop)", xaxis_title="Efficiency (Miles per Hour)", yaxis_title="Route", yaxis=dict(categoryorder="total ascending"), height=400)
        st.plotly_chart(fig_bottom, use_container_width=True)

        st.success(f"Showing monthly trends and efficiency charts for {selected_year}")

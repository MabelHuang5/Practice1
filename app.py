import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =============================================================================
# Session State: Initialize
# =============================================================================
if "all_data" not in st.session_state:
    st.session_state["all_data"] = pd.DataFrame()

# =============================================================================
# Helper: Upload & Clean
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
# Sidebar Upload Panel
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
        st.sidebar.warning("Please upload at least one CSV and enter month.")

if st.sidebar.button("Clear All Data"):
    st.session_state["all_data"] = pd.DataFrame()
    st.sidebar.success("All data cleared!")

# =============================================================================
# Main Dashboard
# =============================================================================
st.title("🚌 CityBus Dashboard")
st.markdown("Upload monthly datasets to generate dynamic visual reports.")

df_all = st.session_state["all_data"]

if df_all.empty:
    st.info("No data available. Please upload your monthly CSV files.")
else:
    df_all = df_all.copy()
    df_all = df_all.dropna(subset=["RouteName", "Passengers", "Revenue"])

    # ------------------ Basic Visualizations ------------------
    st.subheader("Aggregated Data Preview")
    st.dataframe(df_all.head())

    passengers_by_route = df_all.groupby("RouteName")["Passengers"].sum().reset_index()
    fig1 = px.bar(passengers_by_route, x="Passengers", y="RouteName", orientation="h",
                  title="Total Passengers per Route")
    st.plotly_chart(fig1, use_container_width=True)

    revenue_by_route = df_all.groupby("RouteName")["Revenue"].sum().reset_index()
    fig2 = px.bar(revenue_by_route, x="Revenue", y="RouteName", orientation="h",
                  title="Total Revenue per Route", color="Revenue", color_continuous_scale="Viridis")
    st.plotly_chart(fig2, use_container_width=True)

    if "Total Miles" in df_all.columns:
        efficiency_mile = df_all.groupby("RouteName").apply(
            lambda x: x["Passengers"].sum() / x["Total Miles"].sum() if x["Total Miles"].sum() > 0 else 0
        ).reset_index(name="Passengers per Mile")
        fig3 = px.bar(efficiency_mile, x="Passengers per Mile", y="RouteName", orientation="h",
                      title="Efficiency: Passengers per Mile")
        st.plotly_chart(fig3, use_container_width=True)

    if "Total Hours" in df_all.columns:
        efficiency_hour = df_all.groupby("RouteName").apply(
            lambda x: x["Passengers"].sum() / x["Total Hours"].sum() if x["Total Hours"].sum() > 0 else 0
        ).reset_index(name="Passengers per Hour")
        fig4 = px.bar(efficiency_hour, x="Passengers per Hour", y="RouteName", orientation="h",
                      title="Efficiency: Passengers per Hour")
        st.plotly_chart(fig4, use_container_width=True)

    if "Entered_Month" in df_all.columns:
        try:
            df_all["Entered_Month"] = pd.to_datetime(df_all["Entered_Month"], format="%B %Y")
        except:
            st.warning("Month format error. Please use 'March 2023' format.")
        monthly_trend = df_all.groupby("Entered_Month")["Passengers"].sum().reset_index()
        fig5 = px.line(monthly_trend, x="Entered_Month", y="Passengers",
                       title="Monthly Passenger Trend", markers=True)
        st.plotly_chart(fig5, use_container_width=True)

    fig6 = px.scatter(df_all, x="Passengers", y="Revenue", color="RouteName",
                      title="Revenue vs. Passengers")
    st.plotly_chart(fig6, use_container_width=True)

    st.success("Dashboard updated with all visualizations!")

    # ------------------ Advanced: Route Trends & Lollipops ------------------
    st.markdown("---")
    st.header("📊 Monthly Route Trends and Efficiency Insights")

    # Convert & sort month
    try:
        df_all["Entered_Month"] = pd.to_datetime(df_all["Entered_Month"], format="%B %Y")
    except:
        pass
    df_all = df_all.sort_values("Entered_Month")
    available_years = sorted(df_all["Entered_Month"].dt.year.dropna().unique())

    if available_years:
        selected_year = st.selectbox("📅 Select Year to View", available_years)
        df_year = df_all[df_all["Entered_Month"].dt.year == selected_year].copy()

        if not df_year.empty:
            df_year = df_year.sort_values(["Entered_Month", "RouteName"])
            df_year["Monthly Miles"] = df_year.groupby("RouteName")["Total Miles"].diff().fillna(df_year["Total Miles"])
            df_year["Monthly Hours"] = df_year.groupby("RouteName")["Total Hours"].diff().fillna(df_year["Total Hours"])

            # Line chart - Monthly Miles
            miles_trend = df_year.groupby(["Entered_Month", "RouteName"])["Monthly Miles"].sum().reset_index()
            fig7 = px.line(miles_trend, x="Entered_Month", y="Monthly Miles", color="RouteName",
                           title=f"📈 Monthly Miles by Route ({selected_year})", markers=True)
            st.plotly_chart(fig7, use_container_width=True)

            # Line chart - Monthly Hours
            hours_trend = df_year.groupby(["Entered_Month", "RouteName"])["Monthly Hours"].sum().reset_index()
            fig8 = px.line(hours_trend, x="Entered_Month", y="Monthly Hours", color="RouteName",
                           title=f"📉 Monthly Hours by Route ({selected_year})", markers=True)
            st.plotly_chart(fig8, use_container_width=True)

            # Efficiency Lollipops
            st.subheader(f"Route Efficiency (Miles per Hour) - {selected_year}")
            eff_df = df_year.groupby("RouteName").agg({"Monthly Miles": "sum", "Monthly Hours": "sum"}).reset_index()
            eff_df = eff_df[(eff_df["Monthly Hours"] > 0) & (eff_df["Monthly Miles"] > 0)]
            eff_df["Efficiency"] = eff_df["Monthly Miles"] / eff_df["Monthly Hours"]

            top5 = eff_df.sort_values("Efficiency", ascending=False).head(5)
            bottom5 = eff_df.sort_values("Efficiency", ascending=True).head(5)

            def create_lollipop(data, title, color):
                fig = go.Figure()
                for _, row in data.iterrows():
                    fig.add_trace(go.Scatter(
                        x=[0, row["Efficiency"]],
                        y=[row["RouteName"]] * 2,
                        mode="lines+markers",
                        marker=dict(size=[0, 12], color=color),
                        line=dict(color="lightgray", width=2),
                        showlegend=False
                    ))
                fig.update_layout(
                    title=title,
                    xaxis_title="Efficiency (Miles per Hour)",
                    yaxis_title="Route",
                    yaxis=dict(categoryorder="total ascending"),
                    height=400
                )
                return fig

            st.plotly_chart(create_lollipop(top5, "🏎 Top 5 Efficient Routes", "green"), use_container_width=True)
            st.plotly_chart(create_lollipop(bottom5, "🐢 Bottom 5 Efficient Routes", "red"), use_container_width=True)

            st.success("Advanced charts displayed.")

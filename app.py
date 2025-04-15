import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("\U0001F68C CityBus Dashboard - Yearly & Monthly Route Trends")
st.markdown("Upload monthly data and select a year to view monthly trends by route.")

# Initialize session state
if "all_data" not in st.session_state:
    st.session_state["all_data"] = pd.DataFrame()

# Sidebar - Upload
st.sidebar.header("📁 Upload Monthly CSV Data")
uploaded_files = st.sidebar.file_uploader("Upload one or more CSV files", type=["csv"], accept_multiple_files=True)
month_input = st.sidebar.text_input("Enter Month (e.g., February 2023)")

# Clean and process uploaded files
def process_file(file, entered_month):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    for col in ["Total Miles", "Total Hours"]:
        if col in df.columns:
            df[col] = df[col].replace({',': ''}, regex=True)
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Entered_Month"] = entered_month
    return df

# Add Data
if st.sidebar.button("Add Data"):
    if uploaded_files and month_input:
        for file in uploaded_files:
            new_df = process_file(file, month_input)
            st.session_state["all_data"] = pd.concat([st.session_state["all_data"], new_df], ignore_index=True)
        st.sidebar.success("✅ Data added!")
    else:
        st.sidebar.warning("⚠️ Upload files and enter month first.")

# Clear Data
if st.sidebar.button("Clear All Data"):
    st.session_state["all_data"] = pd.DataFrame()
    st.sidebar.success("🗑️ All data cleared.")

# Use the data
df_all = st.session_state["all_data"]

if df_all.empty:
    st.info("📭 Please upload data to begin.")
else:
    try:
        df_all["Entered_Month"] = pd.to_datetime(df_all["Entered_Month"], format="%B %Y")
    except:
        st.warning("⚠️ Check date format (e.g., 'March 2023')")

    df_all = df_all.sort_values("Entered_Month")

    available_years = sorted(df_all["Entered_Month"].dt.year.dropna().unique())
    selected_year = st.sidebar.selectbox("📅 Select Year to View", available_years)

    df_year = df_all[df_all["Entered_Month"].dt.year == selected_year].copy()

    route_col = None
    for col in ["Route", "RouteCode", "RouteName"]:
        if col in df_year.columns:
            route_col = col
            break

    st.subheader(f"📋 Preview: {selected_year}")
    st.write(df_year[["Entered_Month", route_col, "Total Miles", "Total Hours"]].head())

    if not route_col:
        st.error("⚠️ No route column found ('Route', 'RouteCode', or 'RouteName').")
    else:
        df_year = df_year.sort_values(["Entered_Month", route_col])

        # De-cumulate to monthly values
        df_year["Monthly Miles"] = df_year.groupby(route_col)["Total Miles"].diff().fillna(df_year["Total Miles"])
        df_year["Monthly Hours"] = df_year.groupby(route_col)["Total Hours"].diff().fillna(df_year["Total Hours"])

        # --- Line Chart: Monthly Miles ---
        miles_trend = df_year.groupby(["Entered_Month", route_col])["Monthly Miles"].sum().reset_index()
        fig1 = px.line(
            miles_trend, x="Entered_Month", y="Monthly Miles", color=route_col,
            title=f"📈 Monthly Total Miles by Route ({selected_year})", markers=True
        )
        fig1.update_layout(xaxis=dict(type="date"))
        st.plotly_chart(fig1, use_container_width=True)

        # --- Line Chart: Monthly Hours ---
        hours_trend = df_year.groupby(["Entered_Month", route_col])["Monthly Hours"].sum().reset_index()
        fig2 = px.line(
            hours_trend, x="Entered_Month", y="Monthly Hours", color=route_col,
            title=f"📉 Monthly Total Hours by Route ({selected_year})", markers=True
        )
        fig2.update_layout(xaxis=dict(type="date"))
        st.plotly_chart(fig2, use_container_width=True)

        # --- ✨ Efficiency Lollipop Chart ---
        st.subheader(f"⚙️ Route Efficiency (Miles per Hour) - {selected_year}")

        efficiency_df = df_year.groupby(route_col).agg({
            "Monthly Miles": "sum",
            "Monthly Hours": "sum"
        }).reset_index()

        efficiency_df["Efficiency"] = efficiency_df["Monthly Miles"] / efficiency_df["Monthly Hours"]
        efficiency_df = efficiency_df.replace([float("inf"), -float("inf")], pd.NA).dropna(subset=["Efficiency"])

        top5_eff = efficiency_df.sort_values(by="Efficiency", ascending=False).head(5)
        bottom5_eff = efficiency_df.sort_values(by="Efficiency", ascending=True).head(5)

        # Lollipop Top
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
            title="🏎️ Top 5 Most Efficient Routes (Lollipop)",
            xaxis_title="Efficiency (Miles per Hour)",
            yaxis_title="Route",
            yaxis=dict(categoryorder="total ascending"),
            height=400
        )
        st.plotly_chart(fig_top, use_container_width=True)

        # Lollipop Bottom
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

        st.success(f"✅ Showing monthly trends and efficiency charts for {selected_year}")

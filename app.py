import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🚌 CityBus Dashboard - Miles & Hours Tracker")
st.markdown("Upload monthly data to explore route performance in terms of distance and duration.")

# Initialize session state
if "all_data" not in st.session_state:
    st.session_state["all_data"] = pd.DataFrame()

# Sidebar
st.sidebar.header("📁 Upload Monthly CSV Data")
uploaded_files = st.sidebar.file_uploader("Upload one or more CSV files", type=["csv"], accept_multiple_files=True)
month_input = st.sidebar.text_input("Enter Month (e.g., February 2023)")

# Helper function to clean & process uploaded files
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
        st.sidebar.success("✅ Data added successfully!")
    else:
        st.sidebar.warning("⚠️ Please upload file(s) and enter a month.")

# Clear Data
if st.sidebar.button("Clear All Data"):
    st.session_state["all_data"] = pd.DataFrame()
    st.sidebar.success("🗑️ All data cleared.")

# Use current data
df_all = st.session_state["all_data"]

if df_all.empty:
    st.info("No data yet. Please upload CSVs using the sidebar.")
else:
    # 🔧 Fix month order
    try:
        df_all["Entered_Month"] = pd.to_datetime(df_all["Entered_Month"], format="%B %Y")
    except:
        st.warning("⚠️ Could not parse 'Entered_Month'. Use format like 'February 2023'.")

    # Sort by month for all charts
    df_all = df_all.sort_values("Entered_Month")

    # Show preview
    st.subheader("📋 Data Preview")
    st.write(df_all[["Entered_Month"] + [col for col in ["Route", "RouteCode", "RouteName"] if col in df_all.columns] + ["Total Miles", "Total Hours"]].head())

    # Detect the best available route column
    route_col = None
    for col in ["Route", "RouteCode", "RouteName"]:
        if col in df_all.columns:
            route_col = col
            break

    if not route_col:
        st.error("⚠️ No 'Route', 'RouteCode', or 'RouteName' column found.")
    else:
        # --- Visualization 1: Monthly Total Miles ---
        fig1 = px.line(
            df_all.groupby(["Entered_Month", route_col])["Total Miles"].sum().reset_index(),
            x="Entered_Month",
            y="Total Miles",
            color=route_col,
            title="📈 Monthly Total Miles by Route",
            markers=True
        )
        st.plotly_chart(fig1, use_container_width=True)

        # --- Visualization 2: Monthly Total Hours ---
        fig2 = px.line(
            df_all.groupby(["Entered_Month", route_col])["Total Hours"].sum().reset_index(),
            x="Entered_Month",
            y="Total Hours",
            color=route_col,
            title="📉 Monthly Total Hours by Route",
            markers=True
        )
        st.plotly_chart(fig2, use_container_width=True)

        # --- Top & Bottom 5 Total Miles ---
        st.subheader("🏆 Top 5 and Bottom 5 Routes by Total Miles")
        miles_sum = df_all.groupby(route_col)["Total Miles"].sum().reset_index().sort_values(by="Total Miles", ascending=False)
        top5_miles = miles_sum.head(5)
        bottom5_miles = miles_sum.tail(5)

        fig3 = px.bar(top5_miles, x="Total Miles", y=route_col, orientation="h", title="Top 5 Routes by Total Miles")
        fig4 = px.bar(bottom5_miles, x="Total Miles", y=route_col, orientation="h", title="Bottom 5 Routes by Total Miles")

        st.plotly_chart(fig3, use_container_width=True)
        st.plotly_chart(fig4, use_container_width=True)

        # --- Top & Bottom 5 Total Hours ---
        st.subheader("⏱️ Top 5 and Bottom 5 Routes by Total Hours")
        hours_sum = df_all.groupby(route_col)["Total Hours"].sum().reset_index().sort_values(by="Total Hours", ascending=False)
        top5_hours = hours_sum.head(5)
        bottom5_hours = hours_sum.tail(5)

        fig5 = px.bar(top5_hours, x="Total Hours", y=route_col, orientation="h", title="Top 5 Routes by Total Hours")
        fig6 = px.bar(bottom5_hours, x="Total Hours", y=route_col, orientation="h", title="Bottom 5 Routes by Total Hours")

        st.plotly_chart(fig5, use_container_width=True)
        st.plotly_chart(fig6, use_container_width=True)

        st.success("✅ Dashboard loaded with time-sorted trends.")



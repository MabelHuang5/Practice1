import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🚌 CityBus Dashboard - Route Mileage & Hours")
st.markdown("Upload monthly data and view total miles and total hours by route.")

# Store uploaded data
if "all_data" not in st.session_state:
    st.session_state["all_data"] = pd.DataFrame()

# Sidebar: Upload
st.sidebar.header("📁 Upload Monthly Data")
uploaded_files = st.sidebar.file_uploader("Upload CSV(s)", type=["csv"], accept_multiple_files=True)
month_input = st.sidebar.text_input("Enter Month (e.g., February 2023)")

# Helper to process uploaded files
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
        st.sidebar.warning("⚠️ Upload a file and enter a month.")

# Clear Data
if st.sidebar.button("Clear All Data"):
    st.session_state["all_data"] = pd.DataFrame()
    st.sidebar.success("🗑️ Data cleared.")

# Main dashboard logic
df_all = st.session_state["all_data"]

if df_all.empty:
    st.info("Please upload data to view charts.")
else:
    st.subheader("📋 Data Preview")
    st.write(df_all[["Entered_Month", "Route", "Total Miles", "Total Hours"]].head())

    # --- Visualization: Total Miles by Month and Route ---
    fig1 = px.line(
        df_all.groupby(["Entered_Month", "Route"])["Total Miles"].sum().reset_index(),
        x="Entered_Month",
        y="Total Miles",
        color="Route",
        title="📈 Total Miles by Month and Route",
        markers=True
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- Visualization: Total Hours by Month and Route ---
    fig2 = px.line(
        df_all.groupby(["Entered_Month", "Route"])["Total Hours"].sum().reset_index(),
        x="Entered_Month",
        y="Total Hours",
        color="Route",
        title="📉 Total Hours by Month and Route",
        markers=True
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.success("✅ Displaying Total Miles and Hours only.")
# --- Top 5 and Bottom 5 Routes by Total Miles ---
st.subheader("🏆 Top 5 and Bottom 5 Routes by Total Miles")

miles_sum = df_all.groupby("Route")["Total Miles"].sum().reset_index().sort_values(by="Total Miles", ascending=False)
top5_miles = miles_sum.head(5)
bottom5_miles = miles_sum.tail(5)

fig3 = px.bar(top5_miles, x="Total Miles", y="Route", orientation="h", title="Top 5 Routes by Total Miles")
fig4 = px.bar(bottom5_miles, x="Total Miles", y="Route", orientation="h", title="Bottom 5 Routes by Total Miles")

st.plotly_chart(fig3, use_container_width=True)
st.plotly_chart(fig4, use_container_width=True)

# --- Top 5 and Bottom 5 Routes by Total Hours ---
st.subheader("⏱️ Top 5 and Bottom 5 Routes by Total Hours")

hours_sum = df_all.groupby("Route")["Total Hours"].sum().reset_index().sort_values(by="Total Hours", ascending=False)
top5_hours = hours_sum.head(5)
bottom5_hours = hours_sum.tail(5)

fig5 = px.bar(top5_hours, x="Total Hours", y="Route", orientation="h", title="Top 5 Routes by Total Hours")
fig6 = px.bar(bottom5_hours, x="Total Hours", y="Route", orientation="h", title="Bottom 5 Routes by Total Hours")

st.plotly_chart(fig5, use_container_width=True)
st.plotly_chart(fig6, use_container_width=True)

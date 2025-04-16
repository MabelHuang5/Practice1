import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CityBus Dashboard", layout="wide")
st.title("🚌 CityBus Dashboard - Yearly & Monthly Route Trends")
st.write("Upload monthly data and view trends automatically — no need to enter the month!")

# Upload files
uploaded_files = st.file_uploader("📂 Upload one or more CSV files", type="csv", accept_multiple_files=True)

# Collect all uploaded data
all_data = pd.DataFrame()

if uploaded_files:
    for file in uploaded_files:
        try:
            df = pd.read_csv(file)

            # Show file preview
            st.subheader(f"📄 Preview: {file.name}")
            st.dataframe(df.head())

            # Check for required column
            if 'Entered_Month' not in df.columns:
                st.warning(f"⚠️ `{file.name}` is missing 'Entered_Month' column.")
                continue

            df['Entered_Month'] = pd.to_datetime(df['Entered_Month'], errors='coerce')
            df['Year'] = df['Entered_Month'].dt.year
            df['Month'] = df['Entered_Month'].dt.month
            all_data = pd.concat([all_data, df], ignore_index=True)

        except Exception as e:
            st.error(f"❌ Error reading {file.name}: {e}")

# Continue if we have clean data
if not all_data.empty:
    valid_years = all_data['Year'].dropna().unique()
    selected_year = st.selectbox("📅 Select Year", sorted(valid_years, reverse=True))
    filtered_data = all_data[all_data['Year'] == selected_year]

    st.subheader(f"📊 Monthly Total Miles by Route ({selected_year})")

    # Make sure columns exist
    if 'Route' in filtered_data.columns and 'Total Miles' in filtered_data.columns:
        grouped = (
            filtered_data
            .dropna(subset=['Route', 'Total Miles'])
            .groupby([filtered_data['Entered_Month'].dt.to_period("M"), 'Route'])['Total Miles']
            .sum()
            .reset_index()
        )
        grouped['Entered_Month'] = grouped['Entered_Month'].astype(str)

        fig = px.line(
            grouped,
            x='Entered_Month',
            y='Total Miles',
            color='Route',
            title='Monthly Total Miles by Route'
        )
        fig.update_layout(xaxis_title="Month", yaxis_title="Total Miles")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ 'Route' or 'Total Miles' column missing in your data.")
else:
    st.info("📥 Upload CSV files to begin.")

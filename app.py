import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="CityBus Dashboard", layout="wide")
st.title("🚌 CityBus Dashboard - Yearly & Monthly Route Trends")
st.write("Upload monthly data and view trends automatically — no need to enter the month!")

# -- File upload
uploaded_files = st.file_uploader("📂 Upload one or more CSV files", type="csv", accept_multiple_files=True)

# -- Combine uploaded data
all_data = pd.DataFrame()
if uploaded_files:
    for file in uploaded_files:
        df = pd.read_csv(file)
        if 'Entered_Month' in df.columns:
            df['Entered_Month'] = pd.to_datetime(df['Entered_Month'], errors='coerce')
            df['Year'] = df['Entered_Month'].dt.year
            df['Month'] = df['Entered_Month'].dt.month
            all_data = pd.concat([all_data, df], ignore_index=True)

# -- If we have data, show preview and charts
if not all_data.empty:
    selected_year = st.selectbox("📅 Select Year", sorted(all_data['Year'].dropna().unique(), reverse=True))
    filtered_data = all_data[all_data['Year'] == selected_year]

    st.subheader(f"📋 Preview: {selected_year}")
    st.dataframe(filtered_data.head())

    # -- Group and Plot Monthly Miles by Route
    st.subheader(f"📈 Monthly Total Miles by Route ({selected_year})")
    miles_by_route = (
        filtered_data
        .dropna(subset=['Route'])
        .groupby([filtered_data['Entered_Month'].dt.to_period("M"), 'Route'])['Total Miles']
        .sum()
        .reset_index()
    )
    miles_by_route['Entered_Month'] = miles_by_route['Entered_Month'].astype(str)

    fig, ax = plt.subplots(figsize=(12, 6))
    for route in miles_by_route['Route'].unique():
        route_data = miles_by_route[miles_by_route['Route'] == route]
        ax.plot(route_data['Entered_Month'], route_data['Total Miles'], label=route)

    ax.set_title('Monthly Total Miles by Route')
    ax.set_xlabel('Month')
    ax.set_ylabel('Total Miles')
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.info("Upload CSV files to begin.")

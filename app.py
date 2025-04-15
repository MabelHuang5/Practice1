# ----------------------------------------------------------
# Visualization 7: Monthly Total Miles by Route
# ----------------------------------------------------------
if all(col in df_all.columns for col in ["Entered_Month", "RouteName", "Total Miles"]):
    df_all["Total Miles"] = df_all["Total Miles"].replace({',': ''}, regex=True).astype(float)

    miles_by_month = df_all.groupby(["Entered_Month", "RouteName"])["Total Miles"].sum().reset_index()
    fig7 = px.bar(miles_by_month,
                  x="Entered_Month",
                  y="Total Miles",
                  color="RouteName",
                  title="Monthly Total Miles by Route",
                  labels={"Entered_Month": "Month", "Total Miles": "Total Miles"},
                  barmode="group")
    st.plotly_chart(fig7, use_container_width=True)

# ----------------------------------------------------------
# Visualization 8: Monthly Total Hours by Route
# ----------------------------------------------------------
if all(col in df_all.columns for col in ["Entered_Month", "RouteName", "Total Hours"]):
    df_all["Total Hours"] = df_all["Total Hours"].replace({',': ''}, regex=True).astype(float)

    hours_by_month = df_all.groupby(["Entered_Month", "RouteName"])["Total Hours"].sum().reset_index()
    fig8 = px.bar(hours_by_month,
                  x="Entered_Month",
                  y="Total Hours",
                  color="RouteName",
                  title="Monthly Total Hours by Route",
                  labels={"Entered_Month": "Month", "Total Hours": "Total Hours"},
                  barmode="group")
    st.plotly_chart(fig8, use_container_width=True)

# ----------------------------------------------------------
# Visualization 9: Monthly Efficiency (Miles per Hour) by Route
# ----------------------------------------------------------
if all(col in df_all.columns for col in ["Entered_Month", "RouteName", "Total Miles", "Total Hours"]):
    efficiency_df = df_all.groupby(["Entered_Month", "RouteName"]).agg({
        "Total Miles": "sum",
        "Total Hours": "sum"
    }).reset_index()

    efficiency_df["Miles per Hour"] = efficiency_df.apply(
        lambda row: row["Total Miles"] / row["Total Hours"] if row["Total Hours"] > 0 else 0,
        axis=1
    )

    fig9 = px.line(efficiency_df,
                   x="Entered_Month",
                   y="Miles per Hour",
                   color="RouteName",
                   markers=True,
                   title="Monthly Efficiency: Miles per Hour by Route",
                   labels={"Entered_Month": "Month", "Miles per Hour": "Miles/Hour"})
    st.plotly_chart(fig9, use_container_width=True)

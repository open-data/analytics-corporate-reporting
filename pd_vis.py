import plotly.express as px
import pandas as pd
# PD visualization
df = pd.read_csv("structure_pd.csv", encoding="utf-8")
df.rename(columns={"ati_all": "ATI", "contracts": "Contracts", "grants": "Grants",
          "travelq": "Travel", "hospitalityq": "Hospitality"}, inplace=True)
df = df.head(8)
base_val = [("ATI", df["ATI"][7]), ("Contracts", df["Contracts"][7]), ("Grants",
                df["Grants"][7]), ("Travel", df["Travel"][7]), ("Hospitality", df["Hospitality"][7])]
for lab, val in base_val:
    df[lab] = df[lab]-val
df.drop([len(df)-1], inplace=True) # drop the last row with zero values
sel_col = ["ATI", "Contracts", "Grants", "Travel", "Hospitality"]
df_melt = pd.melt(df.head(15), id_vars=['date'], value_vars=sel_col)
df_melt.rename(columns={"variable": "pd_type",
                        "value": "count"}, inplace=True)
df_melt.sort_values(by=['date'], axis=0, ascending=False, inplace=True)
fig_pd = px.bar(df_melt, x="date", y="count", color="pd_type",
             barmode="group", text_auto='s')
fig_pd.update_traces(textfont_size=12, textangle=0,
                  textposition="outside", cliponaxis=False)

fig_pd.update_layout(
    font_family="Courier New",
    font_color="blue",
    title_font_family="Times New Roman",
    title_font_color="blue",
    title_text="New ATI, contracts, grants, travel and hospitality in last 7 days",
    title_font_size=24,
    title_x=0.5,
    legend_title_font_color="green"
)
# Open data visualization
df = pd.read_csv("corporate_report.csv", encoding="utf-8")
df.rename(columns={"number of datasets":"# of open data",}, inplace=True)
df_melt = pd.melt(df, id_vars=['Date'], value_vars=["# of open data", "Non geospatial" ])
df_melt.rename(columns={"variable": "type",
                        "value": "count"}, inplace=True)
fig_od = px.line(df_melt, x="Date", y="count", color ="type")


fig_od.update_layout(
    font_family="Courier New",
    font_color="blue",
    title_font_family="Times New Roman",
    title_font_color="blue",
    title_text="Open Data created within the current fiscal year",
    title_font_size=24,
    title_x=0.5,
    legend_title_font_color="green"
)
fig_od.write_image("opendata.svg")

fig_pd.write_image("PD_plot.svg")

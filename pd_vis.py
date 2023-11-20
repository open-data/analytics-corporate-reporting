import plotly.express as px
import pandas as pd

df = pd.read_csv("structure_pd.csv", encoding="utf-8")
df.rename(columns={"ati_all": "ATI", "contracts": "Contracts", "grants": "Grants",
          "travelq": "Travel", "hospitalityq": "Hospitality"}, inplace=True)
base_val = [("ATI", 165646), ("Contracts", 1036237), ("Grants",
                                                      949177), ("Travel", 91093), ("Hospitality", 22449)]
for lab, val in base_val:
    df[lab] = df[lab]-val
df.drop([len(df)-1], inplace=True)
sel_col = ["ATI", "Contracts", "Grants", "Travel", "Hospitality"]
df_melt = pd.melt(df.head(15), id_vars=['date'], value_vars=sel_col)
df_melt.rename(columns={"variable": "pd_type",
                        "value": "count"}, inplace=True)
df_melt.sort_values(by=['date'], axis=0, ascending=False, inplace=True)
fig = px.bar(df_melt, x="date", y="count", color="pd_type",
             barmode="group", text_auto='.2s')
fig.update_traces(textfont_size=12, textangle=0,
                  textposition="outside", cliponaxis=False)

fig.update_layout(
    font_family="Courier New",
    font_color="blue",
    title_font_family="Times New Roman",
    title_font_color="blue",
    title_text="New ATI, contracts, grants, travel and hospitality in last 15 days",
    title_font_size=24,
    title_x=0.5,
    legend_title_font_color="green"
)
fig.show()
fig.write_image("plot.svg")

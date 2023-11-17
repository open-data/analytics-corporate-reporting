import plotly.express as px
import pandas as pd


df = pd.read_csv("structure_pd.csv", encoding="utf-8")
base_val =[("ati_all",165646),("contracts",1036237),("grants",949177),("travelq",91093),("hospitalityq",22449)]
for lab,val in base_val:
    df[lab] = df[lab]-val
df.drop([len(df)-1], inplace=True) 
col_melt = ["ati_all","ati_nil","contracts","contracts_nil","contractsa","grants","grants_nil","reclassification"
             ,"reclassification_nil","travela","travelq","travelq_nil","hospitalityq","hospitalityq_nil","dac",
             "briefingt","qpnotes","wrongdoing","adminaircraft"]
sel_col =["ati_all","contracts", "grants", "travelq", "hospitalityq" ]
df_melt = pd.melt(df.head(15), id_vars=['date'], value_vars=sel_col) 
df_melt.rename(columns={"variable":"pd_type",
                        "value":"count"}, inplace=True)
df_melt.sort_values(by=['date'], axis=0, ascending=False, inplace=True)
fig=px.bar(df_melt,x="date", y="count", color ="pd_type", barmode="group",text_auto='.2s')
fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)

fig.update_layout(
    font_family="Courier New",
    font_color="blue",
    title_font_family="Times New Roman",
    title_font_color="blue", 
    title_text = "New ATI, contracts, grants, travel and hospitality in last 15 days",
    title_font_size = 24,
    title_x= 0.5,   
    legend_title_font_color="green"
)
fig.show()
fig.write_image("plot.svg", width=800, height = 500)
import plotly.express as px
import pandas as pd


df = pd.read_csv("all_pd_new.csv", encoding="utf-8")

fig=px.bar(df,x="date", y="pd_count", color ="pd_type", barmode="group")

fig.show()
fig.write_image("plot.svg")
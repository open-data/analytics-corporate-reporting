import pandas as pd
from ckanapi import RemoteCKAN

# CKAN API endpoint
ckan = RemoteCKAN('https://open.canada.ca/data')

# Resource ID from the provided URL
datasets_meta = '312a65c5-d0bc-4445-8a24-95b2690cc62b'
dls = '4ebc050f-6c3c-4dfd-817e-875b2caf3ec6'
visits = 'c14ba36b-0af5-4c59-a5fd-26ca6a1ef6db'
maps_views = '15eeafa2-c331-44e7-b37f-d0d54a51d2eb'


resource_ids = [datasets_meta, dls, visits, maps_views]
dfs = {}

for resource_id in resource_ids:
  try:
    resource = ckan.action.resource_show(id=resource_id)
    url = resource['url']
    df_name = resource['name']  # Use the resource name as the key for the dataframe
    dfs[df_name] = pd.read_csv(url)
    print(f"Successfully loaded {df_name} into a dataframe.")
  except Exception as e:
    print(f"Error loading resource {resource_id}: {e}")

# Now you have a dictionary 'dfs' containing the dataframes with resource names as keys
# e.g., dfs['Datasets Metadata'] will contain the dataframe for Datasets Metadata

#create a df 'jurisdiction_dl' that joins the jurisdiction column from dfs['datasets metadata'] on to dfs['Downloads per organization, last 12 months'] based on id, the aggregates the sum of the downloads_telechargements column by year_annee,month_mois,jurisdiction
# then sort by year_annee,month_mois,downloads_telechargements desc

jurisdiction_dl = pd.merge(dfs['Downloads per organization, last 12 months'],
                             dfs['datasets metadata'][['id', 'jurisdiction']],
                             on='id',
                             how='left')

jurisdiction_dl = jurisdiction_dl.groupby(['year_annee', 'month_mois', 'jurisdiction'])['downloads_telechargements'].sum().reset_index()

jurisdiction_dl = jurisdiction_dl.sort_values(['year_annee', 'month_mois', 'downloads_telechargements'],
                                           ascending=[False, False, False])

jurisdiction_visits = pd.merge(dfs['dataset visits per department, last 12 months'],
                             dfs['datasets metadata'][['id', 'jurisdiction']],
                             on='id',
                             how='left')

jurisdiction_visits = jurisdiction_visits.groupby(['year_annee', 'month_mois', 'jurisdiction'])['visits_visites'].sum().reset_index()

jurisdiction_visits = jurisdiction_visits.sort_values(['year_annee', 'month_mois', 'visits_visites'],
                                           ascending=[False, False, False])

jurisdiction_mapviews = pd.merge(dfs['Open Maps Views'],
                             dfs['datasets metadata'][['id', 'jurisdiction']],
                             on='id',
                             how='left')

jurisdiction_mapviews = jurisdiction_mapviews.groupby(['year', 'month', 'jurisdiction'])['pageviews'].sum().reset_index()

jurisdiction_mapviews = jurisdiction_mapviews.sort_values(['year', 'month', 'pageviews'],ascending=[False, False, False])

jurisdiction_mapviews = jurisdiction_mapviews.rename(columns={'pageviews': 'Open Maps Views'})

# Save DataFrames to individual CSV files without index
jurisdiction_dl.to_csv('JURISDICTION_ANALYTICS_REPORT/jurisdiction_dl.csv', index=False)
jurisdiction_visits.to_csv('JURISDICTION_ANALYTICS_REPORT/jurisdiction_visits.csv', index=False)
jurisdiction_mapviews.to_csv('JURISDICTION_ANALYTICS_REPORT/jurisdiction_mapviews.csv', index=False)

# Create a dictionary to store data for each jurisdiction
jurisdiction_data = {}
for jurisdiction in jurisdiction_dl['jurisdiction'].unique():
    jurisdiction_df = jurisdiction_dl[jurisdiction_dl['jurisdiction'] == jurisdiction]
    jurisdiction_data[jurisdiction] = jurisdiction_df

# Create the Mermaid code
mermaid_code = """
xychart-beta
    title "Downloads by Jurisdiction 🟦Fed 🟩Prov 🟥Muni"
    x-axis """

x_axis_labels = []
# Assuming your data has 'year_annee' and 'month_mois' columns
for year, month in jurisdiction_dl[['year_annee', 'month_mois']].drop_duplicates().sort_values(['year_annee', 'month_mois'], ascending=[False, False]).values.tolist()[-12:]:
  x_axis_labels.append(str(year) + '-' + str(month))

mermaid_code += "[" + ", ".join(x_axis_labels[::-1]) + "]"

mermaid_code += """
    y-axis "Downloads" 0 --> """ + str(jurisdiction_dl['downloads_telechargements'].max() + 10)

for jurisdiction in jurisdiction_data:
  jurisdiction_df = jurisdiction_data[jurisdiction]
  downloads_values = []
  for year, month in jurisdiction_dl[['year_annee', 'month_mois']].drop_duplicates().sort_values(['year_annee', 'month_mois'], ascending=[False, False]).values.tolist()[-12:]:
      download_for_month = jurisdiction_df[(jurisdiction_df['year_annee'] == year) & (jurisdiction_df['month_mois'] == month)]['downloads_telechargements'].sum()
      downloads_values.append(str(download_for_month))
      
  mermaid_code += """
    line """
  mermaid_code += "[" + ", ".join(downloads_values[::-1]) + "]"
  

mermaid_code

with open('JURISDICTION_ANALYTICS_REPORT/readme.md', 'w') as f:
  f.write('\n## Downloads by Jurisdiction last 12 months\n\n')
  f.write('```mermaid\n')
  f.write(mermaid_code)
  f.write('\n```\n')

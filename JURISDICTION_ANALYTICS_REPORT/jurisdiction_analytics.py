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


#create a mermaid xychart for jurisdiction_dl with 3 lines, 1 for each jurisdiction value.
def generate_mermaid_xychart(df, title):
  """Generates Mermaid XYChart code for a given dataframe."""
  mermaid_code = """
xychart-beta
    title "{}"
    x-axis """.format(title)

  x_axis_labels = []
  # Ensure that the dataframe is sorted by year and month in descending order.
  df = df.sort_values(['year_annee', 'month_mois'], ascending=[False, False])
  for index, row in df.head(12).iterrows():
    x_axis_labels.append(str(row['year_annee']) + '-' + str(row['month_mois']))
  mermaid_code += "[" + ", ".join(x_axis_labels[::-1]) + "]"

  # Find unique jurisdictions
  jurisdictions = df['jurisdiction'].unique()

  # Generate a line for each jurisdiction
  for jurisdiction in jurisdictions:
    temp_df = df[df['jurisdiction'] == jurisdiction]

    y_values = temp_df['downloads_telechargements'].head(12).tolist()[::-1]

    mermaid_code += """
    line "{}" """.format(jurisdiction)
    mermaid_code += "[" + ", ".join(map(str, y_values)) + "]"


  return mermaid_code


# Generate the Mermaid code and print it
mermaid_code = generate_mermaid_xychart(jurisdiction_dl, "Downloads by Jurisdiction")

with open('JURISDICTION_ANALYTICS_REPORT/readme.md', 'w') as f:
  f.write('\n## Downloads by Jurisdiction last 12 months\n\n')
  f.write('```mermaid\n')
  f.write(mermaid_code)
  f.write('\n```\n')

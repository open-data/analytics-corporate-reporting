import pandas as pd
from ckanapi import RemoteCKAN

# CKAN API endpoint
ckan = RemoteCKAN('https://open.canada.ca/data')

# Resource ID from the provided URL
resource_id = 'e664cf3d-6cb7-4aaa-adfa-e459c2552e3e'

# Get the resource information
resource = ckan.action.resource_show(id=resource_id)

# Download the resource data
# Assuming the resource is a CSV file
url = resource['url']
df = pd.read_csv(url)

#  from the df create a new df that gets the sum of Number of Informal Requests, and count of unique values of Unique Identifier, grouped by Year and Month column, sorted by year and month desc

yrmonth_df = df.groupby(['Year', 'Month'], as_index=False).agg({'Number of Informal Requests': 'sum', 'Unique Identifier': 'nunique'})
yrmonth_df = yrmonth_df.sort_values(['Year', 'Month'], ascending=[False, False])

#  from the df create a new df that gets the sum of Number of Informal Requests, and count of unique values of Unique Identifier, grouped by Year and Month and organization, sorted by year and month desc
org_df = df.groupby(['Year', 'Month','Organization Name - EN','Organization Name - FR','owner_org'], as_index=False).agg({'Number of Informal Requests': 'sum', 'Unique Identifier': 'nunique'})
org_df = org_df.sort_values(['Year', 'Month'], ascending=[False, False])

#  from the df create a new df that gets the sum of Number of Informal Requests, and count of unique values of Unique Identifier, grouped by organization, sorted by Number of Informal Requests desc
orgtot_df = df.groupby(['Organization Name - EN','Organization Name - FR','owner_org'], as_index=False).agg({'Number of Informal Requests': 'sum', 'Unique Identifier': 'nunique'})
orgtot_df = orgtot_df.sort_values(['Number of Informal Requests'], ascending=[False])

#  from the df create a new df that gets the top 100 most requested Informal Requests,
idtot_df = df.groupby(['Unique Identifier', 'Request Number', 'Summary - EN','Summary - FR', 'owner_org', 'Organization Name - EN','Organization Name - FR'], as_index=False).agg({'Number of Informal Requests': 'sum'})
idtot_df = idtot_df.sort_values(['Number of Informal Requests'], ascending=[False])
idtot_df.head(100)

# in a new df get the sum of Number of Informal Requests for each unique idenifier, grouped by year and month and return the top 10 for each year and month from the dataframe called df

top_10_df = df.groupby(['Year', 'Month', 'Unique Identifier','Request Number', 'Summary - EN','Summary - FR','owner_org', 'Organization Name - EN',
       'Organization Name - FR'])['Number of Informal Requests'].sum().reset_index()
top_10_df = top_10_df.groupby(['Year', 'Month']).apply(lambda x: x.nlargest(10, 'Number of Informal Requests')).reset_index(drop=True)
top_10_df = top_10_df.sort_values(['Year', 'Month'], ascending=[False, False])

# write top_10_df, org_df, idtot_df, yrmonth_df, and orgtot_df to csv files 


top_10_df.to_csv('top_10_df.csv', index=False)
org_df.to_csv('org_df.csv', index=False)
idtot_df.head(100).to_csv('idtot_df.csv', index=False)
yrmonth_df.to_csv('yrmonth_df.csv', index=False)
orgtot_df.to_csv('orgtot_df.csv', index=False)

# Generate Markdown table from DataFrame
yrmonth_table = yrmonth_df.head(24).to_markdown(index=False)
orgtot_table = orgtot_df.head(25).to_markdown(index=False)
idtot_table = idtot_df.head(25).to_markdown(index=False)

with open('readme.md', 'w') as f:
  f.write('# Data Tables\n\n')
  f.write('## ID Totals Table\n\n')
  f.write(idtot_table + '\n\n')
  f.write('## Organization Totals Table\n\n')
  f.write(orgtot_table + '\n\n')
  f.write('## Year-Month Table\n\n')
  f.write(yrmonth_table + '\n\n')


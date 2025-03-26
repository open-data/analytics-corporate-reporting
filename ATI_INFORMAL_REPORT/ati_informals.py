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
yrmonth_df = yrmonth_df.rename(columns={'Unique Identifier': 'Unique Packages'})

#  from the df create a new df that gets the sum of Number of Informal Requests, and count of unique values of Unique Identifier, grouped by Year and Month and organization, sorted by year and month desc
org_df = df.groupby(['Year', 'Month','Organization Name - EN','Organization Name - FR','owner_org'], as_index=False).agg({'Number of Informal Requests': 'sum', 'Unique Identifier': 'nunique'})
org_df = org_df.sort_values(['Year', 'Month'], ascending=[False, False])
org_df = org_df.rename(columns={'Unique Identifier': 'Unique Packages'})
org_df['owner_org'] = 'https://open.canada.ca/data/organization/' + org_df['owner_org'].astype(str)

#  from the df create a new df that gets the sum of Number of Informal Requests, and count of unique values of Unique Identifier, grouped by organization, sorted by Number of Informal Requests desc
orgtot_df = df.groupby(['Organization Name - EN','Organization Name - FR','owner_org'], as_index=False).agg({'Number of Informal Requests': 'sum', 'Unique Identifier': 'nunique'})
orgtot_df = orgtot_df.sort_values(['Number of Informal Requests'], ascending=[False])
orgtot_df = orgtot_df.rename(columns={'Unique Identifier': 'Unique Packages'})
orgtot_df['owner_org'] = 'https://open.canada.ca/data/organization/' + orgtot_df['owner_org'].astype(str)


#  from the df create a new df that gets the top 100 most requested Informal Requests,
idtot_df = df.groupby(['Unique Identifier', 'Request Number', 'Summary - EN','Summary - FR', 'owner_org', 'Organization Name - EN','Organization Name - FR'], as_index=False).agg({'Number of Informal Requests': 'sum'})
idtot_df = idtot_df.sort_values(['Number of Informal Requests'], ascending=[False])
idtot_df.head(100)
idtot_md=idtot_df[['Unique Identifier', 'Request Number','owner_org', 'Organization Name - EN','Organization Name - FR','Number of Informal Requests']]
idtot_md['Unique Identifier'] = '['+ idtot_df['Unique Identifier'] +']' + '('+'https://open.canada.ca/en/search/ati/reference/' + idtot_df['Unique Identifier'].astype(str) + ')'
idtot_md['owner_org'] = '['+ idtot_df['owner_org'] +']' + '('+'https://open.canada.ca/data/organization/' + idtot_df['owner_org'].astype(str) + ')'

# in a new df get the sum of Number of Informal Requests for each unique idenifier, grouped by year and month and return the top 10 for each year and month from the dataframe called df

top_10_df = df.groupby(['Year', 'Month', 'Unique Identifier','Request Number', 'Summary - EN','Summary - FR','owner_org', 'Organization Name - EN',
       'Organization Name - FR'])['Number of Informal Requests'].sum().reset_index()
top_10_df = top_10_df.groupby(['Year', 'Month']).apply(lambda x: x.nlargest(10, 'Number of Informal Requests')).reset_index(drop=True)
top_10_df = top_10_df.sort_values(['Year', 'Month'], ascending=[False, False])

# write top_10_df, org_df, idtot_df, yrmonth_df, and orgtot_df to csv files 


top_10_df.to_csv('ATI_INFORMAL_REPORT/top_10_df.csv', index=False)
org_df.to_csv('ATI_INFORMAL_REPORT/org_df.csv', index=False)
idtot_df.head(100).to_csv('ATI_INFORMAL_REPORT/idtot_df.csv', index=False)
yrmonth_df.to_csv('ATI_INFORMAL_REPORT/yrmonth_df.csv', index=False)
orgtot_df.to_csv('ATI_INFORMAL_REPORT/orgtot_df.csv', index=False)

# Generate Markdown table from DataFrame
yrmonth_table = yrmonth_df.head(24).to_markdown(index=False)
orgtot_table = orgtot_df.head(25).to_markdown(index=False)
idtot_table = idtot_md.head(25).to_markdown(index=False)

 #generate a mermaid.js xychart for yrmonth_df.head(24)

mermaid_code = """
xychart-beta
    title "Informal Requests🟩 and Unique Packages🟦 Over Time"
    x-axis """

x_axis_labels = []
for index, row in yrmonth_df.head(12).iterrows():
  x_axis_labels.append(str(row['Year']) + '-' + str(row['Month']))

mermaid_code += "[" + ", ".join(x_axis_labels[::-1]) + "]"
mermaid_code += """
    y-axis "Unique Packages" 0 --> """ + str(yrmonth_df['Unique Packages'].max() + 10) + """
    y-axis "Number of Informal Requests" 0 --> """ + str(yrmonth_df['Number of Informal Requests'].max() + 10) + """

    line """

unique_packages_values = yrmonth_df['Unique Packages'].head(12).tolist()[::-1]
mermaid_code += "[" + ", ".join(map(str, unique_packages_values)) + "]"

mermaid_code += """
    line """

informal_requests_values = yrmonth_df['Number of Informal Requests'].head(12).tolist()[::-1]
mermaid_code += "[" + ", ".join(map(str, informal_requests_values)) + "]"



with open('ATI_INFORMAL_REPORT/readme.md', 'w') as f:
  f.write('\n## Requests and Unique Package Requests last 12 months\n\n')
  f.write('```mermaid\n')
  f.write(mermaid_code)
  f.write('\n```\n')
  f.write('## Number of Requests and Unique Package Requests last 24 Months\n\n')
  f.write(yrmonth_table + '\n\n')
  f.write('## Organization Totals Table\n\n')
  f.write(orgtot_table + '\n\n')
  f.write('## Top 25 Most Requested\n\n')
  f.write(idtot_table + '\n\n')     


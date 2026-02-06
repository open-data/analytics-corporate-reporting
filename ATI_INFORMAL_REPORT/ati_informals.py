import pandas as pd
from ckanapi import RemoteCKAN

# CKAN API endpoint
ckan = RemoteCKAN('https://open.canada.ca/data')

# Resource ID from the provided URL
resource_id = 'e664cf3d-6cb7-4aaa-adfa-e459c2552e3e'

# Get the resource information
resource = ckan.action.resource_show(id=resource_id)

url = resource['url']
df = pd.read_csv(url, encoding="utf-8-sig")

# Normalize headers (handles UTF-8 BOM + stray whitespace)
df.columns = (
    df.columns.astype(str)
      .str.replace("\ufeff", "", regex=False)
      .str.strip()
)

# from the df create a new df that gets the sum of Number of Informal Requests,
# and count of unique values of Unique Identifier, grouped by Year and Month column,
# sorted by year and month desc
yrmonth_df = (
    df.groupby(['Year', 'Month'], as_index=False)
      .agg({'Number of Informal Requests': 'sum', 'Unique Identifier': 'nunique'})
      .sort_values(['Year', 'Month'], ascending=[False, False])
      .rename(columns={'Unique Identifier': 'Unique Packages'})
)

# from the df create a new df that gets the sum of Number of Informal Requests,
# and count of unique values of Unique Identifier, grouped by Year and Month and organization,
# sorted by year and month desc
org_df = (
    df.groupby(['Year', 'Month', 'Organization Name - EN', 'Organization Name - FR', 'owner_org'], as_index=False)
      .agg({'Number of Informal Requests': 'sum', 'Unique Identifier': 'nunique'})
      .sort_values(['Year', 'Month'], ascending=[False, False])
      .rename(columns={'Unique Identifier': 'Unique Packages'})
)
org_df['owner_org'] = 'https://open.canada.ca/data/organization/' + org_df['owner_org'].astype(str)

# from the df create a new df that gets the sum of Number of Informal Requests,
# and count of unique values of Unique Identifier, grouped by organization,
# sorted by Number of Informal Requests desc
orgtot_df = (
    df.groupby(['Organization Name - EN', 'Organization Name - FR', 'owner_org'], as_index=False)
      .agg({'Number of Informal Requests': 'sum', 'Unique Identifier': 'nunique'})
      .sort_values(['Number of Informal Requests'], ascending=[False])
      .rename(columns={'Unique Identifier': 'Unique Packages'})
)
orgtot_df['owner_org'] = 'https://open.canada.ca/data/organization/' + orgtot_df['owner_org'].astype(str)

# from the df create a new df that gets the top 100 most requested Informal Requests
idtot_df = (
    df.groupby(
        ['Unique Identifier', 'Request Number', 'Summary - EN', 'Summary - FR',
         'owner_org', 'Organization Name - EN', 'Organization Name - FR'],
        as_index=False
    )
      .agg({'Number of Informal Requests': 'sum'})
      .sort_values(['Number of Informal Requests'], ascending=[False])
)

# Markdown-friendly view (avoid SettingWithCopyWarning by copying)
idtot_md = idtot_df[
    ['Unique Identifier', 'Request Number', 'owner_org',
     'Organization Name - EN', 'Organization Name - FR',
     'Number of Informal Requests']
].copy()

idtot_md['Unique Identifier'] = (
    '[' + idtot_df['Unique Identifier'].astype(str) + ']' +
    '(' + 'https://open.canada.ca/en/search/ati/reference/' + idtot_df['Unique Identifier'].astype(str) + ')'
)
idtot_md['owner_org'] = (
    '[' + idtot_df['owner_org'].astype(str) + ']' +
    '(' + 'https://open.canada.ca/data/organization/' + idtot_df['owner_org'].astype(str) + ')'
)

# Top 10 per (Year, Month) — keep Year/Month as columns (prevents KeyError in sort_values)
top_10_df = (
    df.groupby(
        ['Year', 'Month', 'Unique Identifier', 'Request Number', 'Summary - EN', 'Summary - FR',
         'owner_org', 'Organization Name - EN', 'Organization Name - FR'],
        as_index=False
    )['Number of Informal Requests'].sum()
)

top_10_df = (
    top_10_df.groupby(['Year', 'Month'], group_keys=False)
             .apply(lambda x: x.nlargest(10, 'Number of Informal Requests'))
             .sort_values(['Year', 'Month'], ascending=[False, False])
             .reset_index(drop=True)
)

# write outputs to csv files (with ATI_INFORMAL_REPORT/ paths)
top_10_df.to_csv('ATI_INFORMAL_REPORT/top_10_df.csv', index=False)
org_df.to_csv('ATI_INFORMAL_REPORT/org_df.csv', index=False)
idtot_df.head(100).to_csv('ATI_INFORMAL_REPORT/idtot_df.csv', index=False)
yrmonth_df.to_csv('ATI_INFORMAL_REPORT/yrmonth_df.csv', index=False)
orgtot_df.to_csv('ATI_INFORMAL_REPORT/orgtot_df.csv', index=False)

# Generate Markdown table from DataFrame
yrmonth_table = yrmonth_df.head(24).to_markdown(index=False)
orgtot_table = orgtot_df.head(25).to_markdown(index=False)
idtot_table = idtot_md.head(25).to_markdown(index=False)

# generate a mermaid.js xychart for last 12 months
mermaid_code = """
xychart-beta
    title "Monthly 🟩Num. Informal Requests and 🟦Num. Unique Packages Requested - Last 12 Months"
    x-axis """

x_axis_labels = []
for _, row in yrmonth_df.head(12).iterrows():
    x_axis_labels.append(f"{row['Year']}-{row['Month']}")

mermaid_code += "[" + ", ".join(x_axis_labels[::-1]) + "]"
mermaid_code += """
    y-axis "Unique Packages" 0 --> """ + str(int(yrmonth_df['Unique Packages'].max()) + 10) + """
    y-axis "Number of Informal Requests" 0 --> """ + str(int(yrmonth_df['Number of Informal Requests'].max()) + 10) + """

    line """

unique_packages_values = yrmonth_df['Unique Packages'].head(12).tolist()[::-1]
mermaid_code += "[" + ", ".join(map(str, unique_packages_values)) + "]"

mermaid_code += """
    line """

informal_requests_values = yrmonth_df['Number of Informal Requests'].head(12).tolist()[::-1]
mermaid_code += "[" + ", ".join(map(str, informal_requests_values)) + "]"

with open('ATI_INFORMAL_REPORT/static.md', 'r', encoding='utf-8') as source_file:
    content = source_file.read()

with open('ATI_INFORMAL_REPORT/readme.md', 'w', encoding='utf-8') as f:
    f.write(content)
    f.write('\n## Requests and Unique Package Requests last 12 months\n\n')
    f.write('```mermaid\n')
    f.write(mermaid_code)
    f.write('\n```\n')
    f.write('## Number of Requests and Unique Package Requests last 24 Months\n\n')
    f.write(yrmonth_table + '\n\n')
    f.write('## Total Informal Requests Top 25 Organizations \n\n')
    f.write(orgtot_table + '\n\n')
    f.write('## Top 25 Most Requested\n\n')
    f.write(idtot_table + '\n\n')

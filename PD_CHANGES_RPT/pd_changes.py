import requests
import base64
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
import time
import os


# CKAN API Base URL
CKAN_API_URL = "https://open.canada.ca/data/api/3/action/organization_show?id={}"
# Define the file name for the Excel workbook
excel_filename = "PD_Activity.xlsx"



GITHUB_API_TOKEN = os.getenv("GITHUB_TOKEN")  # Use GitHub's built-in token


# GitHub Repo Details
GITHUB_API = "https://api.github.com"
REPO = "open-data/analytics-corporate-reporting"  # Change to your repo
FILE_PATH = "Corporate_reporting/pd_count/pd_per_dept.csv"
HEADERS = {"Authorization": f"token {GITHUB_API_TOKEN}"} if GITHUB_API_TOKEN else {} 


# Timeframes for comparison
DATES_TO_FIND = {
    "30-days": datetime.utcnow() - timedelta(days=30),
    "90-days": datetime.utcnow() - timedelta(days=90),
    "6-months": datetime.utcnow() - timedelta(days=180),
}

def get_commits_until(date_threshold):
    """Fetch commits until we find one older than 'date_threshold'"""
    all_commits = []
    page = 1

    while True:
        url = f"{GITHUB_API}/repos/{REPO}/commits?path={FILE_PATH}&per_page=30&page={page}"
        response = requests.get(url, headers=HEADERS)

        try:
            json_data = response.json()
        except ValueError:
            print("Error: Response is not valid JSON")
            print(response.text)  # Print raw response for debugging
            break  # Stop fetching

        if isinstance(json_data, dict) and "message" in json_data:
            print("Error: GitHub API returned an error:", json_data["message"])
            break  # Stop fetching

        if not isinstance(json_data, list) or len(json_data) == 0:
            print("No more commits found.")
            break  # Stop fetching

        for commit in json_data:
            commit_date = datetime.strptime(commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")

            # Stop when we find a commit older than the threshold
            if commit_date < date_threshold:
                print(f"Stopping at commit from {commit_date}, older than threshold {date_threshold}")
                return all_commits

            all_commits.append(commit)

        page += 1  # Move to the next page if needed

    return all_commits


def find_closest_commits(commits):
    """Find commits closest to the desired timeframes"""
    if not isinstance(commits, list):
        print("Error: Expected a list of commits but got:", type(commits))
        return {}

    closest_commits = {}
    for commit in commits:
        if not isinstance(commit, dict) or "sha" not in commit:
            print("Skipping invalid commit entry:", commit)
            continue

        commit_sha = commit["sha"]
        commit_date = datetime.strptime(commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")

        for label, target_date in DATES_TO_FIND.items():
            if label not in closest_commits or abs(commit_date - target_date) < abs(closest_commits[label][1] - target_date):
                closest_commits[label] = (commit_sha, commit_date)

    return closest_commits

def get_csv_from_commit(commit_sha):
    """Fetch and decode the CSV file from a given commit"""
    url = f"{GITHUB_API}/repos/{REPO}/contents/{FILE_PATH}?ref={commit_sha}"
    response = requests.get(url, headers=HEADERS).json()
    csv_content = base64.b64decode(response["content"]).decode("utf-8")

    # Read CSV while ensuring owner_org is set as the index
    df = pd.read_csv(StringIO(csv_content), delimiter=",")
    df.set_index("owner_org", inplace=True)
    return df

# Fetch commit history and find closest commits
six_months_ago = datetime.utcnow() - timedelta(days=180)
commits = get_commits_until(six_months_ago)
closest_commits = find_closest_commits(commits)

# Load current and past data
df_current = get_csv_from_commit(commits[0]["sha"])
df_past = {label: get_csv_from_commit(sha) for label, (sha, _) in closest_commits.items()}

# Ensure all DataFrames align by owner_org
for label, df_old in df_past.items():
    df_old = df_old.reindex(df_current.index).fillna(0)  # Fill missing entries with 0
    df_past[label] = df_old

# Compute differences and reorder columns
df_changes = df_current.copy()
ordered_columns = []

for col in df_current.columns:  # Iterate through all numeric columns
    ordered_columns.append(col)  # Add the main column first
    for label, df_old in df_past.items():
        change_col_name = f"{col}_change_{label}"
        df_changes[change_col_name] = df_current[col] - df_old[col]
        ordered_columns.append(change_col_name)  # Insert the change column right after the main column

# Reorder columns
df_changes = df_changes[ordered_columns]



def get_ckan_organization(org_id):
    """Fetch CKAN organization metadata from Open Canada API."""
    url = CKAN_API_URL.format(org_id)
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching {org_id}: {response.status_code}")
        return None

    data = response.json()
    if not data.get("success", False):
        print(f"Failed to retrieve {org_id}: {data}")
        return None

    return data["result"]

# Load `owner_org` values from existing DataFrame
owner_orgs = df_changes.index.tolist()  # Assuming `df_changes` exists from previous steps

# Create a list to store CKAN organization details
ckan_data = []

# Fetch CKAN data for each `owner_org`
for org in owner_orgs:
    org_data = get_ckan_organization(org)
    if org_data:
        ckan_data.append({
            "owner_org": org,
            "title": org_data.get("title", ""),
            "ati_email": org_data.get("ati_email", ""),
            "packages": org_data.get("package_count", 0),
            "created": org_data.get("created", ""),
            "faa_schedule": org_data.get("faa_schedule", ""),
            "opengov_email": org_data.get("opengov_email", ""),
        })



# Convert CKAN data to a DataFrame
df_ckan = pd.DataFrame(ckan_data)

# Convert 'created' column to YYYY-MM-DD format
df_ckan["created"] = pd.to_datetime(df_ckan["created"], errors="coerce").dt.strftime("%Y-%m-%d")


# --- Add a "Total Original" sum column that sums all the original (non-change) columns ---

# Identify original columns (columns that do not contain '_change_')
original_columns = [col for col in df_changes.columns if '_change_' not in col]

# Create a new column "Total Original" that sums across these columns for each row
df_changes['Total Original'] = df_changes[original_columns].sum(axis=1)

# --- Add sum columns for the change values for each timeframe ---

# Define the timeframes we are interested in
timeframes = ['30-days', '90-days', '6-months']

for timeframe in timeframes:
    # Identify all columns that have change values for this timeframe
    timeframe_columns = [col for col in df_changes.columns if f'_change_{timeframe}' in col]
    if timeframe_columns:  # Only add if such columns exist
        df_changes[f'Total Change {timeframe}'] = df_changes[timeframe_columns].sum(axis=1)




with pd.ExcelWriter(excel_filename, engine="xlsxwriter") as writer:
    # Write the DataFrames to their respective sheets.
    # df_changes is written with index=True so that the index appears as the first column.
    df_changes.to_excel(writer, sheet_name="CSV Changes", index=True)
    df_ckan.to_excel(writer, sheet_name="CKAN Data", index=False)

    # Get the underlying workbook object
    workbook = writer.book

    # Create a header format with text wrapping and top vertical alignment.
    header_format = workbook.add_format({
        'text_wrap': True,
        'valign': 'top'
    })

    # Get the worksheets
    worksheet_changes = writer.sheets["CSV Changes"]
    worksheet_ckan = writer.sheets["CKAN Data"]

    # Set the header row height to 30 and apply the header format on both sheets.
    worksheet_changes.set_row(0, 80, header_format)
    worksheet_ckan.set_row(0, 30, header_format)

    # Freeze the header row in both sheets.
    worksheet_changes.freeze_panes(1, 0)
    worksheet_ckan.freeze_panes(1, 0)

    # Set the width for the first column (the index column) in the CSV Changes sheet to 12.
    worksheet_changes.set_column(0, 0, 12)

    # Create formats for coloring:
    # Medium blue for original value columns.
    original_format = workbook.add_format({'bg_color': '#4F81BD'})
    # Pale blue for change columns.
    change_format = workbook.add_format({'bg_color': '#DCE6F1'})

    # Loop through DataFrame columns (which are written starting at Excel column 1 due to index=True)
    for col in df_changes.columns:
        col_idx = df_changes.columns.get_loc(col) + 1  # offset by 1 because the index is in column 0
        if '_change_' in col:
            worksheet_changes.set_column(col_idx, col_idx, 6, change_format)
        else:
            worksheet_changes.set_column(col_idx, col_idx, 6, original_format)

    # Replace underscores with newline characters in the header row of the CSV Changes sheet.
    # Since the DataFrame headers start at Excel column 1 (index column is column 0),
    # we iterate over the DataFrame's columns and update the cell contents.
    for i, col in enumerate(df_changes.columns):
        # Replace all underscores with newline characters
        new_header = col.replace("_", "\n")
        # Write the new header text back to the header cell (row 0, column i+1)
        worksheet_changes.write(0, i+1, new_header, header_format)

# Write df_changes to CSV file, including the index
df_changes.to_csv("pd_changes_data.csv", index=True)

# Write df_ckan to CSV file without the index
df_ckan.to_csv("pd_org_data.csv", index=False)
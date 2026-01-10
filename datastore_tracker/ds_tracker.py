
#!/usr/bin/env python3

import requests
import gzip
import os
import time
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse
import concurrent.futures  # for parallelization
from tqdm import tqdm      # for progress bar

# Optional faster JSON parsing
try:
    import ujson as json
except ImportError:
    import json

def pretty_bytes(num_bytes):
    """
    Convert a file size in bytes into a human-readable string.
    Equivalent to R's prettyunits::pretty_bytes().
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:3.1f}{unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f}YB"

def is_nonempty_text(value):
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return bool(value)

def get_datastore_info(resource_id):
    """
    Fetches datastore_info for a given resource_id.
    Returns a tuple: (ds_count, ds_fields, ds_size, ds_type_set, ds_label_set, ds_notes_set).
    If the resource is not found or another error occurs,
    returns (None, None, None, None, None, None).
    """
    ds_info_url = f"https://open.canada.ca/data/en/api/3/action/datastore_info?id={resource_id}"
    try:
        resp = requests.get(ds_info_url)
        data = resp.json()
        if data.get("success") and "result" in data:
            meta = data["result"].get("meta", {})
            fields = data["result"].get("fields", [])
            ds_count = meta.get("count", None)
            ds_fields = len(fields)
            ds_size = meta.get("size", None)
            ds_type_set = 0
            ds_label_set = 0
            ds_notes_set = 0
            for field in fields:
                info = field.get("info", {})
                if not isinstance(info, dict):
                    info = {}

                if is_nonempty_text(info.get("type_override", "")):
                    ds_type_set += 1
                if is_nonempty_text(info.get("label_en", "")) or is_nonempty_text(info.get("label_fr", "")):
                    ds_label_set += 1
                if is_nonempty_text(info.get("notes_en", "")) or is_nonempty_text(info.get("notes_fr", "")):
                    ds_notes_set += 1

            return ds_count, ds_fields, ds_size, ds_type_set, ds_label_set, ds_notes_set
    except Exception:
        pass
    return None, None, None, None, None, None

def build_resource_counts_table(df):
    """
    Build a markdown table of resource counts by URL host and owner.
    """
    url_hosts = df["url"].fillna("").map(lambda u: urlparse(u).netloc.lower())
    counts = (
        df.assign(url_host=url_hosts)
        .query("url_host != ''")
        .groupby(["url_host", "owner"])
        .size()
        .reset_index(name="resource_count")
        .sort_values(["url_host", "owner"])
    )

    headers = ["url_host", "owner", "resource_count"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for _, row in counts.iterrows():
        lines.append(f"| {row['url_host']} | {row['owner']} | {int(row['resource_count'])} |")

    return "\n".join(lines)

def update_readme_resource_counts(readme_path, table_md):
    """
    Replace the resource counts section in README.md.
    """
    header = "#### Resource counts by URL host and org"
    start_marker = "<!-- RESOURCE_COUNTS_START -->"
    end_marker = "<!-- RESOURCE_COUNTS_END -->"
    section = f"{header}\n{start_marker}\n{table_md}\n{end_marker}"

    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = ""

    if start_marker in content and end_marker in content:
        prefix, rest = content.split(start_marker, 1)
        _, suffix = rest.split(end_marker, 1)
        content = f"{prefix}{start_marker}\n{table_md}\n{end_marker}{suffix}"
        if header not in prefix:
            content = content.replace(start_marker, f"{header}\n{start_marker}", 1)
    else:
        if content and not content.endswith("\n"):
            content += "\n"
        content += f"\n{section}\n"

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

def format_percent(value):
    formatted = f"{value:.2f}".rstrip("0").rstrip(".")
    return formatted if formatted else "0"

def build_dictionary_radar_chart(df):
    """
    Build a mermaid radar chart showing dictionary edit coverage by type.
    """
    for col in ["ds_count", "ds_type_set", "ds_label_set", "ds_notes_set"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    def percent_counts(subset):
        total_count = subset["ds_count"].sum()
        if pd.isna(total_count) or total_count <= 0:
            return 0.0, 0.0, 0.0
        type_pct = 100 * subset["ds_type_set"].sum() / total_count
        label_pct = 100 * subset["ds_label_set"].sum() / total_count
        notes_pct = 100 * subset["ds_notes_set"].sum() / total_count
        return type_pct, label_pct, notes_pct

    upload_pct = percent_counts(df[df["type"] == "upload"])
    remote_pct = percent_counts(df[df["type"] == "remote"])

    return "\n".join([
        "```mermaid",
        "radar-beta",
        "  axis T[\"Type\"], L[\"Label\"], N[\"Notes\"]",
        f"  curve u[\"Upload\"]{{{format_percent(upload_pct[0])}, {format_percent(upload_pct[1])}, {format_percent(upload_pct[2])}}}",
        f"  curve r[\"Remote\"]{{{format_percent(remote_pct[0])}, {format_percent(remote_pct[1])}, {format_percent(remote_pct[2])}}}",
        "",
        "  showLegend true",
        "",
        "  min 0",
        "  graticule circle",
        "  ticks 5",
        "```",
    ])

def update_readme_dictionary_radar(readme_path, chart_md):
    """
    Replace the dictionary radar section in README.md.
    """
    header = "#### Dictionary edit radar (by type)"
    start_marker = "<!-- DICT_RADAR_START -->"
    end_marker = "<!-- DICT_RADAR_END -->"
    section = f"{header}\n{start_marker}\n{chart_md}\n{end_marker}"

    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = ""

    if start_marker in content and end_marker in content:
        prefix, rest = content.split(start_marker, 1)
        _, suffix = rest.split(end_marker, 1)
        content = f"{prefix}{start_marker}\n{chart_md}\n{end_marker}{suffix}"
        if header not in prefix:
            content = content.replace(start_marker, f"{header}\n{start_marker}", 1)
    else:
        if content and not content.endswith("\n"):
            content += "\n"
        content += f"\n{section}\n"

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

# ---------------------------------------------------------------------
# 1. Download the compressed JSONL file
# ---------------------------------------------------------------------
url = "https://open.canada.ca/static/od-do-canada.jsonl.gz"
print("Downloading file...")
start_download = time.time()
r = requests.get(url, stream=True)
with open("od-do-canada.jsonl.gz", "wb") as f:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)
end_download = time.time()
print(f"Download complete in {end_download - start_download:.2f} seconds.")

# ---------------------------------------------------------------------
# 2. Decompress the file
# ---------------------------------------------------------------------
print("Unzipping file...")
start_unzip = time.time()
with gzip.open("od-do-canada.jsonl.gz", "rb") as f_in, open("od-do-canada.jsonl", "wb") as f_out:
    f_out.write(f_in.read())
os.remove("od-do-canada.jsonl.gz")
end_unzip = time.time()
print(f"Unzip complete in {end_unzip - start_unzip:.2f} seconds.")

# ---------------------------------------------------------------------
# 3. Parse each line and build a list of dictionaries
# ---------------------------------------------------------------------
print("Parsing JSON lines...")
start_parse = time.time()

list_of_dicts = []
with open("od-do-canada.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        tmp_data = json.loads(line)
        tmp_res = tmp_data.get("resources", [])
        if not tmp_res:
            continue

        # For each resource, store relevant row if datastore_active != FALSE
        for resource in tmp_res:
            if resource.get("datastore_active", True):
                url = resource.get("url", "")
                resource_type = "upload" if "https://open.canada.ca" in url else "remote"
                row_dict = {
                    "owner":         tmp_data.get("organization", {}).get("name", ""),
                    "package_id":    resource.get("package_id", ""),
                    "dataset_name":  tmp_data.get("title", ""),
                    "resource_id":   resource.get("id", ""),
                    "resource_name": resource.get("name", ""),
                    "metadata_modified": resource.get("metadata_modified", ""),
                    "size":          resource.get("size", ""),
                    "url":           url,
                    "type":          resource_type
                }
                list_of_dicts.append(row_dict)

end_parse = time.time()
print(f"Parsing complete in {end_parse - start_parse:.2f} seconds.")

# ---------------------------------------------------------------------
# 4. Create a DataFrame from the collected dictionaries
# ---------------------------------------------------------------------
list_of_res = pd.DataFrame(list_of_dicts)

# ---------------------------------------------------------------------
# 5. Summaries (unique counts, date/time, etc.)
# ---------------------------------------------------------------------
date_str = datetime.now().strftime('%Y-%m-%d')
num_dept = list_of_res["owner"].nunique()
num_datasets = list_of_res["package_id"].nunique()
num_res = list_of_res["resource_id"].nunique()
count_open_canada = (list_of_res["type"] == "upload").sum()
count_remote_xload = (list_of_res["type"] == "remote").sum()

# ---------------------------------------------------------------------
# 6. Fetch datastore size from CKAN API (database-level info)
# ---------------------------------------------------------------------
ds_url = "https://open.canada.ca/data/en/api/3/action/datastore_info?id=3c911562-c541-463f-8cd4-490182cd57f9"
ds_resp = requests.get(ds_url)
ds_data = ds_resp.json()
ds_size_bytes = ds_data["result"]["meta"]["db_size"]
ds_size_readable = pretty_bytes(ds_size_bytes)

print("Setup steps complete. Ready to fetch datastore_info in parallel.")
# ---------------------------------------------------------------------
# 7. (Parallel) Fetch datastore info for each resource (with progress bar)
# ---------------------------------------------------------------------
print("Fetching datastore info for each resource in parallel (10 at a time). This may take a while...")

# Create new columns to store datastore info
list_of_res["ds_count"] = None
list_of_res["ds_fields"] = None
list_of_res["ds_size"] = None
list_of_res["ds_type_set"] = None
list_of_res["ds_label_set"] = None
list_of_res["ds_notes_set"] = None

# Use ThreadPoolExecutor to do calls in parallel (up to 10 workers)
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures_map = {}
    for idx, row in list_of_res.iterrows():
        resource_id = row["resource_id"]
        # Submit a job to the executor
        future = executor.submit(get_datastore_info, resource_id)
        futures_map[future] = idx

    # Wrap as_completed() with tqdm so we have a progress bar
    for future in tqdm(
        concurrent.futures.as_completed(futures_map),
        total=len(futures_map),
        desc="Fetching datastore_info"
    ):
        idx = futures_map[future]
        try:
            ds_count, ds_fields, ds_size, ds_type_set, ds_label_set, ds_notes_set = future.result()
            list_of_res.at[idx, "ds_count"] = ds_count
            list_of_res.at[idx, "ds_fields"] = ds_fields
            list_of_res.at[idx, "ds_size"] = ds_size
            list_of_res.at[idx, "ds_type_set"] = ds_type_set
            list_of_res.at[idx, "ds_label_set"] = ds_label_set
            list_of_res.at[idx, "ds_notes_set"] = ds_notes_set
        except Exception:
            # If something fails, just leave columns as None
            pass

print("Parallel fetch complete.")

# ---------------------------------------------------------------------
# 8. Build DS_num_tracker_df (single row)
# ---------------------------------------------------------------------

# Convert ds_count and ds_fields to numeric so we can safely sum them
list_of_res["ds_count"] = pd.to_numeric(list_of_res["ds_count"], errors="coerce")
list_of_res["ds_fields"] = pd.to_numeric(list_of_res["ds_fields"], errors="coerce")
list_of_res["ds_size"] = pd.to_numeric(list_of_res["ds_size"], errors="coerce")
list_of_res["ds_type_set"] = pd.to_numeric(list_of_res["ds_type_set"], errors="coerce")
list_of_res["ds_label_set"] = pd.to_numeric(list_of_res["ds_label_set"], errors="coerce")
list_of_res["ds_notes_set"] = pd.to_numeric(list_of_res["ds_notes_set"], errors="coerce")

dict_edit_mask = (
    (list_of_res["ds_type_set"].fillna(0) > 0)
    | (list_of_res["ds_label_set"].fillna(0) > 0)
    | (list_of_res["ds_notes_set"].fillna(0) > 0)
)
list_of_res["dict_edit"] = dict_edit_mask.map(lambda edited: "Y" if edited else "N")

remote_mask = list_of_res["type"] == "remote"
ds_remote_size = list_of_res.loc[remote_mask, "ds_size"].sum()
ds_remote_rows = list_of_res.loc[remote_mask, "ds_count"].sum()
ds_remote_cols = list_of_res.loc[remote_mask, "ds_fields"].sum()

DS_num_tracker_df = pd.DataFrame([{
    "date": date_str,
    "num_dept": num_dept,
    "num_datasets": num_datasets,
    "num_res": num_res,
    "ds_size_bytes": ds_size_bytes,
    "ds_size_readable": ds_size_readable,
    "sum_ds_fields": list_of_res["ds_fields"].sum(),
    "sum_ds_count": list_of_res["ds_count"].sum(),
    "ds_remote_size": ds_remote_size,
    "ds_remote_rows": ds_remote_rows,
    "ds_remote_cols": ds_remote_cols,
    "count_open_canada": count_open_canada,
    "count_remote_xload": count_remote_xload

}])

# ---------------------------------------------------------------------
# 9. Append the new row to DS_num_tracker.csv, ensuring newest row on top
# ---------------------------------------------------------------------
csv_path = "DS_num_tracker.csv"

if os.path.exists(csv_path):
    old_df = pd.read_csv(csv_path)
    combined_df = pd.concat([DS_num_tracker_df, old_df], ignore_index=True)
    # Convert 'date' column to datetime so we can sort properly
    combined_df["date"] = pd.to_datetime(combined_df["date"], format="%Y-%m-%d", errors="coerce")
    combined_df.sort_values(by="date", ascending=False, inplace=True)
    combined_df["date"] = combined_df["date"].dt.strftime("%Y-%m-%d")
    combined_df.to_csv(csv_path, index=False)
else:
    DS_num_tracker_df.to_csv(csv_path, index=False)

# ---------------------------------------------------------------------
# 10. Save resources list to CSV
# ---------------------------------------------------------------------
resource_cols = [
    "owner",
    "package_id",
    "dataset_name",
    "resource_id",
    "resource_name",
    "metadata_modified",
    "size",
    "url",
    "type",
    "ds_count",
    "ds_fields",
    "ds_size",
]
list_of_res[resource_cols].to_csv("ds-resources.csv", index=False)

# ---------------------------------------------------------------------
# 11. Save dictionary edit stats to CSV
# ---------------------------------------------------------------------
dictionary_cols = [
    "owner",
    "package_id",
    "dataset_name",
    "resource_id",
    "resource_name",
    "metadata_modified",
    "type",
    "ds_count",
    "ds_fields",
    "dict_edit",
    "ds_type_set",
    "ds_label_set",
    "ds_notes_set",
]
list_of_res[dictionary_cols].to_csv("ds-dictionary-use.csv", index=False)

# ---------------------------------------------------------------------
# 12. Print output (useful for debugging or GH Action logs)
# ---------------------------------------------------------------------
print("=== DS_num_tracker (latest) ===")
print(DS_num_tracker_df.to_string(index=False))
print("\nCSV appended (or created) successfully.")


# ---------------------------------------------------------------------
# 13. create org stats
# ---------------------------------------------------------------------
# Convert relevant columns to numeric
list_of_res['size'] = pd.to_numeric(list_of_res['size'], errors='coerce')
list_of_res['ds_fields'] = pd.to_numeric(list_of_res['ds_fields'], errors='coerce')
list_of_res['ds_count'] = pd.to_numeric(list_of_res['ds_count'], errors='coerce')

# Group by 'owner' and aggregate
org_stats = (
    list_of_res
    .groupby('owner')
    .agg(
        sum_size=('size', 'sum'),
        unique_packages=('package_id', 'nunique'),
        unique_resources=('resource_id', 'nunique'),
        sum_ds_fields=('ds_fields', 'sum'),
        sum_ds_n_rows=('ds_count', 'sum')
    )
    .reset_index()
)

# Convert the summed size to a human-readable format
org_stats['sum_size'] = org_stats['sum_size'].apply(pretty_bytes)

# Write the DataFrame to a CSV file
org_stats.to_csv("org_stats.csv", index=False)

# ---------------------------------------------------------------------
# 14. update README with resource counts
# ---------------------------------------------------------------------
resource_counts_table = build_resource_counts_table(list_of_res)
update_readme_resource_counts("README.md", resource_counts_table)

# ---------------------------------------------------------------------
# 15. update README with dictionary radar chart
# ---------------------------------------------------------------------
dictionary_radar_chart = build_dictionary_radar_chart(list_of_res)
update_readme_dictionary_radar("README.md", dictionary_radar_chart)

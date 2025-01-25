
#!/usr/bin/env python3

import requests
import gzip
import os
import time
import pandas as pd
from datetime import datetime
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

def get_datastore_info(resource_id):
    """
    Fetches datastore_info for a given resource_id.
    Returns a tuple: (ds_count, ds_fields, ds_size).
    If the resource is not found or another error occurs,
    returns (None, None, None).
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
            return ds_count, ds_fields, ds_size
    except Exception:
        pass
    return None, None, None

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
                row_dict = {
                    "owner":         tmp_data.get("organization", {}).get("name", ""),
                    "package_id":    resource.get("package_id", ""),
                    "dataset_name":  tmp_data.get("title", ""),
                    "resource_id":   resource.get("id", ""),
                    "resource_name": resource.get("name", ""),
                    "metadata_modified": resource.get("metadata_modified", ""),
                    "size":          resource.get("size", ""),
                    "url":           resource.get("url", "")
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
count_open_canada = list_of_res["url"].str.contains("open.canada.ca").sum()
count_remote_xload = (~list_of_res["url"].str.contains("open.canada.ca")).sum()

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
            ds_count, ds_fields, ds_size = future.result()
            list_of_res.at[idx, "ds_count"] = ds_count
            list_of_res.at[idx, "ds_fields"] = ds_fields
            list_of_res.at[idx, "ds_size"] = ds_size
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

DS_num_tracker_df = pd.DataFrame([{
    "date": date_str,
    "num_dept": num_dept,
    "num_datasets": num_datasets,
    "num_res": num_res,
    "ds_size_bytes": ds_size_bytes,
    "ds_size_readable": ds_size_readable,
    "sum_ds_fields": list_of_res["ds_fields"].sum(),
    "sum_ds_count": list_of_res["ds_count"].sum(),
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
# 10. (Optional) Save resources list to CSV if desired
# ---------------------------------------------------------------------
list_of_res.to_csv("ds-resources.csv", index=False)

# ---------------------------------------------------------------------
# 11. Print output (useful for debugging or GH Action logs)
# ---------------------------------------------------------------------
print("=== DS_num_tracker (latest) ===")
print(DS_num_tracker_df.to_string(index=False))
print("\nCSV appended (or created) successfully.")


# ---------------------------------------------------------------------
# 12. create org stats
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

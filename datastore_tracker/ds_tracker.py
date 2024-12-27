#!/usr/bin/env python3

import requests
import gzip
import os
import time
import pandas as pd
from datetime import datetime

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


def main():
    # -------------------------------------------------------------------------
    # 1. Download the compressed JSONL file
    # -------------------------------------------------------------------------
    url = "https://open.canada.ca/static/od-do-canada.jsonl.gz"
    print("Downloading file...")
    start_download = time.time()
    r = requests.get(url, stream=True)
    with open("od-do-canada.jsonl.gz", "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    end_download = time.time()
    print(f"Download complete in {end_download - start_download:.2f} seconds.")

    # -------------------------------------------------------------------------
    # 2. Decompress the file
    # -------------------------------------------------------------------------
    print("Unzipping file...")
    start_unzip = time.time()
    with gzip.open("od-do-canada.jsonl.gz", "rb") as f_in, open("od-do-canada.jsonl", "wb") as f_out:
        f_out.write(f_in.read())
    os.remove("od-do-canada.jsonl.gz")
    end_unzip = time.time()
    print(f"Unzip complete in {end_unzip - start_unzip:.2f} seconds.")

    # -------------------------------------------------------------------------
    # 3. Parse each line and build a list of dictionaries
    # -------------------------------------------------------------------------
    print("Parsing JSON lines...")
    start_parse = time.time()

    list_of_dicts = []

    with open("od-do-canada.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            tmp_data = json.loads(line)
            tmp_res = tmp_data.get("resources", [])

            # Skip if no resources
            if not tmp_res:
                continue

            # For each resource, store relevant row if datastore_active != FALSE
            for resource in tmp_res:
                if resource.get("datastore_active", False) != False:
                    row_dict = {
                        "owner":         tmp_data.get("organization", {}).get("name", ""),
                        "package_id":    resource.get("package_id", ""),
                        "dataset_name":  tmp_data.get("title", ""),
                        "resource_id":   resource.get("id", ""),
                        "resource_name": resource.get("name", ""),
                        "size":          resource.get("size", "")
                    }
                    list_of_dicts.append(row_dict)

    end_parse = time.time()
    print(f"Parsing complete in {end_parse - start_parse:.2f} seconds.")

    # -------------------------------------------------------------------------
    # 4. Create a DataFrame from the collected dictionaries
    # -------------------------------------------------------------------------
    start_df = time.time()
    list_of_res = pd.DataFrame(list_of_dicts)
    end_df = time.time()
    print(f"DataFrame creation complete in {end_df - start_df:.2f} seconds.")

    # -------------------------------------------------------------------------
    # 5. Summaries (unique counts, date/time, etc.)
    # -------------------------------------------------------------------------
    # Use YYYY-MM-DD format
    date_str = datetime.now().strftime('%Y-%m-%d')
    num_dept = list_of_res["owner"].nunique()
    num_datasets = list_of_res["package_id"].nunique()
    num_res = list_of_res["resource_id"].nunique()

    # -------------------------------------------------------------------------
    # 6. Fetch datastore size from CKAN API
    # -------------------------------------------------------------------------
    ds_url = "https://open.canada.ca/data/en/api/3/action/datastore_info?id=3c911562-c541-463f-8cd4-490182cd57f9"
    ds_resp = requests.get(ds_url)
    ds_data = ds_resp.json()
    ds_size_bytes = ds_data["result"]["meta"]["db_size"]
    ds_size_readable = pretty_bytes(ds_size_bytes)

    # -------------------------------------------------------------------------
    # 7. Build a DataFrame for DS_num_tracker (single row)
    # -------------------------------------------------------------------------
    DS_num_tracker_df = pd.DataFrame([{
        "date": date_str,
        "num_dept": num_dept,
        "num_datasets": num_datasets,
        "num_res": num_res,
        "ds_size_readable": ds_size_readable
    }])

    # -------------------------------------------------------------------------
    # 8. Append the new row to DS_num_tracker.csv, ensuring the newest row is on top
    # -------------------------------------------------------------------------
    csv_path = "DS_num_tracker.csv"

    if os.path.exists(csv_path):
        # Read existing CSV
        old_df = pd.read_csv(csv_path)

        # Append new row (concat) then sort by date descending
        combined_df = pd.concat([DS_num_tracker_df, old_df], ignore_index=True)

        # Convert 'date' column to datetime so we can sort properly
        combined_df["date"] = pd.to_datetime(combined_df["date"], format="%Y-%m-%d", errors="coerce")
        combined_df.sort_values(by="date", ascending=False, inplace=True)

        # Re-format date back to string if needed
        combined_df["date"] = combined_df["date"].dt.strftime("%Y-%m-%d")

        # Write to CSV
        combined_df.to_csv(csv_path, index=False)
    else:
        # If no CSV exists, just write the single row
        DS_num_tracker_df.to_csv(csv_path, index=False)

    # -------------------------------------------------------------------------
    # 9. (Optional) Save resources list to CSV if desired
    # -------------------------------------------------------------------------
    list_of_res.to_csv("ds-resources.csv", index=False)

    # -------------------------------------------------------------------------
    # 10. Print output (useful for debugging or GH Action logs)
    # -------------------------------------------------------------------------
    print("=== DS_num_tracker (latest) ===")
    print(DS_num_tracker_df.to_string(index=False))
    print("\nCSV appended (or created) successfully.")

if __name__ == "__main__":
    main()

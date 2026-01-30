
#!/usr/bin/env python3

import requests
import gzip
import os
import time
import pandas as pd
from datetime import datetime
from io import StringIO
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

def update_readme_section(readme_path, section_content, header, start_marker, end_marker):
    """
    Replace a section in README.md identified by start/end markers with new content.

    Fix: prevent duplicated headers on repeated runs by replacing the *entire* block
    (including any repeated header lines immediately above the start marker).
    """
    import re

    new_section = f"{header}\n{start_marker}\n{section_content}\n{end_marker}"

    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = ""

    # If the markers exist, replace the whole block (header + markers + content),
    # tolerating multiple repeated header lines.
    if start_marker in content and end_marker in content:
        # Match one or more copies of the header (possibly separated by blank lines)
        # directly followed by the start marker, then anything up to end marker.
        hdr = re.escape(header)
        sm = re.escape(start_marker)
        em = re.escape(end_marker)

        block_re = re.compile(
            rf"(?:^|\n)(?:{hdr}\s*\n)+\s*{sm}[\s\S]*?{em}",
            re.MULTILINE
        )

        if block_re.search(content):
            content = block_re.sub(lambda m: "\n" + new_section, content, count=1)
        else:
            # Fallback: replace only the marker-delimited content, and ensure header once.
            content = re.sub(
                rf"{sm}[\s\S]*?{em}",
                f"{start_marker}\n{section_content}\n{end_marker}",
                content,
                count=1
            )
            # Ensure a single header line directly above the start marker
            content = re.sub(
                rf"(?:{hdr}\s*\n)+\s*{sm}",
                f"{header}\n{start_marker}",
                content
            )
    else:
        # Append if not present
        if content and not content.endswith("\n"):
            content += "\n"
        if content.strip():
            content += "\n"
        content += f"{new_section}\n"

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

def update_readme_resource_counts(readme_path, table_md):
    """
    Replace the resource counts section in README.md.
    """
    header = "#### Resource counts by URL host and org"
    start_marker = "<!-- RESOURCE_COUNTS_START -->"
    end_marker = "<!-- RESOURCE_COUNTS_END -->"
    update_readme_section(readme_path, table_md, header, start_marker, end_marker)

def format_percent(value):
    formatted = f"{value:.5f}".rstrip("0").rstrip(".")
    return formatted if formatted else "0"

def build_dictionary_radar_chart(df):
    """
    Build a mermaid radar chart showing dictionary edit coverage by type.
    """
    # Ensure relevant columns are numeric, coercing errors will turn non-numeric into NaN
    for col in ["ds_count", "ds_type_set", "ds_label_set", "ds_notes_set"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    def percent_counts(subset):
        valid_subset = subset[subset["ds_count"].notna() & (subset["ds_count"] > 0)]
        total_count = valid_subset["ds_count"].sum()
        if total_count <= 0:
            return 0.0, 0.0, 0.0
        type_pct = 100 * valid_subset["ds_type_set"].sum() / total_count
        label_pct = 100 * valid_subset["ds_label_set"].sum() / total_count
        notes_pct = 100 * valid_subset["ds_notes_set"].sum() / total_count
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
    update_readme_section(readme_path, chart_md, header, start_marker, end_marker)

def parse_name_translated(name_translated_obj):
    if isinstance(name_translated_obj, dict):
        return name_translated_obj.get("en"), name_translated_obj.get("fr")
    return None, None

def process_relationships_and_resource_ids(relationships_list, current_resource_id):
    results = {}
    if not isinstance(relationships_list, list):
        return results

    resource_ids_by_rel_type = {}

    first_rel_dict = relationships_list[0] if relationships_list else {}
    results["related_relationship"] = first_rel_dict.get("related_relationship")
    results["rel_resource_type"] = first_rel_dict.get("resource_type")

    related_url_obj = first_rel_dict.get("related_url")
    results["related_url_en"] = related_url_obj.get("en") if isinstance(related_url_obj, dict) else None
    results["related_url_fr"] = related_url_obj.get("fr") if isinstance(related_url_obj, dict) else None

    for rel_dict in relationships_list:
        rel_type = rel_dict.get("related_relationship")
        if rel_type:
            if rel_type not in resource_ids_by_rel_type:
                resource_ids_by_rel_type[rel_type] = []
            if current_resource_id not in resource_ids_by_rel_type[rel_type]:
                resource_ids_by_rel_type[rel_type].append(current_resource_id)

    for rel_type, ids in resource_ids_by_rel_type.items():
        col_name = f"{rel_type}_resource_id"
        results[col_name] = ", ".join(ids)

    return pd.Series(results)

# ---------------------------------------------------------------------
# 1. Download and unzip the compressed JSONL file
# ---------------------------------------------------------------------
url_jsonl_gz = "https://open.canada.ca/static/od-do-canada.jsonl.gz"
file_gz = "od-do-canada.jsonl.gz"
file_jsonl = "od-do-canada.jsonl"

max_retries = 5
for attempt in range(max_retries):
    try:
        print(f"Downloading file (Attempt {attempt + 1}/{max_retries})...")
        r = requests.get(url_jsonl_gz, stream=True, timeout=30)
        r.raise_for_status()
        with open(file_gz, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")
        break
    except requests.exceptions.RequestException as e:
        print(f"Download failed: {e}")
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)
        else:
            raise

print("Unzipping file...")
with gzip.open(file_gz, "rb") as f_in, open(file_jsonl, "wb") as f_out:
    f_out.write(f_in.read())
os.remove(file_gz)
print("Unzip complete.")

# ---------------------------------------------------------------------
# 2. Parse JSONL in a single pass
# ---------------------------------------------------------------------
print("Parsing JSONL file in a single pass...")
list_of_dicts = []
package_lookup = {}
resource_relations_list = []
resource_validation_list = []

with open(file_jsonl, "r", encoding="utf-8") as f:
    for line in f:
        tmp_data = json.loads(line)
        package_id_main = tmp_data.get("id")
        dataset_name_main = tmp_data.get("title")
        owner_main = tmp_data.get("organization", {}).get("name")

        resource_names_dict_jsonl = {}
        tmp_res = tmp_data.get("resources", [])
        if not tmp_res:
            continue

        for resource in tmp_res:
            if resource.get("datastore_active", True):
                url_res = resource.get("url", "")
                row_dict = {
                    "owner": tmp_data.get("organization", {}).get("name", None),
                    "package_id": resource.get("package_id", None),
                    "dataset_name": tmp_data.get("title", None),
                    "resource_id": resource.get("id", None),
                    "resource_name": resource.get("name", None),
                    "metadata_modified": resource.get("metadata_modified", None),
                    "size": resource.get("size", None),
                    "url": url_res,
                    "type": "upload" if "https://open.canada.ca" in url_res else "remote",
                }
                list_of_dicts.append(row_dict)

            res_id_jsonl = resource.get("id")
            res_name_jsonl = resource.get("name")
            if res_id_jsonl and res_name_jsonl:
                resource_names_dict_jsonl[res_id_jsonl] = res_name_jsonl

            if "relationship" in resource:
                resource_relations_list.append(resource)

            if "validation_status" in resource:
                resource_validation_list.append(resource)

        if package_id_main:
            package_lookup[package_id_main] = {
                "owner": owner_main,
                "dataset_name": dataset_name_main,
                "resource_names": resource_names_dict_jsonl,
            }
print("JSONL parsing complete.")

# ---------------------------------------------------------------------
# 3. Create initial DataFrames
# ---------------------------------------------------------------------
print("Creating initial DataFrames...")
list_of_res = pd.DataFrame(list_of_dicts)
df_relations_values = pd.DataFrame(resource_relations_list)
df_validation_values = pd.DataFrame(resource_validation_list)

# ---------------------------------------------------------------------
# 4. Process df_resource_views
# ---------------------------------------------------------------------
print("Processing df_resource_views...")
url_resource_views_csv = "https://open.canada.ca/data/dataset/c4c5c7f1-bfa6-4ff6-b4a0-c164cb2060f7/resource/a79f7297-9b20-427a-be79-d286daa92412/download/resources_resource_views.csv"
response = requests.get(url_resource_views_csv)
response.raise_for_status()
df_resource_views = pd.read_csv(StringIO(response.text))

list_of_res_subset = list_of_res[["resource_id", "owner", "dataset_name", "resource_name"]].copy()

df_resource_views = pd.merge(
    df_resource_views,
    list_of_res_subset,
    on="resource_id",
    how="left"
)

default_view_type = "Unknown"
df_resource_views["view_type"] = df_resource_views.get("view_type", pd.Series(dtype="object")).fillna(default_view_type)

columns_to_keep_and_order_views = [
    "owner",
    "package_id",
    "dataset_name",
    "resource_id",
    "resource_name",
    "id",
    "view_type",
]
df_resource_views = df_resource_views[columns_to_keep_and_order_views]

package_details_cache_local = {}
for idx, row in df_resource_views.iterrows():
    if pd.isna(row["owner"]) or pd.isna(row["dataset_name"]) or pd.isna(row["resource_name"]):
        package_id = row["package_id"]
        resource_id = row["resource_id"]

        if package_id not in package_details_cache_local:
            package_details = package_lookup.get(package_id, {})
            owner_from_lookup = package_details.get("owner")
            dataset_name_from_lookup = package_details.get("dataset_name")
            resource_names_from_lookup_dict = package_details.get("resource_names", {})
            package_details_cache_local[package_id] = (
                owner_from_lookup,
                dataset_name_from_lookup,
                resource_names_from_lookup_dict,
            )
        else:
            owner_from_lookup, dataset_name_from_lookup, resource_names_from_lookup_dict = package_details_cache_local[package_id]

        if pd.isna(row["owner"]) and owner_from_lookup is not None:
            df_resource_views.at[idx, "owner"] = owner_from_lookup

        if pd.isna(row["dataset_name"]) and dataset_name_from_lookup is not None:
            df_resource_views.at[idx, "dataset_name"] = dataset_name_from_lookup

        if pd.isna(row["resource_name"]) and resource_id in resource_names_from_lookup_dict:
            df_resource_views.at[idx, "resource_name"] = resource_names_from_lookup_dict[resource_id]

df_resource_views.to_csv("res_views.csv", index=False)
print("df_resource_views processed and saved.")

# ---------------------------------------------------------------------
# 5. Process df_relations_values
# ---------------------------------------------------------------------
print("Processing df_relations_values...")
df_relations_values[["name_translated_en", "name_translated_fr"]] = (
    df_relations_values["name_translated"].apply(lambda x: pd.Series(parse_name_translated(x)))
)

relationship_parsed_df = df_relations_values.apply(
    lambda row: process_relationships_and_resource_ids(row["relationship"], row["id"]),
    axis=1
)
df_relations_values = pd.concat([df_relations_values, relationship_parsed_df], axis=1)

columns_to_keep_relations = [
    "package_id",
    "id",
    "resource_type",
    "name_translated_en",
    "name_translated_fr",
    "rel_resource_type",
    "related_relationship",
    "related_url_en",
    "related_url_fr",
]
df_relations_values = df_relations_values[columns_to_keep_relations]
df_relations_values.to_csv("res_relations.csv", index=False)
print("df_relations_values processed and saved.")

# ---------------------------------------------------------------------
# 6. Process df_validation_values
# ---------------------------------------------------------------------
print("Processing df_validation_values...")
columns_to_keep_validation = [
    "format",
    "resource_type",
    "validation_status",
    "validation_timestamp",
    "id",
    "package_id",
]
df_validation_values = df_validation_values[columns_to_keep_validation]
df_validation_values = df_validation_values[df_validation_values["validation_status"].isin(["success", "failure"])]
df_validation_values.to_csv("res_validation_status.csv", index=False)
print("df_validation_values processed and saved.")

# ---------------------------------------------------------------------
# 7. Generate Mermaid.js charts
# ---------------------------------------------------------------------
print("Generating Mermaid.js charts...")
readme_path = "README.md"

view_type_counts = df_resource_views["view_type"].fillna("Unknown").value_counts()
pie_chart_data_view_type = [f"    \"{index}\": {value}" for index, value in view_type_counts.items()]
pie_chart_mermaid_view_type = f"""
```mermaid
---
config:
  theme: dark
---
pie showData title Resource View Types
{'\n'.join(pie_chart_data_view_type)}
```
"""
with open("resource_view_types_pie_chart.md", "w", encoding="utf-8") as f:
    f.write(pie_chart_mermaid_view_type)
print("Mermaid.js pie chart for 'view_type' saved to resource_view_types_pie_chart.md")
update_readme_section(
    readme_path,
    pie_chart_mermaid_view_type,
    "#### Resource View Types",
    "<!-- RESOURCE_VIEW_TYPES_CHART_START -->",
    "<!-- RESOURCE_VIEW_TYPES_CHART_END -->"
)
print("README.md updated with 'Resource View Types' chart.")

owner_counts = df_resource_views["owner"].fillna("Unknown").value_counts()
top_20_owners = owner_counts.head(20)
pie_chart_data_owner = [f"    \"{index}\": {value}" for index, value in top_20_owners.items()]
pie_chart_mermaid_owner = f"""
```mermaid
---
config:
  theme: dark
---
pie showData title Top 20 Orgs by View Count
{'\n'.join(pie_chart_data_owner)}
```
"""
with open("resource_owners_pie_chart.md", "w", encoding="utf-8") as f:
    f.write(pie_chart_mermaid_owner)
print("Mermaid.js pie chart for 'owner' saved to resource_owners_pie_chart.md")
update_readme_section(
    readme_path,
    pie_chart_mermaid_owner,
    "#### Top 20 Orgs by View Count",
    "<!-- TOP_20_OWNERS_CHART_START -->",
    "<!-- TOP_20_OWNERS_CHART_END -->"
)
print("README.md updated with 'Top 20 Orgs by View Count' chart.")

validation_status_counts = df_validation_values["validation_status"].value_counts()
pie_chart_data_validation_status = [f"    \"{index}\": {value}" for index, value in validation_status_counts.items()]
pie_chart_mermaid_validation_status = f"""
```mermaid
---
config:
  theme: dark
---
pie showData title Resource Validation Status
{'\n'.join(pie_chart_data_validation_status)}
```
"""
with open("resource_validation_status_pie_chart.md", "w", encoding="utf-8") as f:
    f.write(pie_chart_mermaid_validation_status)
print("Mermaid.js pie chart for 'Validation Status' saved to resource_validation_status_pie_chart.md")
update_readme_section(
    readme_path,
    pie_chart_mermaid_validation_status,
    "#### Resource Validation Status",
    "<!-- VALIDATION_STATUS_CHART_START -->",
    "<!-- VALIDATION_STATUS_CHART_END -->"
)
print("README.md updated with 'Resource Validation Status' chart.")

relations_type_counts = df_relations_values["related_relationship"].value_counts()
pie_chart_data_relations_counts = [f"    \"{index}\": {value}" for index, value in relations_type_counts.items()]
pie_chart_mermaid_relations = f"""
```mermaid
---
config:
  theme: dark
---
pie showData title Resource Relation Type
{'\n'.join(pie_chart_data_relations_counts)}
```
"""
with open("resource_relation_type_pie_chart.md", "w", encoding="utf-8") as f:
    f.write(pie_chart_mermaid_relations)
print("Mermaid.js pie chart for 'Resource Relation Type' saved to resource_relation_type_pie_chart.md")
update_readme_section(
    readme_path,
    pie_chart_mermaid_relations,
    "#### Resource Relation Type",
    "<!-- RESOURCE_RELATION_TYPE_CHART_START -->",
    "<!-- RESOURCE_RELATION_TYPE_CHART_END -->"
)
print("README.md updated with 'Resource Relation Type' chart.")

# ---------------------------------------------------------------------
# 8. Summaries (unique counts, date/time, etc.)
# ---------------------------------------------------------------------
date_str = datetime.now().strftime('%Y-%m-%d')
num_dept = list_of_res["owner"].nunique()
num_datasets = list_of_res["package_id"].nunique()
num_res = list_of_res["resource_id"].nunique()
count_open_canada = (list_of_res["type"] == "upload").sum()
count_remote_xload = (list_of_res["type"] == "remote").sum()

# ---------------------------------------------------------------------
# 9. Fetch datastore size from CKAN API (database-level info)
# ---------------------------------------------------------------------
ds_url = "https://open.canada.ca/data/en/api/3/action/datastore_info?id=3c911562-c541-463f-8cd4-490182cd57f9"
ds_resp = requests.get(ds_url)
ds_data = ds_resp.json()
ds_size_bytes = ds_data["result"]["meta"]["db_size"]
ds_size_readable = pretty_bytes(ds_size_bytes)

print("Setup steps complete. Ready to fetch datastore_info in parallel.")
# ---------------------------------------------------------------------
# 10. (Parallel) Fetch datastore info for each resource (with progress bar)
# ---------------------------------------------------------------------
print("Fetching datastore info for each resource in parallel (20 at a time). This may take a while...")

# Create new columns to store datastore info
list_of_res["ds_count"] = None
list_of_res["ds_fields"] = None
list_of_res["ds_size"] = None
list_of_res["ds_type_set"] = None
list_of_res["ds_label_set"] = None
list_of_res["ds_notes_set"] = None

# Use ThreadPoolExecutor to do calls in parallel (up to 20 workers)
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
# 11. Build DS_num_tracker_df (single row)
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
# 12. Append the new row to DS_num_tracker.csv, ensuring newest row on top
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
# 13. Save resources list to CSV
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
# 14. Save dictionary edit stats to CSV
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
# 15. Print output (useful for debugging or GH Action logs)
# ---------------------------------------------------------------------
print("=== DS_num_tracker (latest) ===")
print(DS_num_tracker_df.to_string(index=False))
print("\nCSV appended (or created) successfully.")


# ---------------------------------------------------------------------
# 16. create org stats
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
# 17. update README with resource counts
# ---------------------------------------------------------------------
resource_counts_table = build_resource_counts_table(list_of_res)
update_readme_resource_counts(readme_path, resource_counts_table)

# ---------------------------------------------------------------------
# 18. update README with dictionary radar chart
# ---------------------------------------------------------------------
dictionary_radar_chart = build_dictionary_radar_chart(list_of_res)
update_readme_dictionary_radar(readme_path, dictionary_radar_chart)

# ---------------------------------------------------------------------
# 19. Final display (useful for debugging or GH Action logs)
# ---------------------------------------------------------------------
print("\n--- Final DataFrames Head ---")
print("\ndf_resource_views.head():")
print(df_resource_views.head().to_string(index=False))
print("\ndf_relations_values.head():")
print(df_relations_values.head().to_string(index=False))
print("\ndf_validation_values.head():")
print(df_validation_values.head().to_string(index=False))
print("\norg_stats.head():")
print(org_stats.head().to_string(index=False))

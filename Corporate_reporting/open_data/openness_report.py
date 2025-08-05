
import requests
import os
import yaml
import gzip
import json
from io import BytesIO
import csv
import pandas as pd



# Fetch and parse the YAML file
url = "https://raw.githubusercontent.com/open-data/ckanext-canada/36375f75e8b77a00e1fb5054436f2f49c98ef9d7/ckanext/canada/schemas/presets.yaml"
response = requests.get(url)
yaml_content = response.text
parsed_yaml = yaml.safe_load(yaml_content)

# Create the lookup table for openness scores
openness_rating_lookup = {}
for preset in parsed_yaml.get('presets', []):
    if preset.get('preset_name') == 'canada_resource_format':
        for choice in preset.get('values', {}).get('choices', []):
            value = choice.get('value')
            if not value:
                continue
            openness_rating_lookup[value] = choice.get('openness_score', 1)
        break

# Download and decompress the gzipped JSON Lines file
gz_url = "https://open.canada.ca/static/od-do-canada.jsonl.gz"
gz_response = requests.get(gz_url)
gz_file = BytesIO(gz_response.content)

# Generate the CSV file
with open(os.path.join("Corporate_reporting", "open_data", "openness_report.csv"), 'w', newline='', encoding='utf-8-sig') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow([
        "Department Name Englist | Nom du ministère en français",
        "Title English | Titre en français",
        "URL",
        "Openness Rating | Cote d'ouverture",
        "Collection",
        "Jurisdiction",
        "Organization Name"
    ])

    with gzip.GzipFile(fileobj=gz_file, mode='rb') as f:
        for line in f:
            record = json.loads(line)

            """ # Filter for records of type "dataset"
            if record.get('type') != 'dataset':
                continue """

            # Calculate the openness rating
            score = 1
            for resource in record.get('resources', []):
                format_value = resource.get('format')
                if format_value in openness_rating_lookup:
                    score = max(score, openness_rating_lookup[format_value])

                if 'data_includes_uris' in resource.get('data_quality', []):
                    score = max(4, score)
                    if 'data_includes_links' in resource.get('data_quality', []):
                        score = max(5, score)

            # Extract and format the data
            org_title = record.get('organization', {}).get('title', ' | ')
            if isinstance(org_title, dict):
                org_title_en = org_title.get('en', '')
                org_title_fr = org_title.get('fr', '')
                org_title_formatted = f"{org_title_en} | {org_title_fr}"
            else:
                org_title_formatted = org_title

            record_title_translated = record.get('title_translated', {})
            record_title_en = record_title_translated.get('en', record_title_translated.get('en-t-fr', ''))
            record_title_fr = record_title_translated.get('fr', record_title_translated.get('fr-t-en', ''))
            record_title_formatted = f"{record_title_en} | {record_title_fr}"

            dataset_id = record.get('id', '')
            url_formatted = f"https://open.canada.ca/data/en/dataset/{dataset_id} | https://ouvert.canada.ca/data/fr/dataset/{dataset_id}"

            collection = record.get('collection', '')
            jurisdiction = record.get('jurisdiction', '')
            organization_name = record.get('organization', {}).get('name', '')

            # Write the row to the CSV
            csv_writer.writerow([
                org_title_formatted,
                record_title_formatted,
                url_formatted,
                score,
                collection,
                jurisdiction,
                organization_name
            ])



import pandas as pd
import numpy as np
import requests, tempfile, gzip, sys, json, traceback


def catalogue_download(batch_size=500):
    url = "https://open.canada.ca/static/od-do-canada.jsonl.gz"
    try:
        # Download and save the file to a temporary location
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False) as f:
                for chunk in r.iter_content(chunk_size=64 * 1024):
                    f.write(chunk)
                temp_file_path = f.name

        # Read and yield records in batches
        with gzip.open(temp_file_path, 'rb') as fd:
            batch = []
            for line in fd:
                try:
                    record = json.loads(line.decode('utf-8'))
                    batch.append(record)
                    if len(batch) >= batch_size:
                        yield batch
                        batch = []
                except json.JSONDecodeError as e:
                    print(f"Skipping malformed line: {e}")

            if batch:
                yield batch

    except requests.RequestException as e:
        print(f"Download error: {e}")
        sys.exit(1)
    except GeneratorExit:
        pass
    except Exception as e:
        traceback.print_exc()
        print('Error reading downloaded file')
        sys.exit(1)
        
def open_dataset ():
    dataset = []
    for line in catalogue_download():
        for record in line:
            keys_dataset = list(record.get('title_translated').keys())  
            # Extraction of Dataset with no resource to track main dataset page visits or downloads
            
            dataset_record ={
                        "record_id"   : record['id'],
                        "resource_id"   : "No resource",
                        "Dataset_creation"  : record['metadata_created'].split('T')[0],
                        "Resource_creation"  : record['metadata_created'].split('T')[0],
                        "Resource_modification"  : record['metadata_modified'].split('T')[0],
                        "dataset_title"       : record['title_translated'][keys_dataset[0]],
                        "titre_du_jeu_de_donnees"       : record['title_translated'][keys_dataset[1]],                
                        "resource_title"       : "No resources covered",
                        "titre_du_ressource"       : "Aucune ressource couverte",
                        "institution_EN" : record['organization']['title'].split("|")[0],
                        "institution_FR" : record['organization']['title'].split("|")[-1]
            }
            dataset.append(dataset_record)
            # Extraction of Dataset resource if any to track resource page visits or downloads
            for res in record['resources']:
                keys_resource = list(res.get('name_translated').keys()) 
                try:
                    # Will attempt to create details of resources 
                    dataset_record ={
                        "record_id"   : record['id'],
                        "resource_id"   : res['id'],
                        "Dataset_creation"  : record['metadata_created'].split('T')[0],
                        "Resource_creation"  : res['created'].split('T')[0],
                        "Resource_modification"  : res['metadata_modified'].split('T')[0],
                        "dataset_title"       : record['title_translated'][keys_dataset[0]],
                        "titre_du_jeu_de_donnees"       : record['title_translated'][keys_dataset[1]],                
                        "resource_title"       : res['name_translated'][keys_resource[0]],
                        "titre_du_ressource"       : res['name_translated'][keys_resource[1]],
                        "institution_EN" : record['organization']['title'].split("|")[0],
                        "institution_FR" : record['organization']['title'].split("|")[-1]
            
                }
                except Exception as e:
                    print (f'Dataset title : {record.get('title_translated')},  Resource title: {res.get('name_translated') }')
                dataset.append(dataset_record)
    return dataset
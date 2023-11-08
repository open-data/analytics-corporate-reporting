import gzip
import json
import sys
import requests
import os
import io
from collections import defaultdict
from datetime import datetime
import pandas as pd
import tempfile

pd_data = []
current_date = datetime.now().strftime('%a %d %b %Y')
row = [current_date]
total = 0
all_pd = [current_date]
pd_count = [current_date]
headers = ["date"]
pd_col = ["date", "transition", "transition_deputy", "parliament_report",
          "parliament_committee", "parliament_committee_deputy", "total"]
pd_list = [elm for elm in pd_col if not elm in ["date", "total"]]
df_column = []


def download():
    url = "https://open.canada.ca/static/od-do-canada.jsonl.gz"
    r = requests.get(url, stream=True)
    f = tempfile.NamedTemporaryFile(delete=False)
    for chunk in r.iter_content(1024 * 64):
        f.write(chunk)
    f.close()
    records = []
    fname = f.name
    records = []
    try:
        with gzip.open(fname, 'rb') as fd:
            for line in fd:
                records.append(json.loads(line.decode('utf-8')))
                if len(records) >= 500:
                    yield (records)
                    records = []
        if len(records) > 0:
            yield (records)
            records = []
    except GeneratorExit:
        pass
    except:
        import traceback
        traceback.print_exc()
        print('error reading downloaded file')
        sys.exit(0)


def filedow(reqURL):
    try:
        req = requests.get(reqURL)
        filename = reqURL.split("/")[-1]
        filename = filename.split(".")[0]
        filename = "_".join(filename.split("-"))
        headers.append(filename)
        if req.status_code == 200:
            df = pd.read_csv(io.StringIO(
                req.content.decode("utf-8")), low_memory=False)
            file_path = os.path.join("resources", "".join([filename, ".csv"]))
            df.to_csv(file_path, index=False, encoding="utf-8")
        return filename, len(df)
    except Exception as e:
        print(e)


def csv_file_create(csv_file, col_head):
    if not os.path.isfile(csv_file):
        print("no file should create")
        df = pd.DataFrame(columns=col_head)
        df.to_csv(csv_file, index=False, encoding="utf-8")


def add_record(row, csv_file, col_head):
    csv_file_create(csv_file, col_head)
    df = pd.read_csv(csv_file)
    if row[0] in df['date'].values:
        print('record exist no overwriting ')
        return
    else:

        df.loc[len(df.index)] = row
        df.sort_values(by='date', axis=0, ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
    df.to_csv(csv_file, index=False)


def add_record_plus(data, csv_file, col_head):
    csv_file_create(csv_file, col_head)
    df = pd.read_csv(csv_file)
    for row in data:
        df.loc[len(df.index)] = row
        df.sort_values(by=['date','pd_type'], axis=0, ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
    df.to_csv(csv_file, index=False)


def main():
    total = 0
    # Non Structured pd types downloads and count
    for records in download():
        # package_id, date_created = [], []
        for record in records:
            try:
                pd_data.append([record["owner_org"], record["organization"],
                                record["title"], record["type"], record["collection"],])
            except IndexError as e:
                print(e)
            except Exception as e:
                print(e)
    df = pd.DataFrame(pd_data, columns=[
        "owner_org", "organization", "title", "type", "collection"])
    for elmt in pd_list:
        elmt = df[df['collection'] == elmt]
        total += len(elmt)
        pd_count.append(len(elmt))
    pd_count.append(total)
    current_date = datetime.now().strftime('%a %d %b %Y')

    # Structured pd types downloads and count
    with open("links.txt", "r") as f:
        Urls = [line.rstrip('\n') for line in f]
    f.close

    total = 0  # reusing the same variable

    for url in Urls:
        filename, len_df = filedow(url)
        total += len_df
        row.append(len_df)
        df_column.append([current_date, filename, len_df])
    for i,elmt in enumerate(pd_list):
        print(pd_count[i+1])
        df_column.append([current_date, elmt, pd_count[i+1]])
    print(df_column)
    headers.append("total")
    row.append(total)
    total_all = row[-1] + pd_count[-1]
    all_pd.extend([row[-1], pd_count[-1], total ])
    

# adding records to csv files
    add_record(row, "structure_pd.csv", headers)
    add_record(pd_count, "nonstruc_pd.csv", pd_col)
    add_record(all_pd, "all_pd.csv", ["date","structured_pd", "non_structured_pd", "total"])
    add_record_plus(df_column, "structure_pd_new.csv",
                    ["date", "pd_type", "pd_count"])

if __name__ == '__main__':
    main()

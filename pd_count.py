import gzip
import json
import sys
import requests
import os
import io
from collections import defaultdict
from datetime import *
import pandas as pd
import tempfile


class Proactive_disclosure:
    def __init__(self, current_date):
        self.current_date = current_date
        self.pd_list = ["transition", "transition_deputy", "parliament_report",
                        "parliament_committee", "parliament_committee_deputy"]
        self.headers = ["date"]
        self.unstruct_pd_count = [self.current_date]
        self.df_pd_org = pd.DataFrame()
        self.df_melt = pd.DataFrame()
        self.df_unpd_org = pd.DataFrame()
        self.record_added = False

    def download(self):
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

    # Structured PDs download
    def filedow(self, reqURL):
        try:
            req = requests.get(reqURL)
            filename = reqURL.split("/")[-1]
            filename = filename.split(".")[0]
            filename = "_".join(filename.split("-"))
            self.headers.append(filename)
            if req.status_code == 200:
                df = pd.read_csv(io.StringIO(
                    req.content.decode("utf-8")), low_memory=False)
                if filename != "adminaircraft":                  
                    df_agg = df.groupby(
                        "owner_org").size().reset_index(name="count")
                    df_agg["type"] = filename
                    self.df_pd_org = pd.concat(
                        [self.df_pd_org, df_agg], ignore_index=True)
                   
            return filename, len(df)
        except Exception as e:
            print(e)

    # Create CSV file if it does not exist (initialize)
    def csv_file_create(self, csv_file, col_head):
        if not os.path.isfile(csv_file):
            print("no file should create")
            df = pd.DataFrame(columns=col_head)
            df.to_csv(csv_file, index=False, encoding="utf-8")

    def add_record(self, row, csv_file, col_head, combined=False):
        self.csv_file_create(csv_file, col_head)
        df = pd.read_csv(csv_file)
        if row[0] in df['date'].values:
            print('record exist no overwriting ')
            self.record_added = False
            return
        else:
            df.loc[len(df.index)] = row
            df.sort_values(by='date', axis=0, ascending=False, inplace=True)
            df.reset_index(drop=True, inplace=True)
        if not combined:
            header = col_head.remove("date")
            df_unpivot = pd.melt(df, id_vars=['date'], value_vars=header)
            self.df_melt = pd.concat(
                [self.df_melt, df_unpivot], ignore_index=True)
        df.to_csv(csv_file, index=False)
        self.record_added = True
        return

    def unstruct_pd(self):  # Non Structured pd types downloads and count
        total = 0
        non_struc_pd = []
        pd_col = ["date"]
        pd_col.extend(self.pd_list)
        for records in self.download():
            for record in records:
                try:
                    non_struc_pd.append([record["organization"]["name"], record["organization"]["title"],
                                         record["title"], record["type"], record["collection"],])
                except IndexError as e:
                    print(e)
                except Exception as e:
                    print(e)
        df = pd.DataFrame(non_struc_pd, columns=[
            "owner_org", "organization", "title", "type", "collection"])        
        for elmt in self.pd_list:
            elmt_df = df[df['collection'] == elmt]
            elmt_agg = elmt_df.groupby(
                        "owner_org").size().reset_index(name="count")
            elmt_agg['type'] = elmt
            self.df_unpd_org = pd.concat(
                        [self.df_unpd_org, elmt_agg], ignore_index=True)
            total += len(elmt_df)
            self.unstruct_pd_count.append(len(elmt_df))
        pd_col.extend(["total"])        
        self.unstruct_pd_count.append(total)
        self.add_record(self.unstruct_pd_count, "nonstruc_pd.csv", pd_col)
        return total

    def struct_pd(self):
        pd_name = []
        row = [self.current_date]
        total = 0       
        with open("links.txt", "r") as f:
            Urls = [line.rstrip('\n') for line in f]
        f.close
        for url in Urls:
            filename, len_df = self.filedow(url)
            if filename != "adminaircraft":
                pd_name.append(filename)
            total += len_df
            row.append(len_df)
        pd_name.sort()
        self.headers.append("total")
        row.append(total)
        self.add_record(row, "structure_pd.csv", self.headers)
        return total

    def pd_combined(self):
        all_pd = [self.current_date]
        struc_pd_total = self.struct_pd()  # Structured pds total
        unstruc_pd_total = self.unstruct_pd()  # unstructured pds total
        total_all = struc_pd_total + unstruc_pd_total
        all_pd.extend([struc_pd_total, unstruc_pd_total, total_all])
        if self.record_added:
            self.df_melt.sort_values(
                by='date', axis=0, ascending=False, inplace=True)
            #print (self.df_melt.head())
            self.df_melt.rename(columns = {"variable":"pd_type", "value": "pd_count"}, inplace=True)
            print (self.df_melt.head())
            self.df_melt = self.df_melt.query(f'pd_type != "total"')
            self.df_melt.to_csv("unpivoted_pd.csv",
                                encoding="utf-8", index=False)
        self.add_record(all_pd, "all_pd.csv", [
            "date", "structured_pd", "non_structured_pd", "total"], True)

    def pd_per_dept(self):
        all_pd_df = pd.concat(
                        [self.df_unpd_org, self.df_pd_org], ignore_index=True)        
        df_dpt = all_pd_df.pivot(index="owner_org", columns="type")        
        df_dpt = df_dpt['count'].reset_index()
        df_dpt.columns.name = None
        df_dpt.fillna(0, inplace=True)
        df_dpt = df_dpt.astype({'transition':'int', 'transition_deputy':'int', 'parliament_report':'int',
                        'parliament_committee':'int', 'parliament_committee_deputy':'int','ati_all': 'int', 'ati_nil': 'int', 'briefingt': 'int', 'contracts': 'int', 'contracts_nil': 'int', 'contractsa': 'int', 'dac': 'int', 'grants': 'int', 'grants_nil': 'int',
                                'hospitalityq': 'int', 'hospitalityq_nil': 'int', 'qpnotes': 'int', 'reclassification': 'int', 'reclassification_nil': 'int', 'travela': 'int', 'travelq': 'int', 'travelq_nil': 'int', 'wrongdoing': 'int'})
        df_dpt.to_csv("pd_per_dept.csv", encoding='utf-8', index=False)


def main():
    current_date = date.today().strftime('%Y-%m-%d')
    pd_obj = Proactive_disclosure(current_date)
    pd_obj.pd_combined()
    pd_obj.pd_per_dept()


if __name__ == '__main__':
    main()

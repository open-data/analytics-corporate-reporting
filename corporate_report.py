import gzip
import json
import sys
import requests
import os
import io
from collections import defaultdict
from datetime import date, datetime
import pandas as pd
import tempfile
from ckanapi import RemoteCKAN
from dateutil import parser


class Corporate:
    def __init__(self):
        self.offset = "0"
        self.limit = 10000

    def catalogue_download(self):
        url = "https://open.canada.ca/static/od-do-canada.jsonl.gz"
        r = requests.get(url, stream=True)
        f = tempfile.NamedTemporaryFile(delete=False)
        for chunk in r.iter_content(1024 * 64):
            f.write(chunk)
        f.close()
        records = []
        fname = f.name
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
     # Dataset generation

    def datasets_generation(self):
        report = []
        error_report = []
        for records in self.catalogue_download():

            for record in records:

                try:
                    package_id = [res['package_id']
                                  for res in record['resources']]
                    datastore_active = [res['datastore_active']
                                        for res in record['resources']]
                    report.append([record['organization']['title'].split("|")[0], record['type'], record['id'], record['metadata_created'].split('T')[
                                  0], record['metadata_modified'].split('T')[0], len(package_id), datastore_active, any(datastore_active), all(datastore_active), record['collection']])
                except IndexError:
                    error_report.append([record['organization']['title'].split("|")[
                                        0], record['organization']['created'].split('T')[0], record['type'], record['collection']])
                    continue
        df = pd.DataFrame(report, columns=['organization', 'type', 'package id', 'metadata_created', 'metadata_modified',
                          'number of ressources', 'datastore_active', 'any_datastore_active', 'all_datastore_active', 'collection'])
        return df

    # Downloads the most updated openness score do data
    def openness_dow(self):
        # records = []
        fields = ["_id", "Department Name Englist | Nom du ministere en francais",
                  "Title English | Titre en francais", "URL", "Openness Rating | Cote d'ouverture"]
        record_agg = []
        while True:
            ckan = RemoteCKAN('https://open.canada.ca/data')
            result = ckan.action.datastore_search(
                resource_id="88c73a5e-905e-4c78-b440-c5d5c3acfea8",
                limit=self.limit,
                offset=int(self.offset),
                fields=fields

            )
            for record in result['records']:
                records = [record["_id"], record["Department Name Englist | Nom du ministere en francais"], record["Title English | Titre en francais"],
                           record["URL"], record["Openness Rating | Cote d'ouverture"]]
                record_agg.append(records)

            if (int(result['total']) <= int(self.offset)+self.limit):
                print(
                    f"The total record of {result['total']} and offset is {self.offset}")
                break
            self.offset = result['_links']['next'].split('=')[-1]
        df = pd.DataFrame(record_agg, columns=fields)
        return df

    # Downloads and calculates total visits and downloads within a fiscal year
    def get_fy_download(self):
        data = defaultdict()
        today = date.today()
        try:
            url = "https://open.canada.ca/data/dataset/2916fad5-ebcc-4c86-b0f3-4f619b29f412/resource/02a92b0f-b26d-4fbd-9601-d27651703715/download/opendataportal.siteanalytics.totalmonthlyusage.bilingual.csv"
            r = requests.get(url, stream=True).content
            df_dow = pd.read_csv(io.StringIO(r.decode("UTF-8")))
            #year_annee	month_mois	visits_visites	downloads_telechargements
            # df_dow.rename(columns={'year / année': "year", 'month / mois': "month", 'visits / visites': "visits",
            #                        'downloads / téléchargements': "downloads"}, inplace=True)
            if today.month < 4:
                start_year = today.year - 1
            else:
                start_year = today.year
          # start_year = int(fiscal_year.split("-")[0])
            down_list = df_dow.query(
                f'(year_annee == {start_year} & month_mois > 3) | (year_annee == {start_year + 1} & month_mois < 4)')
            data["visits_visites"] = sum(down_list['visits_visites'])
            data["downloads_telechargements"] = sum(down_list['downloads_telechargements'])
            return data

        except Exception as e:
            print(e)

    # Processes the full data and info to extract datasets created within a specific fiscal year.
    # It also generates Non geospatial dataset, Non geospatial and no federated dataset, datasets with at least one resource API enabled,
    def corporate_report(self, csv_file):
        corporate_metrics = []
        today = date.today()
        if today.month > 3:
            # fiscal_year = str(today.year) + '-'+str(today.year + 1)[-2:]
            start_date = parser.parse(str(today.year) + "-04-01")
            end_date = today

        else:
            start_date = parser.parse(str(today.year-1) + "-04-01")
            end_date = today
            # fiscal_year = str(today.year - 1) + '-'+str(today.year)[-2:]

        # df = pd.read_csv('open_data_&_info.csv')
        df = self.datasets_generation()
        df_fiscal = df[(df['metadata_created'] >= str(start_date)) & (df['metadata_created'] <= str(
            end_date)) & (df['type'] == "dataset")]  # & df["any_datastore_active"]==True
        total = df_fiscal.shape[0]
        # federated_dt = df_fiscal.query('collection == "federated" ')
        df_openness = self.openness_dow()
        df_openness['ID'] = df_openness.URL.str.rsplit(
            '/', n=1, expand=True)[1]

        # Fiscal year datasets with openess rating
        merged_df = df_fiscal.merge(
            df_openness, how='inner', left_on='package id', right_on='ID')
        full_data_col = ['organization', 'type', 'package id', 'Title English | Titre en francais', "Openness Rating | Cote d'ouverture",
                         'metadata_created', 'number of ressources', 'any_datastore_active', 'collection']
        fiscal_op = merged_df[full_data_col]

        fiscal_openess_score = fiscal_op.rename(
            columns={"Openness Rating | Cote d'ouverture": "Openness_Rating"})
        fiscal_openess_score.Openness_Rating = fiscal_openess_score.Openness_Rating.astype(
            int)
        Non_geo = fiscal_openess_score.query(
            'collection != "fgp" & collection !="geogratis"')
        Non_geo_good = Non_geo.query('Openness_Rating >=3')
        API_enable = fiscal_openess_score.query('any_datastore_active == True')
        eligible_API = Non_geo.query('collection != "federated"')
        data = self.get_fy_download()
        corporate_metrics = [date.today().strftime('%Y-%m-%d'), start_date.strftime('%Y-%m-%d'), end_date, total, Non_geo.shape[0], round(100*Non_geo_good.shape[0]/Non_geo.shape[0], 2), API_enable.shape[0],
                             round(100*API_enable.shape[0]/eligible_API.shape[0], 2), data['downloads_telechargements'], data['visits_visites']]
        return corporate_metrics

    def csv_file_create(self, csv_file, col_head):
        if not os.path.isfile(csv_file):
            print("no file should create")
            df = pd.DataFrame(columns=col_head)
            df.to_csv(csv_file, index=False, encoding="utf-8")

    def add_record(self, row, csv_file, col_head):
        self.csv_file_create(csv_file, col_head)
        df = pd.read_csv(csv_file)
        if row[0] in df['Date'].values:
            print('record exist no overwriting ')
            return
        else:
            df.loc[len(df.index)] = row
            df.sort_values(by='Date', axis=0, ascending=False, inplace=True)
            df.reset_index(drop=True, inplace=True)
        df.to_csv(csv_file, index=False)


def main():
    cr = Corporate()  # "2022-04-01", "2023-03-31"
    header = ["Date", "From", "To", "number of datasets", "Non geospatial", "% of non-geospatial with 3+ rating",
              "number of API enabled datasets", "% of API enable datasets", "Totals downloads", "Total visits"]
    cr.datasets_generation()
    row = cr.corporate_report('open_data_&_info.csv')
    cr.add_record(row, "corporate_report.csv", header)


if __name__ == '__main__':
    main()

# encoding: utf-8

"""OG Analytics Reporting GA 4."""
from datetime import *
import os
import tempfile
import time
import gzip
import json
import sys
import csv
import requests
import unicodecsv
import codecs
from collections import defaultdict
import ckanapi
from ckanapi.errors import CKANAPIError
import yaml
import pandas as pd
import math
from openpyxl.utils.exceptions import IllegalCharacterError
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    Filter,
    FilterExpression,
    RunReportRequest,
    OrderBy,
    FilterExpressionList
)
import down_files
# import rename_files
# import archive
import onetime_concat
import resource_patch

def write_csv(filename, rows, header=None):
    outf = open(filename, 'wb')
    outf.write(codecs.BOM_UTF8)
    writer = unicodecsv.writer(outf)

    if header:
        writer.writerow(header)
    for row in rows:
        writer.writerow(row)


def read_csv(filename):
    content = []
    with open(filename, encoding='UTF-8') as f:
        reader = csv.reader(f)
        firstrow = next(reader)
        # firstrow[0] = firstrow[0].lstrip(codecs.BOM_UTF8)
        content.append(firstrow)
        for x in reader:
            content.append(x)
    return content


def simplify_lang(titles):
    return {
        'en': titles.get('en', titles.get('en-t-fr', '')),
        'fr': titles.get('fr', titles.get('fr-t-en', '')),
    }
# https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/installed-py
# https://developers.google.com/analytics/devguides/reporting/core/v4/basics
# CLIENT_SECRETS_PATH = 'client_secrets.json' # Path to client_secrets.json file.
# VIEW_ID = '<REPLACE_WITH_VIEW_ID>'


def initialize_analyticsreporting(client_secrets_path):

    client = BetaAnalyticsDataClient.from_service_account_file(
        client_secrets_path)
    return client

# GA API response parser and returs data in list and total rows for pagination
def parseReport(response, dimension_name='pagePath', metric_name='eventCount'):
    data, rowCount = [], 0    
    for rowIdx, row in enumerate(response.rows):        
        dim, mtr = [], []
        if dimension_name:
            for i, dimension_value in enumerate(row.dimension_values):
                if response.dimension_headers[i].name == dimension_name:
                    dim.append(dimension_value.value)
        for i, metric_value in enumerate(row.metric_values):
            if response.metric_headers[i].name == metric_name:
                mtr.append(metric_value.value)                
        if dimension_name:
            data.append(dim + mtr)
        else:
            data.extend(mtr)
    rowCount = response.row_count
    return data, rowCount


class DatasetDownload():
    def __init__(self, start_date, end_date, og_type, ga, property_id, conf_file=None):       
        ga_rmote_ckan = "https://open.canada.ca/data"
        self.ga = ga
        self.property_id = property_id
        # self.file = os.path.join(self.ga_tmp_dir, 'od-do-canada.jl.gz')
        self.site = ckanapi.RemoteCKAN(ga_rmote_ckan)
        self.start_date = start_date
        self.end_date = end_date
        self.og_type = og_type
        self.read_orgs()
        self.country = yaml.full_load(open('country_region.yml', 'r', encoding='utf-8'))

    
    def __delete__(self):
        if not self.file:
            if self.download_file:
                os.unlink(self.download_file)
                print('temp file deleted', self.download_file)

   
    def read_orgs(self):
        count = 0
        while count <= 5:
            try:
                print('reading organizations...')
                orgs = self.site.action.organization_list(all_fields=True)
                break
            except ckanapi.errors.CKANAPIError:
                count += 1
                print('Error read org list from open.canada.ca')
                time.sleep(2)
        self.orgs = {}
        self.org_name2id = {}
        self.org_id2name = {}
        for rec in orgs:
            title = rec['title'].split('|')
            self.orgs[rec['id']] = title
            self.org_name2id[rec['name']] = rec['id']
            self.org_id2name[rec['id']] = [rec['name'], rec['title']]
        assert (len(self.orgs) > 100)

# reads the catalogue file 
    def read_portal(self, stats, og_type=None):
        self.ds = {}
        self.org_count = defaultdict(int)
        og_type = og_type
        count = 0
        for records in self.download():
            count += len(records)
            for rec in records:
                if not stats.get(rec['id']):
                    continue
               # if self.og_type == 'info':
                if og_type == 'info':
                    if rec['type'] != 'info':
                        stats.pop(rec['id'])  # not open info
                        continue
                self.ds[rec['id']] = {'title_translated': rec['title_translated'],
                                      'owner_org': rec['owner_org']}
                self.org_count[rec['owner_org']] += 1

# Screen and page views per month and per dataset
    def getVisitStats(self): 
        self.set_catalogue_file()        
        offset = 0
        limit = 10000
        stats = defaultdict(int)        
        while True:            
            response = self.getRawReport(offset, limit, "page_view")            
            data, rowCount = parseReport(
                response, 'pagePath', 'screenPageViews')
            for [url, count] in data:                
                id = url.split('/')[-1]
                if id[:8] == 'dataset?':
                    continue
                id = id.split('&')[0]
                id = id.strip()
                if len(id) != 36:
                    continue  # make sure it is an UUID
                stats[id] += int(count)

            if (rowCount <= limit or (rowCount - offset) <= limit):
                break
            else:
                offset += limit
        stats = dict(stats)     
        self.dump(stats, True)

# Downloads per month and dataset (either info or data)
    def getStats(self): #, og_type
        self.set_catalogue_file()
        #self.og_type = og_type
        offset = 0        
        limit = 10000
        stats = defaultdict(int)
        while True:
            response = self.getRawReport(offset, limit, "file_download")           
            data, rowCount = parseReport(response)
            for [url, count] in data:
                id = url.split('/dataset/')[-1]
                id = id.split('/')[0]                
                if len(id) != 36:
                    print(f"not an UUID {id} : {count}")
                    continue  # make sure it is an UUID
                stats[id] += int(count)
            if (rowCount <= limit or (rowCount - offset) <= limit):
                break
            else:
                offset += limit
        stats = dict(stats)        
        self.dump(stats)
        self.dump_info(stats)      
        
# genrates statisc file for TOP info downloads and last month info download
    def dump_info(self, data):
        self.read_portal(data, og_type = 'info')
        y, m, d = self.start_date.split('-')
        sheets = []
        all_rec = [[id, c] for id, c in data.items()]
        all_rec.sort(key=lambda x: x[1], reverse=True)
        # top100 = heapq.nlargest(100, top100, key=lambda x: x[1])
        rows = [['id','title', 'titre', 'department',
                 'ministere', 'downloads_telechargements', 
                 'month_mois', 'year_annee']]
        for rec_id, count in all_rec:
            rec = self.ds.get(rec_id, None)
            if not rec:
                # deleted, skip it
                continue
            else:
                rec_title = simplify_lang(rec['title_translated'])
                org_id = rec['owner_org']
            [_, org_title] = self.org_id2name.get(org_id)
            org_title = org_title.split('|')
            org_title = [x.strip() for x in org_title]
            rows.append([rec_id, rec_title['en'], rec_title['fr'],
                         org_title[0], org_title[1], count, m, y])
            if len(rows) == 21:
                write_csv(os.path.join("GA_TMP_DIR", "".join(["openDataPortal.siteAnalytics.top20Info", m, y,".csv"])), rows)
        write_csv(os.path.join("GA_TMP_DIR",
                  "od_ga_All_Info_download.csv"), rows)
        
# genrates statisc files for views and downloads of datasets last month (Top 100 downlads and all downloads/dataset)
    def dump(self, data, ignore_deleted=False):
        self.read_portal(data)               
        ds = defaultdict(int)        
        deleted_ds = {}       
        count = 0
        for id, c in data.items():
            rec = self.ds.get(id, None)
            if (not rec) and ignore_deleted:
                deleted_ds[id] = True
                continue
            if not rec:
                count +=1   
                print(id, ' deleted', count)
                continue               
            else:
                org_id = rec['owner_org']
            ds[org_id] += c
            
        if ignore_deleted:
            for k, v in deleted_ds.items():
                data.pop(k)
            deleted_ds = {}
        self.save_csv( data, ds, deleted_ds, ignore_deleted)

# Save dataset download and view records to csv files. 
    def save_csv(self, data, org_stats, deleted_ds, isVisit=False):
        sheets = []
        rows = []
        y, m, d = self.start_date.split("-")       
        all_rec = [[id, c] for id, c in data.items()]
        all_rec.sort(key=lambda x: x[1], reverse=True)        

        rows = [['id','title', 'titre', 'department',
                 'ministere', 'downloads_telechargements', 
                 'month_mois', 'year_annee']]        
        if isVisit:
            rows[0][5] = "visits_visites"
        for rec_id, count in all_rec:
            rec = self.ds.get(rec_id, None)
            if not rec:
                # continue
                if rec_id in deleted_ds.keys():
                    rec_title = deleted_ds[rec_id]['title_translated']
                    rec_title = simplify_lang(rec_title)
                    org_id = deleted_ds[rec_id]['org_id']
                else:
                    continue            
            else:
                rec_title = simplify_lang(rec['title_translated'])

                org_id = rec['owner_org']
            [_, org_title] = self.org_id2name.get(org_id)
            org_title = org_title.split('|')
            org_title = [x.strip() for x in org_title]
            rows.append([rec_id, rec_title['en'], rec_title['fr'],
                         org_title[0], org_title[1], count, m, y])
            if not isVisit and len(rows) == 101:
                write_csv( os.path.join("GA_TMP_DIR", "".join(["openDataPortal.siteAnalytics.top100Datasets.bilingual", m, y,".csv"])), rows)
        if isVisit:
            write_csv(os.path.join(
                "GA_TMP_DIR",  ".".join(["openDataPortal.siteAnalytics.visits", "csv"])), rows)
        else:
            write_csv(os.path.join("GA_TMP_DIR", ".".join(["openDataPortal.siteAnalytics.downloads","csv"])), rows)

#Get raw report from GA4 API filtered by screenPageViews or downloads
    def getRawReport(self, offset, limit, eventName):
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[
                Dimension(name="pagePath")
            ],
            metrics=[Metric(name="screenPageViews"),
                     Metric(name="eventCount")],
            date_ranges=[
                DateRange(start_date=self.start_date, end_date=self.end_date)],
            dimension_filter=FilterExpression(
                and_group=FilterExpressionList(
                    expressions=[

                        FilterExpression(
                            filter=Filter(
                                field_name='eventName',
                                string_filter=Filter.StringFilter(
                                    value=eventName)
                            )
                        ),

                        FilterExpression(

                            or_group=FilterExpressionList(
                                expressions=[
                                    FilterExpression(
                                        filter=Filter(
                                            field_name='pagePath',
                                            string_filter=Filter.StringFilter(match_type="BEGINS_WITH",
                                                                              value='/data/en/dataset/',
                                                                              case_sensitive=True)
                                        )
                                    ),
                                    FilterExpression(
                                        filter=Filter(
                                            field_name='pagePath',
                                            string_filter=Filter.StringFilter(match_type="BEGINS_WITH",
                                                                              value='/data/fr/dataset/',
                                                                              case_sensitive=True)
                                        )

                                    )
                                ]
                            )
                        )

                    ]
                )

            ),
            order_bys=[OrderBy(
                desc=True,
                metric=OrderBy.MetricOrderBy(metric_name="screenPageViews")
            )],
            limit=limit,
            offset=offset,
        )
        return self.ga.run_report(request)
    
# Download the catalogue
    def download(self): 
        records = []              
        if not self.file:
            print("downloading new catalogue")
            # dataset http://open.canada.ca/data/en/dataset/c4c5c7f1-bfa6-4ff6-b4a0-c164cb2060f7
            url = 'http://open.canada.ca/static/od-do-canada.jl.gz'
            r = requests.get(url, stream=True)
            f = tempfile.NamedTemporaryFile(delete=False)
            for chunk in r.iter_content(1024 * 64):
                f.write(chunk)
            f.close()
            self.download_file = f.name

        fname = self.file or f.name
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

# Monthly downloads and visits stat
    def monthly_usage(self, csv_file):
        total, downloads = 0, 0
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            # dimensions=[Dimension(name="PagePath")],
            metrics=[Metric(name="sessions")
                     ],
            date_ranges=[
                DateRange(start_date=self.start_date, end_date=self.end_date)],

            limit=10000,
            offset=0,
        )
        while True:
            response = self.ga.run_report(request)
            data, rowCount = parseReport(response, None, 'sessions')
            for eCount in data:
                total += int(eCount)
            if (rowCount <= request.limit or (rowCount - request.offset) <= request.limit):
                break
            request.offset += request.limit
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[Dimension(name="eventName"),
                        Dimension(name="PagePath")
                        ],
            metrics=[Metric(name="eventCount"),
                     Metric(name="eventValue")],
            date_ranges=[
                DateRange(start_date=self.start_date, end_date=self.end_date)],
            dimension_filter=FilterExpression(
                filter=Filter(
                    field_name='eventName',
                    string_filter=Filter.StringFilter(value='file_download')
                )
            ),

            limit=10000,
            offset=0,
        )
        while True:
            response = self.ga.run_report(request)
            data, rowCount = parseReport(response, None, 'eventCount')
            for eCount in data:
                downloads += int(eCount)
            if (rowCount <= request.limit or (rowCount - request.offset) <= request.limit):                
                break
            request.offset += request.limit

        # Checking if the report is up to date and updating otherwise
        [year, month, _] = self.end_date.split('-')
        data = read_csv(csv_file)
        if int(data[1][0]) == int(year) and int(data[1][1]) == int(month):
            print('entry exists, no overwriting')
            return
        row = [year, month, total, downloads]
        data[0] = ['year / année', 'month / mois',
                   'visits / visites', 'downloads / téléchargements']
        data.insert(1, row)
        write_csv(csv_file, data)
 
 # Visits by country stat
    def by_country(self, csv_file):
        country_name = self.country.get('country_region').get('country')
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[Dimension(name="country")],
            metrics=[Metric(name="sessions")],
            date_ranges=[
                DateRange(start_date=self.start_date, end_date=self.end_date)],
            order_bys=[OrderBy(
                desc=True,
                metric=OrderBy.MetricOrderBy(metric_name="sessions")
            )],
            limit=100000,
            offset=0,
        )
        response = self.ga.run_report(request)
        data, rowCount = parseReport(response, 'country', 'sessions')
        total = 0  # should be initialized with cummul upto 2023-07-01
        country_fr = [c for c in country_name.values()]
        country_en = [c for c in country_name.keys()]
        assert (len(country_en) == len(country_fr))
        country_dict = {country_en[i]: country_fr[i]
                        for i in range(len(country_en))}
        total_visits = 0
        for country, visits in data:
            total_visits += int(visits)
        for row in data:
            c = row[0]
            if c == '(not set)':
                row[0] = 'unknown / Inconnu'
            elif c in country_en:
                c_fr = country_dict.get(c, c)
                row[0] = c + u' | ' + c_fr
            else:
                print(f'{row[0]} ,{row[1]}')
            row[1] = int(row[1])

        for c, count in data:
            total += count
        data = [[country, int(count), "%.2f" % ((count*100.0)/total) + '%']
                for [country, count] in data]
        self.hist_visits(data, csv_file)

    # Visits by region stat
    def by_region(self, csv_file):
        region_name = self.country.get('country_region').get('region')
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[Dimension(name="region")],
            metrics=[Metric(name="sessions"),
                     Metric(name="eventValue")],
            date_ranges=[
                DateRange(start_date=self.start_date, end_date=self.end_date)],
            dimension_filter=FilterExpression(
                filter=Filter(
                    field_name='country',
                    string_filter=Filter.StringFilter(match_type="BEGINS_WITH",
                                                      value='Canada',
                                                      case_sensitive=False)
                )

            ),
            order_bys=[OrderBy(
                desc=True,
                metric=OrderBy.MetricOrderBy(metric_name="sessions")
            )],
            limit=100000,
            offset=0,

        )
        response = self.ga.run_report(request)
        data, rowCount = parseReport(response, 'region', 'sessions')

        total = 0  # should be initialized with cummul upto 2023-07-01
        data = [[region, int(count)] for [region, count] in data]
        for c, count in data:
            total += count
        region_fr = [r for r in region_name.values()]
        region_en = [r for r in region_name.keys()]
        assert (len(region_en) == len(region_fr))
        region_dict = {region_en[i]: region_fr[i]
                       for i in range(len(region_en))}
        data = [[region if region != ('(not set)' or "") else 'unknown / Inconnu', int(
            count), "%.2f" % ((count*100.0)/total) + '%'] for [region, count] in data]
        for row in data:
            r = row[0]
            if r == '(not set)':
                row[0] = 'unknown / Inconnu'
            elif r:
                r_fr = region_dict.get(r, r)
                row[0] = r + u' | ' + r_fr
        self.hist_visits(data, csv_file)

    # To include historical visits from last reporting
    def hist_visits(self, data, csv_file):
        df = pd.DataFrame(data, columns=['region / Région', 'visits / Visites',
                          'percentage of total visits / Pourcentage du nombre total de visites'])
        old_df = pd.read_csv(csv_file)
        last_region = [c for c in old_df['region / Région']]
        new_region = [c for c in df['region / Région']]
        new_region_visit = {}
        old_region_visit = {}
        for i in range(len(df)):
            new_region_visit[df.iloc[i]['region / Région']
                             ] = df.iloc[i]['visits / Visites']
        for i in range(len(old_df)):
            old_region_visit[old_df.iloc[i]['region / Région']
                             ] = old_df.iloc[i]['visits / Visites']

        for c in last_region:
            if c in new_region:
                old_region_visit[c] += new_region_visit[c]

        for c in new_region:
            if c not in last_region:
                old_region_visit[c] = new_region_visit[c]

        new_df = pd.DataFrame.from_dict(
            old_region_visit, orient='index', columns=['visits / Visites'])
        new_df.reset_index(inplace=True)
        new_df.rename(columns={'index': 'region / Région'}, inplace=True)
        total = sum(new_df['visits / Visites'])
        per_tage = ["%.2f" % ((count*100.0)/total) +
                    '%' for count in new_df['visits / Visites']]
        new_df['percentage of total visits / Pourcentage du nombre total de visites'] = per_tage
        new_df.sort_values(by='visits / Visites', axis=0,
                           ascending=False, inplace=True)
        new_df.to_csv(csv_file, encoding="utf-8", index=False)

# set catalogue file name
    def set_catalogue_file(self):
        y, m, d = self.end_date.split('-')    
        self.file = ''.join(
            ["GA_STATIC_DIR", '\od-do-canada.', y, m, d, '.jl.gz'])
        if not os.path.exists(self.file):
            raise Exception('not found ' + self.file)
        
   # generate catalogue      
    def by_org(self, org_stats, csv_file):
        rows = []
        header = ['department', 'ministere',
                  'datasets', 'jeux_de_donnees', 'total']
        for org_id, count in org_stats.items():
            [title_en, title_fr] = self.orgs.get(org_id, ['', ''])
            name = self.org_id2name[org_id][0]
            link_en = 'http://open.canada.ca/data/en/dataset?organization=' + name
            link_fr = 'http://ouvert.canada.ca//data/fr/dataset?organization=' + name
            rows.append([title_en, title_fr, link_en, link_fr, count])
        rows.sort(key=lambda x: x[0])
        write_csv(csv_file, rows, header)

# Generates dataset released by organization by month for the last 12 month
    def by_org_month(self, csv_month_file, csv_file):
        self.set_catalogue_file()
        # need to use cataloge file downloaded at last day of prev month
        # need to update the last column, insert before last column
        # insert row if new org is created
        org_stats = defaultdict(int)
        total_num = 0
        total_new = 0
        for records in self.download():
            total_num += len(records)
            for rec in records:
                org_stats[rec['owner_org']] += 1
        org_stats = dict(org_stats)
        self.by_org(org_stats, csv_file)
        ds = read_csv(csv_month_file)
        header = ds[0]
        total = ds[-1]
        ds = ds[1:-1]
        en_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                     'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        fr_months = ['janv.', 'févr.', 'mars', 'avril', 'mai',
                     'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']
        [y, m, d] = self.end_date.split('-')
        en_header = en_months[int(m)-1]+'-'+y
        fr_header = fr_months[int(m)-1]+'-'+y
        new_header = en_header + ' / ' + fr_header
        if header[-2] == new_header:
            print('exists ', new_header)
            return
        header[0] = 'department_ministere'
        header[1] = 'datasets_jeux_de_donnees'
        header[-1] = 'total'
        header.insert(-1, new_header)
        # need to rotate, merge column 2, and 3, update the title
        del header[2]

        def prior_header(h):
            hs = h.split(' / ')
            if len(hs) == 2:  # new header
                return ' '.join(['prior to', hs[0], ' / Avant', hs[1]])
            else:  # old english header
                hs = h.split('-')
                mi = en_months.index(hs[0].strip())
                nh = fr_months[mi] + '-' + hs[1]
                return ' '.join(['prior to', h, ' / Avant', nh])
        header[2] = prior_header(header[3])
        for i in range(3, len(header)-2):
            h = header[i]
            if len(h.split(' / ')) == 1:  # translate
                hs = h.split('-')
                mi = en_months.index(hs[0].strip())
                nh = fr_months[mi] + '-' + hs[1]
                header[i] = h + ' / ' + nh

        # update exists one
        exists = {}
        for row in ds:
            # get org shortname
            name = row[1].split('=')[-1]
            # some orgs got new shortforms
            name = {
                'ceaa-acee': 'iaac-aeic',
                'neb-one': 'cer-rec',
            }.get(name, name)
            org_id = self.org_name2id[name]
            exists[org_id] = True
            titles = self.orgs.get(org_id, ['', ''])
            title = titles[0] + ' | ' + titles[1]
            link_en = 'http://open.canada.ca/data/en/dataset?organization=' + name
            link_fr = 'http://ouvert.canada.ca//data/fr/dataset?organization=' + name
            link = link_en + ' | ' + link_fr
            row[0] = title
            row[1] = link
            count = org_stats.get(org_id, 0)
            var = count - int(row[-1])
            row[-1] = count
            row.insert(-1, var)
            pr, c = int(row[2]), int(row[3])
            del row[2]
            row[2] = pr + c
            total_new += row[2]
        del total[2]
        total[2] = total_new

        # New org
        for org_id, count in org_stats.items():
            if org_id in exists:
                continue
            titles = self.orgs.get(org_id, ['', ''])
            title = titles[0] + ' | ' + titles[1]
            name = self.org_id2name[org_id][0]
            link_en = 'http://open.canada.ca/data/en/dataset?organization=' + name
            link_fr = 'http://ouvert.canada.ca//data/fr/dataset?organization=' + name
            link = link_en + ' | ' + link_fr
            row = [0 for i in range(len(header))]
            row[0] = title
            row[1] = link
            row[-2] = row[-1] = count
            ds.append(row)
        ds.sort(key=lambda x: x[0])
        var = total_num - int(total[-1])
        total[-1] = total_num
        total.insert(-1, var)
        ds.append(total)
        write_csv(csv_month_file, ds, header)


def report(client_secret_path, property_id, start, end, va=None, og_config_file=None):
    og_type = va
    client = initialize_analyticsreporting(client_secret_path)
    ds = DatasetDownload(start, end, og_type, client,
                         property_id, og_config_file)
    ds.set_catalogue_file()   
    ds.getVisitStats()
    time.sleep(2)
    ds.getStats()
    time.sleep(2)
    ds.monthly_usage(os.path.join(
        "GA_TMP_DIR", 'openDataPortal.siteAnalytics.totalMonthlyUsage.bilingual.csv'))
    time.sleep(2)
    ds.by_country(os.path.join(
        "GA_TMP_DIR", 'openDataPortal.siteAnalytics.internationalUsageBreakdown.bilingual.csv'))
    time.sleep(2)
    ds.by_region(os.path.join(
        "GA_TMP_DIR", 'openDataPortal.siteAnalytics.provincialUsageBreakdown.bilingual.csv'))
    ds.by_org_month(os.path.join("GA_TMP_DIR", 'openDataPortal.siteAnalytics.datasetsByOrgByMonth.bilingual.csv'),
                    os.path.join("GA_TMP_DIR", 'openDataPortal.siteAnalytics.datasetsByOrg.bilingual.csv'))
 
def main():
    down_files.csv_download()    
    down_files.archive_download() 
    t0 = time.time() 
    today = date.today()
    last_day = today - timedelta(days=today.day)
    first_day = last_day-timedelta(days=last_day.day-1)
    last_day = last_day.strftime('%Y-%m-%d')
    first_day = first_day.strftime('%Y-%m-%d')
    report("credentials.json", "359132180", first_day, last_day)  
    onetime_concat.concat_hist() 
    down_files.archive_files(last_day)
    #resource_patch.resources_update()    
    time_m = math.floor((time.time()-t0)/60)
    time_s = (time.time()-t0) - time_m*60
    print(f"All done in {time_m} min and {time_s:.2f} s")

if __name__ == '__main__':
    main()

# encoding: utf-8

"""OG Analytics Reporting GA 4."""

import argparse
import os
import tempfile
import time
import gzip
import json
import urllib
import sys
import csv
import requests
import unicodecsv
import codecs
from collections import defaultdict

import ckanapi
from ckanapi.errors import CKANAPIError

import configparser
import psycopg2
import traceback
import openpyxl
import heapq
import re
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

def cleanup_illegal_characters(rows):
    for row in rows:
        for cell in rows:
            if (isinstance(cell, str)):
                cell = re.sub(r'[\000-\010]|[\013-\014]|[\016-\037]', '', cell)
    return rows

def write_xls(filename, sheets):
    book = openpyxl.Workbook()

    for sheet in sheets:
        ws = book.create_sheet(title=sheet.get('name', 'sheet 1'))
        try:
            for row in sheet.get('data',[]):
                ws.append(row)
        except IllegalCharacterError as e:
            pass

        cols =  [col for col in ws.columns]
        widths = sheet.get('col_width', {})
        for k,v in widths.iteritems():
            ws.column_dimensions[cols[k][0].column_letter].width = v
    try:
        sheet1 = book.get_sheet_by_name("Sheet")
        book.remove_sheet(sheet1)
    except:
        pass
    book.save(filename)

def write_csv(filename, rows, header=None):
    outf=open(filename, 'wb')
    outf.write(codecs.BOM_UTF8)
    writer = unicodecsv.writer(outf)

    if header:
        writer.writerow(header)
    for row in rows:
        writer.writerow(row)

def read_csv(filename):
    content=[]
    with open(filename, encoding='UTF-8') as f:
        reader = csv.reader(f)
        firstrow = next(reader)
        #firstrow[0] = firstrow[0].lstrip(codecs.BOM_UTF8)
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
#CLIENT_SECRETS_PATH = 'client_secrets.json' # Path to client_secrets.json file.
#VIEW_ID = '<REPLACE_WITH_VIEW_ID>'


def initialize_analyticsreporting(client_secrets_path):
 
  # Parse command-line arguments.
#  parser = argparse.ArgumentParser(
#      formatter_class=argparse.RawDescriptionHelpFormatter,
#      parents=[tools.argparser])
  # flags = parser.parse_args(['--noauth_local_webserver'])
#  flags = parser.parse_args([])

  # Set up a Flow object to be used if we need to authenticate.
  #os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = client_secrets_path

  # Build the service object.
  #client = BetaAnalyticsDataClient()
#http=http, discoveryServiceUrl=DISCOVERY_URI)
  client = BetaAnalyticsDataClient.from_service_account_file(client_secrets_path)
  return client

def parseReport(response, dimension_name='pagePath', metric_name='eventCount'):
    data, rowCount = [], 0
    
    for rowIdx, row in enumerate(response.rows):
        
        dim, mtr = [],[]
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
    def __init__(self,start_date, end_date,og_type, ga, property_id, conf_file):
        ga_tmp_dir = os.environ['GA_TMP_DIR']
        ga_rmote_ckan = os.environ['GA_REMOTE_CKAN']
        self.ga = ga
        self.property_id = property_id
        self.file = os.path.join(ga_tmp_dir, 'od-do-canada.jl.gz')
        self.site = ckanapi.RemoteCKAN(ga_rmote_ckan)
        self.start_date = start_date
        self.end_date = end_date
        self.og_type = og_type

        self.read_orgs()

        user, passwd, host, db = self.read_conf(conf_file)
        db = db.split('?')[0]
        try:
            self.conn = psycopg2.connect(
                database=db, user=user,
                password=passwd, host=host, port="5432")
        except:
            import traceback
            traceback.print_exce()
            print ("Opened database failed")
            sys.exit(-1)

    def read_conf(self,filename):
        config = configparser.ConfigParser()
        config.read(filename)
        psql_conn_str = config.get('app:main', 'sqlalchemy.url')
        import re
        r = re.match(r'^postgresql://(.*):(.*)@(.*)/(.*)', psql_conn_str)
        return (r.group(1), r.group(2), r.group(3), r.group(4))

    def get_deleted_dataset(self, id):
        cur = self.conn.cursor()
        cur.execute('''SELECT a.id, c.value, a.owner_org from package a,
                    package_extra c
                    where a.state='deleted' 
                        and a.id=c.package_id and c.key='title_translated'; ''')
        rows = cur.fetchall()
        for row in rows[:1]:
            id, title, org = row[0], row[1], row[2]
            return (title, org)

        return (None, None)

    def __delete__(self):
        if not self.file:
            if self.download_file:
                os.unlink(self.download_file)
                print('temp file deleted', self.download_file)

    def get_details(self, id):
        try:
            target_pkg = self.site.action.package_show(id=id)
        except:
            target_pkg = None
        return target_pkg

    def read_orgs(self):
        count = 0
        while count <=5:
            try:
                print ('reading organizations...')
                orgs = self.site.action.organization_list(all_fields=True)
                break
            except ckanapi.errors.CKANAPIError:
                count += 1
                print ('Error read org list from open.canada.ca')
                time.sleep(2)
        self.orgs = {}
        self.org_name2id = {}
        self.org_id2name = {}

        for rec in orgs:
            title = rec['title'].split('|')
            self.orgs[rec['id']] = title
            self.org_name2id[rec['name']] = rec['id']
            self.org_id2name[rec['id']] = [ rec['name'], rec['title'] ]
        assert(len(self.orgs)>100)
        print ('total orgs ', len(self.orgs))

    def read_portal(self, stats):
        self.ds = {}
        self.org_count = defaultdict(int)
        count = 0
        for records in self.download():
            count += len(records)
            print ('read records ', count, ' ',  len(self.ds))
            for rec in records:
                if not stats.get(rec['id']):
                    continue
                if self.og_type =='info':
                    if rec['type'] != 'info':
                        stats.pop(rec['id']) # not open info 
                        continue
                self.ds[rec['id']] = {'title_translated':rec['title_translated'],
                                      'owner_org':rec['owner_org']}
                self.org_count[rec['owner_org']] += 1
            
    def getVisitStats(self, og_type):
        self.set_catalogue_file(self.end_date) 
        self.og_type = og_type
        offset = 0
        limit = 100000
        stats = defaultdict(int)
        while True:
            response = self.getRawVisitReport(offset)
            data, rowCount = parseReport(response, 'pagePath', 'screenPageViews')
            for [url, count] in data:
                id = url.split('/')[-1]
                if id[:8] == 'dataset?': continue
                id = id.split('&')[0]
                id = id.strip()
                if len(id)!=36: continue #make sure it is an UUID
                stats[id] += int(count)
            if (rowCount<=limit or (rowCount - offset)<=limit):
                print ('Done ', offset, len(stats))
                break
            else:
                offset += limit
                print (offset)
        stats = dict(stats)
        self.read_portal(stats)

        self.dump(stats, True)

    def getStats(self, og_type):
        self.set_catalogue_file(self.end_date)
        self.og_type = og_type
       
        offset = 0
        limit = 100000
        stats = defaultdict(int)
        while True:
            response = self.getRawReport(offset)
            data, rowCount = self.parseReport(response)
            for [url, count] in data:
                id = url.split('/dataset/')[-1]
                id = id.split('/')[0]
                if len(id)!=36: continue #make sure it is an UUID
                stats[id] += int(count)
            if (rowCount<=limit or (rowCount - offset)<=limit):
                print( 'Done ', offset, len(stats))
                break
            else:
                offset += limit
                print(offset)
        stats = dict(stats)
        self.read_portal(stats)

        if self.og_type == 'info':
            self.dump_info(stats)
        else:
            self.dump(stats)

    def dump_info(self, data):
        sheets =[]
        top100 = [[id,c] for id,c in data.iteritems()]
        top100 = heapq.nlargest(100, top100, key=lambda x:x[1])
        rows = [['ID / Identificateur',
                 'Title English / Titre en anglais',
                 'Title French / Titre en français', 
                 "Department Name English / Nom du ministère en anglais",
                 "Department Name French / Nom du ministère en français",
                 "number of downloads / nombre de téléchargements"]]
        for rec_id,count in top100:
            #get top20
            if len(rows)>=21:
                break
            rec = self.ds.get(rec_id, None)
            if not rec:
                #deleted, skip it
                continue
            else:
                rec_title = simplify_lang(rec['title_translated'])
                org_id = rec['owner_org']
            [_, org_title] = self.org_id2name.get(org_id)
            org_title = org_title.split('|')
            org_title = [x.strip() for x in org_title]
            rows.append( [rec_id, rec_title['en'], rec_title['fr'],
                          org_title[0], org_title[1], count])
        rows.append([])
        rows.append([self.start_date, self.end_date])
        rows = cleanup_illegal_characters(rows)
        sheet1 = {'name':'Top 20 Information',
                  'data': rows,
                   'col_width':{0:40, 1:50, 2:50, 3:50, 4:50, 5:40}  # col:width
                   }
        sheets.insert(0, sheet1)
        ga_tmp_dir = os.environ['GA_TMP_DIR']
        write_xls(os.path.join(ga_tmp_dir, 'downloads_info.xls'), sheets)

    def dump(self, data, ignore_deleted=False):
        #further reduce to departments
        ds = defaultdict(int)
        sheets = defaultdict(list)
        deleted_ds = {}
        for id,c in data.iteritems():
            rec = self.ds.get(id, None)
            if (not rec) and ignore_deleted:
                deleted_ds[id] = True
                continue
            if not rec:
                print( id, ' deleted')
                rec_title, org_id = self.get_deleted_dataset(id)
                deleted_ds[id] = {'title_translated':rec_title,
                                  'org_id':org_id}
                print (rec_title, org_id)
            else:
                org_id = rec['owner_org']
            ds[org_id] += c

            sheet = sheets[org_id]
            sheet.append(id)
        if ignore_deleted:
            for k,v in deleted_ds.iteritems():
                data.pop(k)
            deleted_ds = {}
        
        rows = []
        for k,v in ds.iteritems():
            title = self.orgs.get(k, ['', ''])
            if len(title) ==1:
                title.append(title[0])
            rows.append([title[0].strip(), title[1].strip(),v]) 
        rows.sort(key=lambda x: -x[2])
        header = ["Department Name English / Nom du ministère en anglais",
                  "Department Name French / Nom du ministère en français",
                  "number of downloads / nombre de téléchargements"]

        #write_csv('/tmp/a.csv', rows, header)
        
        #now save to xls
        self.saveXls(sheets, data, ds, deleted_ds, ignore_deleted)

    def saveXls(self, org_recs, data, org_stats, deleted_ds, isVisit=False):
        sheets =[]
        rows =[]
        for k, [name, title] in self.org_id2name.iteritems():
            count = org_stats.get(k, 0)
            if count == 0:
                continue
            title = title.split('|')
            rows.append( [name, title[0].strip(), title[1].strip(), count])
        rows.sort(key=lambda x: -x[3])
        rows.insert(0, ['Abbreviation / Abréviation', 
                        "Department Name English / Nom du ministère en anglais",
                        "Department Name French / Nom du ministère en français",
                        "Number of downloads / Nombre de téléchargements"])
        if isVisit:
            rows[0][3] = "Number of visits / Nombre de visites"
        rows = cleanup_illegal_characters(rows)
        sheet1 = {'name':'Summary by departments',
                  'data': rows,
                   'col_width':{0:26, 1:50, 2:50, 3:40}  # col:width
                   }

        #get top100
        top100 = [[id,c] for id,c in data.iteritems()]
        top100 = heapq.nlargest(100, top100, key=lambda x:x[1])
        rows = [['ID / Identificateur',
                 'Title English / Titre en anglais',
                 'Title French / Titre en français', 
                 "Department Name English / Nom du ministère en anglais",
                 "Department Name French / Nom du ministère en français",
                 "number of downloads / nombre de téléchargements"]]
        if isVisit:
            rows[0][5] = "Number of visits / Nombre de visites"
        for rec_id,count in top100:
            rec = self.ds.get(rec_id, None)
            if not rec:
                rec_title = deleted_ds[rec_id]['title_translated']
                rec_title = simplify_lang(json.loads(rec_title))
                org_id = deleted_ds[rec_id]['org_id']
            else:
                rec_title = simplify_lang(rec['title_translated'])
                org_id = rec['owner_org']
            [_, org_title] = self.org_id2name.get(org_id)
            org_title = org_title.split('|')
            org_title = [x.strip() for x in org_title]
            rows.append( [rec_id, rec_title['en'], rec_title['fr'],
                          org_title[0], org_title[1], count])
        rows = cleanup_illegal_characters(rows)
        sheet2 = {'name':'Top 100 Datasets',
                  'data': rows,
                   'col_width':{0:40, 1:50, 2:50, 3:50, 4:50, 5:40}  # col:width
                   }
        ga_tmp_dir = os.environ['GA_TMP_DIR']
        write_csv(os.path.join(ga_tmp_dir, "od_ga_top100.csv"), rows)

        for org_id, recs in org_recs.iteritems():
            rows = []
            title = self.org_id2name.get(org_id, ['unknown'])[0]
            for rec_id in recs:
                rec = self.ds.get(rec_id, None)
                if not rec:
                    rec_title = deleted_ds[rec_id]['title_translated']
                    rec_title = simplify_lang(json.loads(rec_title))
                else:
                    rec_title = simplify_lang(rec['title_translated'])
                count = data.get(rec_id)
                rows.append( [rec_id, rec_title['en'], rec_title['fr'], count])
            rows.sort(key=lambda x:-x[3])
            rows.insert(0, ['ID / Identificateur',
                            'Title English / Titre en anglais',
                            'Title French / Titre en français',
                            'Number of downloads / Nombre de téléchargements'])
            if isVisit:
                rows[0][3] = "Number of visits / Nombre de visites"
            rows.append(['total','','', org_stats.get(org_id)])
            rows = cleanup_illegal_characters(rows)
            sheets.append({'name':title,
                           'data': rows,
                           'col_width':{0:40, 1:50, 2:50, 3:40}
                           }
                          )
        sheets.sort(key=lambda x: x['name'])
        sheets.insert(0, sheet2)
        sheets.insert(0, sheet1)
        write_xls(os.path.join(ga_tmp_dir, 'od_ga_downloads.xls'), sheets)
        
   
    def getRawReport(self, offset):
        request = RunReportRequest(
        property=f"properties/{self.property_id}",
        dimensions= [Dimension(name="eventName"),
                        Dimension(name="pagePath")
                        ],
        metrics=[Metric(name="eventValue"), 
                    Metric(name="eventCount")],
        date_ranges=[DateRange(start_date= self.start_date, end_date=self.end_date)]
            , 
        dimension_filter  = FilterExpression(
            filter = Filter (
                field_name ='eventName',
                string_filter = Filter.StringFilter(value = 'page_view')
            )

        ),
        order_bys =[OrderBy(
        desc = True,
        metric = OrderBy.MetricOrderBy(metric_name = "eventCount")
        )],   
        limit = 100000,
        offset = offset,
           
        )
        return self.ga.run_report(request)  
    def parseReport(self, response):
        return parseReport(response, 'ga:pagePath', 'ga:totalEvents')
        
    def getRawVisitReport( self, offset):        
        request = RunReportRequest(
        property=f"properties/{self.property_id}",
        dimensions= [Dimension(name="pagePath")],
        metrics=[Metric(name="sessions"), 
                Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date= self.start_date, end_date=self.end_date)]
        , 
        dimension_filter  = FilterExpression(
            or_group= FilterExpressionList(
                 expressions=[
                    FilterExpression(            
                filter = Filter (
                    field_name ='pagePath',
                    string_filter = Filter.StringFilter(match_type="BEGINS_WITH", 
                                                        value = '/data/en/dataset/', 
                                                        case_sensitive=True)
                )
                    ),
                FilterExpression(            
                filter = Filter (
                    field_name ='pagePath',
                    string_filter = Filter.StringFilter(match_type="BEGINS_WITH", 
                                                        value = '/data/fr/dataset/', 
                                                        case_sensitive=True)
                )

            )
                    ]
                )
            ),
        order_bys =[OrderBy(
        desc = True,
        metric = OrderBy.MetricOrderBy(metric_name = "screenPageViews")
        )],   
        limit = 100000,
        offset = offset,        
        )
        return self.ga.run_report(request)  

    def download(self):
        if not self.file:
            # dataset http://open.canada.ca/data/en/dataset/c4c5c7f1-bfa6-4ff6-b4a0-c164cb2060f7
            url='http://open.canada.ca/static/od-do-canada.jl.gz'
            r = requests.get(url, stream=True)

            f = tempfile.NamedTemporaryFile(delete=False)
            for chunk in r.iter_content(1024 * 64):
                    f.write(chunk)
            f.close()
            self.download_file = f.name

        records = []
        fname = self.file or f.name
        try:
            with gzip.open(fname, 'rb') as fd:
                for line in fd:
                    records.append(json.loads(line.decode('utf-8')))
                    if len(records) >= 500:
                        yield (records)
                        records = []
            if len(records) >0:
                yield (records)
                records = []
        except GeneratorExit:
            pass
        except:
            import traceback
            traceback.print_exc()
            print('error reading downloaded file')
            sys.exit(0)
        
    def monthly_usage(self, csv_file):
        total, downloads = 0, 0        
        request = RunReportRequest(
        property=f"properties/{self.property_id}",
        dimensions= [ Dimension(name="PagePath")],
        metrics=[Metric(name="sessions"),
                 Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date= self.start_date, end_date=self.end_date)]
        ,
        order_bys =[OrderBy(
        desc = True,
        metric = OrderBy.MetricOrderBy(metric_name = "screenPageViews")
        )],   
        limit = 100000,
        offset = 0,        
    )
        while True:
            response = self.ga.run_report(request)
            data, rowCount = parseReport(response, None, 'sessions')             
            for eCount in data: 
                    total += int(eCount)
            if (rowCount<=request.limit or (rowCount - request.offset)<=request.limit):
               # print(f'row count {rowCount}, limit {request.limit} and offset {request.offset} with total:{total}')
                break
            request.offset += request.limit      

        request = RunReportRequest(
        property=f"properties/{self.property_id}",
        dimensions= [Dimension(name="eventName"),
                     Dimension(name="PagePath")
                     ],
        metrics=[Metric(name="eventCount"), 
                 Metric(name="eventValue")],
        date_ranges=[DateRange(start_date= self.start_date, end_date=self.end_date)]
         , 
        dimension_filter  = FilterExpression(
            filter = Filter (
                field_name ='eventName',
                string_filter = Filter.StringFilter(value = 'file_download')
            )

        ),
                
        limit = 100000,
        offset = 0,
       
    )
        response = self.ga.run_report(request)
        data, rowCount = parseReport(response, None, 'eventCount')         
        for eCount in data:
            downloads += int(eCount)
        #print(f"Visits:{total} and Downloads:  {downloads}")
        # Checking if the report is up to date and updating otherwise
        [year, month, _] = self.end_date.split('-')
        data = read_csv(csv_file)        
        if int(data[1][0]) == int(year) and int(data[1][1]) == int(month):
            print ('entry exists, no overwriting')
            return
        row = [year, month, total, downloads]        
        data[0] = ['year / année', 'month / mois', 'visits / visites', 'downloads / téléchargements']
        data.insert(1,row)
        write_csv(csv_file, data)
    
    def by_country(self, csv_file):
        request = RunReportRequest(
        property=f"properties/{self.property_id}",
        dimensions= [Dimension(name="country")],
        metrics=[Metric(name="sessions")],
        date_ranges=[DateRange(start_date= '2023-04-01', end_date=self.end_date)]
            ,      
        order_bys =[OrderBy(
            desc = True,
            metric = OrderBy.MetricOrderBy(metric_name = "sessions")
        )],   
        limit = 100000,
        offset = 0,

            
        )
        response = self.ga.run_report(request) 
        data, rowCount = parseReport(response, 'country', 'sessions')            
        total = 0 # should be initialized with cummul upto 2023-07-01
        country_fr = u'''Canada
            États-Unis
            Inde
            France
            Royaume Unis
            Chine
            Allemagne
            Australie
            Brésil
            Inconnu
            Russie
            Pakistan
            Algérie
            Espagne
            Mexique
            Japon
            Philippines
            Corée du Sud
            Italie
            Émirats Arabe Unis
            Turquie
            Maroc
            Ukraine
            Hollande
            Arabie Saoudite
            Iran
            Taiwan
            Nigéria
            Hong Kong
            Vietnam
            Indonésie
            Belgique
            Singapour
            Bangladesh
            Suisse
            Malaysie
            Égypte
            Colombie
            Tunisie
            Thaïlande
            Afrique du Sud
            Pologne
            Irlande
            Roumanie
            Suède
            Kenya
            Israël
            Nouvelle-Zélande
            Argentine
            Grèce
            Portugal
            Liban
            Tchétchénie
            Côte d’Ivoire
            Danemark
            Autriche
            Norvège
            Cameroon
            Finlande
            Pérou
            Qatar
            Chili
            Hongrie
            Sri Lanka
            Jordanie
            Bulgarie
            Koweit
            Kazakhstan
            Iraq
            Jamaïque
            Serbie
            Sénégal
            Népal
            Vénézuela
            Ghana
            Croatie
            Syrie
            Slovaquie
            Costa Rica
            Équateur
            République Dominicaine
            Soudan
            Biélorussie
            Éthiopie
            Oman
            Haïti
            Moldavie
            Lithuanie
            Trinidad & Tobago
            Tanzanie
            Albanie
            Maurice
            Bénin
            Congo - Kinshasa
            Luxembourg
            Madagascar
            Togo
            Ouganda
            Géorgie
            Slovénie'''
        country_en = u'''Canada
            United States
            India
            France
            United Kingdom
            China
            Germany
            Australia
            Brazil
            Unknown
            Russia
            Pakistan
            Algeria
            Spain
            Mexico
            Japan
            Philippines
            South Korea
            Italy
            United Arab Emirates
            Turkey
            Morocco
            Ukraine
            Netherlands
            Saudi Arabia
            Iran
            Taiwan
            Nigeria
            Hong Kong
            Vietnam
            Indonesia
            Belgium
            Singapore
            Bangladesh
            Switzerland
            Malaysia
            Egypt
            Colombia
            Tunisia
            Thailand
            South Africa
            Poland
            Ireland
            Romania
            Sweden
            Kenya
            Israel
            New Zealand
            Argentina
            Greece
            Portugal
            Lebanon
            Czechia
            Côte d’Ivoire
            Denmark
            Austria
            Norway
            Cameroon
            Finland
            Peru
            Qatar
            Chile
            Hungary
            Sri Lanka
            Jordan
            Bulgaria
            Kuwait
            Kazakhstan
            Iraq
            Jamaica
            Serbia
            Senegal
            Nepal
            Venezuela
            Ghana
            Croatia
            Syria
            Slovakia
            Costa Rica
            Ecuador
            Dominican Republic
            Sudan
            Belarus
            Ethiopia
            Oman
            Haiti
            Moldova
            Lithuania
            Trinidad & Tobago
            Tanzania
            Albania
            Mauritius
            Benin
            Congo - Kinshasa
            Luxembourg
            Madagascar
            Togo
            Uganda
            Georgia
            Slovenia'''
        country_fr = [c.strip() for c in country_fr.split('\n')]
        country_en = [c.strip() for c in country_en.split('\n')]
        assert( len(country_en)==len(country_fr))
        country_dict = { country_en[i]:country_fr[i] for i in range(len(country_en)) }

        for row in data:
            c = row[0]
            if c == '(not set)':
                row[0] = 'unknown / Inconnu'
            else:
                c_fr = country_dict.get(c, c)
                row[0] = c + u' | ' + c_fr
            row[1] = int(row[1])

        for c, count in data:
            total += count        
        data = [ [country, int(count), "%.2f"%((count*100.0)/total) + '%' ] for [country, count] in data ]
        data.insert(0,['region / Région', 'visits / Visites', 'percentage of total visits / Pourcentage du nombre total de visites'])
        write_csv(csv_file, data)

    def by_region(self, csv_file):
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions= [Dimension(name="region")],
            metrics=[Metric(name="sessions"), 
                     Metric(name="eventValue")],
            date_ranges=[DateRange(start_date= '2023-04-01', end_date=self.end_date)]
             , 
            dimension_filter  = FilterExpression(
                filter = Filter (
                    field_name ='country',
                    string_filter = Filter.StringFilter(match_type="BEGINS_WITH", 
                                                            value = 'canada', 
                                                            case_sensitive=False)
                )

            ),
            order_bys =[OrderBy(
            desc = True,
            metric = OrderBy.MetricOrderBy(metric_name = "sessions")
            )],        
            limit = 100000,
            offset = 0,
           
        )
        response = self.ga.run_report(request)
        data, rowCount = parseReport(response, 'region', 'sessions')  

        total =  0 # should be initialized with cummul upto 2023-07-01
        data = [ [country, int(count)] for [country, count] in data ]
        for c, count in data:
            total += count
        region_dict = {
                    'Ontario': u'Ontario',
                    'Quebec': u'Québec',
                    'British Columbia': u'Colombie-Britannique',
                    'Alberta': u'Alberta',
                    'Nova Scotia': u'Nouvelle-Écosse',
                    'Manitoba': u'Manitoba',
                    'Saskatchewan': u'Saskatchewan',
                    'New Brunswick': u'Nouveau-Brunswick',
                    'Newfoundland and Labrador': u'Terre-Neuve-et-Labrador',
                    'Prince Edward Island': u'Île-du-Prince-Édouard',
                    'Northwest Territories':u'Territoires du Nord-Ouest',
                    'Yukon Territory':u'Yukon',
                    'Nunavut':u'Nunavut',
        }
        data = [ [country if country !='(not set)' else 'unknown / Inconnu', int(count), "%.2f"%((count*100.0)/total) + '%' ] for [country, count] in data ]
        for row in data:
            r = row[0]
            if r == '(not set)':
                row[0] = 'unknown / Inconnu'
            else:
                r_fr = region_dict.get(r, r)
                row[0] = r + u' | ' + r_fr
        #df = pd.DataFrame(data, columns=['region / Région', 'visits / Visites', 'percentage of total visits / Pourcentage du nombre total de visites'])
        #print (df.head())
        data.insert(0,['region / Région', 'visits / Visites', 'percentage of total visits / Pourcentage du nombre total de visites'])
        write_csv(csv_file, data)
    
    def set_catalogue_file(self, end):
        y,m,d = end.split('-')
        ga_static_dir = os.environ['GA_STATIC_DIR']
        self.file = ''.join([ga_static_dir,'/od-do-canada.',y,m,d,'.jl.gz'])
        if not os.path.exists(self.file):
            raise Exception('not found ' + self.file)
    def by_org(self, org_stats, csv_file):
        rows = []
        header = ['Department or Agency', 'Ministère ou organisme',
                     'Department or Agency datasets', 'Jeux de données du Ministère ou organisme' , 'Total']
        for org_id, count in org_stats.iteritems():
            [title_en, title_fr] = self.orgs.get(org_id, ['', ''])
            name = self.org_id2name[org_id][0]
            link_en = 'http://open.canada.ca/data/en/dataset?organization=' + name
            link_fr = 'http://ouvert.canada.ca//data/fr/dataset?organization=' + name
            rows.append([title_en, title_fr, link_en, link_fr, count])
        rows.sort(key=lambda x: x[0])
        rows = cleanup_illegal_characters(rows)
        write_csv(csv_file, rows, header)

    def by_org_month(self, csv_month_file, csv_file):
        self.set_catalogue_file(self.end_date)
        # need to use cataloge file downloaded at 1st day of each month (or last day of prev month), same for by_org
        # need to update the last column, insert before last column
        # insert row if new org is created
        org_stats = defaultdict(int)
        total_num = 0
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
        en_months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        fr_months = ['janv.','févr.','mars','avril','mai','juin','juil.','août','sept.','oct.','nov.','déc.']
        [y,m,d] = self.end_date.split('-')
        en_header = en_months[int(m)-1]+'-'+y
        fr_header = fr_months[int(m)-1]+'-'+y
        new_header = en_header + ' / ' + fr_header
        if header[-2] == new_header:
            print ('exists ', new_header)
            return
        header[0] = 'Government of Canada Department or Agency / Ministère ou organisme'
        header[1] = 'Department or Agency datasets / Jeux de données du Ministère ou organisme'
        header[-1] = 'Total number of datasets / Nombre de jeux de données'
        header.insert(-1, new_header)

        #need to rotate, merge column 2, and 3, update the title
        del header[2]
        def prior_header(h):
            hs = h.split(' / ')
            if len(hs) ==2:  # new header
                return ' '.join(['prior to', hs[0], ' / Avant', hs[1]])
            else:  # old english header
                hs = h.split('-')
                mi = en_months.index(hs[0].strip())
                nh = fr_months[mi] + '-' + hs[1]
                return ' '.join(['prior to', h, ' / Avant', nh])
        header[2] = prior_header(header[3])
        for i in range(3, len(header)-2):
            h = header[i]
            if len(h.split(' / ')) == 1:  #translate
                hs = h.split('-')
                mi = en_months.index(hs[0].strip())
                nh = fr_months[mi] + '-' + hs[1]
                header[i] = h + ' / ' + nh

        # update exists one
        exists = {}
        for row in ds:
            #get org shortname
            name = row[1].split('=')[-1]
            # some orgs got new shortforms
            name = {
                'ceaa-acee': 'iaac-aeic',
                'neb-one': 'cer-rec',
            }.get(name, name)

            org_id = self.org_name2id[name]
            exists[org_id] = True
            titles =  self.orgs.get(org_id, ['', ''])
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

        # New org
        for org_id, count in org_stats.iteritems():
            if org_id in exists:
                continue
            titles =  self.orgs.get(org_id, ['', ''])
            title = titles[0] + ' | ' + titles[1]
            name = self.org_id2name[org_id][0]
            link_en = 'http://open.canada.ca/data/en/dataset?organization=' + name
            link_fr = 'http://ouvert.canada.ca//data/fr/dataset?organization=' + name
            link = link_en + ' | ' + link_fr
            row = [ 0 for i in range(len(header)) ]
            row[0] = title
            row[1] = link
            row[-2] = row[-1] = count
            ds.append(row)
        ds.sort(key=lambda x:x[0])

        var = total_num - int(total[-1])
        total[-1] = total_num
        total.insert(-1, var)
        pr, c = int(total[2]), int(total[3].replace(',', ''))
        del total[2]
        total[2] = pr + c

        ds.append(total)
        write_csv(csv_month_file, ds, header)

def report(client_secret_path, property_id, og_config_file, start, end, va):
      og_type = va
      client = initialize_analyticsreporting(client_secret_path)
      ds = DatasetDownload(start, end,og_type, client, property_id, og_config_file)
      if og_type == 'info':
          return ds.getStats(og_type )
      elif og_type == 'visit':
          return ds.getVisitStats(og_type)
      elif og_type == 'download':
          return ds.getStats(og_type)

      ga_tmp_dir = os.environ['GA_TMP_DIR']
      ds.getStats(og_type); time.sleep(2)
      ds.monthly_usage(os.path.join(ga_tmp_dir, 'od_ga_month.csv')); time.sleep(2)
      ds.by_country(os.path.join(ga_tmp_dir, 'od_ga_by_country.csv')); time.sleep(2)
      ds.by_region(os.path.join(ga_tmp_dir, 'od_ga_by_region.csv'))
      ds.by_org_month(os.path.join(ga_tmp_dir, 'od_ga_by_org_month.csv'), 
                      os.path.join(ga_tmp_dir, 'od_ga_by_org.csv'))

def main():
    report(*sys.argv[1:])

if __name__ == '__main__':
  main()

#python $GA_OG_ANALYTICS \
#    $GA_CLIENT_SECRET 68455797 $GA_PORTAL_INI \
#    $STARTYR-$CURMTH-01 $PRVYR-$PRVMTH-$LASTDY info
# Should be set to :
#$GA_OG_ANALYTICS \
#    $GA_CLIENT_SECRET - Credentials.json path
#  68455797 - property_id ( 363143703 or 359129908) 
# $GA_PORTAL_INI  CKAN INI FILE
#  $STARTYR-$CURMTH-01 - start_date
#  $PRVYR-$PRVMTH-$LASTDY - end_date
#  info - og_type (info, visit, download)
# CSV files downloaded. 
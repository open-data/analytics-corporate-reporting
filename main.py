import os
import csv
import pandas as pd 
import codecs
import unicodecsv
import yaml
import math
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    Filter,
    FilterExpression,
    RunReportRequest,
    OrderBy,
    
    
)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "credentials.json"
client = BetaAnalyticsDataClient()
country = yaml.full_load(open('reg.yml', 'r', encoding='utf-8'))
country_name = country.get('country_region').get('country')
region_name = country.get('country_region').get('region')
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
# parsing GA4 report to align with our reporting
def parseReport(response, dimension_name='pagePath', metric_name='eventCount'):
    data, rows_returned = [], 0
    
    for rowIdx, row in enumerate(response.rows):
        
        dim, mtr = [],[]
        if dimension_name:
            for i, dimension_value in enumerate(row.dimension_values): 
                if response.dimension_headers[i].name == dimension_name:          
                    dim.append(dimension_value.value)         

        for i, metric_value in enumerate(row.metric_values):            
            mtr.append(metric_value.value)
        if dimension_name:                     
            data.append(dim + mtr)
        else:
             data.append(mtr)
    rows_returned = response.row_count
    return data, rows_returned
def by_country(start,end,property_id="359129908", csv_file= None):
    request = RunReportRequest(
    property=f"properties/{property_id}",
    dimensions= [Dimension(name="country")],
    metrics=[Metric(name="sessions")],
    date_ranges=[DateRange(start_date= start, end_date=end)]
        , 
     
    order_bys =[OrderBy(
        desc = True,
        metric = OrderBy.MetricOrderBy(metric_name = "sessions")
    )],   
    # dimension_filter  = FilterExpression(
    #     filter = Filter (
    #         field_name ='eventName',
    #         string_filter = Filter.StringFilter(value = 'file_download')
    #     )

    # ),
    limit = 100000,
    offset = 0,

        
    )
    response = client.run_report(request) 
    data, rows_retuned = parseReport(response, 'country', 'sessions')            
    total = 0
    country_fr = [c for c in country_name.values()]
    country_en = [c for c in country_name.keys()]
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

# Total visits and downloads within a given period 
def total_usage( start, end, csv_file,property_id="359129908"):
        total, downloads = 0, 0        
        request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions= [ Dimension(name="PagePath")],
        metrics=[Metric(name="sessions")],
        date_ranges=[DateRange(start_date= start, end_date=end)]
        ,
        limit = 100000,
        offset = 0,

        
    )
        while True:
            response = client.run_report(request)
            data, rows_returned = parseReport(response, None, 'sessions')             
            for [vcount] in data: 
                    total += int(vcount)
            if (rows_returned<=request.limit or (rows_returned - request.offset)<=request.limit):
                break
            request.offset += request.limit      

        request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions= [Dimension(name="eventName"),
                     Dimension(name="PagePath")
                     ],
        metrics=[Metric(name="eventCount"), 
                 Metric(name="eventValue")],
        date_ranges=[DateRange(start_date= start, end_date=end)]
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
        response = client.run_report(request)
        data, rows_retuned = parseReport(response, None, 'eventCount')         
        for eCount , eVal in data:
            downloads += int(eCount)
        #print(f"Visits:{total} and Downloads:  {downloads}")
        # Checking if the report is up to date and updating otherwise
        [year, month, _] = start.split('-')
        data = read_csv(csv_file)        
        if int(data[1][0]) == int(year) and int(data[1][1]) == int(month):
            print ('entry exists, no overwriting')
            return
        row = [year, month, total, downloads]
        print(row)
        data[0] = ['year / année', 'month / mois', 'visits / visites', 'downloads / téléchargements']
        data.insert(1,row)
        write_csv(csv_file, data)
        
        

def getRawReport(start, end, property_id="359129908"):
    """Runs a simple report on a Google Analytics 4 property."""
    # TODO(developer): Uncomment this variable and replace with your
    #  Google Analytics 4 property ID before running the sample.
    property_id = property_id


    # Using a default constructor instructs the client to use the credentials
    # specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
    client = BetaAnalyticsDataClient()

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions= [Dimension(name="eventName"),
                     Dimension(name="pagePath")
                     ],
        metrics=[Metric(name="eventValue"), 
                 Metric(name="eventCount")],
        date_ranges=[DateRange(start_date= start, end_date=end)]
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
    response = client.run_report(request)   
    data, rows_retuned = parseReport(response, 'eventName', 'sessions') 
    df = pd.DataFrame(data, columns=['eventName','eventValue', 'eventCount'])
    print(df.head())    
getRawReport("2023-04-01","today")
total_usage("2023-04-01","today", csv_file='usage.csv')
by_country( '2023-04-01','2023-04-30', csv_file= 'visits_by_Country.csv')

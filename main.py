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
    FilterExpressionList
    
    
)



country = yaml.full_load(open('reg.yml', 'r', encoding='utf-8'))
country_name = country.get('country_region').get('country')
region_name = country.get('country_region').get('region')
client_secrets_path = "credentials.json"
def initialize_analyticsreporting(client_secrets_path):
 
  # Parse command-line arguments.
#  parser = argparse.ArgumentParser(
#      formatter_class=argparse.RawDescriptionHelpFormatter,
#      parents=[tools.argparser])
  # flags = parser.parse_args(['--noauth_local_webserver'])
#  flags = parser.parse_args([])

  # Set up a Flow object to be used if we need to authenticate.
  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = client_secrets_path

  # Build the service object.
  client = BetaAnalyticsDataClient()
#http=http, discoveryServiceUrl=DISCOVERY_URI)

  return client
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
            if response.metric_headers[i].name == metric_name:    
                 mtr.append(metric_value.value)
        if dimension_name:                     
            data.append(dim + mtr)
        else:
             data.extend(mtr)
    rows_returned = response.row_count
    return data, rows_returned
def by_region( ga, end, property_id, csv_file=None):
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions= [Dimension(name="region")],
        metrics=[Metric(name="sessions"), 
                 Metric(name="eventValue")],
        date_ranges=[DateRange(start_date= '2023-04-01', end_date=end)]
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
    response = ga.run_report(request)
    data, rows_retuned = parseReport(response, 'region', 'sessions')  

    total =  0 # should initialized with records upto 2023-04-01
    data = [ [country, int(count)] for [country, count] in data ]
    for c, count in data:
        total += count

    data = [ [country if country !='(not set)' else 'unknown / Inconnu', int(count), "%.2f"%((count*100.0)/total) + '%' ] for [country, count] in data ]
    region_fr = [r for r in region_name.values()]
    region_en = [r for r in region_name.keys()]
    assert( len(region_en)==len(region_fr))
    region_dict = { region_en[i]:region_fr[i] for i in range(len(region_en)) }
    for row in data:
        r = row[0]
        if r == '(not set)':
            row[0] = 'unknown / Inconnu'
        else:
            r_fr = region_dict.get(r, r)
            row[0] = r + u' | ' + r_fr
    df = pd.DataFrame(data, columns=['region / Région', 'visits / Visites', 'percentage of total visits / Pourcentage du nombre total de visites'])
    print (df.head())
    data.insert(0,['region / Région', 'visits / Visites', 'percentage of total visits / Pourcentage du nombre total de visites'])
    write_csv(csv_file, data)
def by_country(ga, start,end,property_id, csv_file= None):
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
    limit = 100000,
    offset = 0,

        
    )
    response = ga.run_report(request) 
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
def monthly_usage(ga, start, end, csv_file,property_id):
        total, downloads = 0, 0        
        request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions= [ Dimension(name="PagePath")],
        metrics=[Metric(name="sessions"),
                 Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date= start, end_date=end)]
        ,
        order_bys =[OrderBy(
        desc = True,
        metric = OrderBy.MetricOrderBy(metric_name = "screenPageViews")
        )],   
        limit = 100000,
        offset = 0,        
    )
        while True:
            response = ga.run_report(request)
            data, rows_returned = parseReport(response, None, 'sessions')             
            for eCount in data: 
                    total += int(eCount)
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
        response = ga.run_report(request)
        data, rows_retuned = parseReport(response, None, 'eventCount')         
        for eCount in data:
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
        
def getRawVisitReport( ga, start, end, property_id):
        """Runs a simple report on a Google Analytics 4 property."""
        # TODO(developer): Uncomment this variable and replace with your
        #  Google Analytics 4 property ID before running the sample.
        property_id = property_id
        # Using a default constructor instructs the client to use the credentials
        # specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
        #client = BetaAnalyticsDataClient()
        request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions= [Dimension(name="pagePath"), 
                     Dimension(name="eventName")],
        metrics=[Metric(name="sessions"), 
                Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date= start, end_date=end)]
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
        offset = 0,        
        )
        return ga.run_report(request)   

def getRawReport(ga, start, end, property_id):
    """Runs a simple report on a Google Analytics 4 property."""
    # TODO(developer): Uncomment this variable and replace with your
    #  Google Analytics 4 property ID before running the sample.
    property_id = property_id


    # Using a default constructor instructs the client to use the credentials
    # specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
    #client = BetaAnalyticsDataClient()


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
                string_filter = Filter.StringFilter(value = 'page_view')
            )

        ),
        order_bys =[OrderBy(
        desc = True,
        metric = OrderBy.MetricOrderBy(metric_name = "eventCount")
    )],   
        limit = 100000,
        offset = 0,
       
    )
    return ga.run_report(request)   
def main ():
    client = initialize_analyticsreporting(client_secrets_path)
    R = "363143703"
    S = "359129908"
    response = getRawReport(client, "2023-04-01","today", R)
    data, rows_retuned = parseReport(response, 'eventName', 'eventCount') 
    df = pd.DataFrame(data, columns=['eventName','eventCount'])
    print(df.head(20))    
    # monthly_usage(client, "2023-04-01","2023-04-30", 'usage.csv',R)
    # by_country(client, '2023-04-01','2023-04-30',R, 'visits_by_Country.csv')
    # by_region( client, "today", R, csv_file='visits_by_region.csv')
    #test = getRawVisitReport( client, '2023-04-01','today',R)
    # d, rt = parseReport(test, 'pagePath', 'screenPageViews')
    # df1 = pd.DataFrame(d, columns=['pagePath','screenPageViews'])
    # df1.to_csv("test.csv",index=False)
    #print(df1.head())
if __name__ == '__main__':
  main()
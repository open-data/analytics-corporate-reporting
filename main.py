import os
import pandas as pd 
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    Filter,
    FilterExpression,
    RunReportRequest,
)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "credentials.json"
client = BetaAnalyticsDataClient()
def parseReport(response, dimension_name='pagePath', metric_name='eventCount'):
    data, rows_returned = [], 0
    
    for rowIdx, row in enumerate(response.rows):
        
        dim, mtr = [],[]
        if dimension_name:
            for i, dimension_value in enumerate(row.dimension_values):            
                dim.append(dimension_value.value)         

        for i, metric_value in enumerate(row.metric_values):            
            mtr.append(metric_value.value)
        if dimension_name:                     
            data.append(dim + mtr)
        else:
             data.append(mtr)
    rows_returned = response.row_count
    return data, rows_returned
def monthly_usage( start, end, csv_file=None,property_id="359129908"):
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
        response = client.run_report(request)
        data, rows_retuned = parseReport(response, None, 'sessions')             
        for [vcount] in data: 
            total += int(vcount)

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
                     Dimension(name="PagePath")
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
    data, rows_retuned = parseReport(response, True, 'sessions') 
    df = pd.DataFrame(data, columns=['eventName','PagePath', 'eventValue', 'eventCount'])
    print(df.head())
getRawReport("2023-04-01","today")
monthly_usage("2023-04-01","today", csv_file=None)
"""OG Analytics Reporting Open Map."""
from datetime import *
import tempfile
import gzip
import json
import sys
import io
import os
import requests
from collections import defaultdict
import pandas as pd
import warnings
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
warnings.resetwarnings()
warnings.simplefilter('ignore', SyntaxWarning)
warnings.simplefilter('ignore', pd.errors.SettingWithCopyWarning)
import open_map_patch

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


def download():
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


# reads the catalogue file
def read_portal(end):
    y, m, d = end.split('-')
    data = []
    for records in download():
        for record in records:
            try:
                if record['collection'] == "fgp":
                    data.append([y, m, record['id'], record['title_translated'], record['collection'],
                                record['organization']['name'], record['organization']['title'], "".join(record['display_flags'])])
            except IndexError as e:
                print(e)
                continue
    df = pd.DataFrame(data, columns=['year', 'month', 'id', 'title_translated',
                      'collection', 'owner_org', 'org_name', 'display_flags'])
    df_map = df.loc[df["display_flags"] == "fgp_viewer"]
    title = [elm.get('en') for elm in df_map["title_translated"]]
    titre = [elm.get('fr') for elm in df_map["title_translated"]]
    df_map['title_en'] = title
    df_map['title_fr'] = titre
    new_columns = ['year', 'month', 'id', 'title_en', 'title_fr',
                   'collection', 'owner_org', 'org_name', 'display_flags']
    return df_map[new_columns]


def getOpenMap(property_id, start_date, end_date, ga):
    offset = 0
    limit = 10000
    stats = defaultdict(int)
    while True:
        response = getRawReport(
            offset, limit, property_id, start_date, end_date, ga)
        data, rowCount = parseReport(response, metric_name="screenPageViews")
        for [url, count] in data:
            id = url.split('/')[-1]
            for id in id.split(','):
                if len(id) >= 36:
                    stats[id[:36]] += int(count)
        if (rowCount <= limit or (rowCount - offset) <= limit):
            break
        else:
            offset += limit
    return stats


# Get raw report from GA4 API filtered by screenPageViews or downloads
def getRawReport(offset, limit, property_id, start_date, end_date, ga):
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="pagePath")
        ],
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[
            DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=FilterExpression(

            or_group=FilterExpressionList(
                expressions=[
                    FilterExpression(
                        filter=Filter(
                            field_name='pagePath',
                            string_filter=Filter.StringFilter(match_type="BEGINS_WITH",
                                                              value='/openmap/',
                                                              case_sensitive=True)
                        )
                    ),
                    FilterExpression(
                        filter=Filter(
                            field_name='pagePath',
                            string_filter=Filter.StringFilter(match_type="BEGINS_WITH",
                                                              value='/carteouverte/',
                                                              case_sensitive=True)
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
    return ga.run_report(request)


def report(client_secret_path, property_id, start, end):
    geo_dataset = read_portal(end)
    client = initialize_analyticsreporting(client_secret_path)
    data = getOpenMap(property_id, start, end, client)
    openMap_views = pd.DataFrame.from_dict(data, orient='index', columns=[
                                           'pageviews']).reset_index(names='id')
    geo_mapViews = geo_dataset.merge(openMap_views, how='inner', on='id')
    geo_mapViews.sort_values('pageviews', ascending=False, inplace=True)
    return geo_mapViews.drop(columns=['collection', 'display_flags'])


def main():
    today = datetime.today()
    last_day = (today - timedelta(days=today.day))
    first_day = (last_day-timedelta(days=last_day.day-1)
                 ).strftime('%Y-%m-%d')
    last_day = last_day.strftime('%Y-%m-%d')
    y, m, d = last_day.split("-")
    df = report("credentials.json", "359132180", first_day, last_day)
    df.to_csv("current_map.csv", encoding="utf-8", index=False)
    #df = report("credentials.json", "359132180", first_day, last_day)
    Url = "https://open.canada.ca/data/dataset/2916fad5-ebcc-4c86-b0f3-4f619b29f412/resource/15eeafa2-c331-44e7-b37f-d0d54a51d2eb/download/open-maps-analytics.csv"
    r = requests.get(Url).content
    old_df = pd.read_csv(io.StringIO(r.decode('utf-8')))
    old_df_current = old_df.query(f'year == {str(y)} & month == {int(m)}')
    print (old_df.head(20))
    if len(old_df_current) > 0:
        print("Record already exists and no overwriting")
        return
    else:
        df = pd.concat([old_df, df], ignore_index=True)
        df.sort_values(['year', 'month', 'pageviews'],
                       ascending=False, inplace=True)
        df.to_csv('open-maps-analytics.csv', encoding='utf-8', index=False)
    if os.path.isfile('open-maps-analytics.csv'):    
        #open_map_patch.resources_update()
if __name__ == '__main__':
    main()

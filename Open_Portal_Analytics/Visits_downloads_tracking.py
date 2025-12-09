import aanalytics2 as api2
import pandas as pd
import Open_data as od
import json,os
from copy import deepcopy
from datetime import *
from dateutil.relativedelta import relativedelta
import time

def timeFormat (str_date):    
    date_time = datetime.fromisoformat(str_date.strftime('%Y-%m-%d'))
    return date_time.isoformat(timespec='milliseconds')

def report_extraction (day_url_json,day_loop, first_day, last_day, ags, report_type):
    
    day_url_json['globalFilters'][1]['dateRange']=str(timeFormat(first_day))+"/"+str(timeFormat(last_day))
    tracked_metric = day_url_json['metricContainer']['metrics'][0]['id']

    day_dict = {}
    df = pd.DataFrame()
    for _, row in day_loop.iterrows():
        temp_json = deepcopy(day_url_json)
        temp_json['metricContainer']['metricFilters'][0]['itemId']=row['item_id']
        temp_report = ags.getReport(temp_json,limit = 2000,n_results=50000)
        print(f'retreiving report on {row['Day']} now')
        temp_df = temp_report['data']
        temp_df['day'] = row['Day']    
        df = pd.concat([df,temp_df], ignore_index=True)

    df.rename(columns={'variables/evar12' : 'Page_URL', tracked_metric : report_type}, inplace= True)
    df.to_csv( os.path.join("Open_Portal_Analytics","".join([last_day.strftime("%b"),"_daily_",report_type,".csv"])),encoding='utf-8-sig',index=False)
    print(f'dataset from daily visits : {df.shape}')
    dataset_portion = df['Page_URL'].transform(lambda x : x.split('/resource/')[0])
    df['resource_id']= df['Page_URL'].transform(lambda x : x.split('/resource/')[-1] if len( x.split('/resource/')[-1]) ==36 else "No resource" )
    df['dataset_id'] = dataset_portion.transform(lambda x : x.split('/dataset/')[-1] )
    df['ID_len'] = df['dataset_id'].transform(lambda x : len(x))
    df.query(f'ID_len==36', inplace=True)
    df['full_id'] = df['dataset_id'] +'|'+ df['resource_id']
    df.drop(['ID_len'],axis=1, inplace =True)
    print (df.columns.tolist())

    df_group= df.groupby(['full_id','day'])[report_type].sum().reset_index()
    df_group[['dataset_id','resource_id']] = df_group['full_id'].str.split('|', expand=True)
    print(f'{last_day.strftime("%B")} daily {tracked_metric} from Adobe Analytics: {df_group.shape}')
    
    # Extracting dataset on Open Portal catalogue
    df_OG = pd.DataFrame(od.open_dataset())
    df_OG['full_id'] = df_OG['record_id'] +'|'+ df_OG['resource_id']
    print(f'Dataset from the catalogue {df_OG.shape}')
    report_dataset_mapping (df_group, df_OG, last_day, report_type)


def report_dataset_mapping (df_report, dataset, last_day, tracked_metric):
    df_merge = pd.merge(df_report, dataset, on='full_id', how='inner')
    df_merge.drop(['full_id','record_id', 'resource_id_x'],axis=1, inplace = True)
    df_merge.rename(columns ={'resource_id_y': 'resource_id'}, inplace = True)    
    df_merge.to_csv(os.path.join("Open_Portal_Analytics","".join([last_day.strftime("%b"),"_daily_Open_data_",tracked_metric,".csv"])),encoding='utf-8-sig',index=False)
    print (f'Merged dataset and daily visits:  {df_merge.shape}')
    
def breakdown_id (first_day, last_day, ags):
        
    # Extracting the Day ids in the last month        

    with open(os.path.join("Open_Portal_Analytics",'last_month_itemID.json'),'r') as file:
        json_data = json.loads(file.read())

    json_data['globalFilters'][1]['dateRange']=str(timeFormat(first_day))+"/"+str(timeFormat(last_day))
    loop_itemId = ags.getReport(json_data,n_results=50000, verbose=True, item_id=True)
    print (loop_itemId['data'].head()) # checking the breakdown loop
    Day_itemId = loop_itemId['data'][['variables/daterangeday','item_id']]
    Day_itemId.rename(columns={'variables/daterangeday':'Day'}, inplace = True)
    return Day_itemId
    
    


def main ():
    # Initialization of Adobe Analytics 
    api2.configure(org_id = os.environ['org_id'],
        client_id = os.environ['client_id'],
        secret = os.environ['secret'],
        scopes= os.environ['scopes'])

    login = api2.Login()
    ags = api2.Analytics ('canada5')
    rsid ='canadalivemain'
    
    # Visit report json template

    with open (os.path.join("Open_Portal_Analytics","day_url_report.json"),'r') as f:
        day_url_json = json.loads(f.read())
   
   
    # Current month visits and download reports extraction 
      
    cur_last_day = date.today()
    cur_first_day = cur_last_day-timedelta(days=cur_last_day.day-1)       
    print (f'Extracting report from {cur_first_day} to {cur_last_day}')
    Day_itemId = breakdown_id(cur_first_day,cur_last_day, ags)   
       
    
    # Visit report extraction
    
    day_url_json['metricContainer']['metrics'][0] = {'columnId': '0', 'id': 'metrics/visits', 'filters': ['0']}
    report_extraction (day_url_json, Day_itemId,cur_first_day, cur_last_day, ags, 'Visits')  
     
    # Download report extraction 
    day_url_json['metricContainer']['metrics'][0] = {'columnId': '0', 'id': 'metrics/event25', 'filters': ['0']}
    report_extraction (day_url_json, Day_itemId,cur_first_day, cur_last_day, ags, 'Downloads')  
    
    
    # Last month visits and download report extraction    
    
    last_day = cur_last_day - timedelta(days=cur_last_day.day)
    last_first_day = last_day-timedelta(days=last_day.day-1)
    last_visits = os.path.join("Open_Portal_Analytics","".join([last_day.strftime("%b"),"_daily_Open_data_","Visits",".csv"])) 
    last_downloads = os.path.join("Open_Portal_Analytics","".join([last_day.strftime("%b"),"_daily_Open_data_","Downloads",".csv"])) 
   
    print (f'Checking report from {last_first_day} to {last_day}')
    Day_itemId = breakdown_id(last_first_day,last_day, ags)
    
    if not os.path.isfile(last_visits):
        print (f'Extracting visits report from {last_first_day} to {last_day}')   
       
        # Visit report extraction
        day_url_json['metricContainer']['metrics'][0] = {'columnId': '0', 'id': 'metrics/visits', 'filters': ['0']}
        report_extraction (day_url_json, Day_itemId,last_first_day, last_day, ags, 'Visits')  
    
    if not os.path.isfile(last_downloads):
        print (f'Extracting downloads report from {last_first_day} to {last_day}')      
        # Download extraction 
        day_url_json['metricContainer']['metrics'][0] = {'columnId': '0', 'id': 'metrics/event25', 'filters': ['0']}
        report_extraction (day_url_json, Day_itemId,last_first_day, last_day, ags, 'Downloads')  
   

if __name__ == '__main__':
    main()
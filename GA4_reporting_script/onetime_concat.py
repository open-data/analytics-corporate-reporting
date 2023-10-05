import pandas as pd
from datetime import *
import os
# to correct month in file_list and list_top
today = date.today()
last_day = today- timedelta(days=today.day) 
last_day= last_day.strftime('%Y-%m-%d') 
y,m,d =last_day.split("-")
last_month = str("%02d" %(int(m)-1))
next_month = str("%02d" %(int(m)+ 1))
new_download = os.path.join("GA_TMP_DIR", "-".join(["openDataPortal.siteAnalytics.downloads", 
                                        "".join([m,str(int(y)-1)]),"".join([m,y, ".csv"])])) 
new_visit = os.path.join("GA_TMP_DIR", "-".join(["openDataPortal.siteAnalytics.visits", 
                                        "".join([m,str(int(y)-1)]),"".join([m,y, ".csv"])])) 
new_info = os.path.join("GA_TMP_DIR", "-".join(["openDataPortal.siteAnalytics.info", 
                                        "".join([m,str(int(y)-1)]),"".join([m,y, ".csv"])])) 
current_visits = os.path.join ("GA_TMP_DIR","openDataPortal.siteAnalytics.visits.csv") 
current_downloads = os.path.join ("GA_TMP_DIR", "openDataPortal.siteAnalytics.downloads.csv")
current_info = os.path.join ("GA_TMP_DIR", "od_ga_All_Info_download.csv")

file_list = [(os.path.join("GA_TMP_DIR", "-".join(["opendataportal.siteanalytics.downloads", 
                                        "".join([last_month,str(int(y)-1)]),"".join([last_month,y, ".csv"])])) ,
                                        current_downloads, new_download, False), 
             (os.path.join("GA_TMP_DIR", "-".join(["opendataportal.siteanalytics.visits", 
                                        "".join([last_month,str(int(y)-1)]),"".join([last_month,y, ".csv"])])) ,
                                          current_visits, new_visit, True),
             (os.path.join("GA_TMP_DIR", "-".join(["opendataportal.siteanalytics.info", 
                                        "".join([last_month,str(int(y)-1)]),"".join([last_month,y, ".csv"])])),
                                          current_info, new_info, False)]

list_top =[("opendataportal.siteanalytics.top20info.csv", 
            "".join(["openDataPortal.siteAnalytics.top20Info", m, y,".csv"])) , 
           ("opendataportal.siteanalytics.top100datasets.bilingual.csv", 
            "".join(["openDataPortal.siteAnalytics.top100Datasets.bilingual", m, y,".csv"]))] 
def concat_top (list_top):
    for old_file, new_file in list_top:
        old_path = os.path.join("GA_TMP_DIR", old_file )
        new_path = os.path.join("GA_TMP_DIR", new_file )
        new_top = pd.concat([pd.read_csv(old_path , encoding="utf-8"), pd.read_csv(new_path , encoding="utf-8")],ignore_index= True)
        new_top.sort_values(by=["year_annee", "month_mois", "downloads_telechargements"], ascending=False, inplace=True)
        new_top.to_csv(old_path, index=False, encoding="utf-8")
        os.remove(new_path)

def add_new_month(last_month_csv, new_month_csv, new_filename,isVisit ):
    df_old = pd.read_csv(last_month_csv, encoding ="utf-8")
    #df_old.rename(columns={'Year/année': "year", 'Month/mois':"month" }, inplace=True)
    df_11_month = df_old.query(f'year_annee != {today.year-1} or month_mois !={today.month-1}')   
     
    df_12_month= pd.concat([df_11_month , pd.read_csv(new_month_csv, encoding="utf-8")],ignore_index= True)
    
    if isVisit:
        df_12_month.sort_values(by=["year_annee", "month_mois", "visits_visites"], ascending=False, inplace=True)
    else:
        df_12_month.sort_values(by=["year_annee", "month_mois", "downloads_telechargements"], ascending=False, inplace=True)
    df_12_month.to_csv(new_filename, index=False, encoding="utf-8")
    os.remove(new_month_csv)
def concat_hist():
    for l_csv, new_csv, new_f, isV in file_list:
        add_new_month(l_csv, new_csv,new_f, isV)
        os.remove(l_csv)
    concat_top (list_top)

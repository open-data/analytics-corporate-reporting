import os 
from pathlib import Path
def old_to_new_names ():    
    old_top100 = os.path.join("GA_TMP_DIR", "od_ga_top100.csv")
    new_top100  = os.path.join("GA_TMP_DIR", "openDataPortal.siteAnalytics.top100Datasets.bilingual.csv")  
    file_rename(old_top100, new_top100)
    old_top20 = os.path.join("GA_TMP_DIR", "downloads_info.xlsx")
    new_top20  = os.path.join("GA_TMP_DIR", "openDataPortal.siteAnalytics.top20Info.xlsx")  
    file_rename(old_top20, new_top20)

def file_rename(old_name, new_name):
    new_file = Path(new_name)
    if not new_file.exists():    
        try:
            os.rename(old_name, new_name)
        except FileNotFoundError as e:         
            print (f'the file {old_name} does not exist')
            return
    else:
        os.remove(old_name)
        print (f'the file {new_name}  exists')
        return

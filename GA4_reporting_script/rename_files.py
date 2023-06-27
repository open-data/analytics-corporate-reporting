import os 
from pathlib import Path
ga_tmp_dir = os.environ["GA_TMP_DIR"]
def old_to_new_names (end):
    y,m,d = end.split("-")
    old_download = os.path.join(ga_tmp_dir, "od_ga_downloads.xlsx")
    new_download = os.path.join(ga_tmp_dir, "-".join(["openDataPortal.siteAnalytics.downloads", 
                                  "".join([m,str(int(y)-1)]),"".join([m,y, ".xlsx"])])) 
    file_rename(old_download, new_download)
    old_top100 = os.path.join(ga_tmp_dir, "od_ga_top100.csv")
    new_top100  = os.path.join(ga_tmp_dir, "openDataPortal.siteAnalytics.top100Datasets.bilingual.csv")  
    file_rename(old_top100, new_top100)
    old_top20 = os.path.join(ga_tmp_dir, "downloads_info.xlsx")
    new_top20  = os.path.join(ga_tmp_dir, "openDataPortal.siteAnalytics.top20Info.xlsx")  
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

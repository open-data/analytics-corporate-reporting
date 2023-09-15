import requests
import os
from zipfile import ZipFile
# retreive urls from the linkFile
with open ('linkFile.txt') as f:
    lines = [line.rstrip('\n') for line in f]
f.close
new_filename = ["openDataPortal.siteAnalytics.datasetsByOrg.bilingual.csv","openDataPortal.siteAnalytics.datasetsByOrgByMonth.bilingual.csv",
                "openDataPortal.siteAnalytics.internationalUsageBreakdown.bilingual.csv", "openDataPortal.siteAnalytics.provincialUsageBreakdown.bilingual.csv",
                "openDataPortal.siteAnalytics.totalMonthlyUsage.bilingual.csv"]
# CSV files downloading method / URL
ga_tmp_dir = os.environ["GA_TMP_DIR"]

def filedow (reqURL):
    try:        
        req = requests.get(reqURL)
        filename =  reqURL.split('/')[-1]
        for new_name in new_filename:
            if new_name.lower() == filename:
                filename = new_name
        file_path = os.path.join(ga_tmp_dir,filename)
        with open (file_path, 'wb') as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        f.close
    except Exception as e:
        print(e)

    
 # Removes old files form TMP and downloads all csv the files fresh copy    
def csv_download():
    for filename in os.listdir(ga_tmp_dir):
       file_path = os.path.join(ga_tmp_dir, filename)
       os.remove(file_path)

    for line in lines:
        filedow(line)

# Downloads the current archive
def archive_download():
  arch_path = os.path.join("GA_STATIC_DIR", "archive.zip")
  url = "https://open.canada.ca/data/dataset/2916fad5-ebcc-4c86-b0f3-4f619b29f412/resource/8debb421-e9cb-49de-98b0-6ce0f421597b/download/archive.zip"
  r = requests.get(url, stream=True)
  with open (arch_path, "wb") as f:
      try:
         for chunk in r.iter_content(1024 * 64):
            f.write(chunk)
         f.close() 
      except Exception as e :
            print (e)
          
# Updates the archive with new files        
def archive_files (end):
    archive = os.path.join("GA_STATIC_DIR","archive.zip")
    for filename in os.listdir("GA_TMP_DIR"):
        file_source = os.path.join("ga_tmp_dir",filename)
        file_des = os.path.join("analytics", end, filename)
        full_path = os.path.join (archive, "analytics", end)
        archive_files= "/".join(["analytics", end, filename])
        
        with ZipFile(archive, "a") as archive_zip:
           
            if archive_files not in archive_zip.namelist():               
                # print (f'{filename} not archived ')                       
                archive_zip.write(file_source, arcname=file_des)
            
            else:
                print (f'{filename} is already archived no overwriting')
                continue
            archive_zip.close()
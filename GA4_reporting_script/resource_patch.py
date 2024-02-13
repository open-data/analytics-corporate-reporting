from ckanapi import RemoteCKAN
from ckanapi.errors import CKANAPIError
import os
import time
"""['openDataPortal.siteAnalytics.downloads-012022-012023.csv', 'openDataPortal.siteAnalytics.info-012022-012023.csv',
    'openDataPortal.siteAnalytics.visits-012022-012023.csv', 'opendataportal.siteanalytics.datasetsbyorg.bilingual.csv', 
    'opendataportal.siteanalytics.datasetsbyorgbymonth.bilingual.csv', 'opendataportal.siteanalytics.datasetsbyorgbymonth.bilingual_new.csv',
    'opendataportal.siteanalytics.internationalusagebreakdown.bilingual012024.csv', 'opendataportal.siteanalytics.provincialusagebreakdown.bilingual012024.csv',
    'opendataportal.siteanalytics.top100datasets.bilingual.csv', 'opendataportal.siteanalytics.top20info.csv',     
    'opendataportal.siteanalytics.totalmonthlyusage.bilingual.csv'] 
 """
def resources_update():

    all_files = sorted([filename for filename in os.listdir('GA_TMP_DIR')])     
 # Analytics resources
    resource_ids =["4ebc050f-6c3c-4dfd-817e-875b2caf3ec6", "b1dfa726-7ed1-4a6b-ae49-77a200abee72", "c14ba36b-0af5-4c59-a5fd-26ca6a1ef6db", 
                   "5a1b343d-2fea-4c31-8652-f77506e3ea37","f09148f9-a09b-46ec-bf5b-52f26720f3f3","d9138bac-8f9a-42e3-ac7c-450420c5d272", "b52ee0b2-f2be-4bc5-a27a-db93a228d38b",
                   "e06f06a9-d897-4a35-9b73-4c2bc1c2d5cf","ba980e38-f110-466a-ad92-3ee0d5a60d49","9d395c98-f33f-4d40-9e3b-3d383321c577",
                   "02a92b0f-b26d-4fbd-9601-d27651703715"]  
   
    api_reg = os.environ['API_Registry']
    ckan = RemoteCKAN('https://registry.open.canada.ca/', apikey=api_reg)
    count =0
    for id, filename in enumerate(all_files):
        print (f'{os.path.join("GA_TMP_DIR", filename)} corresponds to {resource_ids[id]}')
        while count <= 5:
          try:
            ckan.action.resource_patch(
              
              id =resource_ids[id],
              upload= open (os.path.join("GA_TMP_DIR", filename), "rb")
            


            )
            print("sucess")
            break
          except CKANAPIError as e:
            count +=1
            print(resource_ids[id])
            print (e)
            time.sleep(3*count)
          except Exception as e:
            count +=1
            print(e)
            continue  
   

    ckan.action.resource_patch(
          
          id = "8debb421-e9cb-49de-98b0-6ce0f421597b",

          upload= open (os.path.join("GA_STATIC_DIR", "archive.zip"), "rb")

        ) 


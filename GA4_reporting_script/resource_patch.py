from ckanapi import RemoteCKAN
from ckanapi.errors import CKANAPIError
import os

def resources_update():

    all_files = sorted([filename for filename in os.listdir('GA_TMP_DIR')])
    print(all_files)
    # Analytics resources
    """ resource_ids =["5a1b343d-2fea-4c31-8652-f77506e3ea37","f09148f9-a09b-46ec-bf5b-52f26720f3f3","4ebc050f-6c3c-4dfd-817e-875b2caf3ec6", 
                  "b52ee0b2-f2be-4bc5-a27a-db93a228d38b","e06f06a9-d897-4a35-9b73-4c2bc1c2d5cf", "ba980e38-f110-466a-ad92-3ee0d5a60d49",
                    "9d395c98-f33f-4d40-9e3b-3d383321c577","02a92b0f-b26d-4fbd-9601-d27651703715", "c14ba36b-0af5-4c59-a5fd-26ca6a1ef6db" ] """


    #Registry resources Id 
    """ resource_ids =["5dda926f-0718-4f1d-ac00-c601cb05194c","9ae83baa-dd01-4755-b079-60f697b52ebd","5eb3595a-3242-416f-8ee1-e885eb4356eb", 
                  "371d7ed8-a8e1-48d2-b53d-3f8b6fdd1259","de9f3d98-87f9-47a3-b8f7-c12e27fe3f76", "34d53825-0693-43b2-8cf4-cda323602a53",
                    "df33b8c2-ebed-4d86-9a01-3df80c584c56","eca0267e-4164-4bd1-8bfb-73117be1daec" ] """
    #Staging registery
    resource_ids =["926c4041-ad91-4624-951f-dfaf92acb15c","2a9fba67-5a33-49b5-946a-23a21f6b10c4","77e8753d-4da8-42a1-ae74-af0f9129674b", 
                  "150a6d3c-d057-4094-a572-7139a365f1f5","3450046b-29f4-4cbd-a53a-73c114b07bb6", "efa94ec1-b294-429a-851e-bd69bdc295d7",
                    "724e8a64-1288-43e3-9a28-07f266d94b69","f097b167-fd7c-41ab-92ff-c0819434a3ac", "3be6fb30-f2bc-4121-adeb-63410bbf7ad6" ]

    #ckan = RemoteCKAN('https://registry.open.canada.ca/', apikey=apikey)
    ckan = RemoteCKAN('https://registry-staging.open.canada.ca/', apikey=apikey)
    for id, filename in enumerate(all_files):
        #print (f'{filename} corresponds to {resource_ids[id]}')
        try:
          ckan.action.resource_patch(
            
            id =resource_ids[id],
            upload= open (os.path.join("GA_TMP_DIR", filename), "rb")

          )
        except CKANAPIError as e:
           print(resource_ids[id])
           print (e)

    ckan.action.resource_patch(
          
          #id="2026faa9-88b4-40dd-8abe-84a140adf647",
          id="674bf651-03d5-4b9f-8794-5cc5e6b91e9f",
          # analytic resources
          #id: " 8debb421-e9cb-49de-98b0-6ce0f421597b"
          upload= open (os.path.join("GA_STATIC_DIR", "archive.zip"), "rb")

        ) 

# dataset / package_id : 102e17d5-d573-463a-b5bc-94376e3ff48e
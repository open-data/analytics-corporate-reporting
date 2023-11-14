from ckanapi import RemoteCKAN
from ckanapi.errors import CKANAPIError
import os
api_reg = os.environ['API_Registry']

def resources_update():
    
    ckan = RemoteCKAN('https://registry.open.canada.ca/', apikey=api_reg)    
    try:
        ckan.action.resource_patch(
            
            id = "15eeafa2-c331-44e7-b37f-d0d54a51d2eb",

            upload= open ("open-maps-analytics.csv", "rb")

            )
    except CKANAPIError as e:
           print(id)
           print (e)
    except Exception as e:
        print(e)
        
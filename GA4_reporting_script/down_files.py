import requests
import os
# retreive urls from the linkFile
with open ('linkFile.txt') as f:
    lines = [line.rstrip('\n') for line in f]
f.close
# CSV files downloading method / URL
ga_tmp_dir = os.environ["GA_TMP_DIR"]

def filedow (reqURL):
    try:
        req = requests.get(reqURL)
        # filename = ".".join(reqURL.split('.')[-3:])
        # file_path = os.path.join(ga_tmp_dir,filename)
        filename = reqURL.split('/')[-1]
        file_path = os.path.join(ga_tmp_dir,filename)
        with open (file_path, 'wb') as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        f.close
    except Exception as e:
        print(e)

 # downloading catalogue files in STATIC directory 
def cat_download (end):
    y, m, d = end.split('-')
    #ga_static_dir = os.environ['GA_STATIC_DIR']
    file = ''.join(
        ["GA_STATIC_DIR", '\od-do-canada.', y, m, d, '.jl.gz'])
    url = 'http://open.canada.ca/static/od-do-canada.jl.gz'
    r = requests.get(url, stream=True)                
    with open (file, 'wb') as f:
        for chunk in r.iter_content(1024 * 64):
            f.write(chunk)
    f.close()
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
          
        
    
 # Removes old files form TMP and downloads all csv the files fresh copy    
def csv_download():
    for filename in os.listdir(ga_tmp_dir):
       file_path = os.path.join(ga_tmp_dir, filename)
       os.remove(file_path)

    for line in lines:
        filedow(line)


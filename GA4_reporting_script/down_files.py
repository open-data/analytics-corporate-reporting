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
    ga_static_dir = os.environ['GA_STATIC_DIR']
    file = ''.join(
        [ga_static_dir, '\od-do-canada.', y, m, d, '.jl.gz'])
    url = 'http://open.canada.ca/static/od-do-canada.jl.gz'
    r = requests.get(url, stream=True)                
    with open (file, 'wb') as f:
        for chunk in r.iter_content(1024 * 64):
            f.write(chunk)
    f.close()
    
 # downloading all csv the files in TMP directory    
def csv_download():
    for filename in os.listdir(ga_tmp_dir):
       file_path = os.path.join(ga_tmp_dir, filename)
       os.remove(file_path)

    for line in lines:
        filedow(line)


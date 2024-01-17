import requests
import os
from datetime import *
from zipfile import ZipFile




def filedow(reqURL):
    try:
        req = requests.get(reqURL)
        if req.status_code == 200:
            filename = reqURL.split('/')[-1]
            file_path = os.path.join("GA_TMP_DIR", filename)
            with open(file_path, 'wb') as f:
                for chunk in req.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            f.close

    except Exception as e:
        print(e)

 

# Removes old files form TMP and downloads all csv the files fresh copy
def csv_download(end):
    # today = date.today()
    # last_day = today - timedelta(days=today.day)
    # last_day = last_day.strftime('%Y-%m-%d')
    y, m, d = end.split("-") # last_day
    last_month = str("%02d" % (int(m)-1))
    resource_link = "https://open.canada.ca/data/dataset/2916fad5-ebcc-4c86-b0f3-4f619b29f412/resource/"
    urls = ["https://open.canada.ca/data/dataset/2916fad5-ebcc-4c86-b0f3-4f619b29f412/resource/02a92b0f-b26d-4fbd-9601-d27651703715/download/opendataportal.siteanalytics.totalmonthlyusage.bilingual.csv",
            resource_link + "e06f06a9-d897-4a35-9b73-4c2bc1c2d5cf/download/opendataportal.siteanalytics.provincialusagebreakdown.bilingual"+last_month+y+".csv",
            resource_link + "b52ee0b2-f2be-4bc5-a27a-db93a228d38b/download/opendataportal.siteanalytics.internationalusagebreakdown.bilingual"+last_month+y+".csv",
            "https://open.canada.ca/data/dataset/2916fad5-ebcc-4c86-b0f3-4f619b29f412/resource/5a1b343d-2fea-4c31-8652-f77506e3ea37/download/opendataportal.siteanalytics.datasetsbyorg.bilingual.csv",
            "https://open.canada.ca/data/dataset/2916fad5-ebcc-4c86-b0f3-4f619b29f412/resource/f09148f9-a09b-46ec-bf5b-52f26720f3f3/download/opendataportal.siteanalytics.datasetsbyorgbymonth.bilingual.csv",
            resource_link + "4ebc050f-6c3c-4dfd-817e-875b2caf3ec6/download/opendataportal.siteanalytics.downloads" +
            "-" + last_month + str(int(y)-1) + "-" + last_month+y+".csv",
            resource_link + "c14ba36b-0af5-4c59-a5fd-26ca6a1ef6db/download/opendataportal.siteanalytics.visits" +
            "-" + last_month + str(int(y)-1) + "-" + last_month+y+".csv",
            resource_link + "b1dfa726-7ed1-4a6b-ae49-77a200abee72/download/opendataportal.siteanalytics.info" +
            "-" + last_month + str(int(y)-1) + "-" + last_month+y+".csv",
            "https://open.canada.ca/data/dataset/2916fad5-ebcc-4c86-b0f3-4f619b29f412/resource/9d395c98-f33f-4d40-9e3b-3d383321c577/download/opendataportal.siteanalytics.top20info.csv",
            "https://open.canada.ca/data/dataset/2916fad5-ebcc-4c86-b0f3-4f619b29f412/resource/ba980e38-f110-466a-ad92-3ee0d5a60d49/download/opendataportal.siteanalytics.top100datasets.bilingual.csv"]
    for filename in os.listdir("GA_TMP_DIR"):
        file_path = os.path.join("GA_TMP_DIR", filename)
        os.remove(file_path)

    for url in urls:
        filedow(url)



# Downloads the current archive
def archive_download():
    arch_path = os.path.join("GA_STATIC_DIR", "archive.zip")
    url = "https://open.canada.ca/data/dataset/2916fad5-ebcc-4c86-b0f3-4f619b29f412/resource/8debb421-e9cb-49de-98b0-6ce0f421597b/download/archive.zip"
    r = requests.get(url, stream=True)
    with open(arch_path, "wb") as f:
        try:
            for chunk in r.iter_content(1024 * 64):
                f.write(chunk)
            f.close()
        except Exception as e:
            print(e)



# Updates the archive with new files
def archive_files(end):
    archive = os.path.join("GA_STATIC_DIR", "archive.zip")
    for filename in os.listdir("GA_TMP_DIR"):
        file_source = os.path.join("GA_TMP_DIR", filename)
        file_des = os.path.join("analytics", end, filename)
        full_path = os.path.join(archive, "analytics", end)
        archive_files = "/".join(["analytics", end, filename])

        with ZipFile(archive, "a") as archive_zip:

            if archive_files not in archive_zip.namelist():
                # print (f'{filename} not archived ')
                archive_zip.write(file_source, arcname=file_des)

            else:
                print(f'{filename} is already archived no overwriting')
                continue
            archive_zip.close()




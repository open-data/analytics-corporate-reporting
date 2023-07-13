import os
from zipfile import ZipFile, Path
import shutil
#ga_static_dir= os.environ["GA_STATIC_DIR"]
#ga_tmp_dir = os.environ["GA_TMP_DIR"]
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
           





         

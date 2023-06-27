import os
from zipfile import ZipFile, Path
import shutil
ga_static_dir= os.environ["GA_STATIC_DIR"]
ga_tmp_dir = os.environ["GA_TMP_DIR"]
def archive_files (end):
    archive = os.path.join(ga_static_dir,"archive.zip")
    for filename in os.listdir(ga_tmp_dir):
        file_source = os.path.join(ga_tmp_dir,filename)
        file_des = os.path.join("analytics", end, filename)
        full_path = os.path.join (archive, "analytics", end)
        archive_files= "/".join(["analytics", end, filename])
        
        with ZipFile(archive, "a") as archive_zip:
           # print (archive_files in archive_zip.namelist() )
            if archive_files not in archive_zip.namelist():               
                print (f'{filename} not archived ')                       
                archive_zip.write(file_source, arcname=file_des)
            
            else:
                print (f'{filename} is already archived no overwriting')
                continue
            archive_zip.close()
           

        
        # print (full_path)
        # if filename not in test.name:
        #     print (test)
        #     print (f'{filename} not archived ')
        #     with ZipFile(archive, "a") as archive_zip:            
        #         archive_zip.write(file_source, arcname=file_des)
        #     archive_zip.close()
        # else:
        #     print (f'{filename} is already archived no overwriting')

        # with ZipFile(archive, "a") as archive_zip:
           
        #     if not test.exists():                
        #         print (f'{test} not archived ')
        #         # with ZipFile(archive, "a") as archive_zip:            
        #         #     archive_zip.write(file_source, arcname=file_des)
        #         # archive_zip.close()
        #     else:
        #          print (test.exists())
        #          print (f'{test} is already archived no overwriting')


        # try:
        #     with ZipFile(archive, "x") as archive_zip:            
        #         archive_zip.write(file_source, arcname=file_des)
        # except FileExistsError as e:
        #     print (f'{file_des.split("/")[-1]} is already archived no overwriting')
        #     continue
        #archive_zip.close()




         

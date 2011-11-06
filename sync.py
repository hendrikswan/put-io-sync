#todo: check wanneer files download of dit al klaar exist en dieselfde size is
#todo: skip files wat al klaar gedownload het
#todo: probeer files delete wat nog op die server is en wat mens klaar gedownload het 
#todo: voordat mens files delete, check eers dat dit klaar geseed is, mens kan nie fi
# todo: do not download sample.avi files
#todo: progress bar

#TODO: moenie files delete wat nog nie klaar gedownload is nie

import putio 
import urllib2
import base64
import series_sort
import utils
import os
import time
from datetime import timedelta
import datetime
import time
from progressbar import Bar,   ETA, FileTransferSpeed,  Percentage, ProgressBar,  RotatingMarker
import ConfigParser

config = ConfigParser.ConfigParser()
config.readfp(open('defaults.ini'))

putio_uname = config.get("Defaults", "putio_uname")
putio_secret_key = config.get("Defaults", "putio_secret_key")
movies_folder = config.get("Defaults", "movies_folder")
series_folder = config.get("Defaults", "series_folder")
series_downloads_folder = config.get("Defaults", "series_downloads_folder")
archive_folder_name = "archived"

def get_root_folder(api, folder_name):
    all_folders = api.get_items()
    filter_lambda = lambda it: it.name==folder_name
    print "found %i items in the root" % len(all_folders)
    folders = filter(filter_lambda, all_folders)
    print "found %i items that matched the description" % len(folders)
    if len(folders) == 0: 
        print "couldn't find folder, going to create it: ", folder_name
        api.create_folder(name=folder_name)
        print "created the new folder"
        folders = filter(filter_lambda, api.get_items())
    return folders[0]

def download_file(url, file_name, target_dir):
    file_path = target_dir + "/" + file_name
    print "downloading file to ", file_path
    # try:
    base64string = base64.encodestring('%s:%s' % (putio_uname, putio_secret_key))[:-1]
    req = urllib2.Request(url)
    req.add_header("Authorization", "Basic %s" % base64string)
    u = urllib2.urlopen(req)
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    if(os.path.exists(file_path)):
        existing_size = os.path.getsize(file_path)
        print "existing path: %s, size: %i - download size: %i" % (file_path, existing_size, file_size)
        if(existing_size == file_size):
          return
    f = open(file_path, 'wb')    
    try:
        print "Downloading: %s Bytes %s" % (file_name, file_size)
        widgets = ["Download progress", Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA(), ' ', FileTransferSpeed()]
        pbar = ProgressBar(widgets=widgets, maxval=file_size).start()
        file_size_dl = 0
        block_sz = 48 * 1024
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            pbar.update(file_size_dl)
        pbar.finish()
    finally:  
        f.close()
  
def import_series():
    series = series_sort.SortSeries(series_downloads_folder, series_folder)
    series.sort()
    print 'Finished sorting your series'
  
  
 
def download_items(api, folder, target_folder):
    # active_transfers = api.get_transfers()
    #print "Found %i active transfers" % len(active_transfers)
    print "looking for items to download in folder: " + folder
    put_folder = get_root_folder(api, folder)
    new_items = api.get_items(parent_id=put_folder.id)
    # print "Found %i items in folder [%s] to download" % (len(new_items), folder)
    # new_items = filter(lambda download_item: len(filter(lambda transfer_item: transfer_item.id == download_item.id, active_transfers)) == 0, new_items)
    # print "After removing items that are still being transfered from new items in [%s], we have %i items left to download" % (folder, len(new_items))
    # return
    for item in new_items:

        #utils.reflect_item(item)
        print "downloading item %s" % (item.name)
        
        if len(api.get_items(id=item.id)) == 0:
            print "the item with name %s has been removed" % item.name
            continue
            
        #friendly_movie_name = mov.name.replace("-", " ").strip().replace(".", "_").replace(" ", "_")
        
        #movie_target = movies_folder + "/" +  friendly_movie_name + "/"
        # if not os.path.isdir(movie_target):
            # os.mkdir(movie_target)
            # print "created movie directory ", movie_target
        
        if item.type == "movie":
        #download_file(mov.download_url, mov.name, movie_target)
            download_file(item.download_url, item.name, target_folder)
        else:     
            friendly_item_name = item.name.replace("-", " ").strip().replace(".", "_").replace(" ", "_")
            item_target = target_folder + "/" +  friendly_item_name + "/"
            if not os.path.isdir(item_target):
                os.mkdir(item_target)
                print "created item directory ", item_target
            item_files = filter(lambda it: not it.is_dir, api.get_items(parent_id=item.id))
            #utils.print_items(movie_files)
            for it in item_files:
                download_file(it.download_url, it.name, item_target)
        
        #item.delete_item()
        item.move_item(target=get_root_folder(api, archive_folder_name).id)
        import_series()


if __name__=="__main__":
    api = putio.Api(putio_uname, putio_secret_key)
    while True: 
        try:
            #arch_folder=get_root_folder(api, archive_folder_name)
            #download_items(api, "test_series", movies_folder)            
            download_items(api, "series", series_downloads_folder)
            download_items(api, "movies", movies_folder)
        except Exception as inst:
            print inst
            utils.reflect_item(inst)
        finally:
            time.sleep(10)
      


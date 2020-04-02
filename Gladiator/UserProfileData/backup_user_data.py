from google.cloud import storage
from glob import glob
import os
from threading import Thread


client = storage.Client()
bucket = client.get_bucket('hut_assistant_user_info_storage')

def backup_single_profile(filename):
    thread = Thread(target=backup_single_profile_task, args=(filename,))
    thread.start()

def backup_single_profile_task(filename):
    try:
        blob = bucket.blob(filename)
        blob.upload_from_filename(filename=filename)
        #print(f"Uploaded {filename}")
    except ValueError:
        pass

def backup_profiles():
    print("Uploading profiles to cloud")
    for f_name in glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), '*.json')):
        blob = bucket.blob(f_name)
        blob.upload_from_filename(filename=f_name)
    print("Upload complete")
    
def download_profiles():
    print("Downloading all the files from cloud")
    for blob in bucket.list_blobs():
        try:
            blob.download_to_filename(filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), blob.name))
        except FileNotFoundError:
            pass
    print("Download complete")

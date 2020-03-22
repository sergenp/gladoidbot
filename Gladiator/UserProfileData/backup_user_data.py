from google.cloud import storage
from glob import glob
import os


client = storage.Client()
bucket = client.get_bucket('hut_assistant_user_info_storage')

def backup_profiles():
    print("Uploading profiles to cloud")
    for f_name in glob(os.path.join(os.path.dirname(__file__), '*.json')):
        blob = bucket.blob(f_name)
        blob.upload_from_filename(filename=f_name)
    print("Upload complete")
    
def download_profiles():
    print("Downloading all the files from cloud")
    for blob in bucket.list_blobs():
        blob.download_to_filename(filename=os.path.join(os.path.dirname(__file__), blob.name))
    print("Download complete")
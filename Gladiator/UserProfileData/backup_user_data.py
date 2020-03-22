from google.cloud import storage
from glob import glob


client = storage.Client()
# https://console.cloud.google.com/storage/browser/[bucket-id]/
bucket = client.get_bucket('hut_assistant_user_info_storage')

def backup_profiles():
    for f_name in glob('*.json'):
        blob = bucket.blob(f_name)
        blob.upload_from_filename(filename=f_name)

def download_profiles():
    for blob in bucket.list_blobs():
        blob.download_to_filename(filename=blob.name)
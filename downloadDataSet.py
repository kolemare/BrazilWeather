import os
import io
import zipfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Function to authenticate and create the drive service
def create_drive_service():
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

# Function to download the file
def download_file(service, file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False

    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))

    with open(file_name, 'wb') as f:
        fh.seek(0)
        f.write(fh.read())

# Function to extract the zip file
def extract_zip(file_name, extract_to):
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

# Main script
def main():
    service = create_drive_service()
    file_id = '1r5kwpE_3ngzBHBixWLNkbZV8H21XdTkX'
    file_name = 'archive.zip'
    dataset_dir = 'dataset'

    # Download the file
    download_file(service, file_id, file_name)

    # Extract the file
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
    extract_zip(file_name, dataset_dir)

    # Remove the zip file
    os.remove(file_name)

    print("Extraction complete. The dataset is available in the 'dataset' folder.")

if __name__ == '__main__':
    main()
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

def get_drive_service():
    """Authenticate and return the Google Drive service."""
    credentials = service_account.Credentials.from_service_account_file(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    service = build('drive', 'v3', credentials=credentials)
    return service

def get_documents(service, folder_id):
    """Get a list of documents from the specified folder in Google Drive."""
    query = f"'{folder_id}' in parents"
    result = service.files().list(q=query, fields="files(id, name)").execute()
    files = result.get('files', [])
    return files

def get_document_content(service, file_id):
    """Retrieve the raw content of a document from Google Drive."""
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    file.seek(0)
    return file.read()
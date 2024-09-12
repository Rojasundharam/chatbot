import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from file_processor import extract_file_text
from config import GOOGLE_APPLICATION_CREDENTIALS

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_APPLICATION_CREDENTIALS,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build('drive', 'v3', credentials=credentials)

def get_documents(service, folder_id):
    query = f"'{folder_id}' in parents"
    result = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    return result.get('files', [])

def get_document_content(service, file):
    file_id = file['id']
    mime_type = file['mimeType']
    
    if mime_type == 'application/vnd.google-apps.document':
        request = service.files().export_media(fileId=file_id, mimeType='text/plain')
    elif mime_type == 'application/vnd.google-apps.spreadsheet':
        request = service.files().export_media(fileId=file_id, mimeType='text/csv')
    elif mime_type == 'application/vnd.google-apps.presentation':
        request = service.files().export_media(fileId=file_id, mimeType='text/plain')
    else:
        request = service.files().get_media(fileId=file_id)
    
    file_content = io.BytesIO()
    downloader = MediaIoBaseDownload(file_content, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    file_content.seek(0)
    return file_content.read()

def index_documents(service, folder_id):
    files = get_documents(service, folder_id)
    documents = []
    for file in files:
        try:
            content = get_document_content(service, file)
            text = extract_file_text(file['name'], io.BytesIO(content))
            documents.append({
                'id': file['id'],
                'name': file['name'],
                'content': text
            })
        except Exception as e:
            print(f"Error processing file {file['name']}: {str(e)}")
    print(f"Indexed {len(documents)} documents")
    return documents
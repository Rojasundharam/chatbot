import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from file_processor import extract_file_text

# Load environment variables
load_dotenv()

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build('drive', 'v3', credentials=credentials)

def get_documents(service, folder_id):
    query = f"'{folder_id}' in parents"
    result = service.files().list(q=query, fields="files(id, name, mimeType, shortcutDetails)").execute()
    return result.get('files', [])

def get_actual_file_id(service, file):
    if file.get('mimeType') == 'application/vnd.google-apps.shortcut':
        shortcut_details = file.get('shortcutDetails', {})
        return shortcut_details.get('targetId')
    return file['id']

def get_document_content(service, file):
    file_id = get_actual_file_id(service, file)
    
    # Get the file metadata to determine its type
    file_metadata = service.files().get(fileId=file_id, fields="mimeType").execute()
    mime_type = file_metadata['mimeType']
    
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
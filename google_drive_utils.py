import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from elasticsearch import Elasticsearch
from file_processor import extract_file_text

# Load environment variables
load_dotenv()

# Correct Elasticsearch initialization
es = Elasticsearch(["http://localhost:9200"])

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build('drive', 'v3', credentials=credentials)

def get_documents(service, folder_id):
    query = f"'{folder_id}' in parents"
    result = service.files().list(q=query, fields="files(id, name)").execute()
    return result.get('files', [])

def get_document_content(service, file_id):
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    file.seek(0)
    return file.read()

def index_documents(service, folder_id):
    files = get_documents(service, folder_id)
    for file in files:
        content = get_document_content(service, file['id'])
        text = extract_file_text(file['name'], io.BytesIO(content))
        
        es.index(index="jkkn_documents", id=file['id'], body={
            'name': file['name'],
            'content': text
        })
    print(f"Indexed {len(files)} documents")
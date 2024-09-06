import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

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
    """Retrieve the content of a document from Google Drive with flexible encoding."""
    request = service.files().get_media(fileId=file_id)
    content = request.execute()

    try:
        # Try decoding with UTF-8 first
        return content.decode('utf-8')
    except UnicodeDecodeError:
        # If decoding fails, try ISO-8859-1 or any other encoding that might work
        return content.decode('ISO-8859-1')

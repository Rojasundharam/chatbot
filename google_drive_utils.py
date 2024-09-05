from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    )
    return build('drive', 'v3', credentials=credentials)

def get_documents(drive_service):
    results = drive_service.files().list(pageSize=10).execute()
    return results.get('files', [])

def get_document_content(drive_service, file_id):
    content = drive_service.files().get_media(fileId=file_id).execute()
    return content.decode('utf-8')

import os
from flask import current_app
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

class GoogleDriveService:
    def __init__(self):
        credentials_file = current_app.config['GOOGLE_CREDENTIALS_FILE']
        scopes = ['https://www.googleapis.com/auth/drive']
        
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file, scopes=scopes)
        
        self.service = build('drive', 'v3', credentials=credentials)
    
    def upload_file(self, file_path, mime_type, folder_id=None):
        """
        Upload a file to Google Drive
        
        Args:
            file_path (str): Path to the file to upload
            mime_type (str): MIME type of the file
            folder_id (str, optional): ID of the folder to upload to
        
        Returns:
            str: ID of the uploaded file
        """
        file_metadata = {
            'name': os.path.basename(file_path)
        }
        
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')
    
    def get_file_url(self, file_id):
        """
        Get the URL of a file in Google Drive
        
        Args:
            file_id (str): ID of the file
        
        Returns:
            str: URL of the file
        """
        # Make the file publicly accessible
        self.service.permissions().create(
            fileId=file_id,
            body={
                'type': 'anyone',
                'role': 'reader'
            }
        ).execute()
        
        # Get the file's web view link
        file = self.service.files().get(
            fileId=file_id,
            fields='webViewLink'
        ).execute()
        
        return file.get('webViewLink')
    
    def delete_file(self, file_id):
        """
        Delete a file from Google Drive
        
        Args:
            file_id (str): ID of the file to delete
        """
        self.service.files().delete(fileId=file_id).execute()
    
    def create_folder(self, folder_name, parent_folder_id=None):
        """
        Create a folder in Google Drive
        
        Args:
            folder_name (str): Name of the folder
            parent_folder_id (str, optional): ID of the parent folder
        
        Returns:
            str: ID of the created folder
        """
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        
        folder = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        return folder.get('id')
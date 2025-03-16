"""
Storage service for file operations.
"""
import os
import uuid
from datetime import datetime
from flask import current_app
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

class StorageService:
    """Service for file storage operations."""
    
    def __init__(self):
        """Initialize the storage service."""
        self._init_google_drive()
    
    def _init_google_drive(self):
        """Initialize Google Drive client."""
        credentials_file = current_app.config['GOOGLE_CREDENTIALS_FILE']
        scopes = ['https://www.googleapis.com/auth/drive']
        
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file, scopes=scopes)
        
        self.drive_service = build('drive', 'v3', credentials=credentials)
    
    def upload_file(self, file, folder=None):
        """
        Upload a file to storage.
        
        Args:
            file: File object or path
            folder (str, optional): Folder to upload to
            
        Returns:
            str: URL of the uploaded file
        """
        # Handle different file input types
        if isinstance(file, str):
            # File path
            file_path = file
            file_name = os.path.basename(file_path)
        else:
            # File object (e.g., from request.files)
            file_name = self._generate_unique_filename(file.filename)
            file_path = os.path.join('/tmp', file_name)
            file.save(file_path)
        
        # Get MIME type
        mime_type, _ = self._get_mime_type(file_name)
        
        # Upload to Google Drive
        file_id = self._upload_to_drive(file_path, file_name, mime_type, folder)
        
        # Get public URL
        url = self._get_file_url(file_id)
        
        # Clean up temporary file if needed
        if not isinstance(file, str):
            os.remove(file_path)
        
        return url
    
    def delete_file(self, file_url):
        """
        Delete a file from storage.
        
        Args:
            file_url (str): URL of the file to delete
            
        Returns:
            bool: True if successful
        """
        # Extract file ID from URL
        file_id = self._get_file_id_from_url(file_url)
        if not file_id:
            return False
        
        # Delete from Google Drive
        self.drive_service.files().delete(fileId=file_id).execute()
        
        return True
    
    def _upload_to_drive(self, file_path, file_name, mime_type, folder=None):
        """
        Upload a file to Google Drive.
        
        Args:
            file_path (str): Path to the file
            file_name (str): Name of the file
            mime_type (str): MIME type of the file
            folder (str, optional): Folder to upload to
            
        Returns:
            str: ID of the uploaded file
        """
        file_metadata = {
            'name': file_name
        }
        
        if folder:
            # Get or create folder
            folder_id = self._get_or_create_folder(folder)
            file_metadata['parents'] = [folder_id]
        
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        
        file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')
    
    def _get_file_url(self, file_id):
        """
        Get the URL of a file in Google Drive.
        
        Args:
            file_id (str): ID of the file
            
        Returns:
            str: URL of the file
        """
        # Make the file publicly accessible
        self.drive_service.permissions().create(
            fileId=file_id,
            body={
                'type': 'anyone',
                'role': 'reader'
            }
        ).execute()
        
        # Get the file's web view link
        file = self.drive_service.files().get(
            fileId=file_id,
            fields='webViewLink'
        ).execute()
        
        return file.get('webViewLink')
    
    def _get_or_create_folder(self, folder_name):
        """
        Get or create a folder in Google Drive.
        
        Args:
            folder_name (str): Name of the folder
            
        Returns:
            str: ID of the folder
        """
        # Check if folder exists
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
        results = self.drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        
        items = results.get('files', [])
        if items:
            return items[0]['id']
        
        # Create folder
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = self.drive_service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        return folder.get('id')
    
    def _get_file_id_from_url(self, url):
        """
        Extract file ID from Google Drive URL.
        
        Args:
            url (str): Google Drive URL
            
        Returns:
            str: File ID or None
        """
        # Example URL: https://drive.google.com/file/d/FILE_ID/view
        if 'drive.google.com' not in url:
            return None
        
        try:
            if '/file/d/' in url:
                file_id = url.split('/file/d/')[1].split('/')[0]
            elif 'id=' in url:
                file_id = url.split('id=')[1].split('&')[0]
            else:
                return None
            
            return file_id
        except Exception:
            return None
    
    def _generate_unique_filename(self, original_filename):
        """
        Generate a unique filename.
        
        Args:
            original_filename (str): Original filename
            
        Returns:
            str: Unique filename
        """
        filename, extension = os.path.splitext(original_filename)
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        return f"{filename}_{timestamp}_{unique_id}{extension}"
    
    def _get_mime_type(self, filename):
        """
        Get MIME type from filename.
        
        Args:
            filename (str): Filename
            
        Returns:
            tuple: (mime_type, extension)
        """
        import mimetypes
        
        mime_type, encoding = mimetypes.guess_type(filename)
        if mime_type is None:
            # Default to binary data
            mime_type = 'application/octet-stream'
        
        extension = os.path.splitext(filename)[1]
        
        return mime_type, extension
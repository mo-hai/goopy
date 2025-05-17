import os
import io
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from .BaseGoogleServiceAPI import BaseService, logger
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('googpy')


class DriveService(BaseService):
    """
    Class to interact with Google Drive API.
    Inherits from BaseService.
    Provides methods to copy files, download files, create files, and download folder.
    """

    def __init__(self):
        self.service_name = "drive"
        self.version = "v3"
        self.scopes = [
            'https://www.googleapis.com/auth/drive',
        ]
        super(DriveService, self).__init__()
    
    def copy_file(
            self,
            copy_title: str,
            file_link: str = None,
            file_id: str = None,
            folder_link: str = None,
            folder_id: str = None,
        ) -> str:
        """
        Creates the copy of Presentation or Sheets the user has access to.
        
        :param copy_title: Name of the copied file.
        :param file_link: Link to the file to be copied. If file_id is provided, this parameter is ignored.
        :param file_id: ID of the file to be copied. If not provided, it will be extracted from the link. (optional)
        :param folder_link: Link to the folder where the copied file will be placed.
        :param folder_id: ID of the folder where the copied file will be placed. If not provided, it will be extracted from the link. (optional)
        :return: ID of the copied file.
        """
        try:
            if not file_id:
                file_id = self._extract_id(file_link)
                logger.info(f"file_id: {file_id}")
            if not folder_id:
                parent_folder_id = self._extract_id(folder_link)
                logger.info(f"parent_folder_id: {parent_folder_id}")
            body = {"parents": [parent_folder_id], "name": copy_title}
            copy_id = self.service.files().copy(fileId=file_id, supportsAllDrives=True, body=body).execute().get("id")

        except HttpError as error:
            logger.error(f"Presentations not copied. An error occurred: {error}")
            return error

        return copy_id
    
    def get_folder_files(self, folder_link: str = None, folder_id: str = None, mimeType: str = None) -> list:
        """ Get files from a folder
        
        :param folder_link: Link to the folder to get files from. If file_id is provided, this parameter is ignored.
        :param folder_id: ID of the folder to get files from. If not provided, it will be extracted from the link. (optional)
        :param mimeType: MIME type of the files to filter by. If None, all files will be returned.
        :return: List of files in the folder.
        """

        if not folder_id:
            folder_id = self._extract_id(folder_link)
        query = f"'{folder_id}' in parents and mimeType='{mimeType}' and trashed=false" if mimeType else f"'{folder_id}' in parents and trashed=false"
        results = self.service.files().list(
            q=query,
            pageSize=1000,
            spaces="drive",
            fields="nextPageToken, files(id, name, mimeType)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        return results.get('files', [])
    
    def download_file(self, file_link: str = None, file_id: str = None, local_path: str = None, mime_type: str = None) -> None:
        """
        Downloads a file from Google Drive.

        :param file_link: Link to the file to download. If file_id is provided, this parameter is ignored.
        :param file_id: ID of the file to download. If not provided, it will be extracted from the link. (optional)
        :param local_path: Local path where the file will be saved.
        :param mime_type: MIME type of the file. If not provided, it will be extracted from the file metadata.
        :return: None
        """
        if not file_id:
            file_id = self._extract_id(file_link)
        export_formats = {
            'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        }
        export_format = export_formats.get(mime_type, None)

        if export_format:
            request = self.service.files().export_media(fileId=file_id, mimeType=export_format)
        else:
            request = self.service.files().get_media(fileId=file_id)

        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        try:
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logger.info(f"Download {int(status.progress() * 100)}%.")
            fh.seek(0)
            with open(local_path, 'wb') as f:
                f.write(fh.read())
            logger.info(f'File downloaded successfully as {local_path}.')
        except Exception as e:
            logger.error(f'An error occurred during download: {e}')

    def generate_access_link(self, file_id: str) -> str:
        """
        Generates a shareable link for the file.
        :param file_id: ID of the file.
        :return: Shareable link for the file.
        """

        return f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"

    def download_folder(self, folder_link: str = None, folder_id: str = None, local_path: str = None) -> dict:
        """
        Downloads all files from a Google Drive folder and saves them to a local path.

        :param folder_link: Link to the folder to download. If file_id is provided, this parameter is ignored.
        :param folder_id: ID of the folder to download. If not provided, it will be extracted from the link. (optional)
        :param local_path: Local path where the files will be saved.
        :return: Dictionary with file names as keys and their shareable links as values.
        """

        if not folder_id:
            folder_id = self._extract_id(folder_link)
        access_links = {}

        def download_and_map(folder_id, path_prefix):
            items = self.get_folder_files(folder_id)
            logger.debug(items)
            for item in items:
                item_id = item['id']
                item_name = item['name']
                item_mime_type = item['mimeType']
                item_path = os.path.join(path_prefix, item_name)

                if item_mime_type == 'application/vnd.google-apps.folder':
                    download_and_map(item_id, item_path)
                else:
                    self.download_file(item_id, item_path, item_mime_type)
                    access_links[item_name] = self.generate_access_link(item_id)

        download_and_map(folder_id, local_path)
        return access_links

    def create_file(
            self,
            file_name: str,
            file_type: str = 'spreadsheet',
            folder_id: str = None,
            folder_link: str = None
        ) -> str:
        """
        Creates an empty file (spreadsheet, document, or presentation) in the specified folder.

        :param file_name: Name of the file to create.
        :param file_type: Type of the file ('spreadsheet', 'document', 'presentation').
        :param folder_link: Link to the folder where the file will be created. If folder_id is provided, this parameter is ignored.
        :param folder_id: ID of the folder where the file will be created. If not provided, it will be extracted from the link. (optional)
        :return: ID of the created file.
        """
        if not folder_id:
            if not folder_link:
                logger.error("Either folder_id or folder_link must be provided.")
                raise ValueError("Either folder_id or folder_link must be provided.")
            folder_id = self._extract_id(folder_link)
        
        mime_types = {
            'spreadsheet': 'application/vnd.google-apps.spreadsheet',
            'document': 'application/vnd.google-apps.document',
            'presentation': 'application/vnd.google-apps.presentation'
        }
        
        if file_type not in mime_types:
            logger.error(f"Invalid file type: {file_type}. Supported types are: {list(mime_types.keys())}")
            raise ValueError(f"Invalid file type: {file_type}. Supported types are: {list(mime_types.keys())}")
        
        file_metadata = {
            'name': file_name,
            'mimeType': mime_types[file_type],
            'parents': [folder_id] if folder_id else []
        }
        try:
            file = self.service.files().create(body=file_metadata, fields='id').execute()
            logger.info(f"{file_type.capitalize()} '{file_name}' created with ID: {file.get('id')}")
            return file.get('id')
        except HttpError as error:
            logger.error(f"Failed to create {file_type}. An error occurred: {error}")
            raise error

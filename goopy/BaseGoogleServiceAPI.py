import os
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('googpy')


class BaseService(object):
    """
    Base class for Google API services.
    This class is not meant to be used directly, but rather as a base class for other Google API services.
    """

    def __init__(self, service_account_file: str = None):
        self.service_account_file = self._get_credentials(service_account_file)
        self.credentials = service_account.Credentials.from_service_account_file(self.service_account_file, scopes=self.scopes)
        self.service = self._build()
    
    def _get_credentials(self, service_account_file):
        """
        Returns the credentials used to authenticate with the Google API.
        Returns:
            google.oauth2.service_account.Credentials: The credentials used to authenticate with the Google API.
        """
        if service_account_file is None:
            service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if service_account_file is None:
            raise Exception(
                "The service_account_file option must be set either by passing service_account_file to the client or by setting the GOOGLE_APPLICATION_CREDENTIALS environment variable"
            )
        
        if not os.path.exists(service_account_file):
            logger.error(f"service_account_file does not exist.")
        elif not os.path.isfile(service_account_file):
            logger.error(f"service_account_file is not a file.")
        elif not os.access(service_account_file, os.R_OK):
            logger.error(f"service_account_file cannot be read.")
        
        return service_account_file

    def _build(self):
        service = build(self.service_name, self.version, credentials=self.credentials)
        return service
    
    def _extract_id(self, link: str):
        """
        Extracts the ID from a Google link.
        Args:
            link (str): The Google link to extract the ID from.
        Returns:
            str: The extracted ID.
        Raises:
            ValueError: If the link is not a valid Google link.
        """

        match = re.search(r'/(spreadsheets|presentation)/d/([a-zA-Z0-9-_]+)', link)
        match = match if match else re.search(r'/drive/(folders|d)/([a-zA-Z0-9-_]+)', link) # TODO: fix links like https://drive.google.com/drive/u/0/folders/....
        match = match if match else re.search(r'(id)=([a-zA-Z0-9_-]+)', link)
        if match:
            return match.group(2)  # Modify the group index to capture the ID
        else:
            raise ValueError("Invalid Google link")
    
    def _get_file_id(self, file_link: str = None, file_id: str = None) -> str:
        if not file_id:
            if not file_link:
                raise ValueError("Either file_link or file_id must be provided.")
            file_id = self._extract_id(file_link)
        return file_id


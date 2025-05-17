import re
from collections import defaultdict
from src.BaseGoogleServiceAPI import BaseService, logger
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('googpy')


class SlidesService(BaseService):
    """
    Class to interact with Google Slides API.
    Inherits from BaseService.
    Provides methods to get presentation, batch update, and manipulate slides.
    """

    def __init__(self):
        self.service_name = "slides"
        self.version = "v1"
        self.scopes = [
            'https://www.googleapis.com/auth/presentations'
        ]
        super(SlidesService, self).__init__()
    
    def get_presentation(self, file_link = None, file_id = None, fields='slides'):
        """
        Fetches a presentation from Google Slides.
        :param file_link: Link to the presentation. If file_id is provided, this parameter is ignored.
        :param file_id: ID of the presentation. If not provided, it will be extracted from the link. (optional)
        :param fields: Fields to be fetched from the presentation. Default is 'slides'.
        :return: The content of the presentation.
        """

        file_id = self._get_file_id(file_link, file_id)
        return self.service.presentations().get(presentationId=file_id, fields=fields).execute()
    
    def batch_update(self, requests_batch: list, link: str = None, file_id: str = None):
        """
        Updates a presentation with a batch of requests.
        :param requests_batch: List of requests to be executed
        :param link: Link to the presentation. If file_id is provided, this parameter is ignored.
        :param file_id: ID of the presentation. If not provided, it will be extracted from the link. (optional)
        :return: None
        """

        file_id = self._get_file_id(link, file_id)
        response = self.service.presentations().batchUpdate(
            body={'requests': requests_batch},
            presentationId=file_id,
            fields='',
        ).execute()
        logger.info('Presentation updated')
        return response

    def get_tags_from_speaker_notes(self, slides) -> dict:
        """
        Maps hashtags from speaker notes to slide ids in a presentation. Later used to delete slides with specific tags.
        :param slides: List of slides in the presentation.
        :return: Dictionary mapping hashtags to slide ids.
        """
        hashtag_slide_map = defaultdict(list)
        for slide in slides:
            note = slide['slideProperties']['notesPage']['pageElements'][1]['shape'].get('text')
            if note:
                note_text = note['textElements'][1]['textRun']['content']
                try:
                    tag = re.search(r'#[a-zA-Z0-9-_]+', note_text).group(0)
                except:
                    continue
                hashtag_slide_map[tag].append(slide['objectId'])
        return hashtag_slide_map

    def create_image_request(self, img_url: str, slide: dict, obj: dict) -> dict:
        request = {
            'createImage': {
                'url': img_url,
                'elementProperties': {
                    'pageObjectId': slide['objectId'],
                    'size': obj['size'],
                    'transform': obj['transform'],
                },
            }
        }
        return request
    
    def create_delete_object_request(self, obj_id: dict) -> dict:
        request = {'deleteObject': {'objectId': obj_id}}
        return request
    
    def create_replace_text_request(self, new_text: str, find_text: str = '{{CLIENT_NAME}}') -> dict:
        request = {
            "replaceAllText": {
                "containsText": {"matchCase": False, "text": find_text},
                "pageObjectIds": [],
                "replaceText": new_text,
            }
        }
        return request

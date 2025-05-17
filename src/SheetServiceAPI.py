import polars as pl
from src.BaseGoogleServiceAPI import BaseService, logger
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('googpy')


class SheetsService(BaseService):
    """
    Class to interact with Google Sheets API.
    This class provides methods to read, write, and manipulate Google Sheets.
    It inherits from BaseService which handles authentication and service creation.
    """

    def __init__(self):
        self.service_name = "sheets"
        self.version = "v4"
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        super(SheetsService, self).__init__()

    def get_sheet(self, file_link: str = None, file_id: str = None, page_id: int = 0, sheet_range: str = None) -> dict:
        """
        Fetches a specific sheet from a Google Spreadsheet.
        
        :param file_link: Link to the spreadsheet. If file_id is provided, this parameter is ignored.
        :param file_id: ID of the spreadsheet. If not provided, it will be extracted from the link. (optional)
        :param page_id: The index of the sheet to fetch (default is 0 for the first sheet).
        :param sheet_range: The range of the sheet to fetch (e.g., 'Sheet1!A1:C10').
        :return: The content of the sheet.
        """

        file_id = self._get_file_id(file_link, file_id)

        if not file_id:
            if not file_link:
                raise ValueError("Either link or sheet_id must be provided.")
            file_id = self._extract_id(file_link)
        
        if not sheet_range:
            response = self.service.spreadsheets().get(spreadsheetId=file_id).execute()
            sheet_range = response.get("sheets", [])[page_id].get("properties").get("title")
            logger.info(f"Parsing sheet range: {sheet_range}")
        
        content = self.service.spreadsheets().values().get(spreadsheetId=file_id, valueRenderOption='FORMATTED_VALUE', range=sheet_range).execute()
        logger.info(f"Sheet '{sheet_range}' from spreadsheet '{file_id}' downloaded")
        return content

    def __get_column_name(self, idx: int) -> str:
        """
        Given an index of a column returns the name of a column following the known spreadsheet naming: A, B, C, ..., AA, AB, ...
        """
        result = ''
        while idx > 0:
            letter_index = (idx - 1) % 26
            result += chr(letter_index + ord('A'))
            idx = (idx - 1) // 26
        return result[::-1]

    def __get_column_names(self, columns_num: int) -> list:
        output = []
        for i in range(1, columns_num+1):
            output.append(self.__get_column_name(i))
        return output

    def get_dataframe_from_sheet(
            self,
            file_link: str = None,
            file_id: str = None,
            sheet_range: str = 'Sheet1',
            sheet: dict = None,
            index: str = None,
            header_id: int = False
        ) -> pl.DataFrame:
        """
        Creates a pandas DataFrame from a Google Sheet object.
        :param file_link: Link to the spreadsheet. If file_id is provided, this parameter is ignored.
        :param file_id: ID of the spreadsheet. If not provided, it will be extracted from the link. (optional)
        :param sheet_range: The range of the sheet to fetch (e.g., 'Sheet1!A1:C10').
        :param sheet: The sheet object to convert to DataFrame. If not provided, it will be fetched using file_link or file_id.
        :param index: The column to set as the index of the DataFrame. If None, no index is set.
        :param header_id: The row to use as the header. If False, the first row is used.
        :return: A pandas DataFrame containing the data from the sheet.
        """
        if not sheet:
            try:
                sheet = self.get_sheet(file_link, file_id, sheet_range=sheet_range)
            except ValueError:
                raise ValueError("Either sheet or file_link or file_id must be provided.")
        
        if header_id:
            headers = sheet['values'][header_id]
        else:
            max_len = 0 
            for row in sheet['values']:
                if len(row) > max_len:
                    max_len = len(row)
            headers = self.__get_column_names(max_len)

        if index:
            return pl.DataFrame(sheet['values'], columns=headers).set_index(index, drop=False)
        return pl.DataFrame(sheet['values'], columns=headers)

    def update(self, file_link: str = None, file_id: str = None, range: str = None, values: list = None, append: bool = False):
        """
        Universal method to update a spreadsheet. Can either append a new row or update a specific cell range.
        
        :param file_link: Link to the spreadsheet. If file_id is provided, this parameter is ignored.
        :param file_id: ID of the spreadsheet. If not provided, it will be extracted from the link. (optional)
        :param range: The range to update (e.g., 'Sheet1!A1' or 'Sheet1!A1:C1').
        :param values: The values to update as a list of lists (e.g., [[value1, value2]]).
        :param append: If True, appends a new row instead of updating a specific range.
        """
        file_id = self._get_file_id(file_link, file_id)
        
        if append:
            response = self.service.spreadsheets().values().append(
                spreadsheetId=file_id,
                range=range,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': values}
            ).execute()
        else:
            response = self.service.spreadsheets().values().update(
                spreadsheetId=file_id,
                range=range,
                valueInputOption='RAW',
                body={'values': values}
            ).execute()
        
        logger.info(f"Spreadsheet updated. Response: {response}")
        return response

    def delete(self, file_link: str = None, file_id: str = None, 
                    sheet_id: int = 0, dimension: str = "ROWS", 
                    start_index: int = None, end_index: int = None):
        """
        Delete rows or columns from a spreadsheet.
        
        :param file_link: Link to the spreadsheet. If file_id is provided, this parameter is ignored.
        :param file_id: ID of the spreadsheet. If not provided, it will be extracted from the link. (optional)
        :param sheet_id: The ID of the sheet within the spreadsheet (default 0 for first sheet).
        :param dimension: "ROWS" to delete rows, "COLUMNS" to delete columns.
        :param start_index: The index where to start deleting (0-based, inclusive).
        :param end_index: The index where to end deleting (0-based, exclusive).
        :return: The response from the API.
        """
        file_id = self._get_file_id(file_link, file_id)
            
        if start_index is None:
            raise ValueError("start_index must be provided for deletion")
            
        if end_index is None:
            end_index = start_index + 1
            
        request_body = {
            'requests': [
                {
                    'deleteDimension': {
                        'range': {
                            'sheetId': sheet_id,
                            'dimension': dimension,
                            'startIndex': start_index,
                            'endIndex': end_index
                        }
                    }
                }
            ]
        }
        
        response = self.service.spreadsheets().batchUpdate(
            spreadsheetId=file_id,
            body=request_body
        ).execute()
        
        logger.info(f"Deleted {dimension.lower()} {start_index}-{end_index} from spreadsheet. Response: {response}")
        return response

    def insert(self, file_link: str = None, file_id: str = None,
        sheet_id: int = 0, dimension: str = "ROWS",
        start_index: int = None, number_to_insert: int = 1):
        """
        Insert rows or columns in a spreadsheet.
        
        :param file_link: Link to the spreadsheet. If file_id is provided, this parameter is ignored.
        :param file_id: ID of the spreadsheet. If not provided, it will be extracted from the link. (optional)
        :param sheet_id: The ID of the sheet within the spreadsheet (default 0 for first sheet).
        :param dimension: "ROWS" to insert rows, "COLUMNS" to insert columns.
        :param start_index: The index where to insert (0-based).
        :param number_to_insert: The number of rows/columns to insert (default 1).
        :return: The response from the API.
        """
        
        file_id = self._get_file_id(file_link, file_id)
            
        if start_index is None:
            raise ValueError("start_index must be provided for insertion")
            
        request_body = {
            'requests': [
                {
                    'insertDimension': {
                        'range': {
                            'sheetId': sheet_id,
                            'dimension': dimension,
                            'startIndex': start_index,
                            'endIndex': start_index + number_to_insert
                        },
                        'inheritFromBefore': True
                    }
                }
            ]
        }
        
        response = self.service.spreadsheets().batchUpdate(
            spreadsheetId=file_id,
            body=request_body
        ).execute()
        
        logger.info(f"Inserted {number_to_insert} {dimension.lower()} at position {start_index} in spreadsheet. Response: {response}")
        return response

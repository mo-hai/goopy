from goopy.DriveServiceAPI import DriveService
from goopy.SheetsServiceAPI import SheetsService
from goopy.SlidesServiceAPI import SlidesService


from dotenv import load_dotenv
load_dotenv()

import os
print(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))


def create_file(folder_link: str):

    file_name = "Test File"
    file_type = "presentation"  # Options: 'spreadsheet', 'document', 'presentation'
    
    try:
        drive_service = DriveService()
        file_id = drive_service.create_file(
            file_name=file_name,
            file_type=file_type,
            folder_link=folder_link,
        )
        
        access_link = drive_service.generate_access_link(file_id)
        
        print(f"File '{file_name}' created successfully")
        print(f"File ID: {file_id}")
        print(f"Access Link: {access_link}")
        
    except Exception as e:
        print(f"Error creating file: {str(e)}")

def append_rows_to_spreadsheet(spreadsheet_link: str):
    range = "Sheet1!A1"  # The range where to add the row
    row_values = [[1, "hello lala", "jj.kk"]] # The values to add
    multiple_rows = [
        [2, "row two", "data2"],
        [3, "row three", "data3"]
    ]
    
    try:
        sheets = SheetsService()
        response = sheets.update(
            file_link=spreadsheet_link,
            range=range,
            values=row_values,
            append=True # Append the values as a new row
        )
        print(f"Added new row successfully: {response}")
        
        response = sheets.update(
            file_link=spreadsheet_link,
            range="Sheet1",
            values=multiple_rows,
            append=True
        )
        print(f"Added multiple rows: {response}")
        
    except Exception as e:
        print(f"Error adding row: {str(e)}")

def add_column_to_spreadsheet(spreadsheet_link: str):
    column_range = "Sheet1!D1:D4" 
    values = [
        ["numbers"],  # Header
        [12],         # First value
        [0],          # Second value
        [9]           # Third value
    ]

    try:
        sheets_service = SheetsService()
        response = sheets_service.update(
            file_link=spreadsheet_link,
            range=column_range,
            values=values,
            append=False  # We're updating a specific range, not appending rows
        )
        print(f"Column 'numbers' added successfully with values [12, 0, 9]")
        return response
    except Exception as e:
        print(f"Error adding column: {str(e)}")
        return None

def insert_columns_rows_tp_spreadsheet(spreadsheet_link: str):

    try:
        sheets = SheetsService()

        response = sheets.insert(
            file_link=spreadsheet_link,
            sheet_id=0,                # First sheet in the spreadsheet
            dimension="ROWS",          # Insert rows (use "COLUMNS" for columns)
            start_index=5,             # Insert after row 5 (0-based, so this is the 6th row)
            number_to_insert=3         # Insert 3 rows
        )
        print(f"Inserted 3 rows successfully: {response}")
        
        # Example 2: Insert 2 columns at position 2 (after column B)
        response = sheets.insert(
            file_link=spreadsheet_link,
            sheet_id=0,                # First sheet in the spreadsheet
            dimension="COLUMNS",       # Insert columns
            start_index=2,             # Insert after column B (0-based: A=0, B=1, C=2, etc.)
            number_to_insert=2         # Insert 2 columns
        )
        print(f"Inserted 2 columns successfully: {response}")
        
    except Exception as e:
        print(f"Error inserting rows/columns: {str(e)}")


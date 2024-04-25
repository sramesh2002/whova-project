#!/usr/bin/env python3

import sys
import xlrd
from db_table import db_table
import logging

# Define the starting row for the data in the Excel file
START_ROW = 15

def create_table():
    """
    Creates and returns a database object for the 'agendas' table.
    The table schema is defined within the function.
    """
    # Initialize the database table with the specified schema
    db = db_table(
        "agendas",
        {
            "id": "integer PRIMARY KEY AUTOINCREMENT",  # Unique identifier for each row
            "date": "text REQUIRED",                   # Date of the agenda item
            "time_start": "text REQUIRED",             # Start time of the agenda item
            "time_end": "text REQUIRED",               # End time of the agenda item
            "session": "integer REQUIRED",             # Indicator of a session (1) or a sub-session (0)
            "parent_session": "integer",               # Reference to the parent session (if applicable)
            "title": "text REQUIRED",                  # Title of the agenda item
            "location": "text",                        # Location of the agenda item
            "description": "text",                     # Description of the agenda item
            "speaker": "text",                         # Speaker(s) for the agenda item
        }
    )
    return db

def insert_row(db, row_data):
    """
    Inserts a single row into the 'agendas' table.
    Handles the session logic and escapes string values for safe SQL insertion.
    """
    # Determine if the row represents a session or sub-session
    row_data['session'] = 1 if (row_data['session'].strip() == "Session") else 0
    
    # For sessions, 'parent_session' should be None; otherwise, keep the existing 'parent_session' value
    if row_data['session']:
        row_data['parent_session'] = None

    # Escape single quotes in text fields to prevent SQL injection
    for key in ['title', 'location', 'description', 'speaker']:
        row_data[key] = row_data[key].strip().replace("'", "''")  

    # Insert the row into the database, logging any errors that occur
    try:
        row_id = db.insert(row_data)
        return row_id
    except Exception as e:
        return None

def process_excel_file(file_name):
    """
    Processes each row of an Excel file and inserts the data into the database.
    Assumes the file format is consistent and starts reading data from the predefined START_ROW.
    """
    # Attempt to open the provided Excel file and read its contents
    try:
        book = xlrd.open_workbook(file_name)
        sheet = book.sheet_by_index(0)
        db = create_table()

        # Variable to hold the ID of the current parent session, if any
        parent_session = None

        # Loop through each row in the Excel sheet, starting at START_ROW
        for row_idx in range(START_ROW, sheet.nrows):
            # Read data for each cell in the row
            row = sheet.row(row_idx)
            row_data = {
                "date": row[0].value,
                "time_start": row[1].value,
                "time_end": row[2].value,
                "session": row[3].value,
                "title": row[4].value,
                "location": row[5].value,
                "description": row[6].value,
                "speaker": row[7].value,
                "parent_session": parent_session,
            }
            # Insert the row into the database and update 'parent_session' if needed
            parent_session = insert_row(db, row_data)
            
        print("Database has been initalized and values have been inserted!")
        
    # Catch any exceptions that occur while processing the file
    except Exception as e:
        print(f"Error occurred while processing the Excel file {file_name}: {e}")

def main():
    """
    Main function that checks command line arguments and initiates the processing of the Excel file.
    """
    # Check for the correct number of command line arguments
    if len(sys.argv) != 2:
        print("Incorrect number of arguments passed. Expected usage: ./import_agenda.py <filename>")
        return

    # Process the provided Excel file
    file_name = sys.argv[1]
    process_excel_file(file_name)

if __name__ == '__main__':
    main()

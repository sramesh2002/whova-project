#!/usr/bin/env python3

import sys
from db_table import db_table
import xlrd
import logging

START_ROW = 15
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_table():
    """ Creates a table for storing agenda details and returns the db object. """
    db = db_table(
        "agendas",
        {
            "id": "integer PRIMARY KEY AUTOINCREMENT",
            "date": "text REQUIRED",
            "time_start": "text REQUIRED",
            "time_end": "text REQUIRED",
            "session": "integer REQUIRED",
            "parent_session": "integer",
            "title": "text REQUIRED",
            "location": "text",
            "description": "text",
            "speaker": "text",
        }
    )
    return db

def insert_row(db, row_data):
    """ Insert a single row into the database and handle the session logic. """
    row_data['session'] = 1 if (row_data['session'].strip() == "Session") else 0
    if row_data['session']:
        row_data['parent_session'] = None

    # Apply escaping to all string fields to prevent SQL injection and errors
    for key in ['title', 'location', 'description', 'speaker']:
        row_data[key] = row_data[key].strip().replace("'", "''")  

    try:
        return db.insert(row_data)
    except Exception as e:
        logging.error(f"Error inserting row: {e}")
        return None

def process_excel_file(file_name):
    """ Process each row of the Excel file and insert data into the database. """
    try:
        book = xlrd.open_workbook(file_name)
        sheet = book.sheet_by_index(0)
        db = create_table()
        parent_session = None

        for row_idx in range(START_ROW, sheet.nrows):
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
            parent_session = insert_row(db, row_data)

    except Exception as e:
        logging.error(f"Error opening file {file_name}: {e}")

def main():
    if len(sys.argv) != 2:
        logging.error("Incorrect number of arguments passed!")
        return

    file_name = sys.argv[1]
    process_excel_file(file_name)

if __name__ == '__main__':
    main()

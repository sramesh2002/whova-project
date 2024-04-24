#!/usr/bin/env python3

import sys
import logging
from db_table import db_table

# Columns that are expected to be queried
COLUMNS = ["date", "time_start", "time_end", "title", "location", "description", "speaker"]

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_table():
    """Create and return a database table object."""
    logging.info("Creating the 'agendas' table...")
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
    logging.info("Database table created successfully.")
    return db

def format_result(result):
    """Format database result for printing in a concise format, handling empty values."""
    session_type = "Session" if result.get("session") else "Subsession"
    title = result.get('title', 'N/A')
    location = result.get('location', 'N/A')
    description = result.get('description', 'N/A') if result.get('description') else "<No Description>"
    speakers = result.get('speaker', 'N/A') if result.get('speaker') else "<No Speakers>"
    date = result.get('date', 'N/A')
    time_start = result.get('time_start', 'N/A')
    time_end = result.get('time_end', 'N/A')

    return (f"Date: {date}, Time: {time_start} to {time_end}, "
            f"Title: {title}, Location: {location}, Description: {description}, "
            f"{session_type}, Speakers: {speakers}")

def fetch_and_print_results(db, column, value):
    """Fetch results based on a column and value and print formatted results."""
    if column == 'speaker':
        where_clause = f"{column} LIKE '%{value}%'"
    else:
        where_clause = {column: value}
    
    logging.info(f"Fetching results with where clause: {where_clause}")
    results = db.select_custom(where=where_clause) if isinstance(where_clause, str) else db.select(where=where_clause)
    for result in results:
        print(format_result(result))
        if result.get("session"):
            fetch_and_print_results(db, "parent_session", result['id'])
def main():
    if len(sys.argv) < 3:
        logging.error("Incorrect number of arguments passed. Usage: <column> <value>")
        print("Usage: <column> <value>")
        return

    column = sys.argv[1]
    if column not in COLUMNS:
        logging.error(f"Invalid column specified: {column}. Valid columns are {COLUMNS}.")
        print(f"Invalid column. Choose from {COLUMNS}.")
        return

    # Concatenate all parts of the value to accommodate spaces in inputs like descriptions
    value = ' '.join(sys.argv[2:])

    db = create_table()
    fetch_and_print_results(db, column, value)

if __name__ == "__main__":
    main()

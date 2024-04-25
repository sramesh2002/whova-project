#!/usr/bin/env python3

import sys
import logging
from db_table import db_table

# Define the expected columns for querying the database
COLUMNS = ["date", "time_start", "time_end", "title", "location", "description", "speaker"]

def create_table():
    """
    Create and return a database table object.
    Initializes the 'agendas' table with the specified schema in the database.
    """
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

def format_result(result):
    """
    Format a database result for printing.
    Constructs a user-friendly string representation of a result row, handling any empty fields gracefully.
    """
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
    """
    Fetch and print results based on a specified column and value.
    Executes a database query and prints out the formatted results.
    Recursively fetches and prints sub-session results if the result has an associated session.
    """
    if column == 'speaker':
        where_clause = f"{column} LIKE '%{value}%'"
    else:
        where_clause = {column: value}
    
    results = db.select_custom(where=where_clause) if isinstance(where_clause, str) else db.select(where=where_clause)
    for result in results:
        print(format_result(result))
        if result.get("session"):
            fetch_and_print_results(db, "parent_session", result['id'])

def main():
    """
    The main function that processes command-line arguments and initiates the database query.
    It checks for the correct number of arguments and validates the column name.
    Reads description values from a file if specified, and replaces single quotes with escaped ones for SQL queries.
    """
    # Check if the correct number of arguments is passed
    if len(sys.argv) < 3:
        print("Incorrect number of arguments passed. Usage: <column> <value>")
        print("Usage: <column> <value>")
        return

    # Extract column name from the first argument
    column = sys.argv[1]
    if column not in COLUMNS:
        print(f"Invalid column specified: {column}. Valid columns are {COLUMNS}.")
        print(f"Invalid column. Choose from {COLUMNS}.")
        return

    # Handle 'description' column differently by reading from a file
    if column == 'description':
        filename = ' '.join(sys.argv[2:])
        with open(filename, 'r') as file:
            value = file.read().strip()
            value = value.replace("'", "''")  # Escape single quotes for SQL query
    else:
        value = ' '.join(sys.argv[2:])  # Join the remaining arguments to form the value

    db = create_table()
    fetch_and_print_results(db, column, value)

if __name__ == "__main__":
    main()

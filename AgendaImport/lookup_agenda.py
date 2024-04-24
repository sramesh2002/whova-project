import sys
from db_table import db_table
import logging

COLUMNS = ["date", "time_start", "time_end", "title", "location", "description", "speaker"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_table():
    """Create and return a database table object."""
    logging.info("Creating database table...")
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


def fetch_and_print_results(db, where_clause, is_custom=False):
    """Fetch results based on a where clause and print formatted results."""
    #logging.info(f"Fetching results with where clause: {where_clause}")
    results = db.select(where=where_clause)
    for result in results:
        print(format_result(result))
        if result.get("session"):
            sub_where = {"parent_session": result['id']}
            #logging.info(f"Fetching sub-session results for session ID {result['id']}")
            fetch_and_print_results(db, sub_where, is_custom=True)

def main():
    if len(sys.argv) < 3:
        logging.error("Incorrect number of arguments passed!")
        print("Usage: <column> <value>")
        return

    column = sys.argv[1]
    if column not in COLUMNS:
        logging.error(f"Invalid column specified: {column}")
        print("Invalid column")
        return
    
    value = ' '.join(sys.argv[2:])  # This joins all parts of the value into one string

    db = create_table()
    where = {column: value} if column != "speaker" else f"{column} LIKE '%{value}%'"
    fetch_and_print_results(db, where)

if __name__ == "__main__":
    main()

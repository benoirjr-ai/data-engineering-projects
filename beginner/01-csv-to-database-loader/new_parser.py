import csv
import logging
from pathlib import Path

def get_csv_reader(file_path: str):
    """ 
    Programatically opens a CSV, detects its dialect, 
    and yields rows to keep memory usage low.
    """
    path = Path(file_path)
    if not path.exists():
        logging.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"No file at {file_path}")
    
    try:
        # 1. Open file with 'utf-8-sig' to handle potential Excel BOM
        file = open(path, mode='r', encoding='utf-8-sig', newline='')

        # 2. Sniff the dialect (comma, tab, semicolon)
        sample = file.read(2048)
        file.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except csv.Error:
            dialect = 'excel'

        # 3. Create a DictReader for named-column access
        return csv.DictReader(file, dialect=dialect), file
    
    except csv.Error as e:
        logging.error(f"Could not parse CSV structure: {e}")
        raise 
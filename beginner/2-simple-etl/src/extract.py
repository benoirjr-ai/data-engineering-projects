import csv
from pathlib import Path


def extract(file_path: Path) -> list[dict[str, str]]:
    """
    Read customer records from a CSV file.

    The extract stage is responsible only for reading the data.
    It should NOT clean, validate, or transform the records.
    """

    # Check that the input file exists before trying to open it.
    # This gives us a clear error message if the file path is wrong.
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    # Open the CSV file for reading.
    # encoding="utf-8" handles standard text encoding.
    # newline="" allows Python's CSV module to handle line endings correctly.
    with file_path.open(
        mode="r",
        encoding="utf-8",
        newline=""
    ) as file:

        # DictReader reads each CSV row as a dictionary.
    
        reader = csv.DictReader(file)

        # Return all records as a list of dictionaries.
        #
        # Important:
        # We keep the values exactly as they appear in the CSV.
        # Cleaning and validation will happen later in transform.py.
        return list(reader)

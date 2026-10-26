"""
Handle CSV files that fail validation.

Invalid files are moved into the project's quarantine directory
so they cannot accidentally continue through the ingestion pipeline.
"""

import json 
import shutil
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
QUARANTINE_DIR = PROJECT_ROOT / "data" / "quarantine"

def quarantine_file(file_path, errors):
    """
    Move an invalid file to quarantine and save its error report.

    Args:
        file_path: Path to the invalid CSV file.
        errors: List of ValidationError objects.

    Returns:
        Path to the quarantined CSV file.
    """

    source = Path(file_path)

    if not source.is_file():
        raise FileNotFoundError(
            f"Cannot quarantine a file that does not exist: {source}"
        )

    # Create the quarantine directory if it does not exist.
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    # Add a UTC timestamp to avoid overwriting previous quarantined files.
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination = QUARANTINE_DIR / f"{source.stem}_{timestamp}{source.suffix}"

    # Move the original file rather than making an extra copy.
    shutil.move(str(source), str(destination))

    # Save a seperate JSON report explaining why validation failed.
    report_path = destination.with_suffix(".errors.json")

    report = {
        "original_filename": source.name,
        "quarantined_filename": destination.name,
        "quaratined_at_utc": datetime.now(timezone.utc).isoformat(),
        "errors": [
            {
                "category": error.category,
                "message": error.message,
                "row_number": error.row_number,
            }
            for error in errors
        ],
    }

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    return destination
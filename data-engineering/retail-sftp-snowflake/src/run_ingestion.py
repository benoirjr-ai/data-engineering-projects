
"""Run the CSV ingestion workflow with Snowflake loading enabled."""

from pathlib import Path

from src.ingestion import process_file
from src.snowflake_loader import load_csv_to_snowflake


def main():
    # Locate the sample CSV relative to the project root.
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "raw" / "sales_2026-10-24.csv"

    # Validate the file, load it into Snowflake, and update the registry.
    result = process_file(
        csv_path,
        loader=load_csv_to_snowflake,
    )

    print("\nIngestion result:")
    print(f"Status: {result['status']}")
    print(f"Rows: {result['row_count']}")
    print(f"File hash: {result['file_hash']}")

    if result["errors"]:
        print("Errors:")
        for error in result["errors"]:
            print(error)


if __name__ == "__main__":
    main()

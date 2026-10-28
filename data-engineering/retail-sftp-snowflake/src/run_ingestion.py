
"""Run the SFTP-to-Snowflake CSV ingestion workflow."""

from src.ingestion import process_file
from src.sftp_download import download_from_sftp
from src.snowflake_loader import load_csv_to_snowflake


def main():
    # Step 1: Download the CSV from the SFTP server.
    # The downloader returns the path to the local landing file.
    try:
        csv_path = download_from_sftp("sales_2026-10-24.csv")
    except Exception as error:
        print(f"SFTP download failed: {error}")
        raise

    # Step 2: Validate the downloaded file and load it into Snowflake.
    # process_file manages validation, quarantine, retries, and registry status.
    result = process_file(
        csv_path,
        loader=load_csv_to_snowflake,
    )

    # Step 3: Report the ingestion outcome.
    print("\nIngestion result:")
    print(f"Status: {result['status']}")
    print(f"Rows: {result['row_count']}")
    print(f"File hash: {result['file_hash']}")

    if result["errors"]:
        print("Errors:")
        for error in result["errors"]:
            print(error)

    # Return the result so the workflow can be tested programmatically.
    return result


if __name__ == "__main__":
    main()

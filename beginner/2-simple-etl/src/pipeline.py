from pathlib import Path

from src.extract import extract
from src.transform import transform
from src.load import get_connection, load_customer, quarantine_record


def run_pipeline():
    """
    Run the complete customer ETL pipeline.

    Flow:
        Extract → Transform → Load
    """

    # ---------------------------------------------------------
    # 1. EXTRACT
    # ---------------------------------------------------------

    file_path = Path("data/customer.csv")

    raw_records = extract(file_path)

    print(f"Extracted {len(raw_records)} records.")

    # ---------------------------------------------------------
    # 2. CONNECT TO DATABASE
    # ---------------------------------------------------------

    connection = get_connection()

    # Keep track of what happened during the pipeline run.
    valid_count = 0
    invalid_count = 0

    try:

        # -----------------------------------------------------
        # 3. TRANSFORM + LOAD
        # -----------------------------------------------------

        for raw_record in raw_records:

            # Transform the original CSV record.
            result = transform(raw_record)

            # -------------------------------------------------
            # VALID RECORD
            # -------------------------------------------------

            if result["status"] == "valid":

                load_customer(
                    connection,
                    result["record"],
                )

                valid_count += 1

            # -------------------------------------------------
            # INVALID RECORD
            # -------------------------------------------------

            else:

                quarantine_record(
                    connection,
                    raw_record,
                    result["errors"],
                )

                invalid_count += 1

    finally:
        # Always close the database connection,
        # even if something goes wrong.
        connection.close()

    # ---------------------------------------------------------
    # 4. PIPELINE SUMMARY
    # ---------------------------------------------------------

    print("\nPipeline completed.")
    print(f"Valid records loaded: {valid_count}")
    print(f"Invalid records quarantined: {invalid_count}")


if __name__ == "__main__":
    run_pipeline()

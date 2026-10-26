
"""Load validated sales CSV files into Snowflake safely."""

from pathlib import Path

from src.file_fingerprint import calculate_file_hash
from src.snowflake_connection import get_snowflake_connection


STAGE_NAME = "RETAIL_DB.RAW.RETAIL_LOAD_STAGE"
FILE_FORMAT = "RETAIL_DB.RAW.RETAIL_CSV_FORMAT"
STAGING_TABLE = "RETAIL_DB.RAW.SALES_STAGING"
TARGET_TABLE = "RETAIL_DB.RAW.SALES_RAW"

COLUMNS = [
    "TRANSACTION_ID",
    "SALE_DATE",
    "STORE_ID",
    "PRODUCT_ID",
    "PRODUCT_CATEGORY",
    "QUANTITY",
    "UNIT_PRICE",
    "DISCOUNT_AMOUNT",
    "SALES_AMOUNT",
]


def load_csv_to_snowflake(file_path):
    """
    Load a validated CSV into staging, then merge new transactions.

    Identical existing transactions are ignored.
    Conflicting transactions are rejected.
    """

    path = Path(file_path).resolve()

    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    if path.suffix.lower() != ".csv":
        raise ValueError("Only CSV files can be loaded.")

    # Use the file content hash to separate different versions of a file.
    file_hash = calculate_file_hash(path)
    stage_prefix = f"@{STAGE_NAME}/{file_hash}"
    staged_filename = f"{path.name}.gz"
    staged_file = f"{file_hash}/{staged_filename}"

    connection = get_snowflake_connection()
    transaction_started = False

    try:
        with connection.cursor() as cursor:
            # Step 1: Upload the CSV to its hash-specific stage path.
            file_uri = f"file://{path.as_posix()}"

            put_sql = (
                f"PUT '{file_uri}' "
                f"{stage_prefix} "
                "AUTO_COMPRESS=TRUE "
                "OVERWRITE=FALSE"
            )

            cursor.execute(put_sql)
            upload_results = cursor.fetchall()

            if not upload_results:
                raise RuntimeError("Snowflake returned no upload result.")

            print("Upload result:")
            for result in upload_results:
                print(result)

            # Step 2: Refresh staging for this load.
            # FORCE=TRUE is intentional here because staging is cleared
            # before every COPY. It does not force-load into the target.
            cursor.execute(f"TRUNCATE TABLE {STAGING_TABLE}")

            copy_sql = f"""
                COPY INTO {STAGING_TABLE}
                FROM @{STAGE_NAME}
                FILES = ('{staged_file}')
                FILE_FORMAT = (FORMAT_NAME = '{FILE_FORMAT}')
                FORCE = TRUE
                ON_ERROR = 'ABORT_STATEMENT'
            """

            cursor.execute(copy_sql)
            load_results = cursor.fetchall()

            if len(load_results) != 1:
                raise RuntimeError(
                    "Expected exactly one result from COPY INTO."
                )

            copy_result = load_results[0]
            load_status = copy_result[1]
            rows_loaded = int(copy_result[3])

            print("\nStaging load result:")
            for result in load_results:
                print(result)

            if load_status != "LOADED":
                raise RuntimeError(
                    f"Unexpected staging load status: {load_status}"
                )

            if rows_loaded == 0:
                raise RuntimeError("Snowflake loaded zero rows.")

            # Step 3: Start a transaction for conflict checking and MERGE.
            cursor.execute("BEGIN TRANSACTION")
            transaction_started = True

            differences = " OR ".join(
                f"t.{column} IS DISTINCT FROM s.{column}"
                for column in COLUMNS
                if column != "TRANSACTION_ID"
            )

            conflict_sql = f"""
                SELECT COUNT(*)
                FROM {STAGING_TABLE} s
                JOIN {TARGET_TABLE} t
                    ON t.TRANSACTION_ID = s.TRANSACTION_ID
                WHERE {differences}
            """

            cursor.execute(conflict_sql)
            conflict_count = int(cursor.fetchone()[0])

            if conflict_count:
                raise ValueError(
                    f"Found {conflict_count} transaction ID conflict(s). "
                    "Existing transaction values were not overwritten."
                )

            # Step 4: Insert only transaction IDs not already in the target.
            column_list = ", ".join(COLUMNS)
            source_values = ", ".join(
                f"s.{column}" for column in COLUMNS
            )

            merge_sql = f"""
                MERGE INTO {TARGET_TABLE} t
                USING {STAGING_TABLE} s
                    ON t.TRANSACTION_ID = s.TRANSACTION_ID
                WHEN NOT MATCHED THEN
                    INSERT ({column_list})
                    VALUES ({source_values})
            """

            cursor.execute(merge_sql)
            merge_results = cursor.fetchall()

            connection.commit()
            transaction_started = False

            print("\nMerge result:")
            for result in merge_results:
                print(result)

            return {
                "upload_results": upload_results,
                "load_results": load_results,
                "merge_results": merge_results,
                "rows_loaded_to_staging": rows_loaded,
            }

    except Exception:
        if transaction_started:
            connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    csv_path = (
        project_root / "data" / "raw" / "sales_2026-10-24.csv"
    )

    result = load_csv_to_snowflake(csv_path)
    print("\nLoading operation completed.")
    print(f"Rows loaded into staging: {result['rows_loaded_to_staging']}")

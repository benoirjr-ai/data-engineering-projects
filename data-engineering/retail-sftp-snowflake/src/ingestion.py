
"""
Coordinate file ingestion.

Current workflow:
1. Calculate the file's SHA-256 fingerprint.
2. Skip files that have already been processed successfully.
3. Register a new processing attempt.
4. Validate the CSV file.
5. Quarantine invalid files and record failures.
6. Leave valid files in PROCESSING until the data load succeeds.
"""

from pathlib import Path

from src.file_fingerprint import calculate_file_hash
from src.file_registry import FileRegistry
from src.file_validator import validate_file
from src.quarantine import quarantine_file


def process_file(file_path, registry=None, loader=None):
    """
    Process a CSV file through fingerprinting and validation.

    Args:
        file_path: Path to the incoming CSV file.
        registry: Optional FileRegistry instance, useful for testing.
    
    loader: Optional function that uploads and loads a validated CSV.
                If omitted, the function validates the file only.

    Returns:
        A dictionary describing the processing outcome.
    """

    path = Path(file_path)

    # Use the supplied registry or create the default registry.
    if registry is None:
        registry = FileRegistry()

    # Step 1: Calculate a content-based fingerprint.
    # If the file does not exist, return a safe rejection result.
    try:
        file_hash = calculate_file_hash(path)
    except (FileNotFoundError, OSError) as error:
        return {
            "status": "REJECTED",
            "row_count": 0,
            "errors": [str(error)],
            "quarantined_path": None,
            "file_hash": None,
        }

    # Step 2: Skip files already processed successfully.
    if registry.should_skip(file_hash):
        return {
            "status": "SKIPPED",
            "row_count": 0,
            "errors": [],
            "quarantined_path": None,
            "file_hash": file_hash,
        }

    # Step 3: Record the attempt before validation.
    registry.mark_processing(file_hash, path.name)

    # Step 4: Validate the CSV file.
    result = validate_file(path)

    # Step 5: Quarantine invalid files and record the failure.
    if not result.valid:
        quarantined_path = None

        if path.is_file():
            try:
                quarantined_path = quarantine_file(path, result.errors)
            except (OSError, ValueError) as error:
                # Keep the failure visible if quarantine itself fails.
                registry.mark_failed(
                    file_hash,
                    f"Validation failed; quarantine failed: {error}",
                )
                return {
                    "status": "FAILED",
                    "row_count": result.row_count,
                    "errors": result.errors + [str(error)],
                    "quarantined_path": None,
                    "file_hash": file_hash,
                }

        error_summary = "; ".join(
            error.message for error in result.errors
        )

        registry.mark_failed(file_hash, error_summary)

        return {
            "status": "REJECTED",
            "row_count": result.row_count,
            "errors": result.errors,
            "quarantined_path": quarantined_path,
            "file_hash": file_hash,
        }

        # Step 6: Validation succeeded.
    # If no loader was supplied, stop after validation.
    if loader is None:
        return {
            "status": "VALIDATED",
            "row_count": result.row_count,
            "errors": [],
            "quarantined_path": None,
            "file_hash": file_hash,
        }

    # Step 7: Load the validated CSV into Snowflake.
    try:
        load_result = loader(path)

        # Confirm that Snowflake returned exactly one load result.
        load_results = load_result.get("load_results", [])

        if len(load_results) != 1:
            raise RuntimeError(
                "Expected exactly one Snowflake load result."
            )

        snowflake_result = load_results[0]

        # Snowflake's COPY INTO result contains:
        # index 1: status
        # index 3: number of rows loaded
        load_status = snowflake_result[1]
        rows_loaded = int(snowflake_result[3])

        if load_status != "LOADED":
            raise RuntimeError(
                f"Unexpected Snowflake load status: {load_status}"
            )

        if rows_loaded != result.row_count:
            raise RuntimeError(
                f"Row count mismatch: validated {result.row_count}, "
                f"but Snowflake loaded {rows_loaded}."
            )

        # Record success only after the load is confirmed.
        registry.mark_processed(file_hash)

        return {
            "status": "PROCESSED",
            "row_count": rows_loaded,
            "errors": [],
            "quarantined_path": None,
            "file_hash": file_hash,
        }

    except Exception as error:
        # Make failed loads visible and eligible for retry.
        registry.mark_failed(file_hash, str(error))

        return {
            "status": "FAILED",
            "row_count": result.row_count,
            "errors": [str(error)],
            "quarantined_path": None,
            "file_hash": file_hash,
        }
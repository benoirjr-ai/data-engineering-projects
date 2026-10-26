
"""
Validate a retail sales CSV before loading it into Snowflake.

Responsibilities:
1. Check that the file exists and is not empty.
2. Validate the CSV header against the expected schema.
3. Validate required values, dates, and numeric fields.
4. Detect duplicate transaction IDs within the file.
5. Validate the sales calculation.
6. Collect detectable errors instead of stopping at the first bad row.

This module validates files only. Quarantine, logging, and Snowflake
loading will be handled by separate modules.
"""

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from src.schema import EXPECTED_COLUMNS, REQUIRED_COLUMNS
from src.validation_models import ValidationError, ValidationResult


def validate_headers(actual_columns):
    """
    Validate the CSV header.

    Return a list of structured validation errors.
    """

    errors = []

    # A CSV without a header cannot be checked against our schema.
    if actual_columns is None:
        return [
            ValidationError(
                category="SCHEMA_ERROR",
                message="CSV header is missing.",
            )
        ]

    # Identify expected columns that are missing.
    missing_columns = set(EXPECTED_COLUMNS) - set(actual_columns)

    # Identify columns that are not part of our expected schema.
    unexpected_columns = set(actual_columns) - set(EXPECTED_COLUMNS)

    if missing_columns:
        errors.append(
            ValidationError(
                category="SCHEMA_ERROR",
                message=f"Missing columns: {sorted(missing_columns)}",
            )
        )

    if unexpected_columns:
        errors.append(
            ValidationError(
                category="SCHEMA_ERROR",
                message=f"Unexpected columns: {sorted(unexpected_columns)}",
            )
        )

    # Duplicate headers can make CSV field mapping ambiguous.
    if len(actual_columns) != len(set(actual_columns)):
        errors.append(
            ValidationError(
                category="SCHEMA_ERROR",
                message="Duplicate column names detected.",
            )
        )

    return errors


def validate_row(row, line_number, seen_transaction_ids):
    """
    Validate one CSV row.

    Return all detectable validation errors for this row.
    """

    errors = []

    # Check that every required field has a value.
    missing_values = [
        column
        for column in REQUIRED_COLUMNS
        if row.get(column) is None or not row[column].strip()
    ]

    if missing_values:
        errors.append(
            ValidationError(
                category="MISSING_VALUE",
                message=f"Missing values in {missing_values}.",
                row_number=line_number,
            )
        )

        # Avoid checks that depend on missing values.
        return errors

    # Detect duplicate transaction IDs within this file.
    transaction_id = row["transaction_id"]

    if transaction_id in seen_transaction_ids:
        errors.append(
            ValidationError(
                category="DUPLICATE_TRANSACTION",
                message=f"Duplicate transaction_id '{transaction_id}'.",
                row_number=line_number,
            )
        )
    else:
        seen_transaction_ids.add(transaction_id)

    # Validate the sale date.
    try:
        date.fromisoformat(row["sale_date"])
    except ValueError:
        errors.append(
            ValidationError(
                category="INVALID_DATE",
                message="Invalid sale_date.",
                row_number=line_number,
            )
        )

    # Validate quantity as a positive integer.
    try:
        quantity = int(row["quantity"])

        if quantity <= 0:
            errors.append(
                ValidationError(
                    category="INVALID_NUMBER",
                    message="Quantity must be positive.",
                    row_number=line_number,
                )
            )

    except ValueError:
        errors.append(
            ValidationError(
                category="INVALID_NUMBER",
                message="Quantity must be an integer.",
                row_number=line_number,
            )
        )

        # Sales calculations cannot be performed without valid quantity.
        return errors

    # Parse monetary fields using Decimal to avoid float rounding errors.
    try:
        unit_price = Decimal(row["unit_price"])
        discount = Decimal(row["discount_amount"])
        sales_amount = Decimal(row["sales_amount"])

    except InvalidOperation:
        errors.append(
            ValidationError(
                category="INVALID_NUMBER",
                message="Invalid monetary value.",
                row_number=line_number,
            )
        )
        return errors

    monetary_values = [unit_price, discount, sales_amount]

    # Reject NaN and infinity before performing calculations.
    if not all(value.is_finite() for value in monetary_values):
        errors.append(
            ValidationError(
                category="INVALID_NUMBER",
                message="Monetary values must be finite numbers.",
                row_number=line_number,
            )
        )
        return errors

    # Monetary values cannot be negative.
    if any(value < 0 for value in monetary_values):
        errors.append(
            ValidationError(
                category="INVALID_NUMBER",
                message="Monetary values cannot be negative.",
                row_number=line_number,
            )
        )

    # Validate the sales calculation when the values are usable.
    expected_sales = Decimal(quantity) * unit_price - discount

    if expected_sales != sales_amount:
        errors.append(
            ValidationError(
                category="BUSINESS_RULE_VIOLATION",
                message=(
                    "sales_amount does not match "
                    "quantity * unit_price - discount_amount."
                ),
                row_number=line_number,
            )
        )

    return errors


def validate_file(file_path) -> ValidationResult:
    """
    Validate a CSV file.

    Return a dictionary containing:
    - valid: whether the file passed validation
    - row_count: number of data rows examined
    - errors: human-readable validation errors

    Structured ValidationError objects are used internally. The
    dictionary return format is retained for compatibility with
    the current tests and calling code.
    """

    path = Path(file_path)
    errors = []
    row_count = 0

    # Track transaction IDs to detect duplicates within this file.
    seen_transaction_ids = set()

    # Check that the file exists.
    if not path.is_file():
        return ValidationResult(
            valid=False,
            errors=[
                ValidationError(
                    category="FILE_ERROR",
                    message=f"File nor found: {path}",
                )
            ],
        )
    
    # Check whether the file is empty.
    if path.stat().st_size == 0:
        return ValidationResult(
            valid=False,
            errors=[
                ValidationError(
                    category="FILE_ERROR",
                    message="File is empty.",
                )
            ],
        )

    try:
        with path.open(
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as file:
            reader = csv.DictReader(file)
            actual_columns = reader.fieldnames

            # Validate the CSV header before processing rows.
            header_errors = validate_headers(reader.fieldnames)

            if header_errors:
                return ValidationResult(
                    valid=False,
                    errors=header_errors,
                )

            # Validate every row while the file remains open.
            for line_number, row in enumerate(reader, start=2):
                row_count += 1

                # DictReader uses None as a key when a row has extra fields.
                if None in row:
                    errors.append(
                         ValidationError(
                            category="ROW_FORMAT_ERROR",
                            message="Too many fields in CSV row.",
                            row_number=line_number,
                         )
                    )
                    continue

                # Validate this row and collect its errors.
                row_errors = validate_row(
                    row=row,
                    line_number=line_number,
                    seen_transaction_ids=seen_transaction_ids,
                )

                errors.extend(row_errors)

    except (OSError, UnicodeDecodeError, csv.Error) as exc:
         errors.append(
            ValidationError(
                category="FILE_READ_ERROR",
                message=f"Unable to read CSV: {exc}",
            )
        )

    # An empty CSV with a header is not a valid daily delivery.
    if row_count == 0 and not errors:
        errors.append(
            ValidationError(
                category="EMPTY_DATA_ERROR",
                message="CSV contains no data rows.",
            )
        )

    return ValidationResult(
        valid=len(errors) == 0,
        row_count=row_count,
        errors=errors,
    )


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent

    sample_file = (
        project_root / "data" / "raw" / "sales_2026-10-24.csv"
    )

    report = validate_file(sample_file)

    print(f"Valid: {report.valid}")
    print(f"Rows checked: {report.row_count}")

    if report.errors:
        print("Validation errors:")

        for error in report.errors:
            location = (
                f"Line {error.row_number}: "
                if error.row_number is not None
                else ""
            )
            print(f"- [{error.category}] {location}{error.message}")

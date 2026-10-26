
"""
Test the retail CSV validator against invalid input files.

We test three scenarios:
1. An unexpected column is added.
2. A required column is missing.
3. A sales amount violates the business rule.
"""

import csv
import sys
import tempfile
import unittest
from pathlib import Path

# Allow this test file to import modules from src/.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.file_validator import validate_file
from src.schema import EXPECTED_COLUMNS


VALID_ROW = [
    "TXN-TEST-001",
    "2026-10-24",
    "STORE-001",
    "PROD-101",
    "Electronics",
    "2",
    "49.99",
    "5.00",
    "94.98",
]


class TestFileValidator(unittest.TestCase):

    def create_csv(self, folder, columns, row):
        """Create a temporary CSV for one test."""

        file_path = Path(folder) / "test_sales.csv"

        with file_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            writer.writerow(row)

        return file_path

    def test_unexpected_column(self):
        """The validator must reject an unexpected column."""

        with tempfile.TemporaryDirectory() as folder:
            columns = EXPECTED_COLUMNS + ["new_column"]
            row = VALID_ROW + ["unexpected value"]

            file_path = self.create_csv(folder, columns, row)
            report = validate_file(file_path)

            self.assertFalse(report.valid)
            self.assertTrue(
                any("Unexpected columns" in error.message
                    for error in report.errors)
            )

    def test_missing_required_column(self):
        """The validator must reject a missing column."""

        with tempfile.TemporaryDirectory() as folder:
            columns = [
                column
                for column in EXPECTED_COLUMNS
                if column != "product_category"
            ]

            row = [
                value
                for column, value in zip(EXPECTED_COLUMNS, VALID_ROW)
                if column != "product_category"
            ]

            file_path = self.create_csv(folder, columns, row)
            report = validate_file(file_path)

            self.assertFalse(report.valid)
            self.assertTrue(
                any("Missing columns" in error.message
                    for error in report.errors)
            )

    def test_invalid_sales_amount(self):
        """The validator must reject an incorrect sales calculation."""

        with tempfile.TemporaryDirectory() as folder:
            row = VALID_ROW.copy()
            row[-1] = "100.00"

            file_path = self.create_csv(
                folder,
                EXPECTED_COLUMNS,
                row,
            )

            report = validate_file(file_path)

            self.assertFalse(report.valid)
            self.assertTrue(
                any("sales_amount does not match" in error.message
                    for error in report.errors)
            )


    def test_duplicate_transaction_id(self):
        """The validator must reject duplicate transaction IDs."""

        with tempfile.TemporaryDirectory() as folder:
            duplicate_row = VALID_ROW.copy()

            # Write the same transaction twice.
            file_path = Path(folder) / "duplicate_sales.csv"

            with file_path.open(
                "w",
                newline="",
                encoding="utf-8",
            ) as file:
                writer = csv.writer(file)
                writer.writerow(EXPECTED_COLUMNS)
                writer.writerow(VALID_ROW)
                writer.writerow(duplicate_row)

            report = validate_file(file_path)

            self.assertFalse(report.valid)
            self.assertTrue(
                any("Duplicate transaction_id" in error.message
                    for error in report.errors)
            )

    def test_missing_file(self):
        """The validator must reject a file that does not exist."""

        report = validate_file("file_that_does_not_exist.csv")

        self.assertFalse(report.valid)
        self.assertTrue(
            any(
                error.category == "FILE_ERROR"
                for error in report.errors
            )
        )


    def test_empty_file(self):
        """The validator must reject an empty CSV file."""

        with tempfile.TemporaryDirectory() as temp_dir:
            empty_file = Path(temp_dir) / "empty.csv"
            empty_file.touch()

            report = validate_file(empty_file)

            self.assertFalse(report.valid)
            self.assertTrue(
                any(
                    error.message == "File is empty."
                    for error in report.errors
                )
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)


"""Test CSV header validation independently."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.file_validator import validate_headers 
from src.schema import EXPECTED_COLUMNS


class TestValidateHeaders(unittest.TestCase):

    def test_valid_headers(self):
        errors = validate_headers(EXPECTED_COLUMNS.copy())

        self.assertEqual(errors, [])

    def test_missing_column(self):
        columns = [
            column
            for column in EXPECTED_COLUMNS
            if column != "product_category"
        ]

        errors = validate_headers(columns)

        self.assertTrue(
            any("Missing columns" in error.message for error in errors)
        )

    def test_unexpected_column(self):
        columns = EXPECTED_COLUMNS + ["new_column"]

        errors = validate_headers(columns)

        self.assertTrue(
            any("Unexpected columns" in error.message for error in errors)
        )

    def test_duplicate_column(self):
        columns = EXPECTED_COLUMNS + ["quantity"]

        errors = validate_headers(columns)

        self.assertTrue(
            any(
                "Duplicate column names" in error.message
                for error in errors
            )
        )

    def test_missing_header(self):
        errors = validate_headers(None)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].category, "SCHEMA_ERROR")


if __name__ == "__main__":
    unittest.main(verbosity=2)

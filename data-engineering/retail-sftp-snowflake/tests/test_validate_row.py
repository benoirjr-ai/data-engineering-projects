
"""Test row-level validation independently."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.file_validator import validate_row
from src.schema import EXPECTED_COLUMNS


VALID_ROW = dict(zip(
    EXPECTED_COLUMNS,
    [
        "TXN-TEST-001",
        "2026-10-24",
        "STORE-001",
        "PROD-101",
        "Electronics",
        "2",
        "49.99",
        "5.00",
        "94.98",
    ],
))


class TestValidateRow(unittest.TestCase):

    def test_valid_row(self):
        errors = validate_row(VALID_ROW, 2, set())
        self.assertEqual(errors, [])

    def test_duplicate_transaction(self):
        seen = {"TXN-TEST-001"}

        errors = validate_row(VALID_ROW, 3, seen)

        self.assertTrue(
            any(error.category == "DUPLICATE_TRANSACTION"
                for error in errors)
        )
        self.assertEqual(errors[0].row_number, 3)

    def test_invalid_date(self):
        row = VALID_ROW.copy()
        row["sale_date"] = "not-a-date"

        errors = validate_row(row, 2, set())

        self.assertTrue(
            any(error.category == "INVALID_DATE" for error in errors)
        )

    def test_invalid_quantity(self):
        row = VALID_ROW.copy()
        row["quantity"] = "two"

        errors = validate_row(row, 2, set())

        self.assertTrue(
            any(error.category == "INVALID_NUMBER" for error in errors)
        )

    def test_incorrect_sales_amount(self):
        row = VALID_ROW.copy()
        row["sales_amount"] = "100.00"

        errors = validate_row(row, 2, set())

        self.assertTrue(
            any(
                error.category == "BUSINESS_RULE_VIOLATION"
                for error in errors
            )
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

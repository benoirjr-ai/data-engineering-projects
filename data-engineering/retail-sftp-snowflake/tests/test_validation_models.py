
"""Test the validation result and error structures."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.validation_models import ValidationError, ValidationResult


class TestValidationModels(unittest.TestCase):

    def test_validation_error_stores_details(self):
        error = ValidationError(
            category="INVALID_NUMBER",
            message="Quantity must be an integer.",
            row_number=2,
        )

        self.assertEqual(error.category, "INVALID_NUMBER")
        self.assertEqual(error.message, "Quantity must be an integer.")
        self.assertEqual(error.row_number, 2)

    def test_valid_result_has_no_errors(self):
        result = ValidationResult(valid=True, row_count=5)

        self.assertTrue(result.valid)
        self.assertEqual(result.row_count, 5)
        self.assertEqual(result.errors, [])

    def test_results_have_independent_error_lists(self):
        first = ValidationResult(valid=False)
        second = ValidationResult(valid=True)

        first.errors.append(
            ValidationError(
                category="SCHEMA_ERROR",
                message="Missing required column.",
            )
        )

        self.assertEqual(len(first.errors), 1)
        self.assertEqual(len(second.errors), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

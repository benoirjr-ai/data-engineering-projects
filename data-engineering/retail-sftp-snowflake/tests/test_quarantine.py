
"""Tests for invalid-file quarantine handling."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.quarantine import quarantine_file
from src.validation_models import ValidationError


class TestQuarantine(unittest.TestCase):

    def test_moves_file_and_writes_error_report(self):
        """The CSV should move to quarantine with a JSON error report."""

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "invalid_sales.csv"
            quarantine_dir = root / "quarantine"

            source.write_text(
                "transaction_id,sales_amount\nTXN-1,invalid\n",
                encoding="utf-8",
            )

            errors = [
                ValidationError(
                    category="INVALID_NUMBER",
                    message="Invalid monetary value.",
                    row_number=2,
                )
            ]

            # Use a temporary quarantine directory to avoid
            # changing the project's real data during the test.
            with patch("quarantine.QUARANTINE_DIR", quarantine_dir):
                destination = quarantine_file(source, errors)

            self.assertTrue(destination.is_file())
            self.assertFalse(source.exists())
            self.assertEqual(destination.read_text(encoding="utf-8"),
                             "transaction_id,sales_amount\nTXN-1,invalid\n")

            report_path = destination.with_suffix(".errors.json")
            self.assertTrue(report_path.is_file())

            report = json.loads(report_path.read_text(encoding="utf-8"))

            self.assertEqual(report["original_filename"], "invalid_sales.csv")
            self.assertEqual(len(report["errors"]), 1)
            self.assertEqual(
                report["errors"][0]["category"],
                "INVALID_NUMBER",
            )
            self.assertEqual(report["errors"][0]["row_number"], 2)

    def test_missing_file_raises_error(self):
        """A nonexistent file must not be quarantined."""

        with tempfile.TemporaryDirectory() as temp_dir:
            missing_file = Path(temp_dir) / "missing.csv"

            with self.assertRaises(FileNotFoundError):
                quarantine_file(missing_file, [])

            
if __name__ == "__main__":
    unittest.main(verbosity=2)

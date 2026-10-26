
"""Tests for file fingerprinting."""

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.file_fingerprint import calculate_file_hash


class TestFileFingerprint(unittest.TestCase):

    def test_same_content_produces_same_hash(self):
        """Identical file contents should produce identical hashes."""

        with tempfile.TemporaryDirectory() as folder:
            first = Path(folder) / "first.csv"
            second = Path(folder) / "renamed.csv"

            first.write_text("transaction_id,sales_amount\nTXN-1,25.00\n",
                             encoding="utf-8")
            second.write_text("transaction_id,sales_amount\nTXN-1,25.00\n",
                              encoding="utf-8")

            self.assertEqual(
                calculate_file_hash(first),
                calculate_file_hash(second),
            )

    def test_different_content_produces_different_hash(self):
        """Changing the contents should change the fingerprint."""

        with tempfile.TemporaryDirectory() as folder:
            first = Path(folder) / "first.csv"
            second = Path(folder) / "second.csv"

            first.write_text("TXN-1,25.00", encoding="utf-8")
            second.write_text("TXN-1,26.00", encoding="utf-8")

            self.assertNotEqual(
                calculate_file_hash(first),
                calculate_file_hash(second),
            )

    def test_missing_file_raises_error(self):
        """A nonexistent file should raise FileNotFoundError."""

        with tempfile.TemporaryDirectory() as folder:
            missing = Path(folder) / "missing.csv"

            with self.assertRaises(FileNotFoundError):
                calculate_file_hash(missing)


if __name__ == "__main__":
    unittest.main(verbosity=2)

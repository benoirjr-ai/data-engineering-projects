
"""Tests for the CSV ingestion orchestration."""

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.file_registry import FileRegistry
from src.ingestion import process_file
from src.schema import EXPECTED_COLUMNS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


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


class TestIngestion(unittest.TestCase):

    def create_csv(self, folder, columns, rows):
        """Create a temporary CSV for testing."""

        file_path = Path(folder) / "sales.csv"

        with file_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            writer.writerows(rows)

        return file_path

    def test_valid_file_is_accepted(self):
        """A valid file should be ready for the next stage."""

        with tempfile.TemporaryDirectory() as folder:
            file_path = self.create_csv(
                folder,
                EXPECTED_COLUMNS,
                [VALID_ROW],
            )

            result = process_file(file_path)

            self.assertEqual(result["status"], "VALIDATED")
            self.assertEqual(result["row_count"], 1)
            self.assertIsNone(result["quarantined_path"])
            self.assertTrue(file_path.exists())

    def test_invalid_file_is_quarantined(self):
        """An invalid file should be rejected and moved."""

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            quarantine_dir = root / "quarantine"

            # Remove a required column to make the CSV invalid.
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

            file_path = self.create_csv(root, columns, [row])

            with patch(
                "quarantine.QUARANTINE_DIR",
                quarantine_dir,
            ):
                result = process_file(file_path)

            self.assertEqual(result["status"], "REJECTED")
            self.assertFalse(file_path.exists())
            self.assertIsNotNone(result["quarantined_path"])
            self.assertTrue(Path(result["quarantined_path"]).exists())
            self.assertTrue(
                Path(result["quarantined_path"])
                .with_suffix(".errors.json")
                .exists()
            )

    def test_missing_file_is_rejected_safely(self):
        """A missing file should be rejected without quarantine."""

        with tempfile.TemporaryDirectory() as folder:
            file_path = Path(folder) / "missing.csv"

            result = process_file(file_path)

            self.assertEqual(result["status"], "REJECTED")
            self.assertIsNone(result["quarantined_path"])
            self.assertTrue(result["errors"])

    
    def test_successfully_processed_file_is_skipped(self):
        """A file marked PROCESSED should be skipped on a rerun."""

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = root / "sales.csv"
            database_path = root / "registry.db"

            # Create a valid CSV file.
            with csv_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=EXPECTED_COLUMNS)
                writer.writeheader()
                writer.writerow({
                    "transaction_id": "TXN-20001",
                    "sale_date": "2026-10-24",
                    "store_id": "STORE-01",
                    "product_id": "PROD-01",
                    "product_category": "Electronics",
                    "quantity": "2",
                    "unit_price": "10.00",
                    "discount_amount": "0.00",
                    "sales_amount": "20.00",
                })

            registry = FileRegistry(database_path)

            # Simulate a successful previous data load.
            from src.file_fingerprint import calculate_file_hash
            file_hash = calculate_file_hash(csv_path)
            registry.mark_processing(file_hash, csv_path.name)
            registry.mark_processed(file_hash)

            result = process_file(csv_path, registry=registry)

            self.assertEqual(result["status"], "SKIPPED")
            self.assertEqual(registry.get_status(file_hash), "PROCESSED")
            self.assertTrue(csv_path.exists())


    def test_identical_file_content_is_skipped(self):
        """Identical content under a different filename should be skipped."""

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first_file = root / "sales_first.csv"
            second_file = root / "sales_second.csv"
            registry = FileRegistry(root / "registry.db")

            content = (
                ",".join(EXPECTED_COLUMNS)
                + "\n"
                + "TXN-20002,2026-10-24,STORE-01,PROD-02,"
                "Home,1,25.00,0.00,25.00\n"
            )

            first_file.write_text(content, encoding="utf-8")
            second_file.write_text(content, encoding="utf-8")

            from src.file_fingerprint import calculate_file_hash
            file_hash = calculate_file_hash(first_file)
            registry.mark_processing(file_hash, first_file.name)
            registry.mark_processed(file_hash)

            result = process_file(second_file, registry=registry)

            self.assertEqual(result["status"], "SKIPPED")
            self.assertTrue(second_file.exists())


    def test_invalid_file_is_marked_failed(self):
        """An invalid file must not be recorded as successfully processed."""

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = root / "invalid_sales.csv"
            registry = FileRegistry(root / "registry.db")

            # The required product_category column is missing.
            columns = [
                column for column in EXPECTED_COLUMNS
                if column != "product_category"
            ]

            with csv_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=columns)
                writer.writeheader()
                writer.writerow({
                    "transaction_id": "TXN-20003",
                    "sale_date": "2026-10-24",
                    "store_id": "STORE-01",
                    "product_id": "PROD-03",
                    "quantity": "1",
                    "unit_price": "10.00",
                    "discount_amount": "0.00",
                    "sales_amount": "10.00",
                })

            from src.file_fingerprint import calculate_file_hash
            file_hash = calculate_file_hash(csv_path)

            # Redirect quarantine output to the temporary directory.
            with patch(
                "src.quarantine.QUARANTINE_DIR",
                root / "quarantine",
            ):
                result = process_file(csv_path, registry=registry)

            self.assertEqual(result["status"], "REJECTED")
            self.assertEqual(registry.get_status(file_hash), "FAILED")
            self.assertFalse(registry.should_skip(file_hash))
            self.assertIsNotNone(result["quarantined_path"])

    
    def test_loader_failure_can_be_retried_successfully(self):
        """A failed load can be retried and eventually marked PROCESSED."""

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = self.create_csv(
                root,
                EXPECTED_COLUMNS,
                [VALID_ROW],
            )
            registry = FileRegistry(root / "registry.db")

            from src.file_fingerprint import calculate_file_hash
            file_hash = calculate_file_hash(csv_path)

            # First attempt: simulate a Snowflake connection failure.
            def failing_loader(path):
                raise RuntimeError("Simulated Snowflake failure")

            first_result = process_file(
                csv_path,
                registry=registry,
                loader=failing_loader,
            )

            self.assertEqual(first_result["status"], "FAILED")
            self.assertEqual(registry.get_status(file_hash), "FAILED")
            self.assertFalse(registry.should_skip(file_hash))

            # Second attempt: simulate a successful one-row load.
            def successful_loader(path):
                return {
                    "load_results": [
                        (
                            "sales.csv.gz",
                            "LOADED",
                            1,
                            1,
                            1,
                            0,
                            None,
                            None,
                            None,
                            None,
                        )
                    ]
                }

            second_result = process_file(
                csv_path,
                registry=registry,
                loader=successful_loader,
            )

            self.assertEqual(second_result["status"], "PROCESSED")
            self.assertEqual(second_result["row_count"], 1)
            self.assertEqual(registry.get_status(file_hash), "PROCESSED")
            self.assertTrue(registry.should_skip(file_hash))

    def test_loader_row_count_mismatch_marks_failed(self):
        """A row-count mismatch must never be marked PROCESSED."""

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = self.create_csv(
                root,
                EXPECTED_COLUMNS,
                [VALID_ROW],
            )
            registry = FileRegistry(root / "registry.db")

            from src.file_fingerprint import calculate_file_hash
            file_hash = calculate_file_hash(csv_path)

            # The CSV has one valid row, but the loader reports two.
            def mismatched_loader(path):
                return {
                    "load_results": [
                        (
                            "sales.csv.gz",
                            "LOADED",
                            2,
                            2,
                            1,
                            0,
                            None,
                            None,
                            None,
                            None,
                        )
                    ]
                }

            result = process_file(
                csv_path,
                registry=registry,
                loader=mismatched_loader,
            )

            self.assertEqual(result["status"], "FAILED")
            self.assertTrue(result["errors"])
            self.assertEqual(registry.get_status(file_hash), "FAILED")
            self.assertFalse(registry.should_skip(file_hash))

    def test_loader_unexpected_status_marks_failed(self):
        """An unexpected Snowflake status must not mark success."""

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = self.create_csv(
                root,
                EXPECTED_COLUMNS,
                [VALID_ROW],
            )
            registry = FileRegistry(root / "registry.db")

            from src.file_fingerprint import calculate_file_hash
            file_hash = calculate_file_hash(csv_path)

            def unexpected_status_loader(path):
                return {
                    "load_results": [
                        (
                            "sales.csv.gz",
                            "LOAD_FAILED",
                            1,
                            0,
                            1,
                            1,
                            "Simulated failure",
                            None,
                            None,
                            None,
                        )
                    ]
                }

            result = process_file(
                csv_path,
                registry=registry,
                loader=unexpected_status_loader,
            )

            self.assertEqual(result["status"], "FAILED")
            self.assertEqual(registry.get_status(file_hash), "FAILED")
            self.assertFalse(registry.should_skip(file_hash))

        
    def test_registry_failure_after_load_does_not_report_success(self):
        """A registry error after loading must not report PROCESSED."""

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            csv_path = self.create_csv(
                root,
                EXPECTED_COLUMNS,
                [VALID_ROW],
            )
            registry = FileRegistry(root / "registry.db")

            from src.file_fingerprint import calculate_file_hash
            file_hash = calculate_file_hash(csv_path)

            # Simulate a successful one-row Snowflake load.
            def successful_loader(path):
                return {
                    "load_results": [
                        (
                            "sales.csv.gz",
                            "LOADED",
                            1,
                            1,
                            1,
                            0,
                            None,
                            None,
                            None,
                            None,
                        )
                    ]
                }

            # Simulate the local registry failing to record success.
            with patch.object(
                registry,
                "mark_processed",
                side_effect=RuntimeError(
                    "Simulated registry write failure"
                ),
            ):
                result = process_file(
                    csv_path,
                    registry=registry,
                    loader=successful_loader,
                )


            self.assertEqual(result["status"], "FAILED")
            self.assertTrue(result["errors"])
            self.assertNotEqual(
                registry.get_status(file_hash),
                "PROCESSED",
            )
            self.assertFalse(registry.should_skip(file_hash))

if __name__ == "__main__":
    unittest.main(verbosity=2)

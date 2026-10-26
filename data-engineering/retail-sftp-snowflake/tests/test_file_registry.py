
import sqlite3
import tempfile
import unittest
from pathlib import Path
from contextlib import closing

from src.file_registry import FileRegistry


class TestFileRegistry(unittest.TestCase):

    def setUp(self):
        # Give each test its own temporary database.
        # This prevents tests from affecting one another.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test_registry.db"

        self.registry = FileRegistry(self.database_path)
        self.file_hash = "abc123"
        self.filename = "sales_2026-10-24.csv"

    def tearDown(self):
        # Remove the temporary database after each test.
        self.temp_dir.cleanup()

    def test_new_file_is_not_registered(self):
        # An unseen file has no status and should not be skipped.
        self.assertIsNone(self.registry.get_status(self.file_hash))
        self.assertFalse(self.registry.should_skip(self.file_hash))

    def test_mark_processing(self):
        self.registry.mark_processing(self.file_hash, self.filename)

        self.assertEqual(
            self.registry.get_status(self.file_hash),
            "PROCESSING",
        )
        self.assertFalse(self.registry.should_skip(self.file_hash))

    def test_processed_file_should_be_skipped(self):
        self.registry.mark_processing(self.file_hash, self.filename)
        self.registry.mark_processed(self.file_hash)

        self.assertEqual(
            self.registry.get_status(self.file_hash),
            "PROCESSED",
        )
        self.assertTrue(self.registry.should_skip(self.file_hash))

    def test_failed_file_can_be_retried(self):
        self.registry.mark_processing(self.file_hash, self.filename)
        self.registry.mark_failed(self.file_hash, "Temporary loading error")

        self.assertEqual(
            self.registry.get_status(self.file_hash),
            "FAILED",
        )
        self.assertFalse(self.registry.should_skip(self.file_hash))

        # Start another attempt for the same file.
        self.registry.mark_processing(self.file_hash, self.filename)

        self.assertEqual(
            self.registry.get_status(self.file_hash),
            "PROCESSING",
        )

        # Confirm the old error message was cleared.
        with closing(sqlite3.connect(self.database_path)) as connection:
            row = connection.execute(
                """
                SELECT error_message
                FROM processed_files
                WHERE file_hash = ?
                """,
                (self.file_hash,),
            ).fetchone()

        self.assertIsNone(row[0])

    def test_status_persists_across_registry_instances(self):
        self.registry.mark_processing(self.file_hash, self.filename)
        self.registry.mark_processed(self.file_hash)

        # Simulate a later pipeline run opening the same database.
        new_registry = FileRegistry(self.database_path)

        self.assertEqual(
            new_registry.get_status(self.file_hash),
            "PROCESSED",
        )
        self.assertTrue(new_registry.should_skip(self.file_hash))

    def test_processing_cannot_overwrite_processed_status(self):
        self.registry.mark_processing(self.file_hash, self.filename)
        self.registry.mark_processed(self.file_hash)

        # Accidentally registering the same content again must not
        # downgrade its completed status.
        self.registry.mark_processing(self.file_hash, "renamed_sales.csv")

        self.assertEqual(
            self.registry.get_status(self.file_hash),
            "PROCESSED",
        )
        self.assertTrue(self.registry.should_skip(self.file_hash))


if __name__ == "__main__":
    unittest.main()

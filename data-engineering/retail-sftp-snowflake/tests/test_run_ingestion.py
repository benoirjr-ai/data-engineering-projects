
"""Unit tests for the SFTP ingestion runner."""

import unittest
from pathlib import Path
from unittest.mock import patch

from src import run_ingestion


class TestRunIngestion(unittest.TestCase):
    """Test the orchestration between SFTP and ingestion."""

    @patch("src.run_ingestion.process_file")
    @patch("src.run_ingestion.download_from_sftp")
    def test_downloaded_file_is_passed_to_ingestion(
        self,
        mock_download,
        mock_process,
    ):
        """The downloaded CSV should be passed to process_file."""
        downloaded_path = Path("data/landing/sales_2026-10-24.csv")

        mock_download.return_value = downloaded_path
        mock_process.return_value = {
            "status": "PROCESSED",
            "row_count": 5,
            "errors": [],
            "quarantined_path": None,
            "file_hash": "test-hash",
        }

        result = run_ingestion.main()

        mock_download.assert_called_once_with(
            "sales_2026-10-24.csv"
        )
        mock_process.assert_called_once_with(
            downloaded_path,
            loader=run_ingestion.load_csv_to_snowflake,
        )
        self.assertEqual(result["status"], "PROCESSED")
        self.assertEqual(result["row_count"], 5)

    @patch("src.run_ingestion.process_file")
    @patch("src.run_ingestion.download_from_sftp")
    def test_download_failure_stops_ingestion(
        self,
        mock_download,
        mock_process,
    ):
        """Ingestion must not start if the download fails."""
        mock_download.side_effect = OSError("SFTP unavailable")

        with self.assertRaisesRegex(OSError, "SFTP unavailable"):
            run_ingestion.main()

        mock_process.assert_not_called()


if __name__ == "__main__":
    unittest.main()


"""Unit tests for downloading CSV files from SFTP."""

import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src import sftp_download


class TestSFTPDownload(unittest.TestCase):
    """Test SFTP download behavior without a live server."""

    def setUp(self):
        """Prepare a clean environment for each test."""
        self.password_patcher = patch.dict(
            os.environ,
            {"SFTP_PASSWORD": "test-password"},
        )
        self.password_patcher.start()
        self.addCleanup(self.password_patcher.stop)

        # Patch the landing directory to avoid creating project files.
        self.temp_dir_patcher = patch.object(
            sftp_download,
            "LANDING_DIR",
            Path("test_landing"),
        )
        self.temp_dir_patcher.start()
        self.addCleanup(self.temp_dir_patcher.stop)

    @patch("src.sftp_download.paramiko.SSHClient")
    def test_successful_download_returns_local_path(self, mock_ssh_class):
        """A successful download should return the destination path."""
        mock_client = MagicMock()
        mock_sftp = MagicMock()

        mock_ssh_class.return_value = mock_client
        mock_client.open_sftp.return_value.__enter__.return_value = mock_sftp

        result = sftp_download.download_from_sftp("orders.csv")

        expected_path = Path("test_landing") / "orders.csv"

        self.assertEqual(result, expected_path)
        mock_client.connect.assert_called_once_with(
            hostname="127.0.0.1",
            port=2222,
            username="retail",
            password="test-password",
            timeout=10,
        )
        mock_sftp.get.assert_called_once_with(
            "/upload/orders.csv",
            str(expected_path),
        )
        mock_client.close.assert_called_once()

    def test_missing_password_raises_error(self):
        """The function must reject missing credentials."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(
                ValueError,
                "SFTP_PASSWORD",
            ):
                sftp_download.download_from_sftp("orders.csv")

    @patch("src.sftp_download.paramiko.SSHClient")
    def test_connection_failure_closes_client(self, mock_ssh_class):
        """A connection failure should propagate and close the client."""
        mock_client = MagicMock()
        mock_ssh_class.return_value = mock_client
        mock_client.connect.side_effect = OSError("Connection failed")

        with self.assertRaisesRegex(OSError, "Connection failed"):
            sftp_download.download_from_sftp("orders.csv")

        mock_client.close.assert_called_once()

    @patch("src.sftp_download.paramiko.SSHClient")
    def test_download_failure_closes_client(self, mock_ssh_class):
        """A remote download failure should propagate and close the client."""
        mock_client = MagicMock()
        mock_sftp = MagicMock()

        mock_ssh_class.return_value = mock_client
        mock_client.open_sftp.return_value.__enter__.return_value = mock_sftp
        mock_sftp.get.side_effect = FileNotFoundError("Remote file not found")

        with self.assertRaisesRegex(
            FileNotFoundError,
            "Remote file not found",
        ):
            sftp_download.download_from_sftp("missing.csv")

        mock_client.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()

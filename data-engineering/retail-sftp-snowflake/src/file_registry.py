
"""
Store file-processing history in a local SQLite database.

The registry helps the pipeline:
- Recognize files that have already been processed.
- Skip successfully processed files on reruns.
- Retry files that previously failed.
- Preserve processing history between program runs.
"""

import sqlite3
from contextlib import closing
from pathlib import Path


# Find the project root directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Store the registry database inside the project's data directory.
DATABASE_PATH = PROJECT_ROOT / "data" / "file_registry.db"


class FileRegistry:
    """Manage file-processing status using SQLite."""

    def __init__(self, database_path=DATABASE_PATH):
        """Initialize the registry and create its table if necessary."""

        self.database_path = Path(database_path)

        # Ensure the database directory exists.
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._create_table()

    def _connect(self):
        """Create and return a new SQLite connection."""

        return sqlite3.connect(self.database_path)

    def _create_table(self):
        """Create the processing-history table if it does not exist."""

        # closing() ensures the connection closes after use.
        # The inner context manages the database transaction.
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS processed_files (
                        file_hash TEXT PRIMARY KEY,
                        filename TEXT NOT NULL,
                        status TEXT NOT NULL,
                        error_message TEXT,
                        created_at TEXT NOT NULL
                            DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT NOT NULL
                            DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

    def get_status(self, file_hash):
        """Return a file's status, or None if it is not registered."""

        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT status
                FROM processed_files
                WHERE file_hash = ?
                """,
                (file_hash,),
            ).fetchone()

        return row[0] if row else None

    def should_skip(self, file_hash):
        """Return True only if the file was processed successfully."""

        return self.get_status(file_hash) == "PROCESSED"

    def mark_processing(self, file_hash, filename):
        """
        Register a processing attempt.

        A previously failed file can be retried.
        A successfully processed file keeps its PROCESSED status.
        """

        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO processed_files (
                        file_hash,
                        filename,
                        status,
                        error_message
                    )
                    VALUES (?, ?, 'PROCESSING', NULL)

                    ON CONFLICT(file_hash) DO UPDATE SET
                        filename = excluded.filename,
                        status = 'PROCESSING',
                        error_message = NULL,
                        updated_at = CURRENT_TIMESTAMP

                    WHERE processed_files.status != 'PROCESSED'
                    """,
                    (file_hash, filename),
                )

    def mark_processed(self, file_hash):
        """Mark a registered file as successfully processed."""

        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    UPDATE processed_files
                    SET status = 'PROCESSED',
                        error_message = NULL,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE file_hash = ?
                    """,
                    (file_hash,),
                )

    def mark_failed(self, file_hash, error_message):
        """Record a failed processing attempt and its error message."""

        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    UPDATE processed_files
                    SET status = 'FAILED',
                        error_message = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE file_hash = ?
                    """,
                    (error_message, file_hash),
                )

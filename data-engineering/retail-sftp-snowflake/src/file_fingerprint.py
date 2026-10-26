"""
Calculate a SHA-256 fingerprint for a file.

The fingerprint helps identify files by their contents,
even if the filename changes.
"""

import hashlib
from pathlib import Path

def calculate_file_hash(file_path, chunck_size=1024 * 1024):
    """
    Return the SHA-256 hex digest of a file.

    Read the file in chunks to avoid loading large files
    entirely into memory.
    """
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    sha256 = hashlib.sha256()

    with path.open("rb") as file:
        while True:
            chunck = file.read(chunck_size)

            if not chunck:
                break

            sha256.update(chunck)

    return sha256.hexdigest()

"""Download a CSV file from the local SFTP server."""

import os
from pathlib import Path

import paramiko

# Find the project root from this file's location.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Store downloaded files separately from the SFTP server's files.
LANDING_DIR = PROJECT_ROOT / "data" / "landing"

def download_from_sftp(
    remote_filename: str,
    host: str = "127.0.0.1",
    port: int = 2222,
    username: str = "retail",
) -> Path:
    """Download one file from SFTP into the local landing folder."""

    password = os.environ.get("SFTP_PASSWORD")

    if not password:
        raise ValueError("Set the SFTP_PASSWORD environment variable.")

    # Build the remote path and local destination.
    remote_path = f"/upload/{remote_filename}"
    local_path = LANDING_DIR / remote_filename

    # Create the landing folder if it does not exist.
    LANDING_DIR.mkdir(parents=True, exist_ok=True)

    # Connect to the SFTP server.
    # Host-key verification is configured explicitly for this local test.
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=10,
        )

        with client.open_sftp() as sftp:
            sftp.get(remote_path, str(local_path))

    finally:
        client.close()

    print(f"Downloaded file to: {local_path}")
    return local_path

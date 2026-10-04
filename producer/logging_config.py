import logging
import sys 

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | "
    "%(name)s | %(message)s"
)

def configure_logging():
    """
    Configure application-wide logging.

    Logging is sent to stdout so messages are visible in
    PowerShell, Docker logs, and CI environments.
    """

    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        stream=sys.stdout,
        force=True,
    )


def get_logger(name):
    """Return a logger for the requested module."""
    return logging.getLogger(name)
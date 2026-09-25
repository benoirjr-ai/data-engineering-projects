from pathlib import Path


def load_watermark(file_path: str) -> int:
    """Load the last processed transaction ID."""

    path = Path(file_path)

    # If no watermark exists, start from zero.
    if not path.exists():
        return 0

    return int(path.read_text(encoding="utf-8"))


def save_watermark(file_path: str, transaction_id: int) -> None:
    """Save the last processed transaction ID."""

    # Make sure the parent directory exists.
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    # Store the transaction ID as text.
    Path(file_path).write_text(
        str(transaction_id),
        encoding="utf-8"
    )
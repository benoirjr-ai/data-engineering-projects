import csv

def read_transactions(file_path):
    """Read transactions from a CSV file."""

    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            yield row


def read_new_transactions(file_path: str, last_processed_id: int):
    """Read only transactions newer than the watermark."""

    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            transaction_id = int(row["transaction_id"])

            # Skip transactions that have already been processed.
            if transaction_id <= last_processed_id:
                continue

            yield row

import csv
from pathlib import Path

def write_customer_summary(file_path, results):
    """Write aggregated customer results to a CSV file."""

    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write the CSV header
        writer.writerow([
            "customer_id",
            "transaction_count",
            "total_amount"
        ])

        # Write one row for each customer.
        for customer_id, summary in results.items():
            writer.writerow([
                customer_id,
                summary["transaction_count"],
                summary["total_amount"]
            ])
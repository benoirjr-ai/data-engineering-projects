"""
Generate a small fictional retail sales CSV for testing.
"""

import csv 
from pathlib import Path

# Locate the project root from this script's location.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "sales_2026-10-24.csv"

COLUMNS = [
    "transaction_id",
    "sale_date",
    "store_id",
    "product_id",
    "product_category",
    "quantity",
    "unit_price",
    "discount_amount",
    "sales_amount",
]

# sales_amount = quantity * unit_price - discount_amount
SAMPLE_SALES = [
    ["TXN-10001", "2026-10-24", "STORE-001", "PROD-101",
     "Electronics", 2, "49.99", "5.00", "94.98"],
    ["TXN-10002", "2026-10-24", "STORE-001", "PROD-202",
     "Home", 1, "25.00", "0.00", "25.00"],
    ["TXN-10003", "2026-10-24", "STORE-002", "PROD-303",
     "Clothing", 3, "19.99", "2.00", "57.97"],
    ["TXN-10004", "2026-10-24", "STORE-002", "PROD-101",
     "Electronics", 1, "49.99", "0.00", "49.99"],
    ["TXN-10005", "2026-10-24", "STORE-003", "PROD-404",
     "Grocery", 5, "4.50", "1.00", "21.50"],
]

def generate_sample():
    """Write the sample sales records to a CSV file"""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(COLUMNS)
        writer.writerows(SAMPLE_SALES)

    print(f"Sample file created: {OUTPUT_FILE}")
    print(f"Rows written: {len(SAMPLE_SALES)}")

if __name__ == "__main__":
    generate_sample()
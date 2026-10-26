
"""
Defines the expected structure of the retail sales CSV.
"""

EXPECTED_COLUMNS = [
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

REQUIRED_COLUMNS = EXPECTED_COLUMNS.copy()

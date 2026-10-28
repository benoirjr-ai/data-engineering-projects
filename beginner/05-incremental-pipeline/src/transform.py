def transform_transaction(row):
    """Transform a raw transaction into database-ready values."""

    return {
        "transaction_id": int(row["transaction_id"]),
        "customer_id": row["customer_id"].strip(),
        "transaction_date": row["transaction_date"],
        "amount": float(row["amount"]),
        "status": row["status"].strip().lower(),
    }
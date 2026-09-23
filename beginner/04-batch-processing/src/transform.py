def transform_batch(batch):
    """Filter and transform one batch of transactions."""

    transformed_batch = []

    for row in batch:
        # Create a copy so the original raw data remains unchanged.
        transformed_row = row.copy()

        # Keep only completed transactions.
        if transformed_row["status"] != "completed":
            continue

        # Convert string values from the CSV into numeric types.
        transformed_row["transaction_id"] = int(
            transformed_row["transaction_id"]
        )
        transformed_row["amount"] = float(
            transformed_row["amount"]
        )

        # Add the transformed transaction to the output batch.
        transformed_batch.append(transformed_row)

    return transformed_batch
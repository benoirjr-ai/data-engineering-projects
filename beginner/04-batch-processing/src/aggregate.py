def aggregate_batch(batch):
    # Dictionary that will store the aggregated results
    # for each customer in the current batch.
    aggregated = {}

    # Process each transaction in the batch.
    for row in batch:

        # Get the customer ID and transaction amount.
        customer_id = row["customer_id"]
        amount = row["amount"]

        # If this is the first transaction we have seen
        # for this customer, create an initial record.
        if customer_id not in aggregated:
            aggregated[customer_id] = {
                "transaction_count": 0,
                "total_amount": 0.0
            }

        # Increase the number of transactions for this customer.
        aggregated[customer_id]["transaction_count"] += 1

        # Add the transaction amount to the customer's total.
        aggregated[customer_id]["total_amount"] += amount

    # Return the aggregated results for this batch.
    return aggregated
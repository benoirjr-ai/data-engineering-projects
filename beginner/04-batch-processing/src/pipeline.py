from src.extract import read_batches
from src.transform import transform_batch
from src.aggregate import aggregate_batch
from src.output import write_customer_summary


def run_pipeline(file_path, batch_size):
    """Run the complete batch-processing pipeline."""

    # Store the final aggregation across all batches.
    aggregated_results = {}

    # Read the input file one batch at a time.
    for batch in read_batches(file_path, batch_size):

        # Filter and transform the current batch.
        transformed_batch = transform_batch(batch)

        # Aggregate transactions within the current batch.
        batch_summary = aggregate_batch(transformed_batch)

        # Merge the current batch results into the global results.
        for customer_id, summary in batch_summary.items():

            # Create an entry for a customer we haven't seen before.
            if customer_id not in aggregated_results:
                aggregated_results[customer_id] = {
                    "transaction_count": 0,
                    "total_amount": 0.0
                }

            # Add this batch's transaction count to the customer's total.
            aggregated_results[customer_id]["transaction_count"] += (
                summary["transaction_count"]
            )

            # Add this batch's amount to the customer's total.
            aggregated_results[customer_id]["total_amount"] += (
                summary["total_amount"]
            )

    # Return the final aggregation from all batches.
    return aggregated_results


if __name__ == "__main__":
    # Run the pipeline.
    result = run_pipeline(
        "data/transactions.csv",
        batch_size=3
    )

    # Write the final customer summary to a CSV file.
    write_customer_summary(
        "output/customer_summary.csv",
        result
    )

    print("Pipeline completed successfully.")
    print("Output written to output/customer_summary.csv")
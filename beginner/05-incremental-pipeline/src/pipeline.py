from src.extract import read_new_transactions
from src.state import load_watermark, save_watermark
from src.database import create_connection, create_transactions_table
from src.load import load_transactions
from src.transform import transform_transaction
from src.logging_config import get_logger

logger = get_logger(__name__)

def run_incremental_pipeline(file_path, state_file):
    """Process and load only transactions newer than the watermark."""

    # Load the last successfully processed transaction ID.
    last_processed_id = load_watermark(state_file)
    logger.info("Watermark loaded: %s", last_processed_id)

    # Extract only transactions newer than the watermark.
    transactions = list(
        read_new_transactions(
            file_path,
            last_processed_id
        )
    )

    logger.info("New transactions found: %s", len(transactions))

    transactions = [
        transform_transaction(row)
        for row in transactions
    ]

    # If there is nothing new, do not connect to the database
    # or update the watermark.
    if not transactions:
        logger.info("No new transactions to process")
        return last_processed_id

    # Connect to PostgreSQL.
    connection = create_connection()

    try:
        # Make sure the target table exists.
        create_transactions_table(connection)

        # Load the new transactions.
        load_transactions(connection, transactions)
        logger.info("Transactions loaded successfully")

        # Find the newest transaction ID that was processed.
        max_transaction_id = max(
            int(row["transaction_id"])
            for row in transactions
        )

        # Only update the watermark after successful loading.
        save_watermark(
            state_file,
            max_transaction_id
        )

        logger.info("Watermark updated: %s", max_transaction_id)

        return max_transaction_id
        

    finally:
        connection.close()


if __name__ == "__main__":
    result = run_incremental_pipeline(
        "data/transactions.csv",
        "state/watermark.txt"
    )

    print(f"Pipeline completed. Watermark: {result}")
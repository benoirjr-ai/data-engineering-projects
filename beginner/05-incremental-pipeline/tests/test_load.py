from src.database import create_connection, create_transactions_table
from src.load import load_transactions


def test_load_transactions():
    connection = create_connection()
    create_transactions_table(connection)

    transactions = [
        {
            "transaction_id": "1001",
            "customer_id": "C001",
            "transaction_date": "2026-09-01",
            "amount": "125.50",
            "status": "completed",
        }
    ]

    load_transactions(connection, transactions)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT transaction_id, customer_id, amount "
            "FROM transactions "
            "WHERE transaction_id = 1001"
        )

        result = cursor.fetchone()

    connection.close()

    assert result == (1001, "C001", 125.50)


def test_duplicate_transaction_is_not_inserted_twice():
    connection = create_connection()
    create_transactions_table(connection)

    transaction = {
        "transaction_id": "2001",
        "customer_id": "C002",
        "transaction_date": "2026-09-04",
        "amount": "75.00",
        "status": "completed",
    }

    # Load the same transaction twice.
    load_transactions(connection, [transaction])
    load_transactions(connection, [transaction])

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) "
            "FROM transactions "
            "WHERE transaction_id = 2001"
        )

        result = cursor.fetchone()[0]

    connection.close()

    assert result == 1
import psycopg2


def load_transactions(connection, transactions):
    """Insert new transactions into PostgreSQL."""

    query = """
        INSERT INTO transactions (
            transaction_id,
            customer_id,
            transaction_date,
            amount,
            status
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (transaction_id) DO NOTHING;
    """

    with connection.cursor() as cursor:
        for row in transactions:
            cursor.execute(
                query,
                (
                    int(row["transaction_id"]),
                    row["customer_id"],
                    row["transaction_date"],
                    float(row["amount"]),
                    row["status"],
                ),
            )

    connection.commit()
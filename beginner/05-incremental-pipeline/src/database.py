import psycopg2


def create_connection():
    """Create a connection to PostgreSQL database."""

    return psycopg2.connect(
        host="localhost",
        port=5433,
        database="incremental_db",
        user="incremental_user",
        password="incremental_password"
    )


def create_transactions_table(connection):
    """Create the transactions table if it does not exist."""

    query = """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY,
            customer_id VARCHAR(50) NOT NULL,
            transaction_date DATE NOT NULL,
            amount NUMERIC(12, 2) NOT NULL,
            status VARCHAR(20) NOT NULL
        );
    """

    with connection.cursor() as cursor:
        cursor.execute(query)

    connection.commit()
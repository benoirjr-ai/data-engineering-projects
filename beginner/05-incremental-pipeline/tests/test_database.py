from src.database import create_connection, create_transactions_table


connection = create_connection()

create_transactions_table(connection)

connection.close()

print("Database setup successful.")

"""Verify Python access to the Snowflake raw sales table."""

from src.snowflake_connection import get_snowflake_connection


def test_sales_raw_table():
    connection = get_snowflake_connection()

    try:
        with connection.cursor() as cursor:
            # Confirm that the table exists and is accessible.
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM RETAIL_DB.RAW.SALES_RAW
                """
            )

            row_count = cursor.fetchone()[0]
            print("Table access successful.")
            print(f"Current row count: {row_count}")

            # Confirm the table's column names and types.
            cursor.execute(
                """
                DESCRIBE TABLE RETAIL_DB.RAW.SALES_RAW
                """
            )

            print("\nTable columns:")
            for column in cursor.fetchall():
                print(f"- {column[0]}: {column[1]}")

    finally:
        connection.close()


if __name__ == "__main__":
    test_sales_raw_table()

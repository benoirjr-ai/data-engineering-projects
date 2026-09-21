
from src.load import get_connection, load_customer, quarantine_record


def test_load_customer():
    connection = get_connection()

    customer = {
        "customer_id": 999,
        "full_name": "Test Customer",
        "email": "test@example.com",
        "city": "Yaounde",
        "age": 30,
        "age_group": "adult",
    }

    try:
        load_customer(connection, customer)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    customer_id,
                    full_name,
                    email,
                    city,
                    age,
                    age_group
                FROM customers
                WHERE customer_id = %s
                """,
                (999,),
            )

            result = cursor.fetchone()

        assert result == (
            999,
            "Test Customer",
            "test@example.com",
            "Yaounde",
            30,
            "adult",
        )

    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM customers WHERE customer_id = %s",
                (999,),
            )
            connection.commit()

        connection.close()


def test_load_customer_upsert():
    connection = get_connection()

    customer = {
        "customer_id": 999,
        "full_name": "Original Customer",
        "email": "original@example.com",
        "city": "Yaounde",
        "age": 30,
        "age_group": "adult",
    }

    updated_customer = {
        "customer_id": 999,
        "full_name": "Updated Customer",
        "email": "updated@example.com",
        "city": "Douala",
        "age": 40,
        "age_group": "adult",
    }

    try:
        load_customer(connection, customer)
        load_customer(connection, updated_customer)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    customer_id,
                    full_name,
                    email,
                    city,
                    age,
                    age_group
                FROM customers
                WHERE customer_id = %s
                """,
                (999,),
            )

            result = cursor.fetchone()

        assert result == (
            999,
            "Updated Customer",
            "updated@example.com",
            "Douala",
            40,
            "adult",
        )

    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM customers WHERE customer_id = %s",
                (999,),
            )
            connection.commit()

        connection.close()


def test_quarantine_record():
    connection = get_connection()

    raw_record = {
        "customer_id": "998",
        "name": "Invalid Customer",
        "email": "INVALID",
        "city": "Yaounde",
        "age": "abc",
    }

    errors = [
        "Invalid email",
        "Invalid age",
    ]

    try:
        quarantine_record(
            connection,
            raw_record,
            errors,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    customer_id,
                    raw_record,
                    errors
                FROM customer_quarantine
                WHERE customer_id = %s
                ORDER BY quarantine_id DESC
                LIMIT 1
                """,
                (998,),
            )

            result = cursor.fetchone()

        assert result is not None
        assert result[0] == 998

        assert result[1] == raw_record
        assert result[2] == errors

    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM customer_quarantine
                WHERE customer_id = %s
                """,
                (998,),
            )
            connection.commit()

        connection.close()

import os

from dotenv import load_dotenv
import psycopg

load_dotenv()


def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

def load_customer(connection, record: dict) -> None:
    """
    Insert or update one customer record in PostgreSQL.

    If the customer_id already exists, the existing customer
    will be updated with the incoming values.
    """

    query = """
        INSERT INTO customers (
            customer_id,
            full_name,
            email,
            city,
            age,
            age_group
        )
        VALUES (%s, %s, %s, %s, %s, %s)

        ON CONFLICT (customer_id) DO UPDATE SET
            full_name = EXCLUDED.full_name,
            email = EXCLUDED.email,
            city = EXCLUDED.city,
            age = EXCLUDED.age,
            age_group = EXCLUDED.age_group;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                record["customer_id"],
                record["full_name"],
                record["email"],
                record["city"],
                record["age"],
                record["age_group"],
            ),
        )

    connection.commit()


import json


def quarantine_record(connection, raw_record: dict, errors: list[str],) -> None:
    """
    Store an invalid raw record and its validation errors
    in the quarantine table.
    """

    query = """
        INSERT INTO customer_quarantine (
            customer_id,
            raw_record,
            errors
        )
        VALUES (%s, %s, %s)
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                int(raw_record["customer_id"]),
                json.dumps(raw_record),
                json.dumps(errors),
            ),
        )

    connection.commit()


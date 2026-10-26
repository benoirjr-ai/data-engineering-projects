"""Create and test a connection to Snowflake."""

import os 
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

# Load ther project's .env file from the repository root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

def get_snowflake_connection():
     """Connect to Snowflake using local environment settings."""

     required_settings = [
          "SNOWFLAKE_ACCOUNT",
          "SNOWFLAKE_USER",
          "SNOWFLAKE_PASSWORD",
          "SNOWFLAKE_WAREHOUSE",
          "SNOWFLAKE_DATABASE",
          "SNOWFLAKE_SCHEMA",
          "SNOWFLAKE_ROLE",
     ]

     missing = [
          setting for setting in required_settings
          if not os.getenv(setting)
          or os.getenv(setting).startswith("your_")
     ]

     if missing:
          raise ValueError(
               "Missing or Placeholder snowflake settings: "
               + ", ".join(missing)
          )

     return snowflake.connector.connect(
          account=os.environ["SNOWFLAKE_ACCOUNT"],
          user=os.environ["SNOWFLAKE_USER"],
          password=os.environ["SNOWFLAKE_PASSWORD"],
          warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
          database=os.environ["SNOWFLAKE_DATABASE"],
          schema=os.environ["SNOWFLAKE_SCHEMA"],
          role=os.environ["SNOWFLAKE_ROLE"],
     )

def test_connection():
    """Verify connectivity and the selected Snowflake context."""

    connection = get_snowflake_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    CURRENT_USER(),
                    CURRENT_ROLE(),
                    CURRENT_WAREHOUSE(),
                    CURRENT_DATABASE(),
                    CURRENT_SCHEMA()
                """
            )

            result = cursor.fetchone()
            print("Snowflake connection successful.")
            print(f"User: {result[0]}")
            print(f"Role: {result[1]}")
            print(f"Warehouse: {result[2]}")
            print(f"Database: {result[3]}")
            print(f"Schema: {result[4]}")

    finally:
        connection.close()


if __name__ == "__main__":
    test_connection()

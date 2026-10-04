import duckdb

from producer.logging_config import configure_logging, get_logger


logger = get_logger(__name__)


# ==========================================
# Configuration
# ==========================================

DATABASE_PATH = "warehouse/insurance_analytics.duckdb"

PARQUET_PATH = "spark/output/enriched_claims/*.parquet"


# ==========================================
# Database
# ==========================================

def create_connection(
    database_path: str = DATABASE_PATH,
) -> duckdb.DuckDBPyConnection:
    """Create a DuckDB connection."""

    logger.info(
        "Connecting to DuckDB | path=%s",
        database_path,
    )

    return duckdb.connect(database_path)


# ==========================================
# Warehouse Load
# ==========================================

def create_claims_table(
    connection: duckdb.DuckDBPyConnection,
    parquet_path: str = PARQUET_PATH,
) -> None:
    """Create or replace the claims table from Parquet."""

    logger.info(
        "Building claims table | parquet=%s",
        parquet_path,
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE claims AS
        SELECT *
        FROM read_parquet(?)
        """,
        [parquet_path],
    )

    logger.info(
        "Claims table created successfully."
    )


def get_claim_count(
    connection: duckdb.DuckDBPyConnection,
) -> int:
    """Return the number of claims in the warehouse."""

    result = connection.execute(
        """
        SELECT COUNT(*) AS total_claims
        FROM claims
        """
    ).fetchone()

    return result[0]


def get_claim_preview(
    connection: duckdb.DuckDBPyConnection,
    limit: int = 10,
) -> list[tuple]:
    """Return a small preview of the claims table."""

    result = connection.execute(
        """
        SELECT
            claim_id,
            claim_type,
            claim_amount,
            country,
            risk_indicator_count
        FROM claims
        ORDER BY claim_id
        LIMIT ?
        """,
        [limit],
    ).fetchall()

    return result


def get_claims_schema(
    connection: duckdb.DuckDBPyConnection,
) -> list[tuple]:
    """Return the schema of the claims table."""

    return connection.execute(
        """
        DESCRIBE claims
        """
    ).fetchall()


# ==========================================
# Reporting
# ==========================================

def display_warehouse_report(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    """Display a summary of the loaded warehouse table."""

    total_claims = get_claim_count(connection)
    preview = get_claim_preview(connection)
    schema = get_claims_schema(connection)

    print("\n=== CLAIMS TABLE SUMMARY ===\n")
    print(f"Total claims loaded: {total_claims}")

    print("\n=== CLAIMS TABLE PREVIEW ===\n")

    for row in preview:
        print(row)

    print("\n=== CLAIMS TABLE SCHEMA ===\n")

    for column in schema:
        print(column)


# ==========================================
# Main
# ==========================================

def main() -> None:
    """Load enriched claims into DuckDB."""

    connection = create_connection()

    try:
        create_claims_table(connection)

        display_warehouse_report(connection)

    finally:
        connection.close()

        logger.info(
            "DuckDB warehouse load completed."
        )


if __name__ == "__main__":
    configure_logging()
    main()
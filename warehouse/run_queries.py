import duckdb

from producer.logging_config import configure_logging, get_logger


logger = get_logger(__name__)


# ==========================================
# Configuration
# ==========================================

DB_PATH = "warehouse/insurance_analytics.duckdb"


# ==========================================
# Database
# ==========================================

def create_connection(
    database_path: str = DB_PATH,
) -> duckdb.DuckDBPyConnection:
    """Create a DuckDB connection to the analytics warehouse."""

    logger.info(
        "Connecting to DuckDB | path=%s",
        database_path,
    )

    return duckdb.connect(database_path)


# ==========================================
# Analytics Queries
# ==========================================

def get_claim_count_by_type(
    connection: duckdb.DuckDBPyConnection,
) -> list[tuple]:
    """Return the number of claims for each claim type."""

    return connection.execute(
        """
        SELECT
            claim_type,
            COUNT(*) AS claim_count
        FROM claims
        GROUP BY claim_type
        ORDER BY claim_type
        """
    ).fetchall()


def get_claim_value_by_type(
    connection: duckdb.DuckDBPyConnection,
) -> list[tuple]:
    """Return total claim value for each claim type."""

    return connection.execute(
        """
        SELECT
            claim_type,
            ROUND(SUM(claim_amount), 2) AS total_claim_value
        FROM claims
        GROUP BY claim_type
        ORDER BY total_claim_value DESC
        """
    ).fetchall()


def get_high_value_claims(
    connection: duckdb.DuckDBPyConnection,
) -> list[tuple]:
    """Return claims flagged as high value."""

    return connection.execute(
        """
        SELECT
            claim_id,
            claim_type,
            claim_amount,
            country
        FROM claims
        WHERE high_value_claim = TRUE
        ORDER BY claim_amount DESC
        """
    ).fetchall()


def get_multi_indicator_claims(
    connection: duckdb.DuckDBPyConnection,
) -> list[tuple]:
    """Return claims with at least two risk indicators."""

    return connection.execute(
        """
        SELECT
            claim_id,
            claim_type,
            claim_amount,
            risk_indicator_count
        FROM claims
        WHERE risk_indicator_count >= 2
        ORDER BY risk_indicator_count DESC
        """
    ).fetchall()


# ==========================================
# Reporting
# ==========================================

def display_claim_count_by_type(
    rows: list[tuple],
) -> None:
    """Display claim counts grouped by claim type."""

    print("\n=== CLAIM COUNT BY TYPE ===\n")

    for row in rows:
        print(row)


def display_claim_value_by_type(
    rows: list[tuple],
) -> None:
    """Display total claim value grouped by claim type."""

    print("\n=== TOTAL CLAIM VALUE BY TYPE ===\n")

    for row in rows:
        print(row)


def display_high_value_claims(
    rows: list[tuple],
) -> None:
    """Display high-value claims."""

    print("\n=== HIGH-VALUE CLAIMS ===\n")

    for row in rows:
        print(row)


def display_multi_indicator_claims(
    rows: list[tuple],
) -> None:
    """Display claims with multiple risk indicators."""

    print("\n=== CLAIMS WITH MULTIPLE RISK INDICATORS ===\n")

    for row in rows:
        print(row)


# ==========================================
# Main
# ==========================================

def main() -> None:
    """Run the warehouse analytics queries."""

    connection = create_connection()

    try:
        display_claim_count_by_type(
            get_claim_count_by_type(connection)
        )

        display_claim_value_by_type(
            get_claim_value_by_type(connection)
        )

        display_high_value_claims(
            get_high_value_claims(connection)
        )

        display_multi_indicator_claims(
            get_multi_indicator_claims(connection)
        )

    finally:
        connection.close()

        logger.info(
            "SQL analytics completed."
        )


if __name__ == "__main__":
    configure_logging()
    main()
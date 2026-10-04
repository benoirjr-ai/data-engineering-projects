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
    """Create a DuckDB connection for the analytics warehouse."""

    logger.info(
        "Connecting to DuckDB | path=%s",
        database_path,
    )

    return duckdb.connect(database_path)


# ==========================================
# Queries
# ==========================================

def get_pipeline_summary(
    connection: duckdb.DuckDBPyConnection,
) -> tuple:
    """Return high-level pipeline metrics."""

    return connection.execute(
        """
        SELECT
            COUNT(*) AS total_customers,
            SUM(claim_count) AS total_claims,
            ROUND(SUM(total_claim_value), 2) AS total_claim_value,
            SUM(
                CASE
                    WHEN risk_level = 'HIGH'
                    THEN 1
                    ELSE 0
                END
            ) AS high_risk_customers
        FROM risk_investigation
        """
    ).fetchone()


def get_risk_level_summary(
    connection: duckdb.DuckDBPyConnection,
) -> list[tuple]:
    """Return aggregated metrics by risk level."""

    return connection.execute(
        """
        SELECT
            risk_level,
            customer_count,
            total_claims,
            total_claim_value,
            average_risk_score
        FROM risk_level_summary
        ORDER BY
            CASE risk_level
                WHEN 'HIGH' THEN 1
                WHEN 'MEDIUM' THEN 2
                WHEN 'LOW' THEN 3
            END
        """
    ).fetchall()


def get_top_investigation_customers(
    connection: duckdb.DuckDBPyConnection,
    limit: int = 10,
) -> list[tuple]:
    """Return customers with the highest investigation priority."""

    return connection.execute(
        """
        SELECT
            customer_id,
            risk_score,
            risk_level,
            claim_count,
            high_value_claim_count,
            maximum_claim_value,
            total_risk_indicators
        FROM risk_investigation
        ORDER BY
            risk_score DESC,
            total_risk_indicators DESC
        LIMIT ?
        """,
        [limit],
    ).fetchall()


# ==========================================
# Reporting
# ==========================================

def display_pipeline_summary(
    summary: tuple,
) -> None:
    """Display high-level pipeline metrics."""

    print("\n0. PIPELINE SUMMARY")
    print("-" * 70)

    print(f"Total customers:       {summary[0]}")
    print(f"Total claims:          {summary[1]}")
    print(f"Total claim value:     {summary[2]:,.2f}")
    print(f"High-risk customers:   {summary[3]}")


def display_risk_level_summary(
    rows: list[tuple],
) -> None:
    """Display the risk-level overview."""

    print("\n1. RISK LEVEL OVERVIEW")
    print("-" * 70)

    for row in rows:
        print(
            f"{row[0]:<10} | "
            f"Customers: {row[1]:>3} | "
            f"Claims: {row[2]:>3} | "
            f"Claim Value: {row[3]:>12,.2f} | "
            f"Avg Score: {row[4]:>5.2f}"
        )


def display_investigation_customers(
    rows: list[tuple],
) -> None:
    """Display customers requiring investigation."""

    print("\n2. TOP CUSTOMERS FOR INVESTIGATION")
    print("-" * 70)

    for row in rows:
        print(
            f"{row[0]} | "
            f"Score: {row[1]:>2} | "
            f"Level: {row[2]:<6} | "
            f"Claims: {row[3]:>2} | "
            f"High Value: {row[4]:>2} | "
            f"Max Claim: {row[5]:>10,.2f} | "
            f"Indicators: {row[6]:>2}"
        )


def display_dashboard(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    """Generate the complete analytics dashboard report."""

    print("\n" + "=" * 70)
    print("INSURANCE FRAUD ANALYTICS DASHBOARD")
    print("=" * 70)

    summary = get_pipeline_summary(connection)
    display_pipeline_summary(summary)

    risk_levels = get_risk_level_summary(connection)
    display_risk_level_summary(risk_levels)

    investigation_customers = get_top_investigation_customers(
        connection
    )
    display_investigation_customers(
        investigation_customers
    )


# ==========================================
# Main
# ==========================================

def main() -> None:
    """Generate the insurance fraud analytics report."""

    connection = create_connection()

    try:
        display_dashboard(connection)
    finally:
        connection.close()

        logger.info(
            "Dashboard report completed."
        )


if __name__ == "__main__":
    configure_logging()
    main()
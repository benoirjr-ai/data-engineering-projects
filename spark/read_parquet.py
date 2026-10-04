from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession

from producer.logging_config import configure_logging, get_logger


# ==========================================
# Configuration
# ==========================================

OUTPUT_PATH = "/opt/spark-apps/output/enriched_claims"


TEST_CLAIM_IDS = [
    "CLM-CED5EECC",
    "CLM-2646FA14",
    "CLM-8FCC5E33",
    "CLM-98B5F50C",
]

CLAIM_COLUMNS = [
    "claim_id",
    "claim_amount",
    "claim_amount_band",
    "incident_date",
    "created_at",
    "incident_age_days",
    "reporting_delay_days",
    "high_value_claim",
    "weekend_incident",
    "long_reporting_delay",
    "risk_indicator_count",
]


# ==========================================
# Spark
# ==========================================

def create_spark_session() -> SparkSession:
    """Create the Spark session used by this utility."""

    return (
        SparkSession.builder
        .appName("ReadEnrichedClaims")
        .getOrCreate()
    )


# ==========================================
# Data Access
# ==========================================

def read_enriched_claims(
    spark: SparkSession,
    path: str = OUTPUT_PATH,
) -> DataFrame:
    """Read enriched claims from the Parquet output."""

    logger.info(
        "Reading enriched claims | path=%s",
        path,
    )

    claims = spark.read.parquet(path)

    logger.info(
        "Enriched claims loaded successfully | rows=%s",
        claims.count(),
    )

    return claims


# ==========================================
# Inspection
# ==========================================

def show_test_claims(
    claims: DataFrame,
    claim_ids: list[str] = TEST_CLAIM_IDS,
) -> None:
    """Display selected claims for manual inspection."""

    logger.info(
        "Inspecting test claims | count=%s",
        len(claim_ids),
    )

    (
        claims
        .filter(claims.claim_id.isin(claim_ids))
        .select(*CLAIM_COLUMNS)
        .show(truncate=False)
    )


def show_schema(claims: DataFrame) -> None:
    """Display the DataFrame schema."""

    logger.info("Displaying enriched claims schema.")

    claims.printSchema()


# ==========================================
# Main
# ==========================================

def main() -> None:
    """Read and inspect the enriched claims dataset."""

    spark = create_spark_session()

    try:
        spark.sparkContext.setLogLevel("WARN")

        claims = read_enriched_claims(spark)

        show_test_claims(claims)
        show_schema(claims)

    finally:
        spark.stop()
        logger.info("Spark session stopped.")


if __name__ == "__main__":
    configure_logging()
    logger = get_logger(__name__)
    main()
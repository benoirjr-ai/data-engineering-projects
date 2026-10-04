from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    avg,
    col,
    count,
    round,
    sum,
)

from producer.logging_config import configure_logging, get_logger


# ==========================================
# Configuration
# ==========================================

OUTPUT_PATH = "/opt/spark-apps/output/enriched_claims"


# ==========================================
# Spark
# ==========================================

def create_spark_session() -> SparkSession:
    """Create the Spark session used for batch analytics."""

    return (
        SparkSession.builder
        .appName("ClaimsAnalytics")
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
        "Claims loaded successfully | rows=%s",
        claims.count(),
    )

    return claims


# ==========================================
# Analytics
# ==========================================

def build_claim_type_summary(claims: DataFrame) -> DataFrame:
    """Calculate business metrics grouped by claim type."""

    return (
        claims
        .groupBy("claim_type")
        .agg(
            count("*").alias("claim_count"),
            round(
                sum("claim_amount"),
                2,
            ).alias("total_claim_amount"),
            round(
                avg("claim_amount"),
                2,
            ).alias("average_claim_amount"),
            round(
                avg("reporting_delay_days"),
                2,
            ).alias("average_reporting_delay_days"),
            sum(
                col("high_value_claim").cast("int")
            ).alias("high_value_claim_count"),
        )
        .orderBy("claim_type")
    )


def calculate_total_claims(claims: DataFrame) -> DataFrame:
    """Calculate the total number of claims."""

    return claims.select(
        count("*").alias("total_claims")
    )


def calculate_total_claim_value(claims: DataFrame) -> DataFrame:
    """Calculate the total monetary value of all claims."""

    return claims.select(
        round(
            sum("claim_amount"),
            2,
        ).alias("total_claim_value")
    )


# ==========================================
# Output
# ==========================================

def display_analytics(
    claims: DataFrame,
) -> None:
    """Display the main claims analytics results."""

    logger.info("Displaying claim analytics summary.")

    print("\n=== CLAIM ANALYTICS SUMMARY ===\n")

    build_claim_type_summary(claims).show(
        truncate=False
    )

    print("\n=== TOTAL CLAIMS ===")

    calculate_total_claims(claims).show()

    print("\n=== TOTAL CLAIM VALUE ===")

    calculate_total_claim_value(claims).show()


# ==========================================
# Main
# ==========================================

def main() -> None:
    """Run the claims analytics batch job."""

    spark = create_spark_session()

    try:
        spark.sparkContext.setLogLevel("WARN")

        claims = read_enriched_claims(spark)

        display_analytics(claims)

    finally:
        spark.stop()

        logger.info("Spark session stopped.")


if __name__ == "__main__":
    configure_logging()
    logger = get_logger(__name__)
    main()
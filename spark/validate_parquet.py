from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col

from producer.logging_config import configure_logging, get_logger


logger = get_logger(__name__)


# ==========================================
# Configuration
# ==========================================

PARQUET_PATH = "/opt/spark-apps/output/enriched_claims/*.parquet"

VALID_CLAIM_TYPES = (
    "AUTO",
    "HOME",
    "HEALTH",
    "TRAVEL",
)

MIN_CLAIM_AMOUNT = 100
MAX_CLAIM_AMOUNT = 25_000


# ==========================================
# Spark
# ==========================================

def create_spark_session() -> SparkSession:
    """Create the Spark session used for validation."""

    spark = (
        SparkSession.builder
        .appName("ValidateEnrichedClaims")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    return spark


# ==========================================
# Data Access
# ==========================================

def read_claims(
    spark: SparkSession,
    path: str = PARQUET_PATH,
) -> DataFrame:
    """Read enriched claims from Parquet."""

    logger.info(
        "Reading enriched claims | path=%s",
        path,
    )

    return spark.read.parquet(path)


# ==========================================
# Data Quality Checks
# ==========================================

def count_null_claim_ids(claims: DataFrame) -> int:
    """Count claims with missing claim IDs."""

    return claims.filter(
        col("claim_id").isNull()
    ).count()


def count_null_claim_amounts(claims: DataFrame) -> int:
    """Count claims with missing claim amounts."""

    return claims.filter(
        col("claim_amount").isNull()
    ).count()


def count_invalid_claim_amounts(claims: DataFrame) -> int:
    """Count claims outside the accepted amount range."""

    return claims.filter(
        (col("claim_amount") < MIN_CLAIM_AMOUNT)
        | (col("claim_amount") > MAX_CLAIM_AMOUNT)
    ).count()


def count_invalid_claim_types(claims: DataFrame) -> int:
    """Count claims with unsupported claim types."""

    return claims.filter(
        ~col("claim_type").isin(*VALID_CLAIM_TYPES)
    ).count()


def run_quality_checks(claims: DataFrame) -> dict[str, int]:
    """Run all configured data-quality checks."""

    return {
        "null_claim_ids": count_null_claim_ids(claims),
        "null_claim_amounts": count_null_claim_amounts(claims),
        "invalid_claim_amounts": count_invalid_claim_amounts(claims),
        "invalid_claim_types": count_invalid_claim_types(claims),
    }


# ==========================================
# Reporting
# ==========================================

def display_quality_report(
    claims: DataFrame,
    results: dict[str, int],
) -> None:
    """Display the validation results."""

    total_errors = sum(results.values())

    print("\n=== ENRICHED CLAIMS DATA QUALITY REPORT ===\n")

    print(f"Total records: {claims.count()}")

    print("\nSchema:")
    claims.printSchema()

    print("\nData quality checks:")

    print(
        f"Null claim IDs: "
        f"{results['null_claim_ids']}"
    )

    print(
        f"Null claim amounts: "
        f"{results['null_claim_amounts']}"
    )

    print(
        f"Invalid claim amounts: "
        f"{results['invalid_claim_amounts']}"
    )

    print(
        f"Invalid claim types: "
        f"{results['invalid_claim_types']}"
    )

    print(
        f"\nTotal data-quality errors: "
        f"{total_errors}"
    )

    if total_errors == 0:
        print("\nDATA QUALITY PASSED")
    else:
        print("\nDATA QUALITY FAILED")


# ==========================================
# Main
# ==========================================

def main() -> None:
    """Validate the enriched claims Parquet dataset."""

    spark = create_spark_session()

    try:
        claims = read_claims(spark)

        logger.info(
            "Claims loaded successfully | rows=%s",
            claims.count(),
        )

        results = run_quality_checks(claims)

        display_quality_report(
            claims,
            results,
        )

    finally:
        spark.stop()

        logger.info(
            "Spark session stopped."
        )


if __name__ == "__main__":
    configure_logging()
    main()
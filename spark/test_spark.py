from pyspark.sql import SparkSession

from producer.logging_config import configure_logging, get_logger


logger = get_logger(__name__)


# ==========================================
# Spark
# ==========================================

def create_spark_session() -> SparkSession:
    """Create a local Spark session for the smoke test."""

    return (
        SparkSession.builder
        .appName("InsuranceFraudSparkSmokeTest")
        .master("local[2]")
        .getOrCreate()
    )


# ==========================================
# Smoke Test
# ==========================================

def run_smoke_test() -> None:
    """Verify that Spark can start, report its version, and stop."""

    spark = create_spark_session()

    try:
        logger.info(
            "Spark started successfully | version=%s",
            spark.version,
        )

    finally:
        spark.stop()

        logger.info(
            "Spark stopped successfully."
        )


# ==========================================
# Entry Point
# ==========================================

if __name__ == "__main__":
    configure_logging()
    run_smoke_test()
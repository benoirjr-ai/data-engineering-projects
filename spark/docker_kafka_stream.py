from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col,
    current_date,
    datediff,
    dayofweek,
    from_json,
    to_date,
    to_timestamp,
    when,
)
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
)

from producer.logging_config import configure_logging, get_logger


logger = get_logger(__name__)


# ==========================================
# Kafka Configuration
# ==========================================

KAFKA_BOOTSTRAP_SERVERS = "kafka:29092"
VALIDATED_TOPIC = "insurance.claims.validated"


# ==========================================
# Storage Configuration
# ==========================================

OUTPUT_PATH = "/opt/spark-apps/output/enriched_claims"
CHECKPOINT_PATH = "/opt/spark-apps/checkpoints/enriched_claims"


# ==========================================
# Streaming Configuration
# ==========================================

PROCESSING_INTERVAL = "10 seconds"


# ==========================================
# Claim Schema
# ==========================================

CLAIM_SCHEMA = StructType([
    StructField("claim_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("customer_name", StringType(), True),
    StructField("claim_type", StringType(), True),
    StructField("claim_amount", DoubleType(), True),
    StructField("country", StringType(), True),
    StructField("incident_date", StringType(), True),
    StructField("created_at", StringType(), True),
])


# ==========================================
# Spark Session
# ==========================================

def create_spark_session() -> SparkSession:
    """Create and configure the Spark session."""

    spark = (
        SparkSession.builder
        .appName("InsuranceClaimsStreaming")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    return spark


# ==========================================
# Kafka Source
# ==========================================

def read_claims_stream(
    spark: SparkSession,
) -> DataFrame:
    """Read validated claims from Kafka."""

    logger.info(
        "Starting Kafka stream | topic=%s | brokers=%s",
        VALIDATED_TOPIC,
        KAFKA_BOOTSTRAP_SERVERS,
    )

    return (
        spark.readStream
        .format("kafka")
        .option(
            "kafka.bootstrap.servers",
            KAFKA_BOOTSTRAP_SERVERS,
        )
        .option(
            "subscribe",
            VALIDATED_TOPIC,
        )
        .option(
            "startingOffsets",
            "earliest",
        )
        .option(
            "failOnDataLoss",
            "false",
        )
        .load()
    )


# ==========================================
# JSON Parsing
# ==========================================

def parse_claims(
    claims_stream: DataFrame,
) -> DataFrame:
    """Convert Kafka JSON payloads into structured columns."""

    return (
        claims_stream
        .select(
            col("value")
            .cast("string")
            .alias("claim_json")
        )
        .select(
            from_json(
                col("claim_json"),
                CLAIM_SCHEMA,
            ).alias("claim")
        )
        .select("claim.*")
    )


# ==========================================
# Feature Engineering
# ==========================================

def enrich_claims(
    claims: DataFrame,
) -> DataFrame:
    """
    Apply business transformations and risk indicators.

    Incident age is calculated relative to the current
    processing date.
    """

    typed_claims = (
        claims
        .withColumn(
            "incident_date",
            to_date(col("incident_date")),
        )
        .withColumn(
            "created_at",
            to_timestamp(col("created_at")),
        )
    )

    created_date = to_date(col("created_at"))

    enriched_claims = (
        typed_claims
        .withColumn(
            "claim_amount_band",
            when(
                col("claim_amount") < 5_000,
                "LOW",
            )
            .when(
                col("claim_amount") < 15_000,
                "MEDIUM",
            )
            .otherwise("HIGH"),
        )
        .withColumn(
            "incident_age_days",
            datediff(
                current_date(),
                col("incident_date"),
            ),
        )
        .withColumn(
            "reporting_delay_days",
            datediff(
                created_date,
                col("incident_date"),
            ),
        )
        .withColumn(
            "high_value_claim",
            col("claim_amount") >= 15_000,
        )
        .withColumn(
            "weekend_incident",
            dayofweek(
                col("incident_date")
            ).isin(1, 7),
        )
        .withColumn(
            "long_reporting_delay",
            col("reporting_delay_days") > 7,
        )
        .withColumn(
            "risk_indicator_count",
            (
                col("high_value_claim").cast("int")
                + col("long_reporting_delay").cast("int")
                + col("weekend_incident").cast("int")
            ),
        )
    )

    return enriched_claims


# ==========================================
# Parquet Sink
# ==========================================

def write_enriched_claims(
    enriched_claims: DataFrame,
) -> StreamingQuery:
    """Write enriched claims to Parquet with checkpointing."""

    logger.info(
        "Starting streaming sink | path=%s | checkpoint=%s",
        OUTPUT_PATH,
        CHECKPOINT_PATH,
    )

    return (
        enriched_claims.writeStream
        .format("parquet")
        .outputMode("append")
        .trigger(
            processingTime=PROCESSING_INTERVAL
        )
        .option(
            "path",
            OUTPUT_PATH,
        )
        .option(
            "checkpointLocation",
            CHECKPOINT_PATH,
        )
        .start()
    )


# ==========================================
# Pipeline
# ==========================================

def run_pipeline(
    spark: SparkSession,
) -> StreamingQuery:
    """Build and start the complete streaming pipeline."""

    claims_stream = read_claims_stream(spark)

    claims = parse_claims(
        claims_stream
    )

    enriched_claims = enrich_claims(
        claims
    )

    return write_enriched_claims(
        enriched_claims
    )


# ==========================================
# Entry Point
# ==========================================

def main() -> None:
    """Run the insurance claims streaming pipeline."""

    configure_logging()

    spark = create_spark_session()

    try:
        query = run_pipeline(spark)

        logger.info(
            "Spark streaming query started successfully."
        )

        query.awaitTermination()

    except KeyboardInterrupt:
        logger.info(
            "Pipeline stopped manually via user interrupt."
        )

    except Exception:
        logger.exception(
            "Pipeline terminated due to an unexpected "
            "runtime exception."
        )
        raise

    finally:
        spark.stop()

        logger.info(
            "Spark session cleanly shut down."
        )


if __name__ == "__main__":
    main()
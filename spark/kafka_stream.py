from pyspark.sql import SparkSession


# ==========================================
# Create Spark session
# ==========================================

spark = (
    SparkSession.builder
    .appName("InsuranceClaimStreaming")
    .master("local[2]")
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0",
    )
    .getOrCreate()
)


# ==========================================
# Reduce Spark logging
# ==========================================

spark.sparkContext.setLogLevel("WARN")


# ==========================================
# Read insurance claims from Kafka
# ==========================================

claim_stream = (
    spark.readStream
    .format("kafka")
    .option(
        "kafka.bootstrap.servers",
        "localhost:9092",
    )
    .option(
        "subscribe",
        "insurance.claims",
    )
    .option(
        "startingOffsets",
        "earliest",
    )
    .load()
)


# ==========================================
# Select Kafka message value
# ==========================================

claims = claim_stream.selectExpr(
    "CAST(value AS STRING) AS claim_json"
)


# ==========================================
# Write stream to console
# ==========================================

query = (
    claims.writeStream
    .format("console")
    .outputMode("append")
    .option("truncate", False)
    .option(
        "checkpointLocation",
        "C:/temp/spark-checkpoints/kafka_test",
    )
    .start()
)


print("Spark Kafka streaming started.")
print("Waiting for claims...")


query.awaitTermination()
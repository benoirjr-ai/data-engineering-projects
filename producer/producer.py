import argparse
import json
import time

from confluent_kafka import KafkaException, Producer

from producer.claim_generator import generate_claim
from producer.logging_config import configure_logging, get_logger


# ==========================================
# Logging
# ==========================================

logger = get_logger(__name__)


# ==========================================
# Kafka configuration
# ==========================================

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
CLAIMS_TOPIC = "insurance.claims"


# ==========================================
# Kafka producer
# ==========================================

def create_producer() -> Producer:
    """Create a Kafka producer using the application configuration."""
    return Producer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    })

# ==========================================
# Kafka delivery callback
# ==========================================

def delivery_report(error, message):
    """Log the result of a Kafka message delivery."""

    if error is not None:
        logger.error(
            "Claim delivery failed | error=%s",
            error,
        )
        return

    logger.info(
        "Claim delivered | topic=%s | partition=%s | offset=%s",
        message.topic(),
        message.partition(),
        message.offset(),
    )


# ==========================================
# Claim production
# ==========================================

def produce_claims(producer, total_claims, sleep_interval):
    """
    Generate claims and publish them to Kafka.

    The Kafka producer is passed into the function so the
    production logic can be tested independently of Kafka.

    Returns the number of claims successfully queued
    for delivery.
    """

    queued_claims = 0

    for iteration in range(1, total_claims + 1):

        try:
            # Generate a new claim.
            claim = generate_claim()

            claim_id = claim.get("claim_id")

            if not claim_id:
                logger.warning(
                    "Claim missing claim_id | iteration=%s",
                    iteration,
                )
                continue

            # Serialize the claim before sending it to Kafka.
            payload = json.dumps(claim)

            producer.produce(
                topic=CLAIMS_TOPIC,
                key=claim_id,
                value=payload,
                callback=delivery_report,
            )

            queued_claims += 1

            # Process delivery callbacks for messages
            # that have already completed.
            producer.poll(0)

            logger.info(
                "Claim queued | claim_id=%s | progress=%s/%s",
                claim_id,
                iteration,
                total_claims,
            )

        except (TypeError, ValueError) as serialization_error:
            logger.error(
                "Failed to serialize claim | iteration=%s | error=%s",
                iteration,
                serialization_error,
            )

        except BufferError:
            logger.warning(
                "Kafka producer queue is full | "
                "flushing pending messages"
            )

            producer.flush()

        except KafkaException as kafka_error:
            logger.error(
                "Kafka error | iteration=%s | error=%s",
                iteration,
                kafka_error,
            )

        except Exception:
            logger.exception(
                "Unexpected error while processing claim | iteration=%s",
                iteration,
            )

        time.sleep(sleep_interval)

    return queued_claims


# ==========================================
# Command-line arguments
# ==========================================

def parse_arguments():
    """Parse runtime options for the producer."""

    parser = argparse.ArgumentParser(
        description=(
            "Generate insurance claims and publish them to Kafka."
        )
    )

    parser.add_argument(
        "--claims",
        type=int,
        default=100,
        help="Number of claims to generate.",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=2,
        help="Seconds to wait between claims.",
    )

    return parser.parse_args()


# ==========================================
# Application entry point
# ==========================================

def main():
    """Run the Kafka claim producer."""

    configure_logging()

    args = parse_arguments()

    logger.info(
        "Kafka producer starting | topic=%s | "
        "total_claims=%s | interval=%s",
        CLAIMS_TOPIC,
        args.claims,
        args.interval,
    )

    kafka_producer = create_producer()

    queued_claims = produce_claims(
        producer=kafka_producer,
        total_claims=args.claims,
        sleep_interval=args.interval,
    )

    logger.info("Flushing remaining Kafka messages...")

    remaining_messages = kafka_producer.flush()

    if remaining_messages > 0:
        logger.warning(
            "Kafka producer stopped with undelivered messages | "
            "remaining=%s",
            remaining_messages,
        )

    logger.info(
        "Producer finished | queued_claims=%s | requested_claims=%s",
        queued_claims,
        args.claims,
    )


if __name__ == "__main__":
    main()
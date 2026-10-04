import json

from confluent_kafka import Consumer, KafkaException, Producer

from producer.duplicate_checker import is_duplicate
from producer.logging_config import configure_logging, get_logger
from producer.validator import validate_claim


# ==========================================
# Logging
# ==========================================

logger = get_logger(__name__)


# ==========================================
# Kafka configuration
# ==========================================

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

CLAIMS_TOPIC = "insurance.claims"
DLQ_TOPIC = "insurance.claims.dlq"
VALIDATED_TOPIC = "insurance.claims.validated"

CONSUMER_GROUP = "insurance-claims-consumer"


# ==========================================
# Kafka clients
# ==========================================

consumer = Consumer({
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    "group.id": CONSUMER_GROUP,
    "auto.offset.reset": "earliest",
})

dlq_producer = Producer({
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
})

validated_producer = Producer({
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
})


# ==========================================
# Delivery callbacks
# ==========================================

def delivery_report(error, message):
    """Log the result of a DLQ message delivery."""

    if error is not None:
        logger.error(
            "DLQ delivery failed | error=%s",
            error,
        )
        return

    logger.info(
        "DLQ message delivered | topic=%s | partition=%s | offset=%s",
        message.topic(),
        message.partition(),
        message.offset(),
    )


def validated_delivery_report(error, message):
    """Log the result of a validated claim delivery."""

    if error is not None:
        logger.error(
            "Validated claim delivery failed | error=%s",
            error,
        )
        return

    logger.info(
        "Validated claim delivered | topic=%s | "
        "partition=%s | offset=%s",
        message.topic(),
        message.partition(),
        message.offset(),
    )


# ==========================================
# DLQ handling
# ==========================================

def send_to_dlq(key, payload):
    """
    Send a rejected record to the dead-letter topic.

    The producer is flushed so the consumer can confirm that
    the rejected message reached Kafka before continuing.
    """

    dlq_producer.produce(
        topic=DLQ_TOPIC,
        key=key,
        value=json.dumps(payload),
        callback=delivery_report,
    )

    remaining = dlq_producer.flush(timeout=10)

    if remaining > 0:
        logger.warning(
            "DLQ messages still pending | remaining=%s",
            remaining,
        )


# ==========================================
# Claim processing
# ==========================================

def process_message(message):
    """
    Process one Kafka message.

    Returns:
        "validated" when the claim is accepted.
        "dlq" when the claim is rejected.
        "error" when a Kafka-level processing error occurs.
    """

    raw_message = message.value().decode("utf-8")

    # ==========================================
    # JSON parsing
    # ==========================================

    try:
        claim = json.loads(raw_message)

    except json.JSONDecodeError as error:
        logger.error(
            "Malformed JSON received | key=%s | error=%s",
            message.key(),
            error,
        )

        malformed_record = {
            "error_type": "malformed_json",
            "raw_message": raw_message,
            "error": str(error),
        }

        send_to_dlq(
            key=message.key(),
            payload=malformed_record,
        )

        return "dlq"

    # ==========================================
    # Claim validation
    # ==========================================

    errors = validate_claim(claim)

    if errors:
        logger.warning(
            "Claim validation failed | claim_id=%s | errors=%s",
            claim.get("claim_id"),
            errors,
        )

        claim["validation_errors"] = errors

        send_to_dlq(
            key=claim.get("claim_id") or "UNKNOWN",
            payload=claim,
        )

        return "dlq"

    logger.info(
        "Claim validation passed | claim_id=%s",
        claim["claim_id"],
    )

    # ==========================================
    # Duplicate detection
    # ==========================================

    if is_duplicate(claim["claim_id"]):
        logger.warning(
            "Duplicate claim detected | claim_id=%s",
            claim["claim_id"],
        )

        claim["validation_errors"] = [
            "Duplicate claim_id"
        ]

        send_to_dlq(
            key=claim["claim_id"],
            payload=claim,
        )

        return "dlq"

    logger.info(
        "Claim accepted | claim_id=%s",
        claim["claim_id"],
    )

    # ==========================================
    # Validated output
    # ==========================================

    validated_producer.produce(
        topic=VALIDATED_TOPIC,
        key=claim["claim_id"],
        value=json.dumps(claim),
        callback=validated_delivery_report,
    )

    remaining = validated_producer.flush(timeout=10)

    if remaining > 0:
        logger.warning(
            "Validated messages still pending | remaining=%s",
            remaining,
        )

    return "validated"


# ==========================================
# Consumer loop
# ==========================================

def consume_claims():
    """Continuously consume and process insurance claims."""

    consumer.subscribe([CLAIMS_TOPIC])

    logger.info(
        "Consumer started | topic=%s | group=%s",
        CLAIMS_TOPIC,
        CONSUMER_GROUP,
    )

    while True:
        message = consumer.poll(1.0)

        if message is None:
            continue

        if message.error():
            logger.error(
                "Kafka consumer error | error=%s",
                message.error(),
            )
            continue

        process_message(message)


# ==========================================
# Application entry point
# ==========================================

def main():
    """Start the insurance claims consumer."""

    configure_logging()

    try:
        consume_claims()

    except KeyboardInterrupt:
        logger.info("Consumer stopped by user.")

    except KafkaException:
        logger.exception("Kafka error stopped the consumer.")

    except Exception:
        logger.exception(
            "Unexpected error stopped the consumer."
        )

    finally:
        consumer.close()
        logger.info("Consumer closed.")


if __name__ == "__main__":
    main()
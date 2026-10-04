from confluent_kafka import Producer

from producer.logging_config import configure_logging, get_logger


# ==========================================
# Logging configuration
# ==========================================

logger = get_logger(__name__)


# ==========================================
# Kafka producer configuration
# ==========================================

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
CLAIMS_TOPIC = "insurance.claims"

producer = Producer({
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS
})


# ==========================================
# Test
# ==========================================

def test_malformed_json_sent_to_kafka():
    configure_logging()

    delivery_errors = []

    # ==========================================
    # Deliberately malformed JSON
    # ==========================================

    # The closing "}" is intentionally missing.
    # This allows us to test how downstream consumers
    # handle messages that cannot be parsed as JSON.
    malformed_message = (
        '{"claim_id": "CLM-BAD-JSON", '
        '"customer_id": "CUS-123", '
        '"customer_name": "Test Customer"'
    )

    logger.info(
        "Preparing malformed JSON message | key=CLM-BAD-JSON"
    )

    # ==========================================
    # Delivery callback
    # ==========================================

    def delivery_report(error, message):
        if error is not None:
            delivery_errors.append(error)

            logger.error(
                "Malformed message delivery failed | error=%s",
                error,
            )
            return

        logger.info(
            "Malformed message delivered | topic=%s | "
            "partition=%s | offset=%s",
            message.topic(),
            message.partition(),
            message.offset(),
        )

    # ==========================================
    # Send malformed message to Kafka
    # ==========================================

    producer.produce(
        topic=CLAIMS_TOPIC,
        key="CLM-BAD-JSON",
        value=malformed_message,
        callback=delivery_report,
    )

    # ==========================================
    # Wait for Kafka delivery
    # ==========================================

    remaining_messages = producer.flush()

    assert remaining_messages == 0
    assert delivery_errors == []

    logger.info(
        "Malformed JSON message sent successfully | key=CLM-BAD-JSON"
    )
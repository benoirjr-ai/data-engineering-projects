import json

from confluent_kafka import Producer

from producer.claim_generator import generate_claim
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

def test_missing_customer_name_sent_to_kafka():
    configure_logging()

    delivery_errors = []

    # ==========================================
    # Generate a deliberately invalid claim
    # ==========================================

    # This test is deterministic:
    # every run creates a claim where customer_name is None.
    bad_claim = generate_claim(
        bad_data_type="missing_customer_name"
    )

    logger.info(
        "Generated bad claim | claim_id=%s | customer_name=%s",
        bad_claim["claim_id"],
        bad_claim["customer_name"],
    )

    # ==========================================
    # Delivery callback
    # ==========================================

    def delivery_report(error, message):
        if error is not None:
            delivery_errors.append(error)

            logger.error(
                "Claim delivery failed | claim_id=%s | error=%s",
                bad_claim["claim_id"],
                error,
            )
            return

        logger.info(
            "Bad claim delivered | topic=%s | partition=%s | offset=%s",
            message.topic(),
            message.partition(),
            message.offset(),
        )

    # ==========================================
    # Send invalid claim to Kafka
    # ==========================================

    producer.produce(
        topic=CLAIMS_TOPIC,
        key=bad_claim["claim_id"],
        value=json.dumps(bad_claim),
        callback=delivery_report,
    )

    # ==========================================
    # Wait for Kafka delivery
    # ==========================================

    remaining_messages = producer.flush()

    assert remaining_messages == 0
    assert delivery_errors == []

    logger.info(
        "Invalid claim sent successfully | claim_id=%s",
        bad_claim["claim_id"],
    )
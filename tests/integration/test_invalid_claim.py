import json

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

def test_invalid_claim_sent_to_kafka():
    configure_logging()

    delivery_errors = []

    # ==========================================
    # Deliberately invalid claim
    # ==========================================

    invalid_claim = {
        "claim_id": "CLM-INVALID001",
        "customer_id": "CUS-INVALID001",
        "customer_name": "Test Customer",
        "claim_type": "INVALID",
        "claim_amount": 50,
        "country": "Cameroon",
        "incident_date": "2026-09-28",
        "created_at": "2026-09-28T22:00:00+00:00",
    }

    logger.info(
        "Preparing invalid claim | claim_id=%s",
        invalid_claim["claim_id"],
    )

    # ==========================================
    # Delivery callback
    # ==========================================

    def delivery_report(error, message):
        if error is not None:
            delivery_errors.append(error)

            logger.error(
                "Claim delivery failed | claim_id=%s | error=%s",
                invalid_claim["claim_id"],
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
    # Send claim to the normal claims topic
    # ==========================================

    producer.produce(
        topic=CLAIMS_TOPIC,
        key=invalid_claim["claim_id"],
        value=json.dumps(invalid_claim),
        callback=delivery_report,
    )

    # ==========================================
    # Wait for Kafka delivery
    # ==========================================

    remaining_messages = producer.flush()

    assert remaining_messages == 0
    assert delivery_errors == []

    logger.info(
        "Invalid test claim sent successfully | claim_id=%s",
        invalid_claim["claim_id"],
    )
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

def test_duplicate_claim_sent_twice():
    configure_logging()

    delivery_errors = []

    # ==========================================
    # Claim to send twice
    # ==========================================

    claim = {
        "claim_id": "CLM-DUPLICATE-001",
        "customer_id": "CUS-DUPLICATE-001",
        "customer_name": "Duplicate Test Customer",
        "claim_type": "AUTO",
        "claim_amount": 5000,
        "country": "France",
        "incident_date": "2026-09-28",
        "created_at": "2026-09-29T07:30:00+00:00",
    }

    logger.info(
        "Preparing duplicate claim test | claim_id=%s",
        claim["claim_id"],
    )

    # ==========================================
    # Delivery callback
    # ==========================================

    def delivery_report(error, message):
        if error is not None:
            delivery_errors.append(error)

            logger.error(
                "Claim delivery failed | claim_id=%s | error=%s",
                claim["claim_id"],
                error,
            )
            return

        logger.info(
            "Claim delivered | claim_id=%s | topic=%s | "
            "partition=%s | offset=%s",
            claim["claim_id"],
            message.topic(),
            message.partition(),
            message.offset(),
        )

    # ==========================================
    # Send the same claim twice
    # ==========================================

    for attempt in range(2):
        producer.produce(
            topic=CLAIMS_TOPIC,
            key=claim["claim_id"],
            value=json.dumps(claim),
            callback=delivery_report,
        )

        logger.info(
            "Duplicate claim submitted | attempt=%s | claim_id=%s",
            attempt + 1,
            claim["claim_id"],
        )

    # ==========================================
    # Wait for Kafka delivery
    # ==========================================

    remaining_messages = producer.flush()

    assert remaining_messages == 0
    assert delivery_errors == []

    logger.info(
        "Same claim successfully sent twice | claim_id=%s",
        claim["claim_id"],
    )
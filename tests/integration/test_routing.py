import json
import uuid

from confluent_kafka import Consumer, Producer

from producer.consumer import process_message
from producer.logging_config import configure_logging, get_logger


# ==========================================
# Logging configuration
# ==========================================

logger = get_logger(__name__)


# ==========================================
# Kafka configuration
# ==========================================

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

VALIDATED_TOPIC = "insurance.claims.validated"
DLQ_TOPIC = "insurance.claims.dlq"


# ==========================================
# Test message helper
# ==========================================

class FakeKafkaMessage:
    """
    Minimal Kafka message implementation for testing
    process_message() without starting the infinite consumer loop.
    """

    def __init__(self, key, value):
        self._key = key
        self._value = value

    def key(self):
        return self._key.encode("utf-8")

    def value(self):
        return self._value.encode("utf-8")


# ==========================================
# Kafka helper
# ==========================================

def consume_until_claim_found(
    topic,
    claim_id,
    timeout=10,
):
    """
    Consume messages from a Kafka topic until the expected
    claim ID is found or the timeout is reached.
    """

    consumer = Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": f"routing-test-{uuid.uuid4()}",
        "auto.offset.reset": "earliest",
    })

    consumer.subscribe([topic])

    try:
        while True:
            message = consumer.poll(1.0)

            if message is None:
                timeout -= 1

                if timeout <= 0:
                    return None

                continue

            if message.error():
                continue

            try:
                payload = json.loads(
                    message.value().decode("utf-8")
                )
            except json.JSONDecodeError:
                continue

            if payload.get("claim_id") == claim_id:
                return payload

    finally:
        consumer.close()


# ==========================================
# Test
# ==========================================

def test_routing_claims_to_correct_topics():
    configure_logging()

    producer = Producer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    })

    # ==========================================
    # Valid claim
    # ==========================================

    valid_claim = {
        "claim_id": "CLM-ROUTING-VALID-001",
        "customer_id": "CUS-ROUTING-VALID-001",
        "customer_name": "Test Valid Customer",
        "claim_type": "AUTO",
        "claim_amount": 5000,
        "country": "France",
        "incident_date": "2026-09-28",
        "created_at": "2026-09-29T07:30:00+00:00",
    }

    # ==========================================
    # Invalid claim
    # ==========================================

    invalid_claim = {
        "claim_id": "CLM-ROUTING-INVALID-002",
        "customer_id": "CUS-ROUTING-INVALID-002",
        "customer_name": "Test Invalid Customer",
        "claim_type": "INVALID",
        "claim_amount": 50,
        "country": "Cameroon",
        "incident_date": "2026-09-28",
        "created_at": "2026-09-29T07:30:00+00:00",
    }

    logger.info(
        "Starting routing test | valid=%s | invalid=%s",
        valid_claim["claim_id"],
        invalid_claim["claim_id"],
    )

    # ==========================================
    # Process valid claim
    # ==========================================

    valid_message = FakeKafkaMessage(
        key=valid_claim["claim_id"],
        value=json.dumps(valid_claim),
    )

    valid_result = process_message(valid_message)

    assert valid_result == "validated"

    logger.info(
        "Valid claim processed | result=%s",
        valid_result,
    )

    # ==========================================
    # Process invalid claim
    # ==========================================

    invalid_message = FakeKafkaMessage(
        key=invalid_claim["claim_id"],
        value=json.dumps(invalid_claim),
    )

    invalid_result = process_message(invalid_message)

    assert invalid_result == "dlq"

    logger.info(
        "Invalid claim processed | result=%s",
        invalid_result,
    )

    # ==========================================
    # Verify validated topic
    # ==========================================

    validated_claim = consume_until_claim_found(
        topic=VALIDATED_TOPIC,
        claim_id=valid_claim["claim_id"],
    )

    assert validated_claim is not None
    assert validated_claim["claim_id"] == valid_claim["claim_id"]

    logger.info(
        "Valid claim found in validated topic | claim_id=%s",
        valid_claim["claim_id"],
    )

    # ==========================================
    # Verify DLQ topic
    # ==========================================

    rejected_claim = consume_until_claim_found(
        topic=DLQ_TOPIC,
        claim_id=invalid_claim["claim_id"],
    )

    assert rejected_claim is not None
    assert rejected_claim["claim_id"] == invalid_claim["claim_id"]

    assert "validation_errors" in rejected_claim

    logger.info(
        "Invalid claim found in DLQ | claim_id=%s | errors=%s",
        invalid_claim["claim_id"],
        rejected_claim["validation_errors"],
    )

    logger.info(
        "Routing test passed | "
        "valid -> validated | invalid -> DLQ"
    )
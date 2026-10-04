from producer.consumer import process_message
from producer.logging_config import configure_logging


class FakeKafkaMessage:
    """Minimal Kafka message used to test process_message()."""

    def __init__(self, key, value):
        self._key = key
        self._value = value

    def key(self):
        return self._key.encode("utf-8") if self._key else None

    def value(self):
        return self._value.encode("utf-8")


def test_missing_claim_id_is_sent_to_dlq():
    configure_logging()

    claim_without_id = {
        "customer_id": "CUS-MISSING-ID",
        "customer_name": "Missing ID Customer",
        "claim_type": "AUTO",
        "claim_amount": 5000,
        "country": "France",
        "incident_date": "2026-09-28",
        "created_at": "2026-09-29T07:30:00+00:00",
    }

    message = FakeKafkaMessage(
        key="missing-key",
        value=__import__("json").dumps(claim_without_id),
    )

    result = process_message(message)

    assert result == "dlq"
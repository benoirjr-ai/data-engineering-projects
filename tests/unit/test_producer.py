from producer.producer import produce_claims


class FakeProducer:
    """Minimal Kafka producer replacement for unit testing."""

    def __init__(self):
        self.messages = []
        self.poll_calls = 0
        self.flush_calls = 0

    def produce(self, topic, key, value, callback):
        self.messages.append(
            {
                "topic": topic,
                "key": key,
                "value": value,
                "callback": callback,
            }
        )

    def poll(self, timeout):
        self.poll_calls += 1

    def flush(self):
        self.flush_calls += 1


def test_produce_claims_queues_generated_claims(monkeypatch):
    """Generated claims should be serialized and sent to Kafka."""

    fake_producer = FakeProducer()

    fake_claim = {
        "claim_id": "CLM-TEST001",
        "customer_id": "CUS-TEST001",
        "customer_name": "Test Customer",
        "claim_type": "AUTO",
        "claim_amount": 5000.0,
        "country": "Cameroon",
        "incident_date": "2026-01-10",
        "created_at": "2026-01-12T10:00:00",
    }

    monkeypatch.setattr(
        "producer.producer.generate_claim",
        lambda: fake_claim,
    )

    queued_claims = produce_claims(
        producer=fake_producer,
        total_claims=1,
        sleep_interval=0,
    )

    assert queued_claims == 1
    assert len(fake_producer.messages) == 1

    message = fake_producer.messages[0]

    assert message["topic"] == "insurance.claims"
    assert message["key"] == "CLM-TEST001"
    assert '"claim_id": "CLM-TEST001"' in message["value"]
    assert fake_producer.poll_calls == 1

def test_produce_claims_skips_claim_without_id(monkeypatch):
    """Claims without a claim_id should not be sent to Kafka."""

    fake_producer = FakeProducer()

    invalid_claim = {
        "customer_id": "CUS-TEST001",
        "customer_name": "Test Customer",
        "claim_type": "AUTO",
        "claim_amount": 5000.0,
        "country": "Cameroon",
        "incident_date": "2026-01-10",
        "created_at": "2026-01-12T10:00:00",
    }

    monkeypatch.setattr(
        "producer.producer.generate_claim",
        lambda: invalid_claim,
    )

    queued_claims = produce_claims(
        producer=fake_producer,
        total_claims=1,
        sleep_interval=0,
    )

    assert queued_claims == 0
    assert len(fake_producer.messages) == 0
    assert fake_producer.poll_calls == 0
from datetime import datetime

from producer.claim_generator import generate_claim


def test_reporting_delay_is_valid():
    claim = generate_claim()

    incident_date = datetime.fromisoformat(
        claim["incident_date"]
    )

    created_at = datetime.fromisoformat(
        claim["created_at"]
    )

    reporting_delay = (
        created_at.date() - incident_date.date()
    ).days

    assert 1 <= reporting_delay <= 15
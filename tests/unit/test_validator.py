from producer.validator import validate_claim


def test_valid_claim_has_no_errors():
    valid_claim = {
        "claim_id": "CLM-12345678",
        "customer_id": "CUS-12345678",
        "customer_name": "John Smith",
        "claim_type": "AUTO",
        "claim_amount": 5000,
        "country": "France",
        "incident_date": "2026-09-28",
        "created_at": "2026-09-29T07:30:00+00:00",
    }

    errors = validate_claim(valid_claim)

    assert errors == []


def test_invalid_claim_returns_expected_errors():
    invalid_claim = {
        "claim_id": "",
        "customer_id": "",
        "customer_name": "John Smith",
        "claim_type": "INVALID",
        "claim_amount": 50,
        "country": "Cameroon",
    }

    errors = validate_claim(invalid_claim)

    assert "Missing claim_id" in errors
    assert "Missing customer_id" in errors
    assert "Invalid claim_type" in errors
    assert "claim_amount outside allowed range" in errors
    assert "Invalid country" in errors


def test_invalid_dates_return_expected_errors():
    invalid_date_claim = {
        "claim_id": "CLM-BAD-DATE",
        "customer_id": "CUS-BAD-DATE",
        "customer_name": "Date Tester",
        "claim_type": "AUTO",
        "claim_amount": 5000,
        "country": "France",
        "incident_date": "not-a-date",
        "created_at": "not-a-timestamp",
    }

    errors = validate_claim(invalid_date_claim)

    assert "Invalid incident_date" in errors
    assert "Invalid created_at" in errors


def test_missing_claim_id_is_detected():
    claim_without_id = {
        "customer_id": "CUS-12345678",
        "customer_name": "Missing ID Customer",
        "claim_type": "AUTO",
        "claim_amount": 5000,
        "country": "France",
        "incident_date": "2026-09-28",
        "created_at": "2026-09-29T07:30:00+00:00",
    }

    errors = validate_claim(claim_without_id)

    assert "Missing claim_id" in errors
from producer.duplicate_checker import (
    is_duplicate,
    reset_seen_claims,
)


def test_duplicate_detection():
    reset_seen_claims()

    assert is_duplicate("CLM-001") is False
    assert is_duplicate("CLM-001") is True


def test_reset_duplicate_state():
    reset_seen_claims()

    # First occurrence should not be considered a duplicate.
    assert is_duplicate("CLM-001") is False

    # Reset should allow the same claim ID again.
    reset_seen_claims()

    assert is_duplicate("CLM-001") is False


def test_missing_claim_id_raises_error():
    reset_seen_claims()

    try:
        is_duplicate("")
    except ValueError as error:
        assert str(error) == "claim_id is required"
    else:
        raise AssertionError(
            "Expected ValueError for missing claim_id"
        )
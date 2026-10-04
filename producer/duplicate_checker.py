# ==========================================
# Duplicate detection state
# ==========================================

seen_claim_ids = set()


# ==========================================
# Duplicate detection
# ==========================================

def is_duplicate(claim_id):
    """
    Check whether a claim ID has already been processed.

    A new claim ID is added to the in-memory state.

    Returns:
        True: claim ID has already been seen.
        False: claim ID is new.
    """

    if not claim_id:
        raise ValueError("claim_id is required")

    if claim_id in seen_claim_ids:
        return True

    seen_claim_ids.add(claim_id)

    return False


# ==========================================
# State management
# ==========================================

def reset_seen_claims():
    """Clear all remembered claim IDs."""

    seen_claim_ids.clear()
from datetime import datetime

# ==========================================
# Allowed values
# ==========================================

ALLOWED_CLAIM_TYPES = {
    "AUTO",
    "HOME",
    "HEALTH",
    "TRAVEL",
}

ALLOWED_COUNTRIES = {
    "Netherlands",
    "Germany",
    "France",
    "Belgium",
    "Spain",
}

# ==========================================
# Validate one insurance claim
# ==========================================
def validate_claim(claim):
    """
        Validate an insurance claim.

        Returns:
            list: A list of validation errors.
                An empty list means the claim is valid.
    """

    errors = []

    # ---------------------------------
    # Required fields
    # ---------------------------------

    required_fields = [
        "claim_id",
        "customer_id",
        "customer_name",
        "claim_type",
        "claim_amount",
        "country",
        "incident_date",
        "created_at",
    ]

    for feild in required_fields:
        if not claim.get(feild):
            errors.append(f"Missing {feild}")

    # ------------------------------------------
    # Check claim_type
    # ------------------------------------------

    if claim.get("claim_type") not in ALLOWED_CLAIM_TYPES:
        errors.append("Invalid claim_type")

    # ------------------------------------------
    # Check claim_amount
    # ------------------------------------------

    amount = claim.get("claim_amount")

    if not isinstance(amount, (int, float)):
        errors.append("Invalid claim_amount")
    elif not 100 <= amount <= 25_000:
        errors.append("claim_amount outside allowed range")

    # ------------------------------------------
    # Check country
    # ------------------------------------------

    if claim.get("country") not in ALLOWED_COUNTRIES:
        errors.append("Invalid country")


    # ---------------------------------
    # Incident date
    # ---------------------------------

    incident_date = claim.get("incident_date")

    if incident_date:
        try:
            datetime.strptime(incident_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Invalid incident_date")


    # ---------------------------------
    # Created timestamp
    # ---------------------------------

    created_at = claim.get("created_at")

    if created_at:
        try:
            datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            )
        except ValueError:
            errors.append("Invalid created_at")

    return errors
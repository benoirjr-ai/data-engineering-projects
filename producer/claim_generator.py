import logging
import random
import uuid
from datetime import datetime, timedelta, timezone

from faker import Faker


# ==========================================
# Logging
# ==========================================

logger = logging.getLogger(__name__)


# ==========================================
# Synthetic data configuration
# ==========================================

fake = Faker()

COUNTRIES = [
    "Netherlands",
    "Germany",
    "France",
    "Belgium",
    "Spain",
]

CLAIM_TYPES = [
    "AUTO",
    "HOME",
    "HEALTH",
    "TRAVEL",
]

MIN_CLAIM_AMOUNT = 100
MAX_CLAIM_AMOUNT = 25_000

# The incident must occur 1–15 days before
# the claim is reported/created.
MIN_REPORTING_DELAY_DAYS = 1
MAX_REPORTING_DELAY_DAYS = 15

BAD_DATA_RATIO = 0.10


# ==========================================
# Customer pool
# ==========================================

# Reusing customers allows multiple claims
# to belong to the same customer.
CUSTOMERS = [
    {
        "customer_id": f"CUS-{uuid.uuid4().hex[:8].upper()}",
        "customer_name": fake.name(),
    }
    for _ in range(20)
]


# ==========================================
# Claim ID generation
# ==========================================

def generate_claim_id():
    """Generate a unique claim ID."""

    return f"CLM-{uuid.uuid4().hex[:8].upper()}"


# ==========================================
# Claim generation
# ==========================================

def generate_claim(force_bad=False, bad_data_type=None):
    """
    Generate one synthetic insurance claim.

    Args:
        force_bad:
            Guarantee that the generated claim contains
            intentionally invalid data.

        bad_data_type:
            Explicitly select the type of bad data.

            Supported values:
                - "missing_customer_name"
                - "invalid_claim_amount"

    Returns:
        dict: A synthetic insurance claim.
    """

    customer = random.choice(CUSTOMERS)

    # Generate a realistic claim creation time
    # somewhere within the recent past.
    now = datetime.now(timezone.utc)

    created_at = now - timedelta(
        minutes=random.randint(0, 60 * 24 * 30)
    )

    # Choose the incident date 1–15 days before
    # the claim was created.
    reporting_delay_days = random.randint(
        MIN_REPORTING_DELAY_DAYS,
        MAX_REPORTING_DELAY_DAYS,
    )

    incident_datetime = created_at - timedelta(
        days=reporting_delay_days
    )

    incident_date = incident_datetime.date()

    claim = {
        "claim_id": generate_claim_id(),
        "customer_id": customer["customer_id"],
        "customer_name": customer["customer_name"],
        "claim_type": random.choice(CLAIM_TYPES),
        "claim_amount": round(
            random.uniform(
                MIN_CLAIM_AMOUNT,
                MAX_CLAIM_AMOUNT,
            ),
            2,
        ),
        "country": random.choice(COUNTRIES),
        "incident_date": incident_date.isoformat(),
        "created_at": created_at.isoformat(),
    }

    # Explicitly requesting a bad-data type should
    # automatically enable bad-data generation.
    if bad_data_type is not None:
        force_bad = True

    if force_bad or random.random() < BAD_DATA_RATIO:

        if bad_data_type is None:
            bad_data_type = random.choice([
                "missing_customer_name",
                "invalid_claim_amount",
            ])

        if bad_data_type == "missing_customer_name":
            claim["customer_name"] = None

        elif bad_data_type == "invalid_claim_amount":
            claim["claim_amount"] = 50

        else:
            raise ValueError(
                f"Unsupported bad_data_type: {bad_data_type}"
            )

    return claim


# ==========================================
# Standalone execution
# ==========================================

def main():
    """Generate sample claims for manual inspection."""

    logger.info("Generating sample insurance claims...")

    for _ in range(100):
        claim = generate_claim()

        logger.info(
            "Generated claim | claim_id=%s | customer_id=%s | "
            "customer_name=%s | incident_date=%s | created_at=%s",
            claim["claim_id"],
            claim["customer_id"],
            claim["customer_name"],
            claim["incident_date"],
            claim["created_at"],
        )

    logger.info("Sample claim generation completed.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )

    main()
def clean_name(name: str) -> str:
    if not name:
        return ""
    return name.strip().title()

def clean_city(city: str) -> str:
    if not city:
        return ""
    return city.strip().title()

def clean_email(email: str) -> tuple[str | None, str | None]:
    # A missing email is allowed.
    if not email:
        return (None, None)

    # Remove surrounding whitespace and convert to lowercase.
    cleaned = email.strip().lower()

    # Basic email validation.
    # We require an @ symbol and something after it.
    if "@" not in cleaned:
        return (None, "Invalid email")

    local_part, domain = cleaned.split("@", 1)

    if not local_part or not domain:
        return (None, "Invalid email")

    # Email is valid.
    return (cleaned, None)

def parse_age(age: str) -> tuple[int | None, str | None]:
    # An empty age is invalid because age is required.
    if not age or not age.strip():
        return (None, "Invalid age")

    try:
        # Remove whitespace and convert the value to an integer.
        cleaned_age = int(age.strip())

        return (cleaned_age, None)

    except ValueError:
        # The value could not be converted to an integer.
        return (None, "Invalid age")

def get_age_group(age: int) -> str:
    if age < 18:
        return "minor"
    elif 18 <= age <= 64:
        return "adult"
    else:
        return "senior"


def transform(record: dict[str, str]) -> dict:
    """
    Transform one raw customer record.

    The function:
    1. Cleans and converts the raw values.
    2. Collects all validation errors.
    3. Calculates the customer's age group.
    4. Returns a consistent result structure.
    """

    # Store every validation error found in this record.
    # We do not stop at the first error because we want
    # to report all problems with the record.
    errors = []

    # -------------------------
    # Customer ID
    # -------------------------

    try:
        customer_id = int(record["customer_id"].strip())
    except (ValueError, AttributeError):
        customer_id = None
        errors.append("Invalid customer_id")

    # -------------------------
    # Name
    # -------------------------

    full_name = clean_name(record.get("name", ""))

    # A customer name is required.
    if not full_name:
        errors.append("Invalid name")

    # -------------------------
    # Email
    # -------------------------

    email, email_error = clean_email(record.get("email", ""))

    # Add the email error if validation failed.
    if email_error:
        errors.append(email_error)

    # -------------------------
    # City
    # -------------------------

    city = clean_city(record.get("city", ""))

    # A customer city is required.
    if not city:
        errors.append("Invalid city")

    # -------------------------
    # Age
    # -------------------------

    age, age_error = parse_age(record.get("age", ""))

    # Add the age error if validation failed.
    if age_error:
        errors.append(age_error)

    # -------------------------
    # Age group
    # -------------------------

    # We can only calculate the age group when
    # the age was successfully converted.
    if age is not None:
        age_group = get_age_group(age)
    else:
        age_group = None

    # -------------------------
    # Build transformed record
    # -------------------------

    transformed_record = {
        "customer_id": customer_id,
        "full_name": full_name,
        "email": email,
        "city": city,
        "age": age,
        "age_group": age_group,
    }

    # A record is valid only when no errors were found.
    status = "valid" if not errors else "invalid"

    # Return the standard transformation result.
    return {
        "status": status,
        "record": transformed_record,
        "errors": errors,
    }

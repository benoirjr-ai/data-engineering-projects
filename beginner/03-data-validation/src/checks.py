def check_required(value) -> bool:
    """Return True when a value is present and not blank."""
    if value is None:
        return False

    return bool(str(value).strip())


def check_integer(value) -> bool:
    """Return True when a value represents an integer."""
    if isinstance(value, (bool, float)) or value is None:
        return False

    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


def check_positive(value) -> bool:
    """Return True when a numeric value is greater than zero."""
    return value > 0


def check_unique(values) -> bool:
    """Return True when all values are unique."""
    return len(values) == len(set(values))


def check_no_digits(value) -> bool:
    """Return True when a string contains no digits."""
    if not isinstance(value, str) or not value.strip():
        return False

    return not any(char.isdigit() for char in value)


def check_email(value) -> bool:
    """Return True for a basic valid email format."""
    if not isinstance(value, str) or not value.strip():
        return False

    if "@" not in value:
        return False

    local_part, domain = value.split("@", 1)

    if not local_part or not domain:
        return False

    if "." not in domain:
        return False

    return True


def check_range(value, minimum=18, maximum=100) -> bool:
    """Return True when value falls within the inclusive range."""
    return minimum <= value <= maximum


def check_allowed_value(value, allowed_values) -> bool:
    """Return True when value exists in the allowed values."""
    return value in allowed_values
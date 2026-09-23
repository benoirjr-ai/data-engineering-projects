from src.checks import (
    check_required,
    check_integer,
    check_positive,
    check_no_digits,
    check_email,
    check_range,
    check_allowed_value,
    check_unique
)

ALLOWED_COUNTRIES = {
    "Cameroon",
    "Nigeria",
    "Ghana",
    "Kenya",
    "France",
    "Germany",
    "United Kingdom",
}

def validate_customer(customer):
    errors = {}

    customer_id = customer.get("customer_id")

    if not check_required(customer_id):
        errors["customer_id"] = ["customer ID is required"]

    elif not check_integer(customer_id):
        errors["customer_id"] = ["customer ID must be an integer"]

    elif not check_positive(int(customer_id)):
        errors["customer_id"] = ["customer ID must be positive"]


    name = customer.get("name")

    if not check_required(name):
        errors["name"] = ["customer name is required"]

    elif not check_no_digits(name):
        errors["name"] = ["customer name must not contain any digits"]


    email = customer.get("email")

    if not check_required(email):
        errors["email"] = ["Email is required"]

    elif not check_email(email):
        errors["email"] = ["Must be a valid email"]


    age = customer.get("age")

    if not check_required(age):
        errors["age"] = ["Age is required"]

    elif not check_integer(age):
        errors["age"] = ["Age must be an integer"]

    elif not check_range(int(age)):
        errors["age"] = ["Age must be in the range 18 - 100"]


    country = customer.get("country")

    if not check_required(country):
        errors["country"] = ["Country is required"]

    elif not check_allowed_value(country, ALLOWED_COUNTRIES):
        errors["country"] = ["Country is not allowed"]

    return errors


def validate_dataset(customers):
    errors = {}

    if not customers:
        errors["dataset"] = ["Dataset must contain at least one record"]
        return errors

    customer_ids = [customer.get("customer_id") for customer in customers]

    if not check_unique(customer_ids):
        errors["customer_id"] = ["Customer IDs must be unique"]

    return errors

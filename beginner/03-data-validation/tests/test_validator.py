from src.validator import validate_customer, validate_dataset


def test_valid_customer():
    customer = {
        "customer_id": "1",
        "name": "John Doe",
        "email": "john@email.com",
        "age": "28",
        "country": "Cameroon",
    }

    assert validate_customer(customer) == {}


def test_customer_with_invalid_customer_id():
    customer = {
        "customer_id": "-1",
        "name": "John Doe",
        "email": "john@email.com",
        "age": "28",
        "country": "Cameroon",
    }

    result = validate_customer(customer)

    assert "customer_id" in result
    assert result["customer_id"] == ["customer ID must be positive"]


def test_customer_with_invalid_name():
    customer = {
        "customer_id": "1",
        "name": "John123 Doe",
        "email": "john@email.com",
        "age": "28",
        "country": "Cameroon",
    }

    result = validate_customer(customer)

    assert "name" in result
    assert result["name"] == ["customer name must not contain any digits"]


def test_customer_with_invalid_email():
    customer = {
        "customer_id": "1",
        "name": "John Doe",
        "email": "invalid-email",
        "age": "28",
        "country": "Cameroon",
    }

    result = validate_customer(customer)

    assert "email" in result
    assert result["email"] == ["Must be a valid email"]


def test_customer_with_invalid_age():
    customer = {
        "customer_id": "1",
        "name": "John Doe",
        "email": "john@email.com",
        "age": "17",
        "country": "Cameroon",
    }

    result = validate_customer(customer)

    assert "age" in result
    assert result["age"] == ["Age must be in the range 18 - 100"]


def test_customer_with_invalid_country():
    customer = {
        "customer_id": "1",
        "name": "John Doe",
        "email": "john@email.com",
        "age": "28",
        "country": "Gabon",
    }

    result = validate_customer(customer)

    assert "country" in result
    assert result["country"] == ["Country is not allowed"]


def test_customer_with_multiple_errors():
    customer = {
        "customer_id": "-1",
        "name": "John123 Doe",
        "email": "invalid-email",
        "age": "17",
        "country": "Gabon",
    }

    result = validate_customer(customer)

    assert "customer_id" in result
    assert "name" in result
    assert "email" in result
    assert "age" in result
    assert "country" in result



def test_dataset_with_unique_customer_ids():
    customers = [
        {"customer_id": "1"},
        {"customer_id": "2"},
        {"customer_id": "3"},
    ]

    result = validate_dataset(customers)

    assert result == {}


def test_dataset_with_duplicate_customer_ids():
    customers = [
        {"customer_id": "1"},
        {"customer_id": "2"},
        {"customer_id": "2"},
    ]

    result = validate_dataset(customers)

    assert "customer_id" in result
    assert result["customer_id"] == ["Customer IDs must be unique"]

def test_empty_dataset():
    customers = []

    result = validate_dataset(customers)

    assert "dataset" in result
    assert result["dataset"] == ["Dataset must contain at least one record"]

def test_dataset_with_duplicate_customer_ids():
    customers = [
        {"customer_id": "1"},
        {"customer_id": "2"},
        {"customer_id": "2"},
    ]

    result = validate_dataset(customers)

    assert result == {
        "customer_id": ["Customer IDs must be unique"]
    }
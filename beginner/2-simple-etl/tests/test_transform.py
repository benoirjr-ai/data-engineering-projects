from src.transform import clean_name, clean_city, clean_email, parse_age, get_age_group, transform


def test_clean_name_spaces_and_capitalization():
    # input
    name = "  sarah johnson  "

    # run transformation
    result = clean_name(name)

    # verify expected result
    assert result == "Sarah Johnson"


def test_clean_city_variants():
    # input
    city = " Buea "

    # run transformation
    result = clean_city(city)

    # verify expected result
    assert result == "Buea"

def test_clean_email_valid():
    result, error = clean_email(" SARAH@EMAIL.COM ")

    assert result == "sarah@email.com"
    assert error is None

def test_clean_email_missing():
    result, error = clean_email("")

    assert result is None
    assert error is None

def test_clean_email_invalid():
    result, error = clean_email("INVALID")

    assert result is None
    assert error == "Invalid email"

def test_parse_age_valid():
    result, error = parse_age(" 42 ")

    assert result == 42
    assert error is None


def test_parse_age_invalid():
    result, error = parse_age("abc")

    assert result is None
    assert error == "Invalid age"


def test_parse_age_missing():
    result, error = parse_age("")

    assert result is None
    assert error == "Invalid age"

def test_get_age_group_boundaries():
    assert get_age_group(17) == "minor"
    assert get_age_group(18) == "adult"
    assert get_age_group(64) == "adult"
    assert get_age_group(65) == "senior"



def test_transform_valid_record():
    record = {
        "customer_id": "1",
        "name": "John Doe",
        "email": "JOHN@EMAIL.COM",
        "city": "Yaounde",
        "age": "28",
    }

    result = transform(record)

    assert result["status"] == "valid"
    assert result["errors"] == []

    assert result["record"] == {
        "customer_id": 1,
        "full_name": "John Doe",
        "email": "john@email.com",
        "city": "Yaounde",
        "age": 28,
        "age_group": "adult",
    }


def test_transform_missing_email():
    record = {
        "customer_id": "3",
        "name": "Peter Adams",
        "email": "",
        "city": "Yaounde",
        "age": "17",
    }

    result = transform(record)

    assert result["status"] == "valid"
    assert result["errors"] == []
    assert result["record"]["email"] is None
    assert result["record"]["age_group"] == "minor"


def test_transform_multiple_errors():
    record = {
        "customer_id": "5",
        "name": "Michael Brown",
        "email": "INVALID",
        "city": "Douala",
        "age": "abc",
    }

    result = transform(record)

    assert result["status"] == "invalid"

    assert result["errors"] == [
        "Invalid email",
        "Invalid age",
    ]

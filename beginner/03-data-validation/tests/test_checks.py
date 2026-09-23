from src.checks import (
    check_required, 
    check_integer,
    check_positive,
    check_unique,
    check_no_digits,
    check_email,
    check_range,
    check_allowed_value
)
def test_check_required():
    assert check_required("John") is True
    assert check_required(" John  ") is True
    assert check_required(25) is True

    assert check_required(None) is False
    assert check_required("") is False
    assert check_required(" ") is False

def test_check_interger():
    assert check_integer(True) is False
    assert check_integer(25.5) is False
    assert check_integer(None) is False

    assert check_integer(123) is True
    assert check_integer("123") is True
    assert check_integer("-25") is True
    assert check_integer("25.5") is False
    assert check_integer("abc") is False

def test_check_positive():
    assert check_positive(123) is True
    assert check_positive(0) is False
    assert check_positive(-123) is False

def test_check_unique():
    assert check_unique([1, 2, 3, 4]) is True
    assert check_unique([1, 2, 3, 3]) is False

def test_check_no_digits():
    assert check_no_digits("abc") is True
    assert check_no_digits(" abc ") is True
    assert check_no_digits("abc123") is False
    assert check_no_digits("John2 Doe") is False

def test_check_email():
    assert check_email("abc@email.com") is True
    assert check_email("john@test.org") is True

    assert check_email("abc") is False
    assert check_email("john@email") is False
    assert check_email(123) is False

def test_check_range():
    assert check_range(17) is False
    assert check_range(18) is True
    assert check_range(50) is True
    assert check_range(100) is True
    assert check_range(101) is False


def test_check_allowed_value():
    allowed_countries = {
        "Cameroon",
        "Nigeria",
        "Ghana",
        "Kenya",
        "France",
        "Germany",
        "United Kingdom",
    }

    assert check_allowed_value("Cameroon", allowed_countries) is True
    assert check_allowed_value("France", allowed_countries) is True
    assert check_allowed_value("Gabon", allowed_countries) is False
    assert check_allowed_value("Unknown", allowed_countries) is False

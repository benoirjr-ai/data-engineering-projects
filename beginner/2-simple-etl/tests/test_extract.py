from pathlib import Path

from src.extract import extract


def test_extract_returns_list():
    file_path = Path("data/customer.csv")

    result = extract(file_path)

    assert isinstance(result, list)

def test_extract_returns_six_records():
    file_path = Path("data/customer.csv")

    result = extract(file_path)

    assert len(result) == 6

def test_extract_preserves_raw_data():
    file_path = Path("data/customer.csv")

    result = extract(file_path)

    assert result[0]["customer_id"] == "1"
    assert result[0]["email"] == "JOHN@EMAIL.COM"
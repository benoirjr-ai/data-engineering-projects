import csv

from src.output import write_customer_summary


def test_write_customer_summary(tmp_path):
    # Arrange
    output_file = tmp_path / "customer_summary.csv"

    results = {
        "C001": {
            "transaction_count": 2,
            "total_amount": 300.00
        },
        "C002": {
            "transaction_count": 1,
            "total_amount": 50.00
        }
    }

    # Act
    write_customer_summary(output_file, results)

    # Assert
    assert output_file.exists()

    with open(output_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    assert len(rows) == 2

    assert rows[0]["customer_id"] == "C001"
    assert rows[0]["transaction_count"] == "2"
    assert rows[0]["total_amount"] == "300.0"

    assert rows[1]["customer_id"] == "C002"
    assert rows[1]["transaction_count"] == "1"
    assert rows[1]["total_amount"] == "50.0"
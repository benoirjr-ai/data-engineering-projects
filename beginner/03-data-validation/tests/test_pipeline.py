from src.pipeline import (
    load_customers,
    validate_customers,
    run_pipeline
)


def test_load_customers():
    customers = load_customers("data/customers.csv")

    assert len(customers) == 9
    assert customers[0]["customer_id"] == "1"
    assert customers[0]["name"] == "John Doe"


def test_validate_customers():
    customers = load_customers("data/customers.csv")

    results = validate_customers(customers)

    assert len(results) == 9

    valid_records = [
        result for result in results
        if result["valid"]
    ]

    invalid_records = [
        result for result in results
        if not result["valid"]
    ]

    assert len(valid_records) == 4
    assert len(invalid_records) == 5


def test_run_pipeline(tmp_path):
    report_path = tmp_path / "reports" / "quality_report.json"

    report = run_pipeline(
        "data/customers.csv",
        report_path
    )

    assert report["total_records"] == 9
    assert report["valid_records"] == 4
    assert report["invalid_records"] == 5
    assert report["status"] == "FAILED"

    assert report_path.exists()
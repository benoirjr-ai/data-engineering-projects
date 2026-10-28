import json
from src.report import generate_report, save_report


def test_report_with_valid_records():
    validation_results = [
        {
            "customer_id": "1",
            "valid": True,
            "errors": {}
        },
        {
            "customer_id": "2",
            "valid": True,
            "errors": {}
        }
    ]

    report = generate_report(validation_results, {})

    assert report["total_records"] == 2
    assert report["valid_records"] == 2
    assert report["invalid_records"] == 0
    assert report["status"] == "PASSED"
    assert report["errors"] == {}


def test_report_with_invalid_records():
    validation_results = [
        {
            "customer_id": "1",
            "valid": True,
            "errors": {}
        },
        {
            "customer_id": "2",
            "valid": False,
            "errors": {
                "email": ["Must be a valid email"]
            }
        }
    ]

    report = generate_report(validation_results, {})

    assert report["total_records"] == 2
    assert report["valid_records"] == 1
    assert report["invalid_records"] == 1
    assert report["status"] == "FAILED"
    assert report["errors"] == {
        "email": 1
    }


def test_report_counts_multiple_errors():
    validation_results = [
        {
            "customer_id": "1",
            "valid": False,
            "errors": {
                "email": ["Must be a valid email"],
                "age": ["Age must be in the range 18 - 100"]
            }
        },
        {
            "customer_id": "2",
            "valid": False,
            "errors": {
                "email": ["Must be a valid email"],
                "country": ["Country is not allowed"]
            }
        }
    ]

    dataset_errors = {
        "customer_id": ["Customer IDs must be unique"]
    }

    report = generate_report(validation_results, dataset_errors)

    assert report["total_records"] == 2
    assert report["valid_records"] == 0
    assert report["invalid_records"] == 2
    assert report["status"] == "FAILED"
    assert report["errors"] == {
        "email": 2,
        "age": 1,
        "country": 1,
        "customer_id": 1
    }

def test_save_report(tmp_path):
    validation_results = [
        {
            "customer_id": "1",
            "valid": True,
            "errors": {}
        }
    ]

    report = generate_report(validation_results, {})

    report_path = tmp_path / "reports" / "quality_report.json"

    save_report(report, report_path)

    assert report_path.exists()

    with open(report_path, encoding="utf-8") as file:
        saved_report = json.load(file)

    assert saved_report == report
import json
from pathlib import Path

def generate_report(validation_results, dataset_errors):

    total_records = len(validation_results)

    valid_records = 0
    invalid_records = 0

    for result in validation_results:
        if result["valid"]:
            valid_records += 1
        else:
            invalid_records += 1

    error_counts = {}

    for result in validation_results:
        for field in result["errors"]:
            error_counts[field] = error_counts.get(field, 0) + 1

    for field in dataset_errors:
        error_counts[field] = error_counts.get(field, 0) + 1

    if invalid_records == 0 and not dataset_errors:
        status = "PASSED"
    else:
        status = "FAILED"

    return {
        "total_records": total_records,
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "status": status,
        "errors": error_counts
    }

def save_report(report, file_path):
    file_path = Path(file_path)

    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)
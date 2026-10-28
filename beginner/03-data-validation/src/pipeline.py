import csv

from src.validator import validate_customer, validate_dataset
from src.report import generate_report, save_report

def load_customers(file_path):
    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def validate_customers(customers):
    validation_results = []

    for customer in customers:
        errors = validate_customer(customer)

        result = {
            "customer_id": customer.get("customer_id"),
            "valid": errors == {},
            "errors": errors
        }

        validation_results.append(result)

    return validation_results



def run_pipeline(file_path, report_path):
    customers = load_customers(file_path)

    validation_results = validate_customers(customers)

    dataset_errors = validate_dataset(customers)

    report = generate_report(
        validation_results,
        dataset_errors
    )

    save_report(report, report_path)

    return report


if __name__ == "__main__":
    report = run_pipeline(
        "data/customers.csv",
        "reports/quality_report.json"
    )
    print(report)
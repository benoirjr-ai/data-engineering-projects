# Data Validation Pipeline

A Python-based data validation pipeline that checks customer data against a defined quality contract and generates a JSON data-quality report.

The project demonstrates how data validation can be treated as a separate layer in a data engineering pipeline rather than silently cleaning or modifying bad data.

---

## Project Overview

Data pipelines depend on trustworthy input data.

This project receives a customer CSV file and validates it against a set of predefined rules.

The pipeline:

1. Loads customer data from CSV.
2. Validates individual customer records.
3. Performs dataset-level validation.
4. Identifies invalid records and their errors.
5. Generates a data-quality report.
6. Saves the report as JSON.

### Architecture

```text
Customer CSV
     │
     ▼
Load Raw Data
     │
     ▼
Record Validation
     │
     ├── Field-level checks
     │       ├── Required
     │       ├── Integer
     │       ├── Positive
     │       ├── Email
     │       ├── Range
     │       ├── Allowed value
     │       └── No digits
     │
     ▼
Dataset Validation
     │
     └── Duplicate customer IDs
     │
     ▼
Quality Report
     │
     ▼
quality_report.json
```

---

## Data Quality Contract

The pipeline validates the following rules.

| Field         | Rules                                        |
| ------------- | -------------------------------------------- |
| `customer_id` | Required, integer, positive, unique          |
| `name`        | Required, non-empty, must not contain digits |
| `email`       | Required, valid email format                 |
| `age`         | Required, integer, between 18 and 100        |
| `country`     | Required, must be an allowed country         |

### Allowed Countries

* Cameroon
* Nigeria
* Ghana
* Kenya
* France
* Germany
* United Kingdom

The dataset must also contain at least one record.

---

## Project Structure

```text
03-data-validation/
│
├── data/
│   ├── customers.csv
│
│
├── reports/
│   └── .gitkeep
│
├── src/
│   ├── __init__.py
│   ├── checks.py
│   ├── validator.py
│   ├── report.py
│   └── pipeline.py
│
├── tests/
│   ├── __init__.py
│   ├── test_checks.py
│   ├── test_validator.py
│   ├── test_report.py
│   └── test_pipeline.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Key Components

### `checks.py`

Contains reusable validation functions such as:

* `check_required()`
* `check_integer()`
* `check_positive()`
* `check_unique()`
* `check_no_digits()`
* `check_email()`
* `check_range()`
* `check_allowed_value()`

These functions are intentionally generic so they can be reused by different validation rules.

### `validator.py`

Applies the validation rules to individual customer records and performs dataset-level validation.

It returns structured errors instead of modifying the original data.

### `report.py`

Generates a summary of the validation results and saves the report as JSON.

Example report:

```json
{
    "total_records": 9,
    "valid_records": 4,
    "invalid_records": 5,
    "status": "FAILED",
    "errors": {
        "name": 1,
        "email": 1,
        "age": 2,
        "country": 1,
        "customer_id": 1
    }
}
```

### `pipeline.py`

Orchestrates the complete validation workflow:

```text
Load → Validate Records → Validate Dataset → Generate Report → Save Report
```

---

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Pipeline

From the project root:

```bash
python -m src.pipeline
```

The pipeline reads:

```text
data/customers.csv
```

and generates:

```text
reports/quality_report.json
```

The `reports/` directory is created automatically if it does not already exist.

---

## Running the Tests

Run the complete test suite with:

```bash
pytest
```

Current test coverage includes:

* Individual validation checks
* Customer record validation
* Dataset validation
* Report generation
* Report persistence
* CSV loading
* Customer validation pipeline
* End-to-end pipeline execution

Current result:

```text
25 passed
```

---

## Example Dataset

The project includes both valid and invalid customer records to demonstrate data-quality failures.

Examples of detected problems include:

* Duplicate customer IDs
* Names containing digits
* Invalid email addresses
* Ages outside the accepted range
* Countries outside the allowed list

The pipeline reports these problems instead of silently changing the source data.

---

## Design Principles

### 1. Validation is separate from transformation

The pipeline does not silently fix invalid records.

Instead, it identifies the problem and reports it.

### 2. Field-level and dataset-level validation are separate

Field-level validation checks individual values.

Dataset-level validation checks relationships across records, such as duplicate IDs.

### 3. Errors are structured

Validation errors are returned as dictionaries so they can easily be consumed by reporting or future data-quality systems.

### 4. The pipeline is testable

Each major component has its own unit tests, while the pipeline tests verify that the components work together.

---

## Technologies

* Python
* CSV
* JSON
* Pytest
* pathlib

---

## What I Learned

This project demonstrates the fundamentals of building a data-quality layer:

* Designing a data-quality contract
* Creating reusable validation functions
* Separating validation responsibilities
* Performing record-level validation
* Performing dataset-level validation
* Producing structured quality reports
* Writing unit tests
* Testing an end-to-end data pipeline
* Managing generated output directories with `pathlib`

---

## Future Improvements

Possible extensions for a more production-oriented version include:

* Pandera or Great Expectations
* Data-quality thresholds
* Configurable validation rules
* Logging
* CSV/JSON/Parquet input support
* Quarantine output for invalid records
* Database integration
* Airflow orchestration
* Data-quality monitoring
* Automated CI/CD tests

---

## Project Status

**Status: Complete**

The current implementation contains **25 automated tests**, all passing successfully.

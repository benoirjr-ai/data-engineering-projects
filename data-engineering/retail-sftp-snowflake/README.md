# Retail CSV-to-Snowflake Data Pipeline

## Overview

This project implements a Python-based data ingestion pipeline that validates retail sales CSV files and loads trusted records into Snowflake. It demonstrates practical data engineering concepts, including data quality validation, file fingerprinting, ingestion tracking, quarantine handling, and idempotent loading.

The project uses fictional retail transactions for testing and portfolio demonstration.

## Architecture

```text
Retail Sales CSV
       |
       v
File Discovery and Fingerprinting
       |
       v
Schema and Data Validation
       |
       +---- Invalid file/records ---> Quarantine
       |
       v
SQLite Ingestion Registry
       |
       v
Snowflake Staging Table
       |
       v
Insert-only MERGE
       |
       v
Snowflake Raw Sales Table
```

## Key Features

- **CSV validation:** Checks expected headers and validates sales records before loading.
- **Quarantine handling:** Separates invalid input for investigation instead of silently accepting it.
- **File fingerprinting:** Uses SHA-256 hashes to identify previously processed files.
- **Ingestion registry:** Tracks file-processing status using a local SQLite database.
- **Snowflake integration:** Loads validated data through a staging table before merging it into the target table.
- **Idempotency:** Skips previously processed identical files and prevents duplicate transaction inserts during normal retries.
- **Conflict detection:** Rejects conflicting transaction data instead of silently overwriting existing records.
- **Automated tests:** Includes unit tests for validation, file tracking, quarantine, fingerprinting, and ingestion behavior.

## Technology Stack

- Python
- pandas / CSV processing
- SQLite
- Snowflake
- pytest
- uv for Python dependency management

## Project Structure

```text
retail-sftp-snowflake/
├── data/
│   └── raw/
│       └── sales_2026-10-24.csv
├── src/
│   ├── file_fingerprint.py
│   ├── file_registry.py
│   ├── file_validator.py
│   ├── generate_sample.py
│   ├── ingestion.py
│   ├── quarantine.py
│   ├── run_ingestion.py
│   ├── schema.py
│   ├── snowflake_connection.py
│   ├── snowflake_loader.py
│   └── validation_models.py
├── tests/
├── main.py
├── pyproject.toml
└── README.md
```

## Sample Data

The sample dataset contains fictional retail transactions with fields such as:

- `transaction_id`
- `sale_date`
- `store_id`
- `product_id`
- `product_category`
- `quantity`
- `unit_price`
- `discount_amount`
- `sales_amount`

The expected sales calculation is:

`sales_amount = quantity × unit_price − discount_amount`

## Getting Started

### 1. Requirements

Install Python compatible with `.python-version`, `uv`, and access to a Snowflake account.

### 2. Install dependencies

From this project directory:

```bash
uv sync
```

### 3. Configure Snowflake credentials

Configure the connection using the environment variables expected by `src/snowflake_connection.py`. Keep credentials in your local environment or a properly ignored `.env` file. **Never commit passwords, private keys, or account secrets.**

### 4. Generate sample data

```bash
uv run python -m src.generate_sample
```

### 5. Run tests

```bash
uv run pytest -v
```

### 6. Run ingestion

Review the configuration and entry point in `main.py` and `src/run_ingestion.py`, then run the pipeline using the invocation configured by the project.

## Snowflake Objects

The pipeline is designed to use the following objects:

- Database: `RETAIL_DB`
- Raw schema: `RAW`
- Target table: `SALES_RAW`
- Staging table: `SALES_STAGING`
- File format: `RETAIL_CSV_FORMAT`
- Named stage: `RETAIL_LOAD_STAGE`
- Warehouse: `RETAIL_WH`

Ensure the required Snowflake objects and permissions are configured before running a live ingestion.

## Testing and Reliability

The automated test suite covers file fingerprinting, registry behavior, validation, quarantine, and ingestion workflows. Snowflake-related behavior is tested with mocks where appropriate, so passing unit tests does not by itself prove that every live Snowflake operation will succeed.

The project also includes checks for duplicate or conflicting transaction IDs and retry behavior.

## Future Improvements

- Schedule ingestion with Apache Airflow.
- Add structured logging and operational metrics.
- Add integration tests against a dedicated Snowflake test environment.
- Add CI with automated linting and test execution.
- Extend ingestion to support multiple incoming files and operational reporting.

## Disclaimer

This is an educational portfolio project using fictional sample sales data. Credentials and live infrastructure are not included in the repository.

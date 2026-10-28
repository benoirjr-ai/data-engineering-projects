# Retail SFTP-to-Snowflake Data Pipeline

## Overview

This project implements a Python-based data ingestion pipeline that downloads retail sales CSV files from an SFTP server, validates the data, and loads trusted records into Snowflake.

It demonstrates practical data engineering concepts, including secure credential configuration, file fingerprinting, data quality validation, quarantine handling, ingestion tracking, idempotent processing, and database loading.

The project uses fictional retail transactions and a locally hosted SFTP server for portfolio demonstration.

## Architecture

```text
Retail Sales CSV
       |
       v
SFTP Server (Docker)
       |
       v
SFTP Download and Local Landing
       |
       v
File Fingerprinting (SHA-256)
       |
       v
Schema and Data Validation
       |
       +---- Invalid input ---> Quarantine
       |
       v
SQLite Ingestion Registry
       |
       v
Snowflake Staging Table
       |
       v
Conflict Detection and MERGE
       |
       v
Snowflake Raw Sales Table
```

The ingestion workflow downloads a CSV file, validates it, and passes trusted data to the Snowflake loader. The registry records processing status, while the loader uses staging and transaction conflict checks to support reliable ingestion.

## Key Features

- **SFTP ingestion:** Downloads CSV files from an SFTP server using Paramiko.
- **Containerized SFTP:** Uses Docker Compose to run a local SFTP server for development and testing.
- **CSV validation:** Checks expected headers and validates sales records before loading.
- **Quarantine handling:** Separates invalid input for investigation rather than silently accepting it.
- **File fingerprinting:** Uses SHA-256 hashes to identify files by content.
- **Ingestion registry:** Tracks file-processing status in a local SQLite database.
- **Snowflake integration:** Loads validated data through a staging table before merging it into the target table.
- **Idempotency:** Skips files already marked as successfully processed and avoids duplicate transaction inserts during normal retries.
- **Conflict detection:** Rejects conflicting transaction data instead of silently overwriting existing records.
- **Automated testing:** Uses Python's `unittest` framework to test validation, file tracking, quarantine, SFTP behavior, and ingestion orchestration.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Pipeline implementation |
| Paramiko | SFTP connections and file downloads |
| Docker Compose | Local SFTP development environment |
| CSV processing | Reading and validating retail transactions |
| SQLite | Local ingestion registry |
| Snowflake | Staging and target data storage |
| `snowflake-connector-python` | Snowflake connectivity |
| `python-dotenv` | Environment-based configuration |
| `uv` | Python dependency and environment management |
| `unittest` | Automated unit testing |

## Project Structure

```text
retail-sftp-snowflake/
├── data/
│   ├── raw/                 # Local sample input, if used
│   ├── sftp/                # Local SFTP server files (ignored by Git)
│   ├── landing/             # Downloaded CSV files (ignored by Git)
│   ├── quarantine/          # Quarantined input (ignored by Git)
│   └── processed/           # Runtime artifacts (ignored by Git)
├── src/
│   ├── file_fingerprint.py
│   ├── file_registry.py
│   ├── file_validator.py
│   ├── generate_sample.py
│   ├── ingestion.py
│   ├── quarantine.py
│   ├── run_ingestion.py
│   ├── schema.py
│   ├── sftp_download.py
│   ├── snowflake_connection.py
│   ├── snowflake_loader.py
│   └── validation_models.py
├── tests/
│   ├── test_file_fingerprint.py
│   ├── test_file_registry.py
│   ├── test_file_validator.py
│   ├── test_ingestion.py
│   ├── test_quarantine.py
│   ├── test_validate_headers.py
│   ├── test_validate_row.py
│   ├── test_validation_models.py
│   ├── test_run_ingestion.py
│   └── test_sftp_download.py
├── docker-compose.yaml
├── main.py
├── pyproject.toml
├── uv.lock
└── README.md
```

Local data directories may be created at runtime. Their actual contents depend on the files generated or downloaded during execution.

## Getting Started

### 1. Prerequisites

Install and configure:

- Python version compatible with `.python-version` and `pyproject.toml`
- `uv`
- Docker Desktop with Docker Compose
- Access to a Snowflake account with the required database objects and permissions

### 2. Install dependencies

From the project directory:

```powershell
uv sync
```

This installs the project dependencies and synchronizes the environment with `uv.lock`.

### 3. Configure SFTP credentials

Set the password in your current PowerShell session:

```powershell
$env:SFTP_PASSWORD = "your-local-development-password"
```

Use the password configured for your local SFTP service. The example above is a placeholder; do not use it as a real credential.

The Compose configuration reads the password from the environment rather than storing it directly in the configuration file.

### 4. Start the local SFTP server

From the project directory, validate the configuration:

```powershell
docker compose config -q
```

Then start the service:

```powershell
docker compose up -d
```

The server is configured to listen on `127.0.0.1:2222` on the host.

The local `data/sftp/` directory is mounted into the SFTP container's upload directory. Place the intended CSV file there so the downloader can retrieve it.

Check the service status:

```powershell
docker compose ps
```

### 5. Configure Snowflake

Configure the Snowflake connection using the environment variables expected by `src/snowflake_connection.py`.

Keep credentials in your local environment or an appropriately ignored `.env` file. Never commit passwords, private keys, account secrets, or other sensitive configuration.

The pipeline expects the required Snowflake objects to exist before live ingestion.

### 6. Generate sample data

If you need to regenerate the project's sample data, run:

```powershell
uv run python -m src.generate_sample
```

Review the generator's output path before uploading or downloading the resulting CSV.

### 7. Run automated tests

Run the complete unit test suite:

```powershell
uv run python -m unittest discover -s tests -v
```

The tests cover core ingestion logic and use mocks where appropriate to test SFTP and pipeline orchestration without requiring a live transfer or Snowflake load for every test.

Passing unit tests does not, by itself, prove that a live Snowflake ingestion will succeed.

### 8. Run the ingestion workflow

The current runner downloads the configured file, `sales_2026-10-24.csv`, from SFTP before invoking the validation and Snowflake loading workflow.

Run:

```powershell
uv run python -m src.run_ingestion
```

Review the reported status, row count, and file hash.

The runner requires a reachable SFTP server, the `SFTP_PASSWORD` environment variable, a compatible input CSV, and correctly configured Snowflake access.

## Snowflake Objects

The pipeline is designed to use the following objects:

| Object | Name |
|---|---|
| Database | `RETAIL_DB` |
| Raw schema | `RAW` |
| Target table | `SALES_RAW` |
| Staging table | `SALES_STAGING` |
| File format | `RETAIL_CSV_FORMAT` |
| Named stage | `RETAIL_LOAD_STAGE` |
| Warehouse | `RETAIL_WH` |

Create the required objects and grant the necessary permissions before running a live ingestion. Exact setup requirements depend on the Snowflake account and role being used.

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

```text
sales_amount = quantity × unit_price − discount_amount
```

The CSV headers and validation rules must match the schema expected by the pipeline.

## Testing and Reliability

The project separates file acquisition, validation, tracking, and loading into distinct components.

- SHA-256 fingerprints help identify files with identical contents.
- The SQLite registry tracks ingestion status and supports retry behavior.
- Invalid input can be quarantined for investigation.
- Snowflake staging isolates the incoming data before it reaches the target table.
- Transaction conflict detection helps prevent inconsistent records from being silently accepted.
- Unit tests exercise individual components and important failure scenarios.

The registry is local to the running environment. For a production deployment with multiple workers, a shared registry or centralized orchestration mechanism would be preferable.

## Security Considerations

- Credentials are supplied through environment variables rather than committed to source control.
- The local SFTP service binds to loopback, making it intended for local development rather than public deployment.
- Local input, landing files, and registry artifacts should remain outside version control unless a sanitized sample is deliberately selected for publication.
- A production SFTP deployment should use managed credentials, verified host keys, appropriate access restrictions, and secure secret storage.
- Production Snowflake access should follow least-privilege principles.

## Future Improvements

- Replace the fixed filename with configurable file discovery.
- Add structured logging and operational metrics.
- Add integration tests against a dedicated Snowflake test environment.
- Add CI with automated testing and linting.
- Add scheduling with Apache Airflow.
- Support multiple incoming files and more comprehensive operational reporting.
- Introduce centralized state management for deployments with multiple workers.

## Disclaimer

This is an educational data engineering portfolio project using fictional sample sales data. Live infrastructure, account credentials, and production secrets are not included in the repository.

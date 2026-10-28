# Incremental Data Pipeline

A Python-based incremental ETL pipeline that processes only new transaction records using a persistent watermark, transforms the data, loads it into PostgreSQL, and provides automated tests and logging.

## Project Goal

This project demonstrates how an ETL pipeline can avoid reprocessing data that has already been loaded.

Instead of processing the entire dataset on every run, the pipeline stores the ID of the last successfully processed transaction and uses it as a watermark.

## Architecture

```text
CSV Source
    ↓
Extract New Records
    ↓
Watermark Check
    ↓
Transform
    ↓
PostgreSQL
    ↓
Update Watermark
```

## Features

* Incremental data extraction
* Persistent watermark state
* Data transformation
* PostgreSQL loading
* Duplicate protection with `ON CONFLICT`
* Failure-safe watermark updates
* Structured logging
* Automated tests with pytest
* Dockerized PostgreSQL database

## Project Structure

```text
05-incremental-pipeline/
├── data/
│   └── transactions.csv
├── src/
│   ├── __init__.py
│   ├── database.py
│   ├── extract.py
│   ├── load.py
│   ├── logging_config.py
│   ├── pipeline.py
│   ├── state.py
│   └── transform.py
├── state/
│   └── .gitkeep
├── tests/
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_extract.py
│   ├── test_load.py
│   ├── test_logging_config.py
│   ├── test_pipeline.py
│   ├── test_state.py
│   └── test_transform.py
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## How Incremental Processing Works

The pipeline stores the last successfully processed transaction ID in:

```text
state/watermark.txt
```

For example:

```text
1005
```

When the pipeline runs, transactions with IDs less than or equal to `1005` are skipped.

A new transaction:

```text
1006
```

is processed and, after a successful database load, the watermark becomes:

```text
1006
```

If the database load fails, the watermark is not updated.

## Example

Initial state:

```text
Watermark: 1005
```

New transaction:

```text
1006
```

Pipeline:

```text
1001 → skipped
1002 → skipped
1003 → skipped
1004 → skipped
1005 → skipped
1006 → processed
```

After successful processing:

```text
Watermark: 1006
```

Running the pipeline again without new data results in:

```text
New transactions found: 0
No new transactions to process
```

## Database

PostgreSQL runs locally through Docker Compose.

Database configuration:

```text
Database: incremental_db
User: incremental_user
Host: localhost
Port: 5433
```

The PostgreSQL container internally listens on port `5432`, which is mapped to host port `5433`.

## Running the Project

### 1. Start PostgreSQL

```powershell
docker compose up -d
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Run the tests

```powershell
pytest -v
```

Expected:

```text
11 passed
```

### 4. Run the pipeline

```powershell
python src/pipeline.py
```

Example output:

```text
INFO - Watermark loaded: 1006
INFO - New transactions found: 0
INFO - No new transactions to process
Pipeline completed. Watermark: 1006
```

## Testing Incremental Processing

To simulate new data, add a new transaction to:

```text
data/transactions.csv
```

For example:

```csv
1007,C001,2026-09-06,150.00,completed
```

Then run:

```powershell
python src/pipeline.py
```

The pipeline should process only transaction `1007` and update the watermark.

## Tests

The project tests:

* CSV extraction
* Incremental extraction
* Data transformation
* Watermark saving/loading
* Missing watermark behavior
* Database connection and table creation
* Transaction loading
* Duplicate protection
* Pipeline execution
* Incremental reprocessing prevention
* Watermark safety when loading fails
* Logging configuration

## Technologies

* Python
* PostgreSQL
* Docker
* pytest
* psycopg2

## Key Data Engineering Concepts

This project demonstrates:

* Incremental ETL
* Watermarking
* State management
* Idempotency
* Deduplication
* Data transformation
* Database loading
* Failure handling
* Logging
* Automated testing

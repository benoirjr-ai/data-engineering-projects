# Simple ETL Pipeline

A beginner-friendly ETL (Extract, Transform, Load) pipeline built with Python and PostgreSQL.

The project demonstrates the fundamental structure of a data pipeline:

```text
CSV File
   │
   ▼
Extract
   │
   ▼
Raw Records
   │
   ▼
Transform & Validate
   │
   ├───────────────┐
   ▼               ▼
Valid           Invalid
   │               │
   ▼               ▼
PostgreSQL     Quarantine
   │
   ▼
Customers Table
```

The goal is to understand how the three major stages of an ETL pipeline can be separated into independent, testable components before moving on to more complex technologies such as Airflow, Spark, Kafka, dbt, and cloud platforms.

---

## Project Overview

The pipeline reads customer records from a CSV file, cleans and validates the data, and loads valid records into PostgreSQL.

Records that fail validation are not discarded. Instead, the original record and its validation errors are stored in a quarantine table for later investigation.

### Pipeline stages

1. **Extract**

   * Read customer records from a CSV file.
   * Preserve the original values.
   * Return records as Python dictionaries.

2. **Transform**

   * Clean names and cities.
   * Normalize email addresses.
   * Parse customer IDs and ages.
   * Assign an age group.
   * Validate required fields.
   * Collect validation errors.

3. **Load**

   * Load valid customers into PostgreSQL.
   * Update existing customers using an UPSERT.
   * Store invalid records in a quarantine table.

---

## Technologies

* Python 3.13
* PostgreSQL 15
* Docker & Docker Compose
* psycopg
* python-dotenv
* pytest
* CSV
* SQL

---

## Project Structure

```text
simple-etl/
│
├── data/
│   └── customer.csv
│
├── src/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── pipeline.py
│
├── tests/
│   ├── __init__.py
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_load.py
│
├── sql/
│   └── schema.sql
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Source Data

The pipeline uses a small customer CSV file:

```text
customer_id,name,email,city,age
1,John Doe,JOHN@EMAIL.COM,Yaounde,28
2,Mary Smith,mary@email.com,Douala,34
3,Peter Adams,,Yaounde,17
4,  sarah johnson  ,SARAH@EMAIL.COM, Buea ,42
5,Michael Brown,INVALID,Douala,abc
6,David Wilson,david@email.com,Yaounde,67
```

The dataset intentionally contains both valid and invalid records so that the pipeline can demonstrate validation and quarantine behavior.

---

## Transformations

The transformation stage performs the following operations.

### Name cleaning

Names are stripped of unnecessary whitespace and normalized using title case.

```text
"  sarah johnson  "
        ↓
"Sarah Johnson"
```

### City cleaning

City values are stripped and normalized.

```text
" Buea "
    ↓
"Buea"
```

### Email normalization

Emails are converted to lowercase.

```text
"JOHN@EMAIL.COM"
        ↓
"john@email.com"
```

Missing email addresses are allowed.

Invalid email values are flagged.

### Age parsing

Age values from the CSV are converted from strings to integers.

```text
"42" → 42
```

Invalid values such as:

```text
"abc"
```

are rejected.

### Age groups

Customers are assigned an age group:

| Age      | Group    |
| -------- | -------- |
| Under 18 | `minor`  |
| 18–64    | `adult`  |
| 65+      | `senior` |

---

## Data Validation

The transformation stage collects all validation errors for a record instead of stopping at the first error.

For example:

```text
Customer 5

Email: INVALID
Age: abc
```

Produces:

```text
[
    "Invalid email",
    "Invalid age"
]
```

The record is then classified as:

```text
status = "invalid"
```

---

## Quarantine

Invalid records are stored in the PostgreSQL `customer_quarantine` table.

The quarantine table preserves:

* The customer ID
* The original raw record
* The validation errors
* The time the record was quarantined

Example:

```text
customer_id: 5

raw_record:
{
    "customer_id": "5",
    "name": "Michael Brown",
    "email": "INVALID",
    "city": "Douala",
    "age": "abc"
}

errors:
[
    "Invalid email",
    "Invalid age"
]
```

Keeping the original record makes it possible to investigate the failure without losing the source data.

---

## PostgreSQL Schema

The project uses two tables.

### `customers`

Stores successfully validated and transformed customer records.

```text
customer_id
full_name
email
city
age
age_group
```

### `customer_quarantine`

Stores records that fail validation.

```text
quarantine_id
customer_id
raw_record
errors
created_at
```

The customer table uses `customer_id` as its primary key.

---

## UPSERT Behavior

If a customer already exists, the pipeline updates the existing record instead of creating a duplicate.

The load operation uses PostgreSQL:

```sql
ON CONFLICT (customer_id) DO UPDATE
```

This makes the customer load suitable for repeated pipeline executions.

---

## Error Handling

The pipeline separates valid and invalid records.

```text
Valid record
    ↓
customers table

Invalid record
    ↓
customer_quarantine table
```

A failure in one record does not prevent the remaining records from being processed.

---

## Running the Project

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd simple-etl
```

### 2. Create the environment file

Copy `.env.example` to `.env`.

On PowerShell:

```powershell
Copy-Item .env.example .env
```

Update the values if necessary.

> `.env` contains local configuration and should not be committed to Git.

---

### 3. Install Python dependencies

Create and activate a virtual environment if you are using one.

Then:

```bash
pip install -r requirements.txt
```

---

### 4. Start PostgreSQL

```bash
docker compose up -d
```

Check that the container is running:

```bash
docker ps
```

---

### 5. Create the database tables

Run:

```powershell
Get-Content .\sql\schema.sql | docker exec -i postgres_db psql -U postgres -d simple_etl
```

---

### 6. Run the tests

From the project root:

```bash
python -m pytest
```

---

### 7. Run the ETL pipeline

From the project root:

```bash
python -m src.pipeline
```

Expected result:

```text
Extracted 6 records.

Pipeline completed.
Valid records loaded: 5
Invalid records quarantined: 1
```

---

## Verifying the Data

You can connect to PostgreSQL using `psql`, pgAdmin, or another PostgreSQL client.

To view valid customers:

```sql
SELECT *
FROM customers
ORDER BY customer_id;
```

To view quarantined records:

```sql
SELECT *
FROM customer_quarantine
ORDER BY quarantine_id;
```

---

## Testing

The project includes tests for:

* CSV extraction
* Number of extracted records
* Preservation of raw data
* Name cleaning
* City cleaning
* Email validation
* Age parsing
* Age-group assignment
* Transformation validation
* Customer loading
* Customer UPSERT behavior
* Quarantine loading

Run all tests with:

```bash
python -m pytest
```

---

## Design Decisions

### Why return dictionaries from Extract?

The extract stage returns:

```python
list[dict[str, str]]
```

This provides a simple record structure that can be passed from extraction to transformation without coupling the stages to PostgreSQL.

### Why quarantine invalid records?

Invalid records should not simply disappear.

Quarantine provides a place to store failed records and their validation errors so they can be investigated or corrected later.

### Why use PostgreSQL?

PostgreSQL provides a realistic relational destination while keeping the project simple enough to run locally.

### Why Docker?

Docker makes the PostgreSQL environment reproducible without requiring PostgreSQL to be installed directly on the host machine.

---

## Future Improvements

This project intentionally keeps the architecture simple. Possible improvements include:

* Add structured logging
* Add pipeline run IDs
* Add record-level load error handling
* Add more robust email validation
* Add data-quality metrics
* Add configuration management
* Add integration tests
* Add CI/CD with GitHub Actions
* Orchestrate the pipeline with Apache Airflow
* Move the data source to cloud object storage
* Introduce dbt for transformations
* Introduce Spark for larger datasets

These improvements will be explored in later projects rather than adding unnecessary complexity to this beginner implementation.

---

## Learning Objective

The main objective of this project is to understand the fundamental ETL pattern:

```text
Extract → Transform → Load
```

and, more importantly, to understand how each stage can be isolated, tested, and changed independently.

This project serves as the foundation for more advanced data-engineering systems involving orchestration, distributed processing, streaming, data quality, and cloud infrastructure.

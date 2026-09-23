# Batch Processing Pipeline

## Overview

This project implements a batch-processing data pipeline using Python.

The pipeline reads transaction data from a CSV file in configurable batches, filters and transforms the data, aggregates transactions by customer, and writes the final customer summary to a CSV file.

The project demonstrates fundamental batch-processing concepts used in data engineering, including memory-efficient data ingestion, transformation, aggregation, automated testing, and output generation.

---

## Objectives

The main objectives of this project are to:

* Learn how batch processing works.
* Process data incrementally instead of loading an entire dataset into memory.
* Build a modular ETL pipeline.
* Filter and transform raw transaction data.
* Aggregate transaction data by customer.
* Combine results from multiple batches.
* Write processed results to a CSV file.
* Build automated tests for individual pipeline components.
* Practice clean separation of responsibilities between modules.

---

## Architecture

```text
                  transactions.csv
                         |
                         v
                  +--------------+
                  |    Extract   |
                  | Batch Reader |
                  +--------------+
                         |
                         v
                  +--------------+
                  |  Transform   |
                  | Filter/Cast  |
                  +--------------+
                         |
                         v
                  +--------------+
                  |   Aggregate  |
                  | Per Batch    |
                  +--------------+
                         |
                         v
                  +--------------+
                  | Cross-Batch  |
                  |    Merge     |
                  +--------------+
                         |
                         v
                  +--------------+
                  |    Output    |
                  | Customer CSV |
                  +--------------+
                         |
                         v
                customer_summary.csv
```

---

## Project Structure

```text
04-batch-processing/
│
├── data/
│   └── transactions.csv
│
├── output/
│   └── .gitkeep
│
├── src/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   ├── aggregate.py
│   ├── output.py
│   └── pipeline.py
│
├── tests/
│   ├── __init__.py
│   ├── test_extract.py
│   ├── test_transform.py
│   ├── test_aggregate.py
│   ├── test_output.py
│   └── test_pipeline.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Dataset

The project uses a sample transaction dataset stored in:

```text
data/transactions.csv
```

The dataset contains the following fields:

| Column             | Description                   |
| ------------------ | ----------------------------- |
| `transaction_id`   | Unique transaction identifier |
| `customer_id`      | Customer identifier           |
| `transaction_date` | Date of the transaction       |
| `amount`           | Transaction amount            |
| `category`         | Transaction category          |
| `status`           | Transaction status            |

Example:

```csv
transaction_id,customer_id,transaction_date,amount,category,status
1001,C001,2026-09-01,125.50,Electronics,completed
1002,C002,2026-09-01,75.00,Grocery,completed
1003,C001,2026-09-01,250.00,Electronics,completed
1004,C003,2026-09-01,50.00,Clothing,cancelled
```

Only transactions with:

```text
status = completed
```

are included in the final revenue calculations.

---

# Pipeline Components

## 1. Extract

The extraction stage is implemented in:

```text
src/extract.py
```

The `read_batches()` function reads the CSV file and yields records in configurable batches.

```python
read_batches(file_path, batch_size)
```

For example:

```python
read_batches(
    "data/transactions.csv",
    batch_size=3
)
```

The pipeline processes three records at a time instead of loading the entire file into memory.

### Why use `yield`?

The extractor uses a Python generator:

```python
yield batch
```

This allows the pipeline to produce one batch at a time.

Instead of:

```text
Entire dataset
      ↓
Load everything into memory
```

the pipeline processes:

```text
Dataset
   |
   +--> Batch 1
   |
   +--> Batch 2
   |
   +--> Batch 3
   |
   +--> Batch 4
```

This pattern becomes increasingly important as dataset size grows.

---

## 2. Transform

The transformation stage is implemented in:

```text
src/transform.py
```

The `transform_batch()` function processes each batch.

The transformation performs three main operations.

### Filter cancelled transactions

Only completed transactions are retained.

```python
if transformed_row["status"] != "completed":
    continue
```

### Convert transaction ID

The CSV initially provides values as strings.

For example:

```text
"1001"
```

The pipeline converts this into:

```python
1001
```

### Convert amount

The transaction amount is also converted from a string:

```text
"125.50"
```

into a numeric value:

```python
125.50
```

This allows the pipeline to perform numerical calculations correctly.

---

## 3. Aggregate

The aggregation stage is implemented in:

```text
src/aggregate.py
```

The `aggregate_batch()` function groups transactions by customer.

For every customer, the pipeline calculates:

* Number of completed transactions
* Total completed transaction amount

Example:

```python
{
    "C001": {
        "transaction_count": 2,
        "total_amount": 350.50
    }
}
```

The aggregation is performed independently for each batch.

---

## 4. Cross-Batch Aggregation

A customer can appear in multiple batches.

For example:

```text
Batch 1
C001 → $100

Batch 2
C001 → $200

Batch 3
C001 → $150
```

The pipeline must combine these results.

This logic is implemented in:

```text
src/pipeline.py
```

The pipeline maintains a global aggregation dictionary and merges the results from each batch.

This produces the final customer-level summary.

---

## 5. Output

The output stage is implemented in:

```text
src/output.py
```

The `write_customer_summary()` function writes the final aggregation to:

```text
output/customer_summary.csv
```

The generated file contains:

```text
customer_id,transaction_count,total_amount
```

Example:

```csv
customer_id,transaction_count,total_amount
C001,4,610.5
C002,2,195.0
C003,1,45.0
C004,2,800.0
C005,1,90.0
```

The output directory is automatically created if it does not already exist.

---

# Batch Processing

The pipeline supports configurable batch sizes.

For the 12-record dataset, a batch size of `3` produces:

```text
Batch 1 → 3 records
Batch 2 → 3 records
Batch 3 → 3 records
Batch 4 → 3 records
```

A batch size of `5` produces:

```text
Batch 1 → 5 records
Batch 2 → 5 records
Batch 3 → 2 records
```

The extractor correctly handles an incomplete final batch.

This makes the pipeline independent of whether the total number of records is evenly divisible by the batch size.

---

# Example Results

After processing the provided dataset, the pipeline produces the following customer-level summary:

| Customer | Completed Transactions | Total Amount |
| -------- | ---------------------: | -----------: |
| C001     |                      4 |       610.50 |
| C002     |                      2 |       195.00 |
| C003     |                      1 |        45.00 |
| C004     |                      2 |       800.00 |
| C005     |                      1 |        90.00 |

### Important business rule

Cancelled transactions are not included.

For example, customer `C002` has three transactions in the source dataset:

```text
75.00   completed
120.00  completed
60.00   cancelled
```

The pipeline therefore produces:

```text
Transaction count = 2
Total amount      = 195.00
```

---

# Installation

## Requirements

The project requires:

* Python 3
* pip
* pytest

## Create a Virtual Environment

From the project directory:

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```cmd
.venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Pipeline

From the project directory:

```text
beginner/04-batch-processing
```

run:

```bash
python -m src.pipeline
```

The pipeline will:

1. Read `data/transactions.csv`
2. Process the file in batches
3. Filter cancelled transactions
4. Convert data types
5. Aggregate transactions by customer
6. Merge results across batches
7. Generate the final customer summary

The output will be written to:

```text
output/customer_summary.csv
```

The terminal will display:

```text
Pipeline completed successfully.
Output written to output/customer_summary.csv
```

---

# Testing

The project uses `pytest` for automated testing.

Run the complete test suite:

```bash
pytest -v
```

The tests cover:

### Extraction

* Reading CSV data in batches
* Correct batch sizes
* Incomplete final batches

### Transformation

* Completed transaction filtering
* Cancelled transaction removal
* Transaction ID conversion
* Amount conversion

### Aggregation

* Aggregating multiple transactions for the same customer
* Aggregating multiple customers

### Pipeline

* End-to-end pipeline aggregation
* Cross-batch aggregation
* Exclusion of cancelled transactions

### Output

* Output file creation
* Correct CSV structure
* Correct customer data

Expected result:

```text
10 passed
```

---

# Design Principles

## Separation of Concerns

Each component of the pipeline has a specific responsibility.

```text
extract.py
    ↓
Data ingestion

transform.py
    ↓
Data transformation

aggregate.py
    ↓
Batch aggregation

pipeline.py
    ↓
Pipeline orchestration

output.py
    ↓
Output generation
```

This makes the project easier to understand, test, maintain, and extend.

---

## Configurable Batch Size

The batch size is controlled by the caller:

```python
run_pipeline(
    "data/transactions.csv",
    batch_size=3
)
```

The batch size is therefore not hard-coded into the extraction logic.

This allows the same pipeline to be used with different processing requirements.

---

## Memory-Efficient Processing

The extractor uses a generator to process batches incrementally.

The pipeline does not need to load the entire dataset into memory before processing begins.

This design provides a foundation for processing datasets that are significantly larger than the sample dataset used in this project.

---

## Automated Testing

Each major component has its own tests.

```text
extract.py
     ↓
test_extract.py

transform.py
     ↓
test_transform.py

aggregate.py
     ↓
test_aggregate.py

output.py
     ↓
test_output.py

pipeline.py
     ↓
test_pipeline.py
```

This makes it possible to identify problems at the component level before relying on the complete pipeline.

---

# Key Data Engineering Concepts

This project demonstrates the following data engineering concepts:

* Batch processing
* ETL pipeline design
* Generator-based ingestion
* Memory-efficient processing
* Data filtering
* Data type conversion
* Aggregation
* Cross-batch state management
* Separation of concerns
* Automated testing
* File-based data pipelines
* Configurable processing
* Business-rule implementation

---

# What I Learned

Through this project, I learned how to design a batch-processing pipeline that processes data incrementally rather than loading the entire dataset into memory.

I learned how Python generators and the `yield` keyword can be used to create memory-efficient data extraction processes.

I also learned how transformation and aggregation can be performed independently for each batch and then combined into a final result.

Another important lesson was cross-batch state management. A customer can appear in multiple batches, so the pipeline must maintain global aggregation results while processing each batch.

The project also reinforced the importance of automated testing and separation of responsibilities between pipeline components.

---

# Challenges Solved

## Processing Data in Batches

Instead of reading the entire dataset at once, the pipeline processes configurable batches.

This provides a foundation for working with larger datasets.

## Combining Results Across Batches

The same customer can appear in different batches.

The pipeline therefore merges individual batch results into a global customer summary.

## Filtering Business Data

Cancelled transactions are removed before aggregation so that they do not contribute to revenue totals.

## Preserving Raw Data

The transformation stage copies each row before modifying values.

This prevents the original raw input from being modified during transformation.

---

# Future Improvements

Possible improvements for future versions include:

* Add data-quality validation.
* Add structured logging.
* Add configuration files.
* Support multiple input files.
* Support JSON input.
* Write results to PostgreSQL.
* Add database-based extraction.
* Schedule the pipeline with Apache Airflow.
* Store raw data in Amazon S3.
* Add incremental processing.
* Add checkpointing.
* Add error handling.
* Add failed-record quarantine.
* Add pipeline monitoring.
* Add processing metrics.
* Containerize the pipeline with Docker.
* Add CI/CD with GitHub Actions.
* Replace local CSV processing with distributed processing using Apache Spark for larger datasets.

---

# Technologies

* Python
* CSV
* pytest
* Git
* PowerShell

---

# Project Status

**Status: Complete**

The batch-processing pipeline successfully:

* Extracts transaction data incrementally.
* Processes configurable batch sizes.
* Filters cancelled transactions.
* Converts raw CSV values into appropriate data types.
* Aggregates transactions by customer.
* Combines results across multiple batches.
* Generates a customer summary CSV.
* Automatically creates the output directory.
* Includes automated tests for the pipeline components.

The project provides a foundation for progressing toward more advanced data-engineering systems involving databases, orchestration, cloud storage, distributed processing, and production monitoring.

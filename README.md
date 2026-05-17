# 🚀 Beginner CSV to Database Loader

A clean, beginner-friendly ETL (Extract, Transform, Load) pipeline built with Python. This project demonstrates how to read data from a local CSV file, automatically discover its structure, and safely load it into a local SQLite database. 

It is designed to showcase core data engineering fundamentals like **memory efficiency**, **schema validation**, and **error recovery** without needing complex cloud infrastructure.

---

## ✨ Key Features

- **Auto-Schema Discovery**: Automatically scans the CSV headers and data to determine the correct database column types (Integer, Float, DateTime, or String).
- **Schema Validation**: Checks the CSV layout against your database before running to make sure everything matches and won't crash halfway through.
- **Memory-Efficient Chunking**: Streams data in manageable chunks (2,000 rows at a time). This keeps your computer's memory usage low, even if you feed it a large file.
- **Resilient Ingestion (Fallback)**: If a high-speed bulk insert fails because of a corrupt row (e.g., text inside a number column), the pipeline automatically switches to row-by-row mode for that chunk. It saves the good rows and logs the "poison" row safely.
- **Graceful Shutdown**: If you press `Ctrl+C` to stop the script, the pipeline finishes processing its current chunk and safely closes the database connection first to prevent database corruption.

---

## 🛠️ Architecture

The project is split into small, dedicated files using an **Orchestrator Pattern** to keep the code organized and readable:

- **`main.py`**: The entry point. Handles your terminal commands.
- **`beginner/core/pipeline.py`**: The Coordinator. Controls the step-by-step flow of the ETL process and catches stop signals.
- **`beginner/core/discovery.py`**: The Brain. Inspects the CSV and handles data types and validations.
- **`beginner/core/database.py`**: The Worker. Handles connecting to SQLite, bulk loading, and error recovery.

---

## 📋 Prerequisites

You only need Python and a couple of standard data libraries installed:
- Python 3.8+
- Pandas
- SQLAlchemy

---

## 🔧 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/benoirjr-ai/data-engineering-projects.git](https://github.com/benoirjr-ai/data-engineering-projects.git)
   cd data-engineering-projects

---
### 2. Install the required libraries:

 pip install -r requirements.txt

 --- 
 ## 💻 Usage

Run the pipeline from your terminal by pointing it to your CSV file and giving your target database table a name:

```bash
python main.py --file data/your_data.csv --table target_table_name

```

### Supported Arguments:
* `--file`: (Required) Path to your local source CSV file.

* `--table`: (Required) The name of the table you want to create or append to inside the database.

* `--db`: (Optional) Custom database connection string. Defaults automatically to a local file called sqlite:///generic_loader.db.
---
### 📁 Project Structure
```
├── beginner/
│   ├── __init__.py
│   └── core/
│       ├── __init__.py
│       ├── database.py    # Local SQLite Connections & Bulk Loading
│       ├── discovery.py   # Type Detection & Pre-flight Schema Checks
│       ├── new_parser.py  # Custom CSV Stream Handlers
│       └── pipeline.py    # Main ETL Orchestration Logic
├── data/                  # Local folder for your CSV files (Ignored by Git)
├── main.py                # Terminal CLI Entry Point
├── failed_rows.log        # Automatically generated on errors (holds bad rows)
├── requirements.txt       # Python dependencies list
└── README.md              # Project documentation
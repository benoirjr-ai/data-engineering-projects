import os
import csv
import logging
from datetime import datetime


def setup_logger():
    """Set up a dual_logging system to ouput to both the console and a file."""
    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger("fifa_etl_pipeline")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if logger is initialized multiple times
    if not logger.handlers:
        # create handlers
        c_handler = logging.StreamHandler() # Console
        f_handler = logging.FileHandler(os.path.join(log_dir, "pipeline.log"), encoding="utf-8") # File

        # Create formatters and add to handlers
        format_str = logging.Formatter('%(asctime)s -%(levelname)s -%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        c_handler.setFormatter(format_str)
        f_handler.setFormatter(format_str)

        # Add handler To the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

    return logger

def log_pipeline_metrics(total_rows: int, total_cols: int, duration_seconds: float, status: str):
    """
    Appends execution run metrics to a historical tracking CSV 
    for monitoring pipeline throughput and performance trends.
    """
    metrics_file = "./logs/pipeline_metrics.csv"
    file_exists = os.path.exists(metrics_file)

    # Calculate Velocity: Rows processed per second
    rows_per_second = round(total_rows / duration_seconds, 2) if duration_seconds > 0 else 0

    row_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M%S"),
        "status": status,
        "total_columns": total_cols,
        "total_rows": total_rows,
        "duration_seconds": round(duration_seconds, 3),
        "rows_per_second": rows_per_second
    }

    try: 
        with open(metrics_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=row_data.keys())
            if not file_exists:
                writer.writeheader() # Create a header row if it's the first run
            writer.writerow(row_data)
    except Exception as e:
        # We don't want a failure in monitoring to crash the primary ETL data load
        print(f"⚠️ Monitoring warning: Could not write pipeline metrics: {e}")
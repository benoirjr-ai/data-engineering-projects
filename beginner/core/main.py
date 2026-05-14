import sys
import logging
import argparse
from beginner.core.pipeline import PipelineManager

# Setup global logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s' 
)

if __name__ == "__main__":
    # 1. Added argparse so you can pass arguments from the terminal
    parser = argparse.ArgumentParser(description="Generic CSV to DB Loader")
    parser.add_argument("--file", required=True, help="Path to the CSV file")
    parser.add_argument("--table", required=True, help="Target table name")
    parser.add_argument("--db", default="sqlite:///generic_loader.db", help="Optional custom database URL")
    args = parser.parse_args()

    # 2. Instantiate the pipeline manager lifecycle wrapper
    manager = PipelineManager(csv_file=args.file, table_name=args.table, db_url=args.db)

    try:
        # 3. Fire the sequence trigger
        manager.run()

    except Exception as critical_err:
        # Catch any structural exception that managed to slip past internal handlers
        logging.critical(f"FATAL PIPELINE CRASH: {critical_err}")
        
        # Emergency cleanup fallback check
        try:
            manager.close()
        except Exception:
            pass
            
        sys.exit(1) # Error status exit code
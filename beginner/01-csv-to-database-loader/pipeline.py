import os
import sys
import signal
import logging
import pandas as pd
from beginner.core.discovery import discover_schema, validate_schema
from beginner.core.database import DBClient
from beginner.core.new_parser import get_csv_reader

class PipelineManager:
    def __init__(self, csv_file, table_name, db_url="sqlite:///generic_loader.db"):
        self.csv_file = csv_file
        self.table_name = table_name
        self.db = DBClient(db_url)
        
        # Track manual interrupt signals
        self.shutdown_requested = False
        signal.signal(signal.SIGINT, self._handle_interrupt)

    def _handle_interrupt(self, sig, frame):
        """Interceptors OS interrupt signals gracefully."""
        print("\n[!] Stop signal received. Completing active chunk calculations...")
        self.shutdown_requested = True

    def _run_preflight_checks(self):
        """Validates baseline OS file properties before boot."""
        logging.info("Running pre-flight checks...")
        if not os.path.exists(self.csv_file):
            raise FileNotFoundError(f"The file '{self.csv_file}' does not exist.")
        if os.path.getsize(self.csv_file) == 0:
            raise ValueError(f"The file '{self.csv_file}' is empty (0 bytes).")

    def run(self):
        try:
            # Step 1: Structural Validations
            self._run_preflight_checks()
            logging.info(f"Step 1: Validating schema alignment for '{self.csv_file}'...")
            validate_schema(self.csv_file, self.table_name, self.db.engine)

            # Step 2: Target Mapping Configuration
            logging.info(f"Step 2: Generating schema for '{self.csv_file}'...")
            schema_table = discover_schema(self.csv_file, self.table_name, self.db.metadata)
            self.db.create_table_from_schema(schema_table)

            # Step 3: Stream Processing Ingestion
            logging.info("Step 3: Beginning bulk load stream...")
            _, file_handle = get_csv_reader(self.csv_file)
            file_handle.close() 

            for chunk in pd.read_csv(self.csv_file, chunksize=2000, encoding='utf-8-sig'):
                # Atomic Break Check: Stop processing before pulling the next block
                if self.shutdown_requested:
                    logging.warning("Ingest execution halted by user request.")
                    break

                # Clean header fields
                chunk.columns = [c.strip().lower().replace(" ", "_") for c in chunk.columns]

                try:
                    self.db.bulk_load(self.table_name, chunk)
                    logging.info(f"Successfully processed batch of {len(chunk)} records.")
                except Exception as e:
                    logging.warning(f"Batch execution failed: {e}. Reverting to fallback isolation mode...")
                    
                    # Concurrency/Connection Crash Check: If the DB connection dropped, break early
                    if "connection" in str(e).lower() or "operationalerror" in str(type(e)).lower():
                        logging.error("Critical database connection fault. Terminating pipeline.")
                        raise e

                    # Row-by-Row Isolation Recovery
                    for index, row in chunk.iterrows():
                        try:
                            self.db.insert_single_row(self.table_name, row)
                        except Exception as row_err:
                            with open("failed_rows.log", "a") as f:
                                f.write(f"Table: {self.table_name} | Error: {row_err} | Data: {row.to_dict()}\n")

            # Final Evaluation Check
            if self.shutdown_requested:
                logging.info("Pipeline stopped safely. Active states committed cleanly.")
            else:
                logging.info("Pipeline executed and completed successfully.")

        except FileNotFoundError as fnf_err:
            logging.error(f"File System Fault: {fnf_err}")
        except ValueError as val_err:
            logging.error(f"Schema Validation Rejected: {val_err}")
        except Exception as e:
            logging.error(f"Critical execution error derailed the process lifecycle: {e}")
        finally:
            # Ensure database pool connections clear no matter how the run ends
            self.close()

    def close(self):
        """Safely disposes open resource connections."""
        if hasattr(self, 'db') and self.db.engine:
            self.db.engine.dispose()
            logging.info("Database connection resources released cleanly.")
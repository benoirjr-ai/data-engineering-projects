import time
import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import OperationalError


def retry_on_lock(retries=3, delay=2):
        def decorator(func):
            def wrapper(*args, **kwargs):
                for  i in range(retries):
                    try:
                        return func(*args, **kwargs)
                    except OperationalError as e:
                        if "database is locked" in str(e) and i < retries - 1:
                            logging.warning(f"Database locked, retrying {i+1}/{retries}...")
                            time.sleep(delay)
                        else:
                            raise e
            return wrapper
        return decorator
    

class DBClient:
    def __init__(self, db_url):
        # We use a single engine for the lifetime of the client
        self.engine = create_engine(db_url)
        # MetaData acts as a registry for our tables
        self.metadata = MetaData()

    def create_table_from_schema(self, table_object):
        """Actually creates the table in the DB if it doesn't exist."""
        # We ensure the table is 'bound' to our engine
        table_object.to_metadata(self.metadata)
        self.metadata.create_all(self.engine)

    
    # Apply to bulk_load
    @retry_on_lock(retries=5, delay=1)

    def bulk_load(self, table_name, df_chunk):
        """Uses the high-performance 'multi' method for inserts."""
        with self.engine.begin() as connection:
            try:
                df_chunk.to_sql(
                    table_name,
                    con=connection,
                    if_exists='append',
                    index=False,
                    # chunksize here helps the DB driver handle the 'multi' method
                    # without hitting parameter limits (common in Postgres/SQL Server)
                    chunksize=200,
                    method='multi'
                )
            except Exception as e:
                # We raise it so the orchestrator in main.py can decide to 
                # skip the chunk or stop the whole process.
                raise e
            
    def insert_single_row(self, table_name, row_series):
        """Recovery method: Inserts one row at a time if bulk fails."""
        with self.engine.begin() as connection:
            # Convert Series to DataFrame for to_sql compatibility
            df_row = row_series.to_frame().T
            df_row.to_sql(
                table_name,
                con=connection,
                if_exists='append',
                index=False        

            )
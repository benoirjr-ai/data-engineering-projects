import pandas as pd
from sqlalchemy import Table, Column, Integer, String, Float, DateTime, MetaData, inspect

TYPE_MAP = {
    'int64': Integer,
    'float64': Float,
    'datetime64[ns]': DateTime,
    'bool': String(5),
}


def discover_schema(file_path, table_name, metadata):
    """Analyzes CSV and returns a SQLAlchemy Table object."""
    # 1. Sample the CSV (peek at first 500 rows for accuracy)
    df_sample = pd.read_csv(file_path, nrows=500)

    # Force pandas to attempt date conversion on 'object' columns
    for col in df_sample.columns:
        if df_sample[col].dtype == 'object':
            try:
                df_sample[col] = pd.to_datetime(df_sample[col])
            except (ValueError, TypeError):
                pass

    columns = []
    for col_name, dtype in df_sample.dtypes.items():
        # Sanitize name: "User Name!" -> "user_name"
        clean_name = col_name.strip().lower().replace(" ", "_")

        # Get the SQL type or default to String
        sql_type = TYPE_MAP.get(str(dtype), String(255))
        columns.append(Column(clean_name, sql_type))
    
    return Table(table_name, metadata, *columns)


def validate_schema(file_path, table_name, db_engine):

    """Checks if the CSV matches the existing database table structure."""
    inspector = inspect(db_engine)

    # Check if table even exists before validating
    if not inspector.has_table(table_name):
        return True
    

    existing_cols = [c['name'] for c in inspector.get_columns(table_name)]
    
    # Get columns from the new CSV(nrows=0 is supper fast)
    new_cols = pd.read_csv(file_path, nrows=0).columns
    new_cols = [c.strip().lower().replace(" ", "_") for c in new_cols]
    
    # Check for missing columns
    missing = set(existing_cols) - set(new_cols)
    if missing:
        raise ValueError(f"CRITICAL: CSV is missing required columns: {missing}")
    
    return True
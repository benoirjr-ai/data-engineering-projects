import os 
import pandas as pd
from src.utils import setup_logger

logger = setup_logger()

def load_to_file(df: pd.DataFrame, output_dir: str = "./data/processed", file_format: str = "parquet") -> str:
    """
    Strategy A: File-Based Storage. 
    Saves the cleaned DataFrame into a structured data lake folder.
    Supports both CSV and highly-optimized Parquet formats.
    """
    logger.info("🎬 Starting the loading phase...")

    try:
        if df.empty:
            raise ValueError("The provided clean DataFrame is empty. Aborting loading.")
        
        os.makedirs(output_dir, exist_ok=True)

        if file_format.lower() == "parquet":
            output_path = os.path.join(output_dir, "historical_fifa_player.parquet")
            # index=False ensures we don't write an unneeded row-number column
            df.to_parquet(output_path, index=False)

        else: # Fallback to Standard CSV
            output_path = os.path.join(output_dir, "historical_fifa_players.csv")
            print(f"💾 Saving data to statandard CSV format at: {output_path}")
            df.to_csv(output_path, index=False)

        logger.info("✅ File storage write complete!")
        return output_path
   
    except PermissionError:
        logger.error(f"❌ Write Permission Denied! Check access levels for folder: {output_dir}")
        raise
    except Exception as e:
        logger.error(f"❌ Critical error encountered in Loading Layer: {e}")
        raise e


def load_to_database(df: pd.DataFrame, table_name: str, db_engine) -> None:
    """
    Strategy B: Relational Database Storage (Truncate and Load).
    Overwrites the targeted database table with the fresh master DataFrame, 
    maintaining strict idempotency.
    """
    logger.info(f"📤 Preparing database upload to table: '{table_name}'...")

    try:
        # if_exists='replace' drops the existing table rows and replaces them 
        # with the exact layout of our fresh DataFrame, eliminating duplications.
        df.to_sql(
            name=table_name,
            con=db_engine,
            if_exists='replace',
            index=False,
            chunksize=5000
        )
        print(f"✅ Success! Database table '{table_name}' is fully loaded and indexed.")

    except Exception as e:
        print(f"❌ Database load strategy encountered a structural failure: {e}")
        raise e


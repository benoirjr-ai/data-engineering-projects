import sys
import time
from src.extract import extract_data
from src.transform import transform_data 
from src.load import load_to_file
from src.validate import validate_data
from src.utils import setup_logger, log_pipeline_metrics

logger = setup_logger()

def main():
    logger.info("--- 🏁 ETL Pipeline Process Initialized 🏁 ---")

    # Target Kaggle Dataset (Replace this with the exact owner/name of your choice)
    # Example template: 'srinivasav22/sales-transactions-dataset'
    start_time = time.time()
    TARGET_DATASET = "luisfucros/fifa-players"
    RAW_DATA_DIR = "./data/raw"
    PROCESSED_DATA_DIR = "./data/processed"

    # Initializing tracking variables for monitoring
    row_count = 0
    col_count = 0
    status = "FAILED"

    
    try:
        # --------------------------------------------------
        # STEP 1: EXTRACT
        # --------------------------------------------------
        logger.info("--- [1/3] EXTRACTION LAYER STARTING ---")

        raw_data_path = extract_data(dataset_slug=TARGET_DATASET, download_path=RAW_DATA_DIR)
        logger.info(f"\n🎉 Step 1 Complete! Data safely landed at: {raw_data_path}")
        
        # --------------------------------------------------
        # STEP 2: TRANSFORM
        # --------------------------------------------------
        logger.info("--- [2/3] TRANSFORMATION LAYER STARTING ---")
        # Pass the verified raw folder path to the transformatoin function
        clean_df = transform_data(raw_data_dir=raw_data_path)
        logger.info("🎉 Transformation Success! Consolidatd in-memory dataframe created. \n")

        # Capture metrics from the in-memory dataframe for monitoring dashboard
        row_count = clean_df.shape[0]
        col_count = clean_df.shape[1]

        # --------------------------------------------------
        # PREVIEW IN-MEMORY METRICS
        # --------------------------------------------------

        print("--- 📊 METRIC & SCHEMA VALIDATION PREVIEW ---")
        print(f"• Combined Rows Picked Up: {clean_df.shape[0]}")
        print(f"• Active Tracked Features : {clean_df.shape[1]}")
        
        print("\n💡 Sample Snapshot of Historical Database:")
        # Displaying a subset of columns including the new 'fifa_year' column
        preview_columns = ['sofifa_id', 'short_name', 'fifa_year', 'overall', 'club_name', 'value_eur']
        print(clean_df[preview_columns].sort_values(by=['sofifa_id', 'fifa_year']).head(10).to_string(index=False))
        print("-" * 50)


        # 🛡️ STEP 2.5: DATA QUALITY VALIDATION GATE
        # The pipeline will evaluate data integrity before loading begins
        is_data_valid = validate_data(df=clean_df)
        
        if not is_data_valid:
            # Drop straight to the except block, locking out the loading mechanism
            raise ValueError("Data Validation failed to clear quality metrics threshold rules.")

        # --------------------------------------------------
        # STEP 3: LOAD 
        # --------------------------------------------------
        logger.info("--- [3/3] LOADING LAYER ---")
        # 👈 Executing the file-based loading strategy as Parquet
        final_output = load_to_file(
                df=clean_df,
                output_dir=PROCESSED_DATA_DIR,
                file_format="parquet"
        )
        logger.info(f"🎉 Load Success! Clean data asset locked down.")

        # Performance Monitoring Metrics
        status = "SUCCESS"
        execution_time = round(time.time() - start_time, 2)
        logger.info(f"🎉 SUCCESS: Full ETL execution completed smoothly in {execution_time} seconds.")
    
    except Exception as pipeline_error:
        # If any step fails, this catch block captures it, preventing silent failure
        status = "CRITICAL_ERROR"
        logger.critical(f"💥 PIPELINE BREAK: Run aborted due to unhandled exception: {pipeline_error}")
        sys.exit(1)

    finally:
        execution_time = time.time() - start_time
        
        # 📊 FIRE MONITORING METRICS METRIC GATE
        log_pipeline_metrics(
            total_rows=row_count,
            total_cols=col_count,
            duration_seconds=execution_time,
            status=status
        )
        
        # This block ALWAYS runs, perfect for closing database sessions or resource cleanup
        logger.info("==================================================")
        logger.info(" 🛑   ETL PIPELINE RUN TERMINATED CLEANLY       🛑")
        logger.info("==================================================\n")
    

if __name__ == "__main__":
        main()
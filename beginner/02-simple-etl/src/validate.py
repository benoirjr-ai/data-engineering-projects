import pandas as pd
from src.utils import setup_logger

logger = setup_logger()

# Renamed to validate_data to match your main.py import statement
def validate_data(df: pd.DataFrame) -> bool:
    """
    Runs a battery of automated data quality checks on the transformed DataFrame.
    Returns True if all checks pass, or raises an exception/returns False if quality drops.
    """
    logger.info("🕵️‍♂️ Initiating Data Quality Validation Layer...")

    # 🛠️ FIX 1: Safety Check order and correct .empty syntax
    if df is None or df.empty:
        logger.error("❌ DQ Failure: DataFrame is entirely empty or None.")
        return False
    
    validation_passed = True
    errors = []

    # CHECK 1: Completeness Threshold
    MINIMUM_ROW_THRESHOLD = 50000
    if len(df) < MINIMUM_ROW_THRESHOLD:
        errors.append(f'Row count too low: Found {len(df)} rows, expected at least {MINIMUM_ROW_THRESHOLD}.')
        validation_passed = False

    # CHECK 2: Null Identifiers (Crucial keys)
    # 🛠️ FIX 2: Corrected column name string to 'sofifa_id'
    critical_columns = ["sofifa_id", "short_name", "fifa_year"]
    for col in critical_columns:
        if col not in df.columns:
            errors.append(f"Missing critical column layout: '{col}' completely absent.")
            validation_passed = False
            continue
            
        # 🛠️ FIX 3: Added missing parentheses to .isnull()
        null_count = df[col].isnull().sum()
        if null_count > 0:
            errors.append(f"Null values detected in identifier column '{col}': {null_count} rows affected.")
            validation_passed = False

    # CHECK 3: Business Logic Range Testing
    # Ratings should logically be within the standard FIFA 1-99 spectrum
    if 'overall' in df.columns:
        if not df['overall'].between(1, 99).all():
            invalid_ratings = df[~df['overall'].between(1, 99)]['overall'].unique()
            errors.append(f"Out-of-bounds ratings detected in 'overall' column: {invalid_ratings}")
            validation_passed = False
    else:
        errors.append("Column 'overall' missing from dataframe during range check.")
        validation_passed = False

    # Age Check
    if 'age' in df.columns:
        if (df['age'] <= 0).any():
            errors.append("Negative or zero values found in 'age' column.")
            validation_passed = False
    else:
        errors.append("Column 'age' missing from dataframe during validation check.")
        validation_passed = False

    # EVALUATE RESULTS
    if validation_passed:
        logger.info("🎉 DATA QUALITY CHECK PASSED: All structural rules and thresholds satisfied.")
        return True
    else:
        logger.error("🚨 DATA QUALITY VALIDATION FAILED! Summary of structural infractions:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
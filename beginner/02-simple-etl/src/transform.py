import os
import glob
import pandas as pd

def transform_data(raw_data_dir: str = "./data/raw"):
    print("⚙️ Starting Streamlined Data Transformation Phase...")
    
    csv_files = glob.glob(os.path.join(raw_data_dir, "*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"💥 No CSV files found in {raw_data_dir}.")
        
    print(f"📋 Confirmed {len(csv_files)} files ready for unified processing.")
    
    all_dfs = []
    
    # Define our ideal clean schema column names
    target_columns = [
        'sofifa_id', 'short_name', 'overall', 'potential', 
        'value_eur', 'wage_eur', 'age', 'club_name', 'nationality_name'
    ]
    
    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        print(f"⏳ Processing & Extracting Features from: {file_name}")
        
        # 1. Added low_memory=False to stop the mixed-type warning
        df = pd.read_csv(file_path, low_memory=False)
        
        # 2. 🛠️ RUGGED ALIGNMENT: Standardize older FIFA column variations
        # Maps legacy names from FIFA 15-18 to our clean schema targets
        rename_map = {
            'club': 'club_name',
            'nationality': 'nationality_name',
            'contract_valid_until': 'contract_valid_until' # in case you use it later
        }
        df.rename(columns=rename_map, inplace=True)
        
        # 3. Dynamic Filtering: Grab only the targets that exist in this dataframe
        existing_cols = [col for col in target_columns if col in df.columns]
        
        # Safety gate: If critical identifiers are missing, skip or alert
        if 'sofifa_id' not in existing_cols:
            print(f"⚠️ Warning: '{file_name}' missing 'sofifa_id'. Skipping file.")
            continue
            
        df_sliced = df[existing_cols].copy()
        
        # 4. Inject Missing Schema Targets as NaN so the tables match structure perfectly
        for col in target_columns:
            if col not in df_sliced.columns:
                df_sliced[col] = None
        
        # 5. Extract the year from the filename
        try:
            year_digits = "".join(filter(str.isdigit, file_name))
            df_sliced['fifa_year'] = int(f"20{year_digits}") if year_digits else None
        except Exception:
            df_sliced['fifa_year'] = file_name
            
        # 6. Append to our consolidation stack
        all_dfs.append(df_sliced)
        
    # Safety Check before concatenation
    if not all_dfs:
        raise ValueError("💥 Total Failure: All extracted dataframes were empty. Check source schemas.")
        
    # 2. Vertically stack all processed files together
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # 3. Fast Imputation (Filling Missing Values)
    combined_df['club_name'] = combined_df['club_name'].fillna('Free Agent')
    combined_df['value_eur'] = combined_df['value_eur'].fillna(0).astype(int)
    combined_df['wage_eur'] = combined_df['wage_eur'].fillna(0).astype(int)
    
    # 4. Idempotency Gate: Composite Deduplication
    initial_count = len(combined_df)
    combined_df.drop_duplicates(subset=['sofifa_id', 'fifa_year', 'club_name'], keep='first', inplace=True)
    final_count = len(combined_df)
    
    print("\n--- ✅ Transformation Complete ---")
    print(f"🧹 Removed {initial_count - final_count} internal duplicate records.")
    print(f"📊 Integrated Dataset Master Shape: {combined_df.shape[0]} rows across {combined_df.shape[1]} columns.")
    
    return combined_df
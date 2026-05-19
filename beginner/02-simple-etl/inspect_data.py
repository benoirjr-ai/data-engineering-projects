import os
import glob
import pandas as pd

def inspect_all_files(raw_data_dir: str = "./data/raw"):
    print("--- 🔍 Starting Multi-File Deep Inspection 🔍 ---")
    
    # 1. Gather all files
    csv_files = glob.glob(os.path.join(raw_data_dir, "*.csv"))
    if not csv_files:
        print("❌ Error: No CSV files found. Run your main pipeline extraction step first!")
        return

    print(f"📦 Found {len(csv_files)} files in landing zone.")
    for f in csv_files:
        print(f"  - {os.path.basename(f)}")
    print("-" * 50)

    # 2. Map and analyze columns across ALL files
    file_schemas = {}
    for file_path in csv_files:
        fname = os.path.basename(file_path)
        # Read just the header row to save memory and time
        df_head = pd.read_csv(file_path, nrows=0)
        file_schemas[fname] = set(df_head.columns)

    # 3. Check for Schema Consistency
    print("🕵️‍♂️ Checking column consistency across files...")
    all_files = list(file_schemas.keys())
    base_file = all_files[0]
    base_columns = file_schemas[base_file]
    
    consistent = True
    for other_file in all_files[1:]:
        other_columns = file_schemas[other_file]
        missing_in_other = base_columns - other_columns
        new_in_other = other_columns - base_columns
        
        if missing_in_other or new_in_other:
            consistent = False
            print(f"\n⚠️ Schema Mismatch found between '{base_file}' and '{other_file}':")
            if missing_in_other:
                print(f"   Missing in {other_file}: {list(missing_in_other)[:5]}... (Truncated)")
            if new_in_other:
                print(f"   Extra in {other_file}: {list(new_in_other)[:5]}... (Truncated)")
                
    if consistent:
        print("✅ Excellent! All files share the exact same column names.")
    print("-" * 50)

    # 4. Sample a single file for Data Type & Messiness validation
    sample_file = csv_files[0]
    print(f"📊 Sampling Data Formats from: {os.path.basename(sample_file)}")
    
    # Read a small 100-row chunk to evaluate data values
    df_sample = pd.read_csv(sample_file, nrows=100)
    
    # Let's inspect potential key targets for our pipeline
    target_check = ['sofifa_id', 'short_name', 'value_eur', 'wage_eur', 'club_name', 'club']
    existing_targets = [c for c in target_check if c in df_sample.columns]
    
    print("\n💡 Data Sample Preview:")
    print(df_sample[existing_targets].head(5))
    
    print("\n💡 Data Types inferred by Pandas:")
    print(df_sample[existing_targets].dtypes)

if __name__ == "__main__":
    inspect_all_files()
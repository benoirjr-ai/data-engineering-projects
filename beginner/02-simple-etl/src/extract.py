import os
import sys
from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi
from src.utils import setup_logger

logger = setup_logger()

# Load environment variables from .env file
load_dotenv()

def get_kaggle_client():
    """
    Authenticates with Kaggle using environment variables.
    Returns an authorized Kaggle API client instance.
    """
    # Quick sanity check to make sure credentials exist before trying to connect
    if not os.getenv("KAGGLE_USERNAME") or not os.getenv("KAGGLE_KEY"):
        print("❌ CRITICAL ERROR: Kaggle credentials missing from .env file.")
        sys.exit(1)

    try:
        print("🔐 Authenticating with Kaggle API...")
        api = KaggleApi()
        api.authenticate()
        print("✅ Authentication successful!")
        return api
    except Exception as e:
        print(f"❌ Failed to authenticate with Kaggle: {e}")
        sys.exit(1)


def extract_data(dataset_slug: str, download_path: str ="./data/raw"):
    """
    Connects to Kaggle and downloads all files from a multi-CSV dataset.
    
    Parameters:
    - dataset_slug (str): The 'owner/dataset-name' path from the Kaggle URL.
    - output_dir (str): Destination folder where raw files will be saved.
    """

    logger.info(f"🎬 Starting extraction for dataset: {dataset_slug}")

    #check if the directory exists and is NOT empty
    try:
        if os.path.exists(download_path) and os.listdir(download_path):
            logger.info(f"📦 Data already exists in '{download_path}'. Skipping Kaggle download to save bandwidth.")
            return download_path

        # 1. Initialize the authenticated connector client
        api = get_kaggle_client()

        # 2. Ensure target directory exists
        os.makedirs(download_path, exist_ok=True)

        logger.info(f"📥 Fetching all files for dataset: '{dataset_slug}'...")

        # 3. Trigger the download and extraction
        # unzip=True automatically handles unpacking multi-file ZIP bundles into separate CSVs
        api.dataset_download_files(dataset_slug, path=download_path, unzip=True)

        # 4. List downloaded files for validation logs
        downloaded_files = os.listdir(download_path)
        print(f"🚀 Success! Extracted {len(downloaded_files)} files into local directory.")
        for file in downloaded_files:
            print(f" - {file}")

    except ImportError:
        logger.error("🚨 Missing 'Kaggle' library. Run 'pip install kaggle'.")
        raise
    
    except Exception as e:
        logger.error(f"❌ Extraction failed due to an API or Network issue: {e}")
        raise e 
    
    return download_path
    
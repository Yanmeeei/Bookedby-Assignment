from pathlib import Path

# Path values
CONFIG_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CONFIG_DIR

DATA_PATH = PROJECT_ROOT / "data/"
DATASET_PATH = DATA_PATH / "dataset.csv"
PRODUCTS_PATH = DATA_PATH / "products.csv"

OUTPUT_PATH = PROJECT_ROOT / "results"
ANALYSIS_OUTPUT_PATH = PROJECT_ROOT / "results/analysis_results.txt"
CLUSTER_OUTPUT_PATH = PROJECT_ROOT / "results/cluster"
REC_OUTPUT_PATH = PROJECT_ROOT / "results/recommendations"

RECOMMENDATION_TEMP_PATH = PROJECT_ROOT / "recommendation/temp/"
CLUSTER_TEMP_PATH = PROJECT_ROOT / "clustering/temp/"

# Default values for cli arguments
# generate
DEFAULT_NUM_PRODUCTS = 80
DEFAULT_NUM_CUSTOMERS = 500

# clustering kmeans
DEFAULT_NUM_CLUSTERS = 6

# recommendation content-filter
DEFAULT_NUM_CATEGORY = 2
DEFAULT_NUM_PRODUCT = 2

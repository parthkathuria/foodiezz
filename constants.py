import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = "config.json"

# config file keys
SOCRATA_DOMAIN = "socrataDomain"
SOCRATA_DATASET_ID = "socrataDatasetId"
APP_TOKEN = "appToken"
QUERY_LIMIT = "queryLimit"

# default values
DEFAULT_SOCRATA_DOMAIN = "data.sfgov.org"
DEFAULT_SOCRATA_DATASET_ID = "jjew-r69b"
DEFAULT_QUERY_LIMIT = 10

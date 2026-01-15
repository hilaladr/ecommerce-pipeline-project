import os 
import json

# Set config directory BEFORE importing KaggleApi
os.environ['KAGGLE_CONFIG_DIR'] = r'/home/hadryantama/ecommerce-pipeline-project'

import pandas as pd
import requests
from sqlalchemy import create_engine
from kaggle.api.kaggle_api_extended import KaggleApi

# Create kaggle.json if it doesn't exist
config_dir = os.environ['KAGGLE_CONFIG_DIR']
config_file = os.path.join(config_dir, 'kaggle.json')

if not os.path.exists(config_file):
    os.makedirs(config_dir, exist_ok=True)
    with open(config_file, 'w') as f:
        json.dump({"username": "temp", "key": "KGAT_c123002d554ef3da0b5e6721ef84c68e"}, f)

api = KaggleApi()
api.verify_ssl = False
api.authenticate()

DATASET_NAME = 'olistbr/brazilian-ecommerce'
DOWNLOAD_PATH = './data_source'

api.dataset_download_files(DATASET_NAME, path=DOWNLOAD_PATH, unzip=True)

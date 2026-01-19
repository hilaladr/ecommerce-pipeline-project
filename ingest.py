import os 
import json
import boto3
from pathlib import Path

# Downloading files from kaggle and upload them to amazon s3

# Set config directory BEFORE importing KaggleApi
os.environ['KAGGLE_CONFIG_DIR'] = r'/home/hadryantama/ecommerce-pipeline-project'

import pandas as pd
import requests
from sqlalchemy import create_engine
from kaggle.api.kaggle_api_extended import KaggleApi

# --- CONFIG ---
AWS_ACCESS_KEY = "AKIAWULRUHUPK3ZRAHM7"
AWS_SECRET_KEY = "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"
BUCKET_NAME    = "ecommerce-pipeline-project"
REGION         = "ap-southeast-3"
KAGGLE_TOKEN   = "KGAT_c123002d554ef3da0b5e6721ef84c68e"

# Create kaggle.json if it doesn't exist
config_dir = os.environ['KAGGLE_CONFIG_DIR']
config_file = os.path.join(config_dir, 'kaggle.json')

if not os.path.exists(config_file):
    os.makedirs(config_dir, exist_ok=True)
    with open(config_file, 'w') as f:
        json.dump({"username": "temp", "key": KAGGLE_TOKEN}, f)

api = KaggleApi()
api.verify_ssl = False
api.authenticate()

DATASET_NAME = 'olistbr/brazilian-ecommerce'
DOWNLOAD_PATH = 'temp_data'

if DOWNLOAD_PATH not in os.listdir() :
    print("Downloading dataset...")
    api.dataset_download_files(DATASET_NAME, path=DOWNLOAD_PATH, unzip=True)
else :
    print("Dataset already downloaded")

print("Connecting to S3...")
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, 
                      aws_secret_access_key=AWS_SECRET_KEY, region_name=REGION)

for item in Path(DOWNLOAD_PATH).iterdir() :
    s3_raw = f'raw/{item.name}'
    try :
        s3.head_object(Bucket=BUCKET_NAME, Key=s3_raw)
        print(f'File {item.name} already exists')
            # os.remove(item)
    except :
        print(f'Uploading file : {item.name}')
        s3.upload_file(item, BUCKET_NAME, Key=s3_raw)


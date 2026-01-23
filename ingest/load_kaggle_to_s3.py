import os 
import boto3
from pathlib import Path
from dotenv import load_dotenv
import shutil



def kaggle_to_s3() :
    load_dotenv()
    # Set config  BEFORE importing KaggleApi
    # --- CONFIG ---
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
    BUCKET_NAME    = os.environ.get('AWS_S3_BUCKET')
    REGION         = os.environ.get('AWS_REGION')
    KAGGLE_USERNAME  = os.environ.get('KAGGLE_USERNAME')
    KAGGLE_KEY = os.environ.get('KAGGLE_KEY')

    os.environ['KAGGLE_USERNAME'] = KAGGLE_USERNAME
    os.environ['KAGGLE_KEY'] = KAGGLE_KEY

    from kaggle.api.kaggle_api_extended import KaggleApi
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
        except :
            print(f'Uploading file : {item.name}')
            # s3.upload_file(item, BUCKET_NAME, Key=s3_raw)
    # shutil.rmtree(DOWNLOAD_PATH) 

if __name__ == "__main__":
    kaggle_to_s3()
    # print(generate_copy_sql()[0])


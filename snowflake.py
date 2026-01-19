from snowflake.connector import connect
from snowflake.core import Root
import os
import snowflake
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL

# copy local data directly to snowflake db

conn = create_engine(URL(
    user="HILALADR",
    password="N!celySNOWFLAKE00",
    account="QSSEGWF-UY63392",
    warehouse="COMPUTE_WH",
    role="ACCOUNTADMIN",
    database="OLIST_DWH",
    schema="PUBLIC"
    ))


for item in Path('./data_source').iterdir() :
    table_name = item.name.replace('olist_','').replace('.csv','').replace('dataset','')
    data = pd.read_csv(item)
    data.to_sql(table_name, conn, if_exists='replace', chunksize=10000, method='multi', index=False)
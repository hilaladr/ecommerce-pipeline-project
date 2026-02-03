import pandas as pd
import os
from pathlib import Path
from snowflake.connector import connect
from dotenv import load_dotenv
import shutil

# create table di snowflake dgn format berdasarkan file csv di folder temp_data 

def generate_script() :

    sql_table = []
    file_path_list = Path('./temp_data').iterdir()

    for file_path in file_path_list :
        df = pd.read_csv(file_path, nrows=20)
        table_name = str(file_path).split('/')[-1].replace('.csv','').replace('olist_','').replace('_dataset','')

        sql_create = f'CREATE OR REPLACE TABLE {table_name.strip().upper()} ('

        for col in df.columns :
            col_type = df[col].dtypes

            match col_type :
                case 'object' :
                    field_type = 'VARCHAR(16777216)'
                case 'int64' :
                    field_type = 'INTEGER'
                case 'float64' :
                    field_type  = 'FLOAT'

            sql_columns = f'{col.upper()} {field_type},'
            sql_create += sql_columns

        sql_create += ');'
        sql_table.append(sql_create.replace(',);',');'))
    shutil.rmtree('temp_data') 
    return sql_table

def create_table() :
    load_dotenv()
    script = generate_script()

    print("❄️ Connecting to Snowflake...")

    # create connection
    try :
        with connect(
            user=os.environ.get('SNOWFLAKE_USER'),
            password=os.environ.get('SNOWFLAKE_PASSWORD'),
            account=os.environ.get('SNOWFLAKE_ACCOUNT'),
            warehouse="COMPUTE_WH",
            role="ACCOUNTADMIN",
            database="OLIST_DWH",
            schema="PUBLIC"

        ) as conn :
            # Pull existing table list
            with conn.cursor() as cur :
                # check existing tables
                existing_tables = cur.execute('''SELECT table_name FROM INFORMATION_SCHEMA.TABLES 
                                WHERE table_type = 'BASE TABLE';''').fetchall()
                existing_tables = [item[0] for item in existing_tables]
               
                # try to execute create table script
                for i in script :
                    try:
                        table_name = i.split()[4]
                        # check if table already exists, create if not
                        if table_name in existing_tables : 
                            print(f"Table {table_name} already exists...")
                        else :
                            print(f"🔨 Creating Table {table_name}")
                            cur.execute(i)
                    except Exception as e:
                        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Failed to connect. Error: {e}")

if __name__ == "__main__":
    create_table()


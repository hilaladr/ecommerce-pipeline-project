import pandas as pd
import os
from pathlib import Path
from snowflake.connector import connect

def generate_script() :

    sql_table = ''

    for file_path in Path('./temp_data').iterdir() :
        df = pd.read_csv(file_path, nrows=20)
        table_name = str(file_path).split('/')[-1].replace('.csv','').replace('olist_','').replace('_dataset','')

        sql_table += f'CREATE OR REPLACE TABLE {table_name.strip().upper()} ('

        for col in df.columns :
            col_type = df[col].dtypes
            match col_type :
                case 'object' :
                    field_type = 'VARCHAR(16777216)'
                case 'int64' :
                    field_type = 'INTEGER'
                case 'float64' :
                    field_type  = 'FLOAT'
            sql_column = f'{col.upper()} {field_type},\n'
            sql_table += sql_column
        sql_table += ');'
        sql_table = sql_table.replace(',\n);','\n);\n\n')
    return sql_table

def create_table() :

    # split per table
    script = generate_script().replace('\n','').split(";")

    print("❄️ Connecting to Snowflake...")

    # create connection
    conn = connect(
        user="HILALADR",
        password="N!celySNOWFLAKE00",
        account="QSSEGWF-UY63392",
        warehouse="COMPUTE_WH",
        role="ACCOUNTADMIN",
        database="OLIST_DWH",
        schema="PUBLIC"
    )
    cur = conn.cursor()

    # execute sql script
    for i in script :
        if i != '' :
            try:
                print(f"🔨 Creating Table {i.split()[4]}")
                cur.execute(i)
            except Exception as e:
                print(f"❌ Error: {e}")

    cur.close()  
    conn.close()

if __name__ == "__main__":
    # script = generate_script().replace('\n','').strip().split(";")
    # print(script)
    create_table()

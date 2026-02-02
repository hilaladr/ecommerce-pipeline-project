from load_s3_to_snowflake.connector import connect
from pathlib import Path
from dotenv import load_dotenv

# copy local data directly to snowflake db


def generate_copy_sql() :
    table_matching = {}
    sql_copy_into = []

    for i in Path('./temp_data').iterdir() :
        file_name = i.name
        table_name = file_name.replace('.csv','').replace('olist_','').replace('_dataset','')
        table_matching[file_name] = table_name

        sql_copy_into.append( f"COPY INTO {table_name} FROM @MY_S3_STAGE/{file_name} ON_ERROR = 'CONTINUE';")

    return sql_copy_into


def execute_copy_sql() :
    load_dotenv()
    # snowflake connection
    conn= connect(
            user=os.environ.get('SNOWFLAKE_USER'),
            password=os.environ.get('SNOWFLAKE_PASSWORD'),
            account=os.environ.get('SNOWFLAKE_ACCOUNT'),
            warehouse=os.environ.get('SNOWFLAKE_WAREHOUSE'),
            role=os.environ.get('SNOWFLAKE_ROLE'),
            database="OLIST_DWH",
            schema="PUBLIC"
        )

    cur = conn.cursor()
    for script in generate_copy_sql() :
        file_name = script.split()[4].replace('@MY_S3_STAGE/','')
        target_table = script.split()[2]
        print(f"Copying file {file_name} to {target_table}")
        # cur.execute(script)

    cur.close()
    conn.close()
    

if __name__ == "__main__":
    execute_copy_sql()
    # print(generate_copy_sql()[0])
from load_s3_to_snowflake.connector import connect
from pathlib import Path

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
    conn= connect(
            user="HILALADR",
            password="N!celySNOWFLAKE00",
            account="QSSEGWF-UY63392",
            warehouse="COMPUTE_WH",
            role="ACCOUNTADMIN",
            database="OLIST_DWH",
            schema="PUBLIC"
        )

    cur = conn.cursor()
    for script in generate_copy_sql() :
        print(f"Copying file {script.split()[4].replace('@MY_S3_STAGE/','')} to {script.split()[2]}")
        cur.execute(script)

    cur.close()
    conn.close()
    

if __name__ == "__main__":
    execute_copy_sql()
    # print(generate_copy_sql()[0])
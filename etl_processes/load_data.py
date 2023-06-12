import pandas as pd
import psycopg2

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="remote.hungtuan.me",
    port="5432",
    database="tablecheck",
    user="tuan",
    password=""
)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS table_check_data")
create_table_query = '''
CREATE TABLE table_check_data (
    restaurant_names VARCHAR(42),
    food_names VARCHAR(12),
    first_name VARCHAR(12),
    food_cost double precision
);
'''
cursor.execute(create_table_query)

# Execute the COPY command to insert new data
try:
    with open('/root/table_check_project/data_files/transformed_data.csv', 'r') as file:
        #skip header
        next(file)
        cursor.copy_from(file, 'table_check_data', sep=',')
    conn.commit()
    row_count = cursor.rowcount
    print("Data loaded successfully. Rows affected:", row_count)
except (Exception, psycopg2.Error) as e:
    conn.rollback()
    print("Error during data copy:", str(e))

conn.commit()
conn.close()

### Table of Content

- [Table of Content](#table-of-content)
- [Overview](#overview)
- [ETL Implementation](#etl-implementation)
- [Dashboard and Reports](#dashboard-and-reports)
- [Additional question and solution](#additional-question-and-solution)

<a id="Overview"></a>

### Overview

<a id="structure"></a>

- **Structure**
Data download from source, do simple reformat and load to PostgreSQL.
Set up Looker Studio to connect and pull latest data from PostgreSQL for visualizing data
<img width="857" alt="image" src="https://github.com/tuannnh/table_check_take_home_project/assets/51945324/56c489f4-5d54-41c9-bc7f-1d7f0c2e965b">

<a id="resources"></a>
- **Resources**
  - **Database:** PostgreSQL 14
  - **ETL Pipeline:**
    - OS: Ubuntu 22.04
    - Apache Airflow
    - Python 3
    - Libraries: pandas, psycopg2, wget, airflow
  - **Dashboard**: Looker Studio
<a id="etl_implementation"></a>

### ETL Implementation

<a id="extract"></a>

- **Extract:** Download data from remote source (CSV file generated in project GitHub repo)

```python
import wget
import os

# Download csv data file to process
print('Start download data from source')

FILE_NAME='data.csv'

URL = "https://raw.githubusercontent.com/TableCheck-Labs/tablecheck-data-operations-take-home/main/data/data.csv"

if os.path.exists(f"/root/table_check_project/data_files/{FILE_NAME}"):
 os.remove(f"/root/table_check_project/data_files/{FILE_NAME}")

response = wget.download(URL,f"/root/table_check_project/data_files/{FILE_NAME}")

print(f"{FILE_NAME} downloaded successfully")
```

<a id="transform"></a>

- **Transform:** Having some simple reformation: replace '-' character in "**restaurant_names**" field, capitalize names

```python
import pandas as pd

print('Start transforming data')

# Read the CSV file into a DataFrame
df = pd.read_csv('/root/table_check_project/data_files/data.csv')

# Replace '-' to space character

df['restaurant_names'] = df['restaurant_names'].str.replace('-', ' ')

# Capitalize the restaurant names and the food names
df['restaurant_names'] = df['restaurant_names'].str.capitalize()
df['food_names'] = df['food_names'].str.capitalize()

# Save the modified DataFrame to a new CSV file
df.to_csv('/root/table_check_project/data_files/transformed_data.csv', index=False)

print('Transform data successfully!')
```

<a id="load"></a>

- **Load:** Load the transformed data to PostgreSQL

```python
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
```

<a id="orchestration"></a>

- **Orchestration:** Schedule the ETL task to run daily, monitor running processes and logs using **Apache Airflow**

```python
from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
  
default_args = {
 'owner': 'Tuan Nguyen',
 'start_date': days_ago(0),
 'email': ['mail@hungtuan.me'],
 'retries': 1,
 'retry_delay': timedelta(minutes=5)
}


dag = DAG(
 'table_check',
 default_args=default_args,
 description='TableCheck Data Operations Take Home Project',
 schedule_interval=timedelta(days=1)
)

  

# ETL tasks
extract_data = BashOperator(
 task_id='extract_data',
 bash_command='python /root/table_check_project/etl_processes/extract_data.py',
 dag=dag
)

transform_data = BashOperator(
 task_id='transform_data',
 bash_command='python /root/table_check_project/etl_processes/transform_data.py',
 dag=dag
)

  

load_data = BashOperator(
 task_id='load_data',
 bash_command='python /root/table_check_project/etl_processes/load_data.py',
 dag=dag
)

# ETL pipeline
extract_data >> transform_data >> load_data
```

<a id="dashboard_and_reports"></a>

### Dashboard and Reports

- Connect PostgreSQL to Looker Studio for reporting with data refreshing
<img width="1205" alt="image" src="https://github.com/tuannnh/table_check_take_home_project/assets/51945324/987ea248-0412-4de4-ac1c-29e8c248b9b4">

- **Dashboard Live:**<https://lookerstudio.google.com/reporting/f5c5b497-3df7-4a1f-98be-25f2ba7fcc86>
<a id="additional_question_and_solution"></a>

### Additional question and solution

<a id="q1"></a>

- **How would you build this differently if the data was being streamed from Kafka?**
  - There are **three** solutions can be considered to build up the system when data was being streamed from Kafka.
    - **Method 1:** In situations where the data involves straightforward transformations and is relatively small in size and task. This involves performing the data transformation during the ingestion process and delivering it to a database, such as PostgreSQL, with a modified structure and schema. Subsequently, the transformed data can be seamlessly pushed to a visualization tool for further analysis and interpretation.
  <img width="1001" alt="image" src="https://github.com/tuannnh/table_check_take_home_project/assets/51945324/1407a3f6-8f9e-4b76-8fa0-fb71a7aa8d9d">
  
    - **Method 2:** To ensure scalability as the data volume increases, it is worth considering the storage of raw Kafka data in object storage like Amazon S3. Subsequently, the data can be processed either in batches or streams (e.g., using SparkStreaming) based on specific requirement use cases.
  <img width="1021" alt="image" src="https://github.com/tuannnh/table_check_take_home_project/assets/51945324/b5dc43d1-e649-483e-a1b5-ce4ac544a98a">
  
 <a id="q2"></a>
- **How would you improve the deployment of this system?**
  - To enhance the deployment of this system there are several areas I am considering some areas:
    - **Parameterize configurations**: Instead of hardcoding values, make use of configuration files or variables to parameterize settings such as source connection details, transformation logic, destination credentials. This enables flexibility and facilitates easy configuration changes without modifying the codebase.
    - **Error handling and monitoring**: Implement comprehensive error handling mechanisms within each task to handle exceptions gracefully. Incorporate appropriate logging and alerting mechanisms to be notified of any failures or anomalies during the ETL process.
    - **Parallelize and optimize execution**: Identify areas where parallelization can be leveraged to improve processing speed. For example, if certain tasks are independent and can be executed concurrently, configure Airflow to run them in parallel. Additionally, optimizing the performance of transformations by utilizing optimized libraries, caching mechanisms, or distributed computing frameworks like Apache Spark.
    - **Automated testing**: Implement automated testing procedures to validate the ETL pipeline's correctness and integrity. Include unit tests for individual transformation functions, integration tests for the entire workflow, and data quality checks to ensure the accuracy and consistency of the loaded data.
    - **Version control and deployment automation**: Utilize version control systems like Git to manage code changes and maintain a history of modifications. Implement a CI/CD (Continuous Integration/Continuous Deployment) pipeline to automate the deployment process, ensuring seamless updates and rollbacks.

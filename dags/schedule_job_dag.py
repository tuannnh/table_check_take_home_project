from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'Tuan Nguyen',
    'start_date': days_ago(0),
    'email': ['mail@hungtuan.me'],
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'table_check',
    default_args=default_args,
    description='TableCheck Data Operations Take Home Project',
    schedule_interval=timedelta(days=1),
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



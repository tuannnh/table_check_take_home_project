import wget
import os

# Download csv data file to process
print('Start download data from source')

FILE_NAME='data.csv'

URL = "https://raw.githubusercontent.com/TableCheck-Labs/tablecheck-data-operations-take-home/main/data/data.csv"
if os.path.exists(f"/root/table_check_project/data_files/{FILE_NAME}"):
    os.remove(f"/root/table_check_project/data_files/{FILE_NAME}")
response = wget.download(URL, f"/root/table_check_project/data_files/{FILE_NAME}")

print(f"{FILE_NAME} downloaded successfully")
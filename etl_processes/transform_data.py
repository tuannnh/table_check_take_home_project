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
import sqlite3
import pandas as pd

# SQLite Configuration
sqlite_db_path = 'weather_data.db'

# Connect to the SQLite database
conn = sqlite3.connect(sqlite_db_path)

# Query to select data from the table
query = "SELECT * FROM avg_temp_per_month"
df = pd.read_sql_query(query, conn)

# Print the data
print(df)

# Close the connection
conn.close()
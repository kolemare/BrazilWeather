import json
import sqlite3
import pandas as pd
from datetime import datetime


class DaoHandler:
    @staticmethod
    def write_to_db(payload):
        parts = payload.split(":", 1)
        if len(parts) == 2:
            table_name, data_str = parts
            data = json.loads(data_str)

            # Convert the data to a Pandas DataFrame
            df = pd.DataFrame(data)

            # Create or open the SQLite database
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            # Dynamically extract column names from the DataFrame
            columns = ', '.join(df.columns)
            placeholders = ', '.join(['?'] * len(df.columns))

            # Create the table if it does not exist
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
            cursor.execute(create_table_query)

            # Iterate through the DataFrame and update or insert rows
            for _, row in df.iterrows():
                # Check if the row exists
                query_conditions = ' AND '.join([f"{col} = ?" for col in df.columns])
                query = f"SELECT * FROM {table_name} WHERE {query_conditions}"
                cursor.execute(query, tuple(row))
                existing_row = cursor.fetchone()

                if existing_row:
                    # Update the existing row with the new data
                    update_columns = ', '.join([f"{col} = ?" for col in df.columns])
                    update_query = f"UPDATE {table_name} SET {update_columns} WHERE {query_conditions}"
                    cursor.execute(update_query, tuple(row) * 2)
                else:
                    # Insert a new row
                    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    cursor.execute(insert_query, tuple(row))

            # Commit the changes
            conn.commit()
            conn.close()

    @staticmethod
    def get_table(table_name, region, period_months):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Get the maximum date in the table
        max_date_query = f"SELECT MAX(date) FROM {table_name}"
        cursor.execute(max_date_query)
        max_date = cursor.fetchone()[0]
        max_timestamp = pd.to_datetime(max_date, unit='ms').timestamp()

        # Calculate the cutoff time for the period
        cutoff_time = max_timestamp - (period_months * 30 * 24 * 3600)  # Approximate calculation

        # Convert the cutoff time to a datetime object in milliseconds
        cutoff_date_ms = int(cutoff_time * 1000)

        # Construct the query based on the region
        if region == 'all':
            query = f"""
                    SELECT * FROM {table_name}
                    WHERE date >= {cutoff_date_ms}
                """
        else:
            query = f"""
                    SELECT * FROM {table_name}
                    WHERE region = '{region}'
                    AND date >= {cutoff_date_ms}
                """

        result_df = pd.read_sql_query(query, conn)

        conn.close()
        return result_df

    @staticmethod
    def get_realtime_table(region):
        conn = sqlite3.connect("database.db")

        query = f"""
                    SELECT * FROM realtime_data
                    WHERE region = '{region}'
                """

        result_df = pd.read_sql_query(query, conn)

        conn.close()
        return result_df

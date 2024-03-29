import pandas as pd
import matplotlib.pyplot as plt


class Calculator:
    @staticmethod
    def calculate_avg_temp(region, df, months_back):
        # Convert 'date' column to datetime and filter for the last "months_back" months
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        latest_date = df['date'].max()
        max_timestamp = latest_date.timestamp()

        # Calculate the cutoff time for the period
        cutoff_time = max_timestamp - (months_back * 30 * 24 * 3600)  # Approximate calculation

        # Convert the cutoff time to a datetime object
        cutoff_date = pd.to_datetime(cutoff_time, unit='s')

        # Filter the DataFrame for the last "months_back" months
        reg_filtered = df[df['date'] >= cutoff_date].copy()
        reg_filtered['year'] = reg_filtered['date'].dt.year
        reg_filtered['month'] = reg_filtered['date'].dt.month

        # Group by state, year, and month, then calculate average temperature
        avg_temp_by_state = reg_filtered.groupby(['prov', 'year', 'month'])['temp'].mean().reset_index(name='avg_temp')

        # Add period column
        avg_temp_by_state['period'] = avg_temp_by_state['year'].astype(str) + avg_temp_by_state['month'].astype(str).str.zfill(2)

        # Add region and date columns
        avg_temp_by_state['region'] = region
        avg_temp_by_state['date'] = pd.to_datetime(avg_temp_by_state['year'].astype(str) + '-' + avg_temp_by_state['month'].astype(str))

        # Sort by state, year, and then by month to ensure chronological order within each state
        avg_temp_by_state = avg_temp_by_state.sort_values(by=['prov', 'period'])

        # Return results for the specified region
        return avg_temp_by_state

    @staticmethod
    def calculate_total_rainfall(region, df, years_back):
        # Convert 'date' column to datetime
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df['hour'] = df['hour'].str.split(':').str[0].astype(int)

        # Filter for the last "years_back" years
        latest_date = df['date'].max()
        max_timestamp = latest_date.timestamp()

        # Calculate the cutoff time for the period
        cutoff_time = max_timestamp - (years_back * 365 * 24 * 3600)  # Approximate calculation

        # Convert the cutoff time to a datetime object
        cutoff_date = pd.to_datetime(cutoff_time, unit='s')

        # Filter the DataFrame for the last "years_back" years
        reg_filtered = df[df['date'] >= cutoff_date].copy()

        # Create 'year' column
        reg_filtered['year'] = reg_filtered['date'].dt.year

        # Group by state, date, and hour, then calculate average precipitation
        avg_rainfall_by_hour = reg_filtered.groupby(['prov', 'date', 'hour'])['prcp'].mean().reset_index()

        # Ensure 'year' is created for avg_rainfall_by_hour before grouping by state and year
        avg_rainfall_by_hour['year'] = avg_rainfall_by_hour['date'].dt.year

        # Group by state and year, then calculate total precipitation
        total_rainfall_by_state = avg_rainfall_by_hour.groupby(['prov', 'year'])['prcp'].sum().reset_index(
            name='total_rainfall')

        # Add period column
        total_rainfall_by_state['period'] = total_rainfall_by_state['year'].astype(str) + '01'

        # Add region and date columns
        total_rainfall_by_state['region'] = region
        total_rainfall_by_state['date'] = pd.to_datetime(total_rainfall_by_state['year'].astype(str) + '-01')

        # Sort by state and then by year to ensure chronological order within each state
        total_rainfall_by_state = total_rainfall_by_state.sort_values(by=['prov', 'period'])

        # Return results for the specified region
        return total_rainfall_by_state

    @staticmethod
    def calculate_pressure_extremes(region, df, months_back):
        # Convert 'date' column to datetime and filter for the last "months_back" months
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        latest_date = df['date'].max()
        max_timestamp = latest_date.timestamp()

        # Calculate the cutoff time for the period
        cutoff_time = max_timestamp - (months_back * 30 * 24 * 3600)  # Approximate calculation

        # Convert the cutoff time to a datetime object
        cutoff_date = pd.to_datetime(cutoff_time, unit='s')

        # Filter the DataFrame for the last "months_back" months
        reg_filtered = df[df['date'] >= cutoff_date].copy()

        # Group by state and month, then calculate highest and lowest pressures
        reg_filtered['year'] = reg_filtered['date'].dt.year
        reg_filtered['month'] = reg_filtered['date'].dt.month
        pressure_extremes = reg_filtered.groupby(['prov', 'year', 'month']).agg(
            max_pressure=('stp', 'max'),
            min_pressure=('stp', 'min')
        ).reset_index()

        # Add period column
        pressure_extremes['period'] = pressure_extremes['year'].astype(str) + pressure_extremes['month'].astype(str).str.zfill(2)

        # Add region and date columns
        pressure_extremes['region'] = region
        pressure_extremes['date'] = pd.to_datetime(pressure_extremes['year'].astype(str) + '-' + pressure_extremes['month'].astype(str).str.zfill(2))

        # Sort by state, year, and then by month to ensure chronological order within each state
        pressure_extremes = pressure_extremes.sort_values(by=['prov', 'period'])

        # Return results for the specified region
        return pressure_extremes
import pandas as pd
import matplotlib.pyplot as plt


class Calculator:
    @staticmethod
    def calculate_avg_temp(region, df, months_back):
        # Convert 'date' column to datetime and filter for the last "months_back" months
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        latest_date = df['date'].max()
        cutoff_date = latest_date - pd.DateOffset(months=months_back)
        reg_filtered = df[df['date'] > cutoff_date]

        # Group by state, year, and month, then calculate average temperature
        reg_filtered['year'] = reg_filtered['date'].dt.year
        reg_filtered['month'] = reg_filtered['date'].dt.month
        avg_temp_by_state = reg_filtered.groupby(['prov', 'year', 'month'])['temp'].mean().reset_index(name='avg_temp')

        # Sort by state, year, and then by month to ensure chronological order within each state
        avg_temp_by_state = avg_temp_by_state.sort_values(by=['prov', 'year', 'month'])

        # Return results for the specified region
        print(avg_temp_by_state)
        return avg_temp_by_state

    @staticmethod
    def calculate_total_rainfall(region, df, years_back):
        mean_precipitation = df['prcp'].mean()
        print(f"Mean is: {mean_precipitation}")

        # Convert 'date' column to datetime
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df['hour'] = df['hour'].str.split(':').str[0].astype(int)

        # Filter for the last "years_back" years
        latest_date = df['date'].max()
        cutoff_date = latest_date - pd.DateOffset(years=years_back)
        reg_filtered = df[df['date'] > cutoff_date]

        # Create 'year' column
        reg_filtered['year'] = reg_filtered['date'].dt.year

        # Group by state, date, and hour, then calculate average precipitation
        avg_rainfall_by_hour = reg_filtered.groupby(['prov', 'date', 'hour'])['prcp'].mean().reset_index()

        # Ensure 'year' is created for avg_rainfall_by_hour before grouping by state and year
        avg_rainfall_by_hour['year'] = avg_rainfall_by_hour['date'].dt.year

        # Group by state and year, then calculate total precipitation
        total_rainfall_by_state = avg_rainfall_by_hour.groupby(['prov', 'year'])['prcp'].sum().reset_index(
            name='total_rainfall')

        # Sort by state and then by year to ensure chronological order within each state
        total_rainfall_by_state = total_rainfall_by_state.sort_values(by=['prov', 'year'])

        # Return results for the specified region
        print(total_rainfall_by_state)
        return total_rainfall_by_state

    @staticmethod
    def calculate_pressure_extremes(region, df, months_back):
        # Convert 'date' column to datetime and filter for the last "months_back" months
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        latest_date = df['date'].max()
        cutoff_date = latest_date - pd.DateOffset(months=months_back)
        reg_filtered = df[df['date'] > cutoff_date]

        # Group by state and month, then calculate highest and lowest pressures
        reg_filtered['month'] = reg_filtered['date'].dt.month
        pressure_extremes = reg_filtered.groupby(['prov', 'month']).agg(
            max_pressure=('stp', 'max'),
            min_pressure=('stp', 'min')
        ).reset_index()

        # Sort by state and then by month to ensure chronological order within each state
        pressure_extremes = pressure_extremes.sort_values(by=['prov', 'month'])

        # Return results for the specified region
        print(pressure_extremes)
        return pressure_extremes

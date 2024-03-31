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
        avg_temp_by_state['period'] = avg_temp_by_state['year'].astype(str) + avg_temp_by_state['month'].astype(
            str).str.zfill(2)

        # Add region and date columns
        avg_temp_by_state['region'] = region
        avg_temp_by_state['date'] = pd.to_datetime(
            avg_temp_by_state['year'].astype(str) + '-' + avg_temp_by_state['month'].astype(str))

        # Sort by state, year, and then by month to ensure chronological order within each state
        avg_temp_by_state = avg_temp_by_state.sort_values(by=['prov', 'period'])

        # Return results for the specified region
        return avg_temp_by_state

    @staticmethod
    def calculate_total_rainfall(region, df, months_back):
        # Ensure 'hour' and 'prcp' columns are in the correct format
        df['hour'] = df['hour'].astype(str).str.split(':').str[0].astype(int)
        df['prcp'] = df['prcp'].astype(float)

        # Convert 'date' column to datetime and filter by 'months_back'
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        latest_date = df['date'].max()

        # Calculate the cutoff time for the period
        cutoff_time = latest_date.timestamp() - (months_back * 30 * 24 * 3600)
        cutoff_date = pd.to_datetime(cutoff_time, unit='s')
        reg_filtered = df[df['date'] >= cutoff_date].copy()

        # Create 'year' and 'month' columns from 'date'
        reg_filtered['year'] = reg_filtered['date'].dt.year
        reg_filtered['month'] = reg_filtered['date'].dt.month

        # Group by 'prov', 'year', 'month', and 'hour', then calculate average 'prcp'
        avg_rainfall_by_hour = reg_filtered.groupby(['prov', 'year', 'month', 'hour'])['prcp'].mean().reset_index()

        # Group by 'prov', 'year', 'month', then calculate the sum of 'prcp'
        total_rainfall_by_state = avg_rainfall_by_hour.groupby(['prov', 'year', 'month'])['prcp'].sum().reset_index(
            name='total_rainfall')

        # Add 'period' column
        total_rainfall_by_state['period'] = total_rainfall_by_state['year'].astype(str) + total_rainfall_by_state['month'].astype(str).str.zfill(2)

        # Add 'region' column
        total_rainfall_by_state['region'] = region

        # Convert 'period' to datetime format for sorting
        total_rainfall_by_state['date'] = pd.to_datetime(total_rainfall_by_state['period'], format='%Y%m')

        # Sort by 'prov', 'date' to ensure chronological order within each province
        total_rainfall_by_state = total_rainfall_by_state.sort_values(by=['prov', 'date'])

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
        pressure_extremes['period'] = pressure_extremes['year'].astype(str) + pressure_extremes['month'].astype(
            str).str.zfill(2)

        # Add region and date columns
        pressure_extremes['region'] = region
        pressure_extremes['date'] = pd.to_datetime(
            pressure_extremes['year'].astype(str) + '-' + pressure_extremes['month'].astype(str).str.zfill(2))

        # Sort by state, year, and then by month to ensure chronological order within each state
        pressure_extremes = pressure_extremes.sort_values(by=['prov', 'period'])

        # Return results for the specified region
        return pressure_extremes

    @staticmethod
    def calculate_wind_speed(region, df, months_back):
        # Convert 'date' column to datetime and filter for the last "months_back" months
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        latest_date = df['date'].max()
        cutoff_date = latest_date - pd.DateOffset(months=months_back)
        reg_filtered = df[df['date'] > cutoff_date].copy()

        # Group by state, year, and month, then calculate average wind speed
        reg_filtered['year'] = reg_filtered['date'].dt.year
        reg_filtered['month'] = reg_filtered['date'].dt.month
        avg_wind_speed = reg_filtered.groupby(['prov', 'year', 'month'])['wdsp'].mean().reset_index(
            name='avg_wind_speed')

        # Calculate the deviation of wind speed from the average
        reg_filtered['wind_speed_deviation'] = reg_filtered['wdsp'] - reg_filtered.groupby(['prov', 'year', 'month'])[
            'wdsp'].transform('mean')

        # Group by state, year, and month, then calculate average deviation
        wind_speed_deviation = reg_filtered.groupby(['prov', 'year', 'month'])[
            'wind_speed_deviation'].mean().reset_index(name='avg_wind_speed_deviation')

        # Merge the average wind speed and average deviation dataframes
        wind_speed_data = pd.merge(avg_wind_speed, wind_speed_deviation, on=['prov', 'year', 'month'])

        # Add period column
        wind_speed_data['period'] = wind_speed_data['year'].astype(str) + wind_speed_data['month'].astype(
            str).str.zfill(2)

        # Add region and date columns
        wind_speed_data['region'] = region
        wind_speed_data['date'] = pd.to_datetime(
            wind_speed_data['year'].astype(str) + '-' + wind_speed_data['month'].astype(str))

        # Sort by state, year, and then by month to ensure chronological order within each state
        wind_speed_data = wind_speed_data.sort_values(by=['prov', 'period'])

        # Return results for the specified region
        return wind_speed_data

    @staticmethod
    def calculate_total_solar_radiation(region, df, months_back):
        # Convert 'date' column to datetime and filter for the last "months_back" months
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        latest_date = df['date'].max()
        cutoff_date = latest_date - pd.DateOffset(months=months_back)
        reg_filtered = df[df['date'] > cutoff_date].copy()

        # Group by province, year, and month, then calculate the sum of solar radiation
        reg_filtered['year'] = reg_filtered['date'].dt.year
        reg_filtered['month'] = reg_filtered['date'].dt.month
        daily_solar_radiation = reg_filtered.groupby(['prov', 'date'])['gbrd'].mean().reset_index(
            name='daily_solar_radiation')

        # Now calculate the average daily solar radiation per province
        avg_daily_solar_radiation = daily_solar_radiation.groupby(['prov'])['daily_solar_radiation'].mean().reset_index(
            name='avg_daily_solar_radiation')

        # Merge with the original dataframe to distribute the average daily radiation back to each row
        monthly_data = pd.merge(reg_filtered, avg_daily_solar_radiation, on='prov')

        # Calculate the total monthly solar radiation per province
        monthly_data['total_solar_radiation'] = monthly_data['avg_daily_solar_radiation'] * monthly_data[
            'date'].dt.daysinmonth
        monthly_solar_radiation = monthly_data.groupby(['prov', 'year', 'month'])[
            'total_solar_radiation'].sum().reset_index()

        # Add period column
        monthly_solar_radiation['period'] = monthly_solar_radiation['year'].astype(str) + monthly_solar_radiation[
            'month'].astype(str).str.zfill(2)

        # Add region and date columns
        monthly_solar_radiation['region'] = region
        monthly_solar_radiation['date'] = pd.to_datetime(
            monthly_solar_radiation['year'].astype(str) + '-' + monthly_solar_radiation['month'].astype(str))

        # Sort by province, year, and then by month to ensure chronological order within each province
        monthly_solar_radiation = monthly_solar_radiation.sort_values(by=['prov', 'period'])

        # Return results for the specified region
        return monthly_solar_radiation

    @staticmethod
    def calculate_wind_direction_distribution(region, df, months_back):
        # Convert the 'date' column from string to datetime object
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

        # Find the latest date in the dataset for the cutoff calculation
        latest_date = df['date'].max()
        cutoff_time = latest_date.timestamp() - (months_back * 30 * 24 * 3600)

        # Convert the cutoff timestamp back to a datetime object
        cutoff_date = pd.to_datetime(cutoff_time, unit='s')

        # Filter the DataFrame to only include data after the cutoff date
        reg_filtered = df[df['date'] >= cutoff_date].copy()

        # Replace instances of 360 degrees with 0 for wind direction
        reg_filtered['wdct'] = reg_filtered['wdct'].replace(360, 0)

        # Extract the year and month from the 'date' column
        reg_filtered['year'] = reg_filtered['date'].dt.year
        reg_filtered['month'] = reg_filtered['date'].dt.month

        # Define ranges for wind direction categories
        direction_ranges = [(0, 90), (91, 180), (181, 270), (271, 359)]
        direction_labels = ['N', 'E', 'S', 'W']

        # Categorize wind direction measurements into one of four categories
        reg_filtered['wind_direction_range'] = pd.cut(reg_filtered['wdct'],
                                                      bins=[0] + [end for _, end in direction_ranges],
                                                      labels=direction_labels, include_lowest=True)

        # Count occurrences for each wind direction category grouped by province, year, and month
        wind_direction_distribution = reg_filtered.groupby(
            ['prov', 'year', 'month', 'wind_direction_range']).size().unstack(fill_value=0).reset_index()

        # Combine the 'year' and 'month' into a single 'period' column
        wind_direction_distribution['period'] = wind_direction_distribution['year'].astype(str) + wind_direction_distribution['month'].astype(str).str.zfill(2)

        # Add a 'region' column with the region name
        wind_direction_distribution['region'] = region

        # Convert the 'period' column into a datetime object representing the first day of the month
        wind_direction_distribution['date'] = pd.to_datetime(wind_direction_distribution['period'], format='%Y%m')

        # Sort the resulting DataFrame by 'prov' and 'date' to have a chronological order
        wind_direction_distribution = wind_direction_distribution.sort_values(by=['prov', 'date'])

        wind_direction_distribution = wind_direction_distribution.loc[
            ~(wind_direction_distribution[['N', 'E', 'S', 'W']] == 0).any(axis=1)
        ]

        # The method returns a DataFrame with these columns: 'prov', 'year', 'month', 'N', 'E', 'S', 'W', 'period', 'region', 'date'
        return wind_direction_distribution

    @staticmethod
    def calculate_humidity_variability(region, df, months_back):
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        latest_date = df['date'].max()
        cutoff_time = latest_date.timestamp() - (months_back * 30 * 24 * 3600)
        cutoff_date = pd.to_datetime(cutoff_time, unit='s')
        reg_filtered = df[df['date'] >= cutoff_date].copy()

        reg_filtered['year'] = reg_filtered['date'].dt.year
        reg_filtered['month'] = reg_filtered['date'].dt.month
        humidity_variability = reg_filtered.groupby(['prov', 'year', 'month'])['hmdy'].std().reset_index(
            name='humidity_std_dev')

        humidity_variability['period'] = humidity_variability['year'].astype(str) + humidity_variability[
            'month'].astype(str).str.zfill(2)
        humidity_variability['region'] = region
        humidity_variability['date'] = pd.to_datetime(
            humidity_variability['year'].astype(str) + '-' + humidity_variability['month'].astype(str))

        humidity_variability = humidity_variability.sort_values(by=['prov', 'period'])
        return humidity_variability

    @staticmethod
    def calculate_thi(region, df, months_back):
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        latest_date = df['date'].max()
        cutoff_time = latest_date.timestamp() - (months_back * 30 * 24 * 3600)
        cutoff_date = pd.to_datetime(cutoff_time, unit='s')
        reg_filtered = df[df['date'] >= cutoff_date].copy()

        # Calculate THI using the formula: THI = 0.8 * temp + (hmdy * (temp - 14.4)) / 100 + 46.4
        reg_filtered['thi'] = 0.8 * reg_filtered['temp'] + (
                reg_filtered['hmdy'] * (reg_filtered['temp'] - 14.4)) / 100 + 46.4

        reg_filtered['year'] = reg_filtered['date'].dt.year
        reg_filtered['month'] = reg_filtered['date'].dt.month
        thi_data = reg_filtered.groupby(['prov', 'year', 'month'])['thi'].mean().reset_index(name='avg_thi')

        thi_data['period'] = thi_data['year'].astype(str) + thi_data['month'].astype(str).str.zfill(2)
        thi_data['region'] = region
        thi_data['date'] = pd.to_datetime(thi_data['year'].astype(str) + '-' + thi_data['month'].astype(str))

        thi_data = thi_data.sort_values(by=['prov', 'period'])
        return thi_data

    @staticmethod
    def calculate_dew_point_range(region, df, months_back):
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        latest_date = df['date'].max()
        cutoff_time = latest_date.timestamp() - (months_back * 30 * 24 * 3600)
        cutoff_date = pd.to_datetime(cutoff_time, unit='s')
        reg_filtered = df[df['date'] >= cutoff_date].copy()

        reg_filtered['year'] = reg_filtered['date'].dt.year
        reg_filtered['month'] = reg_filtered['date'].dt.month
        dew_point_range = reg_filtered.groupby(['prov', 'year', 'month']).agg(
            max_dewp=('dewp', 'max'),
            min_dewp=('dewp', 'min')
        ).reset_index()

        dew_point_range['dew_point_range'] = dew_point_range['max_dewp'] - dew_point_range['min_dewp']

        # Add period column
        dew_point_range['period'] = dew_point_range['year'].astype(str) + dew_point_range['month'].astype(
            str).str.zfill(2)

        # Add region and date columns
        dew_point_range['region'] = region
        dew_point_range['date'] = pd.to_datetime(
            dew_point_range['year'].astype(str) + '-' + dew_point_range['month'].astype(str))

        # Sort by province, year, and then by month to ensure chronological order within each province
        dew_point_range = dew_point_range.sort_values(by=['prov', 'period'])

        return dew_point_range

    @staticmethod
    def calculate_air_temp_variability(region, df, months_back):
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        latest_date = df['date'].max()
        cutoff_date = latest_date - pd.DateOffset(months=months_back)
        reg_filtered = df[df['date'] > cutoff_date].copy()

        reg_filtered['year'] = reg_filtered['date'].dt.year
        reg_filtered['month'] = reg_filtered['date'].dt.month
        temp_variability = reg_filtered.groupby(['prov', 'year', 'month']).agg(
            temp_std_dev=('temp', 'std')
        ).reset_index()

        # Add period column
        temp_variability['period'] = temp_variability['year'].astype(str) + temp_variability['month'].astype(
            str).str.zfill(2)

        # Add region and date columns
        temp_variability['region'] = region
        temp_variability['date'] = pd.to_datetime(
            temp_variability['year'].astype(str) + '-' + temp_variability['month'].astype(str))

        # Sort by province, year, and then by month to ensure chronological order within each province
        temp_variability = temp_variability.sort_values(by=['prov', 'period'])

        return temp_variability

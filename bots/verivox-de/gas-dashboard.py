import os
import pandas as pd
import sys
import json
from datetime import date, timedelta, datetime
from user_agent import generate_user_agent

if __name__ == '__main__':
    try:

        # add parent directory to path so helpers file can be referenced
        print('gas-dashboard.py started')
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # get current date
        today = date.today()
        todaystr = today.strftime('%Y-%m-%d')
        yesterday_year = datetime.now() - timedelta(days=1)
        year = yesterday_year.year

        df_storage = pd.read_csv(
            f'./data/{todaystr}-gasspeicher.csv', encoding='utf-8', index_col='Datum', usecols=['Datum', f'{year}²'])
        df_storage_trend = pd.read_csv(
            f'./data/{todaystr}-gasspeicher.csv', encoding='utf-8', index_col='Datum', usecols=['Datum', 'Trend'])
        df_gas = pd.read_csv('./data/gas-strom-bundesschnitt.tsv', sep='\t',
                             encoding='utf-8', usecols=['date', 'Gas'], index_col='date')
        df_strom = pd.read_csv('./data/gas-strom-bundesschnitt.tsv', sep='\t',
                               encoding='utf-8', usecols=['date', 'Strom'], index_col='date')
        # df_ns = pd.read_csv('./data/pipelines_ns.csv', encoding='utf-8', index_col='periodFrom')
        df_fossile = pd.read_csv(
            './data/smard_percentage.csv', encoding='utf-8', index_col='Datum')
        # df_usage = pd.read_csv('./data/gasverbrauch.csv', encoding='utf-8', index_col='Datum', usecols=['Datum', 'Normaler Verbrauch¹', 'Aktuell'])
        df_lng = pd.read_csv(
            './data/german-imports.tsv', sep='\t', encoding='utf-8', index_col='Datum')
        df_super = pd.read_csv('./data/node_super.csv', encoding='utf-8',
                               usecols=['meldedatum', 'Mittlerer Preis'], index_col='meldedatum')
        df_imports = pd.read_csv(
            './data/imports-countries-dash.csv', encoding='utf-8')
        df_gasstock = pd.read_csv(
            './data/ttf-gas-stock-dash.csv', encoding='utf-8', index_col='Datum')
        df_acstockeex = pd.read_csv(
            './data/eex-ac-stock-dash.csv', encoding='utf-8', index_col='Datum')
        # fallback with daily data if hourly data above is not available
        # DELETE UNRELIABLE CURRENT STOCK smard_spot_current.csv
        """
        if os.path.isfile('./data/smard_spot_current.csv'): 
            df_acstock = pd.read_csv(
                './data/smard_spot_current.csv', encoding='utf-8', index_col='Datum')
        else:
            df_acstock = pd.read_csv(
                './data/smard_spot.tsv', sep='\t', encoding='utf-8', index_col='Datum')
        """
        df_acstock = pd.read_csv('./data/smard_spot.tsv', sep='\t', encoding='utf-8', index_col='Datum')
        df_acconsumption = pd.read_csv(
            './data/power_consumption.tsv', sep='\t', encoding='utf-8', index_col='Datum')

        # sort, round, calculate mvg avg and convert index to DatetimeIndex
        df_storage.index = pd.to_datetime(df_storage.index)
        df_storage = df_storage.sort_index().round(1)
        df_storage_trend.index = pd.to_datetime(df_storage_trend.index)
        df_storage_trend = df_storage_trend.sort_index()
        df_gas.index = pd.to_datetime(df_gas.index)
        df_strom.index = pd.to_datetime(df_strom.index)
        # df_ns.index = pd.to_datetime(df_ns.index)
        df_super.index = pd.to_datetime(df_super.index)
        df_super = df_super.round(2)
        df_gasstock.index = pd.to_datetime(df_gasstock.index)
        df_acstockeex.index = pd.to_datetime(df_acstockeex.index)
        df_acstock.index = pd.to_datetime(df_acstock.index)

        # Remove spikes due to missing suppliers in the Verivox database, see also verivox-daily-diff.py #
        # Make sure data is sorted by date (if not already)
        df_strom.sort_index(inplace=True)
        df_gas.sort_index(inplace=True)
        # Define threshold percentages
        increase_threshold = 1.1  # 10% increase
        decrease_threshold = 0.9  # 10% decrease
        def clean_outliers(df, column, inc_thresh=1.1, dec_thresh=0.9):
            """
            Detects and replaces both upward and downward isolated outliers in the specified column.
            """
            # Convert column to float for accurate calculations
            df[column] = df[column].astype(float)
            # Create shifted series for previous and next values
            prev = df[column].shift(1)
            next_ = df[column].shift(-1)
            prev_prev = df[column].shift(2)
            next_next = df[column].shift(-2)
            # Detect upward outliers
            upward_outliers = (df[column] > inc_thresh * prev) & (df[column] > inc_thresh * next_)
            # Ensure isolation: neither previous nor next day is also an upward outlier
            upward_isolated = upward_outliers & ~((prev > inc_thresh * prev_prev) | (next_ > inc_thresh * next_next))
            # Detect downward outliers
            downward_outliers = (df[column] < dec_thresh * prev) & (df[column] < dec_thresh * next_)
            # Ensure isolation: neither previous nor next day is also a downward outlier
            downward_isolated = downward_outliers & ~((prev < dec_thresh * prev_prev) | (next_ < dec_thresh * next_next))
            # Combine isolated outliers
            isolated_outliers = upward_isolated | downward_isolated
            # Replace outliers with the average of previous and next day's values
            df.loc[isolated_outliers, column] = (prev + next_) / 2
            # Round the values and convert back to integer
            df[column] = df[column].round().astype(int)
        # Smooth line chart data with a moving average
        def smooth_moving_average(df, column, window=7):
            """
            Smooths a time series column using a moving average, overwriting the original column,
            and keeping the last value unchanged.
            """
            # Calculate the moving average
            smoothed = df[column].rolling(window=window, min_periods=1).mean()
            # Replace the last value with the original value using .loc
            smoothed.loc[df.index[-1]] = df.loc[df.index[-1], column]
            # Overwrite the original column with the smoothed data, rounding and converting to int
            df[column] = smoothed.round().astype(int)
        # Create backup with real data
        df_strom_real = df_strom[['Strom']].copy()
        df_gas_real = df_gas[['Gas']].copy()
        # Apply the cleaning function to both 'Strom' and 'Gas' columns
        clean_outliers(df_strom, 'Strom', inc_thresh=increase_threshold, dec_thresh=decrease_threshold)
        clean_outliers(df_gas, 'Gas', inc_thresh=increase_threshold, dec_thresh=decrease_threshold)
        # Apply the smoothing function to both 'Strom' and 'Gas' columns
        #smooth_moving_average(df_strom, 'Strom', window=3)
        #smooth_moving_average(df_gas, 'Gas', window=3)

        df_gas_mean = df_gas_real.rolling(window=7).mean().dropna()
        df_gas_mean.index = pd.to_datetime(df_gas_mean.index)
        df_strom_mean = df_strom_real.rolling(window=7).mean().dropna()
        df_strom_mean.index = pd.to_datetime(df_strom_mean.index)
        df_fossile.index = pd.to_datetime(df_fossile.index)
        df_fossile = df_fossile.sort_index().round(1)
        # df_usage.index = pd.to_datetime(df_usage.index)
        # df_usage = df_usage.sort_index()
        df_lng.index = pd.to_datetime(df_lng.index)
        df_lng = df_lng.sort_index()
        df_acconsumption.index = pd.to_datetime(df_acconsumption.index)

        # rename columns and remove dates before 2024-01-01
        df_gas_mean = df_gas_mean[(
            df_gas_mean.index.get_level_values(0) >= '2024-01-01')]
        # get last year and adjust time range
        # lasty = today - timedelta(days=365) # alternative with last year
        # lasty = lasty.strftime('%Y-%m-%d') # alternative with last year
        df_gas = df_gas[(df_gas.index.get_level_values(0) >= f'2024-01-01')]
        df_gas_real = df_gas_real[(df_gas_real.index.get_level_values(0) >= f'2024-01-01')]
        df_strom_mean = df_strom_mean[(
            df_strom_mean.index.get_level_values(0) >= '2024-01-01')]
        df_strom = df_strom[(df_strom.index.get_level_values(0) >= '2024-01-01')]
        df_strom_real = df_strom_real[(df_strom_real.index.get_level_values(0) >= '2024-01-01')]
        df_storage.index = df_storage.index.rename('date')
        df_storage = df_storage.rename(columns={f'{year}²': 'Gasspeicher'})
        df_storage_trend.index = df_storage_trend.index.rename('date')
        df_super.index = df_super.index.rename('date')
        df_super = df_super.rename(columns={'Mittlerer Preis': 'Benzinpreis'})
        df_super = df_super[~df_super.index.duplicated(
            keep='last')]  # drop duplicates
        df_gas = df_gas.rename(columns={'Gas': 'Gaspreis'})
        df_gas_real = df_gas_real.rename(columns={'Gas': 'Gaspreis'})
        df_gas_mean = df_gas_mean.rename(columns={'Gas': 'Gaspreis'})
        df_strom = df_strom.rename(columns={'Strom': 'Strompreis'})
        df_strom_real = df_strom_real.rename(columns={'Strom': 'Strompreis'})
        df_strom_mean = df_strom_mean.rename(columns={'Strom': 'Strompreis'})
        df_acstock.rename(
            columns={df_acstock.columns[0]: 'Strom-Börsenpreis'}, inplace=True)
        # df_ns.index = df_ns.index.rename('date')
        # df_ns = df_ns.rename(columns={'Russland': 'Nord Stream 1'})
        df_fossile.index = df_fossile.index.rename('date')
        # df_usage.index = df_usage.index.rename('date')
        # df_usage = df_usage.rename(columns={'Normaler Verbrauch¹': 'Vorjahr', 'Aktuell': 'Gasverbrauch'})
        df_lng.index = df_lng.index.rename('date')
        df_gasstock.index = df_gasstock.index.rename('date')
        df_acstockeex.index = df_acstockeex.index.rename('date')
        df_acstock.index = df_acstock.index.rename('date')
        df_acconsumption.index = df_acconsumption.index.rename('date')

        # convert 20 MWh to 20000 kWh and euro to cent / 4 MWh to 4000 kWh
        df_gas = (df_gas / 200).round(2)
        df_gas_real = (df_gas_real / 200).round(2)
        df_gas_mean = (df_gas_mean / 200).round(2)
        df_strom = (df_strom / 40).round(2)
        df_strom_real = (df_strom_real / 40).round(2)
        df_strom_mean = (df_strom_mean / 40).round(2)

        # convert KWh to GWh and calculate share of imports of power consumption
        df_acconsumption = (df_acconsumption / 1000)
        df_importsshare = df_acconsumption.copy().tail(2)
        share = [df_imports['value'].iloc[-2], (df_imports['value'].iloc[-1])]
        df_importsshare['Import-Anteil'] = share
        # Import-Export-Saldo -> Export-Import-Saldo
        df_importsshare['Import-Anteil'] = -df_importsshare['Import-Anteil']
        df_importsshare['Import-Anteil'] = round(
            (df_importsshare.iloc[:, 1] / df_importsshare.iloc[:, 0]) * 100, 1)
        # replace negative values with zeros
        df_importsshare.loc[df_importsshare['Import-Anteil']
                            <= 0, 'Import-Anteil'] = 0
        df_importsshare = df_importsshare[['Import-Anteil']]

        # get time for stock prices
        # fallback with daily data if hourly data above is not available
        if os.path.isfile('./data/smard_spot_current.csv'):
            acstock_time = df_acstock.index[-1]
            acstock_time = acstock_time.strftime('%-d. %-m., %k Uhr')
        else:
            acstock_time = df_acstock.index[-1]
            acstock_time = acstock_time.strftime('%-d. %-m.')
        gasstock_time = df_gasstock.index[-1]
        gasstock_time = gasstock_time + \
            timedelta(minutes=1) + timedelta(hours=1)  # GMT+1
        gasstock_time = gasstock_time.strftime('%-d. %-m., %k Uhr')

        # merge dataframes
        df = pd.concat([df_gas_real, df_strom_real, df_fossile,
                       df_storage, df_lng['LNG'], df_super, df_gasstock, df_acstock, df_acstockeex], axis=1)

        # STORAGE df = pd.concat([df_storage, df_gas, df_strom], axis=1)
        # BENZIN df = pd.concat([df_storage, df_gas, df_super], axis=1)

        # create temporary dataframe for old data in gas storage and Russian gas
        df_temp = df.copy().tail(90)

        # check if last row in gas fossile(2)/storage (3)/usage(4) column is NaN, then shift numbers
        while pd.isna(df_temp.iloc[-1:, 2].item()) == True:
            df_temp.iloc[:, 2] = df_temp.iloc[:, 2].shift(1)  # fossile
        while pd.isna(df_temp.iloc[-1:, 3].item()) == True:
            df_temp.iloc[:, 3] = df_temp.iloc[:, 3].shift(1)  # storage
        # while pd.isna(df_temp.iloc[-1:, 4].item()) == True: df_temp.iloc[:, 4] = df_temp.iloc[:, 4].shift(1)  # usage
        while pd.isna(df_temp.iloc[-1:, 4].item()) == True:
            df_temp.iloc[:, 4] = df_temp.iloc[:, 4].shift(1)  # LNG
        while pd.isna(df_temp.iloc[-1:, 5].item()) == True:
            df_temp.iloc[:, 5] = df_temp.iloc[:, 5].shift(1)  # Benzin
        while pd.isna(df_temp.iloc[-1:, 6].item()) == True:
            df_temp.iloc[:, 6] = df_temp.iloc[:, 6].shift(1)  # Gas stock
        while pd.isna(df_temp.iloc[-1:, 7].item()) == True:
            df_temp.iloc[:, 7] = df_temp.iloc[:, 7].shift(1)  # AC stock
        while pd.isna(df_temp.iloc[-1:, 8].item()) == True:
            df_temp.iloc[:, 8] = df_temp.iloc[:, 8].shift(1)  # AC EEX stock
        # RUS GAS while pd.isna(df_temp.iloc[-1:, 1].item()) == True:
           # df_temp.iloc[:, 1] = df_temp.iloc[:, 1].shift(1)

        # calculate imports diff
        df_imports_meta = df_imports.copy().tail(1)
        df_imports_meta = df_imports_meta.rename(
            {'value': 'Trend Importe'}, axis='columns')
        i_diff = abs(df_imports['value'].iloc[-1]
                     ) - abs(df_imports['value'].iloc[-2])
        if i_diff >= 2:
            df_imports['Trend Importe'] = 'steigend'
        elif i_diff <= -2:
            df_imports['Trend Importe'] = 'fallend'
        else:
            df_imports['Trend Importe'] = 'gleichbleibend'

        # calculate imports share diff
        df_importsshare_meta = df_importsshare.copy().tail(1)
        df_importsshare_meta = df_importsshare_meta.rename(
            {'value': 'Trend Importe'}, axis='columns')
        i_diff = abs(df_importsshare['Import-Anteil'].iloc[-1]
                     ) - abs(df_importsshare['Import-Anteil'].iloc[-2])
        if i_diff >= 1:
            df_importsshare['Trend Import-Anteil'] = 'steigend'
        elif i_diff <= -1:
            df_importsshare['Trend Import-Anteil'] = 'fallend'
        else:
            df_importsshare['Trend Import-Anteil'] = 'gleichbleibend'

        # calculate gas savings
        """
        u_diff = ((df_usage['Gasverbrauch'].iloc[-1] /
                   df_usage['Vorjahr'].iloc[-1])-1)*100
        u_diffy = ((df_usage['Gasverbrauch'].iloc[-8] /
                    df_usage['Vorjahr'].iloc[-8])-1)*100
        u_diff_diffy = u_diffy - u_diff  # change order for usage instead savings
        u_diff = u_diff.round(1)
        # u_diff_str = f'{u_diff:+g}' # + sign for usage
        # convert to negative/positive number
        if u_diff > 0:
            u_diff_str = -abs(u_diff)
        else:
            u_diff_str = +abs(u_diff)
        """

        # create new dataframe for trends and find last non NaN value (ICU with iloc)
        df_meta = df_temp.copy().tail(1)

        # on Mondays there's no new gas and electricity price data; use last friday for comparison instead
        if datetime.today().weekday() == 0:
            df_meta['Trend Gas'] = ((df['Gaspreis'].loc[~df['Gaspreis'].isnull()].iloc[-1] - df['Gaspreis'].loc[~df['Gaspreis'].isnull(
            )].iloc[-4]) / df['Gaspreis'].loc[~df['Gaspreis'].isnull()].iloc[-4]) * 100  # diff friday
            df_meta['Trend Strom'] = ((df['Strompreis'].loc[~df['Strompreis'].isnull()].iloc[-1] - df['Strompreis'].loc[~df['Strompreis'].isnull(
            )].iloc[-4]) / df['Strompreis'].loc[~df['Strompreis'].isnull()].iloc[-4]) * 100  # diff friday
        else:
            df_meta['Trend Gas'] = ((df['Gaspreis'].loc[~df['Gaspreis'].isnull()].iloc[-1] - df['Gaspreis'].loc[~df['Gaspreis'].isnull(
            )].iloc[-2]) / df['Gaspreis'].loc[~df['Gaspreis'].isnull()].iloc[-2]) * 100  # diff previous day
            df_meta['Trend Strom'] = ((df['Strompreis'].loc[~df['Strompreis'].isnull()].iloc[-1] - df['Strompreis'].loc[~df['Strompreis'].isnull(
            )].iloc[-2]) / df['Strompreis'].loc[~df['Strompreis'].isnull()].iloc[-2]) * 100  # diff previous day

        # other trends not affected by this
        df_meta['Trend Fossile'] = ((df['Fossile Abhängigkeit'].loc[~df['Fossile Abhängigkeit'].isnull(
        )].iloc[-1] - df['Fossile Abhängigkeit'].loc[~df['Fossile Abhängigkeit'].isnull()].iloc[-2]) / df['Fossile Abhängigkeit'].loc[~df['Fossile Abhängigkeit'].isnull()].iloc[-2]) * 100
        df_meta['Trend Speicher'] = df_storage_trend['Trend'].iloc[-1] * 10
        # df_meta['Trend Verbrauch'] = u_diff_diffy
        df_meta['Trend LNG'] = ((df['LNG'].loc[~df['LNG'].isnull(
        )].iloc[-1] / 10) - (df['LNG'].loc[~df['LNG'].isnull()].iloc[-2] / 10))
        df_meta['Trend Benzin'] = round(((df['Benzinpreis'].loc[~df['Benzinpreis'].isnull()].iloc[-1] - df['Benzinpreis'].loc[~df['Benzinpreis'].isnull(
        )].iloc[-2]) / df['Benzinpreis'].loc[~df['Benzinpreis'].isnull()].iloc[-2]) * 100, 0)  # diff previous day
        df_meta['Trend Gasbörse'] = round(((df['Gas-Börsenpreis'].loc[~df['Gas-Börsenpreis'].isnull()].iloc[-1] - df['Gas-Börsenpreis'].loc[~df['Gas-Börsenpreis'].isnull(
        )].iloc[0]) / df['Gas-Börsenpreis'].loc[~df['Gas-Börsenpreis'].isnull()].iloc[0]) * 100, 0)  # diff first value
        df_meta['Trend Strombörse'] = round(((df['Strom-Börsenpreis'].loc[~df['Strom-Börsenpreis'].isnull()].iloc[-1] - df['Strom-Börsenpreis'].loc[~df['Strom-Börsenpreis'].isnull(
        )].iloc[0]) / df['Strom-Börsenpreis'].loc[~df['Strom-Börsenpreis'].isnull()].iloc[0]) * 100, 0)  # diff first value
        df_meta['Trend Strombörse EEX'] = round(((df['Strom-Terminmarkt'].loc[~df['Strom-Terminmarkt'].isnull()].iloc[-1] - df['Strom-Terminmarkt'].loc[~df['Strom-Terminmarkt'].isnull(
        )].iloc[0]) / df['Strom-Terminmarkt'].loc[~df['Strom-Terminmarkt'].isnull()].iloc[0]) * 100, 0)  # diff first value

        # NS1 df_meta = df_meta[['Trend Speicher', 'Trend Gas', 'Trend NS1', 'Gasspeicher', 'Gaspreis', 'Strompreis']]
        # STORAGE df_meta = df_meta[['Trend Speicher', 'Trend Gas', 'Trend Strom', 'Gasspeicher', 'Gaspreis', 'Strompreis']]
        df_meta = df_meta[['Trend Gas', 'Trend Strom', 'Trend Fossile', 'Trend Speicher',
                           'Trend LNG', 'Trend Benzin', 'Trend Gasbörse', 'Trend Strombörse', 'Trend Strombörse EEX', 'Gaspreis', 'Strompreis', 'Fossile Abhängigkeit', 'Gasspeicher', 'LNG', 'Benzinpreis', 'Gas-Börsenpreis', 'Strom-Börsenpreis', 'Strom-Terminmarkt']]

        # STROM/NS1: change cols1/cols7
        # replace percentages with strings
        # NS1 cols1 = ['Trend Speicher', 'Trend Gas']
        # NS1 cols7 = ['Trend NS1']
        # STORAGE cols1 = ['Trend Speicher', 'Trend Gas', 'Trend Strom']
        cols1 = ['Trend Gas', 'Trend Strom',
                 'Trend Fossile', 'Trend Speicher', 'Trend LNG', 'Trend Benzin', 'Trend Gasbörse', 'Trend Strombörse', 'Trend Strombörse EEX']

        # function for string trends (storage and gas=previous day, petrol=previous week)
        def replace_vals(df_meta):
            for col in cols1:
                if df_meta[col] >= 0.2:
                    df_meta[col] = 'steigend'
                elif df_meta[col] <= -0.2:
                    df_meta[col] = 'fallend'
                else:
                    df_meta[col] = 'gleichbleibend'
            """
            # NS1
            for col in cols7:
                if df_meta[col] >= 7:
                    df_meta[col] = 'steigend'
                elif df_meta[col] <= -7:
                    df_meta[col] = 'fallend'
                else:
                    df_meta[col] = 'gleichbleibend'
            """
            return df_meta
        df_meta = df_meta.apply(replace_vals, axis=1)

        # get last values of df_meta as objects
        df_meta = df_meta.iloc[0]
        trend_storage = df_meta['Trend Speicher']
        trend_gas = df_meta['Trend Gas']
        trend_strom = df_meta['Trend Strom']
        trend_fossile = df_meta['Trend Fossile']
        # trend_usage = df_meta['Trend Verbrauch']
        trend_lng = df_meta['Trend LNG']
        # NS1 trend_ns = df_meta['Trend NS1']
        # RUS GAS trend_rus = df_meta['Trend Importe']
        trend_super = df_meta['Trend Benzin']
        trend_imports = df_imports['Trend Importe'].iloc[-1]
        trend_importsshare = df_importsshare['Trend Import-Anteil'].iloc[-1]
        trend_gasstock = df_meta['Trend Gasbörse']
        trend_acstock = df_meta['Trend Strombörse']
        trend_acstockeex = df_meta['Trend Strombörse EEX']
        diff_storage = df_meta['Gasspeicher']
        diff_gas = df_gas['Gaspreis'].iloc[-1].round(1)
        diff_strom = df_strom['Strompreis'].iloc[-1].round(1)
        # diff_ns = df_ns['Nord Stream 1'].iloc[-1].round(2)
        diff_fossile = df_fossile['Fossile Abhängigkeit'].iloc[-1]
        # diff_usage = u_diff_str
        diff_lng = df_meta['LNG'].round(1)
        # RUS GAS diff_rus = df_meta['Russisches Gas']
        diff_super = df_meta['Benzinpreis']
        # convert to opposite sign for imports
        df_imports['value'] = -df_imports['value']
        diff_imports = df_imports['value'].iloc[-1].round(0).astype(int)
        diff_importsshare = df_importsshare['Import-Anteil'].iloc[-1]

        # convert to kWh and remove negative sign from zeros
        diff_gasstock = df_meta['Gas-Börsenpreis'] / 10
        diff_gasstock = round(diff_gasstock, 1).astype(str)
        diff_acstock = df_meta['Strom-Börsenpreis'] / 10
        diff_acstock = round(diff_acstock, 1).astype(str)
        diff_acstock = diff_acstock.replace('-0.0', '0.0')
        diff_acstockeex = df_meta['Strom-Terminmarkt'] / 10
        diff_acstockeex = round(diff_acstockeex, 1).astype(str)
        diff_acstockeex = diff_acstockeex.replace('-0.0', '0.0')
        diff_gasstock = diff_gasstock.replace('-0.0', '0.0')
        diff_acstock = pd.to_numeric(diff_acstock)
        diff_acstockeex = pd.to_numeric(diff_acstockeex)
        diff_gasstock = pd.to_numeric(diff_gasstock)

        # get current date for chart notes and reset index
        df = df.reset_index()
        df_storage = df_storage.reset_index()
        df_gas = df_gas.reset_index()
        df_strom = df_strom.reset_index()
        # df_ns = df_ns.reset_index()
        df_fossile = df_fossile.reset_index()
        # df_usage = df_usage.reset_index()
        df_lng = df_lng.reset_index()
        df_super = df_super.reset_index()
        df['date'] = pd.to_datetime(
            df['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        df_storage['date'] = pd.to_datetime(
            df_storage['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        df_gas['date'] = pd.to_datetime(
            df_gas['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        df_strom['date'] = pd.to_datetime(
            df_strom['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        # df_ns['date'] = pd.to_datetime(df_ns['date'], dayfirst=True).dt.strftime('%Y-%m-%d %H:%M:%S')
        df_fossile['date'] = pd.to_datetime(
            df_fossile['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        # df_usage['date'] = pd.to_datetime( df_usage['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        df_lng['date'] = pd.to_datetime(
            df_lng['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        df_super['date'] = pd.to_datetime(
            df_super['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        timestamp_str = df_gas['date'].tail(1).item()
        timestamp_str_price = df_gas['date'].tail(1).item()
        timestamp_str_price = pd.to_datetime(
            timestamp_str_price).strftime('%-d. %-m.')
        # timestamp_str_usage = df_usage['date'].tail(1).item()
        # timestamp_str_usage = pd.to_datetime( timestamp_str_usage).strftime('%-d. %-m.')
        timestamp_str_storage = df_storage['date'].tail(1).item()
        timestamp_str_storage = pd.to_datetime(
            timestamp_str_storage).strftime('%-d. %-m.')
        timestamp_str_fossile = (pd.to_datetime(
            df_fossile['date'].tail(1).item())).strftime('KW %U')
        timestamp_str_lng = df_lng['date'].tail(1).item()
        timestamp_str_lng = pd.to_datetime(
            timestamp_str_lng).strftime('%-d. %-m.')
        timestamp_str_imports = df_imports['date'].tail(1).item()

        # OLD replace NaN with empty string for old storage data
        # df['Gasspeicher'] = df['Gasspeicher'].fillna(0).astype(int).astype(str)
        # df['Gasspeicher'] = df['Gasspeicher'].replace(['0', '0.0'], '')

        # create dictionaries for JSON file and drop NaN
        # dict_gas = df_gas.rename(columns={df_storage.columns[1]: 'value'}).to_dict(orient='records')
        dict_super = df.drop(df.columns[[1, 2]], axis=1).rename(
            columns={df.columns[3]: 'value'}).to_dict(orient='records')
        dict_storage = df_storage.rename(
            columns={df_storage.columns[1]: 'value'}).to_dict(orient='records')
        # dict_gas = df.drop(df.columns[[2, 3]], axis=1).rename(columns={df.columns[1]: 'value'}).dropna().to_dict(orient='records')
        dict_gas = df_gas.rename(
            columns={df_gas.columns[1]: 'value'}).to_dict(orient='records')
        dict_strom = df_strom.rename(
            columns={df_strom.columns[1]: 'value'}).to_dict(orient='records')
        #dict_strom = df.drop(df.columns[[1, 3]], axis=1).rename(columns={df.columns[2]: 'value'}).dropna().to_dict(orient='records')
        dict_fossile = df_fossile.rename(
            columns={df_fossile.columns[1]: 'value'}).to_dict(orient='records')
        # dict_usage = df_usage.rename(columns={df_usage.columns[2]: 'value'}).to_dict(orient='records')
        # df_ns['Nord Stream 1'] = df_ns['Nord Stream 1'].round(2).astype(float)
        # dict_ns = df_ns.rename(columns={'Nord Stream 1': 'value'}).dropna().to_dict(orient='records')
        dict_lng = df_lng.rename(
            columns={df_lng.columns[1]: 'value'}).to_dict(orient='records')
        # replace 'KW' with real dates
        df_imports.at[df_imports.index[-1],
                      'date'] = str(df_fossile['date'].iloc[-1])
        df_imports.at[df_imports.index[-2],
                      'date'] = str(df_fossile['date'].iloc[-2])
        dict_imports = df_imports.drop(df_imports.columns[[0, 3]], axis=1).rename(
            columns={df_imports.columns[2]: 'value'}).to_dict(orient='records')
        dict_importsshare = df_importsshare.rename(
            columns={df_importsshare.columns[1]: 'value'}).to_dict(orient='records')

        # additional data for JSON file
        # y-axis start and ticks
        storage_y = 0  # if y-axis starts at 0: value is optional
        gas_y = 0
        strom_y = 0
        ns_y = 0
        fossile_y = 20
        imports_y = -2000
        importsshare_y = 0
        # RUS GAS rus_y = 0
        super_y = 1.6
        fueloil_y = 60
        storage_ytick = [0, 25, 50, 75, 100]
        # gas_ytick = [0, 15, 30, 45] # from January 2021
        gas_ytick = [6, 8, 10, 12]
        strom_ytick = [24, 28, 32, 36]
        ns_ytick = [0, 0.5, 1, 1.5]
        fossile_ytick = [20, 35, 50, 65]
        # RUS GAS rus_ytick = [0, 100, 200, 300]
        super_ytick = [1.6, 1.8, 2.0, 2.2, 2.4]
        fueloil_ytick = [60, 80, 100, 120, 140]
        imports_ytick = [-2000, -1000, 0, 1000, 2000]
        importsshare_ytick = [0, 5, 10, 15, 20]

        # change decimal seperator
        diff_storage_str = diff_storage.astype(str).replace('.', ',')
        diff_gas_str = diff_gas.astype(str).replace('.', ',')
        diff_strom_str = diff_strom.astype(str).replace('.', ',')
        # diff_ns_str = diff_ns.astype(str).replace('.', ',')
        diff_fossile_str = diff_fossile.astype(str).replace('.', ',')
        diff_fossile = diff_fossile.astype(float)
        # diff_usage_str = u_diff_str.astype(str).replace('.', ',')
        diff_lng_str = diff_lng.astype(str).replace('.', ',')
        # RUS GAS diff_rus_str = diff_rus.round(0).astype(int)
        diff_super_str = diff_super.astype(str).replace('.', ',')
        diff_gasstock_str = diff_gasstock.astype(str).replace('.', ',')
        diff_acstock_str = diff_acstock.astype(str).replace('.', ',')
        diff_acstockeex_str = diff_acstockeex.astype(str).replace('.', ',')
        diff_importsshare_str = diff_importsshare.astype(str).replace('.', ',')

        def replace_vals(df_meta):
            """
            Replaces numeric differences in df_meta with string trends:
            - >= +0.2 => 'steigend'
            - <= -0.2 => 'fallend'
            - otherwise => 'gleichbleibend'
            """
            # Example list of columns that contain numeric differences:
            cols1 = ['Heizoel_diff']  # adjust this to the columns you want to convert
            
            for col in cols1:
                # Round the difference to 1 decimal place before comparison
                rounded_diff = round(df_meta.loc[0, col], 1)
                if rounded_diff >= 0.1:
                    df_meta.loc[0, col] = 'steigend'
                elif rounded_diff <= -0.1:
                    df_meta.loc[0, col] = 'fallend'
                else:
                    df_meta.loc[0, col] = 'gleichbleibend'
            return df_meta

        def scrape_esyoil_data():
            """
            1) Scrapes JSON data from esyoil.com
            2) Extracts the last two values in 'year0'
            3) Creates a mini DataFrame with old/new prices and difference
            4) Applies the 'replace_vals' function to turn numeric difference into a trend
            """
            url = "https://api.esyoil.com/v1/charts/jahresvergleich"
            
            # Generate a random user agent and include “no-cache” headers
            fheaders = {
                'user-agent': generate_user_agent(),
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # 1) Fetch JSON data
            response = requests.get(url, headers=fheaders)
            data = response.json()
            
            # 2) Extract "year0" array and grab the last two entries
            year0_data = data["data"]["year0"]
            old_ts, old_str = year0_data[-2]
            new_ts, new_str = year0_data[-1]
            
            # Convert prices to float and round to 1 decimal place
            old_price = round(float(old_str), 1)
            new_price = round(float(new_str), 1)
            
            # Convert UNIX timestamps to human-readable dates (UTC)
            old_date = datetime.utcfromtimestamp(old_ts).strftime('%Y-%m-%d')
            new_date = datetime.utcfromtimestamp(new_ts).strftime('%Y-%m-%d')
            
            # 3) Build a small DataFrame with old/new prices, difference, etc.
            df_meta = pd.DataFrame(
                [[old_ts, old_date, old_price, new_ts, new_date, new_price]],
                columns=[
                    'Heizoel_old_ts', 'Heizoel_old_date', 'Heizoel_old_price',
                    'Heizoel_new_ts', 'Heizoel_new_date', 'Heizoel_new_price'
                ]
            )
            
            # Create a difference column (new price - old price)
            df_meta['Heizoel_diff'] = df_meta['Heizoel_new_price'] - df_meta['Heizoel_old_price']
            
            # 4) Use the function to convert numeric differences to trends
            df_meta = replace_vals(df_meta)
            
            return df_meta
        df_fueloil = scrape_esyoil_data()
        trend_fueloil = df_fueloil.loc[0, 'Heizoel_diff']
        diff_fueloil = df_fueloil.loc[0, 'Heizoel_new_price']
        diff_fueloil_str = diff_fueloil.astype(str).replace('.', ',')

        # {gasstock_time} = date and time for gas stock description

        meta_storage = {'indicatorTitle': 'Gasspeicher', 'date': todaystr, 'indicatorSubtitle': f'Füllstand, gesicherte Kapazität¹', 'value': diff_storage, 'valueLabel': f'{diff_storage_str} %',
                        'yAxisStart': storage_y, 'yAxisLabels': storage_ytick, 'yAxisLabelDecimals': 0, 'color': '#ce4631', 'trend': trend_storage, 'chartType': 'area'}
        meta_gas = {'indicatorTitle': 'Gaspreis', 'date': todaystr, 'indicatorSubtitle': f'je kWh für Neukunden, ohne Bonus', 'value': diff_gas, 'valueLabel': f'{diff_gas_str} Cent',
                    'yAxisStart': gas_y, 'yAxisLabels': gas_ytick, 'yAxisLabelDecimals': 0, 'color': '#ce4631', 'trend': trend_gas, 'chartType': 'line'}
        meta_gasstock = {'indicatorTitle': 'Gas im Grosshandel', 'date': todaystr, 'indicatorSubtitle': f'je kWh, mittelfristige Lieferung', 'value': diff_gasstock, 'valueLabel': f'{diff_gasstock_str} Cent',
                         'yAxisStart': gas_y, 'yAxisLabels': gas_ytick, 'yAxisLabelDecimals': 0, 'color': '#ce4631', 'trend': trend_gasstock, 'chartType': 'line'}
        meta_strom = {'indicatorTitle': 'Strompreis', 'date': todaystr, 'indicatorSubtitle': f'je kWh für Neukunden, ohne Bonus', 'value': diff_strom, 'valueLabel': f'{diff_strom_str} Cent',
                      'yAxisStart': strom_y, 'yAxisLabels': strom_ytick, 'yAxisLabelDecimals': 0, 'color': '#374e8e', 'trend': trend_strom, 'chartType': 'line'}
        meta_stromstockeex = {'indicatorTitle': 'Strom im Grosshandel', 'date': todaystr, 'indicatorSubtitle': f'je kWh, langfristige Lieferung', 'value': diff_acstockeex, 'valueLabel': f'{diff_acstockeex_str} Cent',
                              'yAxisStart': strom_y, 'yAxisLabels': strom_ytick, 'yAxisLabelDecimals': 0, 'color': '#374e8e', 'trend': trend_acstockeex, 'chartType': 'line'}
        meta_stromstock = {'indicatorTitle': 'Strom am Spotmarkt', 'date': todaystr, 'indicatorSubtitle': f'je kWh, {acstock_time}, sofortige Lieferung', 'value': diff_acstock, 'valueLabel': f'{diff_acstock_str} Cent',
                           'yAxisStart': strom_y, 'yAxisLabels': strom_ytick, 'yAxisLabelDecimals': 0, 'color': '#374e8e', 'trend': trend_acstock, 'chartType': 'line'}
        meta_fossile = {'indicatorTitle': 'Fossiler Anteil', 'date': todaystr, 'indicatorSubtitle': f'an der Stromerzeugung in der {timestamp_str_fossile}',
                        'value': diff_fossile, 'valueLabel': f'{diff_fossile_str} %', 'yAxisStart': fossile_y, 'yAxisLabels': fossile_ytick, 'yAxisLabelDecimals': 0, 'color': '#374e8e', 'trend': trend_fossile, 'chartType': 'area'}
        # meta_imports = {'indicatorTitle': 'Strom-Importe', 'date': todaystr, 'indicatorSubtitle': f'Import-Export-Saldo in der {timestamp_str_imports}', 'value': float(diff_imports), 'valueLabel': f'{diff_imports} GWh', 'yAxisStart': imports_y, 'yAxisLabels': imports_ytick, 'yAxisLabelDecimals': 0, 'color': '#374e8e', 'trend': trend_imports, 'chartType': 'line'}
        meta_importsshare = {'indicatorTitle': 'Anteil Strom-Importe', 'date': todaystr, 'indicatorSubtitle': f'am Stromverbrauch per Saldo in der {timestamp_str_imports}',
                             'value': diff_importsshare, 'valueLabel': f'{diff_importsshare_str} %', 'yAxisStart': imports_y, 'yAxisLabels': importsshare_ytick, 'yAxisLabelDecimals': 0, 'color': '#374e8e', 'trend': trend_importsshare, 'chartType': 'line'}
        # meta_usage = {'indicatorTitle': 'Eingespartes Gas', 'date': todaystr, 'indicatorSubtitle': f'im Vorjahres-Vergleich; Ziel: >25 %', 'value': u_diff, 'valueLabel': f'{diff_usage_str} %', 'yAxisStart': gas_y, 'yAxisLabels': gas_ytick, 'yAxisLabelDecimals': 0, 'color': '#ce4631', 'trend': trend_usage, 'chartType': 'line'}
        meta_lng = {'indicatorTitle': 'Direkt-Importe LNG', 'date': todaystr, 'indicatorSubtitle': f'Anteil an den Gas-Importen insgesamt',
                    'value': diff_lng, 'valueLabel': f'{diff_lng_str} %', 'yAxisStart': gas_y, 'yAxisLabels': gas_ytick, 'yAxisLabelDecimals': 0, 'color': '#ce4631', 'trend': trend_lng, 'chartType': 'line'}
        # NS 1 meta_ns = {'indicatorTitle': 'Nord Stream 1', 'date': timestamp_str, 'indicatorSubtitle': 'Gasflüsse pro Stunde', 'value': diff_ns, 'valueLabel': f'{diff_ns_str} Mio. m³', 'yAxisStart': strom_y, 'yAxisLabels': ns_ytick, 'yAxisLabelDecimals': 1, 'color': '#ce4631', 'trend': trend_ns, 'chartType': 'line'}
        # RUS GAS meta_rus = {'indicatorTitle': 'Russisches Gas', 'date': timestamp_str, 'indicatorSubtitle': 'Gasflüsse nach Deutschland', 'value': diff_rus, 'valueLabel': f'{diff_rus_str} Mio. m³', 'yAxisStart': rus_y, 'yAxisLabels': rus_ytick, 'yAxisLabelDecimals': 0, 'color': '#ce4631', 'trend': trend_rus, 'chartType': 'line'}
        meta_super = {'indicatorTitle': 'Benzinpreis', 'date': timestamp_str, 'indicatorSubtitle': 'je Liter Super E5', 'value': diff_super, 'valueLabel': f'{diff_super_str} Euro',
                      'yAxisStart': super_y, 'yAxisLabels': super_ytick, 'yAxisLabelDecimals': 1, 'color': '#4d313c', 'trend': trend_super, 'chartType': 'line'}
        meta_fueloil = {'indicatorTitle': 'Heizölpreis', 'date': timestamp_str, 'indicatorSubtitle': 'je 100 Liter', 'value': diff_fueloil, 'valueLabel': f'{diff_fueloil_str} Euro',
                      'yAxisStart': fueloil_y, 'yAxisLabels': fueloil_ytick, 'yAxisLabelDecimals': 1, 'color': '#4d313c', 'trend': trend_fueloil, 'chartType': 'line'}

        # merge dictionaries
        # STORAGE meta_storage['chartData'] = dict_storage
        meta_gas['chartData'] = dict_gas
        meta_strom['chartData'] = dict_strom
        meta_fossile['chartData'] = []
        # meta_imports['chartData'] = []
        meta_importsshare['chartData'] = []
        # meta_usage['chartData'] = []
        meta_storage['chartData'] = []
        meta_lng['chartData'] = []
        # NS1 meta_ns['chartData'] = dict_ns
        # RUS GAS meta_rus['chartData'] = dict_rus
        meta_super['chartData'] = []
        meta_fueloil['chartData'] = []
        meta_gasstock['chartData'] = []
        meta_stromstockeex['chartData'] = []
        #meta_stromstock['chartData'] = []
        dicts = []
        # STORAGE dicts.append(meta_storage)
        # RUS GAS dicts.append(meta_rus)
        dicts.append(meta_gas)
        dicts.append(meta_gasstock)
        dicts.append(meta_storage)
        # dicts.append(meta_usage)
        dicts.append(meta_lng)
        dicts.append(meta_strom)
        dicts.append(meta_stromstockeex)
        # dicts.append(meta_stromstock)
        dicts.append(meta_fossile)
        # dicts.append(meta_imports)
        dicts.append(meta_importsshare)
        # NS1 dicts.append(meta_ns)
        dicts.append(meta_super)
        dicts.append(meta_fueloil)
        with open('./data/dashboard_de.json', 'w') as fp:
            json.dump(dicts, fp, indent=4)
        file = [{
            "loadSyncBeforeInit": True,
            "file": {
                "path": "./data/dashboard_de.json"
            }
        }]

        # add chart notes
        # today_str = today.strftime('%-d. %-m. %Y')
        # notes_chart = f'Stand: {today_str}. Pfeile: Veränderung zum Vortag, beim Sprit zur Vorwoche. Quellen: Agsi, Verivox, Bundeskartellamt'

        # run Q function
        update_chart(id='38c6dc628d74a268a1d09ed8065f7803', files=file)

        # delete all csv and geojson files
        dir = 'data/'
        extracted = os.listdir(dir)
        for item in extracted:
            if item.endswith('.csv') or item.endswith('.geojson'):
                os.remove(os.path.join(dir, item))
        # os.remove(os.path.join(dir, 'dashboard_de.json'))
        print('gas-dashboard.py successfully executed')
    except:
        raise
